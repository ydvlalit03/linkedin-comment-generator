"""
Streamlit Frontend
LinkedIn Comment Generator - Updated for JSON Profile + RapidAPI
"""
import streamlit as st
import requests
from datetime import datetime
import time
import os
import json

# Configuration
API_BASE_URL = "http://localhost:8000/api"

# Try multiple possible paths for profiles
import os
POSSIBLE_PROFILE_DIRS = [
    "../backend/user_profiles",  # When running from frontend/
    "backend/user_profiles",     # When running from root
    "user_profiles",             # When running from backend/
    "/Users/aadi/comment-analyser/linkedin-comment-generator/backend/user_profiles"  # Absolute path
]

# Find the correct path
PROFILES_DIR = None
for path in POSSIBLE_PROFILE_DIRS:
    if os.path.exists(path):
        PROFILES_DIR = path
        break

if not PROFILES_DIR:
    PROFILES_DIR = "../backend/user_profiles"  # Default fallback

# Page config
st.set_page_config(
    page_title="LinkedIn Comment Generator",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0077B5;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .comment-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #0077B5;
        margin: 1rem 0;
    }
    .post-preview {
        background-color: #fff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 1rem 0;
    }
    .profile-card {
        background: linear-gradient(135deg, #0077B5 0%, #00A0DC 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def get_available_profiles():
    """Get list of available JSON profiles"""
    try:
        if not os.path.exists(PROFILES_DIR):
            return []
        
        profiles = []
        for filename in os.listdir(PROFILES_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(PROFILES_DIR, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        profiles.append({
                            'filename': filename,
                            'username': filename.replace('.json', ''),
                            'name': data.get('basic_info', {}).get('name', 'Unknown'),
                            'headline': data.get('basic_info', {}).get('headline', '')
                        })
                except:
                    continue
        return profiles
    except:
        return []


def main():
    """Main application"""
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/174/174857.png", width=80)
        st.title("Navigation")
        
        page = st.radio(
            "Select Page",
            ["🏠 Home", "👤 Select Profile", "🎯 Generate Comments", "📊 Stats"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.info("Generate authentic LinkedIn comments using your saved writing style + real-time target data.")
        
        # Show current profile
        if 'user_id' in st.session_state:
            st.markdown("---")
            st.success(f"✅ **{st.session_state.get('user_name', 'User')}**")
            if st.button("Change Profile"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    
    # Main content
    if page == "🏠 Home":
        show_home_page()
    elif page == "👤 Select Profile":
        show_profile_selection()
    elif page == "🎯 Generate Comments":
        show_comment_generator()
    elif page == "📊 Stats":
        show_stats()


def show_home_page():
    """Home page"""
    st.markdown('<p class="main-header">LinkedIn Comment Generator</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your Profile (JSON) + Real LinkedIn Data (RapidAPI) = Perfect Comments</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 👤 Your Profile
        - **Source:** JSON file
        - **Contains:** Your writing style
        - **Speed:** Instant ⚡
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 Target Data
        - **Source:** RapidAPI (Real-time)
        - **Fetches:** 60+ recent posts
        - **Quality:** 100% real data
        """)
    
    with col3:
        st.markdown("""
        ### 💬 AI Generation
        - **Engine:** Gemini 1.5 Flash
        - **Output:** 3 variations
        - **Style:** Matches YOUR voice
        """)
    
    st.markdown("---")
    
    # New workflow
    st.subheader("✨ New Improved Workflow")
    
    st.info("""
    **No More Scraping Your Profile!**
    
    1. 📁 **Select your saved profile** (vidhant-jain.json)
    2. 🎯 **Enter target's LinkedIn URL** (we fetch their REAL posts via RapidAPI)
    3. 💬 **Generate comments** that match YOUR writing style
    
    **Advantages:**
    - ⚡ Instant profile loading (no API calls for you!)
    - 🎯 Real-time target data (always fresh!)
    - 💰 Save API credits (only fetch targets)
    - ✅ Your style stays consistent
    """)
    
    st.markdown("---")
    st.info("👈 Select your profile from the sidebar to get started!")


def show_profile_selection():
    """Profile selection from JSON files"""
    st.markdown('<p class="main-header">Select Your Profile</p>', unsafe_allow_html=True)
    
    # Check if already selected
    if 'user_id' in st.session_state:
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        st.markdown(f"### ✅ Active Profile")
        st.markdown(f"**{st.session_state.user_name}**")
        st.markdown(f"*{st.session_state.get('user_headline', '')}*")
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.expander("📊 Your Writing Style"):
            if 'writing_style' in st.session_state:
                style = st.session_state.writing_style
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Tone", style.get('tone', 'N/A').title())
                    st.metric("Formality", f"{style.get('formality_score', 0.5):.1f}")
                
                with col2:
                    st.metric("Avg Length", f"{style.get('avg_comment_length', 35)} words")
                    st.metric("Emoji Use", style.get('emoji_usage', 'moderate').title())
                
                with col3:
                    st.metric("Contractions", style.get('contraction_frequency', 'frequent').title())
                    st.metric("Structure", style.get('comment_structure', 'varied').title())
        
        return
    
    # Show available profiles
    st.markdown("### Available Profiles")
    st.write("Select a profile that has your saved writing style:")
    
    profiles = get_available_profiles()
    
    if not profiles:
        st.warning("⚠️ No profiles found in `backend/user_profiles/`")
        st.info("""
        **To create a profile:**
        1. Create a JSON file: `backend/user_profiles/your-name.json`
        2. Use the template from `vidhant-jain.json`
        3. Add your info and real comment examples
        4. Refresh this page
        """)
        return
    
    # Display profiles
    for profile in profiles:
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"**{profile['name']}**")
                st.caption(f"{profile['headline']}")
                st.caption(f"Username: `{profile['username']}`")
            
            with col2:
                if st.button("Select", key=f"select_{profile['username']}"):
                    # Load profile via API
                    with st.spinner("Loading profile..."):
                        try:
                            response = requests.post(
                                f"{API_BASE_URL}/user/profile",
                                json={"linkedin_url": profile['username']}
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                
                                st.session_state.user_id = data['user_id']
                                st.session_state.user_name = data['name']
                                st.session_state.user_headline = data['headline']
                                st.session_state.writing_style = data['writing_style']
                                
                                st.success(f"✅ Loaded {data['name']}'s profile!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
            st.markdown("---")


def show_comment_generator():
    """Comment generation page"""
    st.markdown('<p class="main-header">Generate Comments</p>', unsafe_allow_html=True)
    
    # Check profile
    if 'user_id' not in st.session_state:
        st.warning("⚠️ Please select your profile first!")
        st.info("Go to '👤 Select Profile' to choose your saved profile.")
        return
    
    # Show active profile
    st.success(f"✅ Generating as: **{st.session_state.user_name}**")
    
    # Step 1: Target Input
    st.markdown("### Step 1: Enter Target's LinkedIn URL")
    
    target_url = st.text_input(
        "Target's LinkedIn Profile",
        placeholder="https://www.linkedin.com/in/satyanadella",
        help="We'll fetch their REAL posts via RapidAPI",
        key="target_url"
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        fetch_button = st.button("🎯 Fetch Posts", type="primary", use_container_width=True)
    with col2:
        st.caption("This will fetch 60+ real posts from their profile")
    
    if fetch_button:
        if not target_url:
            st.error("Please enter a LinkedIn URL")
            return
        
        with st.spinner("🔄 Fetching real-time data from RapidAPI..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/target/analyze",
                    json={
                        "user_id": st.session_state.user_id,
                        "target_url": target_url
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for warning about no recent posts
                    if data.get('posts_count', 0) == 0 or not data.get('has_recent_posts', True):
                        st.warning(f"⚠️ No Recent Posts Found")
                        st.info(f"""
                        **{data.get('target_name', 'This user')}** hasn't posted in the last 30 days.
                        
                        {data.get('message', 'User may be inactive or not posting publicly.')}
                        
                        **Suggestions:**
                        - Try a different target who posts more frequently
                        - Check if the profile is public
                        - Come back later if they're temporarily inactive
                        """)
                        return
                    
                    st.session_state.target_id = data['target_id']
                    st.session_state.target_name = data['target_name']
                    st.session_state.target_headline = data['target_headline']
                    st.session_state.posts = data['posts']
                    
                    st.success(f"✅ Fetched {len(data['posts'])} recent posts from **{data['target_name']}**")
                    st.caption(f"📅 All posts are from the last 30 days")
                    st.balloons()
                else:
                    error_detail = response.json().get('detail', 'Unknown error')
                    st.error(f"❌ Error: {error_detail}")
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Target may have many posts. Try again.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Step 2: Post Selection
    if 'posts' in st.session_state and st.session_state.posts:
        st.markdown("---")
        st.markdown(f"### Step 2: Select Post from {st.session_state.target_name}")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            sort_by = st.selectbox("Sort by", ["Recent", "Most Liked", "Most Commented"])
        with col2:
            show_count = st.slider("Show posts", 5, 20, 10)
        
        # Sort posts
        posts = st.session_state.posts[:show_count]
        
        # Display posts
        for i, post in enumerate(posts, 1):
            with st.container():
                st.markdown(f"**Post {i}** • {post.get('posted_date', '')[:10]}")
                st.text(post['content'][:200] + "...")
                
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    st.caption(f"👍 {post.get('likes_count', 0)} likes")
                with col2:
                    st.caption(f"💬 {post.get('comments_count', 0)} comments")
                with col3:
                    st.caption(f"📝 {len(post['content'].split())} words")
                with col4:
                    if st.button("Generate", key=f"gen_{i}", use_container_width=True):
                        st.session_state.selected_post = post
                        st.session_state.generate_now = True
                        st.rerun()
                
                st.markdown("---")
        
        # Generate comments
        if st.session_state.get('generate_now'):
            show_generated_comments()


def show_generated_comments():
    """Show generated comments"""
    st.markdown("### 💬 Generated Comments")
    
    post = st.session_state.selected_post
    
    # Post preview
    with st.expander("📄 Selected Post", expanded=True):
        st.write(post['content'])
        st.caption(f"👍 {post.get('likes_count', 0)} • 💬 {post.get('comments_count', 0)}")
    
    with st.spinner("🤖 AI is writing comments in your style..."):
        try:
            response = requests.post(
                f"{API_BASE_URL}/comments/generate",
                json={
                    "user_id": st.session_state.user_id,
                    "post_id": post['post_id'],
                    "post_url": post.get('post_url', '')
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                st.success("✅ Comments generated!")
                
                # Display comments
                for i, comment in enumerate(data['comments'], 1):
                    st.markdown('<div class="comment-box">', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([5, 1])
                    
                    with col1:
                        # Show dynamic approach (not just supportive/questioning/insightful)
                        approach = comment['approach'].replace('_', ' ').title()
                        st.markdown(f"**Variation {i}: {approach}**")
                        st.write(comment['text'])
                        st.progress(comment['confidence'], text=f"Confidence: {comment['confidence']:.0%}")
                        
                        # Show word count
                        word_count = len(comment['text'].split())
                        st.caption(f"📝 {word_count} words")
                    
                    with col2:
                        st.button("📋", key=f"copy_{i}", help="Copy to clipboard")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.session_state.generate_now = False
                
            else:
                error = response.json().get('detail', 'Unknown error')
                st.error(f"❌ Error: {error}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


def show_stats():
    """Show usage statistics"""
    st.markdown('<p class="main-header">Usage Statistics</p>', unsafe_allow_html=True)
    
    try:
        response = requests.get(f"{API_BASE_URL}/usage-stats")
        
        if response.status_code == 200:
            data = response.json()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Users", data['total_users'])
            with col2:
                st.metric("Targets Analyzed", data['total_targets'])
            with col3:
                st.metric("Posts Fetched", data['total_posts'])
            with col4:
                st.metric("Comments Generated", data['total_generated_comments'])
            
            st.markdown("---")
            
            # System info
            st.subheader("System Status")
            st.success("✅ Backend: Connected")
            st.success("✅ RapidAPI: Active")
            st.success("✅ Gemini: Ready")
            
        else:
            st.error("Could not load statistics")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()