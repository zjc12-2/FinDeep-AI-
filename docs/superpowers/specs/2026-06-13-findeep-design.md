# FinDeep-AI 产品设计规格

**日期：** 2026-06-13
**状态：** Approved
**范围：** P0 + P1 + P2 全部功能（MVP完整版）

---

## 一、产品概述

FinDeep（金融深研）是一款AI驱动的多智能体协作金融研报自动生成平台。核心创新在于引入Bull/Bear双方对抗性辩论机制，配合事实核查与溯源锚定，产出平衡、可追溯、有深度的金融研究报告。

### 核心价值

- **对抗性辩论**：多方(Bull)与空方(Bear)并行分析，模拟真实投资博弈
- **溯源锚定**：每条分析结论关联到RAG检索到的原始文档段落
- **事件链推理**：自动构建因果事件时间轴
- **渐进式交互**：概览→展开→追问→视角切换

---

## 二、技术架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                        │
│                                                         │
│  ┌──────────────────┐    ┌──────────────────────────┐   │
│  │  Next.js :3000   │◄──►│  FastAPI :8000            │   │
│  │  (前端 SSR+SPA)   │REST│                          │   │
│  │                  │+SSE│  ┌────────────────────┐  │   │
│  │  / → 首页搜索     │    │  │ LangGraph Agent系统 │  │   │
│  │  /report/{id} →  │    │  │ Bull│Bear│FactCheck │  │   │
│  │    研报展示+溯源  │    │  │     │Synthesize     │  │   │
│  │  /upload → 文档  │    │  └────────────────────┘  │   │
│  │                  │    │  ┌────────────────────┐  │   │
│  │                  │    │  │ RAG引擎(LlamaIndex) │  │   │
│  │                  │    │  │ + 向量检索          │  │   │
│  │                  │    │  └────────────────────┘  │   │
│  └──────────────────┘    │  ┌────────────────────┐  │   │
│                          │  │ 数据源适配层        │  │   │
│  ┌──────────────────┐    │  │ AkShare│用户上传PDF  │  │   │
│  │  ChromaDB :8001  │◄───│  └────────────────────┘  │   │
│  └──────────────────┘    └──────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 2.2 服务组件

| 服务 | 端口 | 技术栈 | 职责 |
|------|------|--------|------|
| Frontend | 3000 | Next.js 14 + Tailwind + shadcn/ui | 页面渲染、SSE消费、交互 |
| Backend | 8000 | Python FastAPI + LangGraph + LlamaIndex | Agent编排、RAG、API |
| VectorDB | 8001 | ChromaDB | 向量存储与相似检索 |

### 2.3 LLM Provider 配置

通过 `.env` 配置文件支持多Provider，每个Agent可独立配置：

```env
# 通用配置
LLM_PROVIDER=claude          # claude | openai | deepseek | openai_compatible
LLM_MODEL=claude-sonnet-4-6

# 按Agent独立配置（可选，覆盖通用配置）
BULL_AGENT_PROVIDER=claude
BULL_AGENT_MODEL=claude-sonnet-4-6
BEAR_AGENT_PROVIDER=claude
BEAR_AGENT_MODEL=claude-sonnet-4-6
FACTCHECK_AGENT_PROVIDER=deepseek
FACTCHECK_AGENT_MODEL=deepseek-chat
SYNTHESIZER_AGENT_PROVIDER=claude
SYNTHESIZER_AGENT_MODEL=claude-sonnet-4-6

# API Keys
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=           # 自定义API端点（openai_compatible时使用）
```

LLM适配层统一接口，支持以下Provider：
- `claude`: Anthropic Claude API
- `openai`: OpenAI API
- `deepseek`: DeepSeek API
- `openai_compatible`: 任意OpenAI兼容端点（自定义URL）

### 2.4 部署方式

**开发/演示：** `docker compose up` 一键启动全部服务
**云部署预留：** 前端可推Vercel，后端可推Railway/Render，ChromaDB可替换为Pinecone/Weaviate云服务

---

