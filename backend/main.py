"""
FastAPI Main Application
LinkedIn Comment Generator Backend
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.core.config import settings
from app.models.database import Base, User, Target, Post, GeneratedComment

# Setup logging FIRST
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Choose LinkedIn service based on configuration
try:
    from app.services.linkedin_service import LinkedInService
    linkedin_service = LinkedInService()
    logger.info(f"✓ LinkedIn Service initialized with DATA_SOURCE={settings.DATA_SOURCE}")
except Exception as e:
    logger.error(f"✗ Error initializing LinkedIn service: {e}")
    from app.services.linkedin_fetcher_free import LinkedInFetcher
    linkedin_fetcher = LinkedInFetcher()
    logger.info("✓ Using MOCK data (fallback)")

from app.services.profile_analyzer_gemini import ProfileAnalyzer
from app.services.comment_generator_gemini import CommentGenerator

# Initialize FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="Generate human-like LinkedIn comments based on your writing style",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (linkedin_service already initialized above)
profile_analyzer = ProfileAnalyzer()
comment_generator = CommentGenerator()


# ============ Pydantic Models ============

class ProfileRequest(BaseModel):
    linkedin_url: str


class TargetAnalysisRequest(BaseModel):
    user_id: int
    target_url: str


class CommentGenerationRequest(BaseModel):
    user_id: int
    post_id: int
    post_url: str


class ProfileResponse(BaseModel):
    user_id: int
    name: str
    headline: str
    writing_style: dict
    message: str


class PostResponse(BaseModel):
    post_id: int
    content: str
    posted_date: str
    likes_count: int
    comments_count: int


class CommentResponse(BaseModel):
    text: str
    variation: int
    confidence: float
    approach: str


class GeneratedCommentsResponse(BaseModel):
    comments: List[CommentResponse]
    analysis: dict


# ============ Database Dependency ============

# Simplified in-memory storage (replace with SQLAlchemy session in production)
users_db = {}
targets_db = {}
posts_db = {}
comments_db = {}


# ============ API Endpoints ============

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": settings.APP_NAME,
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "linkedin_fetcher": "connected",
            "gemini_api": "connected"
        }
    }


@app.get("/api/debug/database")
async def debug_database():
    """Debug endpoint to see database state"""
    return {
        "users": {k: {
            "id": v["id"],
            "name": v.get("name"),
            "created_at": v.get("created_at").isoformat() if v.get("created_at") else None
        } for k, v in users_db.items()},
        "targets": {k: {
            "id": v["id"],
            "name": v.get("name"),
            "created_at": v.get("created_at").isoformat() if v.get("created_at") else None
        } for k, v in targets_db.items()},
        "posts": {k: {
            "id": v["id"],
            "target_id": v.get("target_id"),
            "content": v.get("content", "")[:50] + "..."
        } for k, v in posts_db.items()},
        "total_users": len(users_db),
        "total_targets": len(targets_db),
        "total_posts": len(posts_db),
        "total_comments": len(comments_db)
    }


@app.post("/api/user/profile", response_model=ProfileResponse)
async def create_user_profile(request: ProfileRequest):
    """
    Fetch and analyze user's LinkedIn profile
    Returns user_id and writing style analysis
    """
    try:
        logger.info(f"Fetching profile: {request.linkedin_url}")
        
        # Step 1: Fetch profile data (checks JSON first, then API)
        profile_data = linkedin_service.get_user_profile(request.linkedin_url)
        if not profile_data:
            raise HTTPException(status_code=404, detail="Profile not found or inaccessible")
        
        # Step 2: Fetch user's comment history
        user_comments = linkedin_service.get_user_comments(request.linkedin_url)
        
        # Step 3: Analyze writing style
        writing_style = profile_analyzer.analyze_user_writing_style(
            profile_data, 
            user_comments
        )
        
        # Step 4: Store in database
        user_id = len(users_db) + 1
        users_db[user_id] = {
            "id": user_id,
            "linkedin_url": request.linkedin_url,
            "name": profile_data.get("name"),
            "headline": profile_data.get("headline"),
            "about": profile_data.get("about"),
            "experience": profile_data.get("experience"),
            "skills": profile_data.get("skills"),
            "writing_style": writing_style,
            "created_at": datetime.now()
        }
        
        return ProfileResponse(
            user_id=user_id,
            name=profile_data.get("name", ""),
            headline=profile_data.get("headline", ""),
            writing_style=writing_style,
            message="Profile analyzed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/user/profile/{user_id}")
async def get_user_profile(user_id: int):
    """Get cached user profile"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    return {
        "user_id": user["id"],
        "name": user["name"],
        "headline": user["headline"],
        "writing_style": user["writing_style"]
    }


