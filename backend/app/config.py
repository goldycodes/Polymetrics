from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # GraphQL endpoint for Polymarket API
    graphql_endpoint: str = "https://subgraph.satsuma-prod.com/f5c1a7dd3ab7/polymarket/matic-markets/api"
    
    # Rate limiting configuration
    max_requests_per_10s: int = 50
    request_timeout: float = 30.0  # seconds for GraphQL queries

    model_config = {
        "env_prefix": "POLYMARKET_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "allow"  # Allow extra fields for flexibility
    }

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

settings = get_settings()
