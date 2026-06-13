# FinDeep - AI多智能体深度研报生成系统

多智能体对抗性辩论 × 溯源锚定 × 事件链推理

---

## 快速开始（2 步启动）

**前置条件：** Python 3.11+ / Node.js 18+

### 1. 配置 API Key

编辑 `.env` 文件，填入至少一个 LLM API Key：

```env
# 三选一即可
ANTHROPIC_API_KEY=sk-ant-...    # Claude（推荐，推理最强）
DEEPSEEK_API_KEY=sk-...         # DeepSeek（性价比高）
OPENAI_API_KEY=sk-...           # OpenAI 或自定义端点
```

### 2. 双击启动

```
双击 start.bat
```

自动完成：安装依赖 → 启动后端(:8000) → 启动前端(:3000)
打开浏览器访问 **http://localhost:3000**

---

## 使用流程

1. 输入公司名称或股票代码（如 "宁德时代 300750"）
2. 选择数据源（金融API / 新闻 / 上传PDF财报）
3. 点击「开始研究」
4. 实时观看 Bull🐂 vs Bear🐻 对抗辩论
5. 获得平衡研报 + 溯源引用 + 事件时间轴
6. 追问细节 / 切换多空视角

---

## 架构

| 层 | 技术 | 端口 |
|---|------|------|
| 前端 | Next.js 14 + Tailwind + shadcn/ui | 3000 |
| 后端 | FastAPI + LangGraph + LlamaIndex | 8000 |
| 向量库 | ChromaDB（本地文件，零依赖） | — |

---

## Docker 模式（可选）

如需用 Docker 运行，修改 `.env` 中 `CHROMA_MODE=docker`，然后：

```bash
docker compose up
```

---

## 项目结构

```
├── frontend/          Next.js 前端
│   └── src/
│       ├── app/       页面路由
│       ├── components/ UI组件（11个）
│       └── lib/       类型定义 + API客户端
├── backend/           FastAPI 后端
│   └── app/
│       ├── agents/     Bull/Bear/FactCheck/Synthesizer
│       ├── rag/        RAG引擎 + 数据源适配器
│       ├── llm/        多Provider LLM层
│       └── api/        REST + SSE 端点
├── data/              本地数据目录
│   └── chroma/        向量存储
├── start.bat          Windows一键启动
└── .env               配置文件
```
