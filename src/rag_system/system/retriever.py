import os
from pypdf import PdfReader
from .vector import vector_store

class ChromaRetriever:
    def __init__(self):
        self.vector_store = vector_store
        self._initialize_data()
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extraer texto de PDF"""
        text = ""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error leyendo PDF {pdf_path}: {e}")
        return text.strip()
    
    def _process_pdf_content(self, text: str, filename: str):
        """Dividir PDF en chunks/párrafos para mejor búsqueda"""
        # Dividir por párrafos (saltos de línea dobles)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        documents = []
        metadata = []
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph) > 50:  # Párrafos significativos
                documents.append(paragraph)
                metadata.append({
                    'categoria': 'tecnica_estres',
                    'emocion': 'general', 
                    'fuente': filename,
                    'chunk_id': i
                })
        
        return documents, metadata
    
    def _initialize_data(self):
        """Cargar PDFs directamente a Chroma"""
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        
        all_documents = []
        all_metadata = []
        
        # Cargar todos los archivos PDF
        for filename in os.listdir(data_dir):
            if filename.endswith('.pdf'):
                filepath = os.path.join(data_dir, filename)
                print(f"Procesando PDF: {filename}")
                
                # Extraer texto del PDF
                pdf_text = self._extract_text_from_pdf(filepath)
                
                if pdf_text:
                    # Procesar y dividir el contenido
                    documents, metadata = self._process_pdf_content(pdf_text, filename)
                    all_documents.extend(documents)
                    all_metadata.extend(metadata)
        
        # Añadir a Chroma
        if all_documents:
            self.vector_store.add_documents(all_documents, all_metadata)
            print(f"PDFs cargados: {len(all_documents)} chunks")
        else:
            print("No se encontraron PDFs o estaban vacíos")
    
    def buscar_documentos(self, query: str, n_results: int = 3):
        """Buscar usando Chroma"""
        results = self.vector_store.search(query, n_results)
        return results['documents'][0] if results['documents'] else []

# Instancia global
retriever = ChromaRetriever()

def buscar_documentos(query: str):
    return retriever.buscar_documentos(query)