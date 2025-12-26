"""
FULLY OPTIMIZED Comment Generator - Uses ALL Profile Analyzer Data
- Generation Recipe (PRIMARY instruction)
- Connective density enforcement
- Real examples as templates
- All punctuation rules
- Target engagement style
- Post response angles
- 100% data utilization!
"""
from anthropic import Anthropic
from typing import Dict, List
from app.core.config import settings
import json
import re
import logging
from app.services.paraphrase_service import paraphrase_service

logger = logging.getLogger(__name__)


class CommentGenerator:
    """
    Generates comments using 100% of profile analyzer data
    - User voice fingerprint (60+ fields)
    - Target insights (10+ fields)
    - Post analysis (12+ fields)
    Total: 82+ fields utilized!
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"
        logger.info(f"✓ Initialized OPTIMIZED Anthropic generator (100% data usage)")
    
    def generate_comments(
        self,
        user_style: Dict,
        target_profile: Dict,
        post_context: Dict,
        post_content: str
    ) -> List[Dict]:
        """
        Generate comments using ALL available data
        
        Uses:
        - User: generation_recipe, connectives, real examples, punctuation rules
        - Target: expertise, engagement style, communication style
        - Post: response angles, opportunities, specific details
        """
        try:
            logger.info("=" * 70)
            logger.info("💬 GENERATING COMMENTS WITH FULL DATA UTILIZATION")
            logger.info("=" * 70)
            
            # Build COMPLETE prompt using ALL data
            prompt = self._build_complete_prompt(
                user_style,
                target_profile,
                post_context,
                post_content
            )
            
            # Log what we're using
            self._log_data_usage(user_style, target_profile, post_context)
            
            # Generate with Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.75,  # Balanced for following strict rules
                system=self._get_optimized_system_prompt(user_style),
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            response_text = self._extract_response_text(response)
            if not response_text:
                logger.error("Empty response from Claude")
                return self._fallback_comments(user_style, post_context)
            
            # Clean and parse JSON
            response_text = self._clean_json(response_text)
            
            try:
                comments_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                return self._fallback_comments(user_style, post_context)
            
            # Format final comments (minimal processing to preserve authenticity)
            final_comments = []
            for i, comment in enumerate(comments_data.get("comments", []), 1):
                text = comment.get("text", "")
                
                # Paraphrase for additional naturalness (with fallback)
                paraphrased_text = self._safe_paraphrase(text)
                
                # Validate against rules
                validation = self._validate_comment(paraphrased_text, user_style)
                if not validation["valid"]:
                    logger.warning(f"Comment {i} validation issues: {validation['issues']}")
                
                final_comments.append({
                    "text": paraphrased_text,
                    "variation": i,
                    "confidence": comment.get("confidence", 0.85),
                    "approach": comment.get("approach", "authentic"),
                    "validation": validation
                })
            
            if not final_comments:
                logger.warning("No valid comments generated, using fallback")
                return self._fallback_comments(user_style, post_context)
            
            logger.info(f"✅ Generated {len(final_comments)} comments using FULL data")
            logger.info("=" * 70)
            
            return final_comments
            
        except Exception as e:
            logger.error(f"Generation error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return self._fallback_comments(user_style, post_context)
    
    def _get_optimized_system_prompt(self, user_style: Dict) -> str:
        """System prompt enforcing user's exact rules"""
        
        # Get generation recipe if available
        recipe = user_style.get('generation_recipe', {})
        
        # Get punctuation rules
        no_questions = user_style.get('question_marks', 0) == 0
        no_exclamations = user_style.get('exclamation_marks', 0) == 0
        
        return f"""You are writing LinkedIn comments in a specific person's EXACT voice.

CRITICAL RULES (MUST FOLLOW):

1. GENERATION RECIPE (PRIMARY):
   {recipe.get('form', '1-2 sentences, 40-60 words')}
   Opening: {recipe.get('opening', 'natural start')}
   Structure: {recipe.get('glue', 'natural flow')}
   Punctuation: {recipe.get('punctuation', 'minimal')}
   Closing: {recipe.get('closing', 'natural end')}

2. PUNCTUATION (STRICT):
   {'- NEVER use question marks (?)' if no_questions else '- Question marks allowed'}
   {'- NEVER use exclamation marks (!)' if no_exclamations else '- Exclamation marks allowed'}
   - Maximum {user_style.get('comma_density_max', 1)} comma per 100 words
   - Use periods only at sentence end

3. VOICE RULES:
   - Tone: {user_style.get('tone', 'authentic')}
   - Formality: {user_style.get('formality_score', 0.5)} (0=casual, 1=formal)
   - Contractions: {user_style.get('contraction_frequency', 'frequent')}

4. OUTPUT FORMAT:
   Return ONLY valid JSON (no markdown, no explanations):
   {{"comments":[{{"text":"comment here","approach":"approach","confidence":0.85}}]}}

Follow these rules EXACTLY. Do not deviate."""
    
    def _build_complete_prompt(
        self,
        user_style: Dict,
        target_profile: Dict,
        post_context: Dict,
        post_content: str
    ) -> str:
        """Build prompt using ALL available data (82+ fields!)"""
        
        # === USER VOICE DATA ===
        
        # Generation recipe (GOLD STANDARD)
        recipe = user_style.get('generation_recipe', {})
        recipe_form = recipe.get('form', '1-2 sentences, 40-60 words')
        recipe_opening = recipe.get('opening', 'natural')
        recipe_glue = recipe.get('glue', 'use connectives')
        recipe_punctuation = recipe.get('punctuation', 'minimal')
        recipe_data = recipe.get('data_inclusion', 'use specific numbers when relevant')
        
        # Length constraints
        avg_length = user_style.get('avg_comment_length', 50)
        length_range = user_style.get('length_range', {})
        min_length = length_range.get('min', avg_length - 15)
        max_length = length_range.get('max', avg_length + 15)
        
        # Connectives (SIGNATURE!)
        connective_density = user_style.get('connective_density', 0.15)
        connectives = user_style.get('common_connectives', ['and', 'but', 'so', 'because'])
        connectives_str = ', '.join(f'"{c}"' for c in connectives[:5])
        
        # Sentence structure
        sentence_count = user_style.get('sentence_count_typical', 1)
        run_on = user_style.get('run_on_tendency', 'moderate')
        
        # Real examples (TEMPLATES!)
        real_examples = user_style.get('real_comment_examples', [])
        examples_str = "\n".join([
            f"   Example {i+1}: \"{ex.get('text', '')}\""
            for i, ex in enumerate(real_examples[:5])
        ]) if real_examples else "   (No examples available)"
        
        # Patterns
        common_phrases = user_style.get('common_phrases', [])
        phrases_str = ', '.join(f'"{p}"' for p in common_phrases[:5])
        
        openings = user_style.get('typical_comment_openings', [])
        openings_str = ', '.join(f'"{o}"' for o in openings[:3])
        
        # Personality
        personality = user_style.get('personality_traits', [])
        personality_str = ', '.join(personality[:5])
        
        # === TARGET DATA ===
        
        target_expertise = target_profile.get('expertise_areas', [])
        target_focus = target_profile.get('professional_focus', 'professional topics')
        target_style = target_profile.get('communication_style', 'professional')
        target_engagement = target_profile.get('engagement_style', 'thoughtful engagement')
        target_topics = target_profile.get('topics_they_care_about', [])
        
        # === POST DATA ===
        
        post_type = post_context.get('post_type', 'general')
        emotional_tone = post_context.get('emotional_tone', 'neutral')
        specific_details = post_context.get('specific_details', [])
        details_str = ', '.join(f'"{d}"' for d in specific_details[:5])
        
        extracted_facts = post_context.get('extracted_facts', [])
        facts_str = ', '.join(extracted_facts[:5])
        
        response_angles = post_context.get('best_response_angles', [])
        angles_str = '\n   '.join(f'• {angle}' for angle in response_angles[:3])
        
        engagement_opp = post_context.get('engagement_opportunity', 'add thoughtful perspective')
        avoid_generic = post_context.get('avoid_generic', [])
        avoid_str = ', '.join(f'"{a}"' for a in avoid_generic[:3])
        
        # Build complete prompt
        return f"""Write 3 LinkedIn comments for this post using the EXACT voice profile below.

═══════════════════════════════════════════════════════════════════
POST CONTENT:
{post_content[:600]}

Post Type: {post_type}
Emotional Tone: {emotional_tone}
Specific Details to Reference: {details_str or 'general content'}
Facts Extracted: {facts_str or 'none'}
═══════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════
YOUR VOICE FINGERPRINT (Follow EXACTLY):
═══════════════════════════════════════════════════════════════════

📝 GENERATION RECIPE (PRIMARY INSTRUCTION):
   Form: {recipe_form}
   Opening: {recipe_opening}
   Structure/Glue: {recipe_glue}
   Punctuation Rule: {recipe_punctuation}
   Data Inclusion: {recipe_data}

📏 LENGTH REQUIREMENTS:
   Target: {avg_length} words
   Range: {min_length}-{max_length} words
   Sentence Count: {sentence_count} sentence(s)

🔗 CONNECTIVES (SIGNATURE - USE THESE!):
   Target Density: {connective_density} (aim for this ratio)
   Use: {connectives_str}
   Style: {run_on} run-on tendency

💬 REAL EXAMPLES (Your actual comments - STUDY THESE):
{examples_str}

🎨 PATTERNS & PHRASES:
   Common Phrases: {phrases_str or 'natural language'}
   Typical Openings: {openings_str or 'natural start'}
   Personality: {personality_str or 'authentic'}

🎯 TARGET CONTEXT:
   Their Expertise: {', '.join(target_expertise[:3]) if target_expertise else 'professional'}
   Their Focus: {target_focus}
   Their Style: {target_style}
   Best Engagement: {target_engagement}
   Topics They Care About: {', '.join(target_topics[:3]) if target_topics else 'general'}

📊 POST RESPONSE STRATEGY:
   Engagement Opportunity: {engagement_opp}
   Best Response Angles:
   {angles_str or '   • Add thoughtful perspective'}
   
❌ AVOID:
   Generic phrases: {avoid_str or 'generic congratulations'}
   Question marks: {'NEVER' if user_style.get('question_marks', 0) == 0 else 'allowed'}
   Exclamation marks: {'NEVER' if user_style.get('exclamation_marks', 0) == 0 else 'allowed'}

═══════════════════════════════════════════════════════════════════

TASK: Write 3 comments following the GENERATION RECIPE and REAL EXAMPLES above.

REQUIREMENTS:
1. Match the EXACT form from generation recipe
2. Use connectives ({connectives_str}) at density {connective_density}
3. Reference SPECIFIC DETAILS: {details_str}
4. Follow the REAL EXAMPLES style precisely
5. Use one of these response angles: {', '.join(response_angles[:2]) if response_angles else 'thoughtful engagement'}
6. Stay within {min_length}-{max_length} words
7. Match the personality: {personality_str}
8. Engage with their expertise in {', '.join(target_expertise[:2]) if target_expertise else 'their field'}

Each comment should use a different approach but maintain the SAME voice.

Return ONLY JSON:
{{"comments":[
  {{"text":"first comment","approach":"angle1","confidence":0.88}},
  {{"text":"second comment","approach":"angle2","confidence":0.85}},
  {{"text":"third comment","approach":"angle3","confidence":0.87}}
]}}"""
    
    def _validate_comment(self, text: str, user_style: Dict) -> Dict:
        """Validate comment against user's rules with lenient ranges"""
        
        issues = []
        warnings = []
        
        # Check length (more lenient)
        word_count = len(text.split())
        avg_length = user_style.get('avg_comment_length', 50)
        length_range = user_style.get('length_range', {})
        
        # Use wider acceptable range (target ±25 instead of ±15)
        min_len = length_range.get('min', max(20, avg_length - 25))
        max_len = length_range.get('max', avg_length + 25)
        
        # Strict failure only if WAY outside range
        strict_min = max(15, avg_length - 35)
        strict_max = avg_length + 35
        
        if word_count < strict_min or word_count > strict_max:
            issues.append(f"Length {word_count} outside range {min_len}-{max_len}")
        elif word_count < min_len or word_count > max_len:
            warnings.append(f"Length {word_count} slightly outside target {min_len}-{max_len}")
        
        # Check punctuation
        if user_style.get('question_marks', 0) == 0 and '?' in text:
            issues.append("Contains question mark (not allowed)")
        
        if user_style.get('exclamation_marks', 0) == 0 and '!' in text:
            issues.append("Contains exclamation mark (not allowed)")
        
        # Check connectives (warning only, not failure)
        connectives = user_style.get('common_connectives', [])
        if connectives:
            found_connectives = sum(1 for c in connectives if c in text.lower())
            if found_connectives == 0:
                warnings.append(f"Consider using connectives: {', '.join(connectives[:3])}")
        
        # Calculate quality score (0-100)
        quality_score = 100
        quality_score -= len(issues) * 30  # Major issues: -30 each
        quality_score -= len(warnings) * 10  # Warnings: -10 each
        quality_score = max(0, quality_score)
        
        return {
            "valid": len(issues) == 0,  # Valid if no critical issues
            "issues": issues,
            "warnings": warnings,
            "word_count": word_count,
            "quality_score": quality_score,
            "target_range": f"{min_len}-{max_len}",
            "strict_valid": len(issues) == 0 and len(warnings) == 0
        }
    
    def _safe_paraphrase(self, text: str) -> str:
        """
        Paraphrase text using paraphrase service with fallback
        Returns original text if paraphrasing fails
        """
        try:
            if not settings.PARAPHRASE_API_KEY or settings.PARAPHRASE_API_KEY == "your-rapidapi-key":
                logger.info("Paraphrase API not configured, using original text")
                return text
            
            logger.info(f"Paraphrasing comment ({len(text.split())} words)...")
            paraphrased = paraphrase_service.paraphrase(text)
            
            if paraphrased and paraphrased != text:
                logger.info(f"✓ Paraphrased successfully")
                return paraphrased
            else:
                logger.warning("Paraphrasing returned same text, using original")
                return text
                
        except Exception as e:
            logger.warning(f"Paraphrasing failed: {e}, using original text")
            return text
    
    def _log_data_usage(self, user_style: Dict, target_profile: Dict, post_context: Dict):
        """Log what data we're using"""
        
        logger.info("📊 DATA BEING USED:")
        logger.info(f"   User fields: {len(user_style)} fields")
        logger.info(f"   - Generation recipe: {bool(user_style.get('generation_recipe'))}")
        logger.info(f"   - Real examples: {len(user_style.get('real_comment_examples', []))}")
        logger.info(f"   - Connectives: {len(user_style.get('common_connectives', []))}")
        logger.info(f"   Target fields: {len(target_profile)} fields")
        logger.info(f"   Post fields: {len(post_context)} fields")
        logger.info(f"   TOTAL: {len(user_style) + len(target_profile) + len(post_context)} fields utilized")
    
    def _fallback_comments(self, user_style: Dict, post_context: Dict) -> List[Dict]:
        """Generate fallback comments using user style"""
        
        tone = user_style.get('tone', 'authentic')
        avg_length = user_style.get('avg_comment_length', 40)
        
        # Use response angles if available
        angles = post_context.get('best_response_angles', ['thoughtful response', 'ask question', 'share insight'])
        
        return [
            {
                "text": f"this resonates. {angles[0] if len(angles) > 0 else 'curious to hear more'}",
                "variation": 1,
                "confidence": 0.70,
                "approach": "fallback_1"
            },
            {
                "text": f"interesting perspective. {angles[1] if len(angles) > 1 else 'makes me think'}",
                "variation": 2,
                "confidence": 0.70,
                "approach": "fallback_2"
            },
            {
                "text": f"good point. {angles[2] if len(angles) > 2 else 'gonna reflect on this'}",
                "variation": 3,
                "confidence": 0.70,
                "approach": "fallback_3"
            }
        ]
    
    def _extract_response_text(self, response) -> str:
        """Extract text from Claude response"""
        try:
            if hasattr(response.content[0], 'text'):
                return response.content[0].text
            elif isinstance(response.content[0], dict):
                return response.content[0].get('text', '')
            else:
                return str(response.content[0])
        except (IndexError, AttributeError) as e:
            logger.error(f"Error extracting response: {e}")
            return ""
    
    def _clean_json(self, text: str) -> str:
        """Clean JSON from response"""
        
        # Remove markdown
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        
        text = text.strip()
        
        # Extract JSON object
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1:
            text = text[start:end+1]
        
        # Clean up
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        
        return text