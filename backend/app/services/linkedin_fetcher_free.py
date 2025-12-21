"""
FREE LinkedIn Data Fetcher
Uses intelligent mock data optimized for our advanced analyzers
"""
from typing import Dict, List, Optional
import logging
from app.services.intelligent_mock_data import IntelligentMockData

logger = logging.getLogger(__name__)


class LinkedInFetcher:
    """
    FREE LinkedIn data fetcher using intelligent mock data
    Optimized for our advanced profile analyzer and comment generator
    """
    
    def __init__(self):
        self.mock_generator = IntelligentMockData()
        self.profile_cache = {}  # Cache profiles by URL
    
    def fetch_profile(self, linkedin_url: str) -> Optional[Dict]:
        """
        Generate intelligent mock profile data
        
        Returns realistic data matching our analyzer requirements
        """
        try:
            logger.info(f"✓ Generating intelligent mock profile for: {linkedin_url}")
            
            # Check cache first
            if linkedin_url in self.profile_cache:
                logger.info("  Using cached profile")
                return self.profile_cache[linkedin_url]
            
            # Generate new profile
            profile = self.mock_generator.generate_profile(linkedin_url)
            
            # Cache it
            self.profile_cache[linkedin_url] = profile
            
            logger.info(f"  ✓ Generated profile: {profile['name']}")
            logger.info(f"  ✓ Writing style: {profile.get('_style_template', {}).get('tone', 'varied')}")
            
            return profile
                
        except Exception as e:
            logger.error(f"❌ Error generating profile: {str(e)}")
            return None
    
    def fetch_user_comments(self, linkedin_url: str, limit: int = 100) -> List[Dict]:
        """
        Generate intelligent mock comment history
        
        Returns comments matching the user's writing style
        """
        try:
            logger.info(f"✓ Generating intelligent comment history for: {linkedin_url}")
            
            # Get profile to know writing style
            profile = self.profile_cache.get(linkedin_url)
            style_template = profile.get('_style_template') if profile else None
            
            # Generate comments
            comments = self.mock_generator.generate_user_comments(
                linkedin_url, 
                style_template
            )
            
            logger.info(f"  ✓ Generated {len(comments)} realistic comments")
            
            return comments[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error generating comments: {str(e)}")
            return []
    
    def fetch_posts(self, linkedin_url: str, days: int = 30) -> List[Dict]:
        """
        Generate intelligent mock posts
        
        Returns varied, realistic LinkedIn posts
        """
        try:
            logger.info(f"✓ Generating intelligent posts for: {linkedin_url}")
            
            posts = self.mock_generator.generate_posts(linkedin_url, days)
            
            logger.info(f"  ✓ Generated {len(posts)} varied posts")
            
            return posts
            
        except Exception as e:
            logger.error(f"❌ Error generating posts: {str(e)}")
            return []
    
    def fetch_post_comments(self, post_url: str, limit: int = 50) -> List[Dict]:
        """
        Generate intelligent mock post comments
        
        Returns realistic comments from various writing styles
        """
        try:
            logger.info(f"✓ Generating intelligent post comments")
            
            # Extract post type from URL if possible
            post_type = "thought_leadership"  # Default
            
            comments = self.mock_generator.generate_post_comments(post_type)
            
            logger.info(f"  ✓ Generated {len(comments)} realistic comments")
            
            return comments[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error generating post comments: {str(e)}")
            return []