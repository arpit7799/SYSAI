import { useEffect, useState } from 'react';
import { SystemSnapshot } from '@/types/metrics';

interface UseMetricsReturn {
  snapshot: SystemSnapshot | null;
  history: SystemSnapshot[];
  connected: boolean;
  error: string | null;
}

// Determine backend URL based on environment
const getBackendUrl = () => {
  // Server-side (SSR): use Docker internal hostname directly
  if (typeof window === 'undefined') {
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }
  // Client-side (browser): use relative URLs.
  // Next.js rewrites in next.config.js will proxy /api/* to the backend.
  // This avoids the browser trying to resolve Docker's internal 'backend' hostname.
  return '';
};

export const useMetrics = (): UseMetricsReturn => {
  const [snapshot, setSnapshot] = useState<SystemSnapshot | null>(null);
  const [history, setHistory] = useState<SystemSnapshot[]>([]);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const backendUrl = getBackendUrl();

  useEffect(() => {
    let isMounted = true;

    const fetchMetrics = async () => {
      try {
        const snapshotResponse = await fetch(
          `${backendUrl}/api/v1/metrics/snapshot`
        );

        if (!snapshotResponse.ok) {
          throw new Error(
            `Failed to fetch snapshot: ${snapshotResponse.statusText}`
          );
        }

        const data = await snapshotResponse.json();

        const historyResponse = await fetch(
          `${backendUrl}/api/v1/metrics/history?limit=100`
        );

        let historyData: SystemSnapshot[] = [];
        if (historyResponse.ok) {
          const rawHistory = await historyResponse.json();
          historyData = rawHistory.map((item: any) => ({
            timestamp: item.timestamp,
            cpu: {
              usage_percent: item.cpu_percent || 0,
              per_core_percent: item.cpu?.per_core_percent || [],
              frequency_mhz: item.cpu?.frequency_mhz || 0,
              core_count: 0,
              thread_count: 0,
            },
            ram: {
              total_gb: 0,
              used_gb: item.ram_used_gb || 0,
              available_gb: 0,
              usage_percent: item.ram_percent || 0,
              swap_total_gb: 0,
              swap_used_gb: 0,
              swap_percent: 0,
            },
            disk: {
              total_gb: 0,
              used_gb: 0,
              free_gb: 0,
              usage_percent: item.disk_percent || 0,
              read_mb_per_sec: 0,
              write_mb_per_sec: 0,
            },
            network: {
              bytes_sent_mb: 0,
              bytes_recv_mb: 0,
              packets_sent: 0,
              packets_recv: 0,
            },
            top_processes: [],
            health_score: item.health_score || 0,
          }));
        }

        if (isMounted) {
          const transformedSnapshot: SystemSnapshot = {
            timestamp: data.timestamp,
            cpu: {
              usage_percent: data.cpu?.usage_percent || 0,
              per_core_percent: data.cpu?.per_core_percent || [],
              frequency_mhz: data.cpu?.frequency_mhz || 0,
              core_count: data.cpu?.core_count || 0,
              thread_count: data.cpu?.thread_count || 0,
            },
            ram: {
              total_gb: data.ram?.total_gb || 0,
              used_gb: data.ram?.used_gb || 0,
              available_gb: data.ram?.available_gb || 0,
              usage_percent: data.ram?.usage_percent || 0,
              swap_total_gb: data.ram?.swap_total_gb || 0,
              swap_used_gb: data.ram?.swap_used_gb || 0,
              swap_percent: data.ram?.swap_percent || 0,
            },
            disk: {
              total_gb: data.disk?.total_gb || 0,
              used_gb: data.disk?.used_gb || 0,
              free_gb: data.disk?.free_gb || 0,
              usage_percent: data.disk?.usage_percent || 0,
              read_mb_per_sec: data.disk?.read_mb_per_sec || 0,
              write_mb_per_sec: data.disk?.write_mb_per_sec || 0,
            },
            network: {
              bytes_sent_mb: data.network?.bytes_sent_mb || 0,
              bytes_recv_mb: data.network?.bytes_recv_mb || 0,
              packets_sent: data.network?.packets_sent || 0,
              packets_recv: data.network?.packets_recv || 0,
            },
            top_processes: data.top_processes || [],
            health_score: data.health_score || 0,
          };

          setSnapshot(transformedSnapshot);
          setHistory(historyData);
          setConnected(true);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Unknown error');
          setConnected(false);
        }
      }
    };

    fetchMetrics();
    const intervalId = setInterval(fetchMetrics, 5000);

    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, [backendUrl]);

  return {
    snapshot,
    history,
    connected,
    error,
  };
};