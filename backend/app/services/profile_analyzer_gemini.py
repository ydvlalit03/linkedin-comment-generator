"""
Complete Profile Analyzer - 3-Stage Intelligent System
STAGE 1: Deep User Analysis (JSON + LLM)
STAGE 2: Target + Post Analysis (Scrapped data + LLM)  
STAGE 3: Ready for Comment Generation
"""
import google.generativeai as genai
from typing import Dict, List
from app.core.config import settings
import json
import logging
import re

logger = logging.getLogger(__name__)


class ProfileAnalyzer:
    """
    🎯 Three-Stage Analysis System:
    
    STAGE 1: USER ANALYSIS
    - Input: JSON profile + real comments
    - Process: Load JSON data + LLM deep analysis
    - Output: Complete user voice fingerprint
    
    STAGE 2: TARGET + POST ANALYSIS  
    - Input: Target profile + scrapped posts
    - Process: LLM analyzes expertise, post content, engagement opportunities
    - Output: Target insights + post context
    
    STAGE 3: READY FOR GENERATION
    - Comment generator uses both analyses
    """
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_ANALYSIS_MODEL)
        logger.info("✓ ProfileAnalyzer ready - 3-stage intelligent analysis")
    
    # ==========================================
    # STAGE 1: DEEP USER ANALYSIS
    # ==========================================
    
    def analyze_user_writing_style(
        self, 
        user_data: Dict, 
        user_comments: List[Dict]
    ) -> Dict:
        """
        🎯 STAGE 1: Deep User Analysis
        
        Combines:
        1. ALL data from JSON profile (if available)
        2. LLM deep analysis of voice patterns
        3. Merges into complete user fingerprint
        """
        try:
            logger.info("=" * 60)
            logger.info("🔍 STAGE 1: DEEP USER ANALYSIS STARTING...")
            logger.info("=" * 60)
            
            # Load JSON profile data
            json_profile = self._load_json_profile(user_data)
            
            # LLM analyzes voice patterns
            llm_insights = self._llm_analyze_user_voice(user_data, user_comments, json_profile)
            
            # Merge for complete profile
            complete_profile = self._merge_user_analysis(json_profile, llm_insights)
            
            logger.info("✅ STAGE 1 COMPLETE: User voice profile ready")
            logger.info(f"   Voice: {complete_profile.get('voice_archetype', 'analyzed')}")
            logger.info(f"   Length: {complete_profile.get('avg_comment_length')} words")
            logger.info(f"   Examples: {len(complete_profile.get('real_comment_examples', []))}")
            logger.info("=" * 60)
            
            return complete_profile
            
        except Exception as e:
            logger.error(f"STAGE 1 ERROR: {str(e)}")
            return self._default_user_profile()
    
    def _load_json_profile(self, user_data: Dict) -> Dict:
        """Load complete JSON profile"""
        
        if self._has_complete_json(user_data):
            logger.info("📄 Found COMPLETE JSON profile - loading all data...")
            
            return {
                "has_json": True,
                "basic_info": user_data.get('basic_info', {}),
                "voice": user_data.get('core_voice_fingerprint', {}),
                "rhythm": user_data.get('rhythm_metrics', {}),
                "lexical": user_data.get('lexical_signature', {}),
                "cohesion": user_data.get('cohesion_signature', {}),
                "generation_recipe": user_data.get('generation_recipe', {}),
                "real_examples": user_data.get('real_comment_examples', []),
                "phrases": user_data.get('common_phrases', []),
                "openings": user_data.get('opening_patterns', []),
                "personality": user_data.get('personality_traits', []),
                "engagement": user_data.get('engagement_patterns', {})
            }
        else:
            logger.info("⚠️ No complete JSON - will rely on LLM analysis")
            return {
                "has_json": False,
                "name": user_data.get('name', '')
            }
    
    def _has_complete_json(self, data: Dict) -> bool:
        """Check for complete JSON"""
        required = ['basic_info', 'core_voice_fingerprint', 'rhythm_metrics', 'generation_recipe']
        return all(s in data for s in required)
    
    def _llm_analyze_user_voice(self, user_data: Dict, comments: List[Dict], json_profile: Dict) -> Dict:
        """LLM deep analysis of user voice"""
        
        comments_text = "\n\n".join([
            f"Comment {i+1}: \"{c.get('comment_text', '')}\""
            for i, c in enumerate(comments[:10])
        ])
        
        json_context = ""
        if json_profile.get('has_json'):
            json_context = f"""
EXISTING PROFILE DATA (reference):
- Voice: {json_profile.get('basic_info', {}).get('voice_archetype', 'unknown')}
- Tone: {json_profile.get('voice', {}).get('tone', 'unknown')}
- Recipe: {json_profile.get('generation_recipe', {}).get('form', 'unknown')}
"""
        
        prompt = f"""Analyze this user's writing voice with deep understanding.

USER: {user_data.get('name', 'User')}
{json_context}

COMMENTS:
{comments_text or "Limited samples"}

Identify unique voice characteristics. Analyze:
1. Sentence rhythm & structure
2. Word choice & formality
3. Emotional tone
4. Opening patterns
5. How they connect ideas
6. Use of data/examples
7. Punctuation style
8. Unique quirks

Return JSON:
{{
  "voice_tone": "their natural tone",
  "sentence_rhythm": "their sentence patterns",
  "formality_level": 0.0-1.0,
  "avg_length_words": number,
  "unique_patterns": ["pattern1", "pattern2"],
  "signature_phrases": ["phrase1", "phrase2"],
  "opening_style": "how they start",
  "connective_style": "how they link ideas",
  "uses_data": true|false,
  "uses_questions": true|false,
  "distinctive_markers": ["what makes them unique"]
}}

Base on ACTUAL comments."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1500,
                )
            )
            
            insights = json.loads(self._clean_json(response.text))
            logger.info(f"✓ LLM found {len(insights.get('unique_patterns', []))} unique patterns")
            return insights
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {}
    
    def _merge_user_analysis(self, json_profile: Dict, llm: Dict) -> Dict:
        """Merge JSON + LLM into complete profile"""
        
        if json_profile.get('has_json'):
            # Use rich JSON as base
            rhythm = json_profile.get('rhythm', {})
            cohesion = json_profile.get('cohesion', {})
            
            return {
                # From JSON
                "name": json_profile.get('basic_info', {}).get('name', ''),
                "voice_archetype": json_profile.get('basic_info', {}).get('voice_archetype', ''),
                "tone": json_profile.get('voice', {}).get('tone', ''),
                "formality_score": json_profile.get('voice', {}).get('formality_score', 0.5),
                
                "avg_comment_length": rhythm.get('sentence_length_mean_words', {}).get('target', 50),
                "length_range": {
                    "min": rhythm.get('sentence_length_mean_words', {}).get('min', 30),
                    "max": rhythm.get('sentence_length_mean_words', {}).get('max', 70)
                },
                "burstiness_level": rhythm.get('burstiness_level', 'moderate'),
                "connective_density": cohesion.get('connective_density', {}).get('target', 0.15),
                "common_connectives": cohesion.get('discourse_marker_variety', {}).get('common_markers', []),
                
                "generation_recipe": json_profile.get('generation_recipe', {}),
                "real_comment_examples": json_profile.get('real_examples', []),
                "common_phrases": json_profile.get('phrases', []),
                "typical_comment_openings": json_profile.get('openings', []),
                "personality_traits": json_profile.get('personality', []),
                "engagement_patterns": json_profile.get('engagement', {}),
                
                # From LLM
                "llm_insights": llm.get('unique_patterns', []),
                "llm_markers": llm.get('distinctive_markers', []),
                
                "profile_source": "complete_json_plus_llm",
                "confidence": "very_high"
            }
        else:
            # LLM only
            return {
                "tone": llm.get('voice_tone', 'professional'),
                "formality_score": llm.get('formality_level', 0.5),
                "avg_comment_length": llm.get('avg_length_words', 40),
                "unique_patterns": llm.get('unique_patterns', []),
                "typical_comment_openings": [llm.get('opening_style', '')],
                "profile_source": "llm_only",
                "confidence": "moderate"
            }
    
    # ==========================================
    # STAGE 2A: TARGET ANALYSIS
    # ==========================================
    
    def analyze_target_profile(self, target_data: Dict) -> Dict:
        """
        🎯 STAGE 2A: Target Profile Analysis
        
        Analyzes:
        - Expertise & focus areas
        - Communication style
        - Key themes & values
        - Best engagement approach
        """
        try:
            logger.info("=" * 60)
            logger.info("🔍 STAGE 2A: TARGET ANALYSIS STARTING...")
            logger.info(f"   Target name: {target_data.get('name', 'Unknown')}")
            logger.info("=" * 60)
            
            facts = self._extract_target_facts(target_data)
            logger.info(f"   Extracted {len(facts)} facts from profile")
            
            # Build prompt with all available data
            prompt = f"""Analyze this LinkedIn profile deeply.

