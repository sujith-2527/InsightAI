"use client"

import { useState, useCallback } from "react"
import { Header } from "@/components/header"
import { ChatInput } from "@/components/chat-input"
import { MessageList } from "@/components/message-list"
import { WelcomeScreen } from "@/components/welcome-screen"
import { LoadingState } from "@/components/loading-state"
import { processQuery, parseCSV, uploadDataset } from "@/lib/dashboard-store"
import type { Message, DataSource } from "@/lib/types"

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [loadingStep, setLoadingStep] = useState(0)
  const [dataSource, setDataSource] = useState<DataSource | null>(null)
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null)

  const handleSendMessage = useCallback(
    async (content: string) => {
      // Add user message
      const userMessage: Message = {
        id: Date.now().toString(),
        role: "user",
        content,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, userMessage])
      setIsLoading(true)
      setLoadingStep(0)

      try {
        // Simulate AI processing with loading steps
        const stepDuration = 600
        for (let i = 0; i < 4; i++) {
          await new Promise((resolve) => setTimeout(resolve, stepDuration))
          setLoadingStep(i + 1)
        }

        // Process the query
        const context = messages
          .filter((msg) => msg.role === "user")
          .slice(-5)
          .map((msg) => msg.content)
        const result = await processQuery(content, dataSource, context)

        // Add assistant message with dashboard
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `Here's your dashboard based on "${content}"`,
          timestamp: new Date(),
          dashboard: result,
        }
        setMessages((prev) => [...prev, assistantMessage])
      } catch (error) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `I could not process that query right now. ${error instanceof Error ? error.message : "Please try again."}`,
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, assistantMessage])
      } finally {
        setIsLoading(false)
      }
    },
    [dataSource, messages]
  )

  const handleFileUpload = useCallback(async (file: File) => {
    try {
      // Upload to backend so NL queries run against the new dataset.
      await uploadDataset(file)
      const content = await file.text()
      const parsed = parseCSV(content)
      setDataSource(parsed)
      setUploadedFileName(file.name)
    } catch (error) {
      console.error("Failed to upload or parse file:", error)
    }
  }, [])

  const handleClearFile = useCallback(() => {
    setDataSource(null)
    setUploadedFileName(null)
  }, [])

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Header dataSourceName={uploadedFileName || "Sample Dataset"} />

      <main className="flex-1">
        <div className="mx-auto max-w-6xl px-4 py-8">
          {/* Messages or Welcome Screen */}
          <div className="mb-8">
            {messages.length === 0 ? (
              <WelcomeScreen onExampleClick={handleSendMessage} />
            ) : (
              <MessageList messages={messages} />
            )}

            {/* Loading State */}
            {isLoading && (
              <div className="mt-6">
                <LoadingState step={loadingStep} />
              </div>
            )}
          </div>

          {/* Chat Input - Fixed at bottom */}
          <div className="sticky bottom-0 border-t border-border bg-background py-4">
            <ChatInput
              onSendMessage={handleSendMessage}
              onFileUpload={handleFileUpload}
              isLoading={isLoading}
              uploadedFile={uploadedFileName}
              onClearFile={handleClearFile}
            />
          </div>
        </div>
      </main>
    </div>
  )
}
