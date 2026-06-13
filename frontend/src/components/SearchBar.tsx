"use client";

import { useState } from "react";
import { Search } from "lucide-react";

interface Props {
  onSearch: (query: string) => void;
  loading: boolean;
}

export function SearchBar({ onSearch, loading }: Props) {
  const [value, setValue] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim()) onSearch(value.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl">
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="输入公司名称、行业或股票代码... 如：宁德时代 300750"
          className="w-full pl-12 pr-24 py-4 rounded-xl border border-border bg-white text-lg
                     focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary
                     placeholder:text-muted-foreground/60"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !value.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 px-6 py-2 rounded-lg
                     bg-primary text-primary-foreground font-medium
                     hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed
                     transition-colors"
        >
          {loading ? "分析中..." : "开始研究"}
        </button>
      </div>
    </form>
  );
}
