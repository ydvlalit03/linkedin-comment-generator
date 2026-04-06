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
    batch_id: Optional[str] = None
    batchId: Optional[str] = None

    @property
    def get_batch_id(self) -> str:
        return self.batch_id or self.batchId or "default"


class AnalyzeRequest(BaseModel):
    post_id: Optional[int] = None
    postId: Optional[int] = None

    @property
    def get_post_id(self) -> int:
        return self.post_id or self.postId or 0


class GenerateRequest(BaseModel):
    post_id: Optional[int] = None
    postId: Optional[int] = None
    comment_tone: Optional[str] = None  # user override; None = let LLM decide

    @property
    def get_post_id(self) -> int:
        return self.post_id or self.postId or 0


class ProfileSaveRequest(BaseModel):
    name: str
    username: str
    headline: str = ""
    profile_data: dict = {}
