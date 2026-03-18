"use client"

import { TrendingUp, TrendingDown, Minus } from "lucide-react"
import { cn } from "@/lib/utils"
import type { DashboardInsight } from "@/lib/types"

interface InsightCardProps {
  insight: DashboardInsight
}

export function InsightCard({ insight }: InsightCardProps) {
  const { title, value, change, changeType } = insight

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
        {title}
      </p>
      <div className="mt-2 flex items-end justify-between">
        <p className="text-2xl font-semibold text-foreground">{value}</p>
        {change && (
          <div
            className={cn(
              "flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium",
              changeType === "positive" && "bg-primary/10 text-primary",
              changeType === "negative" && "bg-destructive/10 text-destructive",
              changeType === "neutral" && "bg-secondary text-muted-foreground"
            )}
          >
            {changeType === "positive" && <TrendingUp className="size-3" />}
            {changeType === "negative" && <TrendingDown className="size-3" />}
            {changeType === "neutral" && <Minus className="size-3" />}
            <span>{change}</span>
          </div>
        )}
      </div>
    </div>
  )
}
