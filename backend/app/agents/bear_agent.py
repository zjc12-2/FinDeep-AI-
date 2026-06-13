"""Bear Agent — identifies risks, weaknesses, and negative factors."""
from typing import AsyncIterator
from app.llm.provider import get_llm
from app.rag.engine import RAGEngine

BEAR_SYSTEM_PROMPT = """你是一位资深空方分析师(Bear Analyst)，专注于发现投资风险。

你的职责：
1. 基于提供的资料，找出公司的风险点、竞争威胁和潜在问题
2. 分析行业竞争、财务压力、管理风险、政策变化等负面因素
3. 每个分析结论必须引用具体的检索资料作为支撑，标注来源编号
4. 客观专业，不过度悲观，承认不确定性
5. 用Markdown格式输出，关键数据加粗

输出结构：
## 风险警示
- 风险1 [ref:xxx]
- 风险2 [ref:xxx]

## 潜在压力
1. 压力点1 [ref:xxx]
2. 压力点2 [ref:xxx]

## 需关注的指标
（列出需要持续跟踪的风险指标）

## 总结
（100字以内综合风险评估）"""


async def run_bear_agent(
    query: str,
    rag_engine: RAGEngine,
) -> str:
    """Execute the Bear Agent analysis.

    Args:
        query: Research query
        rag_engine: RAG engine for document retrieval

    Returns:
        Markdown-formatted bear case analysis
    """
    llm = get_llm("bear")

    docs = await rag_engine.search_with_bias(query, bias="bear", top_k=8)

    context_parts = []
    for i, doc in enumerate(docs):
        ref = rag_engine.citations.register(doc)
        context_parts.append(f"--- 资料片段 [{ref.ref_id}] ---\n{doc.text}")

    context = "\n\n".join(context_parts) if context_parts else "无可用的检索资料。"

    messages = [
        {"role": "system", "content": BEAR_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请分析以下公司的投资风险和潜在问题：

**研究标的：** {query}

**检索资料：**
{context}

请基于以上资料，给出你的空方分析报告。每个观点需要标注引用编号。"""},
    ]

    return await llm.chat(messages, max_tokens=4096)


async def run_bear_agent_stream(
    query: str,
    rag_engine: RAGEngine,
) -> AsyncIterator[str]:
    """Streaming version of Bear Agent."""
    llm = get_llm("bear")
    docs = await rag_engine.search_with_bias(query, bias="bear", top_k=8)

    context_parts = []
    for i, doc in enumerate(docs):
        ref = rag_engine.citations.register(doc)
        context_parts.append(f"--- 资料片段 [{ref.ref_id}] ---\n{doc.text}")

    context = "\n\n".join(context_parts) if context_parts else "无可用的检索资料。"

    messages = [
        {"role": "system", "content": BEAR_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请分析以下公司的投资风险和潜在问题：

**研究标的：** {query}

**检索资料：**
{context}

请基于以上资料，给出你的空方分析报告。每个观点需要标注引用编号。"""},
    ]

    async for chunk in llm.chat_stream(messages, max_tokens=4096):
        yield chunk
