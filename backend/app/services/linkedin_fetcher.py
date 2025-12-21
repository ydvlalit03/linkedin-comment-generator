"""
LinkedIn Data Fetcher Service
Fetches data from LinkedIn via RapidAPI
"""
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class LinkedInFetcher:
    """Fetches LinkedIn data via RapidAPI"""
    
    def __init__(self):
        self.base_url = settings.RAPIDAPI_BASE_URL
        self.headers = {
            "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
            "X-RapidAPI-Host": settings.RAPIDAPI_HOST
        }
    
    def fetch_profile(self, linkedin_url: str) -> Optional[Dict]:
        """
        Fetch complete profile data
        
        Returns:
            {
                "name": str,
                "headline": str,
                "about": str,
                "experience": List[Dict],
                "skills": List[str]
            }
        """
        try:
            endpoint = f"{self.base_url}/get-profile-data-by-url"
            response = requests.get(
                endpoint,
                headers=self.headers,
                params={"url": linkedin_url},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._normalize_profile(data)
            else:
                logger.error(f"Profile fetch failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching profile: {str(e)}")
            return None
    
    def fetch_user_comments(self, linkedin_url: str, limit: int = 100) -> List[Dict]:
        """
        Fetch user's recent comment activity
        
        Returns:
            [
                {
                    "comment_text": str,
                    "post_context": str,
                    "date": datetime
                }
            ]
        """
        try:
            endpoint = f"{self.base_url}/get-profile-posts"
            response = requests.get(
                endpoint,
                headers=self.headers,
                params={"url": linkedin_url, "limit": limit},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._extract_user_comments(data)
            return []
            
        except Exception as e:
            logger.error(f"Error fetching user comments: {str(e)}")
            return []
    
    def fetch_posts(self, linkedin_url: str, days: int = 30) -> List[Dict]:
        """
        Fetch recent posts from a profile
        
        Returns:
            [
                {
                    "post_url": str,
                    "content": str,
                    "media_type": str,
                    "posted_date": datetime,
                    "likes_count": int,
                    "comments_count": int
                }
            ]
        """
        try:
            endpoint = f"{self.base_url}/get-profile-posts"
            response = requests.get(
                endpoint,
                headers=self.headers,
                params={"url": linkedin_url},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                posts = self._normalize_posts(data)
                # Filter by date
                cutoff_date = datetime.now() - timedelta(days=days)
                return [p for p in posts if p.get("posted_date", datetime.min) > cutoff_date]
            return []
            
        except Exception as e:
            logger.error(f"Error fetching posts: {str(e)}")
            return []
    
    def fetch_post_comments(self, post_url: str, limit: int = 50) -> List[Dict]:
        """
        Fetch comments on a specific post
        
        Returns:
            [
                {
                    "author_name": str,
                    "comment_text": str,
                    "likes_count": int
                }
            ]
        """
        try:
            endpoint = f"{self.base_url}/get-post-comments"
            response = requests.get(
                endpoint,
                headers=self.headers,
                params={"url": post_url, "limit": limit},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._normalize_comments(data)
            return []
            
        except Exception as e:
            logger.error(f"Error fetching post comments: {str(e)}")
            return []
    
    def _normalize_profile(self, raw_data: Dict) -> Dict:
        """Normalize profile data from API response"""
        # Adapt based on your RapidAPI service's response format
        return {
            "name": raw_data.get("name", ""),
            "headline": raw_data.get("headline", ""),
            "about": raw_data.get("summary", "") or raw_data.get("about", ""),
            "experience": [
                {
                    "title": exp.get("title", ""),
                    "company": exp.get("company", "") or exp.get("companyName", ""),
                    "description": exp.get("description", ""),
                    "duration": exp.get("duration", "")
                }
                for exp in raw_data.get("experience", [])
            ],
            "skills": raw_data.get("skills", [])
        }
    
    def _extract_user_comments(self, raw_data: Dict) -> List[Dict]:
        """Extract comments from user activity data"""
        comments = []
        # This depends on how RapidAPI returns comment data
        for activity in raw_data.get("activities", []):
            if activity.get("type") == "comment":
                comments.append({
                    "comment_text": activity.get("text", ""),
                    "post_context": activity.get("post_summary", ""),
                    "date": self._parse_date(activity.get("date"))
                })
        return comments
    
    def _normalize_posts(self, raw_data: Dict) -> List[Dict]:
        """Normalize posts data"""
        posts = []
        for post in raw_data.get("posts", []):
            posts.append({
                "post_url": post.get("url", ""),
                "content": post.get("text", "") or post.get("content", ""),
                "media_type": self._detect_media_type(post),
                "posted_date": self._parse_date(post.get("date")),
                "likes_count": post.get("likes", 0),
                "comments_count": post.get("comments", 0)
            })
        return posts
    
    def _normalize_comments(self, raw_data: Dict) -> List[Dict]:
        """Normalize comments data"""
        return [
            {
                "author_name": comment.get("author", {}).get("name", ""),
                "comment_text": comment.get("text", ""),
                "likes_count": comment.get("likes", 0)
            }
            for comment in raw_data.get("comments", [])
        ]
    
    def _detect_media_type(self, post: Dict) -> str:
        """Detect post media type"""
        if post.get("images"):
            return "image"
        elif post.get("video"):
            return "video"
        elif post.get("article"):
            return "article"
        elif post.get("poll"):
            return "poll"
        return "text"
    
    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse date string to datetime"""
        if not date_str:
            return datetime.now()
        try:
            # Adjust format based on API response
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return datetime.now()