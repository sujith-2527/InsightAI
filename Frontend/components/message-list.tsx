"use client"

import { useRef, useEffect } from "react"
import { User, BarChart3 } from "lucide-react"
import { cn } from "@/lib/utils"
import { DashboardPanel } from "./dashboard-panel"
import type { Message } from "@/lib/types"

interface MessageListProps {
  messages: Message[]
}

export function MessageList({ messages }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  if (messages.length === 0) {
    return null
  }

  return (
    <div className="flex flex-col gap-6">
      {messages.map((message) => (
        <div
          key={message.id}
          className={cn(
            "flex gap-3",
            message.role === "user" ? "justify-end" : "justify-start"
          )}
        >
          {message.role === "assistant" && (
            <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary">
              <BarChart3 className="size-4 text-primary-foreground" />
            </div>
          )}

          <div
            className={cn(
              "max-w-[85%] space-y-4",
              message.role === "user" && "text-right"
            )}
          >
            <div
              className={cn(
                "inline-block rounded-lg px-4 py-2.5 text-sm",
                message.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "border border-border bg-card text-foreground"
              )}
            >
              {message.content}
            </div>

            {message.dashboard && (
              <DashboardPanel
                charts={message.dashboard.charts}
                insights={message.dashboard.insights}
                summary={message.dashboard.summary}
              />
            )}
          </div>

          {message.role === "user" && (
            <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-secondary">
              <User className="size-4 text-foreground" />
            </div>
          )}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
