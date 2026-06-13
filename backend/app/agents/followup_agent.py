"""Follow-up Agent — answers user questions about an existing report."""
import json
from typing import AsyncIterator
from app.llm.provider import get_llm

FOLLOWUP_SYSTEM_PROMPT = """你是一位金融研究助手，负责回答用户针对已有研究报告的追问。

你的职责：
1. 基于已有的研报内容回答用户的追问
2. 如需补充分析，可以基于你的知识提供更多背景
3. 保持与原始报告一致的客观平衡视角
4. 用Markdown格式回复，如果引用了报告中的具体内容，标注对应的ref编号

如果问题超出研报范围，诚实说明并提供你可以提供的相关信息。"""


async def run_followup_agent(
    question: str,
    report_markdown: str,
    citations: dict,
) -> str:
    """Answer a follow-up question based on the existing report.

    Args:
        question: User's follow-up question
        report_markdown: The full report markdown
        citations: Citation mapping from the report

    Returns:
        Markdown-formatted answer
    """
    llm = get_llm("default")

    messages = [
        {"role": "system", "content": FOLLOWUP_SYSTEM_PROMPT},
        {"role": "user", "content": f"""**原始研究报告：**
{report_markdown[:8000]}

**引用来源：**
{json.dumps(citations, ensure_ascii=False, indent=2)[:2000]}

**用户追问：**
{question}

请基于以上信息回答用户的追问。"""},
    ]

    return await llm.chat(messages, max_tokens=2048)
