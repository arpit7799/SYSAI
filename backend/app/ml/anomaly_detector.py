import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from app.core.logger import log


class AnomalyDetector:
    """
    Production-grade anomaly detector with:
    - Warm-up period (no alerts in first 5 minutes)
    - Dynamic baseline (last 30-50 samples)
    - Hybrid scoring (Z-score + absolute thresholds)
    - Confidence scoring
    - Reduced false positives
    """

    def __init__(self, 
                 min_warmup_samples: int = 60,  # 5 minutes at 1 sample/5 sec
                 baseline_window: int = 30,      # Use last 30 samples for mean/std
                 z_threshold: float = 2.5,       # Only flag if Z > 2.5
                 contamination: float = 0.01):   # 1% expected anomalies, not 5%
        
        self.min_warmup_samples = min_warmup_samples
        self.baseline_window = baseline_window
        self.z_threshold = z_threshold
        self.contamination = contamination
        self.sample_count = 0
        self.is_warmed_up = False

    def _get_baseline(self, values: List[float]) -> Tuple[float, float]:
        """
        Compute mean and std from recent samples only.
        Uses last N samples, not all history.
        """
        if len(values) < self.baseline_window:
            recent = values
        else:
            recent = values[-self.baseline_window:]
        
        arr = np.array(recent, dtype=float)
        mean = float(np.mean(arr))
        std = float(np.std(arr))
        
        return mean, std

    def _compute_z_score(self, value: float, mean: float, std: float) -> float:
        """
        Compute Z-score with protection against division by zero.
        """
        if std < 0.5:  # Very low variance — Z-score unreliable
            return 0.0
        
        z_score = abs((value - mean) / (std + 1e-6))
        return z_score

    def detect(self, values: List[float], current_value: float) -> Dict:
        """
        Check if current value is anomalous.
        Returns: {
            is_anomaly: bool,
            severity: str,
            z_score: float,
            confidence: float,
            reason: str
        }
        """
        self.sample_count = len(values)

        # Warm-up check
        if self.sample_count < self.min_warmup_samples:
            return {
                "is_anomaly": False,
                "severity": "none",
                "z_score": 0.0,
                "confidence": 0.0,
                "reason": f"System warming up ({self.sample_count}/{self.min_warmup_samples} samples)",
            }

        if not self.is_warmed_up:
            self.is_warmed_up = True
            log.info("Anomaly detector warmed up")

        # Not enough data for Z-score
        if len(values) < 3:
            return {
                "is_anomaly": False,
                "severity": "none",
                "z_score": 0.0,
                "confidence": 0.0,
                "reason": "Insufficient data",
            }

        mean, std = self._get_baseline(values)
        z_score = self._compute_z_score(current_value, mean, std)

        # Anomaly flags
        is_statistical_anomaly = z_score > self.z_threshold and std >= 0.5
        
        # Compute confidence (how sure are we?)
        confidence = min(100, max(0, (z_score / self.z_threshold) * 100))

        # If no statistical anomaly and low variance, don't flag
        if not is_statistical_anomaly:
            return {
                "is_anomaly": False,
                "severity": "none",
                "z_score": z_score,
                "confidence": 0.0,
                "reason": f"Within normal range (Z={z_score:.2f}, mean={mean:.1f}, std={std:.2f})",
            }

        # Statistical anomaly detected — now check severity
        return {
            "is_anomaly": True,
            "severity": "medium",  # Statistical anomaly, but not severe
            "z_score": z_score,
            "confidence": confidence,
            "reason": f"Deviation from baseline (Z={z_score:.2f}, value={current_value:.1f}, baseline={mean:.1f}±{std:.1f})",
        }


