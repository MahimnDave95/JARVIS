"""
Database manager for JARVIS operations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from contextlib import contextmanager
from loguru import logger

from jarvis.database.models import (
    SessionLocal, CommandHistory, UserPreference, 
    ConversationContext, init_db
)

@contextmanager
def get_db():
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()

class DatabaseManager:
    """High-level database operations for JARVIS."""
    
    def __init__(self):
        init_db()
        logger.info("Database initialized")
    
    def log_command(
        self,
        source: str,
        raw_text: str,
        action_type: Optional[str] = None,
        success: bool = False,
        error_message: Optional[str] = None,
        response_text: Optional[str] = None
    ) -> int:
        """Log a command to history."""
        with get_db() as db:
            entry = CommandHistory(
                source=source,
                raw_text=raw_text,
                action_type=action_type,
                success=success,
                error_message=error_message,
                response_text=response_text
            )
            db.add(entry)
            db.flush()
            command_id = entry.id
            logger.debug(f"Logged command {command_id}: {action_type}")
            return command_id
    
    def get_recent_commands(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent command history."""
        with get_db() as db:
            commands = db.query(CommandHistory).order_by(
                CommandHistory.timestamp.desc()
            ).limit(limit).all()
            
            return [
                {
                    "id": c.id,
                    "timestamp": c.timestamp.isoformat(),
                    "source": c.source,
                    "raw_text": c.raw_text,
                    "action_type": c.action_type,
                    "success": c.success
                }
                for c in commands
            ]
    
    def get_command_stats(self) -> Dict[str, Any]:
        """Get command statistics."""
        with get_db() as db:
            total = db.query(CommandHistory).count()
            successful = db.query(CommandHistory).filter(
                CommandHistory.success == True
            ).count()
            
            # Last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent = db.query(CommandHistory).filter(
                CommandHistory.timestamp >= yesterday
            ).count()
            
            return {
                "total_commands": total,
                "successful_commands": successful,
                "failed_commands": total - successful,
                "last_24h_commands": recent
            }
    
    def set_preference(self, key: str, value: str):
        """Set a user preference."""
        with get_db() as db:
            pref = db.query(UserPreference).filter(
                UserPreference.key == key
            ).first()
            
            if pref:
                pref.value = value
            else:
                pref = UserPreference(key=key, value=value)
                db.add(pref)
            
            logger.info(f"Set preference: {key} = {value}")
    
    def get_preference(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a user preference."""
        with get_db() as db:
            pref = db.query(UserPreference).filter(
                UserPreference.key == key
            ).first()
            return pref.value if pref else default
    
    def add_conversation_message(self, role: str, content: str, session_id: str = 'default'):
        """Add a message to conversation context."""
        with get_db() as db:
            msg = ConversationContext(
                role=role,
                content=content,
                session_id=session_id
            )
            db.add(msg)
            
            # Keep only last 20 messages per session
            old_msgs = db.query(ConversationContext).filter(
                ConversationContext.session_id == session_id
            ).order_by(ConversationContext.timestamp.desc()).offset(20).all()
            
            for old in old_msgs:
                db.delete(old)
    
    def get_conversation_history(self, session_id: str = 'default', limit: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation history."""
        with get_db() as db:
            msgs = db.query(ConversationContext).filter(
                ConversationContext.session_id == session_id
            ).order_by(ConversationContext.timestamp.desc()).limit(limit).all()
            
            return [
                {"role": m.role, "content": m.content}
                for m in reversed(msgs)
            ]
    
    def clear_conversation_history(self, session_id: str = 'default'):
        """Clear conversation history for a session."""
        with get_db() as db:
            db.query(ConversationContext).filter(
                ConversationContext.session_id == session_id
            ).delete()
            logger.info(f"Cleared conversation history for session {session_id}")

# Global instance
db_manager = DatabaseManager()