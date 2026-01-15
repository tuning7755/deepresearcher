"""FastAPI app providing SSE-driven research sessions."""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from deepresearcher.agent import create_research_agent


WEB_ROOT = Path(__file__).resolve().parent.parent / "web"
STATIC_ROOT = WEB_ROOT / "static"
INDEX_HTML = WEB_ROOT / "index.html"

DEFAULT_OUTPUT_ROOT = Path.cwd() / "research_outputs"


@dataclass
class SessionState:
    thread_id: str
    working_dir: Path
    model: str | None
    queue: asyncio.Queue[dict[str, Any]] = field(default_factory=asyncio.Queue)
    status: str = "idle"
    report_text: str | None = None
    report_path: str | None = None


class SessionCreate(BaseModel):
    model: str | None = None


class MessageCreate(BaseModel):
    content: str


app = FastAPI(title="Deep Research Agent")

app.mount("/static", StaticFiles(directory=STATIC_ROOT), name="static")

_sessions: dict[str, SessionState] = {}


def _format_sse(event: str, data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


def _iter_messages(node_output: dict | None) -> list[Any]:
    if not node_output:
        return []
    messages = node_output.get("messages")
    if messages is None:
        return []
    if isinstance(messages, (list, tuple)):
        return list(messages)
    value = getattr(messages, "value", None)
    if value is not None:
        return list(value) if isinstance(value, (list, tuple)) else [value]
    return [messages]


def _summarize_tool_call(call: Any) -> dict[str, Any]:
    if isinstance(call, dict):
        name = call.get("name") or call.get("tool") or "unknown_tool"
        args = call.get("args") or call.get("arguments") or {}
        call_id = call.get("id")
    else:
        name = getattr(call, "name", None) or getattr(call, "tool", None) or "unknown_tool"
        args = getattr(call, "args", None) or getattr(call, "arguments", None) or {}
        call_id = getattr(call, "id", None)
    return {"id": call_id, "name": name, "args": args}


def _list_files(root: Path) -> set[Path]:
    if not root.exists():
        return set()
    return {path for path in root.rglob("*") if path.is_file()}


def _read_text_file(path: Path, max_bytes: int = 200_000) -> str | None:
    try:
        if path.stat().st_size > max_bytes:
            return None
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


async def _event_stream(session: SessionState) -> AsyncIterator[str]:
    while True:
        try:
            payload = await asyncio.wait_for(session.queue.get(), timeout=15.0)
        except asyncio.TimeoutError:
            yield _format_sse("ping", {"timestamp": time.time()})
            continue
        if payload is None:
            break
        yield _format_sse(payload["event"], payload["data"])


async def _enqueue(session: SessionState, event: str, data: dict[str, Any]) -> None:
    await session.queue.put({"event": event, "data": data})


def _enqueue_from_thread(session: SessionState, event: str, data: dict[str, Any], loop: asyncio.AbstractEventLoop) -> None:
    asyncio.run_coroutine_threadsafe(_enqueue(session, event, data), loop)


def _run_agent_sync(session: SessionState, prompt: str, loop: asyncio.AbstractEventLoop) -> None:
    agent, _ = create_research_agent(
        model=session.model,
        working_dir=session.working_dir,
        auto_approve=True,
    )
    config = {"configurable": {"thread_id": session.thread_id}}

    for event in agent.stream(
        {"messages": [HumanMessage(content=prompt)]},
        config=config,
        stream_mode="updates",
    ):
        for node_name, node_output in event.items():
            if node_name == "__interrupt__":
                continue
            for msg in _iter_messages(node_output):
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for call in msg.tool_calls:
                        summary = _summarize_tool_call(call)
                        _enqueue_from_thread(
                            session,
                            "tool_call",
                            {
                                "message": f"Tool call: {summary['name']}",
                                "node": node_name,
                                "tool_call_id": summary["id"],
                                "tool": summary["name"],
                                "args": summary["args"],
                            },
                            loop,
                        )
                    continue
                if getattr(msg, "type", None) == "tool" or msg.__class__.__name__ == "ToolMessage":
                    tool_call_id = getattr(msg, "tool_call_id", None)
                    tool_name = getattr(msg, "name", None) or getattr(msg, "tool", None) or "tool"
                    _enqueue_from_thread(
                        session,
                        "tool_result",
                        {
                            "message": f"Tool result: {tool_name}",
                            "node": node_name,
                            "tool_call_id": tool_call_id,
                            "tool": tool_name,
                            "content": getattr(msg, "content", None),
                        },
                        loop,
                    )
                    continue
                content = getattr(msg, "content", None)
                if content:
                    _enqueue_from_thread(
                        session,
                        "chat",
                        {"message": content, "node": node_name},
                        loop,
                    )


async def _run_research(session: SessionState, prompt: str) -> None:
    session.status = "running"
    await _enqueue(session, "status", {"state": "running"})

    session.working_dir.mkdir(parents=True, exist_ok=True)
    files_before = _list_files(session.working_dir)

    loop = asyncio.get_running_loop()
    await asyncio.to_thread(_run_agent_sync, session, prompt, loop)

    files_after = _list_files(session.working_dir)
    new_files = sorted(files_after - files_before, key=lambda path: str(path))
    for path in new_files:
        content = _read_text_file(path)
        payload = {
            "path": str(path),
            "name": path.name,
            "content": content,
        }
        await _enqueue(session, "file", payload)

        if path.name == "research_report.md" and content:
            session.report_text = content
            session.report_path = str(path)
            await _enqueue(session, "report", {"content": content, "path": str(path)})
        if path.name == "research_report.pdf":
            session.report_path = str(path)
            await _enqueue(session, "report", {"content": None, "path": str(path)})

    session.status = "complete"
    await _enqueue(session, "status", {"state": "complete"})


@app.get("/")
def index() -> FileResponse:
    return FileResponse(INDEX_HTML)


@app.post("/api/sessions")
def create_session(payload: SessionCreate) -> JSONResponse:
    thread_id = str(uuid.uuid4())
    output_root = DEFAULT_OUTPUT_ROOT / f"session_{thread_id}"
    state = SessionState(thread_id=thread_id, working_dir=output_root, model=payload.model)
    _sessions[thread_id] = state
    return JSONResponse({"thread_id": thread_id})


@app.post("/api/sessions/{thread_id}/messages")
async def post_message(thread_id: str, payload: MessageCreate) -> JSONResponse:
    session = _sessions.get(thread_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status == "running":
        raise HTTPException(status_code=409, detail="Session is already running")
    session.status = "queued"
    asyncio.create_task(_run_research(session, payload.content))
    return JSONResponse({"status": "queued"})


@app.get("/api/sessions/{thread_id}/stream")
def stream_events(thread_id: str) -> StreamingResponse:
    session = _sessions.get(thread_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return StreamingResponse(_event_stream(session), media_type="text/event-stream")


@app.get("/api/sessions/{thread_id}/report")
def get_report(thread_id: str) -> JSONResponse:
    session = _sessions.get(thread_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return JSONResponse(
        {
            "content": session.report_text,
            "path": session.report_path,
            "status": session.status,
        }
    )
