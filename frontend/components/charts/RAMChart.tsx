"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { SystemSnapshot } from "@/types/metrics";

interface Props {
  history: SystemSnapshot[];
}

export function RAMChart({ history }: Props) {
  const data = history.map((s, i) => ({
    t: i,
    ram: parseFloat(s.ram.usage_percent.toFixed(1)),
    swap: parseFloat(s.ram.swap_percent.toFixed(1)),
  }));

  return (
    <div
      className="rounded-xl border p-5"
      style={{ backgroundColor: "var(--bg-card)", borderColor: "var(--border)" }}
    >
      <p
        className="text-xs uppercase tracking-widest mb-4"
        style={{ color: "var(--text-secondary)" }}
      >
        Memory Usage — Live
      </p>
      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="ramGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#7c3aed" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="swapGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="t" hide />
          <YAxis
            domain={[0, 100]}
            tick={{ fill: "var(--text-muted)", fontSize: 10 }}
            tickFormatter={(v) => `${v}%`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--bg-secondary)",
              border: "1px solid var(--border)",
              borderRadius: 8,
              color: "var(--text-primary)",
              fontSize: 12,
            }}
            formatter={(value, name) => [
              `${value ?? 0}%`,
            name === "ram" ? "RAM" : "Swap",
        ]}
            labelFormatter={() => ""}
          />
          <Area
            type="monotone"
            dataKey="ram"
            stroke="#7c3aed"
            strokeWidth={2}
            fill="url(#ramGrad)"
            dot={false}
            isAnimationActive={false}
          />
          <Area
            type="monotone"
            dataKey="swap"
            stroke="var(--accent-cyan)"
            strokeWidth={1.5}
            fill="url(#swapGrad)"
            dot={false}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}