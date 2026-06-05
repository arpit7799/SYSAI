"use client";

import { createContext, useContext, ReactNode } from "react";
import { useMetrics } from "@/hooks/useMetrics";
import { SystemSnapshot } from "@/types/metrics";

interface MetricsContextType {
  snapshot: SystemSnapshot | null;
  history: SystemSnapshot[];
  connected: boolean;
  error: string | null;
}

const MetricsContext = createContext<MetricsContextType>({
  snapshot: null,
  history: [],
  connected: false,
  error: null,
});

export function MetricsProvider({ children }: { children: ReactNode }) {
  const metrics = useMetrics();
  return (
    <MetricsContext.Provider value={metrics}>
      {children}
    </MetricsContext.Provider>
  );
}

export function useMetricsContext() {
  return useContext(MetricsContext);
}