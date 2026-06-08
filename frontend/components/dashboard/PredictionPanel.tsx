"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from "recharts";
import { TrendingUp, TrendingDown, Minus, AlertTriangle } from "lucide-react";

interface PredictionData {
  metric: string;
  current_value: number;
  ensemble_forecast: number[];
  confidence: number;
  trend: string;
  warning: boolean;
  data_points_used: number;
}

interface Props {
  metric: "cpu" | "ram" | "disk";
  label: string;
  accentColor: string;
}

const TREND_ICONS = {
  spike:             { icon: AlertTriangle, label: "SPIKE PREDICTED" },
  rising:            { icon: TrendingUp,   label: "RISING"           },
  stable:            { icon: Minus,        label: "STABLE"           },
  dropping:          { icon: TrendingDown, label: "DROPPING"         },
  falling:           { icon: TrendingDown, label: "FALLING"          },
  insufficient_data: { icon: Minus,        label: "COLLECTING DATA"  },
  no_data:           { icon: Minus,        label: "NO DATA"          },
};

export function PredictionPanel({ metric, label, accentColor }: Props) {
  const [data, setData] = useState<PredictionData | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchPrediction = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/prediction/${metric}`);
      const json = await res.json() as PredictionData;
      setData(json);
    } catch {
      // Backend not ready yet
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrediction();
    const interval = setInterval(fetchPrediction, 30000);
    return () => clearInterval(interval);
  }, [metric]);

  const chartData = data
    ? [
        { t: "NOW", value: data.current_value, type: "current" },
        ...data.ensemble_forecast.map((v, i) => ({
          t: `+${(i + 1) * 5}s`,
          value: v,
          type: "forecast",
        })),
      ]
    : [];

  const trendInfo = TREND_ICONS[data?.trend as keyof typeof TREND_ICONS]
    ?? TREND_ICONS.stable;
  const TrendIcon = trendInfo.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-sm p-4 relative overflow-hidden"
      style={{
        backgroundColor: "#1c252e",
        border: `1px solid ${accentColor}30`,
        clipPath: "polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 12px 100%, 0 calc(100% - 12px))",
      }}
    >
      {/* Top accent line */}
      <div
        className="absolute top-0 left-0 right-0 h-px"
        style={{ background: `linear-gradient(90deg, ${accentColor}, transparent)` }}
      />

      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div>
          <p
            className="text-xs tracking-[0.2em] mb-0.5"
            style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}
          >
            FORECAST / {label}
          </p>
          <div className="flex items-center gap-2">
            <TrendIcon size={12} style={{ color: accentColor }} />
            <span
              className="text-xs font-bold tracking-widest"
              style={{ fontFamily: "var(--font-mono)", color: accentColor }}
            >
              {trendInfo.label}
            </span>
            {data?.warning && (
              <span
                className="text-xs px-1.5 py-0.5 rounded-sm animate-pulse"
                style={{
                  fontFamily: "var(--font-mono)",
                  backgroundColor: "rgba(255,70,85,0.15)",
                  color: "#ff4655",
                  border: "1px solid #ff465540",
                }}
              >
                ⚠ WARNING
              </span>
            )}
          </div>
        </div>

        <div className="text-right">
          <p
            className="text-xs"
            style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}
          >
            CONFIDENCE
          </p>
          <p
            className="text-lg font-black"
            style={{ fontFamily: "var(--font-display)", color: accentColor }}
          >
            {data ? `${data.confidence.toFixed(0)}%` : "--"}
          </p>
        </div>
      </div>

      {/* Chart */}
      {loading ? (
        <div className="h-24 flex items-center justify-center">
          <span
            className="text-xs tracking-widest animate-pulse"
            style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}
          >
            COMPUTING...
          </span>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={100}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id={`grad-${metric}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={accentColor} stopOpacity={0.3} />
                <stop offset="95%" stopColor={accentColor} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="2 4" stroke="#1c252e" vertical={false} />
            <XAxis
              dataKey="t"
              tick={{ fill: "#4a5568", fontSize: 8, fontFamily: "var(--font-mono)" }}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fill: "#4a5568", fontSize: 8, fontFamily: "var(--font-mono)" }}
              width={22}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#0f1115",
                border: `1px solid ${accentColor}`,
                borderRadius: 0,
                fontSize: 10,
                fontFamily: "var(--font-mono)",
                color: accentColor,
              }}
              formatter={(value) => [`${value ?? 0}%`, label]}
              labelFormatter={(l) => l}
            />
            <ReferenceLine
              y={85}
              stroke="#ff4655"
              strokeDasharray="3 3"
              strokeOpacity={0.5}
            />
            <Area
              type="step"
              dataKey="value"
              stroke={accentColor}
              strokeWidth={1.5}
              fill={`url(#grad-${metric})`}
              dot={false}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}

      {/* Footer */}
      <div className="flex justify-between mt-2">
        <span
          className="text-xs"
          style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}
        >
          CURRENT: <span style={{ color: accentColor }}>{data?.current_value.toFixed(1)}%</span>
        </span>
        <span
          className="text-xs"
          style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}
        >
          {data?.data_points_used ?? 0} SAMPLES
        </span>
      </div>
    </motion.div>
  );
}