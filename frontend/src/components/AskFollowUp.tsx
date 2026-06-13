"use client";

import { useState } from "react";
import { Send } from "lucide-react";

interface Props {
  onSubmit: (question: string) => void;
  loading: boolean;
}

export function AskFollowUp({ onSubmit, loading }: Props) {
  const [value, setValue] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim()) {
      onSubmit(value.trim());
      setValue("");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="💬 追问更多细节... 如：海外扩张进展如何？"
        className="flex-1 px-4 py-3 rounded-xl border border-border
                   focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary
                   text-sm"
        disabled={loading}
      />
      <button
        type="submit"
        disabled={loading || !value.trim()}
        className="px-4 py-3 rounded-xl bg-primary text-primary-foreground
                   hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed
                   transition-colors"
      >
        <Send className="w-4 h-4" />
      </button>
    </form>
  );
}
