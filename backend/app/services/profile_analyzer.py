"""
Profile Analyzer Service
Analyzes user profiles and writing styles using Claude
"""
from anthropic import Anthropic
from typing import Dict, List
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)


class ProfileAnalyzer:
    """Analyzes profiles and extracts writing patterns"""
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL
    
    def analyze_user_writing_style(
        self, 
        user_data: Dict, 
        user_comments: List[Dict]
    ) -> Dict:
        """
        Analyze user's writing style from profile and comment history
        
        Returns:
            {
                "tone": str,
                "formality_score": float,
                "avg_comment_length": int,
                "emoji_usage": str,
                "common_phrases": List[str],
                "engagement_patterns": Dict,
                "personality_traits": List[str],
                "comment_structure": str
            }
        """
        try:
            prompt = self._build_style_analysis_prompt(user_data, user_comments)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.3,  # Lower for more consistent analysis
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse JSON response
            analysis = json.loads(response.content[0].text)
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing writing style: {str(e)}")
            return self._default_writing_style()
    
    def analyze_target_profile(self, target_data: Dict) -> Dict:
        """
        Analyze target person's profile to understand their interests
        
        Returns:
            {
                "expertise_areas": List[str],
                "professional_focus": str,
                "communication_style": str,
                "key_themes": List[str]
            }
        """
        try:
            prompt = f"""Analyze this LinkedIn profile and extract key insights:

Name: {target_data.get('name')}
Headline: {target_data.get('headline')}
About: {target_data.get('about', '')[:500]}

Experience:
{self._format_experience(target_data.get('experience', [])[:3])}

Provide analysis in JSON format:
{{
    "expertise_areas": ["area1", "area2"],
    "professional_focus": "description",
    "communication_style": "formal/casual/technical",
    "key_themes": ["theme1", "theme2"]
}}"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            logger.error(f"Error analyzing target profile: {str(e)}")
            return {}
    
    def analyze_post_context(
        self, 
        post: Dict, 
        existing_comments: List[Dict]
    ) -> Dict:
        """
        Analyze post content and existing comments
        
        Returns:
            {
                "main_topic": str,
                "sentiment": str,
                "key_points": List[str],
                "engagement_type": str,
                "comment_themes": List[str]
            }
        """
        try:
            # Limit comments for context
            top_comments = existing_comments[:10]
            
            prompt = f"""Analyze this LinkedIn post and its comments:

POST CONTENT:
{post.get('content', '')[:1000]}

TOP COMMENTS ({len(top_comments)}):
{self._format_comments(top_comments)}

Engagement: {post.get('likes_count', 0)} likes, {post.get('comments_count', 0)} comments

Provide analysis in JSON format:
{{
    "main_topic": "concise topic description",
    "sentiment": "positive/neutral/negative/mixed",
    "key_points": ["point1", "point2"],
    "engagement_type": "congratulatory/advice-seeking/opinion/announcement/question",
    "comment_themes": ["theme1", "theme2"]
}}"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            logger.error(f"Error analyzing post context: {str(e)}")
            return {}
    
    def _build_style_analysis_prompt(
        self, 
        user_data: Dict, 
        comments: List[Dict]
    ) -> str:
        """Build comprehensive prompt for style analysis"""
        
        comments_text = "\n\n".join([
            f"Comment: {c.get('comment_text', '')}\nContext: {c.get('post_context', '')}"
            for c in comments[:20]  # Limit to recent 20
        ])
        
        return f"""Analyze this user's LinkedIn writing style based on their profile and comments:

USER PROFILE:
Name: {user_data.get('name')}
Headline: {user_data.get('headline')}
About: {user_data.get('about', '')[:300]}

RECENT COMMENTS:
{comments_text if comments_text else "No comment history available"}

Analyze their writing style and provide detailed insights in JSON format:
{{
    "tone": "professional|casual|enthusiastic|technical|supportive",
    "formality_score": 0.7,  // 0-1 scale, higher = more formal
    "avg_comment_length": 45,  // average word count
    "emoji_usage": "none|low|moderate|high",
    "common_phrases": ["phrase1", "phrase2"],  // phrases they commonly use
    "engagement_patterns": {{
        "asks_questions": true,
        "shares_experiences": true,
        "gives_advice": false,
        "uses_hashtags": false,
        "tags_people": false
    }},
    "personality_traits": ["supportive", "analytical"],  // 2-4 traits
    "comment_structure": "opinion_first|question_first|agreement_first|story_telling",
    "vocabulary_complexity": "simple|moderate|advanced",
    "typical_comment_openings": ["opening1", "opening2"]  // how they typically start comments
}}

Be specific and accurate based on the actual data provided."""
    
    def _format_experience(self, experience: List[Dict]) -> str:
        """Format experience for prompt"""
        return "\n".join([
            f"- {exp.get('title')} at {exp.get('company')}"
            for exp in experience
        ])
    
    def _format_comments(self, comments: List[Dict]) -> str:
        """Format comments for prompt"""
        return "\n".join([
            f"• {c.get('comment_text', '')[:150]}..."
            for c in comments
        ])
    
    def _default_writing_style(self) -> Dict:
        """Return default style when analysis fails"""
        return {
            "tone": "professional",
            "formality_score": 0.6,
            "avg_comment_length": 50,
            "emoji_usage": "low",
            "common_phrases": [],
            "engagement_patterns": {
                "asks_questions": False,
                "shares_experiences": False,
                "gives_advice": False,
                "uses_hashtags": False,
                "tags_people": False
            },
            "personality_traits": ["professional"],
            "comment_structure": "opinion_first",
            "vocabulary_complexity": "moderate",
            "typical_comment_openings": []
        }