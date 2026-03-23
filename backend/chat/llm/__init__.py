"""
LLM provider package.
Provides factory function for creating LLM provider instances.
"""
from typing import Optional
from django.conf import settings
from .provider import LLMProvider, LLMMessage, LLMResponseChunk
from .anthropic import AnthropicProvider
from .gemini import GeminiProvider


def create_provider(provider_name: Optional[str] = None) -> LLMProvider:
    """
    Create an LLM provider instance based on the provider name.
    
    Args:
        provider_name: Name of the provider ('anthropic' or 'gemini').
                      If None, uses settings.LLM_PROVIDER.
    
    Returns:
        LLMProvider instance
        
    Raises:
        ValueError: If provider name is invalid or required API key is missing
    """
    provider = provider_name or settings.LLM_PROVIDER
    
    if provider == 'gemini':
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured in settings")
        
        return GeminiProvider(
            api_key=settings.GEMINI_API_KEY,
            model=settings.GEMINI_MODEL
        )
    
    elif provider == 'anthropic':
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not configured in settings")
        
        return AnthropicProvider(
            api_key=settings.ANTHROPIC_API_KEY,
            model="claude-sonnet-4-20250514"
        )
    
    else:
        raise ValueError(
            f"Unknown provider: {provider}. "
            f"Supported providers: 'anthropic', 'gemini'"
        )


__all__ = [
    'LLMProvider',
    'LLMMessage', 
    'LLMResponseChunk',
    'AnthropicProvider',
    'GeminiProvider',
    'create_provider',
]
