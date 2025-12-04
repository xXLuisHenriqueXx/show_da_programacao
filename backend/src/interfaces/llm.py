from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional

class LLMClientInterface(ABC):
    @abstractmethod
    def get_streaming_response(
        self, 
        messages: list, 
        vector_store_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Chat via streaming assíncrono (yield)."""
        pass

    @abstractmethod
    async def generate_structured_content(
        self, 
        system_prompt: str, 
        user_prompt: str,
        vector_store_id: Optional[str] = None
    ) -> str:
        """Gera conteúdo estruturado (JSON) de forma assíncrona."""
        pass