## 三、后端设计

### 3.1 API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/research` | 发起研究任务（含数据源选择），返回 task_id |
| `GET` | `/api/research/{task_id}/stream` | SSE 流式推送Agent进度和辩论过程 |
| `GET` | `/api/report/{task_id}` | 获取最终研报JSON（Markdown + 引用映射） |
| `POST` | `/api/upload` | 上传PDF/文档，向量化后返回 doc_id |
| `GET` | `/api/sources/{citation_id}` | 获取引用对应的原文段落 |
| `POST` | `/api/ask` | 追问Agent，针对已有研报深度挖掘 |
| `GET` | `/api/timeline/{task_id}` | 获取事件链时间轴数据 |

### 3.2 LangGraph Agent 工作流

```
POST /api/research { query, uploaded_docs[] }
        │
        ▼
  ┌─ 查询解析 + 全局RAG预检索 ──┐
  │  (LlamaIndex: 财报+新闻+上传文档) │
  └──────────┬─────────────────┘
             │
     ┌───────┴────────┐
     ▼                ▼
🐂 Bull Agent     🐻 Bear Agent        ← LangGraph 并行节点
  多方视角RAG       空方视角RAG
  寻找投资机会       寻找风险隐患
  独立检索上下文     独立检索上下文
     │                │
     └───────┬────────┘
             ▼
     🔍 FactCheck Agent                 ← 顺序节点
       逐条验证双方引用的事实依据
       标记 ⚠️ 无可靠信源支撑的推断
       输出：验证报告 + 可靠性评分
             │
             ▼
     📝 Synthesizer Agent              ← 顺序节点
       融合多方观点 + 事实核查结果
       生成平衡研报
       输出：Markdown报告 + 引用映射表
             │
             ▼
       存储报告 + 返回结果
```

### 3.3 数据源选择（每次研究可选）

用户发起研究时可自由组合数据源——只传PDF、只用API、或两者都用：

```
POST /api/research
{
  "query": "分析宁德时代 300750",
  "data_sources": {
    "akshare": true,        // 是否启用金融API（财报/公告/行情）
    "news": true,           // 是否启用新闻舆情检索
    "uploaded_docs": [      // 用户上传的文档ID列表（空数组=不上传）
      "doc_abc123",
      "doc_def456"
    ]
  }
}
```

前端搜索页提供开关控件：

```
┌──────────────────────────────────────┐
│  🔍 [  输入公司/行业/股票代码...    ] │
│                                      │
│  数据源：                             │
│  [✓] 金融数据API (AkShare)           │
│  [✓] 新闻舆情                        │
│  [📎] 上传PDF财报/研报  [+已选2份]   │
│                                      │
│  [🚀 开始深度研究]                    │
└──────────────────────────────────────┘
```

### 3.4 RAG 数据源适配层

```
class DataSourceAdapter:
    """统一数据源接口"""
    def search(query: str, top_k: int) -> List[Document]
    def load_documents(source_type: str) -> List[Document]
    def is_available() -> bool     # 检查数据源是否可用

# 实现类
AkShareAdapter     # A股财报/公告（免费API）
NewsSearchAdapter  # 新闻舆情检索
UserUploadAdapter  # 用户上传PDF/文档

# RAG引擎根据data_sources配置动态启用适配器
class RAGEngine:
    def __init__(self, data_sources: DataSourceConfig):
        self.adapters = []
        if data_sources.akshare:    self.adapters.append(AkShareAdapter())
        if data_sources.news:       self.adapters.append(NewsSearchAdapter())
        if data_sources.uploaded_docs:
            for doc_id in data_sources.uploaded_docs:
                self.adapters.append(UserUploadAdapter(doc_id))
```

- RAG引擎：LlamaIndex，负责文档解析、分块、向量化、检索
- 向量存储：ChromaDB，持久化到 `./data/chroma`
- 文档解析支持：PDF、TXT、Markdown、CSV
- 空数据源处理：所有数据源都关闭或返回空时，明确告知用户"未选择数据源"或"指定数据源无结果"

