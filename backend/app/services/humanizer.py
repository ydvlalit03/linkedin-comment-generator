"""Advanced Comment Humanizer — burstiness, contractions, imperfections"""
import re
import random
import logging

log = logging.getLogger("humanizer")

FORMAL_TRANSITIONS = [
    "In conclusion,", "To summarize,", "Furthermore,", "Moreover,",
    "Additionally,", "Consequently,", "Nevertheless,", "Subsequently,",
    "Ultimately,", "Initially,", "In essence,", "Essentially,", "Fundamentally,",
]

CASUAL_CONNECTORS = {
    "however": ["but", "though", "still"], "therefore": ["so", "meaning"],
    "additionally": ["also", "plus", "and"], "furthermore": ["plus", "and"],
    "moreover": ["also", "plus"], "consequently": ["so", "meaning"],
    "nevertheless": ["but", "still"], "thus": ["so"], "hence": ["so"],
    "regarding": ["about", "on"], "subsequently": ["then", "later"],
    "ultimately": ["in the end", "finally"],
}

AI_WORDS = {
    "leverage": "use", "navigate": "deal with", "unlock": "find",
    "empower": "help", "delve": "dig into", "foster": "build",
    "robust": "strong", "seamless": "smooth", "holistic": "full",
    "transformative": "big", "innovative": "new", "optimize": "improve",
    "streamline": "simplify", "catalyze": "start", "spearhead": "lead",
}

CONTRACTIONS = [
    (r"\bdo not\b", "don't"), (r"\bdoes not\b", "doesn't"), (r"\bdid not\b", "didn't"),
    (r"\bcannot\b", "can't"), (r"\bwill not\b", "won't"), (r"\bwould not\b", "wouldn't"),
    (r"\bcould not\b", "couldn't"), (r"\bshould not\b", "shouldn't"),
    (r"\bis not\b", "isn't"), (r"\bare not\b", "aren't"),
    (r"\bI am\b", "I'm"), (r"\byou are\b", "you're"), (r"\bit is\b", "it's"),
    (r"\bwe are\b", "we're"), (r"\bthey are\b", "they're"),
    (r"\bI have\b", "I've"), (r"\bwe have\b", "we've"),
    (r"\bthat is\b", "that's"), (r"\bthere is\b", "there's"),
]


def humanize(comment: str, tone: str = "professional", avg_len: int = 45) -> str:
    changes = []
    text = comment

    # 1. Remove AI formality
    before = text
    for f in FORMAL_TRANSITIONS:
        if text.startswith(f):
            text = text[len(f):].strip()
    for formal, casual_list in CASUAL_CONNECTORS.items():
        pat = re.compile(r"\b" + formal + r"\b", re.I)
        if pat.search(text):
            text = pat.sub(random.choice(casual_list), text, count=1)
    for word, repl in AI_WORDS.items():
        pat = re.compile(r"\b" + word + r"\b", re.I)
        text = pat.sub(repl, text)
    if text != before:
        changes.append("removed AI formality")

    # 2. Contractions
    before = text
    for pat, repl in CONTRACTIONS:
        text = re.sub(pat, repl, text, flags=re.I)
    if text != before:
        changes.append("contractions")

    # 3. Imperfections
    before = text
    if random.random() < 0.4 and text.endswith("."):
        text = text[:-1]
    if random.random() < 0.15 and not text.endswith("?"):
        text = (text[:-1] if text.endswith(".") else text) + "..."
    if text != before:
        changes.append("imperfections")

    # 4. Trim to length
    words = text.split()
    max_len = int(avg_len * 1.3)
    if len(words) > max_len:
        sentences = re.split(r"([.!?]+\s*)", text)
        result, count = "", 0
        for i in range(0, len(sentences), 2):
            s = sentences[i] + (sentences[i + 1] if i + 1 < len(sentences) else "")
            if count + len(s.split()) <= max_len:
                result += s
                count += len(s.split())
            else:
                break
        if result:
            text = result
            changes.append("trimmed")

    if changes:
        log.info(f"Humanized: {' → '.join(changes)}")
    return text.strip()
