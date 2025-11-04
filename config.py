from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application settings"""
    port: int = 8080
    app_name: str = "Package Version Checker A2A Agent"
    version: str = "1.0.0"
    
    # API Timeouts
    pypi_timeout: int = 10
    npm_timeout: int = 10
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    """Get cached settings instance"""
    return Settings()