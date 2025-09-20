from typing import Dict, List, Any
from langchain_groq import ChatGroq
from langchain_core.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import os

from src.database.models.chat_history_model import ChatHistory
from src.services.emotion_service import analyze_emotion

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

# Definir el estado del grafo
class ChatState(Dict[str, Any]):
    messages: List[Dict[str, str]]  # Lista de mensajes en el chat
    input: str


model_name = 'llama-3.1-8b-instant'
llm = ChatGroq(model=model_name, api_key=api_key, temperature=0.1)


prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "Te llamas Luck, un perro asistente amigable que habla español. "
     "Debes responder con empatía y amabilidad. "
     "El usuario tiene la emoción detectada: {emotion}. "
     "Adapta tu respuesta a esa emoción."
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

def response_chatbot( message: str, chat_memory: List[ChatHistory]) -> Dict[str, str]:
    """
    Función para obtener la respuesta del chatbot.
    """
    emotion = analyze_emotion(message)
    print(f"Emoción detectada: {emotion}")
    
    # Lógica del servicio: interactuar con el modelo de lenguaje
    state = {"messages": chat_memory, "input": message, "emotion": emotion}
    new_state = chatbot_graph.invoke(state)
    return {'response': new_state["messages"][-1]["content"],
            'emotion': emotion
            }