### 3.5 引用溯源系统

```
报告中的每条分析性结论：
  "公司Q2营收同比下降12%，主要受行业需求疲软影响[ref:a1b2c3]"

引用映射表：
{
  "ref:a1b2c3": {
    "doc_id": "financial_report_2024Q2.pdf",
    "chunk_index": 42,
    "text": "2024年第二季度营业收入为...",
    "page": 15,
    "confidence": 0.92
  }
}
```

- FactCheck Agent 对无可靠信源的推断标注 ⚠️
- 前端点击 `[ref:xxx]` → 右侧面板高亮对应原文

### 3.6 事件链时间轴

```
事件提取流程：
  研报内容 → LLM提取关键事件(时间+描述+类型)
          → 因果推理(事件A→事件B的概率+证据)
          → 结构化时间轴数据

返回格式：
[
  { "date": "2024-Q2", "event": "营收下降12%", "type": "financial",
    "causes": ["行业需求疲软"], "effects": ["管理层变更"],
    "source_ref": "ref:a1b2c3" },
  ...
]
```

---

## 四、前端设计

### 4.1 页面路由

| 路由 | 页面 | 说明 |
|------|------|------|
| `/` | SearchPage | 搜索入口 + 文件上传 |
| `/report/[task_id]` | ReportPage | 研报展示（核心页面） |
| `/history` | HistoryPage | 历史研报列表 |

### 4.2 ReportPage 布局

```
┌──────────────────────────────────────────────────────────┐
│  [FinDeep Logo]  公司名称 - 研报标题              [导出]  │
├────────────────────────┬─────────────────────────────────┤
│                        │  [溯源面板] [时间轴] ← Tab切换    │
│                        │                                 │
│   富文本报告（Markdown） │  原文高亮区                      │
│                        │                                 │
│   营收同比下降12%[1]    │  > "2024年Q2营业收入为..."       │
│   主要受行业需求...     │    ── financial_report_Q2.pdf    │
│                        │    ── 第15页                     │
│   ⚠️ 该推断暂无可靠     │                                 │
│   信源支撑 ← 事实核查   │                                 │
│   标记                  │                                 │
│                        │                                 │
├────────────────────────┴─────────────────────────────────┤
│  💬 追问更多细节...                    [🐂多方][🐻空方][⚖均衡] │
└──────────────────────────────────────────────────────────┘
```

### 4.3 核心组件

| 组件 | 职责 |
|------|------|
| `SearchBar` | 公司/行业输入，自动补全 |
| `DataSourceToggle` | 数据源开关（金融API/新闻/上传文档） |
| `FileUpload` | 拖拽上传PDF，显示上传进度 |
| `ProgressPanel` | SSE实时显示4个Agent进度卡片 |
| `AgentCard` | 单个Agent状态+输出摘要 |
| `ReportContent` | Markdown渲染 + 引用标注点击 |
| `SidePanel` | 右侧面板容器，Tab切换溯源/时间轴 |
| `SourceTracing` | 引用原文高亮对照 |
| `EventTimeline` | 事件链因果可视化 |
| `AskFollowUp` | 追问输入框 |
| `ViewToggle` | Bull/Bear/Balanced 视角切换 |

### 4.4 交互流程

1. **首页** → 输入公司/行业 → 勾选数据源（API/新闻/上传PDF） → 点击"开始研究"
2. **跳转** → `/report/{task_id}` → SSE连接 → 依次看到Agent卡片激活
3. **辩论阶段** → Bull/Bear卡片并行输出观点片段
4. **事实核查阶段** → FactCheck卡片显示验证结果
5. **报告生成** → ReportContent渲染Markdown报告
6. **交互** → 点击引用 → 右侧溯源面板高亮原文
7. **追问** → 底部输入问题 → 新Agent响应 → 追加到报告
8. **视角切换** → Bull/Bear/Balanced Tab → 同一问题不同解读

### 4.5 SSE 事件类型

