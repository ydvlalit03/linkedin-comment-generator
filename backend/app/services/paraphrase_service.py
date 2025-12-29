"""
Paraphrase Service using Custom Humanizer API
Adds extra humanization layer by paraphrasing generated comments
"""
import requests
import logging
from typing import Optional
from requests.auth import HTTPBasicAuth
from app.core.config import settings

logger = logging.getLogger(__name__)


class ParaphraseService:
    """
    Paraphrases comments using Custom Humanizer API
    Adds extra layer of humanization and variation
    """
    
    def __init__(self):
        self.api_url = "https://primary-production-37efc.up.railway.app/webhook/humanizer"
        self.username = getattr(settings, 'HUMANIZER_BOT_AUTH_USER', None)
        self.password = getattr(settings, 'HUMANIZER_BOT_AUTH_PASSWORD', None)
        self.enabled = bool(self.username and self.password)
        
        if self.enabled:
            logger.info("✓ Humanizer API service enabled")
        else:
            logger.warning("⚠️ Humanizer API service disabled (missing HUMANIZER_BOT_AUTH_USER or HUMANIZER_BOT_AUTH_PASSWORD)")
    
    def paraphrase(self, text: str, mode: str = "standard") -> Optional[str]:
        """
        Paraphrase/humanize text using Custom Humanizer API
        
        Args:
            text: Original text to paraphrase/humanize
            mode: Paraphrase mode (ignored for this API, kept for compatibility)
        
        Returns:
            Humanized text or original text if failed
        """
        if not self.enabled:
            logger.debug("Humanizer API disabled, returning original")
            return text
        
        if not text or not text.strip():
            logger.warning("Empty text provided for humanization")
            return text
        
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "content": text
            }
            
            logger.debug(f"Humanizing: {text[:50]}...")
            
            # Use Basic Auth
            auth = HTTPBasicAuth(self.username, self.password)
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                auth=auth,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # DEBUG: Log the actual response structure
                logger.debug(f"📥 API Response type: {type(result)}")
                logger.debug(f"📥 API Response: {result}")
                
                # API returns format: [{"output": "humanized text"}]
                humanized = text  # Default to original
                
                # Handle list response
                if isinstance(result, list) and len(result) > 0:
                    first_item = result[0]
                    if isinstance(first_item, dict):
                        humanized = first_item.get('output', text)
                    elif isinstance(first_item, str):
                        humanized = first_item
                
                # Handle dict response (in case API changes)
                elif isinstance(result, dict):
                    humanized = result.get('output', result.get('content', text))
                
                # Validate humanized output
                if humanized and humanized.strip() and humanized != text:
                    logger.info(f"✓ Humanized successfully")
                    logger.debug(f"Original: {text[:60]}...")
                    logger.debug(f"Humanized: {humanized[:60]}...")
                    return humanized.strip()
                else:
                    logger.warning(f"No humanized output found in response, returning original")
                    return text
                
            elif response.status_code == 401:
                logger.error("Humanizer API authentication failed - check HUMANIZER_BOT_AUTH_USER and HUMANIZER_BOT_AUTH_PASSWORD")
                return text
                
            elif response.status_code == 429:
                logger.warning(f"Humanizer API rate limit exceeded, returning original")
                return text
                
            else:
                logger.warning(f"Humanizer API error {response.status_code}: {response.text[:200]}")
                return text  # Return original on error
                
        except requests.exceptions.Timeout:
            logger.warning("Humanizer API timeout, returning original")
            return text
        except requests.exceptions.ConnectionError:
            logger.error("Humanizer API connection error, returning original")
            return text
        except Exception as e:
            logger.error(f"Humanizer API error: {str(e)}")
            if 'response' in locals():
                try:
                    logger.debug(f"Response was: {response.text[:200]}")
                except:
                    pass
            return text  # Return original on error
    
    def paraphrase_batch(self, texts: list, mode: str = "standard") -> list:
        """
        Humanize multiple texts
        
        Args:
            texts: List of texts to humanize
            mode: Paraphrase mode (ignored, kept for compatibility)
        
        Returns:
            List of humanized texts (originals returned if humanization fails)
        """
        results = []
        
        for i, text in enumerate(texts, 1):
            logger.debug(f"Humanizing comment {i}/{len(texts)}")
            humanized = self.paraphrase(text, mode=mode)
            results.append(humanized)
        
        return results
    
    def paraphrase_with_fallback(self, text: str, modes: list = None) -> str:
        """
        Try to humanize text (modes parameter ignored but kept for compatibility)
        
        Args:
            text: Original text
            modes: List of modes (ignored for this API)
        
        Returns:
            Humanized text or original if failed
        """
        result = self.paraphrase(text)
        
        if result and result.strip() and result != text:
            logger.debug(f"✓ Humanization succeeded")
            return result
        
        logger.warning("Humanization failed, returning original")
        return text
    
    def test_connection(self) -> bool:
        """
        Test connection to humanizer API
        
        Returns:
            True if API is accessible and auth is valid
        """
        if not self.enabled:
            logger.warning("Humanizer API not enabled")
            return False
        
        try:
            # Test with simple text
            test_text = "This is a test message."
            result = self.paraphrase(test_text)
            
            if result and result != test_text:
                logger.info("✓ Humanizer API connection test successful")
                return True
            else:
                logger.warning("Humanizer API connection test returned original text")
                return False
                
        except Exception as e:
            logger.error(f"Humanizer API connection test failed: {e}")
            return False


# Global instance
paraphrase_service = ParaphraseService()


# Backwards compatibility alias
def humanize_text(text: str) -> str:
    """
    Convenience function for humanizing text
    
    Args:
        text: Text to humanize
    
    Returns:
        Humanized text
    """
    return paraphrase_service.paraphrase(text)