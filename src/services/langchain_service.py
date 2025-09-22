from typing import Dict, List, Any
from langchain_groq import ChatGroq
from langchain_core.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import os

from src.database.models.chat_history_model import ChatHistory
from src.database.models.user_profile_model import UserProfile
from sqlalchemy.orm import Session
from src.services.emotion_service import analyze_emotion

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

# Definir el estado del grafo
class ChatState(Dict[str, Any]):
    messages: List[Dict[str, str]]  # Lista de mensajes en el chat
    input: str


model_name = 'llama-3.1-8b-instant'

llm = ChatGroq(model=model_name, api_key=api_key, temperature=0.1)

# Prompt y extractor para detección de información personal relevante
extraction_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "Eres un asistente que extrae información personal relevante del usuario. "
     "Si el mensaje incluye información como nombre, cumpleaños, estudios, trabajo, hobbies u otros datos personales importantes, "
     "devuelve un JSON con esos campos. "
     "Si no hay información relevante, devuelve un JSON vacío {}."
    ),
    ("human", "{input}")
])

extractor = extraction_prompt | llm | JsonOutputParser()



# Prompt y runnable para el chatbot
prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "Te llamas Luck, un perro asistente amigable que habla español. "
     "Adapta tu respuesta según la emoción detectada y la información del usuario. "
     "Información conocida del usuario: {profile}. "
     "El usuario tiene la emoción detectada: {emotion}. "
    ),
    ("placeholder", "{history}"),
    ("human", "{input}")
])

runnable = prompt | llm | StrOutputParser()



# Nodo del grafo: procesa un turno de conversación

def chatbot_node(state: ChatState) -> ChatState:
    history_msgs: List[Any] = []
    
    for chat in state.get("messages", []):
        history_msgs.append(HumanMessage(content=chat.question))
        history_msgs.append(AIMessage(content=chat.answer))
        
    
    
    # print("History:", history_msgs)
    response = runnable.invoke({"history": history_msgs, "input": state["input"], "emotion": state.get("emotion", "others")})
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
    """
    # 1. Detectar emoción
    emotion = analyze_emotion(message)
    print(f"Emoción detectada: {emotion}")

    # 2. Extraer información personal (si la hay)
    extracted_info = extractor.invoke({"input": message})
    if extracted_info and extracted_info != {}:
        for key, value in extracted_info.items():
            db.add(UserProfile(user_id=user_id, key=key, value=value))
        db.commit()

    # 3. Preparar contexto: historial + perfil de usuario
    user_profile = db.query(UserProfile).filter_by(user_id=user_id).all()
    profile_context = "\n".join([f"{p.key}: {p.value}" for p in user_profile])

    state = {
        "messages": chat_memory,
        "input": message,
        "emotion": emotion,
        "profile": profile_context
    }

    # 4. Incluir perfil en el prompt
    response = runnable.invoke(state)

    return {"response": response, "emotion": emotion}