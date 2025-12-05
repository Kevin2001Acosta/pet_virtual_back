from .retriever import get_documents_by_query
from .processor import normalize_text

def get_context_rag(query: str) -> str:
    docs = get_documents_by_query(query)
    contexto = [normalize_text(d) for d in docs]
    return "\n".join(contexto)