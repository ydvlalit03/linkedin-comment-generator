"""
Intelligent Mock LinkedIn Data Generator
Designed specifically for our advanced profile analyzer and comment generator
Generates realistic, varied data that matches professional LinkedIn patterns
"""
import random
from typing import Dict, List
from datetime import datetime, timedelta


class IntelligentMockData:
    """Generates professional-grade mock LinkedIn data"""
    
    # Professional writing style templates (realistic variations)
    WRITING_STYLES = {
        "casual_enthusiastic": {
            "tone": "enthusiastic",
            "formality": 0.3,
            "emojis": "high",
            "contractions": "frequent",
            "avg_length": 35,
            "burstiness": "high",
            "samples": [
                "Love this! We tried something similar last quarter and the results were amazing. Quick question though - how did you handle the initial setup?",
                "This is exactly what I needed today. Thanks for sharing! 🎯",
                "So true. I've been saying this for months. The key thing people miss is the execution part.",
                "Absolutely agree! We saw a 40% increase when we implemented this approach. Game changer.",
                "Great point about the metrics. That's something we overlooked initially and it cost us.",
            ],
            "common_phrases": ["Love this", "So true", "Quick question", "Thanks for sharing"],
            "openings": ["Love this", "This is exactly", "So true", "Absolutely agree"],
            "conversational_markers": ["Quick question though", "The key thing is", "Here's what I found"]
        },
        
        "professional_analytical": {
            "tone": "professional",
            "formality": 0.7,
            "emojis": "low",
            "contractions": "occasional",
            "avg_length": 55,
            "burstiness": "medium",
            "samples": [
                "This aligns with our recent findings. We conducted a similar analysis across 50+ companies and saw consistent patterns. The data suggests that timing is more critical than most realize.",
                "Interesting perspective on the ROI metrics. In my experience, the challenge isn't identifying the opportunity but rather getting organizational buy-in for the required investment.",
                "I appreciate the framework you've outlined here. One consideration that might be worth exploring is the impact of market timing on implementation success.",
                "The case study is compelling. However, I would be curious to understand how these results scale across different industry verticals.",
                "Well articulated. The approach you describe mirrors what we implemented last year, though our execution timeline was considerably longer than anticipated.",
            ],
            "common_phrases": ["In my experience", "I would be curious", "One consideration", "Well articulated"],
            "openings": ["This aligns with", "Interesting perspective", "I appreciate", "The case study"],
            "conversational_markers": ["In my experience", "One consideration", "However", "The challenge is"]
        },
        
        "supportive_mentor": {
            "tone": "supportive",
            "formality": 0.5,
            "emojis": "moderate",
            "contractions": "frequent",
            "avg_length": 45,
            "burstiness": "high",
            "samples": [
                "Really proud of how you've grown in this area! I remember when you first started exploring this topic. Your perspective has evolved significantly.",
                "This is solid advice for anyone starting out. I'd add one thing: don't underestimate the importance of building relationships early.",
                "You're absolutely right about the fundamentals. Too many people skip the basics and wonder why they struggle later. Well said! 💡",
                "Love seeing this kind of thoughtful reflection. What helped me was keeping a weekly journal. Have you tried that approach?",
                "Great insights here. For those new to this, I'd recommend starting small and scaling gradually. Makes a huge difference.",
            ],
            "common_phrases": ["Really proud", "Well said", "You're absolutely right", "For those new to"],
            "openings": ["Really proud", "This is solid", "You're absolutely right", "Love seeing"],
            "conversational_markers": ["I'd add one thing", "What helped me", "For those new to", "Have you tried"]
        },
        
        "technical_detailed": {
            "tone": "technical",
            "formality": 0.8,
            "emojis": "none",
            "contractions": "rare",
            "avg_length": 65,
            "burstiness": "low",
            "samples": [
                "The architecture you described is sound, but I would recommend considering the scalability implications. In our implementation, we encountered significant performance degradation at approximately 10K concurrent users.",
                "Your approach to data normalization is correct. However, you may want to implement additional validation layers to handle edge cases. We discovered this was critical during production deployment.",
                "The methodology is well-structured. One technical consideration: ensure your error handling accounts for network latency variations, particularly in distributed systems.",
                "I have implemented similar solutions using both approaches. The trade-off between complexity and maintainability becomes apparent at scale. Documentation is essential.",
                "The integration pattern you outlined follows best practices. Consider implementing circuit breakers for external service calls to improve system resilience.",
            ],
            "common_phrases": ["I would recommend", "One technical consideration", "In our implementation", "Consider implementing"],
            "openings": ["The architecture", "Your approach", "The methodology", "I have implemented"],
            "conversational_markers": ["However", "One consideration", "In our implementation", "The trade-off"]
        },
        
        "storytelling_experiential": {
            "tone": "casual",
            "formality": 0.4,
            "emojis": "moderate",
            "contractions": "frequent",
            "avg_length": 50,
            "burstiness": "high",
            "samples": [
                "This takes me back to 2019 when we faced the exact same challenge. We thought we had it figured out. We didn't. What saved us was admitting we needed help and bringing in external perspective.",
                "I lived through this transition firsthand. The hardest part wasn't the technical changes - it was getting everyone on board. Took us 6 months longer than planned.",
                "Your point about timing resonates. Last year we launched too early and paid the price. Sometimes waiting is the smartest move, even when pressure is building.",
                "Been there! Our first attempt failed spectacularly. But we learned so much from that failure. Second time around was smooth because we knew what to avoid.",
                "This reminds me of a project where everything that could go wrong did go wrong. Honestly, best learning experience of my career. Failure teaches more than success.",
            ],
            "common_phrases": ["This takes me back", "I lived through", "Been there", "This reminds me"],
            "openings": ["This takes me back", "I lived through", "Your point about", "Been there"],
            "conversational_markers": ["Here's the thing", "What saved us", "The hardest part", "Honestly"]
        }
    }
    
    # Realistic post templates
    POST_TEMPLATES = {
        "achievement": [
            "Excited to share that our team just hit a major milestone! 🎉 After 6 months of hard work, we've successfully launched our new platform. The journey taught us so much about perseverance, collaboration, and the importance of user feedback. Huge thanks to everyone who believed in this vision. What's your biggest lesson from a challenging project?",
            "Proud moment: Just completed my AWS Solutions Architect certification! The exam was tough, but the learning process was incredible. For anyone considering it - yes, it's worth it. The cloud architecture concepts have already changed how I approach system design.",
            "We did it! Our Q4 numbers are in and we exceeded our goals by 35%. This wouldn't have been possible without the amazing team effort. Special shout-out to our customer success team who went above and beyond every single day.",
        ],
        
        "thought_leadership": [
            "Hot take: The future of remote work isn't hybrid - it's asynchronous-first. Here's why I believe this matters more than the office vs. home debate:\n\n1. Time zone flexibility enables global teams\n2. Deep work requires uninterrupted blocks\n3. Documentation becomes a competitive advantage\n\nWhat's your experience with async collaboration?",
            "After analyzing 100+ failed product launches, I've noticed a pattern: Most teams focus on features while neglecting distribution strategy. Building something great is only half the battle. Getting it in front of the right people at the right time? That's the real challenge.\n\nWhat's worked for you in product distribution?",
            "Unpopular opinion: Most companies are over-engineering their tech stack. Simple solutions often outperform complex ones. We recently simplified our architecture from 15 microservices to 3 monoliths and saw:\n• 50% reduction in bugs\n• 3x faster deployment\n• Significantly lower infrastructure costs\n\nSometimes boring is better.",
        ],
        
        "question_engagement": [
            "Quick poll for the product managers here: How do you prioritize feature requests when you have limited engineering resources?\n\nA) Customer impact scoring\nB) Revenue potential\nC) Strategic alignment\nD) Technical debt consideration\n\nCurious to hear what frameworks you use!",
            "Question for the data science community: What's your go-to approach for handling imbalanced datasets? I've tried oversampling, undersampling, and SMOTE with mixed results. What techniques have worked well for you in production?",
            "Calling all startup founders: What's the one thing you wish you knew before raising your first round of funding? I'm currently in the process and would love to learn from your experiences.",
        ],
        
        "industry_news": [
            "Big news in the AI space: GPT-5 capabilities just leaked and the implications are massive. Key takeaways:\n\n• Multimodal by default (text, image, audio, video)\n• 10x reduction in hallucinations\n• Reasoning capabilities approaching human-level\n\nThis changes everything for product teams. How are you preparing for the AI-first era?",
            "Just read the latest Gartner report on cloud adoption trends. Some surprising findings:\n\n1. 78% of enterprises still running hybrid infrastructure\n2. Security concerns decreasing year-over-year\n3. Multi-cloud strategy now the norm, not exception\n\nSeeing this play out in your organization?",
        ],
        
        "personal_story": [
            "Two years ago today, I got laid off. Honestly, it felt like the end of the world. Today, I'm running a team of 12 and working on the most fulfilling project of my career.\n\nSometimes the best things come from the worst moments. If you're going through a tough time right now - it gets better. Keep pushing forward.",
            "Failed my first startup. Lost $50K of savings. Went back to a corporate job feeling defeated.\n\nBut here's what that failure taught me:\n• Timing matters as much as the idea\n• Cash flow > vanity metrics\n• Co-founder selection is everything\n\nFive years later, I'm grateful for that failure. It made me a better founder.",
        ]
    }
    
    def __init__(self):
        self.profiles_generated = 0
    
    def generate_profile(self, linkedin_url: str) -> Dict:
        """Generate a realistic profile with authentic writing style"""
        
        # Extract name from URL
        username = self._extract_username(linkedin_url)
        name = self._username_to_name(username)
        
        # Select a random writing style
        style_name = random.choice(list(self.WRITING_STYLES.keys()))
        style_template = self.WRITING_STYLES[style_name]
        
        # Generate profile
        profile = {
            "name": name,
            "headline": self._generate_headline(style_name),
            "about": self._generate_about(style_name),
            "experience": self._generate_experience(),
            "skills": self._generate_skills(style_name),
            "_style_template": style_template  # Internal use for comment generation
        }
        
        self.profiles_generated += 1
        return profile
    
    def generate_user_comments(self, linkedin_url: str, style_template: Dict = None) -> List[Dict]:
        """Generate realistic comment history matching a writing style"""
        
        if not style_template:
            style_name = random.choice(list(self.WRITING_STYLES.keys()))
            style_template = self.WRITING_STYLES[style_name]
        
        comments = []
        samples = style_template["samples"]
        
        # Generate 15-20 varied comments
        for i in range(random.randint(15, 20)):
            # Mix actual samples with variations
            if i < len(samples):
                comment_text = samples[i]
            else:
                comment_text = self._create_comment_variation(style_template)
            
            comments.append({
                "comment_text": comment_text,
                "post_context": self._generate_post_context(),
                "date": datetime.now() - timedelta(days=random.randint(1, 90))
            })
        
        return comments
    
    def generate_posts(self, linkedin_url: str, days: int = 30) -> List[Dict]:
        """Generate realistic LinkedIn posts"""
        
        posts = []
        post_types = list(self.POST_TEMPLATES.keys())
        
        # Generate 5-10 posts
        num_posts = random.randint(5, 10)
        
        for i in range(num_posts):
            post_type = random.choice(post_types)
            content = random.choice(self.POST_TEMPLATES[post_type])
            
            days_ago = random.randint(1, days)
            
            posts.append({
                "post_url": f"https://linkedin.com/posts/{linkedin_url.split('/')[-1]}-activity-{i}",
                "content": content,
                "media_type": random.choice(["text", "text", "text", "image"]),  # Mostly text
                "posted_date": datetime.now() - timedelta(days=days_ago),
                "likes_count": random.randint(20, 500),
                "comments_count": random.randint(5, 80),
                "_post_type": post_type
            })
        
        # Sort by date
        posts.sort(key=lambda x: x["posted_date"], reverse=True)
        
        return posts
    
    def generate_post_comments(self, post_type: str = "thought_leadership") -> List[Dict]:
        """Generate realistic comments on a post"""
        
        # Select appropriate commenting styles for this post type
        comment_styles = random.sample(list(self.WRITING_STYLES.keys()), k=min(4, len(self.WRITING_STYLES)))
        
        comments = []
        num_comments = random.randint(8, 15)
        
        for i in range(num_comments):
            style_name = random.choice(comment_styles)
            style = self.WRITING_STYLES[style_name]
            
            comment_text = random.choice(style["samples"])
            
            comments.append({
                "author_name": self._generate_random_name(),
                "comment_text": comment_text,
                "likes_count": random.randint(0, 30)
            })
        
        return comments
    
    def _extract_username(self, url: str) -> str:
        """Extract username from LinkedIn URL"""
        url = url.rstrip('/')
        if '/in/' in url:
            return url.split('/in/')[-1].split('/')[0]
        return url.split('/')[-1]
    
    def _username_to_name(self, username: str) -> str:
        """Convert username to realistic name"""
        # Remove numbers and special chars
        clean = username.replace('-', ' ').replace('_', ' ')
        # Title case
        return ' '.join(word.capitalize() for word in clean.split())
    
    def _generate_headline(self, style_name: str) -> str:
        """Generate realistic headline based on style"""
        
        headlines = {
            "casual_enthusiastic": [
                "Product Manager @ TechCo | Building cool stuff | Coffee addict ☕",
                "Software Engineer | Creating amazing user experiences | Always learning",
                "Marketing Lead @ StartupX | Growth hacker | Podcast host 🎙️"
            ],
            "professional_analytical": [
                "Senior Data Scientist @ Fortune 500 | PhD in Machine Learning | Author",
                "VP of Engineering @ Enterprise Corp | Leading distributed teams",
                "Principal Consultant | Cloud Architecture & Digital Transformation"
            ],
            "supportive_mentor": [
                "Engineering Manager @ Tech Inc | Mentor | Building high-performing teams",
                "Career Coach & Leadership Consultant | Helping professionals grow",
                "Director of Product | Passionate about developing future leaders"
            ],
            "technical_detailed": [
                "Staff Software Engineer @ BigTech | Distributed Systems | Open Source Contributor",
                "Solutions Architect @ Cloud Provider | AWS Certified | Speaker",
                "Principal Engineer | Specializing in scalable infrastructure"
            ],
            "storytelling_experiential": [
                "Founder @ StartupName | 2x Exit | Angel Investor",
                "Product Leader | Previously Uber, Airbnb | Sharing lessons learned",
                "Entrepreneur | Failed 3x before success | Mentor to early-stage founders"
            ]
        }
        
        return random.choice(headlines.get(style_name, headlines["professional_analytical"]))
    
    def _generate_about(self, style_name: str) -> str:
        """Generate realistic about section"""
        
        abouts = {
            "casual_enthusiastic": "I love building products that people actually use! Currently leading product at TechCo where we're working on some exciting stuff. When I'm not working, you'll find me hiking, reading sci-fi, or experimenting with new coffee brewing methods. Always happy to connect and chat about product, tech, or the best local coffee spots! ☕",
            
            "professional_analytical": "Experienced data scientist with over 10 years in machine learning and predictive analytics. Specialized in building scalable ML systems for enterprise applications. Published researcher with focus on deep learning and NLP. I enjoy solving complex problems and translating data insights into business value.",
            
            "supportive_mentor": "Passionate about helping engineers and product managers reach their full potential. I've spent 15 years in tech, leading teams ranging from 5 to 50 people. My approach focuses on servant leadership, continuous feedback, and creating psychologically safe environments where people can do their best work. Always happy to help - feel free to reach out!",
            
            "technical_detailed": "Principal engineer specializing in distributed systems architecture. Deep expertise in cloud infrastructure, microservices, and system design. Regular speaker at technical conferences and contributor to open source projects. Focused on building resilient, scalable systems that can handle millions of requests per second.",
            
            "storytelling_experiential": "Serial entrepreneur with 2 successful exits and 3 spectacular failures. Each failure taught me more than any success ever could. Now I spend my time mentoring early-stage founders and investing in companies that are solving real problems. The journey is never linear, but it's always worth it."
        }
        
        return abouts.get(style_name, abouts["professional_analytical"])
    
    def _generate_experience(self) -> List[Dict]:
        """Generate realistic work experience"""
        
        companies = ["TechCorp", "StartupX", "Enterprise Inc", "Innovation Labs", "Digital Solutions"]
        titles = ["Senior Engineer", "Product Manager", "Data Scientist", "Engineering Manager", "Principal Consultant"]
        
        experience = []
        for i in range(random.randint(2, 4)):
            experience.append({
                "title": random.choice(titles),
                "company": random.choice(companies),
                "description": "Led cross-functional teams to deliver high-impact projects. Focused on scalability, user experience, and measurable business outcomes.",
                "duration": f"{random.randint(1, 4)} years"
            })
        
        return experience
    
    def _generate_skills(self, style_name: str) -> List[str]:
        """Generate relevant skills"""
        
        skill_sets = {
            "casual_enthusiastic": ["Product Management", "User Research", "Agile", "Stakeholder Management", "Roadmap Planning"],
            "professional_analytical": ["Machine Learning", "Python", "Statistical Analysis", "Data Visualization", "SQL"],
            "supportive_mentor": ["Leadership", "Team Building", "Coaching", "Performance Management", "Communication"],
            "technical_detailed": ["System Design", "AWS", "Kubernetes", "Distributed Systems", "Go", "Python"],
            "storytelling_experiential": ["Entrepreneurship", "Fundraising", "Strategic Planning", "Business Development", "Mentoring"]
        }
        
        return skill_sets.get(style_name, skill_sets["professional_analytical"])
    
    def _create_comment_variation(self, style_template: Dict) -> str:
        """Create a variation based on style patterns"""
        
        openings = style_template["openings"]
        phrases = style_template["common_phrases"]
        
        opening = random.choice(openings)
        phrase = random.choice(phrases) if phrases else ""
        
        # Simple variation
        variations = [
            f"{opening}. {phrase} - this really resonates with my experience.",
            f"{phrase}! This is spot on. What's been your biggest challenge with this approach?",
            f"{opening} about this topic. {phrase} for bringing this up.",
        ]
        
        return random.choice(variations)
    
    def _generate_post_context(self) -> str:
        """Generate context for a comment"""
        contexts = [
            "Post about remote work trends",
            "Discussion on AI and automation",
            "Career advice thread",
            "Product launch announcement",
            "Industry news analysis",
            "Leadership insights",
            "Technical deep-dive",
            "Startup journey story"
        ]
        return random.choice(contexts)
    
    def _generate_random_name(self) -> str:
        """Generate random professional name"""
        first_names = ["Sarah", "Michael", "Emily", "David", "Jessica", "Ryan", "Amanda", "Chris", "Nicole", "Alex"]
        last_names = ["Johnson", "Chen", "Rodriguez", "Kim", "Taylor", "Patel", "White", "Lee", "Garcia", "Singh"]
        
        return f"{random.choice(first_names)} {random.choice(last_names)}"