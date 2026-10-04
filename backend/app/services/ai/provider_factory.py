from app.core.config import settings
from app.services.ai.base import AIProvider
from app.services.ai.local_ai_provider import local_ai_provider
from app.services.ai.ollama_provider import OllamaProvider

class ProviderFactory:
    _ollama_instance = None

    @classmethod
    def get_provider(cls) -> AIProvider:
        if settings.MODEL_PROVIDER.lower() == "ollama":
            if cls._ollama_instance is None:
                cls._ollama_instance = OllamaProvider()
            return cls._ollama_instance
            
        return local_ai_provider

provider_factory = ProviderFactory()
