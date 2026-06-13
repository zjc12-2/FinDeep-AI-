"""FinDeep FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title="FinDeep API",
    description="AI多智能体深度研报生成系统",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.upload import router as upload_router
from app.api.research import router as research_router
from app.api.timeline import router as timeline_router

app.include_router(upload_router)
app.include_router(research_router)
app.include_router(timeline_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "findeep-backend"}
