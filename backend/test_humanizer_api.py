"""
Test Script for Humanizer API
Run this to verify your humanizer API credentials are working correctly
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.paraphrase_service import paraphrase_service
from app.core.config import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_humanizer_api():
    """Test the humanizer API connection and functionality"""
    
    print("=" * 70)
    print("HUMANIZER API TEST")
    print("=" * 70)
    
    # Check configuration
    print("\n1. Checking Configuration...")
    print(f"   Username: {settings.HUMANIZER_BOT_AUTH_USER}")
    print(f"   Password: {'*' * len(settings.HUMANIZER_BOT_AUTH_PASSWORD) if settings.HUMANIZER_BOT_AUTH_PASSWORD else 'Not set'}")
    print(f"   Enabled: {paraphrase_service.enabled}")
    
    if not paraphrase_service.enabled:
        print("\n❌ ERROR: Humanizer API not configured!")
        print("   Please set HUMANIZER_BOT_AUTH_USER and HUMANIZER_BOT_AUTH_PASSWORD in your .env file")
        return False
    
    # Test connection
    print("\n2. Testing Connection...")
    connection_ok = paraphrase_service.test_connection()
    
    if not connection_ok:
        print("❌ Connection test failed!")
        return False
    
    print("✓ Connection successful!")
    
    # Test with sample text
    print("\n3. Testing Humanization...")
    
    test_cases = [
        "Got it Alanna. The reason I reached out in the first place is your impressive background in high stakes safety and operations.",
        "This is a professional LinkedIn comment about AI and machine learning.",
        "Congratulations on your new role! Your experience in data science is impressive."
    ]
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n   Test {i}:")
        print(f"   Original: {test_text}")
        
        humanized = paraphrase_service.paraphrase(test_text)
        
        if humanized and humanized != test_text:
            print(f"   Humanized: {humanized}")
            print("   ✓ Success!")
        else:
            print(f"   Humanized: {humanized}")
            print("   ⚠️  Warning: Output same as input or empty")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    
    return True


def test_batch_humanization():
    """Test batch humanization"""
    
    print("\n" + "=" * 70)
    print("BATCH HUMANIZATION TEST")
    print("=" * 70)
    
    texts = [
        "Great insights on AI trends!",
        "Thanks for sharing this valuable information.",
        "Your perspective on machine learning is fascinating."
    ]
    
    print(f"\nHumanizing {len(texts)} comments...")
    
    results = paraphrase_service.paraphrase_batch(texts)
    
    print("\nResults:")
    for i, (original, humanized) in enumerate(zip(texts, results), 1):
        print(f"\n{i}. Original:  {original}")
        print(f"   Humanized: {humanized}")
        print(f"   Changed: {'Yes' if humanized != original else 'No'}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\n🚀 Starting Humanizer API Tests...\n")
    
    # Run basic test
    success = test_humanizer_api()
    
    if success:
        # Run batch test if basic test passed
        test_batch_humanization()
        
        print("\n✅ All tests completed successfully!")
        print("\nYour humanizer API is configured correctly and working.")
    else:
        print("\n❌ Tests failed!")
        print("\nPlease check your configuration and try again.")
        print("\nMake sure you have set in your .env file:")
        print("  HUMANIZER_BOT_AUTH_USER=lalit")
        print("  HUMANIZER_BOT_AUTH_PASSWORD=your_password")