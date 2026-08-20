from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database.db import SessionLocal
from app.models.conversation import ConversationMessage

MAX_MEMORY_MESSAGES = 10


def add_to_memory(session_id: str, role: str, content: str) -> None:
    """Persist one message for an isolated chat session."""
    db: Session = SessionLocal()

    try:
        db.add(
            ConversationMessage(
                session_id=session_id,
                role=role,
                content=content,
            )
        )
        db.commit()
    finally:
        db.close()


def get_memory(session_id: str) -> str:
    """Return only the latest messages belonging to this session."""
    db: Session = SessionLocal()

    try:
        statement = (
            select(ConversationMessage)
            .where(ConversationMessage.session_id == session_id)
            .order_by(ConversationMessage.created_at.desc())
            .limit(MAX_MEMORY_MESSAGES)
        )
        messages = list(db.scalars(statement).all())
        messages.reverse()

        return "\n".join(
            f"{message.role.upper()}: {message.content}"
            for message in messages
        )
    finally:
        db.close()


def clear_memory(session_id: str) -> None:
    """Delete conversation history for exactly one chat session."""
    db: Session = SessionLocal()

    try:
        db.execute(
            delete(ConversationMessage).where(
                ConversationMessage.session_id == session_id
            )
        )
        db.commit()
    finally:
        db.close()
