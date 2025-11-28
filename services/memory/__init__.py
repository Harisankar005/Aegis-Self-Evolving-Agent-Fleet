"""
services.memory
===============

This module initializes the memory subsystem for the Aegis Agent Framework.
It exposes the primary memory components used across the system:

- SessionService: Manages per-session conversational state
- MemoryBank: Long-term memory store for persistent knowledge
- MemoryConsolidation: Logic for summarizing, extracting, and compacting memory

These are imported here to provide a clean and simple interface, allowing
other modules to do:

    from services.memory import SessionService, MemoryBank

instead of importing each file individually.

This helps maintain a stable public API for the memory package while keeping
the internal structure modular.
"""

from .session_service import SessionService
from .memory_bank import MemoryBank
from .memory_consolidation import MemoryConsolidation

__all__ = [
    "SessionService",
    "MemoryBank",
    "MemoryConsolidation",
]
