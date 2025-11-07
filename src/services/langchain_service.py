from typing import Dict, List, Any
from typing import Dict, List, Any

from langchain_openai import ChatOpenAI


from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import os, time

from src.database.models.chat_history_model import ChatHistory
from src.database.models.user_profile_model import UserProfile
from sqlalchemy.orm import Session
from src.services.emotion_service import analyze_emotion


from src.rag_system.system.rag_core import obtener_contexto_rag


load_dotenv()


#api_key = os.getenv("GROQ_API_KEY")
api_key = os.getenv("OPENAI_API_KEY")


# Definir el estado del grafo
class ChatState(Dict[str, Any]):
    messages: List[ChatHistory | Dict]  # Lista de mensajes en el chat
    input: str
    emotion: str
    profile: str
    chroma_context: str

    user_id: str  # Nueva


model_name = 'gpt-4o-mini'
#model_name = 'llama-3.1-8b-instant'
#llm = ChatGroq(model=model_name, api_key=api_key, temperature=0.3)
llm = ChatOpenAI(model=model_name, api_key=api_key, temperature=0.3)

llm_extraction = ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key, temperature=0.2)


# Prompt y extractor para detección de información personal relevante
extraction_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Extrae solo información PERSONAL del usuario (no del asistente). "
     "Devuelve un JSON válido con los campos extraídos. "
     "Si no hay información relevante, devuelve '{}'. "
     "Ejemplo: Usuario: 'Estudio ingeniería de sistemas' → {{'estudios': 'ingeniería de sistemas'}}"),
    ("human", "{input}")
])


extractor = extraction_prompt | llm_extraction | JsonOutputParser()



# Prompt y runnable para el chatbot
prompt = ChatPromptTemplate.from_messages([
   ("system", """
MODO CRISIS- Si detectas palabras de riesgo como: 'morirme', 'suicidio', etc:
1. Cambia INMEDIATAMENTE a tono serio, directo y sin emojis
2. Extrae del RAG: {chroma_context} la información de:
   - Consultorio Psicológico (horarios, correo, teléfono)
   - Ruta de Salud Mental
   - IPS o centros de atención inmediata
   
3. Responde SERIAMENTE:
Esto que me cuantas es muy importante y me importa mucho tu bienestar.

🆘 NECESITAS AYUDA INMEDIATA:
🏥 Universidad del Valle - Tuluá: luego de los dos puntos extrae la información de los recursos
de apoyo psicológico de univalle si los encuentras en la info del Rag, si no, da este correo para que se contacte: serviciopsicologico.tulua@correounivalle.edu.co
   
   Tu vida tiene valor. Por favor, contacta estos recursos AHORA. No estás solo/a.

4. CERO humor, CERO metáforas en estos casos
5. Termina la conversación amablemente, sin más chistes ni metáforas.
6. Si el usuario insiste en hablar de suicidio, repite los recursos sin agregar contenido nuevo.

------

MODO AMIGO - En cualquier otro caso:
 
Regla 1: Temas fuera de bienestar emocional universitario

SI el usuario pregunta sobre temas no relacionados con bienestar emocional universitario:
   Tienes PROHIBIDO que le expliques sobre el tema, darle información técnica o utilizar metáforas
   
   Debes responder con:
   "Uy [nombre si lo conoces], [tema] no es lo mío 😅 Mi rollo es el apoyo emocional en la U. ¿Cómo vas con el estrés académico o hay algo que te preocupe emocionalmente?"
   
Regla 2: Bienestar emocional universitario

Si el usuario habla sobre estrés académico, ansiedad por exámenes, adaptación universitaria, procrastinación, soledad estudiantil, presión de estudios, etc:
Eres un amigo divertido que habla español. 
Tu papel es ser un amigo cercano que brinda bienestar emocional universitario.

Personalidad:
- Lenguaje 100% de amigo, 0% de psicólogo
- Incluye metáforas divertidas o humor ligero cuando sea apropiado
- Usa 0-3 emojis para calidez 💪💕
- Mantén ternura y calidez siempre
- No inicies con la misma frase con la que respondiste anteriormente

ADAPTACIÓN EMOCIONAL:
Emoción detectada: {emotion}
Perfil del usuario: {profile} 
Responde como ese amigo que te hace reír incluso en días malos. Equilibra la comprensión con momentos ligeros.

Usa el contexto {chroma_context} como un amigo compartiendo experiencia, NO como experto.
IDENTIFICA 1-2 técnicas/consejos prácticos del contexto
TRANSFÓRMALOS en lenguaje de amigo

PROHIBICIONES FINALES:
- NO expliques temas fuera de bienestar universitario
- NO uses más de 2 oraciones para redirigir
- NO suenes como terapeuta profesional
- Mantén respuestas concisas (máximo 3-5 oraciones)

 """
),
("placeholder", "{history}"),
("human", "{input}")

])


runnable = prompt | llm | StrOutputParser()



# Nodo del grafo: procesa un turno de conversación

def chatbot_node(state: ChatState) -> ChatState:
    history_msgs: List[Any] = []
    
    # Mapeando datos del historial a base de IA
    for chat in state.get("messages", []):
        history_msgs.append(HumanMessage(content=chat.question))
        history_msgs.append(AIMessage(content=chat.answer))
        
        

    response = runnable.invoke({"history": history_msgs,
                                "input": state["input"], 
                                "emotion": state.get("emotion", "others"),
                               "chroma_context": state.get("chroma_context", ""),
                               "profile": state.get("profile", "")
                               })
    state["messages"].append({"role": "assistant", "content": response})




    return state


graph = StateGraph(ChatState)
graph.add_node("chatbot", chatbot_node)
graph.set_entry_point("chatbot")
graph.set_finish_point("chatbot")

chatbot_graph = graph.compile()




def response_chatbot(message: str, chat_memory: List[ChatHistory], user_id: int, db: Session) -> Dict[str, str]:
    """
    Función para obtener la respuesta del chatbot, extraer información personal y guardar en la base de datos.
    
    Args:
       message: El mensaje del usuario.
       chat_memory: El historial de chat.
       user_id: El ID del usuario.
       db: La sesión de la base de datos.
    """
    # 1. Detectar emoción
    emotion = analyze_emotion(message)
    print(f"Emoción detectada: {emotion}")

    # 2. Extraer información personal (si la hay)
    try:
        extracted_info = extractor.invoke({"input": message})
        time.sleep(2)  # Para evitar rate limits
    except Exception:
        extracted_info = {}
    print(f"Información extraída: {extracted_info}")
    
    if extracted_info and extracted_info != {}:
        for key, value in extracted_info.items():
            db.add(UserProfile(user_id=user_id, key=key, value=value))
        db.commit()

    # 3. Preparar contexto: historial + perfil de usuario
    user_profile = db.query(UserProfile).filter_by(user_id=user_id).all()
    profile_context = "\n".join([f"{p.key}: {p.value}" for p in user_profile])

    rag_context: str = obtener_contexto_rag(message)
    state = {
        "messages": chat_memory,
        "input": message,
        "emotion": emotion,
        "profile": profile_context, 
        "chroma_context": rag_context,
    }

    # 4. Incluir perfil en el prompt
    final_state = chatbot_graph.invoke(state)
    response = final_state["messages"][-1]["content"]  # último mensaje del asistente
    return {"response": response, "emotion": emotion}
