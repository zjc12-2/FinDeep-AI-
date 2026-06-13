"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { SearchBar } from "@/components/SearchBar";
import { DataSourceToggle } from "@/components/DataSourceToggle";
import { FileUpload } from "@/components/FileUpload";
import { api } from "@/lib/api";

interface UploadedFile {
  doc_id: string;
  filename: string;
  pages: number;
}

export default function SearchPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [akshare, setAkshare] = useState(true);
  const [news, setNews] = useState(true);
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [error, setError] = useState("");

  const handleSearch = async (query: string) => {
    if (!akshare && !news && files.length === 0) {
      setError("请至少选择一个数据源或上传文档");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const { task_id } = await api.startResearch(query, {
        akshare,
        news,
        uploadedDocs: files.map((f) => f.doc_id),
      });
      router.push(`/report/${task_id}`);
    } catch (err: any) {
      setError(err.message || "启动研究失败");
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-20">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-3">AI驱动的深度金融研报</h1>
        <p className="text-lg text-muted-foreground">
          多智能体对抗性辩论 · 溯源锚定 · 事件链推理
        </p>
      </div>

      <div className="space-y-6">
        <SearchBar onSearch={handleSearch} loading={loading} />

        <DataSourceToggle
          akshare={akshare}
          news={news}
          onAkshareChange={setAkshare}
          onNewsChange={setNews}
        />

        <FileUpload files={files} onChange={setFiles} />

        {error && (
          <div className="p-3 rounded-lg bg-red-50 text-red-600 text-sm">{error}</div>
        )}
      </div>

      <div className="mt-16 grid grid-cols-3 gap-6">
        {[
          { title: "🐂 多方博弈", desc: "Bull/Bear并行分析，模拟真实投资辩论" },
          { title: "🔍 事实核查", desc: "逐条验证数据来源，⚠️标注无支撑推断" },
          { title: "📎 溯源锚定", desc: "点击分析文字，右侧面板高亮原文出处" },
        ].map((f) => (
          <div key={f.title} className="p-4 rounded-xl bg-muted/50 border border-border">
            <h3 className="font-semibold mb-1">{f.title}</h3>
            <p className="text-sm text-muted-foreground">{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
