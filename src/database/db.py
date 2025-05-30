from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.base import Base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

SQLALCHEMY_DATABASE_URL = (
    DATABASE_URL + "?sslmode=disable&connect_timeout=10"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from src.database.models import user_model

Base.metadata.create_all(bind=engine)
