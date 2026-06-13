/** Data source selection for a research request */
export interface DataSourceConfig {
  akshare: boolean;
  news: boolean;
  uploadedDocs: string[];
}

/** A citation linking report text to source document */
export interface Citation {
  ref_id: string;
  doc_id: string;
  chunk_index: number;
  text: string;
  page?: number;
  confidence: number;
}

/** SSE event types from the backend */
export type SSEEvent =
  | { type: "phase"; phase: "bull" | "bear" | "factcheck" | "synthesize" | "done" }
  | { type: "agent_progress"; agent: string; chunk: string }
  | { type: "citation"; ref_id: string; source: Citation }
  | { type: "warning"; message: string; location: string }
  | { type: "error"; message: string }
  | { type: "complete"; report_id: string };

/** Full research report */
export interface ResearchReport {
  task_id: string;
  query: string;
  markdown: string;
  citations: Record<string, Citation>;
  bull_view?: string;
  bear_view?: string;
  factcheck_notes: string[];
  created_at: string;
}

/** Timeline event */
export interface TimelineEvent {
  date: string;
  event: string;
  type: "financial" | "management" | "market" | "other";
  causes: string[];
  effects: string[];
  source_ref?: string;
}
