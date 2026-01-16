from typing import Optional
from .base import LLMProvider
from .openai_provider import OpenAIProvider
from .local_provider import LocalProvider
from .zai_provider import ZaiProvider
import os

def get_llm_provider(provider_type: str, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None) -> LLMProvider:
    """
    Factory to return the correct LLM provider.
    """
    if provider_type == "openai":
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OpenAI API Key is missing")
        return OpenAIProvider(api_key=key, model=model or "gpt-4o")
        
    elif provider_type == "custom_openai":
        # For remote/custom models (e.g. LMStudio)
        # API key might be dummy for some local servers, but we pass it if provided
        key = api_key or "lm-studio" 
        return OpenAIProvider(api_key=key, model=model or "local-model", base_url=base_url)
    
    elif provider_type == "local":
        return LocalProvider(model=model or "llama3")
        
    elif provider_type == "zai":
        # Allowing optional key for mock, but prefer env var
        key = api_key or os.getenv("ZAI_API_KEY") or "mock-key"
        return ZaiProvider(api_key=key, model=model or "glm-4.7")
    
    # Defaults to local if unknown or mocked
    return LocalProvider(model="mock")
