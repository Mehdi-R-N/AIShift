from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from database import Base
from sqlalchemy.sql import func
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    first_name = Column(String(100))
    last_name = Column(String(100))
    company_name = Column(String(255))

class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # Changed String to Integer
    content = Column(String(5000))  # For instance, assuming chat content might be long
    sender = Column(String(1000))
    timestamp = Column(DateTime(timezone=True), default=func.now())   
    