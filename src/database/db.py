from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.base import Base

SQLALCHEMY_DATABASE_URL = (
    "postgresql://postgres:Acos306254@127.0.0.1:5432/chatbot"
    "?sslmode=disable&connect_timeout=10"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from src.database.models import user_model

Base.metadata.create_all(bind=engine)
