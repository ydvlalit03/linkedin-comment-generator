"""
Complete Profile Analyzer - Anthropic Claude with Extended Thinking
Uses Claude Opus 4 with extended thinking for deepest analysis
STAGE 1: Deep User Analysis (JSON + Extended Thinking LLM)
STAGE 2: Target + Post Analysis (Scrapped data + Extended Thinking)
STAGE 3: Ready for Comment Generation
"""
from anthropic import Anthropic
from typing import Dict, List, Optional
from app.core.config import settings
import json
import logging
import re

logger = logging.getLogger(__name__)


class ProfileAnalyzer:
    """
    🎯 Three-Stage Analysis System with Anthropic Extended Thinking:
    
    STAGE 1: USER ANALYSIS
    - Input: JSON profile + real comments
    - Process: Load JSON data + Claude Opus 4 deep analysis with extended thinking
    - Output: Complete user voice fingerprint (60+ fields)
    
    STAGE 2: TARGET + POST ANALYSIS
    - Input: Target profile + scrapped posts
    - Process: Claude analyzes expertise, post content, engagement opportunities
    - Output: Target insights (10+ fields) + post context (12+ fields)
    
    STAGE 3: READY FOR GENERATION
    - Comment generator uses all 82+ fields
    
    Uses Extended Thinking for:
    - Deeper pattern recognition
    - More nuanced voice analysis
    - Better context understanding
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        # Claude Opus 4 for best analysis quality
        self.model = "claude-opus-4-20250514"
        logger.info(f"✓ ProfileAnalyzer ready - Anthropic Claude Opus 4 with extended thinking")
    
    # ==========================================
    # STAGE 1: DEEP USER ANALYSIS
    # ==========================================
    
    def analyze_user_writing_style(
        self, 
        user_data: Dict, 
        user_comments: List[Dict]
    ) -> Dict:
        """
        🎯 STAGE 1: Deep User Analysis with Extended Thinking
        
        Combines:
        1. ALL data from JSON profile (if available)
        2. Claude Opus 4 deep analysis with extended thinking
        3. Merges into complete user fingerprint
        """
        try:
            logger.info("=" * 60)
            logger.info("🔍 STAGE 1: DEEP USER ANALYSIS STARTING (Claude Opus 4)...")
            logger.info("=" * 60)
            
            # Load JSON profile data
            json_profile = self._load_json_profile(user_data)
            
            # Claude analyzes voice patterns with extended thinking
            llm_insights = self._claude_analyze_user_voice(user_data, user_comments, json_profile)
            
            # Merge for complete profile
            complete_profile = self._merge_user_analysis(json_profile, llm_insights)
            
            logger.info("✅ STAGE 1 COMPLETE: User voice profile ready")
            logger.info(f"   Voice: {complete_profile.get('voice_archetype', 'analyzed')}")
            logger.info(f"   Length: {complete_profile.get('avg_comment_length')} words")
            logger.info(f"   Examples: {len(complete_profile.get('real_comment_examples', []))}")
            logger.info(f"   Confidence: {complete_profile.get('confidence', 0.9):.2f}")
            logger.info("=" * 60)
            
            return complete_profile
            
        except Exception as e:
            logger.error(f"STAGE 1 ERROR: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return self._default_user_profile()
    
    def _load_json_profile(self, user_data: Dict) -> Dict:
        """Load complete JSON profile data if available"""
        
        if not user_data:
            logger.info("   No user data provided")
            return {}
        
        # Check if this is a complete JSON profile
        has_complete_profile = any(key in user_data for key in [
            'basic_info', 'core_voice_fingerprint', 'rhythm_metrics', 
            'generation_recipe', 'real_comment_examples'
        ])
        
        if has_complete_profile:
            logger.info("   📄 Found COMPLETE JSON profile - loading all data...")
            
            # Extract all the rich data
            profile = {}
            
            # Basic info
            basic_info = user_data.get('basic_info', {})
            profile['voice_archetype'] = basic_info.get('voice_archetype', 'professional')
            profile['confidence_level'] = basic_info.get('confidence_level', 'moderate')
            
            # Core voice
            core_voice = user_data.get('core_voice_fingerprint', {})
            profile['tone'] = core_voice.get('tone', 'professional')
            profile['formality_score'] = core_voice.get('formality_score', 0.5)
            
            # Rhythm metrics
            rhythm = user_data.get('rhythm_metrics', {})
            sentence_length = rhythm.get('sentence_length_mean_words', {})
            profile['avg_comment_length'] = sentence_length.get('target', 50)
            profile['length_range'] = {
                'min': sentence_length.get('min', 35),
                'max': sentence_length.get('max', 65)
            }
            profile['sentence_count_typical'] = rhythm.get('sentence_count_distribution', {}).get('mode', 1)
            profile['burstiness_level'] = rhythm.get('burstiness_level', 'moderate')
            
            # Generation recipe (GOLD!)
            profile['generation_recipe'] = user_data.get('generation_recipe', {})
            
            # Connectives
            profile['connective_density'] = user_data.get('connective_density', 0.15)
            profile['common_connectives'] = user_data.get('common_connectives', [])
            
            # Real examples (GOLD!)
            profile['real_comment_examples'] = user_data.get('real_comment_examples', [])
            
            # Patterns
            profile['common_phrases'] = user_data.get('common_phrases', [])
            profile['typical_comment_openings'] = user_data.get('typical_comment_openings', [])
            
            # Punctuation
            profile['question_marks'] = user_data.get('question_marks', 0)
            profile['exclamation_marks'] = user_data.get('exclamation_marks', 0)
            profile['comma_density_max'] = user_data.get('comma_density_max', 0.02)
            
            # Style markers
            profile['personality_traits'] = user_data.get('personality_traits', [])
            profile['lexical_density'] = user_data.get('lexical_density', {})
            
            logger.info(f"   ✓ Loaded {len(profile)} fields from JSON")
            return profile
        else:
            logger.info("   Simple profile data - will rely more on LLM analysis")
            return {}
    
    def _claude_analyze_user_voice(
        self, 
        user_data: Dict, 
        user_comments: List[Dict],
        json_profile: Dict
    ) -> Dict:
        """
        Use Claude Opus 4 with extended thinking to analyze user voice
        Extended thinking gives deeper, more nuanced analysis
        """
        
        # Extract comment texts
        comment_texts = []
        for comment in user_comments[:8]:  # Analyze up to 8 comments
            if isinstance(comment, dict):
                comment_texts.append(comment.get('comment_text', ''))
            else:
                comment_texts.append(str(comment))
        
        if not comment_texts:
            logger.info("   No comments to analyze, using JSON data only")
            return {}
        
        # Build analysis prompt
        prompt = f"""Analyze this person's LinkedIn commenting voice deeply.

