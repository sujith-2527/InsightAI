"use client"

import { Database, BarChart3, Lightbulb, CheckCircle2, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

const steps = [
  { icon: Loader2, label: "Understanding your query..." },
  { icon: Database, label: "Analyzing data patterns..." },
  { icon: BarChart3, label: "Selecting visualizations..." },
  { icon: Lightbulb, label: "Generating insights..." },
]

interface LoadingStateProps {
  step: number
}

export function LoadingState({ step }: LoadingStateProps) {
  return (
    <div className="flex items-start gap-4">
      <div className="flex size-9 items-center justify-center rounded-lg bg-primary">
        <Loader2 className="size-4 text-primary-foreground animate-spin" />
      </div>

      <div className="flex-1 space-y-3 rounded-lg border border-border bg-card p-4">
        <p className="font-medium text-foreground">Generating your dashboard...</p>
        <div className="space-y-2">
          {steps.map((s, index) => {
            const Icon = s.icon
            const isActive = index === step
            const isComplete = index < step

            return (
              <div
                key={index}
                className={cn(
                  "flex items-center gap-3 rounded-md p-2 transition-colors",
                  isComplete && "bg-primary/5",
                  isActive && "bg-secondary"
                )}
              >
                <div
                  className={cn(
                    "flex size-7 items-center justify-center rounded-md transition-colors",
                    isComplete && "bg-primary",
                    isActive && "bg-secondary",
                    !isComplete && !isActive && "bg-muted"
                  )}
                >
                  {isComplete ? (
                    <CheckCircle2 className="size-4 text-primary-foreground" />
                  ) : (
                    <Icon className={cn(
                      "size-4",
                      isActive && "text-foreground animate-spin",
                      !isActive && "text-muted-foreground"
                    )} />
                  )}
                </div>
                <span className={cn(
                  "text-sm",
                  isComplete && "text-primary",
                  isActive && "text-foreground font-medium",
                  !isComplete && !isActive && "text-muted-foreground"
                )}>
                  {s.label}
                </span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