NAME: {target_data.get('name', 'Professional')}
HEADLINE: {target_data.get('headline', 'N/A')}

ABOUT:
{target_data.get('about', 'N/A')[:800]}

EXPERIENCE:
{self._format_experience(target_data.get('experience', [])[:5])}

EXTRACTED FACTS: {', '.join(facts) if facts else 'Limited info'}

Analyze:
1. Expertise areas (specific domains)
2. Professional focus/mission
3. Communication style
4. Key themes they discuss
5. Best engagement approach

Return JSON:
{{
  "expertise_areas": ["area1", "area2"],
  "professional_focus": "their main focus",
  "communication_style": "their style",
  "key_themes": ["theme1", "theme2"],
  "industry": "industry",
  "seniority": "mid|senior|executive",
  "engagement_style": "how to engage",
  "topics_they_care_about": ["topic1", "topic2"]
}}

Base analysis on ACTUAL profile content provided above."""

            logger.info("   Calling Gemini for target analysis...")
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1500,
                )
            )
            
            analysis = json.loads(self._clean_json(response.text))
            
            logger.info("✅ STAGE 2A COMPLETE: Target analyzed")
            logger.info(f"   Expertise: {', '.join(analysis.get('expertise_areas', [])[:2])}")
            logger.info(f"   Focus: {analysis.get('professional_focus', 'Unknown')[:50]}")
            logger.info("=" * 60)
            
            return analysis
            
        except Exception as e:
            logger.error(f"STAGE 2A ERROR: {e}")
            logger.error(f"Returning default target profile")
            import traceback
            logger.error(traceback.format_exc())
            return self._default_target()
    
    # ==========================================
    # STAGE 2B: POST ANALYSIS
    # ==========================================
    
    def analyze_post_context(self, post: Dict, comments: List[Dict]) -> Dict:
        """
        🎯 STAGE 2B: Post Content Analysis
        
        Analyzes:
        - Post type & topic
        - Emotional tone
        - Specific details to reference
        - Engagement opportunities
        """
        try:
            logger.info("=" * 60)
            logger.info("🔍 STAGE 2B: POST ANALYSIS STARTING...")
            logger.info("=" * 60)
            
            content = post.get('content', '')
            facts = self._extract_post_facts(content)
            
            prompt = f"""Analyze this LinkedIn post deeply.

