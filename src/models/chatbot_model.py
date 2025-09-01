from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    email: str  # Nuevo campo para el email del usuario