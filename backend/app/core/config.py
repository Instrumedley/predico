"""
Application configuration using Pydantic settings.
"""
import json
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional, Union


class Settings(BaseSettings):
    """Application settings."""
    
    # Project
    PROJECT_NAME: str = "World Cup Predictions"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: Optional[str] = None
    REDIS_CACHE_TTL: int = 3600
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://localhost:3006",
        "http://localhost:3007",
        "http://localhost:3008",
        "http://localhost:3009",
        "http://localhost:3010",
    ]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Union[List[str], str]) -> List[str]:
        """Parse CORS_ORIGINS from JSON string if needed."""
        if isinstance(v, str):
            # Remove extra quotes if present (from docker-compose)
            v = v.strip().strip('"').strip("'")
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                return [parsed]
            except (json.JSONDecodeError, TypeError):
                # If not JSON, treat as comma-separated string
                origins = [origin.strip() for origin in v.split(',') if origin.strip()]
                return origins if origins else cls.model_fields['CORS_ORIGINS'].default
        if isinstance(v, list):
            return v
        return []
    
    # AWS
    AWS_REGION: str = "eu-north-1"  # Stockholm, Sweden
    AWS_S3_BUCKET: Optional[str] = None
    
    # AWS Cognito
    COGNITO_ENABLED: bool = False  # Set to True to enable Cognito
    COGNITO_USER_POOL_ID: Optional[str] = None
    COGNITO_CLIENT_ID: Optional[str] = None
    
    # Cloudflare
    CLOUDFLARE_ZONE_ID: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

