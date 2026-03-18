"use client"

import { BarChart3, Database } from "lucide-react"

interface HeaderProps {
  dataSourceName: string | null
}

export function Header({ dataSourceName }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <div className="flex size-9 items-center justify-center rounded-lg bg-primary">
            <BarChart3 className="size-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-base font-semibold text-foreground">InsightAI</h1>
            <p className="text-xs text-muted-foreground">
              Business Intelligence
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {dataSourceName && (
            <div className="flex items-center gap-2 rounded-md bg-secondary px-3 py-1.5 text-xs font-medium text-foreground">
              <Database className="size-3" />
              <span>{dataSourceName}</span>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
