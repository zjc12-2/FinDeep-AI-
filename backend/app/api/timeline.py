"""Timeline API — extract event chains from research reports."""
from fastapi import APIRouter, HTTPException
from app.llm.provider import get_llm
from app.api.research import _reports

router = APIRouter(prefix="/api", tags=["timeline"])

TIMELINE_EXTRACTION_PROMPT = """从以下研究报告内容中提取关键事件链。

对每个事件提取：
- date: 时间（如 2024-Q2）
- event: 事件描述（简短）
- type: 类型（financial, management, market, other）
- causes: 导致此事件的原因列表
- effects: 此事件导致的结果列表
- source_ref: 相关的引用编号（如无则填null）

返回严格JSON数组格式，不要包含markdown代码块标记：
[
  {"date": "...", "event": "...", "type": "...", "causes": [...], "effects": [...], "source_ref": "ref:xxx"},
  ...
]"""


@router.get("/timeline/{task_id}")
async def get_timeline(task_id: str):
    """Extract event timeline from a completed report."""
    report = _reports.get(task_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    llm = get_llm("default")
    try:
        import json
        response = await llm.chat([
            {"role": "system", "content": "你是一位金融数据分析师。只输出JSON，不要包含其他文字。"},
            {"role": "user", "content": f"{TIMELINE_EXTRACTION_PROMPT}\n\n报告内容：\n{report.markdown[:8000]}"},
        ], max_tokens=2048)

        # Clean potential markdown code fences
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

        events = json.loads(cleaned)
        return {"events": events}
    except Exception as e:
        return {"events": [], "error": str(e)}
