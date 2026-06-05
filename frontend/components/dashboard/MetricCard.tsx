"use client";

import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";
import { getStatusColor } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string;
  subtitle: string;
  percent: number;
  icon: LucideIcon;
  index: number;
}

export function MetricCard({
  title, value, subtitle, percent, icon: Icon, index
}: MetricCardProps) {
  const color = getStatusColor(percent);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="rounded-xl p-5 border"
      style={{
        backgroundColor: "var(--bg-card)",
        borderColor: "var(--border)",
      }}
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-xs uppercase tracking-widest mb-1"
             style={{ color: "var(--text-secondary)" }}>
            {title}
          </p>
          <p className="text-2xl font-bold font-mono" style={{ color }}>
            {value}
          </p>
          <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
            {subtitle}
          </p>
        </div>
        <div className="p-2 rounded-lg" style={{ backgroundColor: "var(--bg-secondary)" }}>
          <Icon size={18} style={{ color }} />
        </div>
      </div>

      {/* Progress bar */}
      <div className="h-1.5 rounded-full w-full"
           style={{ backgroundColor: "var(--bg-secondary)" }}>
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
          animate={{ width: `${Math.min(percent, 100)}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        />
      </div>
      <p className="text-xs mt-1.5 text-right font-mono"
         style={{ color: "var(--text-muted)" }}>
        {percent.toFixed(1)}%
      </p>
    </motion.div>
  );
}