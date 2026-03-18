"use client"

import { useState, useRef, type KeyboardEvent } from "react"
import { Send, Upload, X, FileSpreadsheet } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface ChatInputProps {
  onSendMessage: (message: string) => void
  onFileUpload: (file: File) => void
  isLoading: boolean
  uploadedFile: string | null
  onClearFile: () => void
}

const EXAMPLE_QUERIES = [
  "Show me monthly sales revenue for Q3 broken down by region",
  "What are my top performing products this year?",
  "Display customer segments by revenue contribution",
  "Show revenue trends over the past 9 months",
]

export function ChatInput({
  onSendMessage,
  onFileUpload,
  isLoading,
  uploadedFile,
  onClearFile,
}: ChatInputProps) {
  const [input, setInput] = useState("")
  const fileInputRef = useRef<HTMLInputElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = () => {
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim())
      setInput("")
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto"
      }
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      onFileUpload(file)
    }
  }

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)
    e.target.style.height = "auto"
    e.target.style.height = Math.min(e.target.scrollHeight, 150) + "px"
  }

  return (
    <div className="w-full">
      {/* Example queries */}
      <div className="mb-4 flex flex-wrap gap-2">
        {EXAMPLE_QUERIES.map((query, index) => (
          <button
            key={index}
            onClick={() => setInput(query)}
            className="rounded-md border border-border bg-secondary px-3 py-1.5 text-xs text-foreground transition-colors hover:bg-secondary/80"
          >
            {query}
          </button>
        ))}
      </div>

      {/* Uploaded file indicator */}
      {uploadedFile && (
        <div className="mb-3 flex items-center gap-3 rounded-lg bg-secondary border border-border px-4 py-3">
          <div className="flex size-8 items-center justify-center rounded-md bg-primary">
            <FileSpreadsheet className="size-4 text-primary-foreground" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-foreground">{uploadedFile}</p>
            <p className="text-xs text-muted-foreground">Ready to analyze</p>
          </div>
          <button
            onClick={onClearFile}
            className="rounded-md p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            <X className="size-4" />
          </button>
        </div>
      )}

      {/* Input container */}
      <div className="rounded-lg border border-border bg-card transition-colors focus-within:border-primary">
        <div className="flex items-end gap-2 p-3">
          <div className="flex gap-1">
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.json"
              onChange={handleFileChange}
              className="hidden"
            />
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="size-9 shrink-0 rounded-md text-muted-foreground hover:text-foreground"
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="size-4" />
              <span className="sr-only">Upload file</span>
            </Button>
          </div>

          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your data..."
            rows={1}
            className="max-h-[150px] min-h-[40px] flex-1 resize-none bg-transparent py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
          />

          <Button
            type="button"
            size="icon"
            onClick={handleSubmit}
            disabled={!input.trim() || isLoading}
            className={cn(
              "size-9 shrink-0 rounded-md transition-colors",
              input.trim()
                ? "bg-primary text-primary-foreground hover:bg-primary/90"
                : "bg-secondary text-muted-foreground"
            )}
          >
            <Send className="size-4" />
            <span className="sr-only">Send message</span>
          </Button>
        </div>
      </div>

      <p className="mt-3 text-center text-xs text-muted-foreground">
        Upload a CSV file or use the sample dataset to explore your data
      </p>
    </div>
  )
}
