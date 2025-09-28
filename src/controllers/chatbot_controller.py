from fastapi import APIRouter, Depends, HTTPException
from src.models.chatbot_model import ChatRequest
from src.services.langchain_service import response_chatbot
from src.database.db import SessionLocal
from sqlalchemy.orm import Session
from src.database.models.user_model import User
from src.database.models.chat_history_model import ChatHistory


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Responde a un mensaje del usuario utilizando el servicio de chatbot.
    

    Args:
        request (ChatRequest): The request information to question (message, email).
        db (Session, optional): database. Defaults to Depends(get_db).

    Raises:
        HTTPException: IF the user is not found, raises a 404
        HTTPException:

    Returns:
        _type_: A message with the response from chatbot.
        """
    
    # TODO: La validación del usuario y extracción del historial debería hacerse en services
    # TODO: La validación del usuario debería hacerse con JWT y OAuth2 o algo así
    
    user = db.query(User).filter_by(email=request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    history = (
        db.query(ChatHistory)
        .filter_by(user_id=user.id)
        .order_by(ChatHistory.timestamp.desc())
        .limit(5)
        .all()
    )
    print(history)
    
    
    response_data = response_chatbot(request.message, history, user.id, db)
    
    # Guardar el historial de chat
    chat_entry = ChatHistory(
        user_id=user.id,
        question=request.message,
        answer=response_data['response']
        )
    db.add(chat_entry)
    db.commit()
    db.refresh(chat_entry)
    
    return {"response": response_data['response'],
            "emotion": response_data['emotion'],
            "chat_id": chat_entry.id}

@router.get("/chat/history")
def get_chat_history(email: str, db: Session = Depends(get_db)):
    """
    Obtiene el historial de chat de un usuario por su correo electrónico.
    envía el email como parametro de consulta: '/chat/history?email=usuario@email.com'

    Args:
        email (str): The email of the user whose chat history is to be retrieved.
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If the user is not found.

    Returns:
        dict: A list of chat history entries for the user.
    """
    user = db.query(User).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    history = db.query(ChatHistory).filter_by(user_id=user.id).order_by(ChatHistory.timestamp.asc()).all()
    return [
        {
            "question": chat.question,
            "answer": chat.answer,
            "timestamp": chat.timestamp
        }
        for chat in history
    ]