"use client";

import ReactMarkdown from "react-markdown";
import { Citation } from "@/lib/types";

interface Props {
  markdown: string;
  citations: Record<string, Citation>;
  onCitationClick: (refId: string) => void;
}

export function ReportContent({ markdown, citations, onCitationClick }: Props) {
  if (!markdown) {
    return (
      <div className="flex items-center justify-center h-64 text-muted-foreground">
        等待报告生成...
      </div>
    );
  }

  return (
    <div className="prose prose-slate max-w-none">
      <ReactMarkdown
        components={{
          // Make citation references clickable: [ref:abc123]
          a: ({ href, children, ...props }) => {
            const refMatch = href?.match(/ref:([a-f0-9]+)/);
            if (refMatch) {
              const refId = refMatch[1];
              const citation = citations[refId];
              return (
                <button
                  onClick={() => onCitationClick(refId)}
                  className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded
                             bg-blue-50 text-blue-600 text-xs font-mono
                             hover:bg-blue-100 transition-colors"
                  title={citation?.text?.slice(0, 200)}
                >
                  [{refId}]
                </button>
              );
            }
            return <a href={href} {...props}>{children}</a>;
          },
          // Replace ⚠️ with styled warning
          p: ({ children, ...props }) => {
            const text = String(children);
            if (text.includes("⚠️") || text.includes("⚠")) {
              return (
                <p {...props} className="bg-amber-50 border-l-4 border-amber-400 pl-4 py-2 my-2">
                  {children}
                </p>
              );
            }
            return <p {...props}>{children}</p>;
          },
        }}
      >
        {markdown}
      </ReactMarkdown>
    </div>
  );
}
