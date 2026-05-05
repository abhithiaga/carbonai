from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "CarbonAI"
    DEBUG: bool = False
    SECRET_KEY: str = "changeme-in-production"

    # AWS
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    # OpenAI / LLM
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4o"
    LLM_MAX_TOKENS: int = 1024

    # Database (DynamoDB table names)
    EMISSIONS_TABLE: str = "carbonai-emissions"
    USERS_TABLE: str = "carbonai-users"
    ORGS_TABLE: str = "carbonai-orgs"

    # Redis (optional caching)
    REDIS_URL: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
