"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
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

const NAV_ITEMS = [
  { icon: LayoutDashboard, label: "Dashboard", href: "/" },
  { icon: Cpu, label: "Processes", href: "/processes" },
  { icon: Activity, label: "Predictions", href: "/predictions" },
  { icon: AlertTriangle, label: "Anomalies", href: "/anomalies" },
  { icon: Zap, label: "Optimizer", href: "/optimizer" },
  { icon: Settings, label: "Settings", href: "/settings" },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <motion.aside
      animate={{ width: collapsed ? 64 : 220 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      className="h-screen flex flex-col border-r"
      style={{
        backgroundColor: "var(--bg-secondary)",
        borderColor: "var(--border)",
        minWidth: collapsed ? 64 : 220,
      }}
    >
      {/* Logo */}
      <div
        className="flex items-center gap-3 px-4 py-5 border-b"
        style={{ borderColor: "var(--border)" }}
      >
        <Brain size={24} style={{ color: "var(--accent-cyan)" }} />

        {!collapsed && (
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="font-bold text-lg tracking-wider"
            style={{ color: "var(--accent-cyan)" }}
          >
            SYSAI
          </motion.span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 space-y-1 px-2">
        {NAV_ITEMS.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 hover:bg-[var(--bg-card-hover)]"
          >
            <item.icon
              size={18}
              className="shrink-0"
              style={{ color: "var(--text-secondary)" }}
            />

            {!collapsed && (
              <span
                className="text-sm"
                style={{ color: "var(--text-secondary)" }}
              >
                {item.label}
              </span>
            )}
          </Link>
        ))}
      </nav>

      {/* Collapse Button */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-center p-4 border-t transition-colors hover:bg-[var(--bg-card)]"
        style={{ borderColor: "var(--border)" }}
      >
        <motion.div animate={{ rotate: collapsed ? 180 : 0 }}>
          <ChevronLeft
            size={16}
            style={{ color: "var(--text-secondary)" }}
          />
        </motion.div>
      </button>
    </motion.aside>
  );
}