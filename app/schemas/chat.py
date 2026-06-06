from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    session_id: Optional[str] = None
    tool_used: Optional[str] = None
    tool_input: Optional[str] = None
    tool_output: Optional[str] = None
    tool_error: Optional[str] = None


class ChatLogResponse(BaseModel):
    id: int
    session_id: Optional[str] = None

    user_message: str
    ai_answer: str

    tool_used: Optional[str] = None
    tool_input: Optional[str] = None
    tool_output: Optional[str] = None
    tool_error: Optional[str] = None

    created_at: datetime

    class Config:
        from_attributes = True


class SessionSummaryResponse(BaseModel):
    session_id: str
    last_user_message: str
    last_ai_answer: str
    message_count: int
    last_activity: datetime


class SessionMessageResponse(BaseModel):
    role: str
    content: str
    created_at: datetime

    tool_used: Optional[str] = None
    tool_input: Optional[str] = None
    tool_output: Optional[str] = None
    tool_error: Optional[str] = None


class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: list[SessionMessageResponse]