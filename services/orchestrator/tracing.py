"""
tracing.py
A lightweight OpenTelemetry-style trace recorder used across the system.
"""

import time
import uuid

class TraceRecorder:
    def __init__(self):
        self.spans = []

    def start(self, name, meta=None):
        span = {
            "id": str(uuid.uuid4()),
            "name": name,
            "meta": meta or {},
            "start": time.time(),
            "events": []
        }
        self.spans.append(span)
        return span

    def end(self, span, result):
        span["end"] = time.time()
        span["duration"] = span["end"] - span["start"]
        span["result"] = result
        span["events"].append({
            "event": "end",
            "time": time.time()
        })

    def export(self):
        """Returns all recorded spans."""
        return self.spans


# Global trace recorder used across the project
TRACE = TraceRecorder()
