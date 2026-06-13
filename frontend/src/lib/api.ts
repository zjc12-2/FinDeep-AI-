import { DataSourceConfig, ResearchReport, Citation, TimelineEvent } from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  /** Initiate a new research task */
  startResearch: (query: string, dataSources: DataSourceConfig) =>
    request<{ task_id: string; status: string }>("/api/research", {
      method: "POST",
      body: JSON.stringify({ query, data_sources: dataSources }),
    }),

  /** Get the final research report */
  getReport: (taskId: string) => request<ResearchReport>(`/api/report/${taskId}`),

  /** Get a specific citation source */
  getSource: (citationId: string) => request<Citation>(`/api/sources/${citationId}`),

  /** Ask a follow-up question */
  askFollowUp: (taskId: string, question: string) =>
    request<{ answer: string; task_id: string }>("/api/ask", {
      method: "POST",
      body: JSON.stringify({ task_id: taskId, question }),
    }),

  /** Get event timeline */
  getTimeline: (taskId: string) =>
    request<{ events: TimelineEvent[] }>(`/api/timeline/${taskId}`),

  /** Upload a document */
  uploadDocument: async (file: File) => {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${BASE_URL}/api/upload`, { method: "POST", body: form });
    if (!res.ok) throw new Error("Upload failed");
    return res.json() as Promise<{ doc_id: string; filename: string; pages: number }>;
  },

  /** Get SSE stream URL */
  streamUrl: (taskId: string) => `${BASE_URL}/api/research/${taskId}/stream`,
};
