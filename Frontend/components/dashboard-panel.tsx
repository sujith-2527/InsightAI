"use client"

import { Sparkles } from "lucide-react"
import { ChartCard } from "./chart-card"
import { InsightCard } from "./insight-card"
import type { ChartConfig, DashboardInsight } from "@/lib/types"

interface DashboardPanelProps {
  charts: ChartConfig[]
  insights: DashboardInsight[]
  summary: string
}

export function DashboardPanel({ charts, insights, summary }: DashboardPanelProps) {
  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="relative overflow-hidden rounded-2xl border border-violet-200 bg-gradient-to-r from-violet-50 to-purple-50 p-5">
        <div className="absolute right-4 top-4 opacity-20">
          <Sparkles className="size-12 text-violet-500" />
        </div>
        <div className="flex items-start gap-3">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500 to-purple-500">
            <Sparkles className="size-4 text-white" />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-violet-600">AI Summary</p>
            <p className="mt-1 text-sm leading-relaxed text-foreground">{summary}</p>
          </div>
        </div>
      </div>

      {/* Insights Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {insights.map((insight, index) => (
          <InsightCard key={index} insight={insight} index={index} />
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid gap-4 lg:grid-cols-2">
        {charts.map((chart) => (
          <ChartCard key={chart.id} config={chart} />
        ))}
      </div>
    </div>
  )
}
