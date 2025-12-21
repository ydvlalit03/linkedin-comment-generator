"""
LinkedIn Data Fetcher using RapidAPI
Fetches real LinkedIn posts with smart time-based filtering
"""
import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)


class LinkedInFetcherRapidAPI:
    """Fetch LinkedIn data using RapidAPI with smart filtering"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://linkedin-data-api.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "linkedin-data-api.p.rapidapi.com"
        }
        
        # Time filters in order of preference (newest first)
        self.time_filters = [
            {"days": 3, "label": "3 days"},
            {"days": 7, "label": "1 week"},
            {"days": 21, "label": "3 weeks"},
            {"days": 30, "label": "1 month"}
        ]
    
    def fetch_profile(self, linkedin_url: str) -> Dict:
        """
        Fetch LinkedIn profile data
        
        Args:
            linkedin_url: Full LinkedIn profile URL
            
        Returns:
            Profile data dictionary
        """
        try:
            logger.info(f"Fetching profile from RapidAPI: {linkedin_url}")
            
            # Extract username from URL
            username = self._extract_username(linkedin_url)
            
            # Call RapidAPI endpoint
            endpoint = f"{self.base_url}/get-profile"
            params = {"username": username}
            
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                profile = self._normalize_profile(data)
                logger.info(f"✓ Fetched profile: {profile.get('name')}")
                return profile
            else:
                logger.error(f"RapidAPI error: {response.status_code} - {response.text}")
                return self._empty_profile(linkedin_url)
                
        except Exception as e:
            logger.error(f"Error fetching profile: {str(e)}")
            return self._empty_profile(linkedin_url)
    
    def fetch_posts(
        self, 
        linkedin_url: str,
        max_posts: int = 10,
        use_smart_filtering: bool = True
    ) -> List[Dict]:
        """
        Fetch LinkedIn posts with smart time-based filtering
        
        Strategy:
        1. Try 3 days first (most recent, most relevant)
        2. If < 3 posts, try 1 week
        3. If < 5 posts, try 3 weeks
        4. If < 8 posts, try 1 month
        
        Args:
            linkedin_url: Target person's LinkedIn URL
            max_posts: Maximum posts to fetch (default: 10)
            use_smart_filtering: Use progressive time filtering
            
        Returns:
            List of post dictionaries
        """
        try:
            username = self._extract_username(linkedin_url)
            
            if use_smart_filtering:
                return self._fetch_posts_smart(username, max_posts)
            else:
                return self._fetch_posts_simple(username, max_posts, days=30)
                
        except Exception as e:
            logger.error(f"Error fetching posts: {str(e)}")
            return []
    
    def _fetch_posts_smart(self, username: str, max_posts: int) -> List[Dict]:
        """
        Smart progressive filtering to get optimal recent posts
        
        Algorithm:
        - Start with 3 days (newest, most relevant)
        - If not enough posts, expand to 1 week
        - Continue expanding until we have enough posts or reach 1 month
        """
        logger.info(f"Starting smart post fetch for: {username}")
        
        all_posts = []
        
        for time_filter in self.time_filters:
            days = time_filter['days']
            label = time_filter['label']
            
            logger.info(f"  Trying {label} filter...")
            
            posts = self._fetch_posts_simple(username, max_posts, days=days)
            
            if posts:
                logger.info(f"  ✓ Found {len(posts)} posts in {label}")
                all_posts = posts
                
                # Decision logic
                if len(posts) >= max_posts:
                    logger.info(f"  → Got {len(posts)} posts, sufficient!")
                    break
                elif days == 3 and len(posts) < 3:
                    logger.info(f"  → Only {len(posts)} posts, expanding to 1 week...")
                    continue
                elif days == 7 and len(posts) < 5:
                    logger.info(f"  → Only {len(posts)} posts, expanding to 3 weeks...")
                    continue
                elif days == 21 and len(posts) < 8:
                    logger.info(f"  → Only {len(posts)} posts, expanding to 1 month...")
                    continue
                else:
                    logger.info(f"  → {len(posts)} posts is enough for {label}")
                    break
            else:
                logger.info(f"  → No posts found in {label}, trying longer period...")
        
        if all_posts:
            logger.info(f"✓ Final: {len(all_posts)} posts fetched")
        else:
            logger.warning("⚠️ No posts found in last 30 days")
        
        return all_posts[:max_posts]
    
    def _fetch_posts_simple(
        self, 
        username: str, 
        max_posts: int,
        days: int = 30
    ) -> List[Dict]:
        """
        Fetch posts for a specific time period
        
        Args:
            username: LinkedIn username
            max_posts: Maximum posts to fetch
            days: Number of days to look back
            
        Returns:
            List of posts
        """
        try:
            endpoint = f"{self.base_url}/get-profile-posts"
            params = {
                "username": username,
                "start": 0,
                "count": max_posts
            }
            
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', [])
                
                # Filter by date
                cutoff_date = datetime.now() - timedelta(days=days)
                filtered_posts = []
                
                for post in posts:
                    post_date = self._parse_post_date(post)
                    if post_date and post_date >= cutoff_date:
                        normalized = self._normalize_post(post)
                        filtered_posts.append(normalized)
                
                return filtered_posts
            else:
                logger.error(f"RapidAPI error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error in _fetch_posts_simple: {str(e)}")
            return []
    
    def fetch_post_comments(
        self, 
        post_urn: str,
        max_comments: int = 15
    ) -> List[Dict]:
        """
        Fetch comments for a specific post
        
        Args:
            post_urn: LinkedIn post URN/ID
            max_comments: Maximum comments to fetch
            
        Returns:
            List of comment dictionaries
        """
        try:
            endpoint = f"{self.base_url}/get-post-comments"
            params = {
                "post_urn": post_urn,
                "count": max_comments
            }
            
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                comments = data.get('data', [])
                return [self._normalize_comment(c) for c in comments]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error fetching comments: {str(e)}")
            return []
    
    def _extract_username(self, linkedin_url: str) -> str:
        """Extract username from LinkedIn URL"""
        # https://www.linkedin.com/in/username/ -> username
        # https://linkedin.com/in/username -> username
        
        if '/in/' in linkedin_url:
            username = linkedin_url.split('/in/')[-1].strip('/')
        elif 'linkedin.com/' in linkedin_url:
            username = linkedin_url.split('linkedin.com/')[-1].strip('/')
        else:
            username = linkedin_url
        
        # Remove query parameters
        if '?' in username:
            username = username.split('?')[0]
        
        return username
    
    def _parse_post_date(self, post: Dict) -> Optional[datetime]:
        """Parse post date from various formats"""
        try:
            # RapidAPI usually provides timestamp or ISO date
            if 'created_at' in post:
                timestamp = post['created_at']
                if isinstance(timestamp, int):
                    return datetime.fromtimestamp(timestamp / 1000)  # milliseconds
                elif isinstance(timestamp, str):
                    return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            if 'posted_date' in post:
                date_str = post['posted_date']
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            # If no date, assume recent
            return datetime.now()
            
        except Exception as e:
            logger.debug(f"Error parsing date: {e}")
            return datetime.now()
    
    def _normalize_profile(self, data: Dict) -> Dict:
        """Normalize RapidAPI profile data to our format"""
        return {
            "name": data.get('name', data.get('firstName', '') + ' ' + data.get('lastName', '')),
            "headline": data.get('headline', ''),
            "about": data.get('summary', data.get('about', '')),
            "experience": self._normalize_experience(data.get('experience', [])),
            "education": data.get('education', []),
            "skills": data.get('skills', []),
            "location": data.get('location', ''),
            "connections": data.get('connections', 0),
            "followers": data.get('followers', 0),
            "profile_url": data.get('url', ''),
            "profile_picture": data.get('picture', ''),
        }
    
    def _normalize_experience(self, experience: List) -> List[Dict]:
        """Normalize experience data"""
        normalized = []
        for exp in experience[:5]:  # Top 5 experiences
            normalized.append({
                "title": exp.get('title', ''),
                "company": exp.get('company', exp.get('companyName', '')),
                "duration": exp.get('duration', ''),
                "description": exp.get('description', '')
            })
        return normalized
    
    def _normalize_post(self, post: Dict) -> Dict:
        """Normalize post data"""
        return {
            "post_id": post.get('urn', post.get('id', '')),
            "content": post.get('text', post.get('content', '')),
            "posted_date": self._parse_post_date(post).isoformat() if self._parse_post_date(post) else None,
            "likes_count": post.get('likes', post.get('numLikes', 0)),
            "comments_count": post.get('comments', post.get('numComments', 0)),
            "shares_count": post.get('shares', post.get('numShares', 0)),
            "media_type": self._detect_media_type(post),
            "author": post.get('author', {}).get('name', ''),
        }
    
    def _normalize_comment(self, comment: Dict) -> Dict:
        """Normalize comment data"""
        return {
            "comment_id": comment.get('id', ''),
            "comment_text": comment.get('text', ''),
            "author": comment.get('author', {}).get('name', ''),
            "posted_date": comment.get('created_at', ''),
            "likes_count": comment.get('likes', 0),
        }
    
    def _detect_media_type(self, post: Dict) -> str:
        """Detect if post has media"""
        if post.get('images') or post.get('image'):
            return 'image'
        elif post.get('video'):
            return 'video'
        elif post.get('article'):
            return 'article'
        else:
            return 'text'
    
    def _empty_profile(self, linkedin_url: str) -> Dict:
        """Return empty profile structure"""
        username = self._extract_username(linkedin_url)
        return {
            "name": username,
            "headline": "",
            "about": "",
            "experience": [],
            "education": [],
            "skills": [],
            "location": "",
            "connections": 0,
            "followers": 0,
            "profile_url": linkedin_url,
            "profile_picture": "",
        }


# Rate limiting helper
class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    def wait_if_needed(self):
        """Wait if we're hitting rate limits"""
        now = time.time()
        
        # Remove calls older than 1 minute
        self.calls = [t for t in self.calls if now - t < 60]
        
        # If we've hit the limit, wait
        if len(self.calls) >= self.calls_per_minute:
            wait_time = 60 - (now - self.calls[0])
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
                self.calls = []
        
        # Record this call
        self.calls.append(now)