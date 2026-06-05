"use client";

import { motion } from "framer-motion";
import { getHealthColor } from "@/lib/utils";
import { Shield } from "lucide-react";

interface HealthScoreProps {
  score: number;
}

export function HealthScore({ score }: HealthScoreProps) {
  const color = getHealthColor(score);
  const label =
    score >= 80 ? "OPTIMAL" :
    score >= 60 ? "GOOD" :
    score >= 40 ? "DEGRADED" : "CRITICAL";

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="rounded-xl p-5 border flex items-center gap-5"
      style={{
        backgroundColor: "var(--bg-card)",
        borderColor: "var(--border)",
      }}
    >
      <div className="relative flex items-center justify-center w-16 h-16">
        <svg className="w-16 h-16 -rotate-90" viewBox="0 0 64 64">
          <circle cx="32" cy="32" r="26"
            fill="none" stroke="var(--bg-secondary)" strokeWidth="6" />
          <motion.circle cx="32" cy="32" r="26"
            fill="none" stroke={color} strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={`${2 * Math.PI * 26}`}
            animate={{
              strokeDashoffset: 2 * Math.PI * 26 * (1 - score / 100)
            }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          />
        </svg>
        <span className="absolute text-sm font-bold font-mono"
              style={{ color }}>
          {score.toFixed(0)}
        </span>
      </div>

      <div>
        <div className="flex items-center gap-2 mb-1">
          <Shield size={14} style={{ color }} />
          <span className="text-xs uppercase tracking-widest"
                style={{ color: "var(--text-secondary)" }}>
            System Health
          </span>
        </div>
        <p className="text-xl font-bold tracking-wider" style={{ color }}>
          {label}
        </p>
        <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
          AI scoring active in Step 12
        </p>
      </div>
    </motion.div>
  );
}