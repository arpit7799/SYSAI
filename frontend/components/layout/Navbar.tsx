"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useMetricsContext } from "@/components/providers/MetricsProvider";
import { Signal, Clock4, LogOut } from "lucide-react";

export function Navbar() {
  const router = useRouter();
  const { connected, snapshot } = useMetricsContext();
  const [time, setTime] = useState("");
  const [date, setDate] = useState("");
  const [user, setUser] = useState<string | null>(null);

  useEffect(() => {
    // Read auth state after mount to avoid SSR hydration mismatch
    setUser(localStorage.getItem("sysai_user"));
  }, []);

  useEffect(() => {
    const update = () => {
      const now = new Date();
      setTime(now.toLocaleTimeString("en-US", { hour12: false }));
      setDate(now.toLocaleDateString("en-US", { month: "short", day: "2-digit", year: "numeric" }).toUpperCase());
    };
    update();
    const i = setInterval(update, 1000);
    return () => clearInterval(i);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("sysai_token");
    localStorage.removeItem("sysai_user");
    router.replace("/login");
  };

  return (
    <header
      className="h-12 flex items-center justify-between px-6 relative"
      style={{
        backgroundColor: "var(--bg-secondary)",
        borderBottom: "1px solid var(--border-bright)",
      }}
    >
      {/* Bottom accent */}
      <div className="absolute bottom-0 left-0 right-0 h-px"
           style={{ background: "linear-gradient(90deg, transparent, var(--neon-cyan), transparent)", opacity: 0.4 }} />

      {/* Left */}
      <div className="flex items-center gap-4">
        <span
          className="text-xs tracking-[0.2em]"
          style={{ fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}
        >
          SYSAI / AUTONOMOUS OPTIMIZATION ENGINE
        </span>
        <div className="h-3 w-px" style={{ backgroundColor: "var(--border-bright)" }} />
        <span
          className="text-xs tracking-widest"
          style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}
        >
          v0.1.0
        </span>
      </div>

      {/* Right */}
      <div className="flex items-center gap-5">
        {/* CPU quick stat */}
        {snapshot && (
          <div className="flex items-center gap-2">
            <span className="text-xs" style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>CPU</span>
            <span
              className="text-xs font-bold"
              style={{
                fontFamily: "var(--font-mono)",
                color: snapshot.cpu.usage_percent > 80 ? "var(--neon-red)" :
                       snapshot.cpu.usage_percent > 50 ? "var(--neon-amber)" : "var(--neon-green)",
              }}
            >
              {snapshot.cpu.usage_percent.toFixed(1)}%
            </span>
          </div>
        )}

        {/* Divider */}
        <div className="h-3 w-px" style={{ backgroundColor: "var(--border-bright)" }} />

        {/* Connection */}
        <div className="flex items-center gap-2">
          <Signal
            size={12}
            style={{ color: connected ? "var(--neon-green)" : "var(--neon-red)" }}
          />
          <span
            className="text-xs tracking-widest"
            style={{
              fontFamily: "var(--font-mono)",
              color: connected ? "var(--neon-green)" : "var(--neon-red)",
            }}
          >
            {connected ? "LIVE" : "OFFLINE"}
          </span>
          {connected && <div className="status-dot" />}
        </div>

        {/* Divider */}
        <div className="h-3 w-px" style={{ backgroundColor: "var(--border-bright)" }} />

        {/* Time */}
        <div className="flex items-center gap-2">
          <Clock4 size={11} style={{ color: "var(--text-muted)" }} />
          <span
            className="text-xs"
            style={{ fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}
          >
            {date} <span style={{ color: "var(--neon-cyan)" }}>{time}</span>
          </span>
        </div>

        {/* Divider + User + Logout — only when authenticated */}
        {user && (
          <>
            <div className="h-3 w-px" style={{ backgroundColor: "var(--border-bright)" }} />
            <span
              className="text-xs tracking-widest"
              style={{ fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}
            >
              {user.toUpperCase()}
            </span>
            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 text-xs px-2 py-1 tracking-widest transition-colors hover:bg-[#ff465515]"
              style={{
                fontFamily: "var(--font-mono)",
                color: "#ff4655",
                border: "1px solid #ff465530",
              }}
            >
              <LogOut size={10} />
              LOGOUT
            </button>
          </>
        )}
      </div>
    </header>
  );
}