from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import requests
import json
import logging
from datetime import datetime
import re
import asyncio
import aiohttp
import facebook
from googlesearch import search
import spacy
from spacy.matcher import Matcher
import uvicorn
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for models
nlp = None
job_matcher = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for loading models on startup"""
    global nlp, job_matcher
    
    # Load spaCy model on startup
    try:
        nlp = spacy.load("en_core_web_sm")
        job_matcher = Matcher(nlp.vocab)
        logger.info("spaCy model loaded successfully")
    except OSError:
        logger.warning("spaCy model not found. Job detection will be limited.")
        nlp = None
    
    yield
    
    # Cleanup (if needed)
    logger.info("Shutting down...")

app = FastAPI(
    title="Search Bot API",
    description="A search bot that provides web search, job search, and Facebook search functionality",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration
# Facebook Graph API for group posts
FB_ACCESS_TOKEN = "YOUR_FB_ACCESS_TOKEN"
FB_GROUP_ID = "YOUR_FB_GROUP_ID"

# Pydantic models
class SearchRequest(BaseModel):
    query: str
    max_results: int = 5

class JobSearchRequest(BaseModel):
    location: str = "remote"
    max_results: int = 5

class FacebookSearchRequest(BaseModel):
    query: str
    max_results: int = 10

class SearchBot:
    def __init__(self):
        self.setup_job_patterns()
    
    def setup_job_patterns(self):
        """Setup spaCy patterns for job detection"""
        if not nlp or not job_matcher:
            return
        
        hiring_patterns = [
            [{"LOWER": {"IN": ["hiring", "recruiting", "seeking"]}}],
            [{"LOWER": {"IN": ["job", "position", "role"]}}, 
             {"LOWER": {"IN": ["opening", "available", "vacancy"]}}],
            [{"LOWER": {"IN": ["apply", "send"]}}, 
             {"LOWER": {"IN": ["resume", "cv"]}}],
            [{"LOWER": {"IN": ["full", "part"]}}, {"LOWER": "time"}],
            [{"LOWER": "remote"}, {"LOWER": {"IN": ["work", "job"]}}],
            [{"LOWER": {"IN": ["salary", "wage"]}}, {"IS_DIGIT": True}],
            [{"LOWER": {"IN": ["we", "company"]}}, {"LOWER": {"IN": ["are", "is"]}}, {"LOWER": "hiring"}]
        ]
        
        try:
            for i, pattern in enumerate(hiring_patterns):
                job_matcher.add(f"JOB_PATTERN_{i}", [pattern])
            logger.info("Job patterns loaded successfully")
        except Exception as e:
            logger.error(f"Error setting up job patterns: {str(e)}")
    
    def is_job_post(self, text: str) -> bool:
        """Check if text is a job post using spaCy"""
        if not nlp or not job_matcher or not text:
            return False
        
        try:
            doc = nlp(text)
            matches = job_matcher(doc)
            
            job_keywords = {
                'hire', 'hiring', 'job', 'position', 'role', 'career', 'opportunity',
                'apply', 'resume', 'cv', 'salary', 'wage', 'remote', 'fulltime', 'parttime',
                'interview', 'candidate', 'employee', 'team', 'join', 'work', 'experience'
            }
            
            keyword_count = sum(1 for token in doc if token.lemma_.lower() in job_keywords)
            
            # Additional pattern checks
            salary_pattern = r'\$\d+(?:,\d+)*(?:\.\d+)?'
            has_salary = bool(re.search(salary_pattern, text))
            
            return len(matches) > 0 or keyword_count >= 2 or has_salary
            
        except Exception as e:
            logger.error(f"Error in job detection: {str(e)}")
            return False
    
    async def search_web(self, query: str, max_results: int = 5) -> List[str]:
        """Perform web search and return results"""
        try:
            # Using Google Search in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            search_results = await loop.run_in_executor(
                None, 
                lambda: list(search(query, num_results=max_results))
            )
            return search_results
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []
    
    async def search_jobs(self, location: str = "remote", max_results: int = 5) -> List[str]:
        """Search for job postings"""
        try:
            # Search for jobs using web search
            job_query = f"jobs hiring {location} site:indeed.com OR site:linkedin.com OR site:glassdoor.com"
            
            loop = asyncio.get_event_loop()
            job_results = await loop.run_in_executor(
                None, 
                lambda: list(search(job_query, num_results=max_results))
            )
            return job_results
        except Exception as e:
            logger.error(f"Jobs search error: {str(e)}")
            return []
    
    async def search_facebook(self, search_term: str, max_results: int = 10) -> Dict[str, Any]:
        """Search Facebook group posts"""
        try:
            # Run Facebook API call in executor to avoid blocking
            loop = asyncio.get_event_loop()
            posts_data = await loop.run_in_executor(
                None, 
                self._search_facebook_posts, 
                search_term
            )
            return posts_data
        except Exception as e:
            logger.error(f"Facebook search error: {str(e)}")
            return {"job_posts": [], "regular_posts": []}
    
    def _search_facebook_posts(self, search_term: str):
        """Search Facebook posts synchronously"""
        try:
            graph = facebook.GraphAPI(access_token=FB_ACCESS_TOKEN)
            feed = graph.get_connections(FB_GROUP_ID, "feed", limit=50)
            
            job_posts = []
            regular_posts = []
            
            for post in feed['data']:
                if 'message' in post and search_term.lower() in post['message'].lower():
                    post_data = {
                        'id': post['id'],
                        'message': post['message'][:150] + "..." if len(post['message']) > 150 else post['message'],
                        'created_time': post.get('created_time', 'Unknown')[:10],  # Just date
                        'author': post.get('from', {}).get('name', 'Unknown')
                    }
                    
                    if self.is_job_post(post['message']):
                        job_posts.append(post_data)
                    else:
                        regular_posts.append(post_data)
            
            return {"job_posts": job_posts, "regular_posts": regular_posts}
            
        except Exception as e:
            logger.error(f"Facebook API error: {str(e)}")
            return {"job_posts": [], "regular_posts": []}
    
    async def search_news(self, topic: str = "technology", max_results: int = 5) -> List[str]:
        """Get latest news"""
        try:
            # Search for news
            news_query = f"{topic} news today site:reuters.com OR site:bbc.com OR site:cnn.com OR site:techcrunch.com"
            
            loop = asyncio.get_event_loop()
            news_results = await loop.run_in_executor(
                None, 
                lambda: list(search(news_query, num_results=max_results))
            )
            return news_results
        except Exception as e:
            logger.error(f"News search error: {str(e)}")
            return []

# Initialize bot
bot = SearchBot()

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Search Bot API",
        "version": "1.0.0",
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "spacy_loaded": nlp is not None,
        "timestamp": datetime.now().isoformat()
    }

# API endpoints
@app.post("/api/search")
async def api_search(request: SearchRequest):
    """Direct search API endpoint"""
    try:
        results = await bot.search_web(request.query, request.max_results)
        return {
            "query": request.query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobs")
async def api_jobs(request: JobSearchRequest):
    """Direct job search API endpoint"""
    try:
        results = await bot.search_jobs(request.location, request.max_results)
        return {
            "location": request.location,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/facebook")
async def api_facebook(request: FacebookSearchRequest):
    """Direct Facebook search API endpoint"""
    try:
        posts_data = await bot.search_facebook(request.query, request.max_results)
        return {
            "query": request.query,
            "job_posts": posts_data["job_posts"],
            "regular_posts": posts_data["regular_posts"],
            "total_found": len(posts_data["job_posts"]) + len(posts_data["regular_posts"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/news")
async def api_news(query: str = "technology", max_results: int = 5):
    """Direct news search API endpoint"""
    try:
        results = await bot.search_news(query, max_results)
        return {
            "topic": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def api_status():
    """Check bot status"""
    return {
        "system": "online",
        "ai_model": "spaCy Loaded" if nlp else "Not Available",
        "facebook_api": "Connected" if FB_ACCESS_TOKEN else "Not Configured",
        "search": "available",
        "uptime": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )