"""FactCheck Agent — verifies claims from Bull and Bear analyses."""
from typing import AsyncIterator
from app.llm.provider import get_llm
from app.rag.engine import RAGEngine

FACTCHECK_SYSTEM_PROMPT = """你是一位严谨的事实核查员(Fact Checker)，负责验证分析师的观点是否有可靠的资料来源支撑。

你的职责：
1. 逐一审查Bull和Bear分析师的每个重要论断
2. 检查每个论断在检索资料中是否有对应支撑
3. 标记 ⚠️ 任何缺乏可靠信源支撑的推断
4. 标记 ✅ 有明确来源支撑的论断
5. 不表达你自己的投资观点，只做事实验证

输出结构：
## 事实核查报告

### ✅ 有信源支撑的论断
- 论断内容 → 来源: [ref:xxx]

### ⚠️ 缺乏可靠支撑的推断
- 论断内容 → 原因: 未在检索资料中找到直接证据

### 📊 总体可靠性评估
（百分比，并解释）"""


async def run_factcheck_agent(
    bull_analysis: str,
    bear_analysis: str,
    rag_engine: RAGEngine,
) -> str:
    """Verify claims from both analysts against available sources.

    Args:
        bull_analysis: Bull Agent's output
        bear_analysis: Bear Agent's output
        rag_engine: RAG engine with registered citations

    Returns:
        Markdown-formatted fact-check report
    """
    llm = get_llm("factcheck")

    citations_list = []
    for ref_id, c in rag_engine.citations.get_all().items():
        citations_list.append(f"[{ref_id}] {c.text[:200]}...")

    citations_text = "\n".join(citations_list) if citations_list else "无可验证的引用来源。"

    messages = [
        {"role": "system", "content": FACTCHECK_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请验证以下两份分析的可靠性：

**可用引用来源：**
{citations_text}

**多方分析师(Bull)报告：**
{bull_analysis}

**空方分析师(Bear)报告：**
{bear_analysis}

请逐条验证关键论断，区分有支撑的结论和缺乏支撑的推断。"""},
    ]

    return await llm.chat(messages, max_tokens=4096)


async def run_factcheck_agent_stream(
    bull_analysis: str,
    bear_analysis: str,
    rag_engine: RAGEngine,
) -> AsyncIterator[str]:
    """Streaming version of FactCheck Agent."""
    llm = get_llm("factcheck")

    citations_list = []
    for ref_id, c in rag_engine.citations.get_all().items():
        citations_list.append(f"[{ref_id}] {c.text[:200]}...")

    citations_text = "\n".join(citations_list) if citations_list else "无可验证的引用来源。"

    messages = [
        {"role": "system", "content": FACTCHECK_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请验证以下两份分析的可靠性：

**可用引用来源：**
{citations_text}

**多方分析师(Bull)报告：**
{bull_analysis}

**空方分析师(Bear)报告：**
{bear_analysis}

请逐条验证关键论断，区分有支撑的结论和缺乏支撑的推断。"""},
    ]

    async for chunk in llm.chat_stream(messages, max_tokens=4096):
        yield chunk
