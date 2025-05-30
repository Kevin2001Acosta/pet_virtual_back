from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.models.user_schema import UserCreate, UserLogin
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
    db_user = db.query(User).filter_by(email=user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    user_obj = create_user(db, user.name, user.email, user.password)
    return {"message": "Usuario registrado exitosamente", "user_id": user_obj.id}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    user_obj = authenticate_user(db, user.email, user.password)
    if not user_obj:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {"message": "Login exitoso",
            "pass": True,
            "user_id": user_obj.id}