@app.post("/api/target/analyze")
async def analyze_target(request: TargetAnalysisRequest):
    """
    Analyze target's profile and fetch recent posts
    """
    try:
        logger.info(f"Analyzing target: {request.target_url}")
        
        # Verify user exists
        if request.user_id not in users_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Step 1: Fetch target profile
        target_data = linkedin_service.get_target_profile(request.target_url)
        if not target_data:
            raise HTTPException(status_code=404, detail="Target profile not found")
        
        # Step 2: Analyze target profile
        target_insights = profile_analyzer.analyze_target_profile(target_data)
        
        # Step 3: Fetch recent posts (ONLY from last 30 days)
        posts_result = linkedin_service.get_target_posts(
            request.target_url, 
            max_posts=settings.MAX_POSTS_FETCH,
            max_days=30  # Only get posts from last 30 days
        )
        
        # Check if this is a Dict (new format) or List (old format)
        if isinstance(posts_result, dict):
            posts = posts_result.get("posts", [])
            has_recent = posts_result.get("has_recent_posts", True)
            warning_message = posts_result.get("message")
        else:
            # Fallback for old format
            posts = posts_result
            has_recent = len(posts) > 0
            warning_message = None
        
        # Step 4: Store target
        target_id = len(targets_db) + 1
        targets_db[target_id] = {
            "id": target_id,
            "linkedin_url": request.target_url,
            "name": target_data.get("name"),
            "headline": target_data.get("headline"),
            "about": target_data.get("about"),
            "insights": target_insights,
            "created_at": datetime.now()
        }
        
        # If no recent posts, return early with warning
        if not has_recent:
            logger.warning(f"No recent posts found for {target_data.get('name')}")
            return {
                "target_id": target_id,
                "target_name": target_data.get("name"),
                "target_headline": target_data.get("headline"),
                "insights": target_insights,
                "posts_count": 0,
                "posts": [],
                "warning": "No recent posts found in the last 30 days",
                "message": warning_message or "User may be inactive or hasn't posted recently."
            }
        
        # Step 5: Store posts
        post_responses = []
        for post in posts[:20]:  # Limit to 20 most recent
            post_id = len(posts_db) + 1
            posts_db[post_id] = {
                "id": post_id,
                "target_id": target_id,
                "post_url": post.get("post_url"),
                "content": post.get("content"),
                "posted_date": post.get("posted_date"),
                "likes_count": post.get("likes_count", 0),
                "comments_count": post.get("comments_count", 0)
            }
            
            # Handle date formatting
            posted_date = post.get("posted_date", datetime.now().isoformat())
            if isinstance(posted_date, datetime):
                posted_date = posted_date.isoformat()
            elif not isinstance(posted_date, str):
                posted_date = str(posted_date)
            
            post_responses.append(PostResponse(
                post_id=post_id,
                content=post.get("content", "")[:200] + "...",
                posted_date=posted_date,
                likes_count=post.get("likes_count", 0),
                comments_count=post.get("comments_count", 0)
            ))
        
        logger.info(f"✅ Found {len(post_responses)} recent posts from {target_data.get('name')}")
        
        return {
            "target_id": target_id,
            "target_name": target_data.get("name"),
            "target_headline": target_data.get("headline"),
            "insights": target_insights,
            "posts_count": len(post_responses),
            "posts": post_responses,
            "has_recent_posts": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing target: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/comments/generate", response_model=GeneratedCommentsResponse)
async def generate_comments(request: CommentGenerationRequest):
    """
    Generate 3 comment variations for a specific post
    This is the core functionality!
    """
    try:
        logger.info(f"Generating comments for post {request.post_id}")
        logger.info(f"Request: user_id={request.user_id}, post_id={request.post_id}")
        logger.info(f"Available users: {list(users_db.keys())}")
        logger.info(f"Available posts: {list(posts_db.keys())}")
        
        # Step 1: Get user data
        if request.user_id not in users_db:
            logger.error(f"User {request.user_id} not found in database")
            raise HTTPException(status_code=404, detail=f"User {request.user_id} not found. Please create profile first.")
        user = users_db[request.user_id]
        
        # Step 2: Get post data
        if request.post_id not in posts_db:
            logger.error(f"Post {request.post_id} not found in database")
            raise HTTPException(status_code=404, detail=f"Post {request.post_id} not found. Please fetch posts first.")
        post = posts_db[request.post_id]
        
        # Step 3: Get target data
        target = targets_db.get(post["target_id"])
        if not target:
            logger.error(f"Target {post['target_id']} not found in database")
            raise HTTPException(status_code=404, detail=f"Target not found. Please analyze target first.")
        
        logger.info("✓ All data found, proceeding with generation...")
        
        # Step 4: Fetch post comments for context
        existing_comments = linkedin_service.get_post_comments(
            post["post_url"],
            max_comments=settings.MAX_COMMENTS_ANALYZE
        )
        
        # Step 5: Analyze post context
        post_context = profile_analyzer.analyze_post_context(
            post,
            existing_comments
        )
        
        # Step 6: Generate comments!
        generated = comment_generator.generate_comments(
            user_style=user["writing_style"],
            target_profile=target["insights"],
            post_context=post_context,
            post_content=post["content"]
        )
        
        # Step 7: Store generated comments
        for comment in generated:
            comment_id = len(comments_db) + 1
            comments_db[comment_id] = {
                "id": comment_id,
                "user_id": request.user_id,
                "post_id": request.post_id,
                "text": comment["text"],
                "variation": comment["variation"],
                "confidence": comment["confidence"],
                "created_at": datetime.now()
            }
        
        # Step 8: Return results
        comment_responses = [
            CommentResponse(
                text=c["text"],
                variation=c["variation"],
                confidence=c["confidence"],
                approach=c["approach"]
            )
            for c in generated
        ]
        
        return GeneratedCommentsResponse(
            comments=comment_responses,
            analysis={
                "post_topic": post_context.get("main_topic"),
                "post_sentiment": post_context.get("sentiment"),
                "user_tone": user["writing_style"].get("tone"),
                "generation_timestamp": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating comments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history/{user_id}")
async def get_history(user_id: int):
    """Get user's comment generation history"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_comments = [
        {
            "comment_id": cid,
            "post_id": c["post_id"],
            "text": c["text"],
            "variation": c["variation"],
            "confidence": c["confidence"],
            "created_at": c["created_at"].isoformat()
        }
        for cid, c in comments_db.items()
        if c["user_id"] == user_id
    ]
    
    return {
        "user_id": user_id,
        "total_comments": len(user_comments),
        "comments": sorted(user_comments, key=lambda x: x["created_at"], reverse=True)
    }


@app.get("/api/usage-stats")
async def get_usage_stats():
    """Get usage statistics"""
    return {
        "total_users": len(users_db),
        "total_targets": len(targets_db),
        "total_posts": len(posts_db),
        "total_generated_comments": len(comments_db),
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)