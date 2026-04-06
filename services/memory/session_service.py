"""
session_service.py
------------------
A lightweight, production-style session manager for the Aegis agent system.

Purpose:
- Maintain per-session conversation history (events)
- Expose a structured trace list for the Judge / Evaluator
- Store working memory/state during a mission
- Enable pause/resume for long-running operations
- Provide safe, serializable containers

FIX LOG (v2):
- Added Session.trace property (list of trace-span dicts) — the orchestrator and
  Judge both call session.trace; previously undefined → AttributeError.
- Added Session.trace_event(name, data) — orchestrator calls this extensively; was
  missing entirely in v1.
- append_event() now stores plain dicts instead of SessionEvent objects so that
  callers can iterate session.events without unpacking objects. The SessionEvent
  class is kept for type safety when explicitly constructed.
- get_or_create() now accepts an optional session_id positional arg so callers
  don't need keyword syntax (orchestrator calls get_or_create(session_id)).
"""

import uuid
import time
from typing import Any, Dict, List, Optional


class SessionEvent:
    """
    Represents a single event in a session:
    - agent calls, tool calls, LLM outputs, errors, state mutations.
    """

    def __init__(
        self,
        role: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ):
        self.id       = str(uuid.uuid4())
        self.role     = role        # "agent" | "tool" | "system" | "user"
        self.content  = content     # JSON-serializable dict or string
        self.ts       = time.time()
        self.metadata = metadata or {}
        self.trace_id = trace_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id":        self.id,
            "role":      self.role,
            "content":   self.content,
            "timestamp": self.ts,
            "metadata":  self.metadata,
            "trace_id":  self.trace_id,
        }


class Session:
    """
    A session contains:
    - events : chronological conversation/agent history (list of dicts)
    - _trace  : lightweight trace spans emitted by the orchestrator
    - state   : working memory scratchpad
    - id      : stable identifier
    """

    def __init__(self, session_id: Optional[str] = None):
        self.id         = session_id or str(uuid.uuid4())
        self.events:    List[Dict[str, Any]] = []
        self._trace:    List[Dict[str, Any]] = []
        self.state:     Dict[str, Any]       = {}
        self.created_at = time.time()
        self.updated_at = self.created_at

    # ------------------------------------------------------------------ #
    # Trace API — used by the Orchestrator and Judge
    # ------------------------------------------------------------------ #

    def trace_event(self, name: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Emit a named trace span and append it to the internal trace list.

        Parameters
        ----------
        name : str
            Human-readable label for this trace point.
        data : dict, optional
            Arbitrary payload attached to the span.

        Returns
        -------
        dict — the trace span (useful for testing/debugging).
        """
        span: Dict[str, Any] = {
            "id":        str(uuid.uuid4()),
            "name":      name,
            "timestamp": time.time(),
            "data":      data or {},
        }
        self._trace.append(span)
        self.updated_at = time.time()
        return span

    @property
    def trace(self) -> List[Dict[str, Any]]:
        """
        Return the full list of trace spans for this session.

        The Judge iterates over this list looking for agent names in span["name"].
        """
        return self._trace

    # ------------------------------------------------------------------ #
    # Event (conversation history) API
    # ------------------------------------------------------------------ #

    def append_event(
        self,
        role: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Append a conversation/agent event and return it as a dict."""
        event = {
            "id":        str(uuid.uuid4()),
            "role":      role,
            "content":   content,
            "timestamp": time.time(),
            "metadata":  metadata or {},
            "trace_id":  trace_id,
        }
        self.events.append(event)
        self.updated_at = time.time()
        return event

    # ------------------------------------------------------------------ #
    # State (scratchpad) API
    # ------------------------------------------------------------------ #

    def get_state(self, key: str, default=None):
        return self.state.get(key, default)

    def set_state(self, key: str, value: Any):
        self.state[key] = value
        self.updated_at = time.time()

    def update_state(self, updates: Dict[str, Any]):
        self.state.update(updates)
        self.updated_at = time.time()

    # ------------------------------------------------------------------ #
    # Export
    # ------------------------------------------------------------------ #

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "state":      self.state,
            "events":     self.events,
            "trace":      self._trace,
        }


class SessionService:
    """
    Lightweight in-memory session manager.

    In production, back this with Redis / Firestore / DynamoDB.
    """

    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    # ------------------------------------------------------------------ #
    # Session lifecycle
    # ------------------------------------------------------------------ #

    def create_session(self) -> Session:
        session = Session()
        self.sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        return self.sessions.get(session_id)

    def get_or_create(self, session_id: Optional[str] = None) -> Session:
        """
        Return an existing session or create a fresh one.

        Parameters
        ----------
        session_id : str or None
            If provided and known, the existing session is returned.
        """
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        session = Session(session_id)
        self.sessions[session.id] = session
        return session

    # ------------------------------------------------------------------ #
    # Event helpers
    # ------------------------------------------------------------------ #

    def add_event(
        self,
        session_id: str,
        role: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        session = self.get_or_create(session_id)
        return session.append_event(role, content, metadata, trace_id)

    # ------------------------------------------------------------------ #
    # State helpers
    # ------------------------------------------------------------------ #

    def update_state(self, session_id: str, updates: Dict[str, Any]):
        session = self.get_or_create(session_id)
        session.update_state(updates)

    def get_state(self, session_id: str) -> Dict[str, Any]:
        return self.get_or_create(session_id).state

    # ------------------------------------------------------------------ #
    # Pause / resume
    # ------------------------------------------------------------------ #

    def pause_session(self, session_id: str):
        self.get_or_create(session_id).set_state("paused", True)

    def resume_session(self, session_id: str):
        self.get_or_create(session_id).set_state("paused", False)

    # ------------------------------------------------------------------ #
    # Export / debug
    # ------------------------------------------------------------------ #

    def export_session(self, session_id: str) -> Dict[str, Any]:
        return self.get_or_create(session_id).to_dict()

    def list_sessions(self) -> List[str]:
        return list(self.sessions.keys())
