"""
LinkedIn Scraper API - Real-Time, Fast & Affordable
API by karimgreek on RapidAPI
https://rapidapi.com/karimgreek/api/linkedin-scraper-api-real-time-fast-affordable
"""
import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)


class LinkedInScraperAPI:
    """
    LinkedIn Scraper API client with smart post filtering
    
    Endpoints:
    - /profile - Get LinkedIn profile data
    - /posts - Get user's posts
    - /company-posts - Get company posts
    - /post-comments - Get post comments
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://linkedin-scraper-api-real-time-fast-affordable.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "linkedin-scraper-api-real-time-fast-affordable.p.rapidapi.com"
        }
        
        # Time filters for smart post fetching
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
            linkedin_url: Full LinkedIn profile URL or username
            
        Returns:
            Profile data dictionary
        """
        try:
            username = self._extract_username(linkedin_url)
            logger.info(f"Fetching profile: {username}")
            
            # This API uses /profile/posts to get profile data
            # We'll extract profile info from the posts response
            endpoint = f"{self.base_url}/profile/posts"
            
            querystring = {"username": username, "page_number": "1"}
            
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=querystring,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract profile info from response
                if data and isinstance(data, dict):
                    # Check if we have posts data with profile info
                    posts_data = data.get('data', [])
                    
                    # Try to extract profile from first post's author
                    profile_info = {}
                    if isinstance(posts_data, list) and len(posts_data) > 0:
                        first_post = posts_data[0]
                        author = first_post.get('author', {})
                        profile_info = {
                            'name': author.get('name', username),
                            'headline': author.get('headline', ''),
                            'profile_url': f"https://linkedin.com/in/{username}"
                        }
                    else:
                        # Minimal profile if no posts
                        profile_info = {
                            'name': username,
                            'headline': '',
                            'profile_url': f"https://linkedin.com/in/{username}"
                        }
                    
                    profile = self._normalize_profile(profile_info)
                    logger.info(f"✓ Fetched profile: {profile.get('name', 'Unknown')}")
                    return profile
                else:
                    logger.error(f"Invalid profile data received")
                    return self._empty_profile(linkedin_url)
                    
            elif response.status_code == 429:
                logger.error("⚠️  Rate limit exceeded - wait before next request")
                return self._empty_profile(linkedin_url)
                
            else:
                logger.error(f"API error {response.status_code}: {response.text[:200]}")
                return self._empty_profile(linkedin_url)
                
        except requests.exceptions.Timeout:
            logger.error("Request timeout - API is slow or down")
            return self._empty_profile(linkedin_url)
            
        except Exception as e:
            logger.error(f"Error fetching profile: {str(e)}")
            return self._empty_profile(linkedin_url)
    
    def fetch_posts(
        self, 
        linkedin_url: str,
        max_posts: int = 10,
        use_smart_filtering: bool = True,
        max_days: int = 30
    ):
        """
        Fetch LinkedIn posts with smart time-based filtering
        ONLY returns posts from last max_days
        
        Returns:
            Dict: {
                "posts": [...],
                "has_recent_posts": bool,
                "total_found": int,
                "date_range": str,
                "message": str (optional)
            }
        """
        try:
            if use_smart_filtering:
                result = self._fetch_posts_smart_with_recency_check(linkedin_url, max_posts, max_days)
            else:
                posts = self._fetch_posts_simple(linkedin_url, max_posts, days=max_days)
                # Filter to only recent posts
                recent_posts = self._filter_by_recency(posts, max_days)
                result = {
                    "posts": recent_posts,
                    "has_recent_posts": len(recent_posts) > 0,
                    "total_found": len(recent_posts),
                    "date_range": f"Last {max_days} days"
                }
                
            return result
                
        except Exception as e:
            logger.error(f"Error fetching posts: {str(e)}")
            return {
                "posts": [],
                "has_recent_posts": False,
                "total_found": 0,
                "date_range": f"Last {max_days} days",
                "error": str(e)
            }
    
    def _fetch_posts_smart_with_recency_check(self, linkedin_url: str, max_posts: int, max_days: int):
        """Smart filtering with 30-day recency check"""
        logger.info(f"🔍 Fetching posts from last {max_days} days")
        
        all_posts = []
        
        # Only try filters within the max_days limit
        valid_filters = [f for f in self.time_filters if f['days'] <= max_days]
        
        for time_filter in valid_filters:
            days = time_filter['days']
            label = time_filter['label']
            
            logger.info(f"  ⏱️  Trying {label} filter...")
            
            posts = self._fetch_posts_simple(linkedin_url, max_posts * 2, days=days)
            
            if posts:
                logger.info(f"  ✓ Found {len(posts)} posts in {label}")
                all_posts = posts
                
                # Smart decision logic
                if len(posts) >= max_posts:
                    logger.info(f"  ✅ Got {len(posts)} posts, sufficient!")
                    break
                elif days == 3 and len(posts) < 3:
                    logger.info(f"  → Only {len(posts)} posts, expanding...")
                    continue
                elif days == 7 and len(posts) < 5:
                    logger.info(f"  → Only {len(posts)} posts, expanding...")
                    continue
                elif days == 21 and len(posts) < 8:
                    logger.info(f"  → Only {len(posts)} posts, expanding...")
                    continue
                else:
                    logger.info(f"  ✅ {len(posts)} posts is enough")
                    break
            else:
                logger.info(f"  ⚠️  No posts in {label}, trying longer...")
        
        # Filter to only posts within max_days
        recent_posts = self._filter_by_recency(all_posts, max_days)
        
        if len(recent_posts) == 0:
            logger.warning(f"⚠️  No posts found in last {max_days} days")
            return {
                "posts": [],
                "has_recent_posts": False,
                "total_found": 0,
                "date_range": f"Last {max_days} days",
                "message": f"No posts found in the last {max_days} days. User may be inactive."
            }
        
        logger.info(f"✅ Final: {len(recent_posts)} recent posts")
        return {
            "posts": recent_posts[:max_posts],
            "has_recent_posts": True,
            "total_found": len(recent_posts),
            "date_range": f"Last {max_days} days"
        }
    
    def _filter_by_recency(self, posts: List[Dict], max_days: int) -> List[Dict]:
        """Filter posts to only include those from last max_days"""
        if not posts:
            return []
        
        cutoff_date = datetime.now() - timedelta(days=max_days)
        recent_posts = []
        
        for post in posts:
            post_date = self._parse_post_date(post)
            if post_date and post_date >= cutoff_date:
                recent_posts.append(post)
        
        return recent_posts
    
    def _fetch_posts_smart(self, linkedin_url: str, max_posts: int) -> List[Dict]:
        """
        Smart progressive filtering to get optimal recent posts
        """
        logger.info(f"🔍 Starting smart post fetch for: {linkedin_url}")
        
        all_posts = []
        
        for time_filter in self.time_filters:
            days = time_filter['days']
            label = time_filter['label']
            
            logger.info(f"  ⏱️  Trying {label} filter...")
            
            posts = self._fetch_posts_simple(linkedin_url, max_posts * 2, days=days)
            
            if posts:
                logger.info(f"  ✓ Found {len(posts)} posts in {label}")
                all_posts = posts
                
                # Smart decision logic
                if len(posts) >= max_posts:
                    logger.info(f"  ✅ Got {len(posts)} posts, sufficient!")
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
                    logger.info(f"  ✅ {len(posts)} posts is enough for {label}")
                    break
            else:
                logger.info(f"  ⚠️  No posts found in {label}, trying longer period...")
        
        if all_posts:
            logger.info(f"✅ Final: {len(all_posts)} posts fetched")
        else:
            logger.warning("⚠️  No posts found in last 30 days")
        
        return all_posts[:max_posts]
    
    def _fetch_posts_simple(
        self, 
        linkedin_url: str, 
        max_posts: int,
        days: int = 30,
        page_number: int = 1
    ) -> List[Dict]:
        """
        Fetch posts for a specific time period
        
        Note: This API uses /profile/posts endpoint with username and page_number
        """
        try:
            username = self._extract_username(linkedin_url)
            
            endpoint = f"{self.base_url}/profile/posts"
            
            # API uses username and page_number parameters
            querystring = {
                "username": username,
                "page_number": str(page_number)
            }
            
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=querystring,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # API structure: {"success": true, "data": {"posts": [...], "pagination_token": "..."}}
                if isinstance(data, dict) and data.get('success'):
                    posts_data = data.get('data', {})
                    
                    # Extract posts from nested structure
                    if isinstance(posts_data, dict) and 'posts' in posts_data:
                        posts = posts_data.get('posts', [])
                    elif isinstance(posts_data, list):
                        posts = posts_data
                    else:
                        posts = []
                        
                elif isinstance(data, list):
                    posts = data
                elif isinstance(data, dict):
                    posts = data.get('posts', data.get('data', []))
                else:
                    posts = []
                
                if isinstance(posts, list) and len(posts) > 0:
                    # Filter by date
                    cutoff_date = datetime.now() - timedelta(days=days)
                    filtered_posts = []
                    
                    for post in posts[:max_posts]:  # Limit to max_posts
                        if isinstance(post, dict):
                            post_date = self._parse_post_date(post)
                            if post_date and post_date >= cutoff_date:
                                normalized = self._normalize_post(post)
                                filtered_posts.append(normalized)
                    
                    return filtered_posts
                else:
                    logger.error("Posts data is not a list")
                    return []
                    
            else:
                logger.error(f"Posts API error {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error in _fetch_posts_simple: {str(e)}")
            return []
    
    def fetch_post_comments(
        self, 
        post_url_or_id: str,
        max_comments: int = 15
    ) -> List[Dict]:
        """
        Fetch comments for a specific post
        
        Args:
            post_url_or_id: LinkedIn post URL or ID
            max_comments: Maximum comments to fetch
            
        Returns:
            List of comment dictionaries
        """
        try:
            # This API might use different endpoint structure
            # Check API docs for exact format
            endpoint = f"{self.base_url}/post/comments"
            
            # Try different parameter formats
            querystring = {
                "post_id": post_url_or_id,
                "page_number": "1"
            }
            
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=querystring,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle different response formats
                if isinstance(data, list):
                    comments = data
                elif isinstance(data, dict):
                    comments = data.get('comments', data.get('data', []))
                else:
                    comments = []
                
                if isinstance(comments, list):
                    return [self._normalize_comment(c) for c in comments[:max_comments]]
                else:
                    return []
            else:
                logger.error(f"Comments API error {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching comments: {str(e)}")
            return []
    
    def _parse_post_date(self, post: Dict) -> Optional[datetime]:
        """Parse post date from various formats"""
        try:
            # Try different date field names
            for field in ['publishedAt', 'createdAt', 'postedAt', 'timestamp', 'date']:
                if field in post:
                    date_value = post[field]
                    
                    # Handle timestamp (milliseconds)
                    if isinstance(date_value, (int, float)):
                        if date_value > 10000000000:  # Milliseconds
                            return datetime.fromtimestamp(date_value / 1000)
                        else:  # Seconds
                            return datetime.fromtimestamp(date_value)
                    
                    # Handle ISO string
                    elif isinstance(date_value, str):
                        try:
                            # Remove timezone info for simpler parsing
                            date_str = date_value.replace('Z', '+00:00')
                            return datetime.fromisoformat(date_str.split('+')[0])
                        except:
                            continue
            
            # If no date found, assume recent
            logger.debug("No date found in post, assuming recent")
            return datetime.now()
            
        except Exception as e:
            logger.debug(f"Error parsing date: {e}")
            return datetime.now()
    
    def _normalize_profile(self, data: Dict) -> Dict:
        """Normalize API profile data to our standard format"""
        
        # Handle nested structure
        profile_data = data.get('profile', data)
        
        # Combine first_name and last_name
        first_name = profile_data.get('first_name', '')
        last_name = profile_data.get('last_name', '')
        full_name = f"{first_name} {last_name}".strip() or profile_data.get('username', '')
        
        return {
            "name": full_name,
            "headline": profile_data.get('headline', ''),
            "about": profile_data.get('about', profile_data.get('summary', '')),
            "experience": self._normalize_experience(profile_data.get('experience', [])),
            "education": profile_data.get('education', []),
            "skills": profile_data.get('skills', []),
            "location": profile_data.get('location', ''),
            "connections": profile_data.get('connectionsCount', profile_data.get('connections', 0)),
            "followers": profile_data.get('followersCount', profile_data.get('followers', 0)),
            "profile_url": profile_data.get('profile_url', profile_data.get('url', '')),
            "profile_picture": profile_data.get('profile_picture', profile_data.get('photoUrl', '')),
        }
    
    def _normalize_experience(self, experience: List) -> List[Dict]:
        """Normalize experience data"""
        normalized = []
        
        if not isinstance(experience, list):
            return normalized
        
        for exp in experience[:5]:  # Top 5 experiences
            if isinstance(exp, dict):
                normalized.append({
                    "title": exp.get('title', exp.get('position', '')),
                    "company": exp.get('companyName', exp.get('company', '')),
                    "duration": exp.get('duration', ''),
                    "description": exp.get('description', '')
                })
        
        return normalized
    
    def _normalize_post(self, post: Dict) -> Dict:
        """Normalize post data to standard format"""
        
        # Handle different response structures
        post_data = post.get('post', post)
        
        # Extract stats
        stats = post_data.get('stats', {})
        
        # Extract author name
        author = post_data.get('author', {})
        first_name = author.get('first_name', '')
        last_name = author.get('last_name', '')
        author_name = f"{first_name} {last_name}".strip() or author.get('username', '')
        
        return {
            "post_id": post_data.get('urn', {}).get('activity_urn') or post_data.get('full_urn', post_data.get('id', '')),
            "content": post_data.get('text', post_data.get('commentary', post_data.get('caption', ''))),
            "posted_date": self._parse_posted_at(post_data.get('posted_at')),
            "likes_count": stats.get('total_reactions', stats.get('like', 0)),
            "comments_count": stats.get('comments', 0),
            "shares_count": stats.get('reposts', stats.get('shares', 0)),
            "media_type": self._detect_media_type(post_data),
            "author": author_name,
            "post_url": post_data.get('url', post_data.get('postUrl', '')),
        }
    
    def _parse_posted_at(self, posted_at) -> Optional[str]:
        """Parse posted_at field from API"""
        if not posted_at:
            return None
        
        if isinstance(posted_at, dict):
            # Try timestamp first
            timestamp = posted_at.get('timestamp')
            if timestamp:
                try:
                    # Timestamp is in milliseconds
                    dt = datetime.fromtimestamp(timestamp / 1000)
                    return dt.isoformat()
                except:
                    pass
            
            # Try date string
            date_str = posted_at.get('date')
            if date_str:
                return date_str
        
        return str(posted_at)
    
    def _normalize_comment(self, comment: Dict) -> Dict:
        """Normalize comment data"""
        
        comment_data = comment.get('comment', comment)
        
        return {
            "comment_id": comment_data.get('id', comment_data.get('urn', '')),
            "comment_text": comment_data.get('text', comment_data.get('content', '')),
            "author": comment_data.get('author', {}).get('name', ''),
            "posted_date": comment_data.get('publishedAt', comment_data.get('createdAt', '')),
            "likes_count": comment_data.get('likesCount', 0),
        }
    
    def _detect_media_type(self, post: Dict) -> str:
        """Detect if post has media"""
        if post.get('images') or post.get('image'):
            return 'image'
        elif post.get('video'):
            return 'video'
        elif post.get('article') or post.get('articleUrl'):
            return 'article'
        elif post.get('document'):
            return 'document'
        else:
            return 'text'
    
    def _empty_profile(self, linkedin_url: str) -> Dict:
        """Return empty profile structure"""
        return {
            "name": "",
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
    
    def _extract_username(self, linkedin_url: str) -> str:
        """
        Extract username from LinkedIn URL
        
        Examples:
        - https://linkedin.com/in/satyanadella -> satyanadella
        - https://www.linkedin.com/in/vidhant-jain/ -> vidhant-jain
        - vidhant-jain -> vidhant-jain
        """
        if not linkedin_url:
            return ""
        
        # Remove trailing slash
        url = linkedin_url.rstrip('/')
        
        # If it's just a username, return it
        if '/' not in url:
            return url
        
        # Extract from /in/ pattern
        if '/in/' in url:
            return url.split('/in/')[-1].split('/')[0]
        
        # Extract from /company/ pattern  
        if '/company/' in url:
            return url.split('/company/')[-1].split('/')[0]
        
        # Fallback: get last part of URL
        return url.split('/')[-1]


# Rate limiting for API calls
class APIRateLimiter:
    """
    Rate limiter to prevent hitting API limits
    
    Free plan: 10 requests/day
    Basic plan: 100 requests/month
    Pro plan: 1000 requests/month
    """
    
    def __init__(self, max_requests_per_minute: int = 10):
        self.max_requests = max_requests_per_minute
        self.request_times = []
    
    def wait_if_needed(self):
        """Wait if we're about to exceed rate limit"""
        now = time.time()
        
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        # If at limit, wait
        if len(self.request_times) >= self.max_requests:
            wait_time = 60 - (now - self.request_times[0]) + 1
            if wait_time > 0:
                logger.info(f"⏸️  Rate limit approaching, waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
                self.request_times = []
        
        # Record this request
        self.request_times.append(now)
    
    def get_remaining_requests(self) -> int:
        """Get number of requests available in current minute"""
        now = time.time()
        self.request_times = [t for t in self.request_times if now - t < 60]
        return self.max_requests - len(self.request_times)