import type { ChartConfig, DashboardData, DashboardInsight, DataSource, QueryMeta } from "@/lib/types"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080"

type BackendQueryResponse = {
  data?: Array<Record<string, string | number>>
  meta?: QueryMeta
  error?: string
}

function toNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) return value
  if (typeof value === "string") {
    const parsed = Number(value)
    return Number.isFinite(parsed) ? parsed : null
  }
  return null
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(value)
}

function buildInsights(rows: Array<Record<string, string | number>>, xKey: string, yKey: string, meta?: QueryMeta): DashboardInsight[] {
  const numericValues = rows
    .map((row) => toNumber(row[yKey]))
    .filter((value): value is number => value !== null)

  if (numericValues.length === 0) {
    return [
      { title: "Data Points", value: String(rows.length), changeType: "neutral" },
      { title: "Status", value: "No numeric metric found", changeType: "neutral" },
    ]
  }

  const groupedTotal = numericValues.reduce((sum, value) => sum + value, 0)
  const groupedAverage = groupedTotal / numericValues.length

  const trueAverage = meta?.kpis?.average
  const trueTotal = meta?.kpis?.total
  const sourceRows = meta?.kpis?.source_row_count

  let topRow: Record<string, string | number> | null = null
  for (const row of rows) {
    const yValue = toNumber(row[yKey])
    if (yValue === null) continue
    if (!topRow || yValue > (toNumber(topRow[yKey]) ?? Number.NEGATIVE_INFINITY)) {
      topRow = row
    }
  }

  const topLabel = topRow ? String(topRow[xKey]) : "N/A"
  const topValue = topRow ? toNumber(topRow[yKey]) ?? 0 : 0

  if (yKey === "count") {
    const countValue = meta?.kpis?.count ?? numericValues[0] ?? rows.length
    return [
      { title: "Filtered Rows", value: String(sourceRows ?? rows.length), changeType: "neutral" },
      { title: `Top ${xKey}`, value: topLabel, change: formatNumber(topValue), changeType: "positive" },
      { title: "Count", value: formatNumber(countValue), changeType: "neutral" },
      { title: "Filters Applied", value: String(meta?.filters_applied?.length ?? 0), changeType: "neutral" },
    ]
  }

  return [
    { title: sourceRows ? "Filtered Rows" : "Groups", value: String(sourceRows ?? rows.length), changeType: "neutral" },
    { title: `Top ${xKey}`, value: topLabel, change: formatNumber(topValue), changeType: "positive" },
    {
      title: `Average ${yKey}`,
      value: formatNumber(trueAverage ?? groupedAverage),
      changeType: "neutral",
    },
    {
      title: `Total ${yKey}`,
      value: formatNumber(trueTotal ?? groupedTotal),
      changeType: "positive",
    },
  ]
}

function buildCharts(
  rows: Array<Record<string, string | number>>,
  xKey: string,
  yKey: string,
  preferredChartType: QueryMeta["chart_type"]
): ChartConfig[] {
  const series = [{ key: yKey, label: yKey }]
  const primaryType = preferredChartType || "bar"

  const primary: ChartConfig = {
    id: "primary",
    type: primaryType,
    title: `${yKey} by ${xKey}`,
    description: "Primary analysis",
    data: rows,
    xKey,
    yKeys: primaryType === "pie" || primaryType === "donut" ? undefined : series,
    dataKey: primaryType === "pie" || primaryType === "donut" ? yKey : undefined,
    nameKey: primaryType === "pie" || primaryType === "donut" ? xKey : undefined,
  }

  const secondaryType: ChartConfig["type"] =
    primaryType === "line" ? "area" : primaryType === "donut" || primaryType === "pie" ? "bar" : "line"

  return [
    primary,
    {
      id: "secondary",
      type: secondaryType,
      title: secondaryType === "line" || secondaryType === "area" ? `${yKey} trend by ${xKey}` : `${yKey} distribution`,
      description: "Supporting view",
      data: rows,
      xKey,
      yKeys: series,
    },
  ]
}

function warningInsights(warnings: string[]): DashboardInsight[] {
  if (!warnings.length) return []
  return warnings.slice(0, 2).map((warning, index) => ({
    title: index === 0 ? "Planner Warning" : "Data Notice",
    value: warning,
    changeType: "neutral",
  }))
}

export async function processQuery(
  query: string,
  _dataSource: DataSource | null,
  context: string[] = []
): Promise<DashboardData> {
  const response = await fetch(`${API_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_query: query, context }),
  })

  let payload: BackendQueryResponse
  try {
    payload = (await response.json()) as BackendQueryResponse
  } catch {
    payload = {}
  }

  if (!response.ok || payload.error) {
    throw new Error(payload.error || "Backend query failed.")
  }

  const rows = payload.data || []
  const xKey = payload.meta?.x || "category"
  const yKey = payload.meta?.y || "value"
  const warnings = payload.meta?.warnings || []

  const generatedInsights = buildInsights(rows, xKey, yKey, payload.meta)
  const extraInsights = warningInsights(warnings)

  return {
    summary: payload.meta?.query_parsed || `Generated ${rows.length} grouped records for your query.`,
    insights: [...generatedInsights, ...extraInsights].slice(0, 4),
    charts: buildCharts(rows, xKey, yKey, payload.meta?.chart_type),
  }
}

export async function uploadDataset(file: File): Promise<{ columns: string[] }> {
  const formData = new FormData()
  formData.append("file", file)

  const response = await fetch(`${API_URL}/upload`, {
    method: "POST",
    body: formData,
  })

  const payload = (await response.json()) as { error?: string; columns?: string[] }
  if (!response.ok || payload.error) {
    throw new Error(payload.error || "Upload failed")
  }

  return { columns: payload.columns || [] }
}

export function parseCSV(csvText: string): DataSource {
  const lines = csvText
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)

  if (lines.length < 2) {
    throw new Error("CSV must contain a header and at least one row.")
  }

  const headers = lines[0].split(",").map((header) => header.trim())

  const rows = lines.slice(1).map((line) => {
    const values = line.split(",").map((value) => value.trim())
    const row: Record<string, string | number> = {}

    headers.forEach((header, index) => {
      const raw = values[index] || ""
      const numeric = Number(raw)
      row[header] = raw !== "" && Number.isFinite(numeric) ? numeric : raw
    })

    return row
  })

  return {
    name: "Uploaded CSV",
    columns: headers,
    rows,
  }
}
