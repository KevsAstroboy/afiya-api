from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized configuration management
    Supports multiple environments and secure configuration
    """
    # Database Configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "telemedecine_db"
    DB_BACKEND: str = "postgresql"

    # Computed property for SQLAlchemy async connection
    @computed_field
    @property
    def DATABASE_URL(self) -> PostgresDsn:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Environment-specific settings
    ENV: str = "development"
    DEBUG: bool = False

    # Logging configuration
    LOG_LEVEL: str = "INFO"

    # LLM Provider Configuration
    LLM_PROVIDER: str = "anthropic"
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # WhatsApp Cloud API Configuration
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""

    # Redis Configuration
    REDIS_URL: str = "redis://redis:6379/0"

    # CinetPay Configuration
    CINETPAY_SITE_ID: str = ""
    CINETPAY_API_KEY: str = ""
    CINETPAY_SECRET_KEY: str = ""
    CINETPAY_INIT_ENDPOINT: str = "https://api-checkout.cinetpay.com/v2/payment"
    CINETPAY_CHECK_ENDPOINT: str = "https://api-checkout.cinetpay.com/v2/payment/check"

    # AWS Configuration (DynamoDB)
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = "AKIA57BI3IXJIRNQJPNZ"
    AWS_SECRET_ACCESS_KEY: str = "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"

    # Additional configurations
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def is_production(self) -> bool:
        return self.ENV == "production"


settings = Settings()
