"use client";

import {
  AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";
import { SystemSnapshot } from "@/types/metrics";

interface Props { history: SystemSnapshot[]; }

export function DiskChart({ history }: Props) {
  const data = history.map((s, i) => ({
    t: i,
    read: parseFloat(s.disk.read_mb_per_sec.toFixed(2)),
    write: parseFloat(s.disk.write_mb_per_sec.toFixed(2)),
  }));

  return (
    <div className="tactical-card clip-chamfer p-4 relative group overflow-hidden">
      {/* Background Graphic */}
      <div className="absolute right-0 top-0 bottom-0 w-1/2 z-0 opacity-20 pointer-events-none" style={{
        backgroundImage: "url('/disk_render.png')", 
        backgroundSize: "cover", 
        backgroundPosition: "right center",
        maskImage: "linear-gradient(to left, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%)",
        WebkitMaskImage: "linear-gradient(to left, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%)"
      }} />

      <div className="relative z-10 flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-1 h-4 bg-[var(--text-primary)]" />
          <span className="text-xs font-bold tracking-[0.2em] uppercase" style={{ fontFamily: "var(--font-display)", color: "var(--text-secondary)" }}>
            Disk I/O
          </span>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={140}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="readG" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--text-primary)" stopOpacity={0.6} />
              <stop offset="100%" stopColor="var(--text-primary)" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="writeG" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--valorant-red)" stopOpacity={0.6} />
              <stop offset="100%" stopColor="var(--valorant-red)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="1 3" stroke="var(--border)" vertical={false} />
          <XAxis dataKey="t" hide />
          <YAxis
            tick={{ fill: "var(--text-muted)", fontSize: 10, fontFamily: "var(--font-mono)", fontWeight: "bold" }}
            width={24}
            axisLine={false}
            tickLine={false}
          />
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
            formatter={(value, name) => [`${value ?? 0} MB/s`, name === "read" ? "READ" : "WRITE"]}
            labelFormatter={() => ""}
          />
          <Area type="step" dataKey="read" stroke="var(--text-primary)" strokeWidth={2}
            fill="url(#readG)" dot={false} isAnimationActive={false} />
          <Area type="step" dataKey="write" stroke="var(--valorant-red)" strokeWidth={2}
            fill="url(#writeG)" dot={false} isAnimationActive={false} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}