{'='*60}
EXISTING PROFILE DATA (from JSON):
{'='*60}
{json.dumps(json_profile, indent=2) if json_profile else 'None - perform full analysis'}

{'='*60}
REAL COMMENTS TO ANALYZE:
{'='*60}
{chr(10).join(f'{i+1}. "{text}"' for i, text in enumerate(comment_texts))}

{'='*60}
ANALYSIS TASK:
{'='*60}

Think deeply about:
1. What makes this voice UNIQUE and recognizable?
2. What patterns emerge across all comments?
3. What's the underlying personality/archetype?
4. What subtle patterns might be missed in quick analysis?

Return ONLY valid JSON with these insights:

{{
  "discovered_patterns": [
    "specific pattern you noticed"
  ],
  "voice_qualities": {{
    "primary_trait": "main characteristic",
    "secondary_trait": "supporting characteristic",
    "energy_level": "high/moderate/low"
  }},
  "unique_markers": [
    "phrases or patterns that are signature to this voice"
  ],
  "confidence": 0.0-1.0
}}

Use extended thinking to find subtle patterns."""

        try:
            logger.info("   Calling Claude Opus 4 with extended thinking...")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 3000  # Allow deep thinking
                },
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extract response (skip thinking blocks, get final answer)
            response_text = ""
            for block in response.content:
                if block.type == "text":
                    response_text += block.text
            
            # Clean and parse JSON
            response_text = self._clean_json(response_text)
            insights = json.loads(response_text)
            
            logger.info(f"   ✓ Claude found {len(insights.get('discovered_patterns', []))} unique patterns")
            
            return insights
            
        except Exception as e:
            logger.error(f"   Claude analysis error: {e}")
            return {}
    
    def _merge_user_analysis(self, json_profile: Dict, llm_insights: Dict) -> Dict:
        """Merge JSON data with Claude's insights for complete profile"""
        
        complete = json_profile.copy()
        
        # Add Claude's discoveries
        if llm_insights:
            complete['llm_discovered_patterns'] = llm_insights.get('discovered_patterns', [])
            complete['voice_qualities'] = llm_insights.get('voice_qualities', {})
            complete['unique_markers'] = llm_insights.get('unique_markers', [])
            complete['confidence'] = llm_insights.get('confidence', 0.85)
        
        # Set defaults if missing
        if 'avg_comment_length' not in complete:
            complete['avg_comment_length'] = 50
        if 'tone' not in complete:
            complete['tone'] = 'professional'
        
        return complete
    
    # ==========================================
    # STAGE 2: TARGET + POST ANALYSIS
    # ==========================================
    
    def analyze_target_profile(self, target_data: Dict) -> Dict:
        """
        🎯 STAGE 2A: Target Profile Analysis with Extended Thinking
        
        Analyzes:
        - Expertise & focus areas
        - Communication style
        - Key themes & values
        - Best engagement approach
        """
        try:
            logger.info("=" * 60)
            logger.info("🔍 STAGE 2A: TARGET ANALYSIS STARTING (Claude Opus 4)...")
            logger.info(f"   Target name: {target_data.get('name', 'Unknown')}")
            logger.info("=" * 60)
            
            facts = self._extract_target_facts(target_data)
            logger.info(f"   Extracted {len(facts)} facts from profile")
            
            # Build analysis prompt
            prompt = f"""Analyze this LinkedIn profile deeply to understand how to engage with them.

NAME: {target_data.get('name', 'Professional')}
HEADLINE: {target_data.get('headline', 'N/A')}

ABOUT:
{target_data.get('about', 'N/A')[:800]}

EXPERIENCE:
{self._format_experience(target_data.get('experience', [])[:5])}

EXTRACTED FACTS: {', '.join(facts) if facts else 'Limited info'}

Think deeply about:
1. What are their TRUE areas of expertise (not just keywords)?
2. What do they really care about professionally?
3. How do they communicate - formal, casual, data-driven?
4. What would make them engage with a comment?

Return ONLY valid JSON:

{{
  "expertise_areas": ["specific area 1", "specific area 2"],
  "professional_focus": "their main mission/focus",
  "communication_style": "how they communicate",
  "key_themes": ["theme1", "theme2"],
  "industry": "their industry",
  "seniority": "junior/mid/senior/executive",
  "engagement_style": "best way to engage them",
  "topics_they_care_about": ["topic1", "topic2"],
  "values": ["what they value professionally"]
}}

Base analysis on ACTUAL profile content provided above."""

            logger.info("   Calling Claude Opus 4 with extended thinking...")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 2000
                },
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extract text response
            response_text = ""
            for block in response.content:
                if block.type == "text":
                    response_text += block.text
            
            response_text = self._clean_json(response_text)
            analysis = json.loads(response_text)
            
            logger.info("✅ STAGE 2A COMPLETE: Target analyzed")
            logger.info(f"   Expertise: {', '.join(analysis.get('expertise_areas', [])[:2])}")
            logger.info(f"   Focus: {analysis.get('professional_focus', 'Unknown')[:50]}")
            logger.info("=" * 60)
            
            return analysis
            
        except Exception as e:
            logger.error(f"STAGE 2A ERROR: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._default_target()
    
    def analyze_post_context(
        self, 
        post_content: str, 
        existing_comments: List[str] = None
    ) -> Dict:
        """
        🎯 STAGE 2B: Post Context Analysis with Extended Thinking
        
        Analyzes:
        - Post type & topic
        - Emotional tone
        - Key facts & details
        - Best response angles
        """
        try:
            logger.info("=" * 60)
            logger.info("🔍 STAGE 2B: POST ANALYSIS STARTING (Claude Opus 4)...")
            logger.info("=" * 60)
            
            facts = self._extract_post_facts(post_content)
            logger.info(f"   Extracted {len(facts)} facts from post")
            
            prompt = f"""Analyze this LinkedIn post deeply to understand the best way to comment.

POST CONTENT:
{post_content[:1000]}

EXTRACTED FACTS: {', '.join(facts) if facts else 'No specific facts'}

Think deeply about:
1. What is the REAL message/emotion behind this post?
2. What specific details should a great comment reference?
3. What angles would create meaningful engagement?
4. What should be avoided (generic phrases)?

Return ONLY valid JSON:

{{
  "post_type": "achievement/question/insight/story/announcement",
  "core_message": "the real point of the post",
  "main_topic": "specific topic",
  "emotional_tone": "excited/thoughtful/proud/curious/etc",
  "sentiment": "positive/negative/neutral",
  "specific_details": ["detail1", "detail2"],
  "key_moments": ["moment1", "moment2"],
  "author_wants": "what they want from audience",
  "engagement_opportunity": "best way to engage",
  "best_response_angles": ["angle1", "angle2", "angle3"],
  "extracted_facts": {facts},
  "avoid_generic": ["Congratulations!", "Great post!"]
}}"""

            logger.info("   Calling Claude Opus 4 with extended thinking...")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 1500
                },
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extract text response
            response_text = ""
            for block in response.content:
                if block.type == "text":
                    response_text += block.text
            
            response_text = self._clean_json(response_text)
            analysis = json.loads(response_text)
            
            logger.info("✅ STAGE 2B COMPLETE: Post analyzed")
            logger.info(f"   Type: {analysis.get('post_type', 'Unknown')}")
            logger.info(f"   Topic: {analysis.get('main_topic', 'Unknown')[:40]}")
            logger.info(f"   Details: {len(analysis.get('specific_details', []))}")
            logger.info("=" * 60)
            
            return analysis
            
        except Exception as e:
            logger.error(f"STAGE 2B ERROR: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._default_post(facts if 'facts' in locals() else [])
    
    # ==========================================
    # HELPER METHODS
    # ==========================================
    
    def _extract_target_facts(self, data: Dict) -> List[str]:
        """Extract key facts from target profile"""
        facts = []
        
        if data.get('headline'):
            facts.append(f"Headline: {data['headline'][:60]}")
        
        if data.get('about'):
            about = data['about'][:200]
            facts.append(f"About: {about}")
        
        experience = data.get('experience', [])
        if experience:
            for exp in experience[:2]:
                if isinstance(exp, dict):
                    title = exp.get('title', '')
                    company = exp.get('company', '')
                    if title and company:
                        facts.append(f"{title} at {company}")
        
        return facts
    
    def _format_experience(self, experience: List) -> str:
        """Format experience for prompt"""
        if not experience:
            return "No experience data"
        
        formatted = []
        for exp in experience[:3]:
            if isinstance(exp, dict):
                title = exp.get('title', 'Unknown')
                company = exp.get('company', 'Unknown')
                formatted.append(f"- {title} at {company}")
        
        return "\n".join(formatted) if formatted else "No experience data"
    
    def _extract_post_facts(self, content: str) -> List[str]:
        """Extract specific facts from post"""
        facts = []
        
        # Numbers
        numbers = re.findall(r'\b\d+[kKmMbB%]?\b', content)
        facts.extend(numbers[:5])
        
        # Quotes (key phrases)
        quotes = re.findall(r'"([^"]+)"', content)
        facts.extend(quotes[:3])
        
        # Bullet points/lists
        bullets = re.findall(r'[•\-\*]\s*([^\n]+)', content)
        facts.extend(bullets[:3])
        
        return facts
    
    def _clean_json(self, text: str) -> str:
        """Clean JSON with robust error handling"""
        if not text or not text.strip():
            logger.error("Empty response from Claude")
            return "{}"
        
        # Remove markdown
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        
        text = text.strip()
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1:
            text = text[start:end+1]
        else:
            logger.error(f"No JSON found: {text[:100]}")
            return "{}"
        
        # Clean up
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        text = text.replace('\\"', '"')
        
        return text
    
    def _default_user_profile(self) -> Dict:
        return {
            "tone": "professional", 
            "avg_comment_length": 50,
            "confidence": 0.5,
            "profile_source": "default"
        }
    
    def _default_target(self) -> Dict:
        return {
            "expertise_areas": ["professional"], 
            "professional_focus": "career development", 
            "communication_style": "professional",
            "engagement_style": "thoughtful engagement"
        }
    
    def _default_post(self, facts: List[str]) -> Dict:
        return {
            "post_type": "general", 
            "main_topic": "professional discussion",
            "emotional_tone": "neutral",
            "extracted_facts": facts,
            "best_response_angles": ["share perspective", "ask question"]
        }


# Global instance
profile_analyzer = ProfileAnalyzer()