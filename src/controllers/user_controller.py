from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from src.models.enums import TokenType
from src.services.email_service import send_reset_password_email
from src.models.user_schema import ResetPasswordRequest, UserCreate, UserLogin, changePasswordRequest
from src.services.user_service import create_user, authenticate_user, create_token, verify_token, update_user_password
from src.database.db import SessionLocal
from src.database.models.user_model import User
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv
load_dotenv()


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
    


backendUrl = os.getenv("BACKEND_URL")

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
    token = create_token(user.email)
    reset_link = f"{backendUrl}/users/reset-password?token={token}"
    
    await send_reset_password_email(user.email, reset_link)
    
    return {"message": "Se ha enviado un enlace de recuperación a tu correo electrónico"}


templates = Jinja2Templates(directory="src/templates")

@router.get("/reset-password", response_class=HTMLResponse)
async def serve_reset_password_page(request: Request, token: str):
    return templates.TemplateResponse(
        "reset_password.html",
        {"request": request, "token": token}
    )

@router.put("/reset-password")
def reset_password_confirm(request: changePasswordRequest, db: Session = Depends(get_db)):
    """
    Restablece la contraseña del usuario utilizando un token y una nueva contraseña.

    Args:
        request (changePasswordRequest): The request containing the token and new password.
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If the token is invalid or expired.
        HTTPException: If the user associated with the token is not found.

    Returns:
        dict: A message indicating that the password has been reset successfully.
    """
    print(request.token)
    result = verify_token(request.token, TokenType.RESET_PASSWORD)
    success = result.get("success")
    if not success:
        print('Token inválido o expirado')
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    email = result.get("email")
    user = db.query(User).filter_by(email=email).first()
    if not user:
        print('Usuario no encontrado')
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user = update_user_password(db, user, request.new_password)
    
    return {
        "success": True,
        "message": "Contraseña restablecida exitosamente",
        "Name": user.name
        }