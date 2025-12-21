"""
Unified LinkedIn Data Service
Intelligently routes to RapidAPI, ScraperAPI, or Mock data
"""
import logging
from typing import Dict, List, Optional
from app.core.config import settings
from app.services.user_profile_manager import UserProfileManager

logger = logging.getLogger(__name__)


class LinkedInService:
    """
    Unified service for LinkedIn data with multiple data sources
    
    Priority:
    1. User Profile JSON (for current user)
    2. RapidAPI (for target profiles/posts)
    3. Mock data (fallback)
    """
    
    def __init__(self):
        self.data_source = settings.DATA_SOURCE
        self.profile_manager = UserProfileManager()
        
        # Initialize appropriate fetcher based on configuration
        if self.data_source == 'rapidapi' and settings.RAPIDAPI_KEY:
            from app.services.linkedin_scraper_api import LinkedInScraperAPI
            self.fetcher = LinkedInScraperAPI(settings.RAPIDAPI_KEY)
            logger.info("✓ Using LinkedIn Scraper API (RapidAPI - karimgreek)")
            
        elif self.data_source == 'scraperapi' and settings.SCRAPERAPI_KEY:
            from app.services.linkedin_fetcher_scraperapi import LinkedInFetcherScraperAPI
            self.fetcher = LinkedInFetcherScraperAPI(settings.SCRAPERAPI_KEY)
            logger.info("✓ Using ScraperAPI for LinkedIn data")
            
        else:
            from app.services.linkedin_fetcher_free import LinkedInFetcherFree
            self.fetcher = LinkedInFetcherFree()
            logger.info("✓ Using MOCK data for LinkedIn (no API key provided)")
    
    def get_user_profile(self, linkedin_url: str) -> Dict:
        """
        Get user profile (checks JSON first, then API)
        
        For current user, always prefer saved JSON profile
        """
        username = self._extract_username(linkedin_url)
        
        # Try to load from JSON first
        saved_profile = self.profile_manager.load_profile(username)
        if saved_profile:
            logger.info(f"✓ Using saved profile for: {username}")
            return self._convert_from_json_format(saved_profile)
        
        # Fetch from API
        logger.info(f"Fetching new profile from {self.data_source}: {username}")
        profile = self.fetcher.fetch_profile(linkedin_url)
        
        return profile
    
    def get_target_profile(self, linkedin_url: str) -> Dict:
        """
        Get target profile (always from API, never from JSON)
        """
        logger.info(f"Fetching target profile from {self.data_source}: {linkedin_url}")
        return self.fetcher.fetch_profile(linkedin_url)
    
    def get_user_comments(self, linkedin_url: str, max_comments: int = 50) -> List[Dict]:
        """
        Get user's comment history
        
        For mock data: generates intelligent fake comments
        For RapidAPI: fetches actual comment history (if available)
        """
        if hasattr(self.fetcher, 'fetch_user_comments'):
            return self.fetcher.fetch_user_comments(linkedin_url, max_comments)
        else:
            # Fallback: return empty list
            logger.warning(f"Fetcher {type(self.fetcher).__name__} doesn't support user comments")
            return []
    
    def get_target_posts(
        self,
        linkedin_url: str,
        max_posts: int = 10,
        max_days: int = 30,
        use_smart_filtering: bool = True
    ):
        """
        Get target person's recent posts (ONLY from last max_days)
        
        Args:
            linkedin_url: Target's LinkedIn URL
            max_posts: Maximum number of posts to return
            max_days: Only get posts from last N days (default: 30)
            use_smart_filtering: Use progressive time filtering
            
        Returns:
            Dict with posts and metadata OR List (for backward compatibility)
        """
        if hasattr(self.fetcher, 'fetch_posts'):
            # RapidAPI has smart filtering with recency check
            result = self.fetcher.fetch_posts(
                linkedin_url,
                max_posts=max_posts,
                use_smart_filtering=use_smart_filtering,
                max_days=max_days
            )
            return result
        else:
            # Fallback for mock/scraper (returns list)
            return self.fetcher.fetch_user_posts(linkedin_url, max_posts)
    
    def get_post_comments(self, post_id: str, max_comments: int = 15) -> List[Dict]:
        """Get comments for a specific post"""
        if hasattr(self.fetcher, 'fetch_post_comments'):
            return self.fetcher.fetch_post_comments(post_id, max_comments)
        else:
            # Mock data
            return self.fetcher.generate_post_comments()
    
    def save_user_profile(
        self,
        linkedin_url: str,
        profile_data: Dict,
        writing_style: Dict,
        real_comments: List[str]
    ) -> bool:
        """
        Save user profile to JSON for future use
        
        This is THE WAY to store user data permanently
        """
        username = self._extract_username(linkedin_url)
        
        # Create profile structure
        profile = self.profile_manager.create_profile_structure(
            basic_info={
                'name': profile_data.get('name', ''),
                'headline': profile_data.get('headline', ''),
                'about': profile_data.get('about', ''),
                'location': profile_data.get('location', ''),
                'profile_url': linkedin_url,
                'skills': profile_data.get('skills', [])
            },
            writing_style=writing_style,
            real_comments=real_comments,
            expertise=profile_data.get('expertise_areas', []),
            experience=profile_data.get('experience', [])
        )
        
        return self.profile_manager.save_profile(username, profile)
    
    def get_saved_writing_style(self, linkedin_url: str) -> Optional[Dict]:
        """Get writing style from saved profile"""
        username = self._extract_username(linkedin_url)
        return self.profile_manager.get_writing_style(username)
    
    def has_saved_profile(self, linkedin_url: str) -> bool:
        """Check if user has a saved profile"""
        username = self._extract_username(linkedin_url)
        return self.profile_manager.profile_exists(username)
    
    def list_saved_profiles(self) -> List[str]:
        """List all saved user profiles"""
        return self.profile_manager.list_profiles()
    
    def delete_saved_profile(self, linkedin_url: str) -> bool:
        """Delete a saved profile"""
        username = self._extract_username(linkedin_url)
        return self.profile_manager.delete_profile(username)
    
    def _extract_username(self, linkedin_url: str) -> str:
        """Extract username from LinkedIn URL"""
        if '/in/' in linkedin_url:
            username = linkedin_url.split('/in/')[-1].strip('/')
        else:
            username = linkedin_url.strip('/')
        
        # Remove query parameters
        if '?' in username:
            username = username.split('?')[0]
        
        return username
    
    def _convert_from_json_format(self, json_profile: Dict) -> Dict:
        """Convert saved JSON profile to standard profile format"""
        basic = json_profile.get('basic_info', {})
        professional = json_profile.get('professional', {})
        
        return {
            'name': basic.get('name', ''),
            'headline': basic.get('headline', ''),
            'about': basic.get('about', ''),
            'location': basic.get('location', ''),
            'profile_url': basic.get('profile_url', ''),
            'skills': professional.get('skills', []),
            'experience': professional.get('experience', []),
            'expertise_areas': professional.get('expertise_areas', []),
        }


