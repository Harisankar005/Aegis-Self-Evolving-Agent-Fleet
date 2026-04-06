"""
services/memory/__init__.py
============================
Exposes the memory subsystem for the Aegis agent framework.

Importable as:
    from services.memory import SessionService, MemoryBank, MemoryConsolidation
"""

from .session_service      import SessionService, Session
from .memory_bank          import MemoryBank
from .memory_consolidation import MemoryConsolidation

__all__ = [
    "SessionService",
    "Session",
    "MemoryBank",
    "MemoryConsolidation",
]
