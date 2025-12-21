"""
Profile Analyzer Service
Analyzes user profiles and writing styles using Gemini (FREE)
"""
import google.generativeai as genai
from typing import Dict, List
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)


class ProfileAnalyzer:
    """Analyzes profiles and extracts writing patterns using Gemini 2.5"""
    
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Use Pro/Flash for deep analysis and personalization
        self.model = genai.GenerativeModel(settings.GEMINI_ANALYSIS_MODEL)
    
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
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=2048,
                    candidate_count=1,
                ),
                safety_settings={
                    'HARASSMENT': 'block_none',
                    'HATE_SPEECH': 'block_none', 
                    'SEXUALLY_EXPLICIT': 'block_none',
                    'DANGEROUS_CONTENT': 'block_none',
                }
            )
            
            # Get complete response text
            try:
                response_text = response.text
                
                # Check if response was truncated
                if hasattr(response, 'candidates') and len(response.candidates) > 0:
                    finish_reason = response.candidates[0].finish_reason
                    if finish_reason != 1:  # 1 = STOP (natural completion)
                        logger.warning(f"Response incomplete, finish_reason: {finish_reason}")
                        # Try to use partial response anyway
                        
            except ValueError as e:
                # Response was blocked or incomplete
                logger.error(f"Response blocked or incomplete: {e}")
                logger.error(f"Candidates: {response.candidates if hasattr(response, 'candidates') else 'N/A'}")
                return self._default_writing_style()
            
            # Clean markdown formatting
            response_text = self._clean_json_response(response_text)
            
            try:
                analysis = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                logger.error(f"Response text: {response_text[:500]}")
                return self._default_writing_style()
            
            logger.info("✓ User writing style analyzed successfully")
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

Analyze expertise. Return COMPACT JSON (single line, no formatting):
{{"expertise_areas":["area1","area2"],"professional_focus":"description","communication_style":"style","key_themes":["theme1","theme2"]}}

CRITICAL: Output MUST be single-line compact JSON. No pretty printing. No line breaks inside JSON."""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1536,
                )
            )
            
            response_text = response.text
            response_text = self._clean_json_response(response_text)
            
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                logger.error(f"Response text: {response_text[:500]}")
                return {
                    "expertise_areas": ["professional"],
                    "professional_focus": "career development",
                    "communication_style": "professional",
                    "key_themes": ["work", "growth"]
                }
            
            logger.info("✓ Target profile analyzed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing target profile: {str(e)}")
            return {
                "expertise_areas": ["professional"],
                "professional_focus": "career development",
                "communication_style": "professional",
                "key_themes": ["work", "growth"]
            }
    
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
            
            prompt = f"""Analyze this LinkedIn post briefly.

POST: {post.get('content', '')[:600]}
ENGAGEMENT: {post.get('likes_count', 0)} likes, {post.get('comments_count', 0)} comments

Return compact JSON (single line):
{{"post_type":"type","main_topic":"topic","sentiment":"positive","tone":"professional","key_points":["point1","point2"],"recommended_strategy":"strategy","recommended_length":"1 paragraph"}}

Be brief. Single-line JSON only."""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1536,
                )
            )
            
            response_text = response.text
            response_text = self._clean_json_response(response_text)
            
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                logger.error(f"Response text: {response_text[:500]}")
                return {
                    "post_type": "professional discussion",
                    "main_topic": "professional discussion",
                    "sentiment": "positive",
                    "tone": "professional",
                    "key_points": ["insight", "experience"],
                    "recommended_strategy": "add value with specific insight",
                    "recommended_length": "1 paragraph"
                }
            
            logger.info("✓ Post context analyzed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing post context: {str(e)}")
            return {
                "main_topic": "professional discussion",
                "sentiment": "positive",
                "key_points": ["insight", "experience"],
                "engagement_type": "opinion",
                "comment_themes": ["support", "agreement"]
            }
    
    def _build_style_analysis_prompt(
        self, 
        user_data: Dict, 
        comments: List[Dict]
    ) -> str:
        """Build streamlined prompt for style analysis"""
        
        comments_text = "\n\n".join([
            f"Example {i+1}: \"{c.get('comment_text', '')}\""
            for i, c in enumerate(comments[:8])  # Reduced to 8 for faster processing
        ])
        
        return f"""Analyze this LinkedIn user's writing style from their comments.

USER: {user_data.get('name')}
ROLE: {user_data.get('headline')}

COMMENTS:
{comments_text if comments_text else "Limited samples - analyze profile text"}

Provide analysis as COMPACT single-line JSON (no markdown, no pretty printing):
{{"tone":"professional","formality_score":0.7,"avg_comment_length":50,"sentence_length_variation":"high","emoji_usage":"low","common_phrases":["a","b"],"engagement_patterns":{{"asks_questions":true,"shares_experiences":false}},"personality_traits":["trait1"],"typical_comment_openings":["op1"],"contraction_frequency":"occasional","burstiness_level":"high"}}

CRITICAL: Single line JSON only. No formatting. No line breaks."""

    
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
    
    def _clean_json_response(self, text: str) -> str:
        """Clean and repair JSON response from LLM"""
        import re
        
        # Remove markdown code blocks
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        
        # Strip whitespace
        text = text.strip()
        
        # Remove any text before first { and after last }
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1:
            text = text[start:end+1]
        elif start != -1:
            # No closing brace - response was truncated
            text = text[start:]
            
            # Find last complete key-value pair
            # Strategy: find last valid comma or opening brace
            last_complete = max(
                text.rfind('",'),  # Last complete string value
                text.rfind('},'),  # Last complete object
                text.rfind('],'),  # Last complete array
                text.rfind('{')    # Just the opening
            )
            
            if last_complete > 0:
                text = text[:last_complete+1]
                
                # If we ended with a comma, remove it
                text = text.rstrip(',').rstrip()
                
                # Close any open structures
                open_braces = text.count('{') - text.count('}')
                open_brackets = text.count('[') - text.count(']')
                
                for _ in range(open_brackets):
                    text += ']'
                for _ in range(open_braces):
                    text += '}'
        
        # Remove trailing commas
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        
        return text