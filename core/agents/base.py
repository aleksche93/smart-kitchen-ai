from abc import ABC, abstractmethod
from typing import AsyncGenerator

class BaseChefAgent(ABC):
    """
    Abstract base class for all Chef sub-agents.
    Agents act as asynchronous generators.
    """
    @abstractmethod
    async def generate_stream(self, context: dict) -> AsyncGenerator[dict, None]:
        """
        Asynchronously yields events.
        Expected format:
        {'type': 'status', 'data': {'text': '...'}}
        {'type': 'delta', 'data': {'text': '...'}}
        {'type': 'final', 'data': {'payload': { ... }}}
        """
        pass