POST:
{content[:1000]}

ENGAGEMENT: {post.get('likes_count', 0)} likes, {post.get('comments_count', 0)} comments

FACTS: {', '.join(facts)}

Analyze:
1. Post type
2. Core message  
3. Emotional tone
4. Specific details mentioned
5. Best response angle

Return JSON:
{{
  "post_type": "achievement",
  "core_message": "main point",
  "main_topic": "topic",
  "emotional_tone": "emotion",
  "sentiment": "positive",
  "specific_details": ["detail1", "detail2"],
  "key_moments": ["moment1"],
  "engagement_opportunity": "how to add value",
  "best_response_angles": ["angle1", "angle2"],
  "extracted_facts": {json.dumps(facts)}
}}"""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1500,
                )
            )
            
            analysis = json.loads(self._clean_json(response.text))
            analysis['extracted_facts'] = facts
            
            logger.info("✅ STAGE 2B COMPLETE: Post analyzed")
            logger.info(f"   Type: {analysis.get('post_type')}")
            logger.info(f"   Topic: {analysis.get('main_topic')}")
            logger.info(f"   Details: {len(analysis.get('specific_details', []))}")
            logger.info("=" * 60)
            
            return analysis
            
        except Exception as e:
            logger.error(f"STAGE 2B ERROR: {e}")
            return self._default_post([])
    
    # ==========================================
    # HELPERS
    # ==========================================
    
    def _extract_target_facts(self, data: Dict) -> List[str]:
        """Extract facts from target"""
        facts = []
        
        headline = data.get('headline', '')
        titles = ['CEO', 'CTO', 'VP', 'Director', 'Manager', 'Founder']
        for t in titles:
            if t.lower() in headline.lower():
                facts.append(f"Title: {t}")
                break
        
        exp = data.get('experience', [])
        if exp:
            company = exp[0].get('company', '')
            if company:
                facts.append(f"Company: {company}")
        
        return facts[:5]
    
    def _extract_post_facts(self, content: str) -> List[str]:
        """Extract facts from post"""
        facts = []
        
        # Numbers
        numbers = re.findall(r'\$?\d+[KMB%]?', content)
        facts.extend([f"metric: {n}" for n in numbers[:4]])
        
        # List items
        items = re.findall(r'[\d]+[.)\-]\s*([^\n]{10,60})', content)
        facts.extend([f"point: {i[:35]}" for i in items[:3]])
        
        # Questions
        questions = re.findall(r'([^.!?]{10,70}\?)', content)
        if questions:
            facts.append(f"asks: {questions[0][:50]}")
        
        return facts[:8]
    
    def _format_experience(self, exp: List[Dict]) -> str:
        """Format experience"""
        return "\n".join([
            f"- {e.get('title', 'Role')} at {e.get('company', 'Company')}"
            for e in exp[:5]
        ])
    
    def _clean_json(self, text: str) -> str:
        """Clean JSON with robust error handling"""
        if not text or not text.strip():
            logger.error("Empty response from LLM")
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
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)  # Remove control chars
        text = text.replace('\\"', '"')  # Fix escaped quotes
        
        return text
    
    def _default_user_profile(self) -> Dict:
        return {"tone": "professional", "avg_comment_length": 40, "profile_source": "default"}
    
    def _default_target(self) -> Dict:
        return {"expertise_areas": ["professional"], "professional_focus": "career", "industry": "business"}
    
    def _default_post(self, facts: List[str]) -> Dict:
        return {"post_type": "general", "main_topic": "discussion", "extracted_facts": facts}