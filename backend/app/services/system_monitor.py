import psutil
import time
from datetime import datetime, timezone
from typing import List
from app.schemas.metrics import (
    CPUMetrics, RAMMetrics, DiskMetrics,
    NetworkMetrics, ProcessInfo, SystemSnapshot
)
from app.core.logger import log


class SystemMonitor:
    """
    Core service that reads real-time system metrics using psutil.
    Stateless — every call reads fresh data from the OS.
    """

    def get_cpu(self) -> CPUMetrics:
        freq = psutil.cpu_freq()
        return CPUMetrics(
            usage_percent=psutil.cpu_percent(interval=0.1),
            per_core_percent=psutil.cpu_percent(interval=0.1, percpu=True),
            frequency_mhz=freq.current if freq else 0.0,
            core_count=psutil.cpu_count(logical=False) or 1,
            thread_count=psutil.cpu_count(logical=True) or 1,
        )

    def get_ram(self) -> RAMMetrics:
        vm = psutil.virtual_memory()
        sw = psutil.swap_memory()
        gb = 1024 ** 3
        return RAMMetrics(
            total_gb=round(vm.total / gb, 2),
            used_gb=round(vm.used / gb, 2),
            available_gb=round(vm.available / gb, 2),
            usage_percent=vm.percent,
            swap_total_gb=round(sw.total / gb, 2),
            swap_used_gb=round(sw.used / gb, 2),
            swap_percent=sw.percent,
        )

    def get_disk(self) -> DiskMetrics:
        disk = psutil.disk_usage("/")
        gb = 1024 ** 3
        mb = 1024 ** 2

        # Read I/O counters with a small interval for per-second rates
        io1 = psutil.disk_io_counters()
        time.sleep(0.1)
        io2 = psutil.disk_io_counters()

        read_rate = 0.0
        write_rate = 0.0
        if io1 and io2:
            read_rate = round((io2.read_bytes - io1.read_bytes) / mb / 0.1, 2)
            write_rate = round((io2.write_bytes - io1.write_bytes) / mb / 0.1, 2)

        return DiskMetrics(
            total_gb=round(disk.total / gb, 2),
            used_gb=round(disk.used / gb, 2),
            free_gb=round(disk.free / gb, 2),
            usage_percent=disk.percent,
            read_mb_per_sec=read_rate,
            write_mb_per_sec=write_rate,
        )

    def get_network(self) -> NetworkMetrics:
        net = psutil.net_io_counters()
        mb = 1024 ** 2
        return NetworkMetrics(
            bytes_sent_mb=round(net.bytes_sent / mb, 2),
            bytes_recv_mb=round(net.bytes_recv / mb, 2),
            packets_sent=net.packets_sent,
            packets_recv=net.packets_recv,
        )

    def get_top_processes(self, limit: int = 10) -> List[ProcessInfo]:
        processes = []
        for proc in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_percent", "status", "username"]
        ):
            try:
                info = proc.info
                # Skip system/zombie processes with 0 CPU
                if info["cpu_percent"] is None:
                    info["cpu_percent"] = 0.0
                if info["memory_percent"] is None:
                    info["memory_percent"] = 0.0

                processes.append(
                    ProcessInfo(
                        pid=info["pid"],
                        name=info["name"] or "unknown",
                        cpu_percent=round(info["cpu_percent"], 2),
                        memory_percent=round(info["memory_percent"], 2),
                        status=info["status"] or "unknown",
                        username=info.get("username"),
                    )
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Processes can die mid-iteration — skip silently
                continue

        # Sort by CPU descending, return top N
        return sorted(processes, key=lambda p: p.cpu_percent, reverse=True)[:limit]

    def _calculate_health_score(
        self, cpu: CPUMetrics, ram: RAMMetrics, disk: DiskMetrics
    ) -> float:
        """
        Simple weighted health score (0-100).
        Lower usage = higher score.
        Full ML-based scoring added in Step 12.
        """
        cpu_score = max(0, 100 - cpu.usage_percent)
        ram_score = max(0, 100 - ram.usage_percent)
        disk_score = max(0, 100 - disk.usage_percent)

        return round((cpu_score * 0.4) + (ram_score * 0.4) + (disk_score * 0.2), 2)

    def snapshot(self) -> SystemSnapshot:
        """
        Full system snapshot — called by the API and the WebSocket streamer.
        """
        log.info("Taking system snapshot")

        cpu = self.get_cpu()
        ram = self.get_ram()
        disk = self.get_disk()
        network = self.get_network()
        processes = self.get_top_processes()
        health = self._calculate_health_score(cpu, ram, disk)

        return SystemSnapshot(
            timestamp=datetime.now(timezone.utc).isoformat(),
            cpu=cpu,
            ram=ram,
            disk=disk,
            network=network,
            top_processes=processes,
            health_score=health,
        )