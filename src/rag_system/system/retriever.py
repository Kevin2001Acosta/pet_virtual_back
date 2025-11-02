
import os
from pypdf import PdfReader
from .vector import vector_store
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ChromaRetriever:
    def __init__(self):
        self.vector_store = vector_store
        self._initialized = False
        self._initialize_data()

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        text = ""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error leyendo PDF {pdf_path}: {e}")
        return text.strip()
    
    
    #Chunks
    def _process_pdf_content(self, text: str, filename: str):
            
    # --- 1. CONFIGURACIÓN Y DIVISIÓN USANDO EL SPLITTER RECURSIVO ---
    
    # 1. Configura el separador
        splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,       
        chunk_overlap=100,     
        separators=["\n\n", "\n", " ", ""] 
    )
    
    # 2. Divide el texto. 
        final_chunks = splitter.split_text(text)
    
    # 3. Filtra chunks muy pequeños 
        documents = [c.strip() for c in final_chunks if len(c.strip()) > 50] 
    
    # --- 2. GENERACIÓN DE METADATOS ---
        metadata = []
    
    # Ahora iteramos sobre la lista 'documents' generada por el splitter.
        for i, chunk in enumerate(documents):
            metadata.append({
                'categoria': 'general',
                'emocion': 'general', 
                'fuente': filename,
                'chunk_id': i,
                'longitud': len(chunk) 
            })
            
        print(f"  - Chunks creados: {len(documents)} (tamaño avg: {sum(len(d) for d in documents)//len(documents) if documents else 0})")

        return documents, metadata

    def _initialize_data(self):
      
        if self._initialized:
            return
            
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        
        all_documents = []
        all_metadata = []
        
        for filename in os.listdir(data_dir):
            if filename.endswith('.pdf'):
                filepath = os.path.join(data_dir, filename)
                print(f"Procesando: {filename}")
                
                pdf_text = self._extract_text_from_pdf(filepath)
                
                if pdf_text:
                    documents, metadata = self._process_pdf_content(pdf_text, filename)
                    all_documents.extend(documents)
                    all_metadata.extend(metadata)
        
        if all_documents:
            self.vector_store.add_documents(all_documents, all_metadata)
            self._initialized = True
            print(f"PDFs cargados: {len(all_documents)} chunks")

    def buscar_documentos(self, query: str, n_results: int = 3):
   
        try:
            results = self.vector_store.search(query, n_results)
            #print(results)
            
            #print(f"Estructura results: {list(results.keys())}")
            #print("Fin estructura")
                        
            if results['documents'] and len(results['documents']) > 0:
                #print(f"documentos: {results['documents']}")

                documentos = results['documents'][0] 
                
                #metadatos = results['metadatas'][0] if results['metadatas'] else []
                
                return documentos
            else:
                print("No hay documentos")
                return []
                
        except Exception as e:
            print(f"Error en búsqueda: {e}")
            return []
        
        

# Instancia global
retriever = ChromaRetriever()

def buscar_documentos(query: str):
    return retriever.buscar_documentos(query, n_results=3)

