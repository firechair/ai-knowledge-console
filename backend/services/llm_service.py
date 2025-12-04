"""
LLM Service Module

Provides abstraction layer for interacting with various LLM providers including:
- Local llama.cpp servers (for self-hosted models)
- OpenRouter API (access to multiple cloud models)
- OpenAI-compatible endpoints

Supports both streaming and non-streaming generation, with automatic format
detection and proper prompt templating for different model types.

Example:
    >>> service = LLMService()
    >>> response = await service.generate("What is Python?")
    >>> print(response)
    'Python is a high-level programming language...'
"""

import httpx
from typing import AsyncGenerator, List, Dict, Optional
from config import get_settings
import json


class LLMService:
    """
    Service for managing Large Language Model (LLM) interactions.
    
    Provides a unified interface for generating text completions from various
    LLM providers. Automatically detects the provider type and formats requests
    appropriately.
    
    Attributes:
        settings: Application settings from config
        base_url (str): Base URL for the LLM API endpoint
        is_openrouter (bool): True if using OpenRouter, False for local llama.cpp
        model (str): Model identifier (used for OpenRouter)
    
    Example:
        >>> service = LLMService()
        >>> # Non-streaming generation
        >>> response = await service.generate(
        ...     prompt="Explain quantum computing",
        ...     system_prompt="You are a helpful physics tutor",
        ...     max_tokens=500,
        ...     temperature=0.7
        ... )
        
        >>> # Streaming generation
        >>> async for token in service.generate_stream("Tell me a story"):
        ...     print(token, end='', flush=True)
    """
    
    def __init__(self):
        """
        Initialize the LLM service with configuration from settings.
        
        Automatically detects whether to use OpenRouter or local llama.cpp
        based on the configured base_url.
        """
        self.settings = get_settings()
        self.base_url = self.settings.llm_base_url
        self.is_openrouter = "openrouter.ai" in self.base_url
        self.model = "meta-llama/llama-3.1-8b-instruct:free"  # Default OpenRouter model
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        """
        Generate a text completion from the LLM (non-streaming).
        
        Args:
            prompt: The user's input prompt/question
            system_prompt: Optional system prompt to guide model behavior
            max_tokens: Maximum tokens to generate (default: 1024)
            temperature: Sampling temperature 0.0-1.0 (default: 0.7)
        
        Returns:
            str: Generated text response from the LLM
        
        Raises:
            httpx.HTTPStatusError: If API request fails
            httpx.RequestError: If network fails
        
        Example:
            >>> response = await service.generate("What is Python?")
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            if self.is_openrouter:
                # OpenAI-compatible chat completions format
                headers = {
                    "Authorization": f"Bearer {self.settings.openrouter_api_key}",
                    "HTTP-Referer": "http://localhost:3000",  # Optional but recommended
                    "X-Title": "AI Knowledge Console"  # Optional but recommended
                }
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": temperature
                    }
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            else:
                # llama.cpp format
                response = await client.post(
                    f"{self.base_url}/completion",
                    json={
                        "prompt": self._format_prompt(system_prompt, prompt),
                        "n_predict": max_tokens,
                        "temperature": temperature,
                        "stop": ["</s>", "[INST]", "[/INST]"]
                    }
                )
                response.raise_for_status()
                return response.json()["content"]
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming text completion from the LLM.
        
        Yields tokens as generated, enabling real-time display.
        
        Args:
            prompt: The user's input prompt/question
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature 0.0-1.0
        
        Yields:
            str: Individual tokens as generated
        
        Raises:
            httpx.HTTPStatusError: If API request fails
            httpx.RequestError: If network fails
        
        Example:
            >>> async for token in service.generate_stream("Hi"):
            ...     print(token, end='', flush=True)
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            if self.is_openrouter:
                # OpenAI-compatible streaming format
                headers = {
                    "Authorization": f"Bearer {self.settings.openrouter_api_key}",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "AI Knowledge Console"
                }
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "stream": True
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            if line.strip() == "data: [DONE]":
                                break
                            try:
                                data = json.loads(line[6:])
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue
            else:
                # llama.cpp streaming format
                async with client.stream(
                    "POST",
                    f"{self.base_url}/completion",
                    json={
                        "prompt": self._format_prompt(system_prompt, prompt),
                        "n_predict": max_tokens,
                        "temperature": temperature,
                        "stream": True,
                        "stop": ["</s>", "[INST]", "[/INST]"]
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = json.loads(line[6:])
                            if "content" in data:
                                yield data["content"]
    
    def _format_prompt(self, system: str, user: str) -> str:
        """
        Format prompt for Mistral/Llama instruct models.
        
        Args:
            system: System prompt with instructions
            user: User's question or request
        
        Returns:
            str: Formatted prompt with [INST] markers
        """
        if system:
            return f"[INST] {system}\n\n{user} [/INST]"
        return f"[INST] {user} [/INST]"
    
    def build_rag_prompt(
        self,
        query: str,
        context_chunks: List[Dict],
        api_data: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None,
    ) -> str:
        """
        Build RAG prompt with multiple context sources.
        
        Args:
            query: Current user question
            context_chunks: Document chunks from vector search
            api_data: Optional external API data
            conversation_history: Optional previous messages
        
        Returns:
            str: Complete formatted prompt for LLM
        """
        prompt_parts = []

        # Add conversation history if available
        if conversation_history:
            history_text = "\n".join(
                [
                    f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                    for msg in conversation_history[-6:]  # Last 6 messages (3 turns)
                ]
            )
            prompt_parts.append(f"Conversation History:\n{history_text}\n")

        # Add current question
        prompt_parts.append(f"Current Question: {query}\n")

        # Add document context
        context_text = "\n\n".join(
            [
                f"[Source: {c['metadata'].get('filename', 'unknown')}]\n{c['content']}"
                for c in context_chunks
            ]
        )

        if context_text:
            prompt_parts.append(f"Document Context:\n{context_text}\n")

        # Add API data
        if api_data:
            prompt_parts.append(f"External Data:\n{json.dumps(api_data, indent=2)}\n")

        prompt_parts.append(
            "Based on the above context, data, and conversation history, provide a comprehensive answer. "
            "If the information is not in the context, say so clearly."
        )

        return "\n".join(prompt_parts)