class ProfileAnalysisWorkflow:
    """
    Complete workflow for analyzing and saving user profiles
    """
    
    def __init__(self):
        self.service = LinkedInService()
    
    def analyze_and_save_user(
        self,
        linkedin_url: str,
        force_reanalyze: bool = False
    ) -> Dict:
        """
        Complete workflow:
        1. Check if profile exists
        2. If not (or force), fetch and analyze
        3. Save to JSON
        4. Return analysis
        
        Args:
            linkedin_url: User's LinkedIn URL
            force_reanalyze: Force new analysis even if profile exists
            
        Returns:
            Complete analysis dictionary
        """
        username = self.service._extract_username(linkedin_url)
        
        # Check existing profile
        if not force_reanalyze and self.service.has_saved_profile(linkedin_url):
            logger.info(f"Using existing profile for: {username}")
            saved_profile = self.service.profile_manager.load_profile(username)
            return {
                'profile': self.service._convert_from_json_format(saved_profile),
                'writing_style': saved_profile.get('writing_style'),
                'from_cache': True
            }
        
        # Fetch fresh data
        logger.info(f"Analyzing new profile: {username}")
        
        # Get profile data
        profile = self.service.get_user_profile(linkedin_url)
        
        # Get real comment samples (you'll need to implement this based on your needs)
        # For now, using placeholder
        real_comments = self._fetch_user_comments(linkedin_url)
        
        # Analyze writing style (using your existing analyzer)
        from app.services.profile_analyzer_gemini import ProfileAnalyzer
        analyzer = ProfileAnalyzer()
        
        comments_for_analysis = [{'comment_text': c} for c in real_comments]
        writing_style = analyzer.analyze_user_writing_style(profile, comments_for_analysis)
        
        # Save to JSON
        success = self.service.save_user_profile(
            linkedin_url,
            profile,
            writing_style,
            real_comments
        )
        
        if success:
            logger.info(f"✓ Saved profile: {username}")
        
        return {
            'profile': profile,
            'writing_style': writing_style,
            'from_cache': False,
            'saved': success
        }
    
    def _fetch_user_comments(self, linkedin_url: str) -> List[str]:
        """
        Fetch user's real comments from their activity
        
        TODO: Implement real comment fetching from RapidAPI
        For now, returns empty list
        """
        # This would call RapidAPI to get user's comment history
        # Not all APIs support this, so might need manual input
        return []