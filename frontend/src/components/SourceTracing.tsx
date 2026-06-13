"use client";

import { Citation } from "@/lib/types";
import { FileText } from "lucide-react";

interface Props {
  citations: Record<string, Citation>;
  selectedRef: string | null;
}

export function SourceTracing({ citations, selectedRef }: Props) {
  const entries = Object.entries(citations);

  if (entries.length === 0) {
    return <p className="text-sm text-muted-foreground text-center py-8">暂无引用来源</p>;
  }

  return (
    <div className="space-y-3">
      {selectedRef && citations[selectedRef] && (
        <div className="p-3 rounded-lg bg-primary/5 border border-primary/20 mb-4">
          <p className="text-xs font-semibold text-primary mb-1">📍 当前选中引用</p>
          <p className="text-sm">{citations[selectedRef].text}</p>
          <div className="flex gap-4 mt-2 text-xs text-muted-foreground">
            <span>ID: {selectedRef}</span>
            {citations[selectedRef].page && <span>页码: {citations[selectedRef].page}</span>}
            <span>置信度: {(citations[selectedRef].confidence * 100).toFixed(0)}%</span>
          </div>
        </div>
      )}
      {entries.map(([refId, c]) => (
        <div
          key={refId}
          id={`source-${refId}`}
          className={`p-3 rounded-lg border text-sm transition-colors ${
            selectedRef === refId
              ? "border-primary bg-primary/5 ring-1 ring-primary"
              : "border-border hover:border-primary/30"
          }`}
        >
          <div className="flex items-center gap-2 mb-1">
            <FileText className="w-3 h-3 text-muted-foreground" />
            <span className="text-xs font-mono text-primary">[{refId}]</span>
            <span className="text-xs text-muted-foreground">
              {c.page ? `第${c.page}页` : `片段#${c.chunk_index}`}
            </span>
          </div>
          <p className="text-sm leading-relaxed">{c.text}</p>
          {c.doc_id && (
            <p className="text-xs text-muted-foreground mt-1">来源: {c.doc_id}</p>
          )}
        </div>
      ))}
    </div>
  );
}
