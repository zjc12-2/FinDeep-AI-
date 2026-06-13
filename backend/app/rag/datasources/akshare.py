"""AkShare financial data adapter for A-share market."""
from typing import List
from app.rag.datasources.base import DataSourceAdapter, Document


class AkShareAdapter(DataSourceAdapter):
    source_type = "akshare"

    async def search(self, query: str, top_k: int = 5) -> List[Document]:
        """Fetch financial data from AkShare based on stock code or company name."""
        try:
            import akshare as ak
        except ImportError:
            return []

        docs = []
        stock_code = _extract_stock_code(query)

        if stock_code:
            try:
                # Fetch basic company info
                info = ak.stock_individual_info_em(symbol=stock_code)
                text_parts = []
                for _, row in info.iterrows():
                    text_parts.append(f"{row['item']}: {row['value']}")
                text = "\n".join(text_parts)
                docs.append(Document(
                    text=text,
                    doc_id=f"akshare_info_{stock_code}",
                    source_type="akshare",
                    metadata={"stock_code": stock_code},
                ))
            except Exception:
                pass

            try:
                # Fetch financial statements summary
                fin = ak.stock_financial_abstract(symbol=stock_code)
                if fin is not None and not fin.empty:
                    recent = fin.head(10)
                    text = "财务指标摘要:\n" + recent.to_string()
                    docs.append(Document(
                        text=text,
                        doc_id=f"akshare_fin_{stock_code}",
                        source_type="akshare",
                        metadata={"stock_code": stock_code},
                    ))
            except Exception:
                pass

        return docs[:top_k]

    async def is_available(self) -> bool:
        try:
            import akshare
            return True
        except ImportError:
            return False


def _extract_stock_code(query: str) -> str:
    """Extract 6-digit stock code from query string."""
    import re
    match = re.search(r'\b(\d{6})\b', query)
    return match.group(1) if match else ""
