from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.base import Base

class UserProfile(Base):
    __tablename__ = "user_profile"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key = Column(String, nullable=False)   # Ej: "cumpleaños", "hobby", "profesión"
    value = Column(String, nullable=False) # Ej: "15 de septiembre", "jugar fútbol"
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="profile")
