"use client"

import { DataSource } from "@/lib/types"
import { formatNumber } from "@/lib/utils"

interface DataPreviewProps {
  dataSource: DataSource | null
}

export function DataPreview({ dataSource }: DataPreviewProps) {
  if (!dataSource || !dataSource.rows.length) {
    return null
  }

  const columns = dataSource.columns
  const rows = dataSource.rows.slice(0, 5) // Show first 5 rows
  const hiddenRowsCount = Math.max(0, dataSource.rows.length - 5)

  return (
    <div className="rounded-lg border border-border bg-card p-4 my-4">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-foreground">Data Preview</h3>
        <p className="text-xs text-muted-foreground mt-1">
          Showing first {Math.min(5, dataSource.rows.length)} of {dataSource.rows.length} rows
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              {columns.map((col) => (
                <th key={col} className="px-3 py-2 text-left font-medium text-muted-foreground">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr key={idx} className="border-b border-border hover:bg-secondary/50">
                {columns.map((col) => (
                  <td key={col} className="px-3 py-2 text-foreground">
                    {typeof row[col] === "number"
                      ? formatNumber(row[col])
                      : String(row[col] ?? "-")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {hiddenRowsCount > 0 && (
        <p className="text-xs text-muted-foreground mt-3">
          ... and {hiddenRowsCount} more row{hiddenRowsCount !== 1 ? "s" : ""}
        </p>
      )}
    </div>
  )
}
