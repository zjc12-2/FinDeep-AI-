"""News search adapter using web-based retrieval."""
from typing import List
from app.rag.datasources.base import DataSourceAdapter, Document
from app.llm.provider import get_llm


class NewsSearchAdapter(DataSourceAdapter):
    source_type = "news"

    async def search(self, query: str, top_k: int = 5) -> List[Document]:
        """Use LLM to summarize relevant news context for the query.
        In production, this would integrate with a news API (e.g., NewsAPI, Bing).
        For MVP, we structure the query context as a synthetic news brief.
        """
        llm = get_llm("default")
        prompt = f"""你是一位财经新闻分析师。关于"{query}"，请基于你的知识提供最新的相关新闻要点。
格式：每条新闻一行，包含简要描述。如果涉及具体数据，请注明。"""

        try:
            response = await llm.chat([
                {"role": "user", "content": prompt}
            ], max_tokens=1024)
            return [Document(
                text=response,
                doc_id="news_context",
                source_type="news",
                metadata={"query": query},
            )]
        except Exception:
            return []

    async def is_available(self) -> bool:
        return True
