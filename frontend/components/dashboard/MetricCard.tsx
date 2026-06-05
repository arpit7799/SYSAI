"use client";

import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";

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
  const isHigh = percent >= 85;
  const color = isHigh ? "var(--valorant-red)" : "var(--text-primary)";
  const bgColor = isHigh ? "var(--valorant-red)" : "var(--border-bright)";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.4 }}
      className="tactical-card clip-chamfer p-4 relative group hover:bg-[var(--bg-card-hover)] transition-colors duration-300 cursor-default overflow-hidden"
    >
      {/* Decal Watermark */}
      <div 
        className="absolute inset-0 z-0 opacity-10 mix-blend-overlay group-hover:opacity-20 transition-opacity duration-300 pointer-events-none"
        style={{ backgroundImage: "url('/cyber_decal.png')", backgroundSize: "cover", backgroundPosition: "center" }}
      />
      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <p
              className="text-xs font-bold tracking-[0.1em] mb-1 uppercase"
              style={{ fontFamily: "var(--font-display)", color: "var(--text-secondary)" }}
            >
              {title}
            </p>
            <p
              className="text-3xl font-black leading-none"
              style={{ fontFamily: "var(--font-display)", color: "var(--text-bright)" }}
            >
              {value}
            </p>
          </div>
          <div
            className="p-2 bg-[var(--bg-secondary)] clip-chamfer-tl transition-colors duration-300 group-hover:bg-[var(--valorant-red)]"
          >
            <Icon size={20} className="text-[var(--text-secondary)] group-hover:text-white transition-colors duration-300" />
          </div>
        </div>

        {/* Bar */}
        <div className="h-1.5 w-full mb-3 bg-[var(--bg-primary)] overflow-hidden relative">
          <motion.div
            className="h-full absolute left-0 top-0"
            style={{ backgroundColor: bgColor }}
            animate={{ width: `${Math.min(percent, 100)}%` }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          />
        </div>

        {/* Footer */}
        <div className="flex justify-between items-center">
          <span
            className="text-xs uppercase font-bold tracking-wider"
            style={{ fontFamily: "var(--font-display)", color: "var(--text-muted)" }}
          >
            {subtitle}
          </span>
          <span
            className="text-sm font-bold"
            style={{ fontFamily: "var(--font-mono)", color }}
          >
            {percent.toFixed(1)}%
          </span>
        </div>
      </div>
    </motion.div>
  );
}