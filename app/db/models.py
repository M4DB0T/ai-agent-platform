from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.database import Base


class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=True, index=True)

    user_message = Column(Text, nullable=False)
    ai_answer = Column(Text, nullable=False)

    tool_used = Column(String, nullable=True)
    tool_input = Column(Text, nullable=True)
    tool_output = Column(Text, nullable=True)
    tool_error = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)