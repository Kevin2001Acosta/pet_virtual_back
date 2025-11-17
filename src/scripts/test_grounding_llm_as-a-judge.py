import pandas as pd
import os, time
from langchain_openai import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.rag_system.system.rag_core import obtener_contexto_rag
from dotenv import load_dotenv
load_dotenv()

# --- CONFIGURA EL JUEZ (GPT-4o) ---
api_key = os.getenv("OPENAI_API_KEY")
llm_judge = ChatOpenAI(model="gpt-4o", api_key=api_key, temperature=0.0)

# --- DEFINE EL PROMPT DEL JUEZ ---
prompt_juez_template = """
Eres un evaluador experto de sistemas RAG. Tu tarea es asignar un score de 0 a 5 
y proporcionar una descripción basada en qué tan bien la respuesta del chatbot 
se fundamenta en el contexto proporcionado.

INSTRUCCIONES:
1. Compara la [RESPUESTA_CHATBOT] con el [CONTEXTO_RAG].
2. Asigna un score de 0 a 5 basado en qué tan bien la respuesta está fundamentada.
3. Proporciona una breve descripción explicando el score asignado.

**PREGUNTA:**
'''
{pregunta}
'''

**CONTEXTO_RAG:**
'''
{contexto_rag}
'''

**RESPUESTA_CHATBOT:**
'''
{respuesta_chatbot}
'''

**EVALUACIÓN:**
Responde únicamente con un objeto JSON válido con la siguiente estructura:
{{
  "score": float,  // Score entre 0 y 5
  "descripcion": "Explica brevemente el score asignado."
}}
"""

prompt_juez_grounding = ChatPromptTemplate.from_template(prompt_juez_template)
eval_grounding_chain = prompt_juez_grounding | llm_judge | JsonOutputParser()

# --- PROCESA EL EXCEL GENERADO EN BULK_CHAT_TEST ---
archivo_excel = "src/rag_system/excel_test/test2.xlsx"
df = pd.read_excel(archivo_excel)

# Seleccionar solo las primeras 20 filas (excluyendo el encabezado)
df = df.iloc[:20]

resultados_evaluacion = []

for index, fila in df.iterrows():
    pregunta = fila["Preguntas"]
    respuesta_guardada = fila["test7"]

    # Limitar la impresión de la pregunta a los primeros 50 caracteres
    print(f"--- Evaluando fila {index + 1}: {pregunta[:50]}... ---")

    # A. Llama a tu función RAG en tiempo real
    contexto_rag_actual = obtener_contexto_rag(pregunta)

    # B. Llama al Juez
    try:
        evaluation = eval_grounding_chain.invoke({
            "contexto_rag": contexto_rag_actual,
            "respuesta_chatbot": respuesta_guardada,
            "pregunta": pregunta  # Se agrega la pregunta al modelo
        })

        print(f"Resultado: Score {evaluation['score']}, Descripción: {evaluation['descripcion']}")
        resultados_evaluacion.append({
            "Pregunta": pregunta,
            "Respuesta": respuesta_guardada,
            "Score": evaluation['score'],
            "Descripción": evaluation['descripcion']
        })

    except Exception as e:
        print(f"Error al evaluar fila {index + 1}: {e}")
        resultados_evaluacion.append({
            "Pregunta": pregunta,
            "Respuesta": respuesta_guardada,
            "Score": 0,
            "Descripción": f"Error: {str(e)}"
        })

# --- GUARDA LOS RESULTADOS EN UN NUEVO EXCEL ---
df_resultados = pd.DataFrame(resultados_evaluacion)
df_resultados.to_excel("src/rag_system/excel_test/resultados_evaluacion.xlsx", index=False)
print("Evaluación completada y guardada en 'resultados_evaluacion.xlsx'.")