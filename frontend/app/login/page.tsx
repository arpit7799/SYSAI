"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Brain, Lock, User, AlertCircle } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("http://localhost:8000/api/v1/auth/token", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Login failed");
        return;
      }

      // Save token and user to localStorage
      localStorage.setItem("sysai_token", data.access_token);
      localStorage.setItem("sysai_user", data.username);

      // Use Next.js router for client-side navigation — no full page reload
      // This allows ClientLayout's useEffect to pick up the new token
      // and transition from "unauth" to "auth" without remounting the entire app
      router.replace("/");
    } catch (err) {
      console.error(err);
      setError("Cannot connect to backend");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center relative"
      style={{ backgroundColor: "var(--bg-void)" }}
    >
      <div
        className="absolute inset-0 opacity-30"
        style={{
          backgroundImage: `linear-gradient(#ff465508 1px, transparent 1px),
            linear-gradient(90deg, #ff465508 1px, transparent 1px)`,
          backgroundSize: "40px 40px",
        }}
      />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 w-full max-w-sm p-8"
        style={{
          backgroundColor: "#1c252e",
          border: "1px solid #ff465530",
          clipPath: "polygon(0 0, calc(100% - 16px) 0, 100% 16px, 100% 100%, 16px 100%, 0 calc(100% - 16px))",
        }}
      >
        <div
          className="absolute top-0 left-0 right-0 h-px"
          style={{ background: "linear-gradient(90deg, #ff4655, transparent)" }}
        />

        {/* Logo */}
        <div className="flex items-center gap-3 mb-8">
          <Brain size={24} style={{ color: "#ff4655" }} />
          <div>
            <p
              className="text-lg font-black tracking-[0.3em]"
              style={{ fontFamily: "var(--font-display)", color: "#ff4655" }}
            >
              SYSAI
            </p>
            <p
              className="text-xs tracking-widest"
              style={{ fontFamily: "var(--font-mono)", color: "#4a5568" }}
            >
              AUTONOMOUS OS ENGINE
            </p>
          </div>
        </div>

        <div className="space-y-4">
          {/* Username */}
          <div>
            <label
              className="text-xs tracking-widest block mb-1.5"
              style={{ fontFamily: "var(--font-mono)", color: "#4a5568" }}
            >
              USERNAME
            </label>
            <div className="relative">
              <User size={12} className="absolute left-3 top-1/2 -translate-y-1/2"
                   style={{ color: "#4a5568" }} />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleLogin()}
                className="w-full pl-8 pr-3 py-2.5 text-sm outline-none"
                style={{
                  fontFamily: "var(--font-mono)",
                  backgroundColor: "#0f1115",
                  border: "1px solid #ffffff15",
                  color: "#cdd6f4",
                }}
                placeholder="enter username"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label
              className="text-xs tracking-widest block mb-1.5"
              style={{ fontFamily: "var(--font-mono)", color: "#4a5568" }}
            >
              PASSWORD
            </label>
            <div className="relative">
              <Lock size={12} className="absolute left-3 top-1/2 -translate-y-1/2"
                   style={{ color: "#4a5568" }} />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleLogin()}
                className="w-full pl-8 pr-3 py-2.5 text-sm outline-none"
                style={{
                  fontFamily: "var(--font-mono)",
                  backgroundColor: "#0f1115",
                  border: "1px solid #ffffff15",
                  color: "#cdd6f4",
                }}
                placeholder="enter password"
              />
            </div>
          </div>

          {error && (
            <div
              className="flex items-center gap-2 p-2 text-xs"
              style={{
                fontFamily: "var(--font-mono)",
                backgroundColor: "#ff465510",
                border: "1px solid #ff465530",
                color: "#ff4655",
              }}
            >
              <AlertCircle size={12} />
              {error}
            </div>
          )}

          <motion.button
            onClick={handleLogin}
            disabled={loading}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            className="w-full py-3 text-sm font-black tracking-[0.2em] transition-colors"
            style={{
              fontFamily: "var(--font-display)",
              backgroundColor: loading ? "#ffffff10" : "#ff4655",
              color: loading ? "#4a5568" : "#0f1115",
              clipPath: "polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 8px 100%, 0 calc(100% - 8px))",
            }}
          >
            {loading ? "AUTHENTICATING..." : "ACCESS SYSTEM"}
          </motion.button>

          <p
            className="text-xs text-center"
            style={{ fontFamily: "var(--font-mono)", color: "#4a5568" }}
          >
            NO ACCOUNT?{" "}
            <button
              onClick={() => router.push("/register")}
              className="underline"
              style={{ color: "#ff4655" }}
            >
              REGISTER
            </button>
          </p>
        </div>

        <p
          className="text-xs text-center mt-6"
          style={{ fontFamily: "var(--font-mono)", color: "#4a5568" }}
        >
          SYSAI v0.1.0 · SECURED BY JWT
        </p>
      </motion.div>
    </div>
  );
}