"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { FileText, Clock } from "lucide-react";
import { ResearchReport } from "@/lib/types";

export default function HistoryPage() {
  const [reports, setReports] = useState<ResearchReport[]>([]);

  // Note: in MVP, history comes from localStorage since backend is in-memory
  useEffect(() => {
    const stored = localStorage.getItem("findeep_history");
    if (stored) {
      try {
        setReports(JSON.parse(stored));
      } catch {}
    }
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <h1 className="text-2xl font-bold mb-8">历史研报</h1>

      {reports.length === 0 ? (
        <div className="text-center py-20 text-muted-foreground">
          <FileText className="w-16 h-16 mx-auto mb-4 opacity-30" />
          <p>暂无历史研报</p>
          <Link href="/" className="text-primary hover:underline mt-2 inline-block">
            开始第一份研究 →
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {reports.map((r) => (
            <Link
              key={r.task_id}
              href={`/report/${r.task_id}`}
              className="block p-4 rounded-xl border border-border hover:border-primary/30 hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-primary" />
                  <span className="font-medium">{r.query}</span>
                </div>
                <div className="flex items-center gap-1 text-sm text-muted-foreground">
                  <Clock className="w-3 h-3" />
                  <span>{r.created_at.slice(0, 10)}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
