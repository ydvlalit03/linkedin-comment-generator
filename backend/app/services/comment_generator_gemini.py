"""
Comment Generator Service
Generates human-like LinkedIn comments using Gemini (FREE)
"""
import google.generativeai as genai
from typing import Dict, List
from app.core.config import settings
import json
import re
import logging
import random

logger = logging.getLogger(__name__)


class CommentGenerator:
    """Generates authentic LinkedIn comments using Gemini 2.5 Flash"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Use Flash/Flash-Lite for fast, cheap comment generation
        self.model = genai.GenerativeModel(settings.GEMINI_GENERATION_MODEL)
        self.humanizer = HumanizationEngine()
    
    def generate_comments(
        self,
        user_style: Dict,
        target_profile: Dict,
        post_context: Dict,
        post_content: str
    ) -> List[Dict]:
        """
        Generate 3 comment variations based on post type analysis
        
        STEP 1: Analyze what TYPE of post this is
        STEP 2: Generate 3 variations suited to that type
        
        Returns:
            [
                {
                    "text": str,
                    "variation": int,
                    "confidence": float,
                    "approach": str  # Dynamic based on post type
                }
            ]
        """
        try:
            # STEP 1: Analyze post type and determine appropriate approaches
            post_analysis = self._analyze_post_type(post_content, post_context)
            
            logger.info(f"📊 Post Type: {post_analysis['type']} | Suggested approaches: {post_analysis['approaches']}")
            
            # STEP 2: Build prompt with dynamic approaches
            prompt = self._build_dynamic_generation_prompt(
                user_style, 
                target_profile, 
                post_context, 
                post_content,
                post_analysis
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=settings.TEMPERATURE,
                    max_output_tokens=settings.MAX_TOKENS,
                )
            )
            
            # Parse response
            response_text = response.text
            response_text = self._clean_json_response(response_text)
            
            try:
                comments_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                return self._fallback_comments(post_analysis['approaches'])
            
            # Humanize each comment
            humanized_comments = []
            for i, comment in enumerate(comments_data.get("comments", []), 1):
                humanized_text = self.humanizer.humanize(
                    comment.get("text", ""),
                    user_style
                )
                
                humanized_comments.append({
                    "text": humanized_text,
                    "variation": i,
                    "confidence": comment.get("confidence", 0.8),
                    "approach": comment.get("approach", post_analysis['approaches'][i-1] if i <= len(post_analysis['approaches']) else "engaging")
                })
            
            if not humanized_comments:
                logger.warning("No comments generated, using fallback")
                return self._fallback_comments(post_analysis['approaches'])
            
            logger.info(f"✓ Generated {len(humanized_comments)} comments for {post_analysis['type']} post")
            return humanized_comments
            
        except Exception as e:
            logger.error(f"Error generating comments: {str(e)}")
            return self._fallback_comments()
    
    def _analyze_post_type(self, post_content: str, post_context: Dict) -> Dict:
        """
        Analyze post to determine its type and best comment approaches
        
        Returns:
            {
                "type": "achievement" | "question" | "story" | etc,
                "approaches": [approach1, approach2, approach3],
                "tone": "celebratory" | "thoughtful" | etc
            }
        """
        try:
            # Simplified, clearer prompt
            analysis_prompt = f"""Analyze this LinkedIn post. Return JSON only, no explanation.

POST: {post_content[:400]}

Determine:
1. Post type: achievement, question, story, opinion, news, tips, poll, announcement, lesson, general
2. Best 3 comment approaches
3. Overall tone

Return this exact format:
{{"type":"achievement","approaches":["congratulate","ask_details","relate"],"tone":"celebratory"}}

Examples by type:
- achievement: {{"type":"achievement","approaches":["congratulate","ask_about_process","relate_win"],"tone":"celebratory"}}
- question: {{"type":"question","approaches":["answer_directly","share_experience","ask_followup"],"tone":"helpful"}}
- story: {{"type":"story","approaches":["empathize","share_similar","highlight_lesson"],"tone":"supportive"}}
- tips: {{"type":"tips","approaches":["thank_add_tip","ask_clarification","share_result"],"tone":"engaging"}}
- opinion: {{"type":"opinion","approaches":["agree_expand","polite_counter","add_nuance"],"tone":"thoughtful"}}

