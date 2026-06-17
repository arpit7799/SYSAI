import numpy as np
from typing import Dict, Tuple, List
from app.core.logger import log


class HealthScorer:
    """
    ML-based system health scoring engine.
    Considers: current metrics, trends, volatility, anomalies.
    Returns: health_score (0-100) + health_status (optimal/nominal/degraded/critical)
    """

    def __init__(self, history_size: int = 100):
        self.history_size = history_size

    def _trend_score(self, values: List[float]) -> Tuple[float, str]:
        """
        Analyze trend direction over recent history.
        Returns: trend_score (0-100), trend_direction
        """
        if len(values) < 5:
            return 50.0, "insufficient_data"

        recent = np.array(values[-20:], dtype=float)
        x = np.arange(len(recent))

        if len(recent) < 2:
            return 50.0, "stable"

        slope, _ = np.polyfit(x, recent, 1)

        # Normalize slope to trend score
        max_slope = np.max(np.abs(np.diff(recent))) if len(recent) > 1 else 1.0
        trend_magnitude = min(abs(slope), max_slope) / (max_slope + 1e-6)

        if slope > 0.1:
            # Increasing (bad)
            trend_score = max(0, 100 - trend_magnitude * 100)
            direction = "rising"
        elif slope < -0.1:
            # Decreasing (good)
            trend_score = min(100, 100 - trend_magnitude * 50)
            direction = "falling"
        else:
            trend_score = 100.0
            direction = "stable"

        return round(trend_score, 1), direction

    def _volatility_score(self, values: List[float]) -> float:
        """
        Analyze volatility (erratic behavior is unhealthy).
        Returns: volatility_score (0-100)
        """
        if len(values) < 2:
            return 100.0

        recent = np.array(values[-20:], dtype=float)
        std = np.std(recent)
        mean = np.mean(recent)

        # Coefficient of variation
        if mean < 1:
            return 100.0

        cv = (std / mean) * 100
        volatility_score = max(0, 100 - min(cv, 100))

        return round(volatility_score, 1)

    def _anomaly_score(self, current: float, values: List[float]) -> float:
        """
        Detect if current value is anomalous.
        Returns: anomaly_score (0-100, 100 = normal)
        """
        if len(values) < 5:
            return 100.0

        recent = np.array(values[-50:], dtype=float)
        mean = np.mean(recent)
        std = np.std(recent)

        if std < 1:
            return 100.0

        z_score = abs((current - mean) / std)

        if z_score > 3.0:
            return 0.0  # Critical anomaly
        elif z_score > 2.0:
            return 30.0  # High anomaly
        elif z_score > 1.5:
            return 60.0  # Moderate anomaly
        else:
            return 100.0  # Normal

    def score(
        self,
        cpu_history: List[float],
        ram_history: List[float],
        disk_history: List[float],
        current_cpu: float,
        current_ram: float,
        current_disk: float,
    ) -> Dict:
        """
        Compute comprehensive health score.
        Returns dict with: health_score, status, factors, trends
        """
        # Individual metric scores (0-100, lower = worse)
        cpu_score = max(0, 100 - current_cpu)
        ram_score = max(0, 100 - current_ram)
        disk_score = max(0, 100 - current_disk)

        # Trend analysis
        cpu_trend, cpu_dir = self._trend_score(cpu_history)
        ram_trend, ram_dir = self._trend_score(ram_history)
        disk_trend, disk_dir = self._trend_score(disk_history)

        # Volatility analysis
        cpu_vol = self._volatility_score(cpu_history)
        ram_vol = self._volatility_score(ram_history)
        disk_vol = self._volatility_score(disk_history)

        # Anomaly detection
        cpu_anom = self._anomaly_score(current_cpu, cpu_history)
        ram_anom = self._anomaly_score(current_ram, ram_history)
        disk_anom = self._anomaly_score(current_disk, disk_history)

        # Weighted composite health score
        # Current state: 40%, Trends: 30%, Volatility: 20%, Anomalies: 10%
        current_weight = 0.4
        trend_weight = 0.3
        volatility_weight = 0.2
        anomaly_weight = 0.1

        current = (cpu_score * 0.5 + ram_score * 0.3 + disk_score * 0.2)
        trends = (cpu_trend * 0.5 + ram_trend * 0.3 + disk_trend * 0.2)
        volatility = (cpu_vol * 0.5 + ram_vol * 0.3 + disk_vol * 0.2)
        anomalies = (cpu_anom * 0.5 + ram_anom * 0.3 + disk_anom * 0.2)

        health_score = (
            current * current_weight +
            trends * trend_weight +
            volatility * volatility_weight +
            anomalies * anomaly_weight
        )

        health_score = round(max(0, min(100, health_score)), 1)

        # Health status classification
        if health_score >= 80:
            status = "optimal"
        elif health_score >= 60:
            status = "nominal"
        elif health_score >= 40:
            status = "degraded"
        else:
            status = "critical"

        # Determine primary issue
        issues = []
        if current_cpu > 80:
            issues.append("high CPU")
        if current_ram > 85:
            issues.append("high memory")
        if current_disk > 90:
            issues.append("disk nearly full")
        if cpu_vol < 50:
            issues.append("CPU erratic")
        if ram_vol < 50:
            issues.append("memory erratic")

        return {
            "health_score": health_score,
            "status": status,
            "factors": {
                "current_metrics": round(current, 1),
                "trends": round(trends, 1),
                "volatility": round(volatility, 1),
                "anomalies": round(anomalies, 1),
            },
            "trends": {
                "cpu": cpu_dir,
                "ram": ram_dir,
                "disk": disk_dir,
            },
            "issues": issues if issues else ["System healthy"],
        }