```typescript
type SSEEvent =
  | { type: "phase", phase: "bull" | "bear" | "factcheck" | "synthesize" | "done" }
  | { type: "agent_progress", agent: string, chunk: string }
  | { type: "citation", ref_id: string, source: SourceInfo }
  | { type: "warning", message: string, location: string }
  | { type: "error", message: string }
  | { type: "complete", report_id: string }
```

---

## 五、数据流

### 5.1 一次完整研究请求

```
用户输入: "分析宁德时代 300750"
  勾选: [✓]金融API [✓]新闻 [📎]财报Q2.pdf
  │
  ▼
POST /api/research {
  query: "宁德时代 300750",
  data_sources: { akshare: true, news: true, uploaded_docs: ["doc_xyz"] }
}
  │
  ├─► Backend: 解析查询 → 识别股票代码 → 根据data_sources配置适配器
  ├─► Backend: RAG预检索 (仅已启用的数据源)
  │
  ├─► Bull Agent: "寻找宁德时代的投资价值..."
  │     ├─ 重新检索(多方视角prompt)
  │     ├─ 提取正面因素: 市占率、技术领先、产能扩张...
  │     └─ SSE推送: { type: "agent_progress", agent: "bull", chunk: "..." }
  │
  ├─► Bear Agent: (并行) "寻找宁德时代的风险..."
  │     ├─ 重新检索(空方视角prompt)
  │     ├─ 提取负面因素: 竞争加剧、原材料波动、政策变化...
  │     └─ SSE推送: { type: "agent_progress", agent: "bear", chunk: "..." }
  │
  ├─► FactCheck Agent: 逐条验证
  │     ├─ "市占率35%" → 验证: 找到来源 → ✅
  │     ├─ "可能面临产能过剩" → 验证: 无直接数据 → ⚠️
  │     └─ SSE推送验证结果
  │
  ├─► Synthesizer Agent: 融合生成
  │     ├─ 生成Markdown报告
  │     ├─ 建立引用映射表
  │     └─ SSE推送: { type: "complete", report_id: "..." }
  │
  └─► 存储报告到后端 → 前端渲染
```

### 5.2 追问流程

```
用户在报告中追问: "宁德时代的海外扩张进展如何？"
  │
  ▼
POST /api/ask { task_id: "...", question: "海外扩张进展" }
  │
  ├─► 追加RAG检索(聚焦海外业务关键词)
  ├─► 单一Agent生成回答(非辩论，而是深度挖掘)
  └─► 返回追加内容 + 新引用
```

---

## 六、项目目录结构

```
findeep/
├── docker-compose.yml
├── .env.example
├── README.md
│
├── frontend/                          # Next.js 前端
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx              # 首页 (SearchPage)
│   │   │   ├── report/
│   │   │   │   └── [taskId]/
│   │   │   │       └── page.tsx      # 研报页 (ReportPage)
│   │   │   └── history/
│   │   │       └── page.tsx
│   │   ├── components/
│   │   │   ├── SearchBar.tsx
│   │   │   ├── DataSourceToggle.tsx
│   │   │   ├── FileUpload.tsx
│   │   │   ├── ProgressPanel.tsx
│   │   │   ├── AgentCard.tsx
│   │   │   ├── ReportContent.tsx
│   │   │   ├── SidePanel.tsx
│   │   │   ├── SourceTracing.tsx
│   │   │   ├── EventTimeline.tsx
│   │   │   ├── AskFollowUp.tsx
│   │   │   └── ViewToggle.tsx
│   │   ├── lib/
│   │   │   ├── api.ts                # 后端API调用
│   │   │   ├── sse.ts                # SSE客户端
│   │   │   └── types.ts
│   │   └── styles/
│   │       └── globals.css
│   └── public/
│
├── backend/                           # FastAPI 后端
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── alembic.ini                    # 数据库迁移（如需）
│   ├── app/
│   │   ├── main.py                    # FastAPI 入口
│   │   ├── config.py                  # 配置管理（.env加载）
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── research.py            # 研究相关端点
│   │   │   ├── upload.py              # 文件上传端点
│   │   │   └── timeline.py            # 时间轴端点
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── graph.py               # LangGraph 状态图定义
│   │   │   ├── bull_agent.py          # 多方分析师Agent
│   │   │   ├── bear_agent.py          # 空方分析师Agent
│   │   │   ├── factcheck_agent.py     # 事实核查Agent
│   │   │   ├── synthesizer_agent.py   # 综合编辑Agent
│   │   │   └── followup_agent.py      # 追问Agent
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py              # LlamaIndex RAG引擎
│   │   │   ├── datasources/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py            # DataSourceAdapter 基类
│   │   │   │   ├── akshare.py         # AkShare数据源
│   │   │   │   ├── news.py            # 新闻检索
│   │   │   │   └── user_upload.py     # 用户上传文档
│   │   │   └── citation.py            # 引用映射管理
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── provider.py            # 统一LLM接口
│   │   │   └── providers/
│   │   │       ├── __init__.py
│   │   │       ├── claude.py
│   │   │       ├── openai.py
│   │   │       ├── deepseek.py
│   │   │       └── openai_compatible.py
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── research.py            # Pydantic数据模型
│   │       └── schemas.py
│   └── data/
│       └── chroma/                    # ChromaDB持久化目录
│
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-06-13-findeep-design.md
```

