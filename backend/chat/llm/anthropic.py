"""
Anthropic Claude provider implementation.
"""
from typing import AsyncGenerator, Dict, List, Any, Optional
from anthropic import AsyncAnthropic
from .provider import LLMProvider, LLMMessage, LLMResponseChunk

class AnthropicProvider(LLMProvider):
    """
    Anthropic Claude provider implementation.
    Handles streaming responses and tool calls from Claude API.
    """
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        super().__init__("anthropic")
        
        if not api_key:
            raise ValueError("Anthropic API key is required")
        
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
    
    async def generate_streaming_response(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        max_tokens: int = 16000,
        temperature: float = 0.7
    ) -> AsyncGenerator[LLMResponseChunk, None]:
        """
        Generate a streaming response from Claude.
        
        Yields chunks of the response as they arrive, including tool calls.
        """
        try:
            formatted_messages = self.format_messages(messages)
            print("formatted messages from anthropic", formatted_messages)
            # Prepare request parameters
            request_params = {
                "model": self.model,
                "messages": formatted_messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            
            if system_prompt:
                request_params["system"] = system_prompt
            
           
            async with self.client.messages.stream(**request_params) as stream:
                async for event in stream:
                    # Handle different event types
                    if event.type == "content_block_delta":
                        if hasattr(event.delta, 'type'):
                            if event.delta.type == "text_delta":
                                # Text content - yield as it arrives
                                text = event.delta.text
                                yield LLMResponseChunk(
                                    content=text,
                                    is_complete=False
                                )
                    
                    elif event.type == "message_stop":
                        # End of message - signal completion
                        yield LLMResponseChunk(
                            content="",
                            is_complete=True
                        )
        
        except Exception as error:
            self.handle_error(error)
    
    def format_messages(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """
        Format messages for Anthropic's API.
        
        Anthropic expects messages in the format:
        [{"role": "user" | "assistant", "content": "..."}]
        
        System messages are handled separately via the system parameter.
        """
        formatted = []
        
        for msg in messages:
            # Skip system messages (handled separately)
            if msg.role == "system":
                continue
            
            # Anthropic only accepts 'user' and 'assistant' roles
            if msg.role in ["user", "assistant"]:
                formatted.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        return formatted