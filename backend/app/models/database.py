"""
Database Models
"""
from sqlalchemy import Column, Integer, String, Text, JSON, TIMESTAMP, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User profile cache"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    linkedin_url = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    headline = Column(String)
    about = Column(Text)
    experience = Column(JSON)  # List of experience objects
    skills = Column(JSON)  # List of skills
    writing_style = Column(JSON)  # Analyzed writing style
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, onupdate=func.now())


class UserComment(Base):
    """User's comment history for style learning"""
    __tablename__ = "user_comments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment_text = Column(Text, nullable=False)
    post_context = Column(Text)  # Brief context about the post
    created_at = Column(TIMESTAMP, server_default=func.now())


class Target(Base):
    """Target profile cache"""
    __tablename__ = "targets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    linkedin_url = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    headline = Column(String)
    about = Column(Text)
    experience = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Post(Base):
    """LinkedIn posts"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=False)
    post_url = Column(String, unique=True)
    content = Column(Text, nullable=False)
    media_type = Column(String)  # text, image, video, article, poll
    posted_date = Column(TIMESTAMP)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    sentiment = Column(JSON)  # Analyzed sentiment and themes
    created_at = Column(TIMESTAMP, server_default=func.now())


class PostComment(Base):
    """Comments on posts (for analysis)"""
    __tablename__ = "post_comments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    author_name = Column(String)
    comment_text = Column(Text, nullable=False)
    likes_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())


class GeneratedComment(Base):
    """AI-generated comments"""
    __tablename__ = "generated_comments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    comment_text = Column(Text, nullable=False)
    variation_number = Column(Integer)  # 1, 2, or 3
    confidence_score = Column(Float)  # 0.0 to 1.0
    prompt_used = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())


class APICall(Base):
    """API usage tracking"""
    __tablename__ = "api_calls"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    service = Column(String, nullable=False)  # 'rapidapi' or 'claude'
    endpoint = Column(String)
    tokens_used = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    success = Column(Integer, default=1)  # 1 = success, 0 = failure
    error_message = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())