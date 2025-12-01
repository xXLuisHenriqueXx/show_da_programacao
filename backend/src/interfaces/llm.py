from abc import ABC, abstractmethod
from typing import Generator, Optional

class LLMClientInterface(ABC):
    @abstractmethod
    def get_streaming_response(
        self, 
        messages: list, 
        vector_store_id: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Chat via streaming síncrono (yield)."""
        pass

    @abstractmethod
    def generate_structured_content(
        self, 
        system_prompt: str, 
        user_prompt: str,
        vector_store_id: Optional[str] = None
    ) -> str:
        """Gera conteúdo estruturado (JSON) de forma síncrona."""
        pass