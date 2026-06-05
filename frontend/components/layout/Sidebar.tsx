"use client";

import { useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  Cpu,
  Activity,
  AlertTriangle,
  Zap,
  Settings,
  ChevronLeft,
  Brain,
} from "lucide-react";
import { useMetricsContext } from "@/components/providers/MetricsProvider";

const NAV_ITEMS = [
  { icon: LayoutDashboard, label: "DASHBOARD", href: "/", id: "01" },
  { icon: Cpu, label: "PROCESSES", href: "/processes", id: "02" },
  { icon: Activity, label: "PREDICTIONS", href: "/predictions", id: "03" },
  { icon: AlertTriangle, label: "ANOMALIES", href: "/anomalies", id: "04" },
  { icon: Zap, label: "OPTIMIZER", href: "/optimizer", id: "05" },
  { icon: Settings, label: "SETTINGS", href: "/settings", id: "06" },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const [active, setActive] = useState("/");
  const { connected, snapshot } = useMetricsContext();

  return (
    <motion.aside
      animate={{ width: collapsed ? 60 : 200 }}
      transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1] }}
      className="h-screen flex flex-col relative z-10"
      style={{
        backgroundColor: "var(--bg-secondary)",
        borderRight: "1px solid var(--border-bright)",
        minWidth: collapsed ? 60 : 200,
      }}
    >
      {/* Top accent line */}
      <div
        className="absolute top-0 left-0 right-0 h-px"
        style={{
          background:
            "linear-gradient(90deg, transparent, var(--neon-cyan), transparent)",
        }}
      />

      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 relative">
        <div className="relative">
          <Brain size={20} style={{ color: "var(--neon-cyan)" }} />
          <div
            className="absolute inset-0 blur-sm"
            style={{ color: "var(--neon-cyan)" }}
          >
            <Brain size={20} />
          </div>
        </div>

        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.2 }}
            >
              <span
                className="font-bold text-base tracking-[0.3em] flicker"
                style={{
                  fontFamily: "var(--font-display)",
                  color: "var(--neon-cyan)",
                }}
              >
                SYSAI
              </span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* System Status */}
      {!collapsed && (
        <div
          className="mx-3 mb-4 px-3 py-2 rounded"
          style={{
            backgroundColor: "var(--bg-void)",
            border: "1px solid var(--border)",
          }}
        >
          <div className="flex items-center gap-2 mb-1">
            <div className="status-dot" />
            <span
              className="text-xs"
              style={{
                fontFamily: "var(--font-mono)",
                color: "var(--neon-green)",
              }}
            >
              {connected ? "CONNECTED" : "OFFLINE"}
            </span>
          </div>

          {snapshot && (
            <div
              className="text-xs"
              style={{
                fontFamily: "var(--font-mono)",
                color: "var(--text-secondary)",
              }}
            >
              HEALTH:{" "}
              <span style={{ color: "var(--neon-cyan)" }}>
                {snapshot.health_score.toFixed(0)}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 px-2 space-y-1">
        {NAV_ITEMS.map((item) => {
          const isActive = active === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setActive(item.href)}
              className="flex items-center gap-3 px-3 py-2.5 rounded transition-all duration-200 group relative"
              style={{
                backgroundColor: isActive
                  ? "rgba(0, 229, 255, 0.08)"
                  : "transparent",
                border: isActive
                  ? "1px solid rgba(0, 229, 255, 0.2)"
                  : "1px solid transparent",
              }}
            >
              {isActive && (
                <div
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 rounded-full"
                  style={{
                    backgroundColor: "var(--neon-cyan)",
                    boxShadow: "0 0 6px var(--neon-cyan)",
                  }}
                />
              )}

              <item.icon
                size={15}
                style={{
                  color: isActive
                    ? "var(--neon-cyan)"
                    : "var(--text-secondary)",
                }}
              />

              <AnimatePresence>
                {!collapsed && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex items-center gap-2 flex-1"
                  >
                    <span
                      className="text-xs tracking-[0.15em]"
                      style={{
                        fontFamily: "var(--font-mono)",
                        color: isActive
                          ? "var(--neon-cyan)"
                          : "var(--text-secondary)",
                      }}
                    >
                      {item.label}
                    </span>

                    <span
                      className="ml-auto text-xs"
                      style={{
                        color: "var(--text-muted)",
                        fontFamily: "var(--font-mono)",
                      }}
                    >
                      {item.id}
                    </span>
                  </motion.div>
                )}
              </AnimatePresence>
            </Link>
          );
        })}
      </nav>

      {/* Collapse Button */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-center p-4 transition-colors"
        style={{ borderTop: "1px solid var(--border)" }}
      >
        <motion.div
          animate={{ rotate: collapsed ? 180 : 0 }}
          transition={{ duration: 0.3 }}
        >
          <ChevronLeft
            size={14}
            style={{ color: "var(--text-secondary)" }}
          />
        </motion.div>
      </button>
    </motion.aside>
  );
}