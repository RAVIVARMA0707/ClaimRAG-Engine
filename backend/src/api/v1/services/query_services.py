import re
from src.api.v1.tools.vector_search_tool import vector_search
from src.api.v1.tools.fts_search_tool import fts_search
from src.api.v1.tools.hybrid_search_tool import hybrid_search


_KEYWORD_PATTERNS = [
    r"[A-Z]{2,}-\d{4}-\w+",
    r"\b[A-Z]{2,5}\b",
    r"\d{6,}",
]
_KEYWORD_RE = re.compile("|".join(_KEYWORD_PATTERNS))


class QueryServices:

    @staticmethod
    def detect_mode(query: str) -> str:
        stripped = query.strip()
        if _KEYWORD_RE.search(stripped):
            return "keyword"
        if len(stripped.split()) <= 3:
            return "hybrid"
        return "vector"

    @staticmethod
    def query_documents(query: str, k: int = 5) -> list[dict]:
        mode = QueryServices.detect_mode(query)

        if mode == "keyword":
            return fts_search(query, k)

        if mode == "hybrid":
            return hybrid_search(query, k)

        return vector_search(query, k)
    
    @staticmethod
    def user_query(request: str):
        docs = QueryServices.query_documents(request)

        return {
            "query": request,
            "results": "\n".join(doc["content"] for doc in docs),
        }
