export interface CPUMetrics {
  usage_percent: number;
  per_core_percent: number[];
  frequency_mhz: number;
  core_count: number;
  thread_count: number;
}

export interface RAMMetrics {
  total_gb: number;
  used_gb: number;
  available_gb: number;
  usage_percent: number;
  swap_total_gb: number;
  swap_used_gb: number;
  swap_percent: number;
}

export interface DiskMetrics {
  total_gb: number;
  used_gb: number;
  free_gb: number;
  usage_percent: number;
  read_mb_per_sec: number;
  write_mb_per_sec: number;
}

export interface NetworkMetrics {
  bytes_sent_mb: number;
  bytes_recv_mb: number;
  packets_sent: number;
  packets_recv: number;
}

export interface ProcessInfo {
  pid: number;
  name: string;
  cpu_percent: number;
  memory_percent: number;
  status: string;
  username: string | null;
}

export interface SystemSnapshot {
  timestamp: string;
  cpu: CPUMetrics;
  ram: RAMMetrics;
  disk: DiskMetrics;
  network: NetworkMetrics;
  top_processes: ProcessInfo[];
  health_score: number;
}