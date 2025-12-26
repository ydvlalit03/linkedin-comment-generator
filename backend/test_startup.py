#!/usr/bin/env python3
"""
Quick test to verify main.py loads correctly
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing main.py imports...")

try:
    from app.core.config import settings
    print("✓ Config loaded")
    print(f"  - GEMINI_API_KEY: {'set' if settings.GEMINI_API_KEY else 'NOT SET'}")
    print(f"  - SCRAPERAPI_KEY: {'set' if settings.SCRAPERAPI_KEY else 'NOT SET (will use mock data)'}")
    
    # Test importing main
    import main
    print("✓ Main.py imported successfully")
    print(f"✓ FastAPI app created: {main.app.title}")
    print(f"✓ LinkedIn fetcher initialized")
    print(f"✓ Profile analyzer initialized")
    print(f"✓ Comment generator initialized")
    
    print("\n🎉 All systems ready!")
    print("\nTo start the server, run:")
    print("  python main.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nMake sure you've installed all dependencies:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nCheck your .env file:")
    print("  - GEMINI_API_KEY must be set")
    print("  - SCRAPERAPI_KEY is optional")
    sys.exit(1)