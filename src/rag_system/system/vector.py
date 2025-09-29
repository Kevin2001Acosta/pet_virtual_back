import chromadb
import os
from sentence_transformers import SentenceTransformer

class ChromaVectorStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection("conocimiento_mascota")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    def add_documents(self, documents: list, metadata: list = None):
        """Añadir documentos a Chroma"""
        if not documents:
            return
        
        # Generar IDs únicos
        ids = [f"doc_{i}" for i in range(len(documents))]
        
        # Generar embeddings
        embeddings = self.embedder.encode(documents).tolist()
        
        # Añadir a Chroma
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadata if metadata else [{}] * len(documents),
            ids=ids
        )
    
    def search(self, query: str, n_results: int = 3):
        """Buscar documentos similares"""
        query_embedding = self.embedder.encode([query]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        return results

# Instancia global
vector_store = ChromaVectorStore()