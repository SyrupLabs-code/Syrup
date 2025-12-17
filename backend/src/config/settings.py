from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]
    
    # Solana
    solana_rpc_url: Optional[str] = None
    solana_ws_url: Optional[str] = None
    
    # Polymarket
    polymarket_api_key: Optional[str] = None
    polymarket_secret: Optional[str] = None
    polymarket_passphrase: Optional[str] = None
    
    # Kalshi
    kalshi_api_key: Optional[str] = None
    kalshi_private_key: Optional[str] = None
    
    # AI Providers
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