class AnomalyEngine:
    """
    Multi-metric anomaly detection with hybrid scoring.
    Uses both statistical outlier detection AND absolute thresholds.
    """

    def __init__(self):
        self.cpu_detector = AnomalyDetector(min_warmup_samples=60)
        self.ram_detector = AnomalyDetector(min_warmup_samples=60)
        self.disk_detector = AnomalyDetector(min_warmup_samples=60)
        log.info("AnomalyEngine initialized (production-grade)")

    def analyze(self, snapshots: List[Dict]) -> List[Dict]:
        """
        Comprehensive anomaly analysis with reduced false positives.
        """
        if len(snapshots) < 3:
            return []

        latest = snapshots[-1]
        cpu_pct = latest.get("cpu_percent", 0)
        ram_pct = latest.get("ram_percent", 0)
        disk_pct = latest.get("disk_percent", 0)

        # Extract histories
        cpu_history = [float(s.get("cpu_percent", 0)) for s in snapshots]
        ram_history = [float(s.get("ram_percent", 0)) for s in snapshots]
        disk_history = [float(s.get("disk_percent", 0)) for s in snapshots]

        anomalies = []

        # ─── CPU ANALYSIS ───────────────────────────────────────────────────────

        cpu_result = self.cpu_detector.detect(cpu_history, cpu_pct)

        if cpu_pct > 95:
            # Absolute critical threshold
            anomalies.append({
                "severity": "critical",
                "category": "cpu",
                "description": f"CPU CRITICAL: {cpu_pct:.1f}% (threshold: >95%)",
                "process_name": None,
                "score": 5.0,
                "confidence": 100.0,
            })
        elif cpu_pct > 85:
            # Absolute high threshold
            anomalies.append({
                "severity": "high",
                "category": "cpu",
                "description": f"CPU HIGH: {cpu_pct:.1f}% (threshold: >85%)",
                "process_name": None,
                "score": 3.5,
                "confidence": 100.0,
            })
        elif cpu_result["is_anomaly"]:
            # Statistical anomaly only
            anomalies.append({
                "severity": "medium",
                "category": "cpu",
                "description": f"CPU anomaly detected: {cpu_pct:.1f}% (Z={cpu_result['z_score']:.2f})",
                "process_name": None,
                "score": 2.0,
                "confidence": cpu_result["confidence"],
            })

        # ─── RAM ANALYSIS ───────────────────────────────────────────────────────

        ram_result = self.ram_detector.detect(ram_history, ram_pct)

        if ram_pct > 95:
            anomalies.append({
                "severity": "critical",
                "category": "ram",
                "description": f"MEMORY CRITICAL: {ram_pct:.1f}% (threshold: >95%)",
                "process_name": None,
                "score": 5.0,
                "confidence": 100.0,
            })
        elif ram_pct > 90:
            anomalies.append({
                "severity": "high",
                "category": "ram",
                "description": f"MEMORY HIGH: {ram_pct:.1f}% (threshold: >90%)",
                "process_name": None,
                "score": 3.5,
                "confidence": 100.0,
            })
        elif ram_result["is_anomaly"]:
            # Only flag if AND we have confidence AND it's high enough
            if ram_result["confidence"] > 60 and ram_pct > 30:
                anomalies.append({
                    "severity": "medium",
                    "category": "ram",
                    "description": f"Memory anomaly: {ram_pct:.1f}% (Z={ram_result['z_score']:.2f})",
                    "process_name": None,
                    "score": 2.0,
                    "confidence": ram_result["confidence"],
                })

        # ─── DISK ANALYSIS ──────────────────────────────────────────────────────

        disk_result = self.disk_detector.detect(disk_history, disk_pct)

        if disk_pct > 95:
            anomalies.append({
                "severity": "critical",
                "category": "disk",
                "description": f"DISK CRITICAL: {disk_pct:.1f}% (threshold: >95%)",
                "process_name": None,
                "score": 5.0,
                "confidence": 100.0,
            })
        elif disk_pct > 85:
            anomalies.append({
                "severity": "high",
                "category": "disk",
                "description": f"DISK HIGH: {disk_pct:.1f}% (threshold: >85%)",
                "process_name": None,
                "score": 3.5,
                "confidence": 100.0,
            })
        # Note: Don't flag disk statistical anomalies — disk rarely changes, false positive magnet

        # ─── PROCESS-LEVEL CHECKS ──────────────────────────────────────────────

        if latest.get("top_processes"):
            for proc in latest["top_processes"]:
                if isinstance(proc, dict):
                    cpu = proc.get("cpu_percent", 0)
                    name = proc.get("name", "unknown")
                    if cpu > 80:
                        anomalies.append({
                            "severity": "high",
                            "category": "process",
                            "description": f"Process '{name}' consuming {cpu:.1f}% CPU",
                            "process_name": name,
                            "score": 3.5,
                            "confidence": 100.0,
                        })

        if anomalies:
            log.info("Anomalies detected", count=len(anomalies), cpu=cpu_pct, ram=ram_pct)

        return anomalies