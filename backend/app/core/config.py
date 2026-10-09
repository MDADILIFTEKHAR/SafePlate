import os
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

class Settings(BaseSettings):
    PROJECT_NAME: str = "SafePlate"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # AI Provider & Real-Time Engine
    DEMO_MODE: bool = False
    MODEL_PROVIDER: str = "ollama"
    MODEL_NAME: str = "llama3.2:3b"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_TIMEOUT_SECONDS: int = 30
    
    # Database
    DATABASE_URL: str = "sqlite:///./safeplate.db"
    
    # Bounded Loop Constraints
    MAX_AGENT_ITERATIONS: int = 3
    MAX_SUBSTITUTION_ATTEMPTS: int = 3
    
    # Server & Security
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://safeplate-4.onrender.com",
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    DATA_PATH: Path = DATA_DIR

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
