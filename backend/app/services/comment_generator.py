"""
Comment Generator Service
Generates human-like LinkedIn comments using Claude
"""
from anthropic import Anthropic
from typing import Dict, List
from app.core.config import settings
import json
import re
import logging

logger = logging.getLogger(__name__)


class CommentGenerator:
    """Generates authentic LinkedIn comments"""
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL
        self.humanizer = HumanizationEngine()
    
    def generate_comments(
        self,
        user_style: Dict,
        target_profile: Dict,
        post_context: Dict,
        post_content: str
    ) -> List[Dict]:
        """
        Generate 3 comment variations
        
        Returns:
            [
                {
                    "text": str,
                    "variation": int,
                    "confidence": float,
                    "approach": str
                }
            ]
        """
        try:
            # Build comprehensive prompt
            prompt = self._build_generation_prompt(
                user_style, 
                target_profile, 
                post_context, 
                post_content
            )
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            comments_data = json.loads(response.content[0].text)
            
            # Humanize each comment
            humanized_comments = []
            for i, comment in enumerate(comments_data.get("comments", []), 1):
                humanized_text = self.humanizer.humanize(
                    comment["text"],
                    user_style
                )
                
                humanized_comments.append({
                    "text": humanized_text,
                    "variation": i,
                    "confidence": comment.get("confidence", 0.8),
                    "approach": comment.get("approach", "supportive")
                })
            
            return humanized_comments
            
        except Exception as e:
            logger.error(f"Error generating comments: {str(e)}")
            return self._fallback_comments()
    
    def _build_generation_prompt(
        self,
        user_style: Dict,
        target_profile: Dict,
        post_context: Dict,
        post_content: str
    ) -> str:
        """Build the master prompt for comment generation"""
        
        return f"""You are an expert at generating authentic LinkedIn comments that match a specific person's writing style.

USER'S WRITING STYLE ANALYSIS:
- Tone: {user_style.get('tone')}
- Formality: {user_style.get('formality_score')}/1.0
- Average length: {user_style.get('avg_comment_length')} words
- Emoji usage: {user_style.get('emoji_usage')}
- Common phrases: {', '.join(user_style.get('common_phrases', [])[:3])}
- Personality: {', '.join(user_style.get('personality_traits', []))}
- Comment structure: {user_style.get('comment_structure')}
- Vocabulary: {user_style.get('vocabulary_complexity')}
- Typical openings: {', '.join(user_style.get('typical_comment_openings', [])[:2])}
- Engagement patterns: {self._format_engagement_patterns(user_style.get('engagement_patterns', {}))}

TARGET PERSON:
- Name: {target_profile.get('name')}
- Expertise: {', '.join(target_profile.get('expertise_areas', [])[:3])}
- Focus: {target_profile.get('professional_focus')}

POST ANALYSIS:
- Topic: {post_context.get('main_topic')}
- Sentiment: {post_context.get('sentiment')}
- Key points: {', '.join(post_context.get('key_points', [])[:3])}
- Type: {post_context.get('engagement_type')}
- Comment themes: {', '.join(post_context.get('comment_themes', [])[:3])}

POST CONTENT:
{post_content[:800]}

CRITICAL REQUIREMENTS:
1. Generate 3 DIFFERENT comment variations
2. Each comment MUST sound exactly like this user would write it
3. Match their tone, formality, length, and style precisely
4. Use their common phrases naturally if relevant
5. NO AI clichés: avoid "delve into", "navigate", "landscape", "realm", "tapestry"
6. NO corporate jargon unless user commonly uses it
7. Sound 100% human and authentic
8. Length: {max(30, user_style.get('avg_comment_length', 50) - 10)}-{min(150, user_style.get('avg_comment_length', 50) + 20)} words
9. Each variation should take a different approach:
   - Variation 1: Supportive/agreeing
   - Variation 2: Asking a thoughtful question
   - Variation 3: Sharing a brief related insight or experience

Response format (JSON only, no markdown):
{{
    "comments": [
        {{
            "text": "actual comment text here",
            "approach": "supportive",
            "confidence": 0.85
        }},
        {{
            "text": "actual comment text here",
            "approach": "questioning",
            "confidence": 0.82
        }},
        {{
            "text": "actual comment text here",
            "approach": "insightful",
            "confidence": 0.88
        }}
    ]
}}

Generate comments that this person would ACTUALLY write. Be authentic."""
    
    def _format_engagement_patterns(self, patterns: Dict) -> str:
        """Format engagement patterns for prompt"""
        active_patterns = [k.replace('_', ' ') for k, v in patterns.items() if v]
        return ', '.join(active_patterns) if active_patterns else "neutral engagement"
    
    def _fallback_comments(self) -> List[Dict]:
        """Fallback comments when generation fails"""
        return [
            {
                "text": "Great insights! Thanks for sharing your thoughts on this.",
                "variation": 1,
                "confidence": 0.5,
                "approach": "supportive"
            },
            {
                "text": "Interesting perspective. How do you see this evolving in the future?",
                "variation": 2,
                "confidence": 0.5,
                "approach": "questioning"
            },
            {
                "text": "This resonates with my experience. Really valuable post.",
                "variation": 3,
                "confidence": 0.5,
                "approach": "insightful"
            }
        ]


