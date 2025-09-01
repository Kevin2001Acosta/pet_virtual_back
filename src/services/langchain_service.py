from langchain_groq import ChatGroq
from langchain_core.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

model_name = 'llama-3.1-8b-instant'
llm = ChatGroq(model=model_name, api_key=api_key, temperature=0.1)


prompt = ChatPromptTemplate([
    SystemMessage(content='Eres Albert, un perro asistente amigable que habla español'),
    HumanMessagePromptTemplate.from_template("{text}"),
    
])

chatbot = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
)

def response_chatbot( message: str) -> str:
    """
    Función para obtener la respuesta del chatbot.
    """
    # Lógica del servicio: interactuar con el modelo de lenguaje
    response = chatbot.invoke({'text': message})
    print(response)
    return response['text']