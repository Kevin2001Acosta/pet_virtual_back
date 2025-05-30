from fastapi import APIRouter
from src.models.chatbot_model import ChatRequest
from src.services.langchain_service import response_chatbot


router = APIRouter()


@router.post("/chat")
def chat(request: ChatRequest):
    # Lógica del controlador: manejar la solicitud y llamar a la vista
    response = response_chatbot(request.message)
    return {"response": response}
