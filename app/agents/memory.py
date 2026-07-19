from sqlalchemy.orm import Session

from app.database.db import SessionLocal
from app.models.conversation import ConversationMessage


def add_to_memory(session_id: str, role: str, content: str):
    db: Session = SessionLocal()

    try:
        message = ConversationMessage(
            session_id=session_id,
            role=role,
            content=content,
        )

        db.add(message)
        db.commit()

    finally:
        db.close()


def get_memory(session_id: str) -> str:
    db: Session = SessionLocal()

    try:
        messages = (
            db.query(ConversationMessage)
            .filter(ConversationMessage.session_id == session_id)
            .order_by(ConversationMessage.created_at.asc())
            .all()
        )

        # Keep only the latest 10 messages
        messages = messages[-10:]

        history = []

        for message in messages:
            history.append(
                f"{message.role.upper()}: {message.content}"
            )

        return "\n".join(history)

    finally:
        db.close()


def clear_memory(session_id: str):
    db: Session = SessionLocal()

    try:
        (
            db.query(ConversationMessage)
            .filter(ConversationMessage.session_id == session_id)
            .delete()
        )

        db.commit()

    finally:
        db.close()