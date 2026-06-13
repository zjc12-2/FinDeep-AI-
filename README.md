# FinDeep - AI多智能体深度研报生成系统

## Quick Start

1. Copy `.env.example` to `.env` and fill in your API keys
2. Run `docker compose up`
3. Open http://localhost:3000

## Architecture

- Frontend: Next.js 14 + Tailwind + shadcn/ui (:3000)
- Backend: FastAPI + LangGraph + LlamaIndex (:8000)
- Vector DB: ChromaDB (:8001)
