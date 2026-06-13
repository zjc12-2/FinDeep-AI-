"""Bull Agent — finds investment opportunities and positive factors."""
from typing import AsyncIterator
from app.llm.provider import get_llm
from app.rag.engine import RAGEngine
from app.rag.datasources.base import Document

BULL_SYSTEM_PROMPT = """你是一位资深多方分析师(Bull Analyst)，专注于发现投资机会。

你的职责：
1. 基于提供的资料，找出公司的竞争优势、增长潜力和投资价值
2. 分析行业趋势、市场份额、技术创新、管理能力等正面因素
3. 每个分析结论必须引用具体的检索资料作为支撑，标注来源编号
4. 客观专业，不过度乐观，承认不确定性
5. 用Markdown格式输出，关键数据加粗

输出结构：
## 投资亮点
- 亮点1 [ref:xxx]
- 亮点2 [ref:xxx]

## 增长驱动因素
1. 因素1 [ref:xxx]
2. 因素2 [ref:xxx]

## 估值参考
（基于可用数据）

## 总结
（100字以内综合评估）"""


async def run_bull_agent(
    query: str,
    rag_engine: RAGEngine,
) -> str:
    """Execute the Bull Agent analysis.

    Args:
        query: Research query (company name / stock code)
        rag_engine: RAG engine for document retrieval

    Returns:
        Markdown-formatted bull case analysis
    """
    llm = get_llm("bull")

    # Retrieve documents with bullish bias
    docs = await rag_engine.search_with_bias(query, bias="bull", top_k=8)

    # Build context from retrieved documents
    context_parts = []
    for i, doc in enumerate(docs):
        ref = rag_engine.citations.register(doc)
        context_parts.append(f"--- 资料片段 [{ref.ref_id}] ---\n{doc.text}")

    context = "\n\n".join(context_parts) if context_parts else "无可用的检索资料。"

    messages = [
        {"role": "system", "content": BULL_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请分析以下公司的投资价值和多方因素：

**研究标的：** {query}

**检索资料：**
{context}

请基于以上资料，给出你的多方分析报告。每个观点需要标注引用编号。"""},
    ]

    return await llm.chat(messages, max_tokens=4096)


async def run_bull_agent_stream(
    query: str,
    rag_engine: RAGEngine,
) -> AsyncIterator[str]:
    """Streaming version of Bull Agent."""
    llm = get_llm("bull")
    docs = await rag_engine.search_with_bias(query, bias="bull", top_k=8)

    context_parts = []
    for i, doc in enumerate(docs):
        ref = rag_engine.citations.register(doc)
        context_parts.append(f"--- 资料片段 [{ref.ref_id}] ---\n{doc.text}")

    context = "\n\n".join(context_parts) if context_parts else "无可用的检索资料。"

    messages = [
        {"role": "system", "content": BULL_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请分析以下公司的投资价值和多方因素：

**研究标的：** {query}

**检索资料：**
{context}

请基于以上资料，给出你的多方分析报告。每个观点需要标注引用编号。"""},
    ]

    async for chunk in llm.chat_stream(messages, max_tokens=4096):
        yield chunk
