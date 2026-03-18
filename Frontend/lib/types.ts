export type MessageRole = "user" | "assistant"

export interface DashboardInsight {
  title: string
  value: string
  change?: string
  changeType?: "positive" | "negative" | "neutral"
}

export interface ChartSeries {
  key: string
  label: string
}

export interface ChartConfig {
  id: string
  type: "bar" | "line" | "area" | "pie" | "donut"
  title: string
  description?: string
  data: Array<Record<string, string | number>>
  xKey?: string
  yKeys?: ChartSeries[]
  dataKey?: string
  nameKey?: string
}

export interface DashboardData {
  summary: string
  insights: DashboardInsight[]
  charts: ChartConfig[]
}

export interface Message {
  id: string
  role: MessageRole
  content: string
  timestamp: Date
  dashboard?: DashboardData
}

export interface DataSource {
  name: string
  rows: Array<Record<string, string | number>>
  columns: string[]
}

export interface BackendFilter {
  column: string
  operator: string
  value: string
}

export interface QueryKpis {
  source_row_count?: number
  count?: number
  average?: number
  total?: number
  minimum?: number
  maximum?: number
}

export interface QueryMeta {
  chart_type?: "bar" | "line" | "area" | "pie" | "donut"
  x?: string
  y?: string
  aggregation?: string
  query_parsed?: string
  record_count?: number
  confidence?: number
  filters_applied?: BackendFilter[]
  warnings?: string[]
  kpis?: QueryKpis
}
