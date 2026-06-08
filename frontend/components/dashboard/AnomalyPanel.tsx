"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, Shield, Cpu, HardDrive, Activity, Zap } from "lucide-react";

interface AnomalyEvent {
  id: number;
  detected_at: string;
  severity: string;
  category: string;
  description: string;
  process_name: string | null;
}

interface AnomalySummary {
  total: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  recent: AnomalyEvent[];
}

const SEVERITY_COLORS: Record<string, string> = {
  critical: "#ff4655",
  high:     "#ff9500",
  medium:   "#ffcc00",
  low:      "#00ff9d",
};

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  cpu:     Cpu,
  ram:     Activity,
  disk:    HardDrive,
  process: Zap,
};

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  return `${Math.floor(mins / 60)}h ago`;
}

export function AnomalyPanel() {
  const [data, setData] = useState<AnomalySummary | null>(null);

  const fetchAnomalies = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/anomalies");
      const json = await res.json() as AnomalySummary;
      setData(json);
    } catch {
      // silent
    }
  };

  useEffect(() => {
    fetchAnomalies();
    const interval = setInterval(fetchAnomalies, 30000);
    return () => clearInterval(interval);
  }, []);

  const hasAlerts = data && data.total > 0;

  return (
    <div
      className="rounded-sm p-4 relative overflow-hidden"
      style={{
        backgroundColor: "#1c252e",
        border: `1px solid ${hasAlerts ? "#ff465530" : "#ffffff10"}`,
        clipPath: "polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 12px 100%, 0 calc(100% - 12px))",
      }}
    >
      {/* Top accent */}
      <div
        className="absolute top-0 left-0 right-0 h-px"
        style={{
          background: `linear-gradient(90deg, ${hasAlerts ? "#ff4655" : "#ffffff20"}, transparent)`,
        }}
      />

      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <AlertTriangle
            size={14}
            style={{ color: hasAlerts ? "#ff4655" : "#4a5568" }}
            className={hasAlerts ? "animate-pulse" : ""}
          />
          <span
            className="text-xs tracking-[0.2em] font-bold"
            style={{
              fontFamily: "var(--font-mono)",
              color: hasAlerts ? "#ff4655" : "#4a5568",
            }}
          >
            ANOMALY DETECTION
          </span>
        </div>

        {/* Summary badges */}
        {data && (
          <div className="flex items-center gap-2">
            {data.critical > 0 && (
              <span
                className="text-xs px-2 py-0.5 font-bold animate-pulse"
                style={{
                  fontFamily: "var(--font-mono)",
                  backgroundColor: "rgba(255,70,85,0.15)",
                  color: "#ff4655",
                  border: "1px solid #ff465540",
                }}
              >
                {data.critical} CRITICAL
              </span>
            )}
            {data.high > 0 && (
              <span
                className="text-xs px-2 py-0.5 font-bold"
                style={{
                  fontFamily: "var(--font-mono)",
                  backgroundColor: "rgba(255,149,0,0.15)",
                  color: "#ff9500",
                  border: "1px solid #ff950040",
                }}
              >
                {data.high} HIGH
              </span>
            )}
            {data.total === 0 && (
              <div className="flex items-center gap-1.5">
                <Shield size={12} style={{ color: "#00ff9d" }} />
                <span
                  className="text-xs"
                  style={{ fontFamily: "var(--font-mono)", color: "#00ff9d" }}
                >
                  ALL CLEAR
                </span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Event list */}
      {!data ? (
        <div className="text-center py-4">
          <span
            className="text-xs animate-pulse"
            style={{ fontFamily: "var(--font-mono)", color: "#4a5568" }}
          >
            SCANNING...
          </span>
        </div>
      ) : data.recent.length === 0 ? (
        <div className="flex items-center justify-center py-6 gap-2">
          <Shield size={16} style={{ color: "#00ff9d" }} />
          <span
            className="text-xs tracking-widest"
            style={{ fontFamily: "var(--font-mono)", color: "#00ff9d" }}
          >
            NO ANOMALIES DETECTED
          </span>
        </div>
      ) : (
        <div className="space-y-2 max-h-48 overflow-y-auto">
          <AnimatePresence>
            {data.recent.slice(0, 6).map((event) => {
              const color = SEVERITY_COLORS[event.severity] ?? "#4a5568";
              const Icon = CATEGORY_ICONS[event.category] ?? AlertTriangle;

              return (
                <motion.div
                  key={event.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-start gap-3 py-2 px-3 rounded-sm"
                  style={{
                    backgroundColor: `${color}08`,
                    borderLeft: `2px solid ${color}`,
                  }}
                >
                  <Icon size={12} style={{ color, marginTop: 2, flexShrink: 0 }} />
                  <div className="flex-1 min-w-0">
                    <p
                      className="text-xs leading-relaxed"
                      style={{ fontFamily: "var(--font-mono)", color: "#cdd6f4" }}
                    >
                      {event.description}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <span
                        className="text-xs uppercase font-bold"
                        style={{ color }}
                      >
                        {event.severity}
                      </span>
                      <span style={{ color: "#4a5568" }}>·</span>
                      <span
                        className="text-xs"
                        style={{ fontFamily: "var(--font-mono)", color: "#4a5568" }}
                      >
                        {event.category.toUpperCase()}
                      </span>
                      <span style={{ color: "#4a5568" }}>·</span>
                      <span
                        className="text-xs"
                        style={{ fontFamily: "var(--font-mono)", color: "#4a5568" }}
                      >
                        {timeAgo(event.detected_at)}
                      </span>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      )}

      {/* Footer */}
      {data && data.total > 6 && (
        <p
          className="text-xs mt-3 text-center"
          style={{ fontFamily: "var(--font-mono)", color: "#4a5568" }}
        >
          +{data.total - 6} MORE EVENTS IN HISTORY
        </p>
      )}
    </div>
  );
}