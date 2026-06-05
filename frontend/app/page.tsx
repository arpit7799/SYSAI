"use client";

import { useMetricsContext } from "@/components/providers/MetricsProvider";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { HealthScore } from "@/components/dashboard/HealthScore";
import { CPUChart } from "@/components/charts/CPUChart";
import { RAMChart } from "@/components/charts/RAMChart";
import { PerCoreChart } from "@/components/charts/PerCoreChart";
import { DiskChart } from "@/components/charts/DiskChart";
import { Cpu, MemoryStick, HardDrive, Network } from "lucide-react";
import { formatBytes } from "@/lib/utils";

export default function DashboardPage() {
  const { snapshot, history, connected } = useMetricsContext();

  if (!snapshot) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div
            className="w-8 h-8 border-2 border-t-transparent rounded-full animate-spin mx-auto mb-3"
            style={{ borderColor: "var(--accent-cyan)" }}
          />
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            {connected ? "Loading metrics..." : "Connecting to backend..."}
          </p>
        </div>
      </div>
    );
  }

  const cards = [
    {
      title: "CPU Usage",
      value: `${snapshot.cpu.usage_percent.toFixed(1)}%`,
      subtitle: `${snapshot.cpu.core_count} cores · ${snapshot.cpu.frequency_mhz.toFixed(0)} MHz`,
      percent: snapshot.cpu.usage_percent,
      icon: Cpu,
    },
    {
      title: "Memory",
      value: `${snapshot.ram.usage_percent.toFixed(1)}%`,
      subtitle: `${snapshot.ram.used_gb.toFixed(1)} / ${snapshot.ram.total_gb.toFixed(1)} GB`,
      percent: snapshot.ram.usage_percent,
      icon: MemoryStick,
    },
    {
      title: "Disk",
      value: `${snapshot.disk.usage_percent.toFixed(1)}%`,
      subtitle: `${snapshot.disk.free_gb.toFixed(1)} GB free`,
      percent: snapshot.disk.usage_percent,
      icon: HardDrive,
    },
    {
      title: "Network",
      value: formatBytes(snapshot.network.bytes_recv_mb),
      subtitle: `↑ ${formatBytes(snapshot.network.bytes_sent_mb)} sent`,
      percent: Math.min((snapshot.network.bytes_recv_mb / 1000) * 100, 100),
      icon: Network,
    },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1
          className="text-xl font-bold tracking-wide"
          style={{ color: "var(--text-primary)" }}
        >
          System Overview
        </h1>
        <p className="text-xs mt-1" style={{ color: "var(--text-secondary)" }}>
          Real-time · updates every second
        </p>
      </div>

      {/* Health Score */}
      <HealthScore score={snapshot.health_score} />

      {/* Metric Cards */}
      <div className="grid grid-cols-2 gap-4">
        {cards.map((card, i) => (
          <MetricCard key={card.title} {...card} index={i} />
        ))}
      </div>

      {/* Charts Row 1 — CPU + RAM */}
      <div className="grid grid-cols-2 gap-4">
        <CPUChart history={history} />
        <RAMChart history={history} />
      </div>

      {/* Charts Row 2 — Per Core + Disk */}
      <div className="grid grid-cols-2 gap-4">
        <PerCoreChart snapshot={snapshot} />
        <DiskChart history={history} />
      </div>

      {/* Top Processes */}
      <div
        className="rounded-xl border p-5"
        style={{ backgroundColor: "var(--bg-card)", borderColor: "var(--border)" }}
      >
        <h2
          className="text-sm font-semibold mb-4 uppercase tracking-widest"
          style={{ color: "var(--text-secondary)" }}
        >
          Top Processes
        </h2>
        <div className="space-y-2">
          {snapshot.top_processes.slice(0, 5).map((proc) => (
            <div
              key={proc.pid}
              className="flex items-center justify-between py-2 border-b"
              style={{ borderColor: "var(--border)" }}
            >
              <div className="flex items-center gap-3">
                <span
                  className="w-1.5 h-1.5 rounded-full"
                  style={{ backgroundColor: "var(--accent-cyan)" }}
                />
                <span
                  className="text-sm font-mono"
                  style={{ color: "var(--text-primary)" }}
                >
                  {proc.name}
                </span>
                <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                  PID {proc.pid}
                </span>
              </div>
              <div className="flex items-center gap-4 text-xs font-mono">
                <span style={{ color: "var(--accent-cyan)" }}>
                  CPU {proc.cpu_percent.toFixed(1)}%
                </span>
                <span style={{ color: "var(--accent-purple)" }}>
                  MEM {proc.memory_percent.toFixed(1)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}