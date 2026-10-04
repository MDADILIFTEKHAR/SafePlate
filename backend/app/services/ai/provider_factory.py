from app.core.config import settings
from app.services.ai.base import AIProvider
from app.services.ai.demo_provider import demo_provider
from app.services.ai.ollama_provider import OllamaProvider

class ProviderFactory:
    _ollama_instance = None

    @classmethod
    def get_provider(cls, force_demo: bool = False) -> AIProvider:
        if force_demo or settings.DEMO_MODE:
            return demo_provider
        
        if settings.MODEL_PROVIDER.lower() == "ollama":
            if cls._ollama_instance is None:
                cls._ollama_instance = OllamaProvider()
            return cls._ollama_instance
            
        return demo_provider

provider_factory = ProviderFactory()
