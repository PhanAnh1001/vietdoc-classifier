from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/vietdoc"

    # JWT
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # Groq API
    GROQ_API_KEY: str = ""
    GROQ_VISION_MODEL: str = "llama-3.2-11b-vision-preview"
    GROQ_LLM_MODEL: str = "llama-3.3-70b-versatile"

    # File upload
    MAX_FILE_SIZE_MB: int = 10
    MAX_BATCH_FILES: int = 50

    model_config = {"env_file": ".env"}


settings = Settings()
