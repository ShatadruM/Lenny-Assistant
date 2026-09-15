import httpx
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from app.core.config import settings

class LLMFactory:
    def __init__(self):
        self.ollama_url = f"{settings.OLLAMA_URL}/api/chat"
        self.local_model = "llama3.1"

    async def call_cloud_agent(self, system_prompt: str, messages: list, tools: list, provider: str = "anthropic", api_key: str = None):
        if provider == "anthropic":
            active_key = api_key or settings.ANTHROPIC_API_KEY
            if not active_key:
                raise ValueError("An Anthropic API key is required.")
            client = AsyncAnthropic(api_key=active_key)
            response = await client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=2000,
                system=system_prompt,
                messages=messages,
                tools=tools
            )
            return response

        elif provider == "openai":
            active_key = api_key or getattr(settings, 'OPENAI_API_KEY', None)
            if not active_key:
                raise ValueError("An OpenAI API key is required.")
            client = AsyncOpenAI(api_key=active_key)
            
            # Format Anthropic tools to OpenAI tools format
            openai_tools = [{"type": "function", "function": t} for t in tools] if tools else None
            
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": system_prompt}] + messages,
                tools=openai_tools,
            )
            return response
            
        elif provider == "grok":
            active_key = api_key or getattr(settings, 'GROK_API_KEY', None)
            if not active_key:
                raise ValueError("A Grok API key is required.")
            client = AsyncOpenAI(api_key=active_key, base_url="https://api.x.ai/v1")
            
            openai_tools = [{"type": "function", "function": t} for t in tools] if tools else None
            
            response = await client.chat.completions.create(
                model="grok-beta",
                messages=[{"role": "system", "content": system_prompt}] + messages,
                tools=openai_tools,
            )
            return response

        else:
            raise ValueError(f"Unknown cloud provider: {provider}")

    async def call_local_agent(self, system_prompt: str, messages: list, tools: list):
        formatted_messages = [{"role": "system", "content": system_prompt}] + messages
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                self.ollama_url,
                json={
                    "model": self.local_model,
                    "messages": formatted_messages,
                    "tools": tools,
                    "stream": False
                }
            )
            resp.raise_for_status()
            return resp.json()["message"]