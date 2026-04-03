"""FastAPI + LangGraph Backend for LinkedIn Comment Generator"""
import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="\033[36m%(asctime)s\033[0m \033[1m[%(name)s]\033[0m %(message)s",
    datefmt="%H:%M:%S",
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import init_db
from app.routes.scrape import router as scrape_router
from app.routes.posts import router as posts_router
from app.routes.generate import router as generate_router

log = logging.getLogger("main")

app = FastAPI(title="LinkedIn Comment Generator", version="2.0")

# CORS — allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(scrape_router)
app.include_router(posts_router)
app.include_router(generate_router)


@app.on_event("startup")
async def startup():
    init_db()
    log.info("=" * 60)
    log.info("LinkedIn Comment Generator — FastAPI + LangGraph")
    log.info("=" * 60)
    log.info(f"GROQ_API_KEY: {'set' if os.getenv('GROQ_API_KEY') else 'MISSING'}")
    log.info(f"RAPIDAPI_KEY: {'set' if os.getenv('RAPIDAPI_KEY') else 'MISSING'}")
    log.info(f"SERPAPI_KEY:  {'set' if os.getenv('SERPAPI_KEY') else 'MISSING'}")
    log.info("=" * 60)


@app.get("/api/health")
async def health():
    return {"status": "ok", "engine": "langgraph"}
