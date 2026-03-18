"use client"

import { BarChart3, MessageSquare, Upload, Zap } from "lucide-react"

const features = [
  {
    icon: MessageSquare,
    title: "Natural Language",
    description: "Ask questions in plain English",
  },
  {
    icon: BarChart3,
    title: "Smart Charts",
    description: "Auto-generated visualizations",
  },
  {
    icon: Zap,
    title: "Real-time",
    description: "Instant dashboard updates",
  },
  {
    icon: Upload,
    title: "Data Upload",
    description: "Import your CSV files",
  },
]

const exampleQueries = [
  "Show me monthly sales revenue for Q3",
  "What are my top performing products?",
  "Display customer segments by revenue",
  "Compare this quarter vs last quarter",
]

interface WelcomeScreenProps {
  onExampleClick: (query: string) => void
}

export function WelcomeScreen({ onExampleClick }: WelcomeScreenProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-semibold text-foreground mb-3 tracking-tight">
          Welcome to InsightAI
        </h1>
        <p className="text-muted-foreground max-w-md">
          Ask questions about your business data in natural language and get instant, interactive dashboards.
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10 w-full max-w-2xl">
        {features.map((feature) => (
          <div
            key={feature.title}
            className="flex flex-col items-center p-4 rounded-lg bg-card border border-border"
          >
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mb-3">
              <feature.icon className="w-5 h-5 text-primary" />
            </div>
            <h3 className="font-medium text-foreground text-sm mb-1">
              {feature.title}
            </h3>
            <p className="text-xs text-muted-foreground text-center">
              {feature.description}
            </p>
          </div>
        ))}
      </div>

      <div className="w-full max-w-xl">
        <p className="text-sm text-muted-foreground mb-3 text-center">
          Try an example query
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {exampleQueries.map((query) => (
            <button
              key={query}
              onClick={() => onExampleClick(query)}
              className="text-left px-4 py-3 rounded-lg bg-secondary border border-border text-sm text-foreground hover:bg-secondary/80 transition-colors"
            >
              {query}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
