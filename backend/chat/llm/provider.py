from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, AsyncGenerator

@dataclass
class LLMMessage:
    """Represents a message in the LLM conversation history."""
    role: str      # 'user', 'assistant', 'system'
    content: str

@dataclass
class LLMResponseChunk:
    """Represents a chunk of a streaming LLM response."""
    content: str
    is_complete: bool = False
    tool_calls: Optional[List[Dict]] = None

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate_streaming_response(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str],
        tools: Optional[List[Dict]],
        max_tokens: int,
        temperature: float
    ) -> AsyncGenerator[LLMResponseChunk, None]:
        """
        Generates a streaming response from the LLM.

        Args:
            messages: List of LLMMessage objects representing conversation history.
            system_prompt: Optional system prompt to guide the LLM.
            tools: Optional list of tool definitions for the LLM to use.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature for the LLM.

        Yields:
            LLMResponseChunk objects as the response streams.
        """
        pass

    @abstractmethod
    def format_messages(self, messages: List[LLMMessage]) -> List[Dict]:
        """
        Formats a list of LLMMessage objects into the provider-specific format.

        Args:
            messages: List of LLMMessage objects.

        Returns:
            List of dictionaries in the LLM provider's message format.
        """
        pass

    def handle_error(self, error: Exception) -> None:
        """
        Handles errors that occur during LLM interaction.
        Can be overridden by concrete providers for specific error handling.

        Args:
            error: The exception that occurred.
        """
        print(f"LLM Provider Error: {error}")
