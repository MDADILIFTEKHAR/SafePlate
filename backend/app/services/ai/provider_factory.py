import os
from app.core.config import settings
from app.services.ai.base import AIProvider
from app.services.ai.local_ai_provider import local_ai_provider
from app.services.ai.ollama_provider import OllamaProvider

class ProviderFactory:
    _ollama_instance = None

    @classmethod
    def get_provider(cls) -> AIProvider:
        # If running in cloud production (e.g. Render) without a remote Ollama server,
        # or if MODEL_PROVIDER is not set to ollama, use local deterministic engine.
        if settings.MODEL_PROVIDER.lower() == "ollama":
            if os.getenv("RENDER") and "localhost" in settings.OLLAMA_BASE_URL:
                return local_ai_provider
            if cls._ollama_instance is None:
                cls._ollama_instance = OllamaProvider()
            return cls._ollama_instance

        # For "local", "demo", or any other provider, use the local AI engine
        return local_ai_provider

provider_factory = ProviderFactory()

