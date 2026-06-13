"""Research API endpoints — initiate research and stream progress via SSE."""
import json
import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.research import ResearchRequest, ResearchTask, ResearchReport, DataSourceConfig
from app.agents.graph import run_research, ResearchState
from app.rag.engine import RAGEngine
from app.agents.bull_agent import run_bull_agent_stream
from app.agents.bear_agent import run_bear_agent_stream
from app.agents.factcheck_agent import run_factcheck_agent_stream
from app.agents.synthesizer_agent import run_synthesizer_agent_stream
from app.agents.followup_agent import run_followup_agent
from app.models.research import FollowUpRequest

router = APIRouter(prefix="/api", tags=["research"])

# In-memory task store (replace with DB in production)
_tasks: dict = {}
_reports: dict = {}


@router.post("/research")
async def create_research(request: ResearchRequest):
    """Initiate a new research task. Returns task_id immediately."""
    if not request.data_sources.akshare and not request.data_sources.news and not request.data_sources.uploaded_docs:
        raise HTTPException(status_code=400, detail="至少需要选择一个数据源或上传文档")

    task = ResearchTask(
        query=request.query,
        data_sources=request.data_sources,
        status="pending",
        created_at=datetime.now().isoformat(),
    )
    _tasks[task.task_id] = task

    # Start research in background
    asyncio.create_task(_execute_research(task.task_id, request))

    return {"task_id": task.task_id, "status": "pending"}


async def _execute_research(task_id: str, request: ResearchRequest):
    """Run the full research workflow in background and store the result."""
    _tasks[task_id].status = "running"
    try:
        result = await run_research(request.query, request.data_sources)
        _reports[task_id] = ResearchReport(
            task_id=task_id,
            query=request.query,
            markdown=result.get("final_report", ""),
            citations=result.get("citations", {}),
            bull_view=result.get("bull_analysis", ""),
            bear_view=result.get("bear_analysis", ""),
            factcheck_notes=_extract_factcheck_warnings(result.get("factcheck_analysis", "")),
            created_at=datetime.now().isoformat(),
        )
        _tasks[task_id].status = "completed"
    except Exception as e:
        _tasks[task_id].status = "failed"
        _reports[task_id] = ResearchReport(
            task_id=task_id,
            query=request.query,
            markdown=f"# 研究失败\n\n错误: {str(e)}",
            citations={},
            created_at=datetime.now().isoformat(),
        )


def _extract_factcheck_warnings(factcheck_text: str) -> list:
    """Extract warning items from factcheck output."""
    warnings = []
    for line in factcheck_text.split("\n"):
        if "⚠️" in line or "⚠" in line:
            warnings.append(line.strip())
    return warnings


@router.get("/research/{task_id}/stream")
async def stream_research(task_id: str):
    """SSE endpoint — streams agent progress during research."""
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    async def event_stream():
        """Generate SSE events for the research progress."""
        try:
            # Phase 1: Bull Agent
            yield _sse_event("phase", {"phase": "bull"})
            rag_bull = RAGEngine(task.data_sources)
            bull_chunks = []
            async for chunk in run_bull_agent_stream(task.query, rag_bull):
                bull_chunks.append(chunk)
                yield _sse_event("agent_progress", {"agent": "bull", "chunk": chunk})
            bull_analysis = "".join(bull_chunks)

            # Collect Bull citations
            bull_citations = rag_bull.citations.to_dict()
            for ref_id, c in bull_citations.items():
                yield _sse_event("citation", {"ref_id": ref_id, "source": c})

            # Phase 2: Bear Agent
            yield _sse_event("phase", {"phase": "bear"})
            rag_bear = RAGEngine(task.data_sources)
            bear_chunks = []
            async for chunk in run_bear_agent_stream(task.query, rag_bear):
                bear_chunks.append(chunk)
                yield _sse_event("agent_progress", {"agent": "bear", "chunk": chunk})
            bear_analysis = "".join(bear_chunks)

            # Merge Bear citations
            bear_citations = rag_bear.citations.to_dict()
            for ref_id, c in bear_citations.items():
                if ref_id not in bull_citations:
                    yield _sse_event("citation", {"ref_id": ref_id, "source": c})

            all_citations = {**bull_citations, **bear_citations}

            # Phase 3: FactCheck
            yield _sse_event("phase", {"phase": "factcheck"})
            rag_fc = RAGEngine(task.data_sources)
            fc_chunks = []
            async for chunk in run_factcheck_agent_stream(bull_analysis, bear_analysis, rag_fc):
                fc_chunks.append(chunk)
                yield _sse_event("agent_progress", {"agent": "factcheck", "chunk": chunk})
            factcheck_analysis = "".join(fc_chunks)

            # Check for warnings
            for line in factcheck_analysis.split("\n"):
                if "⚠️" in line or "⚠" in line:
                    yield _sse_event("warning", {"message": line.strip(), "location": "factcheck"})

            # Phase 4: Synthesizer
            yield _sse_event("phase", {"phase": "synthesize"})
            report_chunks = []
            async for chunk in run_synthesizer_agent_stream(
                task.query, bull_analysis, bear_analysis, factcheck_analysis
            ):
                report_chunks.append(chunk)
                yield _sse_event("agent_progress", {"agent": "synthesizer", "chunk": chunk})
            final_report = "".join(report_chunks)

            # Store the report
            _reports[task_id] = ResearchReport(
                task_id=task_id,
                query=task.query,
                markdown=final_report,
                citations=all_citations,
                bull_view=bull_analysis,
                bear_view=bear_analysis,
                factcheck_notes=_extract_factcheck_warnings(factcheck_analysis),
                created_at=datetime.now().isoformat(),
            )
            _tasks[task_id].status = "completed"

            yield _sse_event("complete", {"report_id": task_id})

        except Exception as e:
            _tasks[task_id].status = "failed"
            yield _sse_event("error", {"message": str(e)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def _sse_event(event_type: str, data: dict) -> str:
    """Format a Server-Sent Event."""
    return f"data: {json.dumps({'type': event_type, **data}, ensure_ascii=False)}\n\n"


@router.get("/report/{task_id}")
async def get_report(task_id: str):
    """Get the final research report."""
    report = _reports.get(task_id)
    if not report:
        task = _tasks.get(task_id)
        if task and task.status == "running":
            return {"status": "running", "message": "报告生成中，请等待..."}
        raise HTTPException(status_code=404, detail="Report not found")
    return report.model_dump()


@router.get("/sources/{citation_id}")
async def get_source(citation_id: str):
    """Get the original source text for a citation."""
    # Search through all task reports for the citation
    for task_id, report in _reports.items():
        if citation_id in report.citations:
            return report.citations[citation_id]
    raise HTTPException(status_code=404, detail="Citation not found")


@router.post("/ask")
async def ask_followup(request: FollowUpRequest):
    """Ask a follow-up question about an existing report."""
    report = _reports.get(request.task_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    try:
        answer = await run_followup_agent(
            question=request.question,
            report_markdown=report.markdown,
            citations=report.citations,
        )
        return {"answer": answer, "task_id": request.task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"追问失败: {str(e)}")
