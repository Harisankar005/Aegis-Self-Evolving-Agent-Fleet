import uuid
from typing import Dict, Any, List


class Session:
    """
    A session object that stores events and traces generated during
    multi-agent execution. Each session has a unique ID.
    """

    def __init__(self, session_id: str = None):
        self.id = session_id or str(uuid.uuid4())
        self.events: List[Dict[str, Any]] = []
        self.trace: List[Dict[str, Any]] = []

    def append_event(self, agent_name: str, result: Dict[str, Any]) -> None:
        """
        Store an event in the session. An event records which agent executed
        and the result it produced.
        """
        event = {
            "agent": agent_name,
            "result": result
        }
        self.events.append(event)

        # Minimal trace entry for evaluation and debugging.
        trace_entry = {
            "name": agent_name,
            "output_summary": result.get("output", result)
        }
        self.trace.append(trace_entry)


class SessionService:
    """
    Manages all active sessions. Provides creation, retrieval, and
    storage for session state.
    """

    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    def get_or_create(self, session_id: str = None) -> Session:
        """
        Retrieve an existing session or create a new one if none exists.
        """
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]

        session = Session(session_id)
        self.sessions[session.id] = session
        return session

    def get(self, session_id: str) -> Session:
        """
        Retrieve an existing session by ID. Raises KeyError if not found.
        """
        if session_id not in self.sessions:
            raise KeyError(f"Session '{session_id}' not found.")
        return self.sessions[session_id]

    def list_sessions(self) -> List[str]:
        """
        Return a list of all active session IDs.
        """
        return list(self.sessions.keys())

    def clear(self) -> None:
        """
        Remove all stored sessions. Useful for testing.
        """
        self.sessions.clear()
