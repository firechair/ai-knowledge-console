import httpx
from typing import AsyncGenerator, List, Dict, Optional
from config import get_settings
import json

class LLMService:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.llm_base_url
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        if self.settings.llm_provider == "openrouter":
            async with httpx.AsyncClient(timeout=120.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": self.settings.app_base_url,
                    "X-Title": "AI Knowledge Console",
                }
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                payload = {
                    "model": self.settings.openrouter_model,
                    "messages": messages,
                    "temperature": self.settings.openrouter_temperature if self.settings.openrouter_temperature else temperature,
                    "top_p": self.settings.openrouter_top_p,
                    "frequency_penalty": self.settings.openrouter_frequency_penalty,
                    "presence_penalty": self.settings.openrouter_presence_penalty,
                    "repetition_penalty": self.settings.openrouter_repetition_penalty,
                    "max_tokens": self.settings.openrouter_max_tokens,
                }
                try:
                    resp = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                except httpx.RequestError as e:
                    return json.dumps({"error": str(e)})
                if resp.status_code != 200:
                    try:
                        err = resp.json()
                        return json.dumps({"error": err})
                    except Exception:
                        return json.dumps({"error": resp.text})
                data = resp.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
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
        if self.settings.llm_provider == "openrouter":
            async with httpx.AsyncClient(timeout=120.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": self.settings.app_base_url,
                    "X-Title": "AI Knowledge Console",
                }
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                payload = {
                    "model": self.settings.openrouter_model,
                    "messages": messages,
                    "temperature": self.settings.openrouter_temperature if self.settings.openrouter_temperature else temperature,
                    "top_p": self.settings.openrouter_top_p,
                    "frequency_penalty": self.settings.openrouter_frequency_penalty,
                    "presence_penalty": self.settings.openrouter_presence_penalty,
                    "repetition_penalty": self.settings.openrouter_repetition_penalty,
                    "max_tokens": self.settings.openrouter_max_tokens,
                    "stream": True,
                }
                async with client.stream("POST", "https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload) as response:
                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        try:
                            data = json.loads(line[6:])
                        except json.JSONDecodeError:
                            continue
                        choice = data.get("choices", [{}])[0]
                        delta = choice.get("delta") or {}
                        content = delta.get("content")
                        if content:
                            yield content
        else:
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
