"""
Advanced Comment Humanizer
Implements natural writing patterns based on research:
- Burstiness (sentence length variation)
- Perplexity (word unpredictability)
- Natural conversational markers
- Authentic LinkedIn comment patterns
"""
import random
import re
from typing import List, Dict


class AdvancedHumanizer:
    """
    Advanced humanization using linguistic research:
    - High burstiness (varied sentence length)
    - Moderate perplexity (natural word choices)
    - Conversational markers
    - Strategic imperfections
    """
    
    # Natural conversation starters (real LinkedIn patterns)
    NATURAL_STARTERS = [
        "",  # No starter (most natural)
        "Honestly,",
        "Real talk -",
        "Ngl,",
        "Tbh,",
        "Yeah,",
        "So,",
        "Look,",
        "",  # Duplicate empty for higher probability
        "",
        ""
    ]
    
    # Sentence connectors (casual, not AI-formal)
    CASUAL_CONNECTORS = {
        "however": ["but", "though", "still"],
        "therefore": ["so", "meaning", "which means"],
        "additionally": ["also", "plus", "and"],
        "furthermore": ["plus", "and", "also"],
        "moreover": ["also", "plus", "and"],
        "consequently": ["so", "meaning"],
        "nevertheless": ["but", "still", "though"],
        "thus": ["so"],
        "hence": ["so"],
        "regarding": ["about", "on"],
        "concerning": ["about"],
        "subsequently": ["then", "later"],
        "initially": ["first", "at first"],
        "ultimately": ["in the end", "finally"]
    }
    
    # AI-formal transitions to remove
    FORMAL_TRANSITIONS = [
        "In conclusion,",
        "To summarize,",
        "Furthermore,",
        "Moreover,",
        "Additionally,",
        "Consequently,",
        "Nevertheless,",
        "Subsequently,",
        "Ultimately,",
        "Initially,",
        "In essence,",
        "Essentially,",
        "Fundamentally,"
    ]
    
    # Filler words that add authenticity
    NATURAL_FILLERS = [
        "kinda",
        "sorta",
        "pretty much",
        "basically",
        "honestly",
        "actually",
        "really",
        "just"
    ]
    
    def humanize_comment(self, comment: str, user_style: Dict) -> str:
        """
        Apply comprehensive humanization
        
        Research-based techniques:
        1. Increase burstiness (vary sentence lengths)
        2. Add natural markers
        3. Use contractions
        4. Strategic imperfections
        5. Conversational tone
        """
        # Step 1: Clean AI artifacts
        comment = self._remove_ai_formality(comment)
        
        # Step 2: Apply contractions (universal humanization)
        comment = self._apply_contractions(comment)
        
        # Step 3: Add sentence variety (burstiness)
        comment = self._vary_sentence_structure(comment)
        
        # Step 4: Add natural markers
        comment = self._add_conversational_markers(comment, user_style)
        
        # Step 5: Strategic imperfections
        comment = self._add_natural_imperfections(comment, user_style)
        
        # Step 6: Match user length preference
        comment = self._adjust_to_user_length(comment, user_style)
        
        return comment.strip()
    
    def _remove_ai_formality(self, text: str) -> str:
        """Remove formal AI transitions"""
        for formal in self.FORMAL_TRANSITIONS:
            if text.startswith(formal):
                text = text[len(formal):].strip()
        
        # Replace formal connectors with casual ones
        for formal, casual_list in self.CASUAL_CONNECTORS.items():
            pattern = r'\b' + formal + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                casual = random.choice(casual_list)
                text = re.sub(pattern, casual, text, flags=re.IGNORECASE, count=1)
        
        return text
    
    def _apply_contractions(self, text: str) -> str:
        """
        Apply natural contractions
        Research shows: humans use contractions 70%+ of time in casual writing
        """
        contractions = {
            r'\bdo not\b': "don't",
            r'\bdoes not\b': "doesn't",
            r'\bdid not\b': "didn't",
            r'\bcannot\b': "can't",
            r'\bwill not\b': "won't",
            r'\bwould not\b': "wouldn't",
            r'\bcould not\b': "couldn't",
            r'\bshould not\b': "shouldn't",
            r'\bhave not\b': "haven't",
            r'\bhas not\b': "hasn't",
            r'\bhad not\b': "hadn't",
            r'\bis not\b': "isn't",
            r'\bare not\b': "aren't",
            r'\bwas not\b': "wasn't",
            r'\bwere not\b': "weren't",
            r'\bI am\b': "I'm",
            r'\byou are\b': "you're",
            r'\bhe is\b': "he's",
            r'\bshe is\b': "she's",
            r'\bit is\b': "it's",
            r'\bwe are\b': "we're",
            r'\bthey are\b': "they're",
            r'\bI have\b': "I've",
            r'\byou have\b': "you've",
            r'\bwe have\b': "we've",
            r'\bthey have\b': "they've",
            r'\bI will\b': "I'll",
            r'\byou will\b': "you'll",
            r'\bhe will\b': "he'll",
            r'\bshe will\b': "she'll",
            r'\bwe will\b': "we'll",
            r'\bthey will\b': "they'll",
            r'\bthat is\b': "that's",
            r'\bthere is\b': "there's",
            r'\bwhat is\b': "what's",
            r'\bwho is\b': "who's",
            r'\bwhere is\b': "where's",
            r'\bwhen is\b': "when's",
            r'\bwhy is\b': "why's",
            r'\bhow is\b': "how's"
        }
        
        for pattern, contraction in contractions.items():
            text = re.sub(pattern, contraction, text, flags=re.IGNORECASE)
        
        return text
    
    def _vary_sentence_structure(self, text: str) -> str:
        """
        Increase burstiness - vary sentence lengths
        Research: Human writing has high variance in sentence length
        """
        sentences = re.split(r'([.!?]+)', text)
        sentences = [''.join(sentences[i:i+2]) for i in range(0, len(sentences)-1, 2)]
        
        if len(sentences) > 1:
            # Randomly combine or split sentences for variety
            if random.random() < 0.3 and len(sentences) >= 2:
                # Combine two sentences occasionally
                idx = random.randint(0, len(sentences)-2)
                combined = sentences[idx].rstrip('.!?') + '. ' + sentences[idx+1]
                sentences = sentences[:idx] + [combined] + sentences[idx+2:]
            
            # Occasionally break a long sentence
            for i, sent in enumerate(sentences):
                words = sent.split()
                if len(words) > 15 and random.random() < 0.25:
                    # Split at a logical point
                    if ' but ' in sent.lower():
                        parts = sent.split(' but ', 1)
                        sentences[i] = parts[0].rstrip() + '.'
                        if i+1 < len(sentences):
                            sentences.insert(i+1, 'But ' + parts[1].lstrip())
                        else:
                            sentences.append('But ' + parts[1].lstrip())
                        break
        
        return ' '.join(sentences)
    
    def _add_conversational_markers(self, text: str, user_style: Dict) -> str:
        """
        Add natural conversation markers
        Research: Casual LinkedIn comments use these 40%+ of time
        """
        # 30% chance to add a natural starter
        if random.random() < 0.3:
            # Check user's typical openings
            user_openings = user_style.get('typical_comment_openings', [])
            if user_openings and random.random() < 0.6:
                # 60% chance to use user's actual opening
                starter = random.choice(user_openings).capitalize()
                if not text.startswith(starter):
                    text = f"{starter} {text[0].lower()}{text[1:]}"
            else:
                # Use natural starters
                starter = random.choice(self.NATURAL_STARTERS)
                if starter:
                    text = f"{starter} {text[0].lower()}{text[1:]}"
        
        # 20% chance to add a casual filler (mid-sentence)
        if random.random() < 0.2 and len(text.split()) > 8:
            filler = random.choice(self.NATURAL_FILLERS)
            words = text.split()
            # Insert after 3-5 words
            insert_pos = random.randint(3, min(5, len(words)-1))
            words.insert(insert_pos, filler)
            text = ' '.join(words)
        
        return text
    
    def _add_natural_imperfections(self, text: str, user_style: Dict) -> str:
        """
        Add strategic imperfections (humans aren't perfect)
        Research: Real LinkedIn comments have natural quirks
        """
        # 40% chance: Remove period at end (casual style)
        if random.random() < 0.4 and text.endswith('.'):
            text = text[:-1]
        
        # 30% chance: Use double space occasionally
        if random.random() < 0.3:
            text = re.sub(r'\.  ', '. ', text)  # Fix any existing
            sentences = text.split('. ')
            if len(sentences) > 1:
                # Add double space once
                join_with_double = random.randint(0, len(sentences)-2)
                result = '. '.join(sentences[:join_with_double+1])
                result += '.  ' + '. '.join(sentences[join_with_double+1:])
                text = result
        
        # 25% chance: Start with lowercase (very casual)
        if random.random() < 0.25 and user_style.get('tone') == 'casual':
            if text[0].isupper() and not text.split()[0].isupper():  # Not acronym
                text = text[0].lower() + text[1:]
        
        # 15% chance: Add ellipsis for trailing thought
        if random.random() < 0.15 and not text.endswith('?'):
            if text.endswith('.'):
                text = text[:-1] + '...'
            else:
                text += '...'
        
        return text
    
    def _adjust_to_user_length(self, text: str, user_style: Dict) -> str:
        """
        Match user's typical length
        Research: Staying within user's normal range feels more authentic
        """
        target_length = user_style.get('avg_comment_length', 40)
        current_length = len(text.split())
        
        # Allow 30% variance
        min_length = int(target_length * 0.7)
        max_length = int(target_length * 1.3)
        
        if current_length < min_length:
            # Too short - don't pad artificially, it's ok to be concise
            pass
        
        elif current_length > max_length:
            # Too long - trim
            sentences = re.split(r'([.!?]+)', text)
            sentences = [''.join(sentences[i:i+2]) for i in range(0, len(sentences)-1, 2)]
            
            # Keep first sentence(s) until we hit max
            result = []
            word_count = 0
            for sent in sentences:
                sent_words = len(sent.split())
                if word_count + sent_words <= max_length:
                    result.append(sent)
                    word_count += sent_words
                else:
                    break
            
            if result:
                text = ' '.join(result)
        
        return text
    
    def calculate_burstiness_score(self, text: str) -> float:
        """
        Calculate burstiness score (for testing)
        Higher = more human-like
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 0.0
        
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        
        # Calculate variance
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        std_dev = variance ** 0.5
        
        # Burstiness = std_dev / mean
        burstiness = std_dev / avg_length if avg_length > 0 else 0
        
        return burstiness


def apply_advanced_humanization(comment: str, user_style: Dict) -> str:
    """
    Main function to humanize a comment
    
    Args:
        comment: Raw AI-generated comment
        user_style: User's writing style preferences
    
    Returns:
        Humanized comment with natural patterns
    """
    humanizer = AdvancedHumanizer()
    return humanizer.humanize_comment(comment, user_style)