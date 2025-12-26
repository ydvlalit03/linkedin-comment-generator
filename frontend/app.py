"""
LinkedIn Comment Generator - Simplified UI
Clean 2-step workflow with inline comment generation
"""
import streamlit as st
import requests
from datetime import datetime
import os

# Configuration
try:
    API_BASE_URL = st.secrets.get("API_BASE_URL", os.getenv("API_BASE_URL", "http://localhost:8000/api"))
except:
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

# Page config
st.set_page_config(
    page_title="LinkedIn Comment Generator",
    page_icon="💬",
    layout="wide"
)

# Custom CSS - Dark theme optimized
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0077B5;
        margin-bottom: 0.5rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #0077B5;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #0077B5;
        padding-bottom: 0.5rem;
    }
    .post-card {
        background: #1e1e1e;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #0077B5;
        margin: 1rem 0;
        color: #e0e0e0;
    }
    .comment-card {
        background: #2a2a2a;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #0077B5;
        margin: 1rem 0;
        color: #e0e0e0;
        transition: all 0.3s ease;
    }
    .comment-card:hover {
        box-shadow: 0 4px 12px rgba(0,119,181,0.3);
        transform: translateY(-2px);
    }
    .stat-box {
        background: #2a2a2a;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #444;
        color: #e0e0e0;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #888;
        margin-bottom: 0.5rem;
    }
    .stat-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #0077B5;
    }
    .analysis-card {
        background: #1a2332;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #0077B5;
        margin: 0.5rem 0;
        color: #e0e0e0;
    }
    .success-badge {
        background: #10b981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        display: inline-block;
        margin-right: 0.5rem;
    }
    .info-badge {
        background: #3b82f6;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        display: inline-block;
        margin-right: 0.5rem;
    }
    .warning-badge {
        background: #f59e0b;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        display: inline-block;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def api_call(method, endpoint, **kwargs):
    """Helper for API calls"""
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        response = requests.request(method, url, **kwargs, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None


def main():
    # Header
    st.markdown('<div class="main-header">💬 LinkedIn Comment Generator</div>', unsafe_allow_html=True)
    st.caption("AI-powered authentic comments in your voice")
    
    # Initialize session state FIRST
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    if 'target_data' not in st.session_state:
        st.session_state.target_data = None
    if 'generated_comments' not in st.session_state:
        st.session_state.generated_comments = {}
    
    # Analytics sidebar
    with st.sidebar:
        st.markdown("### 📊 Session Analytics")
        
        # System status
        try:
            health = api_call("GET", "health")
            if health:
                st.success("✅ System Online")
                st.caption(f"AI: {health.get('ai_provider', 'Unknown')}")
            else:
                st.error("❌ System Offline")
        except:
            st.error("❌ Backend Unavailable")
        
        st.markdown("---")
        
        # Profile stats
        if st.session_state.user_profile:
            st.markdown("### 👤 Your Profile")
            writing_style = st.session_state.user_profile.get('writing_style', {})
            
            st.metric("Voice Loaded", "✓ Active")
            st.caption(f"Tone: {writing_style.get('tone', 'N/A')[:20]}")
            st.caption(f"Avg: {writing_style.get('avg_comment_length', 40)} words")
            
            recipe = writing_style.get('generation_recipe', {})
            if recipe:
                with st.expander("📋 Recipe Details"):
                    st.caption(f"Form: {recipe.get('form', 'N/A')}")
                    st.caption(f"Style: {recipe.get('glue', 'N/A')[:30]}...")
        
        st.markdown("---")
        
        # Generation stats
        total_generated = len(st.session_state.generated_comments)
        if total_generated > 0:
            st.markdown("### 💬 Generation Stats")
            
            st.metric("Posts Analyzed", total_generated)
            
            total_comments = sum(
                len(data.get('comments', [])) 
                for data in st.session_state.generated_comments.values()
            )
            st.metric("Comments Created", total_comments)
            
            # Calculate average confidence
            all_confidences = []
            for data in st.session_state.generated_comments.values():
                for comment in data.get('comments', []):
                    conf = comment.get('confidence', 0)
                    if conf:
                        all_confidences.append(conf)
            
            if all_confidences:
                avg_confidence = sum(all_confidences) / len(all_confidences)
                st.metric("Avg Confidence", f"{avg_confidence:.0%}")
            
            # Word count stats
            all_word_counts = []
            for data in st.session_state.generated_comments.values():
                for comment in data.get('comments', []):
                    validation = comment.get('validation', {})
                    wc = validation.get('word_count')
                    if wc:
                        all_word_counts.append(wc)
            
            if all_word_counts:
                avg_words = sum(all_word_counts) / len(all_word_counts)
                st.metric("Avg Words/Comment", f"{avg_words:.0f}")
                
                with st.expander("📈 Detailed Stats"):
                    st.caption(f"Min: {min(all_word_counts)} words")
                    st.caption(f"Max: {max(all_word_counts)} words")
                    st.caption(f"Target: {writing_style.get('avg_comment_length', 40)} words")
            
            # Validation stats
            valid_count = 0
            total_count = 0
            quality_scores = []
            
            for data in st.session_state.generated_comments.values():
                for comment in data.get('comments', []):
                    total_count += 1
                    validation = comment.get('validation', {})
                    if validation.get('valid'):
                        valid_count += 1
                    
                    # Get quality score
                    quality = validation.get('quality_score')
                    if quality is not None:
                        quality_scores.append(quality)
            
            if total_count > 0:
                validation_rate = (valid_count / total_count) * 100
                st.metric("Pass Rate", f"{validation_rate:.0f}%")
                
                if quality_scores:
                    avg_quality = sum(quality_scores) / len(quality_scores)
                    st.metric("Avg Quality", f"{avg_quality:.0f}/100")
                
                with st.expander("📊 Quality Breakdown"):
                    st.caption(f"✓ Passed: {valid_count}/{total_count}")
                    st.caption(f"⚠ Warnings: {total_count - valid_count}")
                    
                    if quality_scores:
                        st.caption(f"Best: {max(quality_scores)}/100")
                        st.caption(f"Worst: {min(quality_scores)}/100")
        else:
            st.markdown("### 💡 Quick Guide")
            st.caption("1. Load your profile")
            st.caption("2. Enter target URL")
            st.caption("3. Generate comments")
            st.caption("4. Copy & use!")
        
        st.markdown("---")
        
        # Clear session
        if st.button("🔄 Clear Session", use_container_width=True):
            st.session_state.generated_comments = {}
            st.rerun()
    
    # ============================================
    # STEP 1: YOUR PROFILE
    # ============================================
    st.markdown('<div class="section-header">📝 Step 1: Your Profile</div>', unsafe_allow_html=True)
    
    profiles_data = api_call("GET", "user/profiles/available")
    
    if profiles_data and profiles_data.get('profiles'):
        profiles = profiles_data['profiles']
        
        profile_options = {f"{p['name']} (@{p['username']})": p for p in profiles}
        selected = st.selectbox("Select your profile:", list(profile_options.keys()), key="profile_selector")
        
        if selected:
            profile = profile_options[selected]
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{profile['name']}**")
                st.caption(profile.get('headline', 'LinkedIn Professional'))
            
            with col2:
                if st.button("✅ Load Profile", type="primary", use_container_width=True):
                    with st.spinner("Loading your voice profile..."):
                        result = api_call("POST", "user/profile", json={"linkedin_url": profile['profile_url']})
                        if result:
                            st.session_state.user_profile = result
                            st.success("✅ Profile loaded!")
                            st.rerun()
            
            # Show analysis if loaded
            if st.session_state.user_profile:
                st.markdown("---")
                st.markdown("#### 📊 Your Voice Analysis")
                
                writing_style = st.session_state.user_profile.get('writing_style', {})
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown('<div class="stat-box">', unsafe_allow_html=True)
                    st.markdown('<div class="stat-label">Avg Length</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="stat-value">{writing_style.get("avg_comment_length", 40)}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="stat-label">words</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="stat-box">', unsafe_allow_html=True)
                    st.markdown('<div class="stat-label">Tone</div>', unsafe_allow_html=True)
                    tone = writing_style.get("tone", "professional")
                    st.markdown(f'<div class="stat-value" style="font-size:1.2rem;">{tone[:15]}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col3:
                    st.markdown('<div class="stat-box">', unsafe_allow_html=True)
                    st.markdown('<div class="stat-label">Examples</div>', unsafe_allow_html=True)
                    examples = len(writing_style.get("real_comment_examples", []))
                    st.markdown(f'<div class="stat-value">{examples}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col4:
                    st.markdown('<div class="stat-box">', unsafe_allow_html=True)
                    st.markdown('<div class="stat-label">Confidence</div>', unsafe_allow_html=True)
                    confidence = writing_style.get("confidence", "moderate")
                    st.markdown(f'<div class="stat-value" style="font-size:1.2rem;">{str(confidence)[:8]}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Detailed analysis (collapsible)
                with st.expander("📋 View Complete Analysis"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Voice Profile:**")
                        st.write(f"• Voice Archetype: {writing_style.get('voice_archetype', 'N/A')}")
                        formality = writing_style.get('formality_score')
                        if formality is not None:
                            st.write(f"• Formality: {formality:.2f}")
                        burstiness = writing_style.get('burstiness_level', 'N/A')
                        st.write(f"• Burstiness: {burstiness}")
                        
                        connectives = writing_style.get('common_connectives', [])
                        if connectives:
                            st.markdown("**Signature Connectives:**")
                            st.write(", ".join(f'"{c}"' for c in connectives[:5]))
                    
                    with col2:
                        recipe = writing_style.get('generation_recipe', {})
                        if recipe:
                            st.markdown("**Generation Recipe:**")
                            st.write(f"• Form: {recipe.get('form', 'N/A')}")
                            st.write(f"• Structure: {recipe.get('glue', 'N/A')}")
                            st.write(f"• Punctuation: {recipe.get('punctuation', 'N/A')}")
                        
                        openings = writing_style.get('typical_comment_openings', [])
                        if openings:
                            st.markdown("**Typical Openings:**")
                            for opening in openings[:3]:
                                st.write(f'• "{opening}"')
    else:
        st.warning("⚠️ No profiles found. Add JSON profiles to `backend/user_profiles/` folder.")
    
    # ============================================
    # STEP 2: TARGET & GENERATE
    # ============================================
    
    if not st.session_state.user_profile:
        st.info("👆 Please load your profile first")
        return
    
    st.markdown('<div class="section-header">🎯 Step 2: Target & Generate Comments</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        target_url = st.text_input(
            "Target's LinkedIn Profile URL:",
            placeholder="https://linkedin.com/in/username",
            key="target_url_input"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        analyze_clicked = st.button("🔍 Analyze Target", type="primary", use_container_width=True)
    
    if analyze_clicked and target_url:
        with st.spinner("Analyzing target profile and fetching posts..."):
            result = api_call(
                "POST",
                "target/analyze",
                json={
                    "user_id": st.session_state.user_profile['user_id'],
                    "target_url": target_url
                }
            )
            if result:
                st.session_state.target_data = result
                st.success("✅ Target analyzed!")
                st.rerun()
    
    # Show target analysis and posts
    if st.session_state.target_data:
        st.markdown("---")
        st.markdown("### 📄 Recent Posts")
        
        posts = st.session_state.target_data.get('posts', [])
        
        if posts:
            st.caption(f"Found {len(posts)} posts. Click 'Generate Comments' to create authentic responses.")
            
            for post in posts[:10]:
                post_id = post['post_id']
                
                st.markdown('<div class="post-card">', unsafe_allow_html=True)
                
                # Post content
                st.markdown(f"**Post {post_id}**")
                content = post.get('content', '')
                st.write(content[:200] + "..." if len(content) > 200 else content)
                
                # Post stats
                col1, col2, col3, col4 = st.columns([2, 2, 2, 3])
                with col1:
                    st.caption(f"👍 {post.get('likes_count', 0)} likes")
                with col2:
                    st.caption(f"💬 {post.get('comments_count', 0)} comments")
                with col3:
                    st.caption(f"📅 {post.get('posted_date', 'N/A')}")
                with col4:
                    if st.button(f"✨ Generate Comments", key=f"gen_{post_id}", use_container_width=True):
                        with st.spinner("Generating authentic comments..."):
                            comments_result = api_call(
                                "POST",
                                "comments/generate",
                                json={
                                    "user_id": st.session_state.user_profile['user_id'],
                                    "post_id": post_id,
                                    "post_url": post.get('post_url', '')
                                }
                            )
                            if comments_result:
                                st.session_state.generated_comments[post_id] = comments_result
                                st.rerun()
                
                # Show generated comments if they exist
                if post_id in st.session_state.generated_comments:
                    st.markdown("---")
                    comments_data = st.session_state.generated_comments[post_id]
                    comments = comments_data.get('comments', [])
                    analysis = comments_data.get('analysis', {})
                    
                    # Post Analysis Header
                    st.markdown("#### 📊 Post Analysis")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f'<span class="info-badge">Type: {analysis.get("post_topic", "General")}</span>', unsafe_allow_html=True)
                    with col2:
                        st.markdown(f'<span class="info-badge">Sentiment: {analysis.get("post_sentiment", "Neutral")}</span>', unsafe_allow_html=True)
                    with col3:
                        st.markdown(f'<span class="info-badge">Generated: {len(comments)} comments</span>', unsafe_allow_html=True)
                    
                    # Detailed Analysis (Collapsible)
                    with st.expander("📋 View Detailed Post Analysis"):
                        # Get post context from backend if available
                        st.markdown("**Post Context:**")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.caption(f"**User Tone Applied:** {analysis.get('user_tone', 'N/A')}")
                            st.caption(f"**Post Topic:** {analysis.get('post_topic', 'N/A')}")
                            st.caption(f"**Sentiment:** {analysis.get('post_sentiment', 'N/A')}")
                        
                        with col2:
                            # Show comment stats
                            word_counts = []
                            confidences = []
                            for comment in comments:
                                validation = comment.get('validation', {})
                                if validation.get('word_count'):
                                    word_counts.append(validation['word_count'])
                                if comment.get('confidence'):
                                    confidences.append(comment['confidence'])
                            
                            if word_counts:
                                st.caption(f"**Word Range:** {min(word_counts)}-{max(word_counts)} words")
                            if confidences:
                                avg_conf = sum(confidences) / len(confidences)
                                st.caption(f"**Avg Confidence:** {avg_conf:.0%}")
                    
                    st.markdown("#### 💬 Generated Comments:")
                    
                    for i, comment in enumerate(comments, 1):
                        st.markdown('<div class="comment-card">', unsafe_allow_html=True)
                        
                        # Header with metrics
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.markdown(f"**Variation {i}**")
                        with col2:
                            confidence = comment.get('confidence', 0.85)
                            conf_pct = f"{confidence:.0%}" if confidence else "85%"
                            st.markdown(f'<span class="info-badge">AI: {conf_pct}</span>', unsafe_allow_html=True)
                        with col3:
                            validation = comment.get('validation', {})
                            quality = validation.get('quality_score', 100)
                            quality_color = "success" if quality >= 80 else "info" if quality >= 60 else "warning"
                            st.markdown(f'<span class="{quality_color}-badge">Q: {quality}/100</span>', unsafe_allow_html=True)
                        
                        # Comment text
                        st.markdown(f"_{comment.get('text', 'N/A')}_")
                        
                        # Metadata row
                        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                        
                        with col1:
                            st.caption(f"Style: {comment.get('approach', 'authentic')}")
                        
                        with col2:
                            if validation:
                                word_count = validation.get('word_count', 'N/A')
                                is_valid = validation.get('valid', False)
                                status = "✓" if is_valid else "⚠"
                                target_range = validation.get('target_range', 'N/A')
                                st.caption(f"{status} {word_count} words (target: {target_range})")
                        
                        with col3:
                            # Show validation status
                            if validation:
                                if validation.get('strict_valid'):
                                    st.caption("✓ Perfect")
                                elif validation.get('valid'):
                                    st.caption("✓ Good")
                                else:
                                    st.caption("⚠ Issues")
                        
                        with col4:
                            if st.button("📋", key=f"copy_{post_id}_{i}", help="Copy comment"):
                                st.code(comment.get('text', ''), language=None)
                        
                        # Show issues and warnings
                        if validation:
                            issues = validation.get('issues', [])
                            warnings = validation.get('warnings', [])
                            
                            if issues:
                                for issue in issues:
                                    st.caption(f"❌ {issue}")
                            
                            if warnings:
                                for warning in warnings[:2]:  # Show max 2 warnings
                                    st.caption(f"⚠️ {warning}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No posts found for this target.")


if __name__ == "__main__":
    main()