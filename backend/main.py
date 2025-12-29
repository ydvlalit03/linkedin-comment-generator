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

# Import profile analyzer with fallback: Anthropic -> Gemini
profile_analyzer = None
analyzer_used = None

# Try Anthropic first (Claude Opus 4 with extended thinking - best quality)
if settings.AI_PROVIDER == "anthropic" or (hasattr(settings, 'ANTHROPIC_API_KEY') and settings.ANTHROPIC_API_KEY):
    try:
        from app.services.profile_analyzer_anthropic import ProfileAnalyzer
        profile_analyzer = ProfileAnalyzer()
        analyzer_used = "anthropic"
        logger.info("✓ Using Anthropic Claude Opus 4 with Extended Thinking for analysis")
    except Exception as e:
        logger.warning(f"⚠️ Anthropic analyzer not available: {e}")

# Fallback to Gemini
if not profile_analyzer:
    try:
        from app.services.profile_analyzer_gemini import ProfileAnalyzer
        profile_analyzer = ProfileAnalyzer()
        analyzer_used = "gemini"
        logger.info("✓ Using Gemini 2.0 Flash for analysis (fallback)")
    except Exception as e:
        logger.error(f"✗ No analyzer available: {e}")
        raise RuntimeError("No profile analyzer could be initialized")

# Import comment generator with fallback chain: Anthropic -> OpenAI -> Gemini
comment_generator = None
generator_used = None

# Try Anthropic first (Claude Sonnet 4.5)
if settings.AI_PROVIDER == "anthropic" or (hasattr(settings, 'ANTHROPIC_API_KEY') and settings.ANTHROPIC_API_KEY):
    try:
        from app.services.comment_generator_anthropic import CommentGenerator
        comment_generator = CommentGenerator()
        generator_used = "anthropic"
        logger.info("✓ Using Anthropic Claude Sonnet 4.5 for comment generation")
    except Exception as e:
        logger.warning(f"⚠️ Anthropic not available: {e}")

# Try OpenAI second
if not comment_generator and (settings.AI_PROVIDER == "openai" or (hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY)):
    try:
        from app.services.comment_generator_openai import CommentGenerator
        comment_generator = CommentGenerator()
        generator_used = "openai"
        logger.info("✓ Using OpenAI GPT for comment generation")
    except Exception as e:
        logger.warning(f"⚠️ OpenAI not available: {e}")

# Fallback to Gemini (free)
if not comment_generator:
    try:
        from app.services.comment_generator_gemini import CommentGenerator
        comment_generator = CommentGenerator()
        generator_used = "gemini"
        logger.info("✓ Using Gemini (FREE) for comment generation")
    except Exception as e:
        logger.error(f"❌ All comment generators failed! {e}")
        raise Exception("No comment generator available. Please configure at least one AI provider.")

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
# profile_analyzer already initialized above
# comment_generator initialized above with fallback chain


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
        "ai_provider": generator_used,
        "analyzer": analyzer_used,
        "data_source": settings.DATA_SOURCE,
        "services": {
            "linkedin_fetcher": "connected",
            "ai_generator": f"{generator_used} (active)",
            "profile_analyzer": f"{analyzer_used} (active)"
        }
    }


