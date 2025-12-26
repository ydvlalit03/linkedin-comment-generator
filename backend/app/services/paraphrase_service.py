"""
Paraphrase Service using Paraphrase Genius API
Adds extra humanization layer by paraphrasing generated comments
"""
import requests
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class ParaphraseService:
    """
    Paraphrases comments using Paraphrase Genius API
    Adds extra layer of humanization and variation
    """
    
    def __init__(self):
        self.api_url = "https://paraphrase-genius.p.rapidapi.com/dev/paraphrase/"
        self.api_key = settings.PARAPHRASE_API_KEY
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            logger.info("✓ Paraphrase service enabled")
        else:
            logger.warning("⚠️ Paraphrase service disabled (no API key)")
    
    def paraphrase(self, text: str, mode: str = "standard") -> Optional[str]:
        """
        Paraphrase text using Paraphrase Genius API
        
        Args:
            text: Original text to paraphrase
            mode: Paraphrase mode ('standard', 'fluent', 'creative', 'formal', 'simple', 'multiple')
        
        Returns:
            Paraphrased text or None if failed
        """
        if not self.enabled:
            logger.debug("Paraphrase disabled, returning original")
            return text
        
        try:
            headers = {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": "paraphrase-genius.p.rapidapi.com",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text,
                "result_type": mode  # standard, fluent, creative, formal, simple, multiple
            }
            
            logger.debug(f"Paraphrasing: {text[:50]}... (mode: {mode})")
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # DEBUG: Log the actual response structure
                logger.info(f"📥 API Response type: {type(result)}")
                logger.info(f"📥 API Response: {result}")
                
                # API can return different formats:
                # 1. Direct dict: {"result": "paraphrased text"}
                # 2. List of dicts: [{"paraphrased_output": "text"}, ...]
                # 3. Dict with result key containing list
                
                paraphrased = text  # Default to original
                
                # Handle list response
                if isinstance(result, list):
                    if len(result) > 0:
                        first_item = result[0]
                        if isinstance(first_item, dict):
                            # Try common keys
                            paraphrased = (
                                first_item.get('paraphrased_output') or 
                                first_item.get('result') or 
                                first_item.get('text') or 
                                text
                            )
                        elif isinstance(first_item, str):
                            paraphrased = first_item
                
                # Handle dict response
                elif isinstance(result, dict):
                    result_value = result.get('result')
                    
                    # Result could be string
                    if isinstance(result_value, str):
                        paraphrased = result_value
                    
                    # Result could be list
                    elif isinstance(result_value, list) and len(result_value) > 0:
                        first_item = result_value[0]
                        if isinstance(first_item, dict):
                            paraphrased = (
                                first_item.get('paraphrased_output') or 
                                first_item.get('result') or 
                                first_item.get('text') or 
                                text
                            )
                        elif isinstance(first_item, str):
                            paraphrased = first_item
                    
                    # Try other possible keys
                    else:
                        paraphrased = (
                            result.get('paraphrased_output') or
                            result.get('paraphrase') or
                            result.get('output') or
                            text
                        )
                
                if paraphrased and paraphrased != text:
                    logger.info(f"✓ Paraphrased successfully")
                    logger.debug(f"Original: {text[:60]}...")
                    logger.debug(f"Paraphrased: {paraphrased[:60]}...")
                    return paraphrased
                else:
                    logger.warning(f"No paraphrase found in response, returning original")
                    return text
                
            else:
                logger.warning(f"Paraphrase API error {response.status_code}: {response.text[:100]}")
                return text  # Return original on error
                
        except requests.exceptions.Timeout:
            logger.warning("Paraphrase API timeout, returning original")
            return text
        except Exception as e:
            logger.error(f"Paraphrase error: {str(e)}")
            logger.debug(f"Response was: {response.json() if 'response' in locals() else 'No response'}")
            return text  # Return original on error
    
    def paraphrase_batch(self, texts: list, mode: str = "standard") -> list:
        """
        Paraphrase multiple texts
        
        Args:
            texts: List of texts to paraphrase
            mode: Paraphrase mode
        
        Returns:
            List of paraphrased texts (originals returned if paraphrase fails)
        """
        results = []
        
        for i, text in enumerate(texts, 1):
            logger.debug(f"Paraphrasing comment {i}/{len(texts)}")
            paraphrased = self.paraphrase(text, mode=mode)
            results.append(paraphrased)
        
        return results
    
    def paraphrase_with_fallback(self, text: str, modes: list = None) -> str:
        """
        Try multiple paraphrase modes until one succeeds
        
        Args:
            text: Original text
            modes: List of modes to try (default: ['standard', 'fluent'])
        
        Returns:
            Paraphrased text or original if all fail
        """
        if modes is None:
            modes = ['standard', 'fluent']
        
        for mode in modes:
            result = self.paraphrase(text, mode=mode)
            if result and result != text:
                logger.debug(f"✓ Paraphrase succeeded with mode: {mode}")
                return result
        
        logger.warning("All paraphrase modes failed, returning original")
        return text


# Global instance
paraphrase_service = ParaphraseService()