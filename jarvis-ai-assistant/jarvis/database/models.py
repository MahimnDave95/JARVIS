"""
SQLAlchemy models for JARVIS database.
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from jarvis.config.settings import DATABASE_URL

Base = declarative_base()

class CommandHistory(Base):
    """Store history of all commands processed by JARVIS."""
    
    __tablename__ = "command_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    source = Column(String(50), nullable=False)  # 'voice', 'phone', 'api'
    raw_text = Column(Text, nullable=False)
    action_type = Column(String(100))  # 'app_launch', 'browser', 'system', etc.
    success = Column(Boolean, default=False)
    error_message = Column(Text)
    response_text = Column(Text)  # What JARVIS said in response
    
    def __repr__(self):
        return f"<CommandHistory(id={self.id}, source='{self.source}', action='{self.action_type}')>"

class UserPreference(Base):
    """Simple key-value store for user preferences."""
    
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserPreference(key='{self.key}')>"

class ConversationContext(Base):
    """Store recent conversation context for AI continuity."""
    
    __tablename__ = "conversation_context"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    session_id = Column(String(100), default='default')
    
    def __repr__(self):
        return f"<ConversationContext(role='{self.role}', session='{self.session_id}')>"

# Create engine and session factory
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)