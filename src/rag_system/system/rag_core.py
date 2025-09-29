from .retriever import buscar_documentos
from .processor import procesar_texto

def obtener_contexto_rag(query: str) -> str:
    docs = buscar_documentos(query)
    contexto = [procesar_texto(d) for d in docs]
    return "\n".join(contexto)