Return ONLY the JSON object, nothing else."""

            response = self.model.generate_content(
                analysis_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,  # Very low for consistent JSON
                    max_output_tokens=150,
                )
            )
            
            # Enhanced JSON cleaning
            analysis_text = self._clean_json_response_strict(response.text)
            
            # Attempt to parse
            analysis = json.loads(analysis_text)
            
            # Validate and extract
            post_type = analysis.get("type", "general")
            approaches = analysis.get("approaches", ["engage", "respond", "react"])
            tone = analysis.get("tone", "thoughtful")
            
            # Ensure we have 3 approaches
            if not isinstance(approaches, list) or len(approaches) < 3:
                approaches = ["engage", "question", "relate"]
            
            logger.info(f"✓ Post analyzed: {post_type} | {', '.join(approaches[:3])}")
            
            return {
                "type": post_type,
                "approaches": approaches[:3],  # Only first 3
                "tone": tone
            }
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed: {e}, using keyword detection")
            return self._fallback_post_analysis(post_content)
        except Exception as e:
            logger.warning(f"Post analysis error: {e}, using keyword detection")
            return self._fallback_post_analysis(post_content)
    
    def _fallback_post_analysis(self, post_content: str) -> Dict:
        """Fallback: Simple keyword-based post type detection"""
        content_lower = post_content.lower()
        
        # Question detection
        if '?' in content_lower or any(word in content_lower for word in ['what do you think', 'thoughts?', 'how do you', 'which', 'recommendations']):
            return {
                "type": "question",
                "approaches": ["answer_directly", "share_experience", "ask_followup"],
                "tone": "helpful"
            }
        
        # Achievement detection
        elif any(word in content_lower for word in ['excited to', 'proud to', 'happy to announce', 'achieved', 'launched', 'released', 'thrilled']):
            return {
                "type": "achievement",
                "approaches": ["congratulate", "ask_details", "relate_experience"],
                "tone": "celebratory"
            }
        
        # Lesson/Failure detection
        elif any(word in content_lower for word in ['failed', 'mistake', 'learned', 'lesson', 'lost', 'tough']):
            return {
                "type": "lesson",
                "approaches": ["empathize", "share_similar", "highlight_growth"],
                "tone": "supportive"
            }
        
        # Tips/Advice detection
        elif any(word in content_lower for word in ['tip', 'tips:', 'advice', 'how to', 'guide', 'steps', 'here\'s how']):
            return {
                "type": "tips",
                "approaches": ["thank_add_tip", "ask_question", "share_result"],
                "tone": "engaging"
            }
        
        # Opinion/Debate detection
        elif any(word in content_lower for word in ['i think', 'in my opinion', 'unpopular', 'controversial', 'hot take']):
            return {
                "type": "opinion",
                "approaches": ["agree_expand", "polite_counter", "add_perspective"],
                "tone": "thoughtful"
            }
        
        # News/Update detection
        elif any(word in content_lower for word in ['just released', 'breaking', 'announced', 'update:', 'news']):
            return {
                "type": "news",
                "approaches": ["react_implications", "ask_question", "share_perspective"],
                "tone": "informative"
            }
        
        # Default: General engagement
        else:
            return {
                "type": "general",
                "approaches": ["engage", "question", "relate"],
                "tone": "thoughtful"
            }
    
    def _clean_json_response_strict(self, text: str) -> str:
        """Enhanced JSON cleaning for better parsing"""
        import re
        
        # Remove markdown code blocks
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        
        # Strip whitespace
        text = text.strip()
        
        # Find JSON object boundaries
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1 and end > start:
            text = text[start:end+1]
        else:
            # No valid JSON found
            raise json.JSONDecodeError("No JSON object found", text, 0)
        
        # Remove trailing commas before closing braces/brackets
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        
        # Remove any newlines within strings (common issue)
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def _build_dynamic_generation_prompt(
        self,
        user_style: Dict,
        target_profile: Dict,
        post_context: Dict,
        post_content: str,
        post_analysis: Dict
    ) -> str:
        """Build prompt based on post type analysis"""
        
        post_type = post_analysis['type']
        approaches = post_analysis['approaches']
        tone = post_analysis['tone']
        
        # Dynamic examples based on post type
        type_examples = {
            "achievement": [
                "That's huge. What was the tipping point?",
                "Congrats! How long did this take?",
                "Love this. The grind paid off."
            ],
            "question": [
                "Been using X for 2 years. Game changer.",
                "Depends on your use case. What's your setup?",
                "Have you tried Y? Worked better for me."
            ],
            "story": [
                "That $50K wasn't lost, it was tuition.",
                "Been there. The clarity after failure changes everything.",
                "Timing is brutal. Great idea, wrong moment = expensive."
            ],
            "tips": [
                "Number 3 is underrated. Saved me months.",
                "Would add: always test before scaling.",
                "This. Especially the part about X."
            ],
            "opinion": [
                "Hard disagree on point 2, but respect the take.",
                "Interesting. How do you handle X then?",
                "This perspective makes sense for B2B, less for B2C."
            ],
            "news": [
                "This changes everything for small teams.",
                "About time. What took them so long?",
                "Curious how this affects enterprise deals."
            ]
        }
        
        examples = type_examples.get(post_type, [
            "That resonates. Been thinking about this too.",
            "Great point. How'd you figure this out?",
            "Makes sense. Timing is everything."
        ])
        
        return f"""Write 3 SHORT LinkedIn comments for a {post_type.upper()} post.