---

## 七、关键技术决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| Agent编排 | LangGraph | 支持并行节点，原生状态图，适合辩论流程 |
| RAG框架 | LlamaIndex | 文档解析强，与LangGraph配合好 |
| 向量库 | ChromaDB | 轻量本地可跑，Docker友好 |
| 前端 | Next.js 14 (App Router) | React Server Components + 流式渲染 |
| UI组件 | shadcn/ui | 可定制，Tailwind原生 |
| 前后端通信 | REST + SSE | REST用于操作，SSE用于流式Agent进度 |
| 样式 | Tailwind CSS | 快速开发，与shadcn/ui一致 |
| 部署 | Docker Compose | 一键启动，演示友好 |

---

## 八、错误处理策略

### 后端
- LLM调用失败：重试3次 + 指数退避 + 降级到简化流程
- 外部API（AkShare）不可用：返回缓存数据或友好提示
- RAG检索为空：明确告知用户"未找到相关数据"，不编造
- 文档解析失败：支持的文件类型校验 + 解析错误提示

### 前端
- SSE连接断开：自动重连 + 显示连接状态
- 报告生成超时（>5分钟）：显示部分结果 + 继续等待按钮
- 空状态：每个组件都有空状态占位
- 错误边界：每个页面有ErrorBoundary

---

## 九、测试策略

| 层级 | 方法 | 覆盖范围 |
|------|------|----------|
| 单元测试 | pytest (后端) + vitest (前端) | Agent逻辑、数据模型、组件渲染 |
| 集成测试 | pytest + TestClient | API端点、RAG检索、Agent工作流 |
| E2E | Playwright | 关键用户路径（搜索→报告→追问） |
| Mock | LLM mock 用于CI | Agent测试不依赖真实API |

---

## 十、自检清单

- [x] 无 TBD/TODO 占位符
- [x] 架构与功能描述一致
- [x] 范围明确：P0+P1+P2全部功能
- [x] 需求无歧义

---

## 附录：与原设计方案的对应关系

| 原方案要求 | 本设计覆盖 |
|-----------|-----------|
| 多智能体对抗性辩论 | LangGraph Bull/Bear并行 → FactCheck → Synthesize |
| 溯源锚定引文系统 | 引用映射表 + SourceTracing组件 |
| 事件链时间推理 | 事件提取 → 因果推断 → EventTimeline组件 |
| 渐进式深度钻取 | 概览→展开→追问 + ViewToggle视角切换 |
| Next.js + FastAPI | 前后端分离，REST + SSE |
| LangGraph + LlamaIndex + ChromaDB | 全部采用 |
| 多Provider LLM | 统一接口 + .env配置 |
