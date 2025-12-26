"""
Comment Generator Service using OpenAI
Generates human-like LinkedIn comments
Enhanced with advanced humanization + paraphrasing
"""
from openai import OpenAI
from typing import Dict, List
from app.core.config import settings
import json
import re
import logging
import random
from app.services.advanced_humanizer import apply_advanced_humanization
from app.services.paraphrase_service import paraphrase_service

logger = logging.getLogger(__name__)


class CommentGenerator:
    """Generates authentic LinkedIn comments using OpenAI GPT-4"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        # Use GPT-4o-mini for cost-effective generation or GPT-4o for best quality
        self.model = settings.OPENAI_MODEL or "gpt-4o-mini"
        logger.info(f"✓ Initialized OpenAI with model: {self.model}")
    
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
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at writing authentic, human-like LinkedIn comments. You write SHORT, direct comments that sound like real people texting, not AI."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # Balanced: natural but grounded
                max_tokens=800,
                top_p=0.9,  # Reduces hallucination
                response_format={"type": "json_object"}  # Force JSON response
            )
            
            # Parse response
            response_text = response.choices[0].message.content
            
            try:
                comments_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                return self._fallback_comments(post_analysis['approaches'])
            
            # STEP 3: Apply advanced humanization + paraphrasing
            humanized_comments = []
            for i, comment in enumerate(comments_data.get("comments", []), 1):
                # Step 3a: Advanced humanization (burstiness, natural patterns)
                humanized_text = apply_advanced_humanization(
                    comment.get("text", ""),
                    user_style
                )
                
                # Step 3b: Paraphrase for extra variation (if enabled)
                if paraphrase_service.enabled:
                    logger.debug(f"Paraphrasing comment {i}/3...")
                    paraphrased_text = paraphrase_service.paraphrase(
                        humanized_text,
                        mode="standard"  # Options: standard, fluent, creative
                    )
                    final_text = paraphrased_text if paraphrased_text else humanized_text
                else:
                    final_text = humanized_text
                
                humanized_comments.append({
                    "text": final_text,
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
        """Analyze post to determine its type and best comment approaches"""
        for attempt in range(2):
            try:
                analysis_prompt = f"""Analyze this LinkedIn post and return a JSON object.

POST: {post_content[:400]}

Return this structure:
{{"type":"achievement","approaches":["approach1","approach2","approach3"],"tone":"celebratory"}}

Types: achievement, question, story, opinion, news, tips, poll, announcement, lesson, general
Tones: celebratory, helpful, supportive, engaging, thoughtful

Return ONLY the JSON object, nothing else."""

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a LinkedIn post analyzer. Return only JSON."},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=200,
                    response_format={"type": "json_object"}
                )
                
                response_text = response.choices[0].message.content
                logger.debug(f"Raw response (attempt {attempt+1}): {response_text[:200]}")
                
                # Parse JSON
                analysis = json.loads(response_text)
                
                # Validate structure
                if not all(k in analysis for k in ["type", "approaches", "tone"]):
                    raise ValueError("Missing required keys in response")
                
                if not isinstance(analysis["approaches"], list) or len(analysis["approaches"]) < 3:
                    raise ValueError("Invalid approaches format")
                
                logger.info(f"✓ Post analyzed: {analysis['type']} | {', '.join(analysis['approaches'][:3])}")
                
                return {
                    "type": analysis["type"],
                    "approaches": analysis["approaches"][:3],
                    "tone": analysis["tone"]
                }
                
            except Exception as e:
                if attempt == 0:
                    logger.warning(f"Analysis attempt {attempt+1} failed: {e}, retrying...")
                    continue
                else:
                    logger.warning(f"Analysis failed after 2 attempts: {e}, using fallback")
                    return self._fallback_post_analysis(post_content)
        
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
    
    def _extract_key_facts(self, post_content: str) -> List[str]:
        """
        Extract specific facts from post to prevent hallucination
        
        Returns list of facts the comment should reference
        """
        facts = []
        
        # Extract numbers (dates, metrics, timeframes)
        numbers = re.findall(r'\b\d+[KMB]?\b|\b\d{4}\b', post_content)
        if numbers:
            facts.extend([f"number: {n}" for n in numbers[:2]])
        
        # Extract list items (numbered or bulleted)
        list_items = re.findall(r'[\d]+[.)\-]\s*([^\n]+)', post_content)
        if list_items:
            facts.extend([f"point: {item[:50].strip()}" for item in list_items[:3]])
        
        # Extract quoted phrases
        quotes = re.findall(r'"([^"]+)"', post_content)
        if quotes:
            facts.extend([f"quote: {q[:40]}" for q in quotes[:2]])
        
        return facts[:5]  # Max 5 facts total
    
    def _build_dynamic_generation_prompt(
        self,
        user_style: Dict,
        target_profile: Dict,
        post_context: Dict,
        post_content: str,
        post_analysis: Dict
    ) -> str:
        """Build prompt based on post type analysis - Anti-hallucination optimized"""
        
        post_type = post_analysis['type']
        approaches = post_analysis['approaches']
        tone = post_analysis['tone']
        
        # Use extracted facts from profile analyzer if available
        key_facts = post_context.get('extracted_facts', [])
        
        # Fallback: Extract our own facts if analyzer didn't provide them
        if not key_facts:
            key_facts = self._extract_key_facts(post_content)
        
        # Use key points from analyzer if available
        analyzer_key_points = post_context.get('key_points', [])
        if analyzer_key_points:
            key_facts.extend([f"key point: {point}" for point in analyzer_key_points[:3]])
        
        # Dynamic examples based on post type
        type_examples = {
            "achievement": [
                "wait this is huge. what was the moment it clicked for you?",
                "yooo congrats! how long did this take",
                "damn the grind really does work"
            ],
            "question": [
                "been using X for like 2 years, honestly changed everything for me",
                "depends what youre trying to do tbh, whats your current setup?",
                "have you tried Y? worked so much better in my case"
            ],
            "story": [
                "that 50k wasnt a loss it was just expensive education lol",
                "been there man. that clarity after you fail hits so different",
                "timing is everything dude. great idea at the wrong time just hurts"
            ],
            "tips": [
                "number 3 is so slept on, literally saved me months",
                "id add - test it out before you go all in. learned that one the hard way",
                "yesss this. especially that part about X"
            ],
            "opinion": [
                "hard disagree on 2 but i get your reasoning",
                "wait interesting. how would you handle X in that case?",
                "this makes sense for B2B, not sure about B2C though"
            ],
            "news": [
                "okay this actually changes things for small teams",
                "finally lol what took them so long",
                "im curious how this affects enterprise stuff"
            ]
        }
        
        examples = type_examples.get(post_type, [
            "ive been thinking about this too lately",
            "wait how did you figure this out",
            "yeah timing really does matter"
        ])
        
        # Build facts section
        facts_instruction = ""
        if key_facts:
            facts_instruction = f"""
SPECIFIC FACTS FROM POST (reference at least ONE):
{chr(10).join(f'- {fact}' for fact in key_facts[:7])}
"""
        
        # Add user's typical openings if available
        user_openings = user_style.get('typical_comment_openings', [])
        openings_hint = ""
        if user_openings:
            openings_hint = f"""
YOUR TYPICAL COMMENT STARTERS (optionally use these naturally):
{', '.join(f'"{opener}"' for opener in user_openings[:3])}
"""
        
        return f"""Write 3 SHORT LinkedIn comments for a {post_type.upper()} post.

POST TYPE: {post_type}
POST TONE: {tone}
REQUIRED APPROACHES: {', '.join(approaches)}

POST CONTENT:
{post_content[:400]}
{facts_instruction}

USER STYLE: {user_style.get('tone')}, {user_style.get('avg_comment_length', 35)} words avg{openings_hint}

CRITICAL RULES (ANTI-HALLUCINATION):
1. Keep it SHORT (20-50 words max)
2. Reference SPECIFIC words/numbers from the post above (not generic "your insights")
3. Match the {tone} tone of the post
4. Use these 3 approaches: {', '.join(approaches)}
5. NO corporate jargon or AI phrases
6. Sound like you're texting a smart friend
7. Add personal touch ONLY if genuinely relevant
8. Vary sentence lengths dramatically
9. NEVER mention topics not in the post
10. NEVER invent credentials or experiences

SELF-CHECK BEFORE GENERATING:
For each comment ask:
- Did I reference something SPECIFIC from the post?
- Did I add real value (not just praise)?
- Does this sound like a real text message?
- Did I stay 100% within what the post discusses?

If ANY answer is NO, rewrite until all are YES.

GOOD EXAMPLES for {post_type}:
{chr(10).join(f'- "{ex}"' for ex in examples)}

BAD EXAMPLES (NEVER do this):
- "Your journey from X to Y is inspiring..." [Generic, could apply anywhere]
- "As someone in enterprise sales..." [Don't invent credentials]
- "This reminds me of Steve Jobs..." [Don't add external references]
- "Great insights!" [Too generic, doesn't reference specifics]
- "This highlights the critical importance of..." [Corporate speak]

BANNED WORDS: "immense", "powerful", "invaluable", "truly", "inspiring", "journey", "pave the way", "wisdom", "transparent", "reflection", "regarding", "highlighted", "critical", "valuable insights", "delve", "leverage", "game-changing"

Write like a REAL person commenting on this SPECIFIC {post_type} post. Short. Direct. Genuine. Grounded in the actual post content.

Return JSON with 3 comments:
{{"comments":[
  {{"text":"comment using {approaches[0]} approach - reference specific post content","approach":"{approaches[0]}","confidence":0.85}},
  {{"text":"comment using {approaches[1]} approach - reference specific post content","approach":"{approaches[1]}","confidence":0.82}},
  {{"text":"comment using {approaches[2]} approach - reference specific post content","approach":"{approaches[2]}","confidence":0.88}}
]}}"""
    
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