POST TYPE: {post_type}
POST TONE: {tone}
REQUIRED APPROACHES: {', '.join(approaches)}

POST: {post_content[:400]}

USER STYLE: {user_style.get('tone')}, {user_style.get('avg_comment_length', 35)} words avg

CRITICAL RULES:
1. Keep it SHORT (20-50 words max)
2. Match the {tone} tone of the post
3. Use these 3 approaches: {', '.join(approaches)}
4. NO corporate jargon or AI phrases
5. Sound like you're texting a smart friend
6. Add personal touch or real experience
7. Vary sentence lengths dramatically

GOOD EXAMPLES for {post_type}:
{chr(10).join(f'- "{ex}"' for ex in examples)}

BAD EXAMPLES (Never write like this):
- "It takes immense courage to share such a raw experience..."
- "This is a fantastic reflection on a tough experience..."
- "Your journey from that low point is truly inspiring..."
- "This highlights the critical importance of..."

BANNED WORDS: "immense", "powerful", "invaluable", "truly", "inspiring", "journey", "pave the way", "wisdom", "transparent", "reflection", "regarding", "highlighted", "critical", "valuable", "insights", "delve", "leverage", "game-changing"

Write like a REAL person commenting on a {post_type} post. Short. Direct. Genuine.

Return JSON with 3 comments matching the approaches: {', '.join(approaches)}
{{"comments":[
  {{"text":"comment using {approaches[0]} approach","approach":"{approaches[0]}"}},
  {{"text":"comment using {approaches[1]} approach","approach":"{approaches[1]}"}},
  {{"text":"comment using {approaches[2]} approach","approach":"{approaches[2]}"}}
]}}"""
    
    def _build_generation_prompt(
        self,
        user_style: Dict,
        target_profile: Dict,
        post_context: Dict,
        post_content: str
    ) -> str:
        """Build ultra-natural comment generation prompt"""
        
        return f"""Write 3 SHORT LinkedIn comments. Sound HUMAN, not AI.

POST: {post_content[:400]}

USER STYLE: {user_style.get('tone')}, {user_style.get('avg_comment_length', 40)} words avg

RULES:
1. Keep it SHORT (20-50 words max)
2. NO corporate jargon or AI phrases
3. Sound like you're texting a friend
4. Use simple, direct language
5. Add personal touch or emotion
6. Vary sentence lengths dramatically

BANNED WORDS: "immense", "powerful", "invaluable", "truly", "inspiring", "journey", "pave the way", "wisdom", "transparent", "reflection", "regarding", "highlighted", "critical", "valuable", "insights"

GOOD EXAMPLES:
- "That $50K wasn't lost, it was tuition. Hard lessons stick."
- "Been there. The clarity that comes after failure changes everything."
- "Cash flow > everything. Learned that one the expensive way too."
- "Timing is brutal. Great idea, wrong moment = expensive lesson."

