"""
Google Gemini provider implementation.
"""
from typing import AsyncGenerator, Dict, List, Any, Optional
import google.generativeai as genai
from .provider import LLMProvider, LLMMessage, LLMResponseChunk


class GeminiProvider(LLMProvider):
    """
    Google Gemini provider implementation.
    Handles streaming responses from Gemini API.
    """
    
    def __init__(self, api_key: str, model: str = "gemini-3.0-flash"):
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model
    
    async def generate_streaming_response(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        max_tokens: int = 16000,
        temperature: float = 0.7
    ) -> AsyncGenerator[LLMResponseChunk, None]:
        """
        Generate a streaming response from Gemini.
        
        Yields chunks of the response as they arrive.
        """
        try:
            # Format messages for Gemini
            formatted_messages = self.format_messages(messages)
            
            # Gemini uses a chat-based API
            # We need to create a chat session with history
            chat = self.model.start_chat(history=formatted_messages[:-1] if len(formatted_messages) > 1 else [])
            
            # Get the last message (user's current message)
            current_message = formatted_messages[-1]["parts"][0] if formatted_messages else ""
            
            # Configure generation settings
            generation_config = genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
            
            # Add system instruction if provided
            if system_prompt:
                # For Gemini, system instructions are set on the model
                # We need to recreate the model with system instruction
                self.model = genai.GenerativeModel(
                    self.model_name,
                    system_instruction=system_prompt
                )
                chat = self.model.start_chat(history=formatted_messages[:-1] if len(formatted_messages) > 1 else [])
            
            # Stream the response
            response = await chat.send_message_async(
                current_message,
                generation_config=generation_config,
                stream=True
            )
            
            async for chunk in response:
                if chunk.text:
                    yield LLMResponseChunk(
                        content=chunk.text,
                        is_complete=False
                    )
            
            # Signal completion
            yield LLMResponseChunk(
                content="",
                is_complete=True
            )
        
        except Exception as error:
            self.handle_error(error)
            raise
    
    def format_messages(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """
        Format messages for Gemini's API.
        
        Gemini expects messages in the format:
        [{"role": "user" | "model", "parts": ["..."]}]
        
        System messages are handled separately via system_instruction parameter.
        """
        formatted = []
        
        for msg in messages:
            # Skip system messages (handled via system_instruction)
            if msg.role == "system":
                continue
            
            # Map roles: 'assistant' -> 'model', 'user' -> 'user'
            role = "model" if msg.role == "assistant" else "user"
            
            formatted.append({
                "role": role,
                "parts": [msg.content]
            })
        
        return formatted
