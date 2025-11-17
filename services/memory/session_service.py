import uuid
import time

class Session:
    """
    Represents an active agent session.
    Stores trace logs, short-term memory, and agent interaction events.
    """

    def __init__(self, session_id=None):
        self.id = session_id or str(uuid.uuid4())
        self.created_at = time.time()
        self.updated_at = time.time()
        
        # Short-term memory (only for this session)
        self.state = {}

        # Full trace for observability
        self.trace = []

    def update_state(self, key, value):
        self.state[key] = value
        self.updated_at = time.time()

    def append_event(self, agent_name, output):
        self.updated_at = time.time()
        event = {
            "timestamp": time.time(),
            "agent": agent_name,
            "output": output
        }
        self.trace.append(event)


class SessionService:
    """
    Manages multiple agent sessions.
    Supports pause/resume for long-running tasks.
    """

    def __init__(self):
        # In production this could be Redis or Firestore.
        self.sessions = {}

    def get_or_create(self, session_id=None):
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]

        session = Session(session_id)
        self.sessions[session.id] = session
        return session

    def save(self, session):
        self.sessions[session.id] = session

    def pause(self, session_id):
        """Mock pause operation."""
        if session_id in self.sessions:
            self.sessions[session_id].update_state("paused", True)

    def resume(self, session_id):
        if session_id in self.sessions:
            self.sessions[session_id].update_state("paused", False)
