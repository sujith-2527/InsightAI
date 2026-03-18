"use client"

import {
  BarChart,
  Bar,
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts"
import type { ChartConfig } from "@/lib/types"

const COLORS = [
  "hsl(260, 60%, 55%)", // primary
  "hsl(200, 50%, 50%)", // teal
  "hsl(160, 40%, 45%)", // muted green
]

interface ChartCardProps {
  config: ChartConfig
}

export function ChartCard({ config }: ChartCardProps) {
  const { type, title, description, data, xKey, yKeys, dataKey, nameKey } = config

  const renderChart = () => {
    switch (type) {
      case "bar":
        return (
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(260, 10%, 25%)" vertical={false} />
              <XAxis
                dataKey={xKey}
                tick={{ fill: "hsl(0, 0%, 60%)", fontSize: 11 }}
                axisLine={{ stroke: "hsl(260, 10%, 25%)" }}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "hsl(0, 0%, 60%)", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(value) => {
                  if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`
                  if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`
                  return value.toString()
                }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(260, 10%, 16%)",
                  border: "1px solid hsl(260, 10%, 25%)",
                  borderRadius: "8px",
                  color: "hsl(0, 0%, 95%)",
                }}
                formatter={(value: number) => [`$${value.toLocaleString()}`, ""]}
              />
              <Legend wrapperStyle={{ color: "hsl(0, 0%, 60%)" }} />
              {yKeys?.map((yKey, index) => (
                <Bar
                  key={yKey.key}
                  dataKey={yKey.key}
                  fill={COLORS[index % COLORS.length]}
                  radius={[4, 4, 0, 0]}
                  name={yKey.label}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        )

      case "line":
        return (
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(260, 10%, 25%)" vertical={false} />
              <XAxis
                dataKey={xKey}
                tick={{ fill: "hsl(0, 0%, 60%)", fontSize: 11 }}
                axisLine={{ stroke: "hsl(260, 10%, 25%)" }}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "hsl(0, 0%, 60%)", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(260, 10%, 16%)",
                  border: "1px solid hsl(260, 10%, 25%)",
                  borderRadius: "8px",
                  color: "hsl(0, 0%, 95%)",
                }}
              />
              <Legend wrapperStyle={{ color: "hsl(0, 0%, 60%)" }} />
              {yKeys?.map((yKey, index) => (
                <Line
                  key={yKey.key}
                  type="monotone"
                  dataKey={yKey.key}
                  stroke={COLORS[index % COLORS.length]}
                  strokeWidth={2}
                  dot={{ fill: COLORS[index % COLORS.length], r: 4 }}
                  name={yKey.label}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )

      case "area":
        return (
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <defs>
                {yKeys?.map((yKey, index) => (
                  <linearGradient key={yKey.key} id={`gradient-${yKey.key}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={COLORS[index % COLORS.length]} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={COLORS[index % COLORS.length]} stopOpacity={0.05} />
                  </linearGradient>
                ))}
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(260, 10%, 25%)" vertical={false} />
              <XAxis
                dataKey={xKey}
                tick={{ fill: "hsl(0, 0%, 60%)", fontSize: 11 }}
                axisLine={{ stroke: "hsl(260, 10%, 25%)" }}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "hsl(0, 0%, 60%)", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(value) => {
                  if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`
                  if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`
                  return value.toString()
                }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(260, 10%, 16%)",
                  border: "1px solid hsl(260, 10%, 25%)",
                  borderRadius: "8px",
                  color: "hsl(0, 0%, 95%)",
                }}
                formatter={(value: number) => [`$${value.toLocaleString()}`, ""]}
              />
              <Legend wrapperStyle={{ color: "hsl(0, 0%, 60%)" }} />
              {yKeys?.map((yKey, index) => (
                <Area
                  key={yKey.key}
                  type="monotone"
                  dataKey={yKey.key}
                  stroke={COLORS[index % COLORS.length]}
                  strokeWidth={2}
                  fill={`url(#gradient-${yKey.key})`}
                  name={yKey.label}
                />
              ))}
            </AreaChart>
          </ResponsiveContainer>
        )

      case "pie":
      case "donut":
        return (
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={type === "donut" ? 60 : 0}
                outerRadius={100}
                dataKey={dataKey || "value"}
                nameKey={nameKey || "name"}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                labelLine={{ stroke: "hsl(0, 0%, 50%)" }}
                strokeWidth={1}
                stroke="hsl(260, 10%, 16%)"
              >
                {data.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(260, 10%, 16%)",
                  border: "1px solid hsl(260, 10%, 25%)",
                  borderRadius: "8px",
                  color: "hsl(0, 0%, 95%)",
                }}
                formatter={(value: number) => [`$${value.toLocaleString()}`, ""]}
              />
            </PieChart>
          </ResponsiveContainer>
        )

      default:
        return null
    }
  }

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="mb-4">
        <h3 className="text-base font-medium text-foreground">{title}</h3>
        {description && (
          <p className="mt-1 text-sm text-muted-foreground">{description}</p>
        )}
      </div>
      {renderChart()}
    </div>
  )
}
