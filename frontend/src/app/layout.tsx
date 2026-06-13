import type { Metadata } from "next";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "FinDeep - AI深度研报",
  description: "AI驱动的多智能体协作金融研究报告自动生成平台",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-background text-foreground">
        <header className="border-b border-border px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center gap-2">
            <span className="text-2xl font-bold text-primary">FinDeep</span>
            <span className="text-sm text-muted-foreground">金融深研</span>
          </div>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
