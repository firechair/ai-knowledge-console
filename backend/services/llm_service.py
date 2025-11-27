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
        """Generate a completion (non-streaming)"""
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
        """Generate a streaming completion"""
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
        api_data: Optional[Dict] = None
    ) -> str:
        """Build a RAG prompt with context and optional API data"""
        context_text = "\n\n".join([
            f"[Source: {c['metadata'].get('filename', 'unknown')}]\n{c['content']}"
            for c in context_chunks
        ])
        
        prompt_parts = [f"Question: {query}\n"]
        
        if context_text:
            prompt_parts.append(f"Document Context:\n{context_text}\n")
        
        if api_data:
            prompt_parts.append(f"External Data:\n{json.dumps(api_data, indent=2)}\n")
        
        prompt_parts.append(
            "Based on the above context and data, provide a comprehensive answer. "
            "If the information is not in the context, say so clearly."
        )
        
        return "\n".join(prompt_parts)
