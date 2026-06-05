import { useEffect, useRef, useState, useCallback } from "react";
import { SystemSnapshot } from "@/types/metrics";

const WS_URL = "ws://localhost:8000/ws/metrics";
const MAX_HISTORY = 60; // keep last 60 snapshots for charts

interface UseMetricsReturn {
  snapshot: SystemSnapshot | null;
  history: SystemSnapshot[];
  connected: boolean;
  error: string | null;
}

export function useMetrics(): UseMetricsReturn {
  const [snapshot, setSnapshot] = useState<SystemSnapshot | null>(null);
  const [history, setHistory] = useState<SystemSnapshot[]>([]);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout>>();

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        setError(null);
      };

      ws.onmessage = (event) => {
        const data: SystemSnapshot = JSON.parse(event.data);
        setSnapshot(data);
        setHistory((prev) => {
          const updated = [...prev, data];
          // Keep only last MAX_HISTORY entries
          return updated.slice(-MAX_HISTORY);
        });
      };

      ws.onclose = () => {
        setConnected(false);
        // Auto-reconnect after 2 seconds
        reconnectTimer.current = setTimeout(connect, 2000);
      };

      ws.onerror = () => {
        setError("WebSocket connection failed");
        ws.close();
      };
    } catch (err) {
      setError("Failed to create WebSocket");
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { snapshot, history, connected, error };
}