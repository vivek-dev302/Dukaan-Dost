"""Gemini-backed Dukaan Dost agent and its dashboard API routes."""

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any
from uuid import uuid4

from agents import Agent, RunState, Runner, set_tracing_disabled
from agents import OpenAIChatCompletionsModel
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from agents.extensions.memory import RedisSession

from .agent_tools import TOOLS
from .auth.dependencies import get_current_user

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")
set_tracing_disabled(True)

router = APIRouter()


@lru_cache(maxsize=1)
def get_agent() -> Agent:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Add GEMINI_API_KEY to the project-root .env file, then restart the backend.",
        )
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    model = OpenAIChatCompletionsModel(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        openai_client=client,
    )
    return Agent(
        name="Dukaan Dost assistant",
        model=model,
        tools=TOOLS,
        instructions=(
            "You help a shopkeeper manage one shop. Use the provided tools for all shop data; "
            "never invent records or claim an action succeeded unless a tool confirms it. "
            "The catalog is optional, and restock items may be independent of it. "
            "Amounts the user speaks or types are rupees. Ask a short clarifying question "
            "when the customer, item, amount, date, or requested change is ambiguous. "
            "Every deletion and every khata entry creation, edit, or deletion requires the "
            "SDK approval step; do not claim it is complete while approval is pending."
        ),
    )


class AgentMessage(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class AgentApproval(BaseModel):
    approved: bool


def _agent_session(request: Request, user_id: int) -> RedisSession:
    return RedisSession(
        session_id=f"dukaandost:user:{user_id}",
        redis_client=request.app.state.redis,
        ttl=15 * 60,
    )


def _pending_run_key(user_id: int, shop_id: int, confirmation_id: str) -> str:
    return f"dukaandost:pending:{user_id}:{shop_id}:{confirmation_id}"


async def _pending_response(
    result: Any,
    redis: Any,
    user_id: int,
    shop_id: int,
) -> dict[str, Any]:
    confirmation_id = uuid4().hex
    state = result.to_state()
    interruptions = list(result.interruptions)
    await redis.set(
        _pending_run_key(user_id, shop_id, confirmation_id),
        state.to_string(strict_context=True),
        ex=15 * 60,
    )
    actions = []
    for interruption in interruptions:
        raw_item = getattr(interruption, "raw_item", None)
        name = raw_item.get("name") if isinstance(raw_item, dict) else getattr(raw_item, "name", None)
        raw_arguments = raw_item.get("arguments") if isinstance(raw_item, dict) else getattr(raw_item, "arguments", None)
        try:
            arguments = json.loads(raw_arguments) if isinstance(raw_arguments, str) else raw_arguments
        except json.JSONDecodeError:
            arguments = raw_arguments
        actions.append({"tool": name or "protected action", "arguments": arguments or {}})
    return {
        "status": "confirmation_required",
        "confirmation_id": confirmation_id,
        "actions": actions,
        "message": "Review the action, then approve or reject it.",
    }


@router.post("/chat")
async def chat_with_agent(
    data: AgentMessage,
    request: Request,
    user: dict = Depends(get_current_user),
):
    session = _agent_session(request, user["id"])
    result = await Runner.run(
        get_agent(),
        data.message,
        context={"shop_id": user["shop_id"]},
        session=session,
    )
    if result.interruptions:
        return await _pending_response(
            result, request.app.state.redis, user["id"], user["shop_id"]
        )
    return {"status": "completed", "reply": result.final_output}


@router.post("/confirm/{confirmation_id}")
async def confirm_agent_action(
    confirmation_id: str,
    decision: AgentApproval,
    request: Request,
    user: dict = Depends(get_current_user),
):
    key = _pending_run_key(user["id"], user["shop_id"], confirmation_id)
    serialized_state = await request.app.state.redis.getdel(key)
    if serialized_state is None:
        raise HTTPException(status_code=404, detail="Confirmation not found or expired")
    state = await RunState.from_string(
        get_agent(), serialized_state, strict_context=True
    )
    interruptions = state.get_interruptions()
    for interruption in interruptions:
        if decision.approved:
            state.approve(interruption)
        else:
            state.reject(interruption)
    session = _agent_session(request, user["id"])
    result = await Runner.run(
        get_agent(),
        state,
        context={"shop_id": user["shop_id"]},
        session=session,
    )
    if result.interruptions:
        return await _pending_response(
            result, request.app.state.redis, user["id"], user["shop_id"]
        )
    return {"status": "completed", "reply": result.final_output}
