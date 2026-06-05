"use client";

import {
  AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from "recharts";
import { SystemSnapshot } from "@/types/metrics";

interface Props { history: SystemSnapshot[]; }

export function CPUChart({ history }: Props) {
  const data = history.map((s, i) => ({
    t: i,
    cpu: parseFloat(s.cpu.usage_percent.toFixed(1)),
  }));

  const latest = data[data.length - 1]?.cpu ?? 0;

  return (
    <div className="tactical-card clip-chamfer p-4 relative group overflow-hidden">
      {/* Background Graphic */}
      <div className="absolute right-0 top-0 bottom-0 w-1/2 z-0 opacity-20 pointer-events-none" style={{
        backgroundImage: "url('/cpu_render.png')", 
        backgroundSize: "cover", 
        backgroundPosition: "right center",
        maskImage: "linear-gradient(to left, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%)",
        WebkitMaskImage: "linear-gradient(to left, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%)"
      }} />

      <div className="relative z-10 flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-1 h-4 bg-[var(--valorant-red)]" />
          <span className="text-xs font-bold tracking-[0.2em] uppercase" style={{ fontFamily: "var(--font-display)", color: "var(--text-secondary)" }}>
            CPU Realtime
          </span>
        </div>
        <span className="text-lg font-black" style={{ fontFamily: "var(--font-display)", color: "var(--text-bright)" }}>
          {latest}%
        </span>
      </div>
      <ResponsiveContainer width="100%" height={140}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="cpuG" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--valorant-red)" stopOpacity={0.6} />
              <stop offset="100%" stopColor="var(--valorant-red)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="1 3" stroke="var(--border)" vertical={false} />
          <XAxis dataKey="t" hide />
          <YAxis
            domain={[0, 100]}
            tick={{ fill: "var(--text-muted)", fontSize: 10, fontFamily: "var(--font-mono)", fontWeight: "bold" }}
            tickFormatter={(v) => `${v}`}
            width={24}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--bg-void)",
              border: "1px solid var(--valorant-red)",
              borderRadius: 0,
              color: "var(--text-primary)",
              fontSize: 12,
              fontFamily: "var(--font-mono)",
              fontWeight: "bold",
            }}
            itemStyle={{ color: "var(--valorant-red)" }}
            formatter={(value) => [`${value ?? 0}%`, "CPU"]}
            labelFormatter={() => ""}
          />
          <ReferenceLine y={80} stroke="var(--valorant-accent)" strokeDasharray="4 4" />
          <Area
            type="step" dataKey="cpu"
            stroke="var(--valorant-red)" strokeWidth={2}
            fill="url(#cpuG)"
            dot={false} isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}