"""
Configuration management for the Guest Recommendation Generation API.
"""

import os
from typing import Optional
from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application metadata
    APP_NAME: str = "Guest Recommendation Generation API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-powered personalized recommendations for hotel guests"
    
    # Google Cloud Configuration (Required)
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_LOCATION: str = "us-east4"
    
    # Optional API Keys
    GOOGLE_PLACES_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Hotel Location Configuration
    HOTEL_LOCATION: str = "Aura New Haven Hotel, New Haven, CT"  # Specific hotel address for distance calculations
    
    # Database API Configuration
    RESERVATION_API_BASE: str = "https://api.gptpricing.com/zendesk-comments/ai-summary"
    RESERVATION_API_SECRET: str = "agentsecretnjzd7f89asa878d97asd"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    RELOAD: bool = False
    
    # AI Model Configuration
    GEMINI_MODEL: str = "gemini-2.5-pro"  # Use gemini-1.0-pro-002 for better availability
    GEMINI_TEMPERATURE: float = 0.3
    GEMINI_MAX_TOKENS: Optional[int] = 4000
    
    # Google Cloud Authentication
    USE_SERVICE_ACCOUNT: bool = True
    SERVICE_ACCOUNT_FILE: Optional[str] = None
    
    # Recommendation Configuration
    DEFAULT_MAX_RECOMMENDATIONS: int = 5
    MIN_RECOMMENDATIONS: int = 3
    
    # Timeout Configuration
    API_TIMEOUT: int = 30
    GOOGLE_PLACES_TIMEOUT: int = 10
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # CORS Configuration
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Health Check
    HEALTH_CHECK_ENABLED: bool = True
    
    # Validation
    @field_validator('GOOGLE_CLOUD_PROJECT')
    @classmethod
    def validate_google_project(cls, v):
        if not v or v == "your_google_cloud_project_id":
            raise ValueError("GOOGLE_CLOUD_PROJECT must be set")
        return v
    
    @field_validator('PORT')
    @classmethod
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("PORT must be between 1 and 65535")
        return v
    
    @field_validator('GEMINI_TEMPERATURE')
    @classmethod
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("GEMINI_TEMPERATURE must be between 0.0 and 1.0")
        return v
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
