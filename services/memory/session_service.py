"""
SessionService
--------------
A lightweight, production-style session manager for the Aegis agent system.

Purpose:
- Maintain per-session conversation history (events)
- Store working memory/state during a mission
- Enable pause/resume (long-running ops)
- Support trace integration (trace span IDs)
- Provide safe, serializable containers

This approach is inspired by:
- ADK Sessions (append-only event model)
- LangGraph State (mutable computation graph)
- Context Engineering best practices
"""

import uuid
import time
from typing import Any, Dict, List, Optional


class SessionEvent:
    """
    Represents a single event in a session:
    - agent calls
    - tool calls
    - LLM outputs
    - errors
    - state mutations
    """

    def __init__(
        self,
        role: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ):
        self.id = str(uuid.uuid4())
        self.role = role            # "agent", "tool", "system", "user"
        self.content = content      # JSON-serializable dict or string
        self.ts = time.time()
        self.metadata = metadata or {}
        self.trace_id = trace_id    # Link to trace span, if exists

    def to_dict(self):
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.ts,
            "metadata": self.metadata,
            "trace_id": self.trace_id,
        }


class Session:
    """
    A session contains:
    - events: chronological conversation history
    - state: working memory (scratchpad)
    - id: stable identifier
    """

    def __init__(self, session_id: Optional[str] = None):
        self.id = session_id or str(uuid.uuid4())
        self.events: List[SessionEvent] = []
        self.state: Dict[str, Any] = {}  # working scratchpad memory
        self.created_at = time.time()
        self.updated_at = self.created_at

    # --------------- Event Handling --------------- #

    def append_event(
        self, role: str, content: Any, metadata: Optional[Dict[str, Any]] = None, trace_id: Optional[str] = None
    ):
        event = SessionEvent(role=role, content=content, metadata=metadata, trace_id=trace_id)
        self.events.append(event)
        self.updated_at = time.time()
        return event

    # --------------- State Handling --------------- #

    def get_state(self, key: str, default=None):
        return self.state.get(key, default)

    def set_state(self, key: str, value: Any):
        self.state[key] = value
        self.updated_at = time.time()

    def update_state(self, updates: Dict[str, Any]):
        self.state.update(updates)
        self.updated_at = time.time()

    # --------------- Export Helpers --------------- #

    def to_dict(self):
        return {
            "session_id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "state": self.state,
            "events": [e.to_dict() for e in self.events],
        }


class SessionService:
    """
    Lightweight session manager.

    Responsibilities:
    - Create sessions
    - Retrieve sessions
    - Pause/resume long-running operations
    - Store session-level memory (scratchpad)
    - Append events with trace integration

    In production, this could be backed by:
    - Redis
    - Firestore
    - DynamoDB
    - Cloud SQL
    - Agent Engine Sessions

    This mock version keeps everything in-memory for simplicity.
    """

    def __init__(self):
        # In real deployments → external DB
        self.sessions: Dict[str, Session] = {}

    # --------------- Session Management --------------- #

    def create_session(self) -> Session:
        session = Session()
        self.sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        return self.sessions.get(session_id)

    def get_or_create(self, session_id: Optional[str] = None) -> Session:
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        return self.create_session()

    # --------------- Event Logging --------------- #

    def add_event(
        self,
        session_id: str,
        role: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ) -> SessionEvent:
        session = self.get_or_create(session_id)
        return session.append_event(role, content, metadata, trace_id)

    # --------------- State Helpers --------------- #

    def update_state(self, session_id: str, updates: Dict[str, Any]):
        session = self.get_or_create(session_id)
        session.update_state(updates)

    def get_state(self, session_id: str) -> Dict[str, Any]:
        session = self.get_or_create(session_id)
        return session.state

    # --------------- Pause / Resume --------------- #

    def pause_session(self, session_id: str):
        """Mark session as paused; good for long-running ops."""
        session = self.get_or_create(session_id)
        session.set_state("paused", True)
        return True

    def resume_session(self, session_id: str):
        """Resume a paused session."""
        session = self.get_or_create(session_id)
        session.set_state("paused", False)
        return True

    # --------------- Export / Debug Helpers --------------- #

    def export_session(self, session_id: str) -> Dict[str, Any]:
        session = self.get_or_create(session_id)
        return session.to_dict()

    def list_sessions(self) -> List[str]:
        return list(self.sessions.keys())
