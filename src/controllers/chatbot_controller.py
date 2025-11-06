from fastapi import APIRouter, Depends, HTTPException, Header
from src.models.enums import TokenType
from src.services.user_service import verify_token
from src.models.chatbot_model import ChatRequest
from src.services.langchain_service import response_chatbot
from src.database.db import SessionLocal
from sqlalchemy.orm import Session
from src.database.models.user_model import User
from src.database.models.chat_history_model import ChatHistory
from src.services.emotion_service import calculate_emotional_status
from fastapi.security import APIKeyHeader


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

api_key_header = APIKeyHeader(name="Authorization")

@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db), Authorization: str = Depends(api_key_header)):
    """
    Responde a un mensaje del usuario utilizando el servicio de chatbot.
    

    Args:
        request (ChatRequest): The request information to question (message, token).
        db (Session, optional): database. Defaults to Depends(get_db).

    Raises:
        HTTPException: IF the user is not found, raises a 404
        HTTPException:

    Returns:
        _type_: A message with the response from chatbot.
        """
    
    # TODO: La validación del usuario y extracción del historial debería hacerse en services

    if not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autorización no proporcionado o formato de token inválido")

    token: str = Authorization.split(" ")[1]

    # Verificar el token y extraer el email
    result = verify_token(token, TokenType.ACCESS)
    
    if not result.get("success"):
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    email = result.get("email")

    user = db.query(User).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    history = (
        db.query(ChatHistory)
        .filter_by(user_id=user.id)
        .order_by(ChatHistory.timestamp.desc())
        .limit(5)
        .all()
    )
    
    
    response_data = response_chatbot(request.message, history, user.id, db)
    
    # Guardar el historial de chat
    chat_entry = ChatHistory(
        user_id=user.id,
        question=request.message,
        answer=response_data['response'],
        emotion=response_data['emotion']
        )
    db.add(chat_entry)
    db.commit()
    db.refresh(chat_entry)
    
    return {"response": response_data['response'],
            "emotion": response_data['emotion'],
            "chat_id": chat_entry.id}

@router.get("/chat/history")
def get_chat_history(db: Session = Depends(get_db), Authorization: str = Depends(api_key_header)):
    """
    Obtiene el historial de chat de un usuario y el nombre de la mascota por su correo electrónico.
    recibe el email en el token de autorización.

    Args:
        token (str): The authorization token.
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If the user is not found.

    Returns:
        dict: A list of chat history entries for the user.
    """
    
    if not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autorización no proporcionado o formato de token inválido")

    token: str = Authorization.split(" ")[1]

    # Verificar el token y extraer el email
    result = verify_token(token, TokenType.ACCESS)

    if not result.get("success"):
        raise HTTPException(status_code=401, detail=result.get("message"))
    
    email = result.get("email")

    user = db.query(User).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    history = db.query(ChatHistory).filter_by(user_id=user.id).order_by(ChatHistory.timestamp.asc()).all()
    return {"history": [
        {
            "question": chat.question,
            "answer": chat.answer,
            "timestamp": chat.timestamp
        }
        for chat in history
    ], "pet_name": user.petName}


@router.get("/chat/emotion-status")
def get_emotion_status(db: Session = Depends(get_db), Authorization: str = Depends(api_key_header)):
    """
    Obtiene el estado emocional del usuario basado en su historial de chat.
    ROJO: Alerta
    AMARILLO: Precaución
    VERDE: Estable

    Args:
        token (str): The authorization token.
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Returns:
        String: The emotional status of the user.
    """
    if not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autorización no proporcionado o formato de token inválido")

    token: str = Authorization.split(" ")[1]

    # Verificar el token y extraer el email
    result = verify_token(token, TokenType.ACCESS)

    if not result.get("success"):
        raise HTTPException(status_code=401, detail=result.get("message"))

    email = result.get("email")

    user = db.query(User).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Obtener el historial de chat del usuario
    history = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == user.id, ChatHistory.emotion.isnot(None))
        .order_by(ChatHistory.timestamp.desc())
        .limit(10)
        .all()
    )
    
    # Calcular el estado emocional basado en el historial
    emotional_status = calculate_emotional_status(history)

    return emotional_status