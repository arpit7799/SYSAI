"use client";

import {
  LineChart,
  Line,
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

export function CPUChart({ history }: Props) {
  const data = history.map((s, i) => ({
    t: i,
    cpu: parseFloat(s.cpu.usage_percent.toFixed(1)),
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
        CPU Usage — Live
      </p>
      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={data}>
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
            formatter={(value) => [`${value ?? 0}%`, "CPU"]}
            labelFormatter={() => ""}
          />
          <Line
            type="monotone"
            dataKey="cpu"
            stroke="var(--accent-cyan)"
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}