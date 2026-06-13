"use client";

import { cn } from "@/lib/utils";
import { Loader2, CheckCircle2, AlertCircle } from "lucide-react";

interface Props {
  agent: string;
  label: string;
  icon: string;
  status: "idle" | "running" | "done";
  output: string;
}

export function AgentCard({ agent, label, icon, status, output }: Props) {
  return (
    <div
      className={cn(
        "p-4 rounded-xl border transition-all",
        status === "running" && "border-primary/40 bg-primary/5 shadow-sm",
        status === "done" && "border-green-200 bg-green-50/50",
        status === "idle" && "border-border bg-white opacity-60"
      )}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{icon}</span>
          <span className="font-semibold text-sm">{label}</span>
        </div>
        {status === "running" && <Loader2 className="w-4 h-4 animate-spin text-primary" />}
        {status === "done" && <CheckCircle2 className="w-4 h-4 text-green-500" />}
      </div>
      {output && (
        <div className="text-sm text-muted-foreground whitespace-pre-wrap line-clamp-4 max-h-24 overflow-y-auto">
          {output}
        </div>
      )}
    </div>
  );
}
