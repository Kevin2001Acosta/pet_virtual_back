from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.base import Base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# En producción, la URL ya incluye parámetros como sslmode; no concatenamos nada extra.
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from src.database.models import user_model, chat_history_model

# No ejecutamos Base.metadata.create_all aquí para evitar conflictos con tablas ya existentes