class HumanizationEngine:
    """Makes comments sound more human and less AI-generated"""
    
    # AI detection patterns to remove/replace
    AI_CLICHES = [
        "delve into", "navigate", "landscape", "realm", "tapestry",
        "robust", "dynamic", "leverage", "synergy", "paradigm",
        "it's worth noting", "in today's world", "at the end of the day",
        "game-changer", "cutting-edge", "state-of-the-art"
    ]
    
    def humanize(self, comment: str, user_style: Dict) -> str:
        """Apply humanization techniques"""
        
        # Remove AI clichés
        comment = self._remove_ai_patterns(comment)
        
        # Add user-specific patterns
        comment = self._apply_user_quirks(comment, user_style)
        
        # Add natural imperfections if user has them
        comment = self._add_natural_elements(comment, user_style)
        
        # Validate length
        comment = self._adjust_length(comment, user_style)
        
        return comment.strip()
    
    def _remove_ai_patterns(self, text: str) -> str:
        """Remove common AI writing patterns"""
        for cliche in self.AI_CLICHES:
            # Case-insensitive replacement
            pattern = re.compile(re.escape(cliche), re.IGNORECASE)
            text = pattern.sub("", text)
        
        # Clean up any double spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def _apply_user_quirks(self, comment: str, user_style: Dict) -> str:
        """Add user-specific writing patterns"""
        
        # Add emojis if user uses them
        emoji_usage = user_style.get('emoji_usage', 'none')
        if emoji_usage == 'high' and '!' in comment:
            comment = comment.replace('!', '! 🎯', 1)
        elif emoji_usage == 'moderate' and len(comment) > 50:
            comment += ' 💡'
        
        # Add common phrases naturally
        common_phrases = user_style.get('common_phrases', [])
        if common_phrases and len(comment) < 100:
            # Could add a phrase if relevant
            pass
        
        return comment
    
    def _add_natural_elements(self, comment: str, user_style: Dict) -> str:
        """Add human-like imperfections"""
        
        formality = user_style.get('formality_score', 0.6)
        
        # If casual, allow contractions
        if formality < 0.5:
            comment = comment.replace('cannot', "can't")
            comment = comment.replace('do not', "don't")
            comment = comment.replace('would not', "wouldn't")
        
        return comment
    
    def _adjust_length(self, comment: str, user_style: Dict) -> str:
        """Adjust comment length to match user's typical length"""
        
        words = comment.split()
        target_length = user_style.get('avg_comment_length', 50)
        
        min_length = max(30, target_length - 15)
        max_length = min(150, target_length + 20)
        
        # If too short, it's okay
        # If too long, trim naturally
        if len(words) > max_length:
            # Find a natural breaking point
            truncated = ' '.join(words[:max_length])
            # Try to end at a sentence
            last_period = truncated.rfind('.')
            if last_period > len(truncated) * 0.7:
                comment = truncated[:last_period + 1]
            else:
                comment = truncated
        
        return comment