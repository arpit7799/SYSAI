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

export function DiskChart({ history }: Props) {
  const data = history.map((s, i) => ({
    t: i,
    read: parseFloat(s.disk.read_mb_per_sec.toFixed(2)),
    write: parseFloat(s.disk.write_mb_per_sec.toFixed(2)),
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
        Disk I/O — MB/s
      </p>
      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="readGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00ff88" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#00ff88" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="writeGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ff3366" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#ff3366" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="t" hide />
          <YAxis
            tick={{ fill: "var(--text-muted)", fontSize: 10 }}
            tickFormatter={(v) => `${v}`}
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
            `${value ?? 0} MB/s`,
            name === "read" ? "Read" : "Write",
            ]}
            labelFormatter={() => ""}
          />
          <Area
            type="monotone"
            dataKey="read"
            stroke="#00ff88"
            strokeWidth={2}
            fill="url(#readGrad)"
            dot={false}
            isAnimationActive={false}
          />
          <Area
            type="monotone"
            dataKey="write"
            stroke="#ff3366"
            strokeWidth={2}
            fill="url(#writeGrad)"
            dot={false}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}