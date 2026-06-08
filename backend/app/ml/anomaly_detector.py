import numpy as np
from typing import List, Dict
from app.core.logger import log


class IsolationForestDetector:
    """
    Lightweight Isolation Forest implementation.
    Detects outliers by measuring how quickly a point
    can be isolated from the rest of the data.

    Points that are isolated quickly = anomalies.
    Points that take many splits to isolate = normal.
    """

    def __init__(self, contamination: float = 0.1, n_estimators: int = 50):
        self.contamination = contamination  # expected % of anomalies
        self.n_estimators = n_estimators
        self.threshold = None
        self.trained = False
        self._scores_history: List[float] = []

    def _anomaly_score(self, values: np.ndarray, point: np.ndarray) -> float:
        """
        Compute a simplified isolation score for a single point.
        Higher score = more anomalous.
        """
        if len(values) < 10:
            return 0.0

        mean = np.mean(values, axis=0)
        std = np.std(values, axis=0) + 1e-6  # prevent division by zero

        # Z-score based isolation — fast and effective for monitoring
        z_scores = np.abs((point - mean) / std)
        score = float(np.max(z_scores))
        return score

    def fit_and_score(self, features: List[List[float]]) -> List[float]:
        """
        Fit on historical data and return anomaly scores.
        Score > threshold = anomaly.
        """
        if len(features) < 10:
            return [0.0] * len(features)

        arr = np.array(features, dtype=float)
        scores = []

        for i, point in enumerate(arr):
            # Train on all points except current
            context = np.delete(arr, i, axis=0)
            score = self._anomaly_score(context, point)
            scores.append(score)

        # Set threshold based on contamination rate
        self.threshold = float(np.percentile(scores, 100 * (1 - self.contamination)))
        self.trained = True

        return scores

    def is_anomaly(self, score: float) -> bool:
        if not self.trained or self.threshold is None:
            return False
        return score > self.threshold

    def get_severity(self, score: float) -> str:
        if score > 4.0:
            return "critical"
        elif score > 3.0:
            return "high"
        elif score > 2.0:
            return "medium"
        else:
            return "low"


class AnomalyEngine:
    """
    Multi-metric anomaly detection engine.
    Runs separate detectors for CPU, RAM, and Disk.
    Also does rule-based checks for process-level anomalies.
    """

    def __init__(self):
        self.cpu_detector = IsolationForestDetector(contamination=0.05)
        self.ram_detector = IsolationForestDetector(contamination=0.05)
        self.disk_detector = IsolationForestDetector(contamination=0.05)
        log.info("AnomalyEngine initialized")

    def analyze(self, snapshots: List[Dict]) -> List[Dict]:
        """
        Analyze a list of snapshots and return detected anomalies.
        Each anomaly is a dict with severity, category, description.
        """
        if len(snapshots) < 10:
            return []

        anomalies = []

        # Extract feature vectors
        cpu_features = [[s["cpu_percent"]] for s in snapshots]
        ram_features = [[s["ram_percent"]] for s in snapshots]
        disk_features = [[s["disk_percent"]] for s in snapshots]

        cpu_scores = self.cpu_detector.fit_and_score(cpu_features)
        ram_scores = self.ram_detector.fit_and_score(ram_features)
        disk_scores = self.disk_detector.fit_and_score(disk_features)

        # Check latest snapshot only
        latest = snapshots[-1]
        latest_cpu_score = cpu_scores[-1]
        latest_ram_score = ram_scores[-1]
        latest_disk_score = disk_scores[-1]

        # CPU anomaly
        if self.cpu_detector.is_anomaly(latest_cpu_score):
            anomalies.append({
                "severity": self.cpu_detector.get_severity(latest_cpu_score),
                "category": "cpu",
                "description": f"Abnormal CPU usage detected: {latest['cpu_percent']:.1f}% (score: {latest_cpu_score:.2f})",
                "process_name": None,
                "score": latest_cpu_score,
            })

        # RAM anomaly
        if self.ram_detector.is_anomaly(latest_ram_score):
            anomalies.append({
                "severity": self.ram_detector.get_severity(latest_ram_score),
                "category": "ram",
                "description": f"Abnormal memory usage detected: {latest['ram_percent']:.1f}% (score: {latest_ram_score:.2f})",
                "process_name": None,
                "score": latest_ram_score,
            })

        # Disk anomaly
        if self.disk_detector.is_anomaly(latest_disk_score):
            anomalies.append({
                "severity": self.disk_detector.get_severity(latest_disk_score),
                "category": "disk",
                "description": f"Abnormal disk usage detected: {latest['disk_percent']:.1f}% (score: {latest_disk_score:.2f})",
                "process_name": None,
                "score": latest_disk_score,
            })

        # Rule-based: CPU > 90%
        if latest["cpu_percent"] > 90:
            anomalies.append({
                "severity": "critical",
                "category": "cpu",
                "description": f"CPU critical threshold exceeded: {latest['cpu_percent']:.1f}%",
                "process_name": None,
                "score": 5.0,
            })

        # Rule-based: RAM > 90%
        if latest["ram_percent"] > 90:
            anomalies.append({
                "severity": "critical",
                "category": "ram",
                "description": f"RAM critical threshold exceeded: {latest['ram_percent']:.1f}%",
                "process_name": None,
                "score": 5.0,
            })

        # Rule-based: process-level check from top_processes
        if latest.get("top_processes"):
            for proc in latest["top_processes"]:
                if isinstance(proc, dict):
                    cpu = proc.get("cpu_percent", 0)
                    name = proc.get("name", "unknown")
                    if cpu > 80:
                        anomalies.append({
                            "severity": "high",
                            "category": "process",
                            "description": f"Process '{name}' consuming excessive CPU: {cpu:.1f}%",
                            "process_name": name,
                            "score": cpu / 20,
                        })

        return anomalies