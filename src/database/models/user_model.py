from sqlalchemy import Column, Integer, String
from src.database.base import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    petName = Column(String, nullable=False)
    
    chat_history = relationship("ChatHistory", back_populates="user")
    profile = relationship("UserProfile", back_populates="user")