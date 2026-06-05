"use client";

import { motion } from "framer-motion";
import { Zap, TrendingUp } from "lucide-react";

interface Props { score: number; }

export function HealthScore({ score }: Props) {
  const isCritical = score < 50;
  const color = isCritical ? "var(--valorant-red)" : "var(--text-primary)";
  const label = isCritical ? "CRITICAL" : "OPTIMAL";

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="tactical-card clip-chamfer p-5 flex items-center gap-8 relative overflow-hidden"
    >
      {/* Score Block */}
      <div className="relative flex-shrink-0 w-24 h-24 bg-[var(--bg-primary)] clip-chamfer flex flex-col items-center justify-center border-l-4 border-[var(--valorant-red)]">
        <span
          className="text-4xl font-black leading-none"
          style={{ fontFamily: "var(--font-display)", color: "var(--text-bright)" }}
        >
          {score.toFixed(0)}
        </span>
        <span
          className="text-[10px] font-bold tracking-widest uppercase mt-1"
          style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}
        >
          Score
        </span>
      </div>

      {/* Info */}
      <div className="relative z-10 flex-1 border-l-2 border-[var(--border)] pl-6">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-2 h-2 bg-[var(--valorant-red)] rotate-45" />
          <span
            className="text-xs font-bold tracking-[0.2em] uppercase"
            style={{ fontFamily: "var(--font-display)", color: "var(--text-secondary)" }}
          >
            System Health Status
          </span>
        </div>
        <p
          className="text-3xl font-black mb-1 uppercase tracking-wide"
          style={{ fontFamily: "var(--font-display)", color }}
        >
          {label}
        </p>
        <p
          className="text-sm font-bold uppercase"
          style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}
        >
          Combat readiness verified
        </p>
      </div>

      {/* Right stats */}
      <div className="relative z-10 space-y-4 border-l-2 border-[var(--border)] pl-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Zap size={14} className="text-[var(--text-secondary)]" />
            <span className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]" style={{ fontFamily: "var(--font-display)" }}>
              Performance
            </span>
          </div>
          <div className="h-1.5 w-32 bg-[var(--bg-primary)] overflow-hidden">
            <div className="h-full bg-[var(--text-primary)]" style={{ width: `${Math.min(score + 5, 100)}%` }} />
          </div>
        </div>
        <div>
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp size={14} className="text-[var(--text-secondary)]" />
            <span className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]" style={{ fontFamily: "var(--font-display)" }}>
              Stability
            </span>
          </div>
          <div className="h-1.5 w-32 bg-[var(--bg-primary)] overflow-hidden">
            <div className="h-full bg-[var(--text-primary)]" style={{ width: `${Math.max(score - 3, 0)}%` }} />
          </div>
        </div>
      </div>
    </motion.div>
  );
}