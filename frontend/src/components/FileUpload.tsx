"use client";

import { useState, useCallback } from "react";
import { Upload, FileText, X } from "lucide-react";
import { api } from "@/lib/api";

interface UploadedFile {
  doc_id: string;
  filename: string;
  pages: number;
}

interface Props {
  files: UploadedFile[];
  onChange: (files: UploadedFile[]) => void;
}

export function FileUpload({ files, onChange }: Props) {
  const [uploading, setUploading] = useState(false);

  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();
      const droppedFiles = Array.from(e.dataTransfer.files);
      await uploadFiles(droppedFiles);
    },
    [files]
  );

  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files || []);
    await uploadFiles(selected);
  };

  const uploadFiles = async (fileList: File[]) => {
    setUploading(true);
    for (const file of fileList) {
      try {
        const result = await api.uploadDocument(file);
        onChange([...files, result]);
      } catch (err) {
        console.error("Upload failed:", file.name, err);
      }
    }
    setUploading(false);
  };

  const removeFile = (docId: string) => {
    onChange(files.filter((f) => f.doc_id !== docId));
  };

  return (
    <div>
      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        className="border-2 border-dashed border-border rounded-xl p-6 text-center
                   hover:border-primary/40 transition-colors cursor-pointer"
      >
        <input
          type="file"
          id="file-upload"
          className="hidden"
          accept=".pdf,.txt,.md,.csv"
          multiple
          onChange={handleFileInput}
        />
        <label htmlFor="file-upload" className="cursor-pointer">
          <Upload className="w-6 h-6 mx-auto mb-2 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            {uploading ? "上传中..." : "拖拽PDF/文档到此处，或点击选择"}
          </p>
          <p className="text-xs text-muted-foreground/60 mt-1">支持 PDF、TXT、Markdown、CSV</p>
        </label>
      </div>

      {files.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {files.map((f) => (
            <div
              key={f.doc_id}
              className="flex items-center gap-2 px-3 py-1.5 bg-muted rounded-lg text-sm"
            >
              <FileText className="w-4 h-4 text-primary" />
              <span>{f.filename}</span>
              <span className="text-muted-foreground">({f.pages}页)</span>
              <button onClick={() => removeFile(f.doc_id)} className="hover:text-red-500">
                <X className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
