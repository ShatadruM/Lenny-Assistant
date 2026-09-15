from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    OLLAMA_URL: str = "http://localhost:11434"
    
    # Optional API keys for cloud providers
    ANTHROPIC_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()