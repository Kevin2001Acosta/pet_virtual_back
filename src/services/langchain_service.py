from typing import Dict, List, Any
from typing import Dict, List, Any

from langchain_openai import ChatOpenAI


from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import os, time

from src.database.models.chat_history_model import ChatHistory
from src.database.models.user_profile_model import UserProfile
from src.services.prompts import CHATBOT_PROMPT, EXTRACTION_PROMPT
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




extractor = EXTRACTION_PROMPT | llm_extraction | JsonOutputParser()
runnable = CHATBOT_PROMPT | llm | StrOutputParser()



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
                               "profile": state.get("profile", ""),
                               "pet_name": state.get("pet_name", "Amigo")
                               })
    state["messages"].append({"role": "assistant", "content": response})




    return state


graph = StateGraph(ChatState)
graph.add_node("chatbot", chatbot_node)
graph.set_entry_point("chatbot")
graph.set_finish_point("chatbot")

chatbot_graph = graph.compile()




def response_chatbot(message: str, chat_memory: List[ChatHistory], user_id: int, db: Session, pet_name: str = "Amigo") -> Dict[str, str]:
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
        "pet_name": pet_name,
    }

    # 4. Incluir perfil en el prompt
    final_state = chatbot_graph.invoke(state)
    response = final_state["messages"][-1]["content"]  # último mensaje del asistente
    return {"response": response, "emotion": emotion}
