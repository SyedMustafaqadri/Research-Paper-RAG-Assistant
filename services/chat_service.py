import json
import uuid
import datetime
from core.logger import logger
from database.connection import get_db
from database.models import Chat, Message, RetrievalLog, User

class ChatService:
    @staticmethod
    def get_or_create_chat(chat_id: str = None, title: str = "New Chat") -> str:
        """
        Creates a new chat session or returns the existing chat_id.
        """
        with get_db() as db:
            # Get default user
            user = db.query(User).filter_by(email="default@example.com").first()
            if not user:
                user = User(id=str(uuid.uuid4()), email="default@example.com", name="Default User")
                db.add(user)
                db.commit()
                db.refresh(user)
                
            if chat_id:
                existing_chat = db.query(Chat).filter_by(id=chat_id).first()
                if existing_chat:
                    return existing_chat.id
            
            # Create new chat
            new_id = chat_id or str(uuid.uuid4())
            new_chat = Chat(
                id=new_id,
                user_id=user.id,
                title=title
            )
            db.add(new_chat)
            db.commit()
            logger.info(f"Created chat session: {new_id} - '{title}'")
            return new_id

    @staticmethod
    def save_message(chat_id: str, role: str, content: str) -> str:
        """
        Saves a message in the chat history.
        """
        with get_db() as db:
            message = Message(
                id=str(uuid.uuid4()),
                chat_id=chat_id,
                role=role,
                content=content
            )
            db.add(message)
            db.commit()
            return message.id

    @staticmethod
    def get_chat_history(chat_id: str, limit: int = 20):
        """
        Returns a list of message dicts for a chat session.
        """
        with get_db() as db:
            messages = db.query(Message).filter_by(chat_id=chat_id).order_by(Message.created_at.asc()).limit(limit).all()
            return [{"role": msg.role, "content": msg.content} for msg in messages]

    @staticmethod
    def log_retrieval(question: str, retrieved_chunks: list, response_time: float) -> str:
        """
        Logs a retrieval operation to the retrieval_logs database.
        """
        try:
            # Serialize chunks metadata
            chunks_meta = []
            for doc in retrieved_chunks:
                chunks_meta.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
            
            serialized_chunks = json.dumps(chunks_meta)
            
            with get_db() as db:
                log_entry = RetrievalLog(
                    id=str(uuid.uuid4()),
                    question=question,
                    retrieved_chunks=serialized_chunks,
                    response_time=response_time
                )
                db.add(log_entry)
                db.commit()
                logger.info(f"Retrieval log entry saved: {log_entry.id}")
                return log_entry.id
        except Exception as e:
            logger.error(f"Failed to log retrieval to database: {e}")
            return ""
