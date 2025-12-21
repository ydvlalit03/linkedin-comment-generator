"""
User Profile Manager
Stores and manages user writing profiles in local JSON files
"""
import json
import os
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UserProfileManager:
    """
    Manages user profiles stored as JSON files
    
    Each user profile contains:
    - Basic info (name, headline, expertise)
    - Writing style analysis
    - Real comment samples
    - Analysis metadata
    """
    
    def __init__(self, profiles_dir: str = "user_profiles"):
        self.profiles_dir = profiles_dir
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Create profiles directory if it doesn't exist"""
        os.makedirs(self.profiles_dir, exist_ok=True)
        logger.info(f"User profiles directory: {self.profiles_dir}")
    
    def save_profile(self, username: str, profile_data: Dict) -> bool:
        """
        Save user profile to JSON file
        
        Args:
            username: LinkedIn username (e.g., 'vidhant-jain')
            profile_data: Complete profile dictionary
            
        Returns:
            True if saved successfully
        """
        try:
            filepath = self._get_profile_path(username)
            
            # Add metadata
            profile_data['_metadata'] = {
                'username': username,
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            # Save to JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Saved profile: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving profile {username}: {e}")
            return False
    
    def load_profile(self, username: str) -> Optional[Dict]:
        """
        Load user profile from JSON file
        
        Args:
            username: LinkedIn username
            
        Returns:
            Profile dictionary or None if not found
        """
        try:
            filepath = self._get_profile_path(username)
            
            if not os.path.exists(filepath):
                logger.info(f"Profile not found: {username}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                profile = json.load(f)
            
            logger.info(f"✓ Loaded profile: {username}")
            return profile
            
        except Exception as e:
            logger.error(f"Error loading profile {username}: {e}")
            return None
    
    def profile_exists(self, username: str) -> bool:
        """Check if profile exists"""
        filepath = self._get_profile_path(username)
        return os.path.exists(filepath)
    
    def delete_profile(self, username: str) -> bool:
        """Delete user profile"""
        try:
            filepath = self._get_profile_path(username)
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"✓ Deleted profile: {username}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting profile {username}: {e}")
            return False
    
    def list_profiles(self) -> list:
        """List all saved profiles"""
        try:
            files = os.listdir(self.profiles_dir)
            profiles = [f.replace('.json', '') for f in files if f.endswith('.json')]
            return sorted(profiles)
        except Exception as e:
            logger.error(f"Error listing profiles: {e}")
            return []
    
    def create_profile_structure(
        self,
        basic_info: Dict,
        writing_style: Dict,
        real_comments: list,
        expertise: list,
        experience: list
    ) -> Dict:
        """
        Create a complete profile structure
        
        Args:
            basic_info: {name, headline, about, location}
            writing_style: {tone, formality_score, avg_length, etc.}
            real_comments: List of actual LinkedIn comments
            expertise: List of expertise areas
            experience: List of work experience
            
        Returns:
            Complete profile dictionary ready to save
        """
        return {
            # Basic Information
            "basic_info": {
                "name": basic_info.get('name', ''),
                "headline": basic_info.get('headline', ''),
                "about": basic_info.get('about', ''),
                "location": basic_info.get('location', ''),
                "profile_url": basic_info.get('profile_url', ''),
            },
            
            # Professional Background
            "professional": {
                "expertise_areas": expertise,
                "experience": experience,
                "skills": basic_info.get('skills', []),
            },
            
            # Writing Style Analysis
            "writing_style": {
                "tone": writing_style.get('tone', 'professional'),
                "formality_score": writing_style.get('formality_score', 0.6),
                "avg_comment_length": writing_style.get('avg_comment_length', 40),
                "sentence_length_variation": writing_style.get('sentence_length_variation', 'medium'),
                "emoji_usage": writing_style.get('emoji_usage', 'low'),
                "common_phrases": writing_style.get('common_phrases', []),
                "typical_openings": writing_style.get('typical_comment_openings', []),
                "contraction_frequency": writing_style.get('contraction_frequency', 'occasional'),
                "burstiness_level": writing_style.get('burstiness_level', 'medium'),
                "engagement_patterns": writing_style.get('engagement_patterns', {
                    "asks_questions": False,
                    "shares_experiences": True,
                    "gives_advice": False
                }),
                "personality_traits": writing_style.get('personality_traits', ['professional']),
            },
            
            # Real Comment Samples (for reference)
            "real_comments": real_comments,
            
            # Analysis Metadata
            "analysis": {
                "total_comments_analyzed": len(real_comments),
                "analyzed_date": datetime.now().isoformat(),
                "confidence_score": writing_style.get('confidence_score', 0.7),
            }
        }
    
    def get_writing_style(self, username: str) -> Optional[Dict]:
        """Get just the writing style section"""
        profile = self.load_profile(username)
        if profile:
            return profile.get('writing_style')
        return None
    
    def get_expertise(self, username: str) -> Optional[list]:
        """Get just the expertise areas"""
        profile = self.load_profile(username)
        if profile:
            return profile.get('professional', {}).get('expertise_areas', [])
        return None
    
    def get_real_comments(self, username: str) -> list:
        """Get real comment samples"""
        profile = self.load_profile(username)
        if profile:
            return profile.get('real_comments', [])
        return []
    
    def update_writing_style(self, username: str, writing_style: Dict) -> bool:
        """Update just the writing style section"""
        profile = self.load_profile(username)
        if profile:
            profile['writing_style'] = writing_style
            profile['analysis']['analyzed_date'] = datetime.now().isoformat()
            return self.save_profile(username, profile)
        return False
    
    def add_comment_sample(self, username: str, comment: str) -> bool:
        """Add a new comment sample to profile"""
        profile = self.load_profile(username)
        if profile:
            if 'real_comments' not in profile:
                profile['real_comments'] = []
            
            # Add comment if not duplicate
            if comment not in profile['real_comments']:
                profile['real_comments'].append(comment)
                profile['analysis']['total_comments_analyzed'] = len(profile['real_comments'])
                return self.save_profile(username, profile)
        return False
    
    def _get_profile_path(self, username: str) -> str:
        """Get filepath for username"""
        # Sanitize username
        safe_username = username.replace('/', '_').replace('\\', '_')
        return os.path.join(self.profiles_dir, f"{safe_username}.json")
    
    def export_profile(self, username: str, export_path: str) -> bool:
        """Export profile to a specific location"""
        try:
            profile = self.load_profile(username)
            if profile:
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(profile, f, indent=2, ensure_ascii=False)
                logger.info(f"✓ Exported profile to: {export_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error exporting profile: {e}")
            return False
    
    def import_profile(self, filepath: str) -> bool:
        """Import profile from a JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                profile = json.load(f)
            
            username = profile.get('_metadata', {}).get('username')
            if not username:
                # Try to extract from basic_info
                username = profile.get('basic_info', {}).get('profile_url', '')
                username = username.split('/in/')[-1].strip('/') if '/in/' in username else 'imported_profile'
            
            return self.save_profile(username, profile)
            
        except Exception as e:
            logger.error(f"Error importing profile: {e}")
            return False


def create_example_profile() -> Dict:
    """
    Create an example profile structure for documentation
    """
    return {
        "basic_info": {
            "name": "Vidhant Jain",
            "headline": "Product Manager | Building AI-powered tools",
            "about": "Passionate about building products that solve real problems...",
            "location": "Jaipur, India",
            "profile_url": "https://linkedin.com/in/vidhant-jain"
        },
        "professional": {
            "expertise_areas": [
                "Product Management",
                "AI/ML",
                "SaaS",
                "Growth Strategy"
            ],
            "experience": [
                {
                    "title": "Product Manager",
                    "company": "Tech Startup",
                    "duration": "2023 - Present",
                    "description": "Leading AI product development"
                }
            ],
            "skills": ["Python", "Product Strategy", "AI", "Leadership"]
        },
        "writing_style": {
            "tone": "professional-casual",
            "formality_score": 0.5,
            "avg_comment_length": 35,
            "sentence_length_variation": "high",
            "emoji_usage": "moderate",
            "common_phrases": [
                "Here's the thing",
                "In my experience",
                "That's spot on"
            ],
            "typical_openings": [
                "Love this.",
                "Great point about",
                "This resonates."
            ],
            "contraction_frequency": "frequent",
            "burstiness_level": "high",
            "engagement_patterns": {
                "asks_questions": True,
                "shares_experiences": True,
                "gives_advice": False
            },
            "personality_traits": ["analytical", "direct", "helpful"]
        },
        "real_comments": [
            "Love this. The part about timing hit different. We learned that the hard way too.",
            "That's exactly what we saw. Cash flow beats everything else when reality hits.",
            "Been there. The pivot saved us but man, those 3 months were brutal."
        ],
        "analysis": {
            "total_comments_analyzed": 3,
            "analyzed_date": datetime.now().isoformat(),
            "confidence_score": 0.85
        }
    }