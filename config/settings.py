import os
import secrets
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Data directory: /data on Render, ./database locally
DATA_DIR = Path(os.getenv("MINTUU_DATA_DIR", str(BASE_DIR / "database")))
DATA_DIR.mkdir(parents=True, exist_ok=True)

class LoggingSettings(BaseModel):
    level: str = os.getenv("LOG_LEVEL", "INFO")
    format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"

class APISettings(BaseModel):
    cors_origins: list = Field(default_factory=lambda: _parse_cors_origins())
    port: int = int(os.getenv("PORT", os.getenv("API_PORT", 8003)))

class DatabaseSettings(BaseModel):
    sqlite_path: str = str(DATA_DIR / "mintuu_ecosystem.db")
    echo_queries: bool = False

class MemorySettings(BaseModel):
    short_term_capacity: int = 500
    ttl_seconds: int = 3600
    conversation_history_limit: int = 50

class AuthSettings(BaseModel):
    secret_key: str = os.getenv("SECRET_KEY", secrets.token_hex(32))
    algorithm: str = "HS256"
    access_token_expire_days: int = 7
    
class Environment(BaseModel):
    value: str = os.getenv("ENVIRONMENT", "development")

def _parse_cors_origins() -> list:
    """Parse CORS origins from environment or use defaults."""
    origins_env = os.getenv("ALLOWED_ORIGINS")
    if origins_env:
        return [o.strip() for o in origins_env.split(",")]
    # Development defaults
    return [
        "http://localhost:3000",
        "http://localhost:8003",
        "http://localhost:5173",
        "http://127.0.0.1:8003",
        "http://127.0.0.1:3000",
    ]

class Settings:
    """Centralized configuration and validation."""
    project_name: str = "Mintuu AI Ecosystem"
    version: str = "3.0.0"
    
    logging: LoggingSettings = LoggingSettings()
    api: APISettings = APISettings()
    database: DatabaseSettings = DatabaseSettings()
    memory: MemorySettings = MemorySettings()
    auth: AuthSettings = AuthSettings()
    environment: Environment = Environment()
    
    # LLM Settings
    DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "ollama")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Infrastructure
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CHROMADB_PATH = os.getenv("CHROMADB_PATH", str(DATA_DIR / "chroma_db"))
    
    # Tools
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    
    # Frontend URL (for CORS and email links)
    FRONTEND_URL = os.getenv("MINTUU_FRONTEND_URL", "http://localhost:8003")
    
    @classmethod
    def validate(cls):
        """Validate startup environment."""
        import logging
        logger = logging.getLogger("mintuu.config")
        warnings = []
        errors = []
        
        if cls.DEFAULT_LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required when default provider is openai.")
            
        if cls.DEFAULT_LLM_PROVIDER == "ollama":
            warnings.append(f"Using local Ollama at {cls.OLLAMA_BASE_URL}")
            
        if cls.GROQ_API_KEY:
            warnings.append("Groq API key detected — will use Groq for LLM inference.")
            
        if not cls.GITHUB_TOKEN:
            warnings.append("GITHUB_TOKEN not set. GitHub tool will be simulated.")
            
        for warn in warnings:
            logger.warning(f"Config Warning: {warn}")
            
        for err in errors:
            logger.error(f"Config Error: {err}")
            
        if errors:
            raise EnvironmentError("Failed to validate environment configuration.")
            
settings = Settings()
