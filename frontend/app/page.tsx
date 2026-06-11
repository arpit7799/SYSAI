"use client";

import { motion } from "framer-motion";
import { useMetricsContext } from "@/components/providers/MetricsProvider";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { HealthScore } from "@/components/dashboard/HealthScore";
import { CPUChart } from "@/components/charts/CPUChart";
import { RAMChart } from "@/components/charts/RAMChart";
import { PerCoreChart } from "@/components/charts/PerCoreChart";
import { DiskChart } from "@/components/charts/DiskChart";
import { Cpu, MemoryStick, HardDrive, Network } from "lucide-react";
import { formatBytes } from "@/lib/utils";
import { PredictionPanel } from "@/components/dashboard/PredictionPanel";
import { AnomalyPanel } from "@/components/dashboard/AnomalyPanel";
import { OptimizerPanel } from "@/components/dashboard/OptimizerPanel";

export default function DashboardPage() {
  const { snapshot, history, connected } = useMetricsContext();

  if (!snapshot) {
    return (
      <div className="flex items-center justify-center h-full bg-[var(--bg-primary)]">
        <div className="text-center space-y-3">
          <div
            className="w-12 h-12 border-4 border-t-transparent rounded-none animate-spin mx-auto"
            style={{ borderColor: "var(--valorant-red) transparent var(--valorant-red) var(--valorant-red)" }}
          />
          <p
            className="text-sm font-bold tracking-[0.2em]"
            style={{ fontFamily: "var(--font-display)", color: "var(--valorant-red)" }}
          >
            {connected ? "INITIALIZING COMBAT STIM..." : "ESTABLISHING LINK..."}
          </p>
        </div>
      </div>
    );
  }

  const cards = [
    {
      title: "CPU",
      value: `${snapshot.cpu.usage_percent.toFixed(1)}%`,
      subtitle: `${snapshot.cpu.core_count}C · ${snapshot.cpu.frequency_mhz.toFixed(0)}MHz`,
      percent: snapshot.cpu.usage_percent,
      icon: Cpu,
    },
    {
      title: "MEMORY",
      value: `${snapshot.ram.usage_percent.toFixed(1)}%`,
      subtitle: `${snapshot.ram.used_gb.toFixed(1)}/${snapshot.ram.total_gb.toFixed(1)} GB`,
      percent: snapshot.ram.usage_percent,
      icon: MemoryStick,
    },
    {
      title: "DISK",
      value: `${snapshot.disk.usage_percent.toFixed(1)}%`,
      subtitle: `${snapshot.disk.free_gb.toFixed(1)} GB FREE`,
      percent: snapshot.disk.usage_percent,
      icon: HardDrive,
    },
    {
      title: "NETWORK",
      value: formatBytes(snapshot.network.bytes_recv_mb),
      subtitle: `↑ ${formatBytes(snapshot.network.bytes_sent_mb)}`,
      percent: Math.min((snapshot.network.bytes_recv_mb / 1000) * 100, 100),
      icon: Network,
    },
  ];

  return (
    <div className="relative min-h-full">
      {/* Background Image */}
      <div
        className="absolute inset-0 z-0 opacity-20 pointer-events-none bg-cover bg-center"
        style={{ backgroundImage: "url('/valorant_bg.png')" }}
      />

      {/* Content wrapper */}
      <div className="p-6 space-y-6 relative z-10">

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-end justify-between border-b-2 border-[var(--border)] pb-4"
        >
          <div>
            <div className="flex items-center gap-3 mb-1">
              <div className="w-2 h-6 bg-[var(--valorant-red)]" />
              <h1
                className="text-3xl font-black tracking-wider uppercase"
                style={{ fontFamily: "var(--font-display)", color: "var(--text-bright)" }}
              >
                System Overview
              </h1>
            </div>
            <p
              className="text-sm tracking-widest text-[var(--text-secondary)] uppercase pl-5"
              style={{ fontFamily: "var(--font-mono)" }}
            >
              Realtime · 1s Interval · {history.length} Samples
            </p>
          </div>
          <div
            className="px-4 py-2 font-bold text-sm tracking-widest clip-chamfer"
            style={{
              fontFamily: "var(--font-display)",
              backgroundColor: "var(--valorant-red)",
              color: "var(--bg-void)",
            }}
          >
            ACTIVE
          </div>
        </motion.div>

        {/* Health */}
        <HealthScore score={snapshot.health_score} />

        {/* Metric cards */}
        <div className="grid grid-cols-4 gap-4">
          {cards.map((card, i) => (
            <MetricCard key={card.title} {...card} index={i} />
          ))}
        </div>

        {/* Charts row 1 */}
        <div className="grid grid-cols-2 gap-4">
          <CPUChart history={history} />
          <RAMChart history={history} />
        </div>

        {/* Charts row 2 */}
        <div className="grid grid-cols-2 gap-4">
          <PerCoreChart snapshot={snapshot} />
          <DiskChart history={history} />
        </div>

        {/* Prediction Panels */}
        <div>
          <h2
            className="text-xs tracking-[0.3em] mb-3"
            style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}
          >
            AI FORECAST / NEXT 50 SECONDS
          </h2>
          <div className="grid grid-cols-3 gap-3">
            <PredictionPanel metric="cpu"  label="CPU"  accentColor="#ff4655" />
            <PredictionPanel metric="ram"  label="RAM"  accentColor="#7c3aed" />
            <PredictionPanel metric="disk" label="DISK" accentColor="#f59e0b" />
          </div>
        </div>

        {/* Anomaly Detection */}
        <div>
          <h2
            className="text-xs tracking-[0.3em] mb-3"
            style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}
          >
            ANOMALY DETECTION / REAL-TIME
          </h2>
          <AnomalyPanel />
        </div>

        {/* Optimizer */}
        <div>
          <h2
            className="text-xs tracking-[0.3em] mb-3"
            style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}
          >
            AUTONOMOUS OPTIMIZER
          </h2>
          <OptimizerPanel />
        </div>
        
        {/* Process table */}
        <div className="tactical-card clip-chamfer p-5">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-1.5 h-4 bg-[var(--valorant-red)]" />
            <span
              className="text-sm font-bold tracking-[0.1em] uppercase"
              style={{ fontFamily: "var(--font-display)", color: "var(--text-bright)" }}
            >
              Active Processes / Top 5
            </span>
          </div>

          {/* Table header */}
          <div
            className="grid grid-cols-4 gap-4 pb-2 mb-3 text-sm font-bold uppercase tracking-wider"
            style={{
              fontFamily: "var(--font-display)",
              color: "var(--text-muted)",
              borderBottom: "2px solid var(--border)",
            }}
          >
            <span>Process</span>
            <span>PID</span>
            <span>CPU</span>
            <span>MEM</span>
          </div>

          <div className="space-y-1">
            {snapshot.top_processes.slice(0, 5).map((proc, i) => (
          <motion.div
            key={proc.pid}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.05 }}
            className="
              grid grid-cols-4 gap-4 py-2 px-3 text-sm
              transition-all duration-200
              group cursor-default
              border-l-4 border-transparent
              hover:bg-[var(--bg-card-hover)]
              hover:border-l-[var(--valorant-red)]
            "
            style={{
              fontFamily: "var(--font-mono)",
            }}
              >
                <span className="truncate font-bold text-[var(--text-primary)] group-hover:text-white transition-colors">
                  {proc.name}
                </span>
                <span className="text-[var(--text-secondary)]">{proc.pid}</span>
                <span
                  className="font-bold"
                  style={{ color: proc.cpu_percent > 50 ? "var(--valorant-red)" : "inherit" }}
                >
                  {proc.cpu_percent.toFixed(1)}%
                </span>
                <span className="font-bold">{proc.memory_percent.toFixed(1)}%</span>
              </motion.div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}