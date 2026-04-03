from pydantic import BaseModel
from typing import Optional


class PostAnalysis(BaseModel):
    post_type: str = ""
    main_topic: str = ""
    sentiment: str = "neutral"
    emotional_tone: str = "thoughtful"
    post_tone: str = "casual_conversational"
    specific_details: list[str] = []
    key_insights: list[str] = []
    best_response_angles: list[str] = []


class GeneratedComment(BaseModel):
    text: str
    angle: str
    variation: int
    confidence: float
    quality_score: int
    word_count: int
    humanized: bool = True
    issues: list[str] = []
    warnings: list[str] = []


class CommenterProfile(BaseModel):
    name: str = "Professional"
    username: str = "default"
    headline: str = ""
    expertise: list[str] = ["technology", "business"]
    tone: str = "professional, direct"
    avg_comment_length: int = 45
    common_phrases: list[str] = []
    real_comment_examples: list[str] = []
    humor_style: Optional[str] = None


class ScrapeRequest(BaseModel):
    profiles: list[dict]
    batch_id: str


class AnalyzeRequest(BaseModel):
    post_id: int


class GenerateRequest(BaseModel):
    post_id: int


class ProfileSaveRequest(BaseModel):
    name: str
    username: str
    headline: str = ""
    profile_data: dict = {}
