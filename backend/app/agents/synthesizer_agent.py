"""Synthesizer Agent — merges Bull/Bear/FactCheck into a balanced final report."""
from typing import AsyncIterator
from app.llm.provider import get_llm

SYNTHESIZER_SYSTEM_PROMPT = """你是一位资深综合编辑(Synthesizer)，负责将多方观点融合为一份平衡、专业的金融研究报告。

你的职责：
1. 综合Bull、Bear和FactCheck的分析结果
2. 产出完整的Markdown格式研究报告
3. 保持平衡视角——既呈现机会也呈现风险
4. 保留原有的引用标注 [ref:xxx]
5. 重要发现用 ⚠️（需关注）和 ✅（已验证）标记

报告结构：
# [公司名称] 深度研究报告

## 一、核心摘要
（200字概览，平衡呈现多空观点）

## 二、多方视角：投资机会
（来自Bull分析的精炼内容）

## 三、空方视角：风险警示
（来自Bear分析的精炼内容）

## 四、事实核查与可靠性评估
（来自FactCheck的验证结果）

## 五、综合评估
（平衡结论，不做买卖建议）

---
*⚠️ 声明：本报告由AI自动生成，仅供参考，不构成投资建议。*"""


async def run_synthesizer_agent(
    query: str,
    bull_analysis: str,
    bear_analysis: str,
    factcheck_analysis: str,
) -> str:
    """Synthesize all analyses into a final balanced report.

    Args:
        query: Original research query
        bull_analysis: Bull Agent output
        bear_analysis: Bear Agent output
        factcheck_analysis: FactCheck Agent output

    Returns:
        Final Markdown research report
    """
    llm = get_llm("synthesizer")

    messages = [
        {"role": "system", "content": SYNTHESIZER_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请综合以下三份分析，生成一份平衡的最终研究报告：

**研究标的：** {query}

**Bull分析：**
{bull_analysis}

**Bear分析：**
{bear_analysis}

**事实核查：**
{factcheck_analysis}

请严格按照报告结构输出，保留引用标注。"""},
    ]

    return await llm.chat(messages, max_tokens=8192)


async def run_synthesizer_agent_stream(
    query: str,
    bull_analysis: str,
    bear_analysis: str,
    factcheck_analysis: str,
) -> AsyncIterator[str]:
    """Streaming version of Synthesizer Agent."""
    llm = get_llm("synthesizer")

    messages = [
        {"role": "system", "content": SYNTHESIZER_SYSTEM_PROMPT},
        {"role": "user", "content": f"""请综合以下三份分析，生成一份平衡的最终研究报告：

**研究标的：** {query}

**Bull分析：**
{bull_analysis}

**Bear分析：**
{bear_analysis}

**事实核查：**
{factcheck_analysis}

请严格按照报告结构输出，保留引用标注。"""},
    ]

    async for chunk in llm.chat_stream(messages, max_tokens=8192):
        yield chunk
