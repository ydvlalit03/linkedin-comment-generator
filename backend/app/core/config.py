"""
Configuration Management
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Keys
    GEMINI_API_KEY: Optional[str] = None  # Optional: Google AI Studio
    OPENAI_API_KEY: Optional[str] = None  # OpenAI API key
    ANTHROPIC_API_KEY: Optional[str] = None  # Anthropic Claude API key
    RAPIDAPI_KEY: Optional[str] = None  # RapidAPI for real LinkedIn data
    PARAPHRASE_API_KEY: Optional[str] = None  # Paraphrase Genius for extra humanization
    RAPIDAPI_BASE_URL: str = "https://linkedin-scraper-api-real-time-fast-affordable.p.rapidapi.com"
    RAPIDAPI_HOST: str = "linkedin-scraper-api-real-time-fast-affordable.p.rapidapi.com"
    SCRAPERAPI_KEY: Optional[str] = None  # Legacy: Optional ScraperAPI
    
    # AI Model Selection
    # Options: 'openai', 'gemini', 'anthropic'
    AI_PROVIDER: str = "anthropic"  # Default to Anthropic Claude
    
    # OpenAI Model Configuration
    # Options: 'gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo'
    OPENAI_MODEL: str = "gpt-4o-mini"  # Cost-effective default
    
    # Data Source Selection
    # Options: 'rapidapi', 'scraperapi', 'mock'
    DATA_SOURCE: str = "mock"  # Change to 'rapidapi' when you have the key
    
    # Gemini Model Configuration (Two-tier architecture)
    # 
    # CURRENT (Dec 2024): Using Gemini 2.0 Flash Exp (latest available)
    # FUTURE: Will upgrade to Gemini 2.5 when publicly released
    #
    # Migration Path:
    # Phase 1 (Now):      2.0-flash-exp (FREE, experimental)
    # Phase 2 (Q1 2025):  2.5-flash (when available)
    # Phase 3 (Stable):   2.5-pro + 2.5-flash (production)
    
    # Analysis Model: Deep reasoning for profiles/posts
    # Current: gemini-2.0-flash-exp (FREE)
    # Future: gemini-2.5-pro (when available)
    GEMINI_ANALYSIS_MODEL: str = "gemini-2.0-flash-exp"
    
    # Generation Model: Fast comment creation
    # Current: gemini-2.0-flash-exp (FREE)
    # Future: gemini-2.5-flash or gemini-2.5-flash-lite (when available)
    GEMINI_GENERATION_MODEL: str = "gemini-2.0-flash-exp"
    
    MAX_TOKENS: int = 3000  # Increased for complete JSON responses
    TEMPERATURE: float = 0.7
    
    # Database
    DATABASE_URL: str = "sqlite:///./linkedin_comments.db"
    
    # Caching Settings
    PROFILE_CACHE_DAYS: int = 7
    POST_CACHE_HOURS: int = 24
    COMMENT_CACHE_HOURS: int = 6
    
    # Fetch Limits
    MAX_POSTS_FETCH: int = 30  # Posts from last 30 days
    MAX_COMMENTS_ANALYZE: int = 50  # Top comments per post
    MAX_USER_COMMENTS_FETCH: int = 100  # User's comment history
    
    # Generation Settings
    COMMENT_VARIATIONS: int = 3
    MIN_COMMENT_LENGTH: int = 30
    MAX_COMMENT_LENGTH: int = 150
    
    # Rate Limiting
    RAPIDAPI_RATE_LIMIT: int = 100  # per hour
    CLAUDE_RATE_LIMIT: int = 50  # per minute
    
    # Application
    APP_NAME: str = "LinkedIn Comment Generator"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()