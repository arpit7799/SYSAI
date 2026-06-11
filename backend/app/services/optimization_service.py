import psutil
import os
from typing import List, Dict, Any
from sqlalchemy import select, desc, func
from app.db.session import AsyncSessionLocal
from app.db.models import OptimizationAction, MetricSnapshot
from app.schemas.optimization import OptimizationSummary, OptimizationActionResponse
from app.core.logger import log


# ─── Safety Policy ────────────────────────────────────────────────────────────

# Processes that must NEVER be touched
PROTECTED_PROCESSES = {
    "kernel", "systemd", "init", "launchd",
    "kthreadd", "sshd", "postgres", "redis",
    "python", "python3", "uvicorn", "node",
    "WindowServer", "loginwindow", "Finder",
}

# Minimum CPU threshold to consider killing a process
KILL_CPU_THRESHOLD = 80.0

# Minimum memory threshold to consider killing a process
KILL_MEM_THRESHOLD = 50.0


def is_protected(proc_name: str) -> bool:
    name_lower = proc_name.lower()
    return any(p.lower() in name_lower for p in PROTECTED_PROCESSES)


# ─── Action Executor ──────────────────────────────────────────────────────────

async def _log_action(
    action_type: str,
    target: str,
    reason: str,
    success: bool,
    rollback_data: Dict[str, Any] = None,
) -> None:
    async with AsyncSessionLocal() as session:
        action = OptimizationAction(
            action_type=action_type,
            target=target,
            reason=reason,
            success=1 if success else 0,
            rollback_data=rollback_data or {},
        )
        session.add(action)
        await session.commit()


def _get_recommendations(
    cpu: float, ram: float, disk: float
) -> List[str]:
    """
    Generate human-readable optimization recommendations
    based on current system state.
    """
    recs = []

    if cpu > 80:
        recs.append("CPU critically high — consider closing unused applications")
    elif cpu > 60:
        recs.append("CPU elevated — background processes may be causing load")

    if ram > 85:
        recs.append("RAM critically high — system may start swapping to disk")
    elif ram > 70:
        recs.append("RAM usage high — consider closing memory-heavy applications")

    if disk > 90:
        recs.append("Disk nearly full — free up space to prevent system slowdown")

    if cpu < 20 and ram < 50:
        recs.append("System is healthy — no optimization needed at this time")

    if not recs:
        recs.append("System operating within normal parameters")

    return recs


# ─── Core Optimizer ───────────────────────────────────────────────────────────

async def run_optimization(mode: str = "safe") -> Dict:
    """
    Main optimization function.
    safe mode: only recommendations + priority adjustments
    aggressive mode: can terminate non-essential processes
    """
    actions_taken = []
    recommendations = []

    # Get current system state
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
    except Exception as e:
        log.error("Failed to read system state", error=str(e))
        return {"actions": [], "recommendations": ["Unable to read system state"]}

    recommendations = _get_recommendations(cpu, ram, disk)

    # Only act if system is under pressure
    if cpu < 60 and ram < 70:
        log.info("System healthy — no optimization needed")
        await _log_action(
            action_type="scan",
            target="system",
            reason="Routine optimization scan — system healthy",
            success=True,
            rollback_data={"cpu": cpu, "ram": ram},
        )
        return {
            "actions": [],
            "recommendations": recommendations,
            "status": "healthy",
        }

    # Scan processes for optimization candidates
    processes = []
    for proc in psutil.process_iter(
        ["pid", "name", "cpu_percent", "memory_percent", "nice", "status"]
    ):
        try:
            info = proc.info
            if info["cpu_percent"] is None:
                info["cpu_percent"] = 0.0
            if info["memory_percent"] is None:
                info["memory_percent"] = 0.0
            processes.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Sort by CPU descending
    processes.sort(key=lambda p: p["cpu_percent"], reverse=True)

    for proc_info in processes[:20]:  # check top 20
        name = proc_info["name"] or "unknown"
        pid = proc_info["pid"]
        proc_cpu = proc_info["cpu_percent"]
        proc_mem = proc_info["memory_percent"]

        # Skip protected processes
        if is_protected(name):
            continue

        try:
            proc = psutil.Process(pid)

            # Action 1: Lower priority for high-CPU non-essential processes
            if proc_cpu > 50 and mode == "safe":
                old_nice = proc.nice()
                proc.nice(10)  # lower priority (higher nice = less priority)

                await _log_action(
                    action_type="set_priority",
                    target=f"{name} (PID {pid})",
                    reason=f"CPU usage {proc_cpu:.1f}% — lowered scheduling priority",
                    success=True,
                    rollback_data={"pid": pid, "old_nice": old_nice, "new_nice": 10},
                )
                actions_taken.append({
                    "action": "set_priority",
                    "target": name,
                    "pid": pid,
                    "detail": f"Priority lowered (nice: {old_nice} → 10)",
                })
                log.info("Priority lowered", process=name, cpu=proc_cpu)

            # Action 2: Terminate high-CPU processes in aggressive mode
            elif proc_cpu > KILL_CPU_THRESHOLD and mode == "aggressive":
                proc.terminate()

                await _log_action(
                    action_type="terminate_process",
                    target=f"{name} (PID {pid})",
                    reason=f"CPU {proc_cpu:.1f}% exceeded threshold in aggressive mode",
                    success=True,
                    rollback_data={"pid": pid, "name": name},
                )
                actions_taken.append({
                    "action": "terminate",
                    "target": name,
                    "pid": pid,
                    "detail": f"Terminated — CPU was {proc_cpu:.1f}%",
                })
                log.info("Process terminated", process=name, cpu=proc_cpu)

        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError) as e:
            log.warning("Could not optimize process", process=name, error=str(e))
            await _log_action(
                action_type="set_priority",
                target=f"{name} (PID {pid})",
                reason=f"Attempted optimization — access denied",
                success=False,
            )

    log.info(
        "Optimization complete",
        actions=len(actions_taken),
        mode=mode,
        cpu=cpu,
        ram=ram,
    )

    return {
        "actions": actions_taken,
        "recommendations": recommendations,
        "status": "optimized" if actions_taken else "healthy",
        "metrics": {"cpu": cpu, "ram": ram, "disk": disk},
    }


async def get_optimization_summary() -> OptimizationSummary:
    """Return recent optimization actions and recommendations."""
    async with AsyncSessionLocal() as session:
        total_result = await session.execute(
            select(func.count(OptimizationAction.id))
        )
        total = total_result.scalar() or 0

        success_result = await session.execute(
            select(func.count(OptimizationAction.id))
            .where(OptimizationAction.success == 1)
        )
        successful = success_result.scalar() or 0

        recent_result = await session.execute(
            select(OptimizationAction)
            .order_by(desc(OptimizationAction.executed_at))
            .limit(10)
        )
        recent = recent_result.scalars().all()

    try:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        recommendations = _get_recommendations(cpu, ram, disk)
    except Exception:
        recommendations = ["Unable to read system state"]

    return OptimizationSummary(
        total_actions=total,
        successful=successful,
        failed=total - successful,
        recent=[OptimizationActionResponse.model_validate(r) for r in recent],
        recommendations=recommendations,
    )