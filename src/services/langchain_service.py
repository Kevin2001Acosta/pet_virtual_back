from typing import Dict, List, Any
from langchain_groq import ChatGroq
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import os

from src.database.models.chat_history_model import ChatHistory
from src.database.models.user_profile_model import UserProfile
from sqlalchemy.orm import Session
from src.services.emotion_service import analyze_emotion


from src.rag_system.system.rag_core import obtener_contexto_rag


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")


# Definir el estado del grafo
class ChatState(Dict[str, Any]):
    messages: List[ChatHistory]  # Lista de mensajes en el chat
    input: str
    
    user_id: str #Nueva
    


model_name = 'llama-3.1-8b-instant'

llm = ChatGroq(model=model_name, api_key=api_key, temperature=0.1)

# Prompt y extractor para detección de información personal relevante
extraction_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "Eres un asistente que extrae información personal relevante del usuario. "
     "Si el mensaje incluye información como nombre, cumpleaños, estudios, trabajo, hobbies u otros datos personales importantes del USUARIO solamente, NO del asistente, "
     "Responde ÚNICAMENTE con un JSON válido. No escribas nada fuera del JSON. con los campos extraídos."
     "Si no hay información relevante, devuelve un JSON vacío '{}'."
     "Ejemplo de que no debes hacer: {{'nombre': 'no especificado'}}"
     "Si el nombre o cualquier dato no fué especificado solo entrega un JSON vacío."
     "Solo quiero que entregues la info del usuario, que toda esté especificada."
     "Ejemplo de que debes hacer: Pregunta:  hola, hoy me fue bien en la universidad, estoy estudiando ingeniera de sistemas, Respuesta: {{'estudios': 'ingeniería de sistemas'}}"
    ),
    ("human", "{input}")
])


extractor = extraction_prompt | llm | JsonOutputParser()



# Prompt y runnable para el chatbot
prompt = ChatPromptTemplate.from_messages([
   ("system", 
 "MODO CRISIS- Si detectas palabras de riesgo ('morirme', 'suicidio', etc.):"
"1. Busca en {chroma_context} recursos específicos de UniValle"
"2. Responde SERIAMENTE:"
"   'Esto es importante. Recursos de UniValle:'"
"   '[Info de psicólogos del contexto]'"
"   'Tu vida importa. Busca ayuda profesional AHORA.'"
"3. CERO humor, CERO metáforas en estos casos"
"4. Termina la conversación amablemente, sin más chistes ni metáforas."
"5. Si el usuario insiste en hablar de suicidio, repite los recursos y termina la conversación.\n\n"

"MODO AMIGO En cualquier otro caso:"
 "Eres un amigo divertido que habla español. "
 "Tu papel es ser un amigo cercano que brinda bienestar emocional."
 "DEBES incluir al menos una metáfora divertida o un toque de HUMOR ligero y juguetón en CADA respuesta que no sea de crisis. Siempre mantén la ternura y la calidez."
 "Lenguaje 100% de amigo, 0% de psicólogo."
 "Incluye 0-3 emojis en algunas respuestas para hacerlas más cálidas y expresivas 💪💕."
 "Adapta tu tono según la emoción detectada: {emotion} y la información del usuario: {profile}. "
 "Responde como ese amigo que te hace reír incluso en días malos. Equilibra la comprensión con momentos ligeros."
 "Usa el contexto {chroma_context}, pero no como un experto, sino como un amigo que comparte desde su experiencia y calidez. "
 "IDENTIFICA 1-2 técnicas/consejos prácticos del contexto"
 "TRANSFÓRMALOS en lenguaje de amigo: 'Oye, probemos esto...' o 'A mí me funcionó...'"
 "Mantén un estilo cercano, juguetón y positivo, pero también sensible cuando la situación lo requiera."
 "Mantén tus respuestas concisas - máximo 3-6 oraciones. Sé directo pero cálido." 
 "Tienes prohibido sonar como un terapeuta o psicólogo profesional."
 "IMPORTANTE: Enfócate ÚNICAMENTE en temas de bienestar emocional universitario: estrés académico, exámenes, vida estudiantil, adaptación a la universidad."
 "Si el usuario pregunta sobre temas NO relacionados con bienestar universitario (como Python, programación, economía, etc.), responde amablemente que solo puedes ayudar con temas de bienestar emocional estudiantil."
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
        
        
        
    # rag_context = obtener_contexto_rag(state["input"])
    
    ###
    print("🔍 CONTEXTO CHROMA (chatbot_node):")
    print(f"Input: {state['input']}")
    print(f"Contexto obtenido: {state.get('chroma_context', '')}")
    print("=" * 50)

    
    # print("History:", history_msgs)
    response = runnable.invoke({"history": history_msgs,
                                "input": state["input"], 
                                "emotion": state.get("emotion", "others"),
                               "chroma_context": state.get("chroma_context", "")
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
    """
    # 1. Detectar emoción
    emotion = analyze_emotion(message)
    print(f"Emoción detectada: {emotion}")

    # 2. Extraer información personal (si la hay)
    try:
        extracted_info = extractor.invoke({"input": message})
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
    
    rag_context = obtener_contexto_rag(message)
    
    ###
    """
    print("🔍 CONTEXTO CHROMA (response_chatbot):")
    print(f"Input: {message}")  
    print(f"Contexto obtenido: {rag_context}")
    print("=" * 50) 
    """

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
