"""Database operations for the agent activity log."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import AgentLog


def insert_agent_log(session: Session, user_id: int, action: str, description: str) -> None:
    session.add(
        AgentLog(user_id=user_id, action=action, description=description)
    )


def get_agent_logs(
    user_id: int,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    with SessionLocal() as session:
        rows = session.execute(
            select(AgentLog.id, AgentLog.action, AgentLog.description, AgentLog.created_at)
            .where(AgentLog.user_id == user_id)
            .order_by(AgentLog.created_at.desc(), AgentLog.id.desc())
            .limit(limit)
            .offset(offset)
        ).mappings().all()
    return [dict(row) for row in rows]
