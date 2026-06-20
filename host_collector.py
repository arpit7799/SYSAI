"""
Host System Metrics Collector
Runs on macOS natively (NOT in Docker)
Collects real system metrics and sends to SYSAI backend
"""

import psutil
import requests
import time
import json
from datetime import datetime, timezone
from typing import Dict, List

BACKEND_URL = "http://localhost:8000"
INGEST_ENDPOINT = f"{BACKEND_URL}/api/v1/metrics/ingest"
INTERVAL_SECONDS = 5


class HostCollector:
    """Collect real host system metrics"""

    def get_cpu(self) -> Dict:
        """Get real CPU metrics"""
        per_core = psutil.cpu_percent(interval=0.1, percpu=True)
        return {
            "usage_percent": psutil.cpu_percent(interval=0.1),
            "per_core_percent": per_core,
            "frequency_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            "core_count": psutil.cpu_count(logical=False),
            "thread_count": psutil.cpu_count(logical=True),
        }

    def get_ram(self) -> Dict:
        """Get real RAM metrics"""
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "total_gb": vm.total / (1024**3),
            "used_gb": vm.used / (1024**3),
            "available_gb": vm.available / (1024**3),
            "usage_percent": vm.percent,
            "swap_total_gb": swap.total / (1024**3),
            "swap_used_gb": swap.used / (1024**3),
            "swap_percent": swap.percent,
        }

    def get_disk(self) -> Dict:
        """Get real disk metrics"""
        disk = psutil.disk_usage("/")
        io = psutil.disk_io_counters()
        return {
            "total_gb": disk.total / (1024**3),
            "used_gb": disk.used / (1024**3),
            "free_gb": disk.free / (1024**3),
            "usage_percent": disk.percent,
            "read_mb_per_sec": io.read_bytes / (1024**2) if io else 0,
            "write_mb_per_sec": io.write_bytes / (1024**2) if io else 0,
        }

    def get_network(self) -> Dict:
        """Get real network metrics"""
        net = psutil.net_io_counters()
        return {
            "bytes_sent_mb": net.bytes_sent / (1024**2),
            "bytes_recv_mb": net.bytes_recv / (1024**2),
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
        }

    def get_top_processes(self, limit: int = 10) -> List[Dict]:
        """Get top processes by CPU usage (real host processes)"""
        processes = []
        try:
            for proc in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_percent", "status", "username"]
            ):
                try:
                    processes.append({
                        "pid": proc.info["pid"],
                        "name": proc.info["name"],
                        "cpu_percent": proc.info["cpu_percent"] or 0,
                        "memory_percent": proc.info["memory_percent"] or 0,
                        "status": proc.info["status"],
                        "username": proc.info["username"],
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            print(f"Warning: Could not collect processes: {e}")

        # Sort by CPU and take top N
        processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
        return processes[:limit]

    def collect(self) -> Dict:
        """Collect all metrics and return as dict"""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu": self.get_cpu(),
            "ram": self.get_ram(),
            "disk": self.get_disk(),
            "network": self.get_network(),
            "top_processes": self.get_top_processes(),
        }

    def send_to_backend(self, metrics: Dict) -> bool:
        """Send metrics to SYSAI backend"""
        try:
            response = requests.post(
                INGEST_ENDPOINT,
                json=metrics,
                timeout=5,
                headers={"Content-Type": "application/json"},
            )
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Backend error: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to {BACKEND_URL}")
            return False
        except Exception as e:
            print(f"❌ Error sending metrics: {e}")
            return False

    def run(self):
        """Main loop"""
        print(f"🟢 Host Collector started")
        print(f"📡 Sending metrics to {INGEST_ENDPOINT}")
        print(f"⏱️  Interval: {INTERVAL_SECONDS} seconds")
        print()

        count = 0
        while True:
            try:
                metrics = self.collect()
                success = self.send_to_backend(metrics)

                count += 1
                status = "✅" if success else "❌"
                cpu = metrics["cpu"]["usage_percent"]
                ram = metrics["ram"]["usage_percent"]
                procs = len(metrics["top_processes"])

                print(
                    f"{status} #{count} | CPU: {cpu:5.1f}% | RAM: {ram:5.1f}% | "
                    f"Processes: {procs} | {metrics['timestamp']}"
                )

                time.sleep(INTERVAL_SECONDS)
            except KeyboardInterrupt:
                print("\n🛑 Host Collector stopped")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    collector = HostCollector()
    collector.run()