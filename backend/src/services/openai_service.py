import os
from openai import AsyncOpenAI
from src.interfaces.llm import LLMClientInterface
from typing import AsyncGenerator, Optional, List, Dict

class OpenAIClient(LLMClientInterface):
    def __init__(self):
        # Cliente Assíncrono para não bloquear o WebSocket
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _get_tools_config(self, vector_store_id: Optional[str]) -> Optional[List[Dict]]:
        if vector_store_id:
            return [{
                "type": "file_search",
                "vector_store_ids": [vector_store_id]
            }]
        return None

    async def get_streaming_response(
        self, 
        messages: list, 
        vector_store_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        
        tools = self._get_tools_config(vector_store_id)
        
        stream = await self.client.responses.create(
            model="gpt-5-nano",
            input=messages,
            tools=tools,
            stream=True
        )
        
        async for event in stream:
            if event.type == 'response.output_text.delta':
                if event.delta:
                    yield event.delta

    async def generate_structured_content(
        self, 
        system_prompt: str, 
        user_prompt: str,
        vector_store_id: Optional[str] = None
    ) -> str:
        
        tools = self._get_tools_config(vector_store_id)
        combined_input = f"INSTRUÇÃO DO SISTEMA: {system_prompt}\n\nPEDIDO DO USUÁRIO: {user_prompt}"

        response = await self.client.responses.create(
            model="gpt-5-nano", 
            input=combined_input,
            tools=tools
        )
        
        return response.output_text