"""LangGraph state graph for multi-agent debate orchestration.

Workflow:
  START -> pre_search -> parallel(Bull | Bear) -> FactCheck -> Synthesizer -> END

The Bull and Bear agents run in parallel via LangGraph's Send API.
"""
import asyncio
import json
import operator
from typing import TypedDict, Annotated, AsyncIterator, List
from langgraph.graph import StateGraph, END
from app.models.research import DataSourceConfig
from app.rag.engine import RAGEngine
from app.agents.bull_agent import run_bull_agent
from app.agents.bear_agent import run_bear_agent
from app.agents.factcheck_agent import run_factcheck_agent
from app.agents.synthesizer_agent import run_synthesizer_agent


class ResearchState(TypedDict):
    query: str
    data_sources: DataSourceConfig
    pre_search_docs: list
    bull_analysis: str
    bear_analysis: str
    factcheck_analysis: str
    final_report: str
    citations: dict
    error: str


async def pre_search_node(state: ResearchState) -> ResearchState:
    """Initial RAG search to gather context for all agents."""
    rag = RAGEngine(state["data_sources"])
    if not rag.has_sources():
        state["error"] = "未选择任何数据源。请至少启用一个数据源或上传文档。"
    else:
        state["pre_search_docs"] = []  # Will be done per-agent
    return state


async def bull_node(state: ResearchState) -> ResearchState:
    """Execute Bull Agent analysis."""
    if state.get("error"):
        return state
    rag = RAGEngine(state["data_sources"])
    try:
        state["bull_analysis"] = await run_bull_agent(state["query"], rag)
        # Collect citations from Bull
        state["citations"] = rag.citations.to_dict()
    except Exception as e:
        state["bull_analysis"] = f"Bull分析生成失败: {str(e)}"
    return state


async def bear_node(state: ResearchState) -> ResearchState:
    """Execute Bear Agent analysis."""
    if state.get("error"):
        return state
    rag = RAGEngine(state["data_sources"])
    try:
        state["bear_analysis"] = await run_bear_agent(state["query"], rag)
        # Merge citations from Bear
        bear_citations = rag.citations.to_dict()
        if state.get("citations"):
            state["citations"].update(bear_citations)
        else:
            state["citations"] = bear_citations
    except Exception as e:
        state["bear_analysis"] = f"Bear分析生成失败: {str(e)}"
    return state


async def factcheck_node(state: ResearchState) -> ResearchState:
    """Execute FactCheck Agent on both analyses."""
    if state.get("error"):
        return state
    rag = RAGEngine(state["data_sources"])
    try:
        state["factcheck_analysis"] = await run_factcheck_agent(
            state.get("bull_analysis", ""),
            state.get("bear_analysis", ""),
            rag,
        )
        # Merge citations
        fc_citations = rag.citations.to_dict()
        if state.get("citations"):
            state["citations"].update(fc_citations)
    except Exception as e:
        state["factcheck_analysis"] = f"事实核查失败: {str(e)}"
    return state


async def synthesizer_node(state: ResearchState) -> ResearchState:
    """Synthesize all analyses into final report."""
    if state.get("error"):
        state["final_report"] = f"# 研究失败\n\n错误: {state['error']}"
        return state
    try:
        state["final_report"] = await run_synthesizer_agent(
            state["query"],
            state.get("bull_analysis", ""),
            state.get("bear_analysis", ""),
            state.get("factcheck_analysis", ""),
        )
    except Exception as e:
        state["final_report"] = f"# 报告生成失败\n\n错误: {str(e)}"
    return state


def build_research_graph() -> StateGraph:
    """Build the LangGraph state graph for research workflow."""
    workflow = StateGraph(ResearchState)

    workflow.add_node("pre_search", pre_search_node)
    workflow.add_node("bull", bull_node)
    workflow.add_node("bear", bear_node)
    workflow.add_node("factcheck", factcheck_node)
    workflow.add_node("synthesizer", synthesizer_node)

    workflow.set_entry_point("pre_search")

    # pre_search -> both bull AND bear (parallel)
    workflow.add_edge("pre_search", "bull")
    workflow.add_edge("pre_search", "bear")

    # Both must complete before factcheck
    workflow.add_edge("bull", "factcheck")
    workflow.add_edge("bear", "factcheck")

    # factcheck -> synthesizer -> END
    workflow.add_edge("factcheck", "synthesizer")
    workflow.add_edge("synthesizer", END)

    return workflow.compile()


async def run_research(
    query: str,
    data_sources: DataSourceConfig,
) -> ResearchState:
    """Run the full research workflow and return final state."""
    graph = build_research_graph()
    initial_state: ResearchState = {
        "query": query,
        "data_sources": data_sources,
        "pre_search_docs": [],
        "bull_analysis": "",
        "bear_analysis": "",
        "factcheck_analysis": "",
        "final_report": "",
        "citations": {},
        "error": "",
    }
    result = await graph.ainvoke(initial_state)
    return result
