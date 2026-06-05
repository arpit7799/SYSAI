"use client";

import { useEffect, useState } from "react";
import { Wifi, WifiOff, Clock } from "lucide-react";
import { useMetricsContext } from "@/components/providers/MetricsProvider";

export function Navbar() {
  const { connected } = useMetricsContext();
  const [time, setTime] = useState("");

  useEffect(() => {
    const update = () => setTime(new Date().toLocaleTimeString());
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header
      className="h-14 flex items-center justify-between px-6 border-b"
      style={{
        backgroundColor: "var(--bg-secondary)",
        borderColor: "var(--border)",
      }}
    >
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium" style={{ color: "var(--text-secondary)" }}>
          Autonomous OS Optimization Engine
        </span>
      </div>

      <div className="flex items-center gap-6">
        {/* Connection status */}
        <div className="flex items-center gap-2">
          {connected ? (
            <>
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              <Wifi size={14} style={{ color: "var(--accent-green)" }} />
              <span className="text-xs" style={{ color: "var(--accent-green)" }}>
                LIVE
              </span>
            </>
          ) : (
            <>
              <span className="w-2 h-2 rounded-full bg-red-400" />
              <WifiOff size={14} style={{ color: "var(--accent-red)" }} />
              <span className="text-xs" style={{ color: "var(--accent-red)" }}>
                DISCONNECTED
              </span>
            </>
          )}
        </div>

        {/* Clock */}
        <div className="flex items-center gap-2">
          <Clock size={14} style={{ color: "var(--text-secondary)" }} />
          <span className="text-xs font-mono" style={{ color: "var(--text-secondary)" }}>
            {time}
          </span>
        </div>
      </div>
    </header>
  );
}