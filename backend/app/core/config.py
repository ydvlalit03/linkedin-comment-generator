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
    PARAPHRASE_API_KEY: Optional[str] = None  # Paraphrase Genius for extra humanization (DEPRECATED)
    
    # Humanizer API Credentials (NEW - Replaces Paraphrase API)
    HUMANIZER_BOT_AUTH_USER: Optional[str] = None  # Humanizer API username
    HUMANIZER_BOT_AUTH_PASSWORD: Optional[str] = None  # Humanizer API password
    
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


# Validation function for configuration
def validate_settings():
    """Validate that required settings are configured"""
    
    # Check AI providers
    has_anthropic = bool(settings.ANTHROPIC_API_KEY)
    has_openai = bool(settings.OPENAI_API_KEY)
    has_gemini = bool(settings.GEMINI_API_KEY)
    
    if not (has_anthropic or has_openai or has_gemini):
        print("⚠️  WARNING: No AI provider configured!")
        print("   Please set at least one of: ANTHROPIC_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY")
        return False
    
    # Log available providers
    providers = []
    if has_anthropic:
        providers.append("Anthropic Claude")
    if has_openai:
        providers.append(f"OpenAI ({settings.OPENAI_MODEL})")
    if has_gemini:
        providers.append(f"Gemini ({settings.GEMINI_GENERATION_MODEL})")
    
    print(f"✓ Available AI providers: {', '.join(providers)}")
    
    # Check humanizer API (optional but recommended)
    has_humanizer = bool(settings.HUMANIZER_BOT_AUTH_USER and settings.HUMANIZER_BOT_AUTH_PASSWORD)
    if has_humanizer:
        print("✓ Humanizer API configured")
    else:
        print("⚠️  Humanizer API not configured (optional - provides extra humanization)")
        if settings.PARAPHRASE_API_KEY:
            print("   Note: PARAPHRASE_API_KEY is deprecated, use HUMANIZER_BOT_AUTH_USER/PASSWORD instead")
    
    # Check LinkedIn data source
    if settings.DATA_SOURCE == "rapidapi" and not settings.RAPIDAPI_KEY:
        print("⚠️  RapidAPI key not set but DATA_SOURCE=rapidapi")
        print("   Either set RAPIDAPI_KEY or change DATA_SOURCE to 'mock'")
    elif settings.DATA_SOURCE == "rapidapi" and settings.RAPIDAPI_KEY:
        print(f"✓ LinkedIn data source: RapidAPI")
    else:
        print(f"✓ LinkedIn data source: {settings.DATA_SOURCE}")
    
    return True


# Run validation on import (can be disabled by setting env var)
import os
if os.getenv("SKIP_CONFIG_VALIDATION") != "true":
    try:
        validate_settings()
    except Exception as e:
        print(f"Configuration validation error: {e}")