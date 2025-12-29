"""
ULTIMATE Dynamic Prompt Engine - Uses Complete Voice Profile
Leverages ALL 82+ fields from user JSON for authentic voice matching
"""

from typing import Dict, List
import json
import re

class DynamicPromptEngine:
    """
    Ultimate prompt engine using complete voice profile:
    - Rhythm metrics (sentence length, burstiness, run-on tendency)
    - Lexical signature (TTR, density, concreteness)
    - Cohesion signature (connective density, discourse markers)
    - Punctuation profile (comma density, no questions/exclamations)
    - Voice markers (first person ratio, hedge patterns)
    - Generation recipe (exact formula)
    - Real comment examples (templates)
    """
    
    # 20 sentiment types with smart detection
    SENTIMENT_PATTERNS = {
        "celebration_win": {
            "keywords": ["excited", "announce", "joined", "promoted", "launched", "hit", "reached", "achieved", "milestone", "thrilled"],
            "angles": ["INEVITABLE_NOT_SURPRISING", "JUST_CHECKPOINT", "REAL_COST", "PROPHETIC_NOT_CONGRATS"]
        },
        "failure_setback": {
            "keywords": ["failed", "lost", "messed up", "mistake", "wrong", "didn't work", "crashed", "shut down"],
            "angles": ["FAILURE_AS_CURRICULUM", "PAINFUL_LESSON", "FAILED_BIGGER_SOFTER", "PORTAL_NOT_PUNISHMENT"]
        },
        "advice_tactical": {
            "keywords": ["how to", "here's how", "steps", "framework", "process", "system", "strategy", "tip"],
            "angles": ["HIDDEN_COST", "MINDSET_SHIFT", "REAL_RISK", "SECRET_NOBODY_ASKED"]
        },
        "reflective_lessons": {
            "keywords": ["learned", "realized", "discovered", "wish i knew", "looking back", "lesson", "years ago"],
            "angles": ["LIVED_IT_DEEPER", "MISSING_CHAPTER", "FUTURE_SELF_LENS", "SCARRED_PEER"]
        },
        "vulnerable_emotional": {
            "keywords": ["struggling", "hard", "difficult", "vulnerable", "scared", "anxious", "burned out"],
            "angles": ["WHISPERED_TRUTH", "EARNED_INSIGHT", "ME_TOO_DEEPER", "PRESENCE_NOT_ADVICE"]
        },
        "comeback_redemption": {
            "keywords": ["back", "returned", "rebuilt", "recovered", "overcame", "survived", "fought back"],
            "angles": ["COST_OF_COMEBACK", "EARNED_THIS", "GHOST_OF_PAST", "REBUILD_BIGGER"]
        },
        "hiring_team": {
            "keywords": ["hiring", "join us", "we're looking", "team", "opportunity", "position", "role"],
            "angles": ["REAL_REASON_JOIN", "FILTER_HARD", "CULTURE_AFTER_MONTH_6", "DO_WE_MEAN_IT"]
        },
        "hot_take_controversial": {
            "keywords": ["unpopular", "controversial", "hot take", "truth", "nobody talks about"],
            "angles": ["REFRAME_SMARTER", "INTENSIFY_SURGICAL", "SEE_WHOLE_GAME", "NEW_ANGLE_NO_REACTION"]
        },
        "frustration_rant": {
            "keywords": ["frustrated", "tired of", "sick of", "enough", "why is", "still", "broken"],
            "angles": ["PATTERN_NOT_MAD", "RESIGNED_GENIUS", "COLD_TRUTH_BOMB", "GASLIT_NOW_WHAT"]
        },
        "gratitude_inspirational": {
            "keywords": ["grateful", "thankful", "blessed", "appreciate", "inspired", "motivated"],
            "angles": ["TIRED_BUT_GRATEFUL", "GRATITUDE_EARNED", "SUNRISE_NOT_FIREWORKS"]
        },
        "milestone_announcement": {
            "keywords": ["launched", "released", "started", "first", "milestone", "announcing"],
            "angles": ["PROPHETIC_NOT_CONGRATS", "WHY_THEY_STARTED", "100_LAUNCHES_LATER", "WAIT_UNTIL_CHAPTER_3"]
        },
        "crowd_engagement": {
            "keywords": ["what do you think", "thoughts?", "curious", "would love to hear", "?"],
            "angles": ["UNEXPECTED_REAL", "REAL_QUESTION_UNDERNEATH", "FLIP_WITH_QUESTION", "TRUTH_NOBODY_ELSE"]
        },
        "philosophical_abstract": {
            "keywords": ["meaning", "purpose", "existence", "identity", "time", "humanity"],
            "angles": ["TANGIBLE_BRUTAL_TRUTH", "METAPHOR_BLEEDS_REALITY", "BIG_IDEA_10_SECOND_MOMENT"]
        },
        "crisis_loss_burnout": {
            "keywords": ["burnout", "crisis", "loss", "grief", "broke", "breaking point", "can't", "drowning"],
            "angles": ["PRESENCE_NOT_ADVICE", "BEEN_THERE_QUIETER", "CHANGES_YOU_FOREVER"]
        },
        "self_promo_pitch": {
            "keywords": ["check out", "link in", "dm me", "book a call", "available", "limited spots"],
            "angles": ["CALL_OUT_VALUE", "BUYER_WHO_SEES", "TRUTH_BEHIND_MARKETING"]
        }
    }
    
    def detect_sentiment(self, post_content: str) -> str:
        """Detect post sentiment from keywords"""
        post_lower = post_content.lower()
        
        sentiment_scores = {}
        for sentiment, data in self.SENTIMENT_PATTERNS.items():
            score = sum(1 for keyword in data["keywords"] if keyword in post_lower)
            sentiment_scores[sentiment] = score
        
        if max(sentiment_scores.values()) > 0:
            return max(sentiment_scores, key=sentiment_scores.get)
        return "reflective_lessons"
    
    def select_best_angle(self, sentiment: str, post_context: Dict) -> str:
        """Select best angle based on context"""
        available_angles = self.SENTIMENT_PATTERNS.get(sentiment, {}).get("angles", [])
        
        if not available_angles:
            return "LIVED_IT_DEEPER"
        
        # Smart selection
        is_achievement = post_context.get("is_achievement", False)
        if is_achievement and "INEVITABLE_NOT_SURPRISING" in available_angles:
            return "INEVITABLE_NOT_SURPRISING"
        
        return available_angles[0]
    
    def build_ultimate_prompt(
        self,
        post_content: str,
        post_context: Dict,
        user_profile: Dict,
        sentiment: str = None,
        angle: str = None
    ) -> str:
        """
        Build ULTIMATE prompt using ALL user profile data
        Uses complete JSON structure with 82+ fields
        """
        
        # Auto-detect
        if not sentiment:
            sentiment = self.detect_sentiment(post_content)
        if not angle:
            angle = self.select_best_angle(sentiment, post_context)
        
        # Extract COMPLETE user data
        basic = user_profile.get("basic_info", {})
        core_voice = user_profile.get("core_voice_fingerprint", {})
        rhythm = user_profile.get("rhythm_metrics", {})
        lexical = user_profile.get("lexical_signature", {})
        cohesion = user_profile.get("cohesion_signature", {})
        punctuation = user_profile.get("punctuation_profile", {})
        voice_markers = user_profile.get("voice_markers", {})
        sentence_struct = user_profile.get("sentence_structure", {})
        recipe = user_profile.get("generation_recipe", {})
        real_examples = user_profile.get("real_comment_examples", [])
        common_phrases = user_profile.get("common_phrases", [])
        personality = user_profile.get("personality_traits", [])
        engagement = user_profile.get("engagement_patterns", {})
        specificity = user_profile.get("specificity_patterns", {})
        
        # Extract professional data
        professional = user_profile.get("professional", {})
        expertise = professional.get("expertise_areas", [])
        experience = professional.get("experience", [])
        
        # Build experience string
        if experience:
            exp_list = []
            for exp in experience[:3]:
                title = exp.get("title", "")
                company = exp.get("company", "")
                desc = exp.get("description", "")
                if desc:
                    exp_list.append(f"{title} at {company}: {desc[:100]}")
                else:
                    exp_list.append(f"{title} at {company}")
            exp_str = " | ".join(exp_list)
        else:
            exp_str = "Experienced professional"
        
        # Get post details
        key_details = self._extract_key_details(post_content, post_context)
        post_type = post_context.get("post_type", "general")
        is_achievement = post_context.get("is_achievement", False)
        achievement_type = post_context.get("achievement_type", "none")
        company = post_context.get("company_mentioned", "")
        
        # Get rhythm metrics
        sentence_length = rhythm.get("sentence_length_mean_words", {})
        target_length = sentence_length.get("target", 53)
        min_length = sentence_length.get("min", 35)
        max_length = sentence_length.get("max", 65)
        
        # Get connective density
        connective_data = cohesion.get("connective_density", {})
        connective_target = connective_data.get("target", 0.151)
        
        # Get common connectives
        discourse_markers = cohesion.get("discourse_marker_variety", {}).get("common_markers", 
            ["and", "so", "because", "then", "also", "but"])
        
        # Build THE ULTIMATE PROMPT
        prompt = f"""You are generating a LinkedIn comment in Vidhant Jain's EXACT voice.

{'='*70}
POST ANALYSIS
{'='*70}
Post Content: {post_content[:800]}

Detected Sentiment: {sentiment}
Post Type: {post_type}
Is Achievement: {is_achievement}
Company: {company or "N/A"}
Key Details: {key_details}

{'='*70}
SELECTED ANGLE: {angle}
{'='*70}

{self._get_angle_instruction(angle, sentiment, is_achievement, key_details)}

{'='*70}
YOUR COMPLETE VOICE PROFILE
{'='*70}

🎯 CORE IDENTITY:
Name: {basic.get('name', 'Professional')}
Archetype: {basic.get('voice_archetype', 'direct_operator')}
Tone: {core_voice.get('tone', 'direct, no-fluff, operator-focused')}
Personality: {', '.join(personality[:5])}

💼 YOUR EXPERIENCE (USE THIS!):
{exp_str}

🎓 YOUR EXPERTISE:
{', '.join(expertise[:5])}

📊 YOUR DATA POINTS (INJECT THESE NATURALLY):
{self._format_data_points(specificity)}

💬 YOUR REAL COMMENTS (TEMPLATES):
{self._format_examples(real_examples[:4])}

🗣️ YOUR SIGNATURE PHRASES (USE THESE):
{', '.join(f'"{p}"' for p in common_phrases[:5])}

{'='*70}
EXACT GENERATION RECIPE (FOLLOW PRECISELY!)
{'='*70}

📏 LENGTH:
- Target: {target_length} words
- Range: {min_length}-{max_length} words
- Typical: {rhythm.get('sentence_count_per_comment', {}).get('typical', 1)} sentence

🔗 CONNECTIVES (CRITICAL - YOUR SIGNATURE!):
- Target density: {connective_target} ({int(connective_target * target_length)} connectives in {target_length} words)
- Use: {', '.join(f'"{m}"' for m in discourse_markers[:5])}
- Style: {recipe.get('glue', '3-5 "and" + 1 "because" + optional "then"')}

✏️ PUNCTUATION RULES (STRICT):
- Question marks: {punctuation.get('question_marks', 0)} (NONE!)
- Exclamation marks: {punctuation.get('exclamation_marks', 0)} (NONE!)
- Commas: {sentence_struct.get('comma_density_per_100_words', {}).get('max', 1)} per 100 words (MINIMAL!)
- Style: {sentence_struct.get('style', 'run-on, chained with connectives')}

🎭 VOICE MARKERS:
- First person: {voice_markers.get('first_person_ratio', {}).get('target', 0.019)} ratio
- Hedges: Use {', '.join(voice_markers.get('hedge_certainty_ratio', {}).get('hedge_hits_per_comment', {}).get('examples', ['I feel']))}
- Opening: {recipe.get('opening', '1 hedge + first person (e.g., "I feel...")')}

📝 STRUCTURE:
- Form: {recipe.get('form', '1 sentence, 45-70 words')}
- Style: {sentence_struct.get('style', 'run-on, chained with connectives')}
- Imagery: {recipe.get('imagery', 'avoid poetic metaphors, keep it plain')}
- Data: {recipe.get('data_inclusion', 'cite specific metrics naturally')}

{'='*70}
ENGAGEMENT STYLE
{'='*70}

Questions: {engagement.get('question_style', 'clarifying, not rhetorical')}
Experience Sharing: {engagement.get('experience_style', 'data-backed, specific results')}
Advice: {engagement.get('advice_style', 'direct, actionable, operator lens')}
Humor: {engagement.get('humor_style', 'dry, subtle, intelligent')}

{'='*70}
CRITICAL REQUIREMENTS
{'='*70}

✅ MUST DO:
1. Use EXACT rhythm: {min_length}-{max_length} words, {rhythm.get('sentence_count_per_comment', {}).get('typical', 1)} sentence
2. Include {int(connective_target * target_length)} connectives (your signature!)
3. NO question marks, NO exclamation marks
4. MINIMAL commas (0-1 max)
5. Reference YOUR experience: {exp_str[:80]}...
6. Use YOUR phrases: {', '.join(common_phrases[:3])}
7. Inject data naturally: {specificity.get('data_usage', 'specific numbers')}

❌ NEVER DO:
1. Generic praise ("Great post!", "Congrats!")
2. Poetic metaphors or writer cadence
3. Template phrases ("Here's the thing", "The X part is")
4. Excessive qualifiers ("just", "simply", "really")
5. Politeness formulae ("Thanks in advance")
6. Break the rhythm (must be {min_length}-{max_length} words!)

{'='*70}
NOW GENERATE ONE COMMENT
{'='*70}

Write ONE comment that:
- Matches {angle} angle perfectly
- Uses Vidhant's EXACT voice
- References specific details: {key_details}
- Follows generation recipe precisely
- Feels 100% authentic

Output ONLY the comment text, nothing else.
"""
        
        return prompt
    
    def _get_angle_instruction(self, angle: str, sentiment: str, is_achievement: bool, details: str) -> str:
        """Get specific instruction for selected angle"""
        
        angle_instructions = {
            "INEVITABLE_NOT_SURPRISING": f"""
🎯 ANGLE: Make this achievement feel INEVITABLE, not surprising.

Instructions:
- Don't say "congrats" - make it feel like you SAW this coming
- Use quiet confidence: "This was coming", "Saw this months ago"
- Reference specific achievement: {details}
- Ask forward-looking operator question
- {is_achievement} words, direct tone

Example structure: "[Observation about inevitability]. [Specific detail]. [Future question]?"
""",
            
            "JUST_CHECKPOINT": f"""
🎯 ANGLE: Reframe this win as JUST A CHECKPOINT, not the endgame.

Instructions:
- Acknowledge win but frame as "step X of 10"
- Share YOUR bigger journey ({details})
- Point to what comes next
- Ask about challenges ahead
- Direct, operator mindset

Example: "[Milestone] is checkpoint 1. We [your experience]. [Next challenge]?"
""",
            
            "REAL_COST": f"""
🎯 ANGLE: Ask about the REAL COST behind this win.

Instructions:
- No praise - just one sharp question
- "What did it REALLY cost to win this?"
- Reference the specific win: {details}
- Make them think about the price, not just the prize
- Direct, penetrating

Example: "[Win acknowledged]. What did you sacrifice to get here?"
""",
            
            "HIDDEN_COST": f"""
🎯 ANGLE: Drop the HIDDEN COST nobody mentions.

Instructions:
- Point out the catch in their advice
- Use YOUR expertise: {details}
- Specific cost/risk they overlooked
- Data-backed when possible
- Operator insight

Example: "[Tactic] works, but [hidden cost]. We [your data]."
""",
            
            "LIVED_IT_DEEPER": f"""
🎯 ANGLE: Someone who learned this lesson but paid a HIGHER price.

Instructions:
- Share YOUR bigger/harder version
- Use specific data from your experience
- Make it feel earned: "Been there, cost more"
- Reference: {details}
- Respectful but real

Example: "[Lesson] resonates. [Your harder experience]. [What you learned]."
""",
            
            "PATTERN_NOT_MAD": f"""
🎯 ANGLE: Used to be mad, now just see the pattern.

Instructions:
- Resigned wisdom tone
- "Used to get mad about this. Now I just see..."
- Pattern recognition from experience
- Tired but clear
- About: {details}

Example: "Used to [reaction]. Now I see [pattern]. [Your experience]."
""",
            
            "FILTER_HARD": f"""
🎯 ANGLE: Filter the room HARD with this hiring post.

Instructions:
- Raise the bar significantly
- Define what "X quality" REALLY means
- Use YOUR standards: {details}
- Repel wrong candidates
- Operator-level specifics

Example: "'[Quality]' means [specific bar]. Most can't. That's your filter."
""",
            
            "WHISPERED_TRUTH": f"""
🎯 ANGLE: Whispered truth, not loud sympathy.

Instructions:
- Human, not helpful
- Quiet power
- Make them feel understood, not rescued
- About: {details}
- Presence, not advice

Example: "[Quiet acknowledgment]. [Simple truth]. [Grounding thought]."
"""
        }
        
        return angle_instructions.get(angle, f"""
🎯 ANGLE: {angle}

Use your operator lens, reference specific details, stay authentic to your voice.
""")
    
    def _format_data_points(self, specificity: Dict) -> str:
        """Format user's data points for injection"""
        number_examples = specificity.get("number_style", [])
        if number_examples:
            return "\n".join(f"   - {ex}" for ex in number_examples[:6])
        return "   - Use specific metrics from your experience"
    
    def _format_examples(self, examples: List[Dict]) -> str:
        """Format real comment examples"""
        if not examples:
            return "   (Use natural, conversational style)"
        
        formatted = []
        for i, ex in enumerate(examples):
            text = ex.get("text", "") if isinstance(ex, dict) else str(ex)
            analysis = ex.get("analysis", "") if isinstance(ex, dict) else ""
            formatted.append(f"   {i+1}. \"{text}\"")
            if analysis:
                formatted.append(f"      → {analysis}")
        
        return "\n".join(formatted)
    
    def _extract_key_details(self, post_content: str, post_context: Dict) -> str:
        """Extract key details to reference"""
        details = []
        
        # From context
        achievement_type = post_context.get("achievement_type", "")
        company = post_context.get("company_mentioned", "")
        numbers = post_context.get("numbers_mentioned", [])
        specific_details = post_context.get("specific_details", [])
        
        if achievement_type and achievement_type != "none":
            details.append(achievement_type.replace("_", " "))
        if company:
            details.append(company)
        if numbers:
            details.extend(numbers[:2])
        if specific_details:
            details.extend(specific_details[:2])
        
        return ", ".join(details) if details else "main topic"


# Global instance
dynamic_prompt_engine = DynamicPromptEngine()