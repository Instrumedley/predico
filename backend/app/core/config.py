"""
Application configuration using Pydantic settings.
"""
import json
from typing import Any, List, Literal, Optional, Union

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings

EnvironmentName = Literal["local", "staging", "production"]
EmailBackendName = Literal["local", "ses", "sendgrid"]


class Settings(BaseSettings):
    """Application settings."""
    
    # Project
    PROJECT_NAME: str = "World Cup Predictions"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    # Deployment environment: drives defaults (e.g. email backend) for stage/prod
    ENVIRONMENT: EnvironmentName = "local"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours when "remember me" is unchecked
    REMEMBER_ME_TOKEN_EXPIRE_DAYS: int = 30
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 5
    
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
                origins = [origin.strip().rstrip('/') for origin in v.split(',') if origin.strip()]
                return origins if origins else cls.model_fields['CORS_ORIGINS'].default
        if isinstance(v, list):
            return [origin.rstrip('/') if isinstance(origin, str) else origin for origin in v]
        return []
    
    # AWS
    AWS_REGION: str = "eu-north-1"  # Stockholm, Sweden
    AWS_S3_BUCKET: Optional[str] = None
    
    # AWS Cognito
    COGNITO_ENABLED: bool = False  # Set to True to enable Cognito
    COGNITO_USER_POOL_ID: Optional[str] = None
    COGNITO_CLIENT_ID: Optional[str] = None
    
    # Email Configuration
    # local: log to console + backend/email_logs/ (no delivery)
    # ses: AWS SES — uses IAM role or AWS credentials on the host
    # sendgrid: SendGrid API (recommended on Heroku; uses SENDGRID_API_KEY)
    EMAIL_ENABLED: bool = True
    EMAIL_BACKEND: EmailBackendName = "local"
    SES_FROM_EMAIL: str = "noreply@predico.com"
    FRONTEND_URL: str = "http://localhost:3005"
    SENDGRID_API_KEY: Optional[str] = None

    @field_validator("EMAIL_BACKEND", mode="before")
    @classmethod
    def validate_email_backend(cls, v: object) -> str:
        allowed = {"local", "ses", "sendgrid"}
        value = str(v).lower() if v is not None else "local"
        if value not in allowed:
            raise ValueError(f"EMAIL_BACKEND must be one of: {', '.join(sorted(allowed))}")
        return value

    @model_validator(mode="before")
    @classmethod
    def default_email_backend_for_environment(cls, data: Any) -> Any:
        """
        When ENVIRONMENT is staging/production, default EMAIL_BACKEND to ses
        unless EMAIL_BACKEND is explicitly set in the environment.
        """
        if not isinstance(data, dict):
            return data

        env = str(data.get("ENVIRONMENT", "local")).lower()
        if env in ("staging", "production") and "EMAIL_BACKEND" not in data:
            data["EMAIL_BACKEND"] = "ses"
        return data

    @model_validator(mode="after")
    def normalize_database_url(self) -> "Settings":
        """Heroku Postgres uses postgres://; SQLAlchemy async needs postgresql+asyncpg://."""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            self.DATABASE_URL = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url and "+psycopg2" not in url:
            self.DATABASE_URL = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self

    @property
    def is_local_environment(self) -> bool:
        return self.ENVIRONMENT == "local"

    @property
    def delivers_email_to_inbox(self) -> bool:
        """True when transactional emails are sent via a real provider."""
        return self.EMAIL_ENABLED and self.EMAIL_BACKEND in ("ses", "sendgrid")
    
    # Feature flags
    LEAGUE_PROGRESS_CHART_ENABLED: bool = False
    KNOCKOUT_STAGE_ENABLED: bool = False
    KNOCKOUT_STAGE_DEFAULT: bool = False
    DASHBOARD_NEWS_BANNER_ENABLED: bool = False

    # Cloudflare
    CLOUDFLARE_ZONE_ID: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

