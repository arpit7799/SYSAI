"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Zap, CheckCircle, XCircle, AlertTriangle, Play } from "lucide-react";

interface OptimizationAction {
  action: string;
  target: string;
  pid: number;
  detail: string;
}

interface OptimizationResult {
  status: string;
  actions: OptimizationAction[];
  recommendations: string[];
}

interface SummaryData {
  total_actions: number;
  successful: number;
  failed: number;
  recommendations: string[];
  recent: {
    id: number;
    executed_at: string;
    action_type: string;
    target: string;
    reason: string;
    success: number;
  }[];
}

export function OptimizerPanel() {
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [running, setRunning] = useState(false);
  const [mode, setMode] = useState<"safe" | "aggressive">("safe");

  const fetchSummary = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/optimize/summary");
      const json = await res.json() as SummaryData;
      setSummary(json);
    } catch {
      // silent
    }
  };

  useEffect(() => {
    fetchSummary();
    const interval = setInterval(fetchSummary, 30000);
    return () => clearInterval(interval);
  }, []);

  const runOptimization = async () => {
    setRunning(true);
    setResult(null);
    try {
      const res = await fetch("http://localhost:8000/api/v1/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode }),
      });
      const json = await res.json() as OptimizationResult;
      setResult(json);
      await fetchSummary();
    } catch {
      // silent
    } finally {
      setRunning(false);
    }
  };

  return (
    <div
      className="rounded-sm p-4 relative overflow-hidden"
      style={{
        backgroundColor: "#1c252e",
        border: "1px solid #ffffff10",
        clipPath: "polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 12px 100%, 0 calc(100% - 12px))",
      }}
    >
      {/* Top accent */}
      <div
        className="absolute top-0 left-0 right-0 h-px"
        style={{ background: "linear-gradient(90deg, #f59e0b, transparent)" }}
      />

      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Zap size={14} style={{ color: "#f59e0b" }} />
          <span
            className="text-xs tracking-[0.2em] font-bold"
            style={{ fontFamily: "var(--font-mono)", color: "#f59e0b" }}
          >
            AUTONOMOUS OPTIMIZER
          </span>
        </div>

        {/* Stats */}
        {summary && (
          <div className="flex items-center gap-3 text-xs" style={{ fontFamily: "var(--font-mono)" }}>
            <span style={{ color: "#00ff9d" }}>
              ✓ {summary.successful}
            </span>
            <span style={{ color: "#ff4655" }}>
              ✗ {summary.failed}
            </span>
            <span style={{ color: "#4a5568" }}>
              TOTAL {summary.total_actions}
            </span>
          </div>
        )}
      </div>

      {/* Recommendations */}
      {summary?.recommendations && (
        <div className="mb-4 space-y-1">
          {summary.recommendations.map((rec, i) => (
            <div key={i} className="flex items-start gap-2">
              <span style={{ color: "#f59e0b", fontSize: 10, marginTop: 2 }}>▶</span>
              <span
                className="text-xs"
                style={{ fontFamily: "var(--font-mono)", color: "#6272a4" }}
              >
                {rec}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Mode selector + Run button */}
      <div className="flex items-center gap-3 mb-4">
        <div className="flex rounded-sm overflow-hidden" style={{ border: "1px solid #ffffff15" }}>
          <button
            onClick={() => setMode("safe")}
            className="px-3 py-1.5 text-xs font-bold tracking-widest transition-colors"
            style={{
              fontFamily: "var(--font-mono)",
              backgroundColor: mode === "safe" ? "#00ff9d20" : "transparent",
              color: mode === "safe" ? "#00ff9d" : "#4a5568",
              borderRight: "1px solid #ffffff15",
            }}
          >
            SAFE
          </button>
          <button
            onClick={() => setMode("aggressive")}
            className="px-3 py-1.5 text-xs font-bold tracking-widest transition-colors"
            style={{
              fontFamily: "var(--font-mono)",
              backgroundColor: mode === "aggressive" ? "#ff465520" : "transparent",
              color: mode === "aggressive" ? "#ff4655" : "#4a5568",
            }}
          >
            AGGRESSIVE
          </button>
        </div>

        <motion.button
          onClick={runOptimization}
          disabled={running}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="flex items-center gap-2 px-4 py-1.5 text-xs font-bold tracking-widest transition-colors"
          style={{
            fontFamily: "var(--font-mono)",
            backgroundColor: running ? "#ffffff10" : "#f59e0b",
            color: running ? "#4a5568" : "#0f1115",
            clipPath: "polygon(0 0, calc(100% - 6px) 0, 100% 6px, 100% 100%, 6px 100%, 0 calc(100% - 6px))",
          }}
        >
          {running ? (
            <>
              <div className="w-3 h-3 border border-t-transparent rounded-full animate-spin" />
              RUNNING...
            </>
          ) : (
            <>
              <Play size={10} />
              RUN OPTIMIZER
            </>
          )}
        </motion.button>
      </div>

      {/* Result */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mb-4 p-3 rounded-sm"
            style={{
              backgroundColor: result.status === "healthy" ? "#00ff9d08" : "#f59e0b08",
              border: `1px solid ${result.status === "healthy" ? "#00ff9d20" : "#f59e0b20"}`,
            }}
          >
            <div className="flex items-center gap-2 mb-2">
              {result.status === "healthy" ? (
                <CheckCircle size={12} style={{ color: "#00ff9d" }} />
              ) : (
                <Zap size={12} style={{ color: "#f59e0b" }} />
              )}
              <span
                className="text-xs font-bold tracking-widest uppercase"
                style={{
                  fontFamily: "var(--font-mono)",
                  color: result.status === "healthy" ? "#00ff9d" : "#f59e0b",
                }}
              >
                {result.status === "healthy"
                  ? "System Healthy — No Action Needed"
                  : `${result.actions.length} Action${result.actions.length !== 1 ? "s" : ""} Taken`}
              </span>
            </div>

            {result.actions.length > 0 && (
              <div className="space-y-1 mt-2">
                {result.actions.map((action, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs"
                       style={{ fontFamily: "var(--font-mono)" }}>
                    <CheckCircle size={10} style={{ color: "#00ff9d" }} />
                    <span style={{ color: "#cdd6f4" }}>{action.target}</span>
                    <span style={{ color: "#4a5568" }}>—</span>
                    <span style={{ color: "#6272a4" }}>{action.detail}</span>
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Recent actions */}
      {summary && summary.recent.length > 0 && (
        <div>
          <p
            className="text-xs tracking-[0.2em] mb-2"
            style={{ fontFamily: "var(--font-mono)", color: "#4a5568" }}
          >
            RECENT ACTIONS
          </p>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {summary.recent.slice(0, 5).map((action) => (
              <div
                key={action.id}
                className="flex items-center gap-3 py-1.5 px-2 text-xs rounded-sm"
                style={{
                  fontFamily: "var(--font-mono)",
                  backgroundColor: "#ffffff04",
                  borderLeft: `2px solid ${action.success ? "#00ff9d40" : "#ff465540"}`,
                }}
              >
                {action.success ? (
                  <CheckCircle size={10} style={{ color: "#00ff9d", flexShrink: 0 }} />
                ) : (
                  <XCircle size={10} style={{ color: "#ff4655", flexShrink: 0 }} />
                )}
                <span style={{ color: "#cdd6f4" }} className="truncate flex-1">
                  {action.target}
                </span>
                <span style={{ color: "#4a5568" }} className="uppercase shrink-0">
                  {action.action_type}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}