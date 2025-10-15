from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.models.enums import TokenType
from src.database.models.user_model import User
import jwt
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv


load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, name: str, email: str, password: str):
    hashed_password = get_password_hash(password)
    user = User(name=name, email=email, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if user and verify_password(password, user.password):
        return user
    return None


SECRET_KEY = os.getenv("SECRET_KEY")

def create_token(email: str, expires_minutes: int = 15, type: TokenType = TokenType.RESET_PASSWORD) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"sub": email, "exp": expire, "type": type.value}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token: str, type: TokenType) -> dict: 
    """
    Verifica el token recibido y su tipo. Devuelve dict indicando éxito,
    motivo y data relevante (por ejemplo: email en 'sub').
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != type.value:  
            print('Tipo de token inválido')
            return {"success": False, "message": "Tipo de token inválido", "data": None}
        return {"success": True, "message": "Token válido", "email": payload.get("sub")}  
    except jwt.ExpiredSignatureError:
        print('El token ha expirado')
        return {"success": False, "message": "El token ha expirado", "data": None}
    except jwt.InvalidTokenError:
        print('Token inválido')
        return {"success": False, "message": "Token inválido", "data": None}

def update_user_password(db: Session, user: User, new_password: str) -> User:
    """Recibe el usuario y la nueva contraseña, la hashea y actualiza el registro en BD.

    Args:
        db (Session): _database session_
        user (User): _user instance_
        new_password (str): _new password_

    Returns:
        _type_: _user instance with updated password_
    """
    user.password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user