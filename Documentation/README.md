# LinkedIn Comment Generator

Generate authentic, human-like LinkedIn comments that match your personal writing style using AI.

## 🎯 Overview

This system analyzes your LinkedIn profile and comment history to understand your unique writing style, then generates personalized comments for target posts that sound exactly like you wrote them.

### Key Features

- **Style Matching**: Replicates your tone, formality, vocabulary, and engagement patterns
- **Context-Aware**: Analyzes post content and existing comments
- **Anti-AI Detection**: Removes AI clichés and corporate jargon
- **3 Variations**: Generate 3 different comment approaches per post
- **Full-Stack**: FastAPI backend + Streamlit frontend

## 🏗️ Architecture

```
Backend (FastAPI)
├── LinkedIn Data Fetching (RapidAPI)
├── Profile Analysis (Claude AI)
├── Comment Generation (Claude AI)
└── SQLite Database

Frontend (Streamlit)
├── Profile Setup
├── Target Analysis
├── Comment Generation
└── History Tracking
```

## 📋 Prerequisites

1. **Python 3.10+**
2. **RapidAPI Account** with LinkedIn API subscription
3. **Anthropic API Key** for Claude
4. **API Keys Required:**
   - RapidAPI Key ([Get here](https://rapidapi.com))
   - Anthropic API Key ([Get here](https://console.anthropic.com))

## 🚀 Installation

### 1. Clone/Download the Project

```bash
cd linkedin-comment-generator
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Setup Frontend

```bash
cd ../frontend

# Install dependencies
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Get RapidAPI Key

1. Go to [RapidAPI](https://rapidapi.com)
2. Search for "LinkedIn" APIs
3. Subscribe to one:
   - **Fresh LinkedIn Profile Data** (Recommended)
   - **LinkedIn Data API**
   - **LinkedIn Profile Data**
4. Copy your `X-RapidAPI-Key`

### 2. Get Anthropic API Key

1. Go to [Anthropic Console](https://console.anthropic.com)
2. Create an account
3. Navigate to API Keys
4. Create a new key

### 3. Update Backend Configuration

Edit `backend/.env`:

```env
RAPIDAPI_KEY=your_actual_rapidapi_key
ANTHROPIC_API_KEY=your_actual_anthropic_key

# Update these based on your RapidAPI service
RAPIDAPI_BASE_URL=https://your-api-url.p.rapidapi.com
RAPIDAPI_HOST=your-api-host.p.rapidapi.com
```

**Important**: Check your RapidAPI service's documentation for the correct base URL and host.

## 🎮 Running the Application

### Terminal 1: Start Backend

```bash
cd backend
source venv/bin/activate
python main.py
```

Backend will start at: `http://localhost:8000`

### Terminal 2: Start Frontend

```bash
cd frontend
streamlit run app.py
```

Frontend will open at: `http://localhost:8501`

## 📖 Usage Guide

### Step 1: Profile Setup

1. Open the Streamlit frontend
2. Go to "Setup Profile"
3. Enter your LinkedIn URL
4. Click "Analyze My Profile"
5. Wait for analysis (30-60 seconds)

The system will:
- Fetch your profile data
- Analyze your comment history
- Extract your writing patterns

### Step 2: Target Analysis

1. Go to "Generate Comments"
2. Enter target person's LinkedIn URL
3. Click "Fetch Posts"
4. View their recent posts (last 30 days)

### Step 3: Generate Comments

1. Select a post to comment on
2. Click "Generate"
3. Wait for AI generation (15-30 seconds)
4. Review 3 comment variations
5. Copy your favorite one

### Step 4: View History

1. Go to "History"
2. See all previously generated comments
3. Track your usage

## 🔧 API Endpoints

### User Profile
- `POST /api/user/profile` - Create user profile
- `GET /api/user/profile/{user_id}` - Get user profile

### Target Analysis
- `POST /api/target/analyze` - Analyze target and fetch posts

### Comment Generation
- `POST /api/comments/generate` - Generate comments

### Utilities
- `GET /api/health` - Health check
- `GET /api/history/{user_id}` - Get history
- `GET /api/usage-stats` - Usage statistics

## 🎨 Customization

### Adjust Comment Length

Edit `backend/app/core/config.py`:

```python
MIN_COMMENT_LENGTH: int = 30
MAX_COMMENT_LENGTH: int = 150
```

### Change AI Model

```python
CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
TEMPERATURE: float = 0.7  # 0.0-1.0 (lower = more consistent)
```

### Modify Caching

```python
PROFILE_CACHE_DAYS: int = 7
POST_CACHE_HOURS: int = 24
```

## 🐛 Troubleshooting

### Backend Won't Start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Try different port
uvicorn main:app --port 8001
```

### RapidAPI Errors

- **403 Forbidden**: Check API key is correct
- **404 Not Found**: Verify endpoint URL in config
- **429 Too Many Requests**: Rate limit exceeded, wait or upgrade plan

### Claude API Errors

- **401 Unauthorized**: Check Anthropic API key
- **429 Rate Limit**: Reduce request frequency
- **500 Server Error**: Check API key has sufficient credits

### Comments Don't Match Style

1. Check if you have enough comment history (minimum 10-20)
2. Adjust `TEMPERATURE` in config (try 0.6-0.8)
3. Review writing style analysis for accuracy

## 📊 Cost Estimation

### Per User
- Initial profile analysis: $0.05-0.15
- Per comment generation: $0.01-0.05

### Monthly (100 users, 1000 comments)
- RapidAPI: ~$50-100
- Claude API: ~$30-80
- **Total: ~$80-180/month**

## 🔐 Security Notes

- Never commit `.env` file
- Keep API keys secret
- Don't share your database file
- Use HTTPS in production
- Implement rate limiting for public deployment

## 📈 Future Enhancements

- [ ] Support for multiple social platforms
- [ ] A/B testing of comment variations
- [ ] Real-time style adaptation
- [ ] Comment scheduling
- [ ] Browser extension
- [ ] Mobile app
- [ ] Team collaboration features

## 🤝 Contributing

This is a complete, production-ready system. Feel free to:
- Fork and customize
- Add new features
- Improve prompts
- Optimize performance

## 📄 License

MIT License - Free to use and modify

## 🆘 Support

If you encounter issues:

1. Check logs: `backend/logs/` and Streamlit console
2. Verify API keys are correct
3. Ensure RapidAPI endpoints match your service
4. Check Claude API credits

## 🎉 Acknowledgments

- Built with FastAPI, Streamlit, and Claude AI
- LinkedIn data via RapidAPI
- Inspired by the need for authentic online engagement

---

**Note**: This system is for educational and personal use. Always follow LinkedIn's Terms of Service and use generated comments responsibly.