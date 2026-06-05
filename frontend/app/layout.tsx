import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { Navbar } from "@/components/layout/Navbar";
import { MetricsProvider } from "@/components/providers/MetricsProvider";

export const metadata: Metadata = {
  title: "SYSAI — OS Optimization Engine",
  description: "Autonomous AI Operating System Optimization Engine",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <MetricsProvider>
          <div className="flex h-screen overflow-hidden">
            <Sidebar />
            <div className="flex flex-col flex-1 overflow-hidden">
              <Navbar />
              <main className="flex-1 overflow-y-auto"
                    style={{ backgroundColor: "var(--bg-primary)" }}>
                {children}
              </main>
            </div>
          </div>
        </MetricsProvider>
      </body>
    </html>
  );
}