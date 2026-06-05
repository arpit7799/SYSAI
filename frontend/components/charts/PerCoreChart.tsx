"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { getStatusColor } from "@/lib/utils";
import { SystemSnapshot } from "@/types/metrics";

interface Props {
  snapshot: SystemSnapshot;
}

export function PerCoreChart({ snapshot }: Props) {
  const data = snapshot.cpu.per_core_percent.map((val, i) => ({
    core: `C${i}`,
    usage: parseFloat(val.toFixed(1)),
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
        Per-Core CPU Usage
      </p>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={data} barSize={20}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis
            dataKey="core"
            tick={{ fill: "var(--text-muted)", fontSize: 10 }}
          />
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
            formatter={(value) => [`${value ?? 0}%`, "Usage"]}
          />
          <Bar dataKey="usage" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={getStatusColor(entry.usage)}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}