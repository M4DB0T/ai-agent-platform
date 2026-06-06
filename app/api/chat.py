import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.agents.agent import run_agent
from app.db.database import get_db
from app.db.models import ChatLog
from app.schemas.chat import (
    ChatLogResponse,
    ChatRequest,
    ChatResponse,
    SessionHistoryResponse,
    SessionSummaryResponse,
)


router = APIRouter()


def build_chat_history(db: Session, session_id: str, limit: int = 10) -> list[dict]:
    """
    Loads previous chat logs for the same session_id
    and converts them into OpenAI message format.
    """

    logs = (
        db.query(ChatLog)
        .filter(ChatLog.session_id == session_id)
        .order_by(ChatLog.created_at.desc())
        .limit(limit)
        .all()
    )

    logs = list(reversed(logs))

    chat_history = []

    for log in logs:
        chat_history.append(
            {
                "role": "user",
                "content": log.user_message,
            }
        )

        chat_history.append(
            {
                "role": "assistant",
                "content": log.ai_answer,
            }
        )

    return chat_history


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    session_id = request.session_id or str(uuid.uuid4())

    chat_history = build_chat_history(
        db=db,
        session_id=session_id,
        limit=10,
    )

    agent_result = run_agent(
        user_message=request.message,
        chat_history=chat_history,
    )

    chat_log = ChatLog(
        session_id=session_id,
        user_message=request.message,
        ai_answer=agent_result["answer"],
        tool_used=agent_result["tool_used"],
        tool_input=agent_result["tool_input"],
        tool_output=agent_result["tool_output"],
        tool_error=agent_result["tool_error"],
    )

    db.add(chat_log)
    db.commit()
    db.refresh(chat_log)

    return ChatResponse(
        answer=agent_result["answer"],
        session_id=session_id,
        tool_used=agent_result["tool_used"],
        tool_input=agent_result["tool_input"],
        tool_output=agent_result["tool_output"],
        tool_error=agent_result["tool_error"],
    )


@router.get("/logs", response_model=list[ChatLogResponse])
def get_chat_logs(db: Session = Depends(get_db)):
    logs = db.query(ChatLog).order_by(ChatLog.created_at.desc()).all()

    return logs


@router.get("/sessions", response_model=list[SessionSummaryResponse])
def get_sessions(db: Session = Depends(get_db)):
    subquery = (
        db.query(
            ChatLog.session_id,
            func.max(ChatLog.created_at).label("last_activity"),
            func.count(ChatLog.id).label("message_count"),
        )
        .filter(ChatLog.session_id.isnot(None))
        .group_by(ChatLog.session_id)
        .subquery()
    )

    sessions = (
        db.query(ChatLog, subquery.c.message_count)
        .join(
            subquery,
            (ChatLog.session_id == subquery.c.session_id)
            & (ChatLog.created_at == subquery.c.last_activity),
        )
        .order_by(subquery.c.last_activity.desc())
        .all()
    )

    return [
        {
            "session_id": chat_log.session_id,
            "last_user_message": chat_log.user_message,
            "last_ai_answer": chat_log.ai_answer,
            "message_count": message_count,
            "last_activity": chat_log.created_at,
        }
        for chat_log, message_count in sessions
    ]
@router.get("/sessions/{session_id}", response_model=SessionHistoryResponse)
def get_session_history(session_id: str, db: Session = Depends(get_db)):
    logs = (
        db.query(ChatLog)
        .filter(ChatLog.session_id == session_id)
        .order_by(ChatLog.created_at.asc())
        .all()
    )

    messages = []

    for log in logs:
        messages.append(
            {
                "role": "user",
                "content": log.user_message,
                "created_at": log.created_at,
            }
        )

        messages.append(
            {
                "role": "assistant",
                "content": log.ai_answer,
                "created_at": log.created_at,
                "tool_used": log.tool_used,
                "tool_input": log.tool_input,
                "tool_output": log.tool_output,
                "tool_error": log.tool_error,
            }
        )

    return {
        "session_id": session_id,
        "messages": messages,
    }