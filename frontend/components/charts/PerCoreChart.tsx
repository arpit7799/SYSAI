"use client";

import {
  BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from "recharts";
import { SystemSnapshot } from "@/types/metrics";

interface Props { snapshot: SystemSnapshot; }

function coreColor(v: number) {
  if (v >= 80) return "var(--valorant-red)";
  return "var(--text-primary)";
}

export function PerCoreChart({ snapshot }: Props) {
  const data = snapshot.cpu.per_core_percent.map((val, i) => ({
    core: `C${i}`,
    usage: parseFloat(val.toFixed(1)),
  }));

  return (
    <div className="tactical-card clip-chamfer p-4 relative group overflow-hidden">
      {/* Background Graphic */}
      <div className="absolute right-0 top-0 bottom-0 w-1/2 z-0 opacity-20 pointer-events-none" style={{
        backgroundImage: "url('/core_render.png')", 
        backgroundSize: "cover", 
        backgroundPosition: "right center",
        maskImage: "linear-gradient(to left, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%)",
        WebkitMaskImage: "linear-gradient(to left, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%)"
      }} />

      <div className="relative z-10 flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-1 h-4 bg-[var(--text-primary)]" />
          <span className="text-xs font-bold tracking-[0.2em] uppercase" style={{ fontFamily: "var(--font-display)", color: "var(--text-secondary)" }}>
            Per-Core Output
          </span>
        </div>
        <span className="text-xs font-bold tracking-wider" style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>
          {data.length} CORES
        </span>
      </div>
      <ResponsiveContainer width="100%" height={140}>
        <BarChart data={data} barSize={12}>
          <CartesianGrid strokeDasharray="1 3" stroke="var(--border)" vertical={false} />
          <XAxis dataKey="core" tick={{ fill: "var(--text-muted)", fontSize: 10, fontFamily: "var(--font-mono)", fontWeight: "bold" }} axisLine={false} tickLine={false} />
          <YAxis domain={[0, 100]} tick={{ fill: "var(--text-muted)", fontSize: 10, fontFamily: "var(--font-mono)", fontWeight: "bold" }} width={24} axisLine={false} tickLine={false} />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--bg-void)",
              border: "1px solid var(--text-primary)",
              borderRadius: 0,
              fontSize: 12,
              fontFamily: "var(--font-mono)",
              fontWeight: "bold",
              color: "var(--text-primary)",
            }}
            cursor={{ fill: 'var(--bg-card-hover)' }}
            formatter={(value) => [`${value ?? 0}%`, "CORE"]}
          />
          <Bar dataKey="usage" radius={[0, 0, 0, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={coreColor(entry.usage)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}