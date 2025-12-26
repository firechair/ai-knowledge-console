import httpx
from typing import AsyncGenerator, List, Dict, Optional
from config import get_settings
from services.config_service import get_config_service, ConfigService
import json

class LLMService:
    def __init__(self, config_service: Optional[ConfigService] = None):
        self.config_service = config_service or get_config_service()
        self.env_settings = get_settings()  # Still need for app_base_url
        self._llm_config = self.config_service.get_llm_config()

    @property
    def provider_type(self) -> str:
        """Get the provider type (cloud or local)"""
        if "provider_type" in self._llm_config:
            return self._llm_config["provider_type"]
        provider = self.env_settings.llm_provider or self._llm_config.get("provider", "local")
        if provider in ("openrouter", "openai", "openai-compatible"):
            return "cloud"
        return "local"

    @property
    def cloud_provider(self) -> Optional[str]:
        """Get the cloud provider (openrouter, openai, custom)"""
        # If env indicates local, do not treat as cloud even if user settings say cloud
        if (self.env_settings.llm_provider or "").lower() == "local":
            return None
        if "cloud_provider" in self._llm_config:
            return self._llm_config["cloud_provider"]
        provider = self.env_settings.llm_provider or self._llm_config.get("provider")
        if provider == "openrouter":
            return "openrouter"
        if provider == "openai":
            return "openai"
        if provider == "openai-compatible":
            return "custom"
        return None

    @property
    def provider(self) -> str:
        """Get the current LLM provider (for backward compatibility)"""
        # Map new format to old format for compatibility
        if self.provider_type == "cloud":
            return self.cloud_provider or "openrouter"
        return self._llm_config.get("provider", "local")

    @property
    def is_openrouter(self) -> bool:
        """Check if using OpenRouter provider"""
        if (self.env_settings.llm_provider or "").lower() == "local":
            return False
        if (self.env_settings.llm_provider or "").lower() == "openrouter":
            return True
        return self.provider_type == "cloud" and self.cloud_provider == "openrouter"

    @property
    def is_openai(self) -> bool:
        """Check if using OpenAI provider"""
        return self.provider_type == "cloud" and self.cloud_provider == "openai"

    @property
    def is_openai_compatible(self) -> bool:
        """Check if using OpenAI-compatible provider (openai or custom)"""
        return self.provider_type == "cloud" and self.cloud_provider in ["openai", "custom"]

    @property
    def is_local(self) -> bool:
        """Check if using local provider"""
        if (self.env_settings.llm_provider or "").lower() == "local":
            return True
        return self.provider_type == "local"

    @property
    def base_url(self) -> str:
        """Get the base URL for the provider"""
        # Prefer env-based routing
        if (self.env_settings.llm_provider or "").lower() == "local":
            return self.env_settings.llm_base_url
        if self.is_openrouter:
            return "https://openrouter.ai/api/v1"
        elif self.is_openai:
            return "https://api.openai.com/v1"
        elif self.cloud_provider == "custom":
            return self._llm_config.get("base_url", "")
        else:  # local
            return self._llm_config.get("base_url", self.env_settings.llm_base_url)

    @property
    def model(self) -> str:
        """Get the model name based on provider"""
        if self.is_openrouter:
            return self.env_settings.openrouter_model
        m = self._llm_config.get("model")
        return m or ""
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        # Prefer env-based routing to satisfy backward-compat expectations
        if not self.is_local:
            # Handle cloud providers (OpenRouter, OpenAI, custom OpenAI-compatible)
            async with httpx.AsyncClient(timeout=120.0) as client:
                headers = {
                    "Content-Type": "application/json",
                }

                # Add authorization if API key is available
                api_key = self._llm_config.get("api_key")
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"

                # Add OpenRouter-specific headers
                if self.is_openrouter:
                    headers["HTTP-Referer"] = self.env_settings.app_base_url
                    headers["X-Title"] = "AI Knowledge Console"

                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                payload = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": self._llm_config.get("temperature", temperature),
                    "max_tokens": self._llm_config.get("max_tokens", max_tokens),
                }

                # Add optional parameters for OpenRouter
                if self.is_openrouter:
                    payload.update({
                        "top_p": self._llm_config.get("top_p", 0.9),
                        "frequency_penalty": self._llm_config.get("frequency_penalty", 0.0),
                        "presence_penalty": self._llm_config.get("presence_penalty", 0.0),
                        "repetition_penalty": self._llm_config.get("repetition_penalty", 1.0),
                    })

                try:
                    resp = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )
                except httpx.RequestError as e:
                    return json.dumps({"error": str(e)})

                if resp.status_code != 200:
                    try:
                        err = resp.json()
                        return json.dumps({"error": err})
                    except Exception:
                        return json.dumps({"error": resp.text})

                data = resp.json()
                # Extract content from OpenAI-compatible response
                choices = data.get("choices", [])
                if choices:
                    message = choices[0].get("message", {})
                    return message.get("content", "")
                return ""

        # Handle local provider
        async with httpx.AsyncClient(timeout=120.0) as client:
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
        # Prefer env-based routing to satisfy backward-compat expectations
        if not self.is_local:
            # Handle cloud providers (OpenRouter, OpenAI, custom OpenAI-compatible)
            async with httpx.AsyncClient(timeout=120.0) as client:
                headers = {
                    "Content-Type": "application/json",
                }

                # Add authorization if API key is available
                api_key = self._llm_config.get("api_key")
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"

                # Add OpenRouter-specific headers
                if self.is_openrouter:
                    headers["HTTP-Referer"] = self.env_settings.app_base_url
                    headers["X-Title"] = "AI Knowledge Console"

                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                payload = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": self._llm_config.get("temperature", temperature),
                    "max_tokens": self._llm_config.get("max_tokens", max_tokens),
                    "stream": True,
                }

                # Add optional parameters for OpenRouter
                if self.is_openrouter:
                    payload.update({
                        "top_p": self._llm_config.get("top_p", 0.9),
                        "frequency_penalty": self._llm_config.get("frequency_penalty", 0.0),
                        "presence_penalty": self._llm_config.get("presence_penalty", 0.0),
                        "repetition_penalty": self._llm_config.get("repetition_penalty", 1.0),
                    })

                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        if line.strip() == "data: [DONE]":
                            break
                        try:
                            data = json.loads(line[6:])
                        except json.JSONDecodeError:
                            continue
                        choice = data.get("choices", [{}])[0]
                        delta = choice.get("delta") or {}
                        content = delta.get("content")
                        if content:
                            yield content
                return

        # Handle local provider
        async with httpx.AsyncClient(timeout=120.0) as client:
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
        """Format prompt for Mistral/Llama instruct models"""
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
        """Build a RAG prompt with context, optional API data, and conversation history"""
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
