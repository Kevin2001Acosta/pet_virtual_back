from fastapi import APIRouter
from src.controllers.chatbot_controller import router as chatbot_router

router = APIRouter()
router.include_router(chatbot_router, prefix="/chatbot", tags=["chatbot"])