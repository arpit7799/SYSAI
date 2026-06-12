import type { Metadata } from "next";
import "./globals.css";
import { ClientLayout } from "@/components/providers/ClientLayout";

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
        <ClientLayout>{children}</ClientLayout>
      </body>
    </html>
  );
}