@app.get("/api/debug/database")
async def debug_database():
    """Debug endpoint to see database state"""
    return {
        "users": {k: {
            "id": v["id"],
            "name": v.get("name"),
            "has_complete_profile": "profile_data" in v,
            "has_professional_data": "professional" in v,
            "writing_style_keys": len(v.get("writing_style", {})),
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


@app.get("/api/user/profiles/available")
async def list_available_profiles():
    """
    List all available user profiles from user_profiles/ folder
    For frontend dropdown selection
    """
    try:
        profiles = linkedin_service.list_saved_profiles()
        
        # Load basic info for each profile
        profile_list = []
        for username in profiles:
            saved_profile = linkedin_service.profile_manager.load_profile(username)
            if saved_profile:
                basic_info = saved_profile.get("basic_info", {})
                profile_list.append({
                    "username": username,
                    "name": basic_info.get("name", username),
                    "headline": basic_info.get("headline", ""),
                    "profile_url": basic_info.get("profile_url", f"https://linkedin.com/in/{username}")
                })
        
        return {
            "profiles": profile_list,
            "total": len(profile_list)
        }
        
    except Exception as e:
        logger.error(f"Error listing profiles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/user/profile", response_model=ProfileResponse)
async def create_user_profile(request: ProfileRequest):
    """
    Load user profile from JSON file ONLY (no API calls)
    Returns user_id and writing style analysis
    
    User profiles must exist in user_profiles/ folder
    """
    try:
        logger.info(f"📥 Received linkedin_url: '{request.linkedin_url}'")
        
        # Step 1: Load from JSON ONLY (no API fallback)
        username = linkedin_service._extract_username(request.linkedin_url)
        logger.info(f"📝 Extracted username: '{username}'")
        
        saved_profile = linkedin_service.profile_manager.load_profile(username)
        
        if not saved_profile:
            raise HTTPException(
                status_code=404, 
                detail=f"Profile '{username}' not found in user_profiles/ folder. Please add {username}.json file."
            )
        
        logger.info(f"✓ Loaded profile: {username}")
        logger.info(f"✓ Profile has {len(saved_profile)} top-level keys")
        
        # Step 2: Convert from JSON format
        profile_data = linkedin_service._convert_from_json_format(saved_profile)
        
        # Step 3: Analyze user writing style from complete JSON profile
        logger.info("🔍 STAGE 1: Analyzing user writing style from JSON...")
        
        # Extract real comment examples from JSON
        real_comments = saved_profile.get("real_comment_examples", [])
        if not real_comments:
            real_comments = saved_profile.get("real_comments", [])
        
        # Convert to comment objects for analyzer
        comment_objects = []
        for comment in real_comments:
            if isinstance(comment, dict):
                comment_objects.append({"comment_text": comment.get("text", "")})
            else:
                comment_objects.append({"comment_text": str(comment)})
        
        # Call profile analyzer with COMPLETE JSON data
        writing_style = profile_analyzer.analyze_user_writing_style(
            saved_profile,  # Pass complete JSON profile
            comment_objects
        )
        
        logger.info(f"✅ User analysis complete: {len(writing_style)} top-level fields extracted")
        
        # Step 4: Store in database with COMPLETE data
        user_id = len(users_db) + 1
        users_db[user_id] = {
            "id": user_id,
            "linkedin_url": request.linkedin_url,
            "username": username,
            "name": profile_data.get("name"),
            "headline": profile_data.get("headline"),
            "about": profile_data.get("about"),
            
            # ⭐ COMPLETE PROFILE DATA (82+ fields)
            "profile_data": saved_profile,  # Full JSON with all sections
            "writing_style": writing_style,  # Analyzed + merged data
            
            # ⭐ PROFESSIONAL DATA (extracted for easy access)
            "professional": {
                "expertise_areas": saved_profile.get("professional", {}).get("expertise_areas", []),
                "experience": saved_profile.get("professional", {}).get("experience", []),
                "skills": saved_profile.get("professional", {}).get("skills", []),
                "industry": saved_profile.get("basic_info", {}).get("industry", "")
            },
            
            # ⭐ REAL EXAMPLES (for reference)
            "real_examples": {
                "comments": real_comments[:10],  # Keep top 10
                "common_phrases": saved_profile.get("common_phrases", [])
            },
            
            "created_at": datetime.now()
        }
        
        logger.info(f"✅ Stored complete profile with {len(users_db[user_id]['profile_data'])} JSON fields")
        logger.info(f"✅ Writing style has {len(users_db[user_id]['writing_style'])} sections")
        logger.info(f"✅ Professional data: {len(users_db[user_id]['professional'])} fields")
        
        return ProfileResponse(
            user_id=user_id,
            name=profile_data.get("name", ""),
            headline=profile_data.get("headline", ""),
            writing_style=writing_style,
            message=f"Profile loaded from user_profiles/{username}.json with {len(saved_profile)} fields"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading user profile: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
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
        "writing_style": user["writing_style"],
        "has_complete_profile": "profile_data" in user,
        "profile_data_keys": len(user.get("profile_data", {}))
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
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/comments/generate", response_model=GeneratedCommentsResponse)
async def generate_comments(request: CommentGenerationRequest):
    """
    Generate 3 comment variations for a specific post
    This is the core functionality with COMPLETE profile integration!
    """
    try:
        logger.info(f"🎯 Generating comments for post {request.post_id}")
        logger.info(f"Request: user_id={request.user_id}, post_id={request.post_id}")
        
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
        
        logger.info("✓ All data found, building complete user profile...")
        
        # Step 4: Build COMPLETE user profile for generation
        # This merges ALL data sources into one comprehensive profile
        complete_user_profile = {
            # ⭐ Core writing style (analyzed by ProfileAnalyzer)
            **user["writing_style"],
            
            # ⭐ Professional data (easy access to expertise)
            "professional": user.get("professional", {
                "expertise_areas": [],
                "experience": [],
                "skills": [],
                "industry": ""
            }),
            
            # ⭐ Real examples (actual comments for reference)
            "real_examples": user.get("real_examples", {
                "comments": [],
                "common_phrases": []
            }),
            
            # ⭐ Raw profile data (complete JSON with 82+ fields)
            "raw_profile": user.get("profile_data", {})
        }
        
        # Log what we're passing to the generator
        logger.info(f"✅ Complete profile assembled:")
        logger.info(f"   - Writing style keys: {len(user['writing_style'])}")
        logger.info(f"   - Professional fields: {len(complete_user_profile['professional'])}")
        logger.info(f"   - Real examples: {len(complete_user_profile['real_examples'].get('comments', []))}")
        logger.info(f"   - Raw profile sections: {len(complete_user_profile['raw_profile'])}")
        logger.info(f"   - Total top-level keys: {len(complete_user_profile)}")
        
        # Step 5: Fetch post comments for context
        existing_comments = linkedin_service.get_post_comments(
            post["post_url"],
            max_comments=settings.MAX_COMMENTS_ANALYZE
        )
        
        # Step 6: Analyze post context
        logger.info("🔍 Analyzing post context...")
        post_context = profile_analyzer.analyze_post_context(
            post,
            existing_comments
        )
        logger.info(f"✅ Post context analyzed: {len(post_context)} fields")
        
        # Step 7: Generate comments with COMPLETE data!
        logger.info("🚀 Generating comments with complete profile data...")
        logger.info(f"   - User profile: {len(complete_user_profile)} keys")
        logger.info(f"   - Target insights: {len(target['insights'])} keys")
        logger.info(f"   - Post context: {len(post_context)} keys")
        
        generated = comment_generator.generate_comments(
            user_style=complete_user_profile,  # ⭐ ALL 82+ fields!
            target_profile=target["insights"],  # 10+ fields
            post_context=post_context,  # 12+ fields
            post_content=post["content"]
        )
        
        logger.info(f"✅ Generated {len(generated)} comment variations")
        
        # Step 8: Store generated comments
        # ✅ FIX: Use 'variation_number' instead of 'variation'
        for comment in generated:
            comment_id = len(comments_db) + 1
            comments_db[comment_id] = {
                "id": comment_id,
                "user_id": request.user_id,
                "post_id": request.post_id,
                "text": comment.get("text", ""),
                "variation": comment.get("variation_number", 1),  # ✅ FIXED
                "confidence": comment.get("confidence", 0.85),
                "created_at": datetime.now()
            }
        
        # Step 9: Return results
        # ✅ FIX: Use 'variation_number' instead of 'variation'
        comment_responses = [
            CommentResponse(
                text=c.get("text", ""),
                variation=c.get("variation_number", idx + 1),  # ✅ FIXED
                confidence=c.get("confidence", 0.85),
                approach=c.get("approach", "context-aware")
            )
            for idx, c in enumerate(generated)
        ]
        
        return GeneratedCommentsResponse(
            comments=comment_responses,
            analysis={
                "post_topic": post_context.get("main_topic"),
                "post_sentiment": post_context.get("sentiment"),
                "user_tone": user["writing_style"].get("tone"),
                "generation_timestamp": datetime.now().isoformat(),
                "profile_completeness": {
                    "writing_style_fields": len(user["writing_style"]),
                    "professional_fields": len(complete_user_profile["professional"]),
                    "real_examples": len(complete_user_profile["real_examples"].get("comments", [])),
                    "total_fields_used": len(complete_user_profile)
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating comments: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
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