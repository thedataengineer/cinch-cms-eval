"""
LLM Provider Abstraction for CMS Evaluation Framework
Supports Ollama (local), OpenAI (cloud), and Anthropic Claude (cloud) providers
"""

import json
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Unified response from LLM providers."""
    content: Dict[str, Any]
    model: str
    provider: str
    raw_text: str


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for display."""
        pass
    
    @abstractmethod
    def chat(self, prompt: str, schema: Dict[str, Any]) -> LLMResponse:
        """
        Send a chat message and get structured JSON response.
        
        Args:
            prompt: The prompt to send
            schema: JSON schema for structured output
            
        Returns:
            LLMResponse with parsed content
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass


class OllamaProvider(LLMProvider):
    """Ollama local model provider."""
    
    def __init__(
        self, 
        model: str = "llama3.1",
        host: str = "http://localhost:11444"
    ):
        self.model = model
        self.host = host
        self._client = None
    
    @property
    def name(self) -> str:
        return f"Ollama ({self.model})"
    
    def _get_client(self):
        """Lazy initialize Ollama client."""
        if self._client is None:
            try:
                import ollama
                self._client = ollama.Client(host=self.host)
            except ImportError:
                raise ImportError(
                    "Ollama library not installed. Run: pip install ollama"
                )
        return self._client
    
    def is_available(self) -> bool:
        """Check if Ollama server is running and model is available."""
        try:
            client = self._get_client()
            # Try to list models to check connectivity
            models = client.list()
            model_names = [m.get('name', '').split(':')[0] for m in models.get('models', [])]
            return self.model.split(':')[0] in model_names or len(model_names) > 0
        except Exception:
            return False
    
    def chat(self, prompt: str, schema: Dict[str, Any]) -> LLMResponse:
        """Send chat with structured output format."""
        client = self._get_client()
        
        response = client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            format=schema,
            options={
                "temperature": 0.7,
                "num_predict": 2000
            }
        )
        
        raw_text = response['message']['content']
        content = json.loads(raw_text)
        
        return LLMResponse(
            content=content,
            model=self.model,
            provider="ollama",
            raw_text=raw_text
        )


class OpenAIProvider(LLMProvider):
    """OpenAI API provider - works on cloud deployments."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini"
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self._client = None
    
    @property
    def name(self) -> str:
        return f"OpenAI ({self.model})"
    
    def _get_client(self):
        """Lazy initialize OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "OpenAI library not installed. Run: pip install openai"
                )
        return self._client
    
    def is_available(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key)
    
    def chat(self, prompt: str, schema: Dict[str, Any]) -> LLMResponse:
        """Send chat with structured JSON output."""
        client = self._get_client()
        
        # Add JSON instruction to prompt
        json_prompt = f"""{prompt}

Return your response as valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Respond ONLY with valid JSON, no other text."""
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": json_prompt}],
            response_format={"type": "json_object"},
            max_tokens=2000,
            temperature=0.7
        )
        
        raw_text = response.choices[0].message.content
        content = json.loads(raw_text)
        
        return LLMResponse(
            content=content,
            model=self.model,
            provider="openai",
            raw_text=raw_text
        )


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022"
    ):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self._client = None
    
    @property
    def name(self) -> str:
        return f"Claude ({self.model.split('-')[2] if '-' in self.model else self.model})"
    
    def _get_client(self):
        """Lazy initialize Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "Anthropic library not installed. Run: pip install anthropic"
                )
        return self._client
    
    def is_available(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key)
    
    def chat(self, prompt: str, schema: Dict[str, Any]) -> LLMResponse:
        """Send chat with structured output format."""
        client = self._get_client()
        
        # Add JSON instruction to prompt for Claude
        json_prompt = f"""{prompt}

Return your response as valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Respond ONLY with valid JSON, no other text."""
        
        message = client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": json_prompt}]
        )
        
        raw_text = message.content[0].text
        content = json.loads(raw_text)
        
        return LLMResponse(
            content=content,
            model=self.model,
            provider="anthropic",
            raw_text=raw_text
        )


def get_provider(
    provider_type: str = "openai",
    **kwargs
) -> LLMProvider:
    """
    Factory function to get the appropriate LLM provider.
    
    Args:
        provider_type: "ollama", "openai", or "anthropic"
        **kwargs: Provider-specific configuration
        
    Returns:
        Configured LLMProvider instance
    """
    if provider_type.lower() == "ollama":
        return OllamaProvider(
            model=kwargs.get("model", os.environ.get("OLLAMA_MODEL", "llama3.1")),
            host=kwargs.get("host", os.environ.get("OLLAMA_HOST", "http://localhost:11444"))
        )
    elif provider_type.lower() == "openai":
        return OpenAIProvider(
            api_key=kwargs.get("api_key"),
            model=kwargs.get("model", os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))
        )
    elif provider_type.lower() in ("anthropic", "claude"):
        return AnthropicProvider(
            api_key=kwargs.get("api_key"),
            model=kwargs.get("model", "claude-3-5-sonnet-20241022")
        )
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")


def get_available_providers() -> Dict[str, bool]:
    """Check which providers are available."""
    return {
        "ollama": OllamaProvider().is_available(),
        "openai": OpenAIProvider().is_available(),
        "anthropic": AnthropicProvider().is_available()
    }

