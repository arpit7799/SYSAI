"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Sidebar } from "@/components/layout/Sidebar";
import { Navbar } from "@/components/layout/Navbar";
import { MetricsProvider } from "@/components/providers/MetricsProvider";

export function ClientLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [status, setStatus] = useState<"loading" | "auth" | "unauth">("loading");

  const isAuthPage = pathname === "/login" || pathname === "/register";

  useEffect(() => {
    const token = localStorage.getItem("sysai_token");

    if (token) {
      setStatus("auth");
      // If user is authenticated but on an auth page, redirect to dashboard
      if (isAuthPage) {
        router.replace("/");
      }
    } else {
      setStatus("unauth");
      // If user is NOT authenticated and NOT on an auth page, redirect to login
      if (!isAuthPage) {
        router.replace("/login");
      }
    }
  }, [pathname, isAuthPage, router]);

  // Still checking auth — show nothing to prevent flash
  if (status === "loading") {
    return null;
  }

  // Auth pages — render children alone (no Sidebar/Navbar)
  // Only render if user is actually unauthenticated (or still redirecting)
  if (isAuthPage) {
    return <>{children}</>;
  }

  // Protected page but not logged in — already redirecting via useEffect, render nothing
  if (status === "unauth") {
    return null;
  }

  // Authenticated user on a protected page — render full dashboard layout
  return (
    <MetricsProvider>
      <div className="flex h-screen overflow-hidden">
        <Sidebar />
        <div className="flex flex-col flex-1 overflow-hidden">
          <Navbar />
          <main
            className="flex-1 overflow-y-auto"
            style={{ backgroundColor: "var(--bg-primary)" }}
          >
            {children}
          </main>
        </div>
      </div>
    </MetricsProvider>
  );
}