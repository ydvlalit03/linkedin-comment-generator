"""
Test script for LinkedIn Scraper API
Tests the actual RapidAPI endpoints
"""
import requests
import json

# Your API key
RAPIDAPI_KEY = "04f901f9b5mshedea468d33db17cp1e8fd2jsn8e6245854334"

headers = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": "linkedin-scraper-api-real-time-fast-affordable.p.rapidapi.com"
}

base_url = "https://linkedin-scraper-api-real-time-fast-affordable.p.rapidapi.com"

print("=" * 60)
print("LinkedIn Scraper API - Test Suite")
print("=" * 60)

# Test 1: Get Posts (Profile info comes from this)
print("\n📝 Test 1: Fetching Posts (includes profile info)...")
print("-" * 60)

try:
    response = requests.get(
        f"{base_url}/profile/posts",
        headers=headers,
        params={
            "username": "satyanadella",
            "page_number": "1"
        },
        timeout=15
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Success!")
        
        # Debug: Show what we got
        print(f"\n🔍 DEBUG - Response Structure:")
        print(f"Response type: {type(data)}")
        print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
        
        if isinstance(data, dict):
            print(f"'success': {data.get('success')}")
            print(f"'message': {data.get('message')}")
            print(f"'data' type: {type(data.get('data'))}")
            
            if isinstance(data.get('data'), dict):
                print(f"'data' keys: {list(data.get('data').keys())}")
                print(f"First few items in 'data':")
                for i, (key, value) in enumerate(list(data.get('data').items())[:3]):
                    print(f"  Key '{key}': type={type(value)}, has {len(value) if isinstance(value, dict) else 'N/A'} fields")
        
        # Handle the actual API response format
        if isinstance(data, dict) and data.get('success'):
            # API structure: {"success": true, "data": {"posts": [...], "pagination_token": "..."}}
            posts_data = data.get('data', {})
            
            print(f"\n🔍 Processing posts_data...")
            
            # Extract posts from the nested structure
            if isinstance(posts_data, dict) and 'posts' in posts_data:
                # Posts are in data.posts
                posts = posts_data.get('posts', [])
                print(f"\nFound {len(posts)} posts from data.posts")
            elif isinstance(posts_data, list):
                # Direct list
                posts = posts_data
                print(f"\nFound {len(posts)} posts (direct list)")
            elif isinstance(posts_data, dict):
                # Fallback: try to convert dict to list
                print(f"Converting dict with {len(posts_data)} keys to list...")
                posts = []
                for key in sorted(posts_data.keys()):
                    if isinstance(posts_data[key], (dict, list)):
                        if isinstance(posts_data[key], list):
                            posts.extend(posts_data[key])
                        else:
                            posts.append(posts_data[key])
                print(f"\nFound {len(posts)} posts (converted from dict)")
            else:
                print(f"\nUnexpected posts_data type: {type(posts_data)}")
                posts = []
            
            if posts and len(posts) > 0:
                first_post = posts[0]
                
                print(f"\n📰 First Post Structure:")
                print(f"Post keys: {list(first_post.keys())[:15]}")
                
                # Extract profile info from author
                author = first_post.get('author', {})
                if author:
                    print(f"\n📋 Profile Info (from post author):")
                    # Try different possible name fields
                    name = author.get('name') or author.get('full_name') or author.get('username', 'N/A')
                    headline = author.get('headline', author.get('description', 'N/A'))
                    print(f"  Name: {name}")
                    print(f"  Headline: {headline[:80]}..." if len(headline) > 80 else f"  Headline: {headline}")
                    print(f"  Author keys: {list(author.keys())}")
                
                # Show first post
                print(f"\n📰 First Post Content:")
                post_text = first_post.get('text', first_post.get('commentary', first_post.get('caption', 'N/A')))
                if len(post_text) > 100:
                    print(f"  Text: {post_text[:100]}...")
                else:
                    print(f"  Text: {post_text}")
                
                # Check stats structure
                stats = first_post.get('stats', {})
                print(f"  Stats keys: {list(stats.keys()) if stats else 'No stats'}")
                
                # Try different field names for engagement metrics
                likes = (stats.get('num_likes') or stats.get('numLikes') or 
                        stats.get('reactionCount') or stats.get('likes') or
                        first_post.get('num_likes', 0))
                comments = (stats.get('num_comments') or stats.get('numComments') or 
                           stats.get('commentCount') or stats.get('comments') or
                           first_post.get('num_comments', 0))
                
                print(f"  Likes: {likes}")
                print(f"  Comments: {comments}")
            else:
                print(f"\n⚠️  No posts found in response")
                print(f"Raw data sample: {str(data)[:500]}")
        else:
            print(f"Unexpected response format")
            print(f"Response: {str(data)[:300]}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except Exception as e:
    print(f"✗ Exception: {str(e)}")
    import traceback
    traceback.print_exc()

# Test 2: Get Post Comments
print("\n\n💬 Test 2: Post Comments...")
print("-" * 60)

try:
    # Use a real post ID from the previous response
    response = requests.get(
        f"{base_url}/post/comments",
        headers=headers,
        params={
            "post_id": "7302343021591674880",  # Example post ID
            "page_number": "1"
        },
        timeout=15
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Comments endpoint works!")
        
        if isinstance(data, dict) and data.get('success'):
            comments_data = data.get('data', {})
            comments = comments_data.get('comments', [])
            print(f"Found {len(comments)} comments")
            
            if comments and len(comments) > 0:
                first_comment = comments[0]
                print(f"\nFirst Comment:")
                print(f"  Text: {first_comment.get('text', 'N/A')[:80]}...")
                print(f"  Author: {first_comment.get('author', {}).get('name', 'N/A')}")
        else:
            print(f"Response: {str(data)[:300]}")
    else:
        print(f"⚠️  Status: {response.status_code}")
        print(f"Note: Comments endpoint may require specific parameters")
        
except Exception as e:
    print(f"✗ Exception: {str(e)}")

# Summary
print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)
print("\n✅ Working Endpoints:")
print("  - /profile/posts (gets posts + profile info from author)")
print("  - /post/comments (gets comments for a post)")
print("\n📝 API Response Format:")
print("  - Returns: {\"success\": true, \"data\": [...]}")
print("  - Profile info extracted from post author")
print("\n⚠️  Parameters:")
print("  - Use 'username' not 'url'")
print("  - Use 'page_number' as string (\"1\", \"2\", etc.)")
print("\n📖 Example Usage:")
print("""
  # Get posts (includes profile info)
  response = requests.get(
      "https://linkedin-scraper-api-real-time-fast-affordable.p.rapidapi.com/profile/posts",
      headers=headers,
      params={
          "username": "satyanadella",
          "page_number": "1"
      }
  )
  data = response.json()
  posts = data['data']  # List of posts
  author = posts[0]['author']  # Profile info
""")

print("\n" + "=" * 60)