BAD EXAMPLES (Don't write like this):
- "It takes immense courage to share such a raw experience..."
- "This is a fantastic reflection on a tough experience..."
- "Your journey from that low point to gratitude is truly inspiring..."

Write like a real person. Short. Direct. Real.

Return JSON:
{{"comments":[{{"text":"short comment here","approach":"supportive"}},{{"text":"another short one","approach":"questioning"}},{{"text":"third variation","approach":"insightful"}}]}}"""

    
    def _format_engagement_patterns(self, patterns: Dict) -> str:
        """Format engagement patterns for prompt"""
        active_patterns = [k.replace('_', ' ') for k, v in patterns.items() if v]
        return ', '.join(active_patterns) if active_patterns else "neutral engagement"
    
    def _fallback_comments(self, approaches: List[str] = None) -> List[Dict]:
        """Fallback comments when generation fails"""
        if not approaches:
            approaches = ["engage", "question", "relate"]
        
        fallback_templates = {
            "congratulate": "Congrats! Well deserved.",
            "empathize": "Been there. It gets better.",
            "ask_details": "How'd you pull this off?",
            "share_experience": "Had similar experience. Game changer.",
            "answer_directly": "From my experience: focus on X first.",
            "thank_add_tip": "Great list. Would add: always test small first.",
            "agree_expand": "Exactly. Plus the timing aspect matters too.",
            "celebrate": "This is huge! Congrats!",
            "engage": "Great insights. Thanks for sharing.",
            "question": "Interesting. How do you see this evolving?",
            "relate": "This resonates. Really valuable post."
        }
        
        return [
            {
                "text": fallback_templates.get(approaches[0], "Great insights!"),
                "variation": 1,
                "confidence": 0.5,
                "approach": approaches[0]
            },
            {
                "text": fallback_templates.get(approaches[1], "Interesting perspective."),
                "variation": 2,
                "confidence": 0.5,
                "approach": approaches[1]
            },
            {
                "text": fallback_templates.get(approaches[2], "This resonates."),
                "variation": 3,
                "confidence": 0.5,
                "approach": approaches[2]
            }
        ]
    
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


class HumanizationEngine:
    """Makes comments sound more human and less AI-generated"""
    
    # Massively expanded AI detection patterns
    AI_CLICHES = [
        # Verbs that sound robotic
        "delve into", "delve", "embark on", "embark", "leverage", "revolutionize",
        "transform", "unlock", "unleash", "streamline", "supercharge", 
        "navigate", "optimize", "implement", "integrate", "underscore",
        "pave the way", "forged", "trumps",
        
        # Nouns that sound corporate/AI
        "endeavor", "realm", "tapestry", "landscape", "paradigm", "synergy",
        "optimization", "implementation", "integration", "journey", "acumen",
        
        # Adjectives that scream AI
        "cutting-edge", "game-changing", "unprecedented", "robust", "comprehensive",
        "dynamic", "innovative", "exceptional", "proven", "seamless", "transformative",
        "thought-provoking", "powerful", "invaluable", "truly inspiring", "fantastic",
        "immense", "raw experience", "critical choice",
        
        # Adverbs that are too formal
        "moreover", "furthermore", "additionally", "nevertheless", "nonetheless",
        "undoubtedly", "arguably", "remarkably", "ultimately", "incredibly",
        "exceptionally", "truly", "especially", "regarding", "clearly",
        
        # Phrases that are dead giveaways
        "in today's digital landscape", "it's important to note", "at the end of the day",
        "thanks for sharing", "great insights", "i hope this finds you well",
        "to be honest", "in my humble opinion", "needless to say",
        "this is a fantastic reflection", "your journey from", "it takes immense courage",
        "which you highlighted", "your insights here could be valuable",
        "many founders struggle with", "separates sustainable ventures"
    ]
    
    # Natural human alternatives
    NATURAL_REPLACEMENTS = {
        # Make it conversational
        "it takes immense courage": "takes guts",
        "your journey": "how you went",
        "truly inspiring": "impressive",
        "powerful reminder": "good reminder",
        "invaluable growth": "real growth",
        "transparent about": "open about",
        "fantastic reflection": "good take",
        "regarding": "about",
        "highlighted": "mentioned",
        "critical choice": "huge decision",
        "valuable to others": "helpful",
        "struggle with": "deal with",
        
        # Shorten everything
        "it is": "it's",
        "you are": "you're",
        "that is": "that's",
        "there is": "there's",
        "what is": "what's",
        "cannot": "can't",
        "should not": "shouldn't",
        "would not": "wouldn't",
    }
    
    def humanize(self, comment: str, user_style: Dict) -> str:
        """Apply humanization techniques"""
        
        # Remove AI clichés
        comment = self._remove_ai_patterns(comment)
        
        # Ensure burstiness (critical for AI detection)
        comment = self._ensure_burstiness(comment, user_style)
        
        # Add user-specific patterns
        comment = self._apply_user_quirks(comment, user_style)
        
        # Add natural imperfections if user has them
        comment = self._add_natural_elements(comment, user_style)
        
        # Validate length
        comment = self._adjust_length(comment, user_style)
        
        return comment.strip()
    
    def _ensure_burstiness(self, comment: str, user_style: Dict) -> str:
        """Ensure dramatic sentence length variation (critical for AI detection)"""
        
        sentences = re.split(r'[.!?]+', comment)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return comment
        
        # Check if burstiness is needed
        lengths = [len(s.split()) for s in sentences]
        variation = max(lengths) - min(lengths) if lengths else 0
        
        # If variation is too low (monotonous), it's AI-like
        if variation < 10 and len(sentences) >= 3:
            # Try to add variation by splitting long sentences or combining short ones
            # This is a safety net - the LLM should handle this
            pass
        
        return comment
    
    def _remove_ai_patterns(self, text: str) -> str:
        """Aggressively remove AI patterns"""
        original = text
        
        # Remove AI clichés
        for cliche in self.AI_CLICHES:
            pattern = re.compile(r'\b' + re.escape(cliche) + r'\b', re.IGNORECASE)
            text = pattern.sub("", text)
        
        # Apply natural replacements
        for ai_phrase, natural in self.NATURAL_REPLACEMENTS.items():
            pattern = re.compile(r'\b' + re.escape(ai_phrase) + r'\b', re.IGNORECASE)
            text = pattern.sub(natural, text)
        
        # Clean up double spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        # If we killed the comment, return original
        if len(text) < 10:
            return original
        
        return text
    
    def _apply_user_quirks(self, comment: str, user_style: Dict) -> str:
        """Add user-specific patterns"""
        
        # ALWAYS use contractions (sounds more human)
        contractions = {
            "it is": "it's", "you are": "you're", "that is": "that's",
            "there is": "there's", "what is": "what's", "cannot": "can't",
            "do not": "don't", "will not": "won't", "should not": "shouldn't",
            "would not": "wouldn't", "could not": "couldn't"
        }
        
        for formal, casual in contractions.items():
            comment = re.sub(r'\b' + formal + r'\b', casual, comment, flags=re.IGNORECASE)
        
        # Add emoji sparingly if user uses them
        emoji_usage = user_style.get('emoji_usage', 'none')
        if emoji_usage in ['moderate', 'high'] and random.random() > 0.8:
            if not any(c in comment for c in ['💯', '🎯', '👏', '💪', '🔥']):
                emojis = ['💯', '🎯', '👏', '💪', '🔥']
                comment += f" {random.choice(emojis)}"
        
        return comment
    
    def _add_natural_elements(self, comment: str, user_style: Dict) -> str:
        """Add human speech patterns"""
        
        # Sometimes start with casual acknowledgment
        if random.random() > 0.75:
            starters = ['Yep.', 'True.', 'Exactly.', 'Yeah,', 'Totally.']
            if not any(comment.startswith(s) for s in ['This', 'That', 'Your', 'The', 'It']):
                comment = f"{random.choice(starters)} {comment}"
        
        return comment
    
    def _adjust_length(self, comment: str, user_style: Dict) -> str:
        """CRITICAL: Enforce SHORT, human-like length"""
        
        words = comment.split()
        word_count = len(words)
        
        # HARD LIMIT: 50 words max
        if word_count > 50:
            # Cut aggressively at sentence boundaries
            sentences = re.split(r'[.!?]+', comment)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Keep only first 1-2 sentences
            kept = []
            current_words = 0
            
            for sent in sentences[:3]:  # Check first 3 sentences max
                sent_words = len(sent.split())
                if current_words + sent_words <= 45:
                    kept.append(sent)
                    current_words += sent_words
                else:
                    break
            
            if kept:
                comment = '. '.join(kept)
                if not comment.endswith(('.', '!', '?')):
                    comment += '.'
        
        # Minimum 15 words (too short looks spam)
        if len(words) < 15 and len(words) > 5:
            # Keep as is - brief is good
            pass
        elif len(words) <= 5:
            # Too short, might need more context
            # But don't force it - Gemini should handle this
            pass
        
        return comment.strip()
        
        return comment