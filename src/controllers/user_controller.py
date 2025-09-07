from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.services.email_service import send_reset_password_email
from src.models.user_schema import ResetPasswordRequest, UserCreate, UserLogin
from src.services.user_service import create_user, authenticate_user
from src.database.db import SessionLocal
from src.database.models.user_model import User


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un usuario nuevo, con nombre, correo y contraseña.
    

    Args:
        user (UserCreate): The user information to register (name, email, password).
        db (Session, optional): database. Defaults to Depends(get_db).

    Raises:
        HTTPException: If the email is already registered.
        HTTPException: If the registration is successful.

    Returns:
        _type_: A message indicating successful registration and the user ID.
    """
    db_user = db.query(User).filter_by(email=user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    user_obj = create_user(db, user.name, user.email, user.password)
    return {"message": "Usuario registrado exitosamente", "user_id": user_obj.id}



@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Logeo de con correo y contraseña.

    Args:
        user (UserLogin): The login credentials (email and password).
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If credentials are incorrect.

    Returns:
        dict: A message indicating login success and the user ID.
    """
    user_obj = authenticate_user(db, user.email, user.password)
    if not user_obj:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {"message": "Login exitoso",
            "pass": True,
            "user_id": user_obj.id}
    



@router.post("/forgot-password")
async def forgot_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Envía un correo electrónico para restablecer la contraseña del usuario.

    Args:
        request (ResetPasswordRequest): The request containing the user's email.
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If the user with the provided email is not found.

    Returns:
        dict: A message indicating that the reset email has been sent.
    """
    user = db.query(User).filter_by(email=request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    reset_link = f"http://example.com/reset-password?email={user.email}&token=dummy-token"
    
    await send_reset_password_email(user.email, reset_link)
    
    return {"message": "Se ha enviado un enlace de recuperación a tu correo electrónico"}