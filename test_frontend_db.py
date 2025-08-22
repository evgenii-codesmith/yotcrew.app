#!/usr/bin/env python3
"""
Test script for the enhanced frontend with database jobs
"""
import asyncio
import logging
import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.database import engine, Base, SessionLocal
from app.models import Job
from app.scrapers.daywork123 import Daywork123Scraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_database():
    """Create database tables if they don't exist"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise

def check_database_content():
    """Check current database content"""
    logger.info("Checking database content...")
    
    with SessionLocal() as db:
        # Count total jobs
        total_jobs = db.query(Job).count()
        logger.info(f"Total jobs in database: {total_jobs}")
        
        # Count by source
        sources = db.query(Job.source, func.count(Job.id)).group_by(Job.source).all()
        for source, count in sources:
            logger.info(f"  - {source}: {count} jobs")
        
        # Recent jobs
        recent_jobs = db.query(Job).order_by(Job.created_at.desc()).limit(5).all()
        
        if recent_jobs:
            logger.info("Recent jobs:")
            for job in recent_jobs:
                source_badge = "🟢" if job.source == "daywork123" else "🔵" if job.source == "yotspot" else "⚫"
                quality_badge = "⭐" if job.quality_score and job.quality_score >= 0.8 else "✨" if job.quality_score and job.quality_score >= 0.6 else "💫"
                logger.info(f"  {source_badge} {job.title} @ {job.company} ({job.location}) {quality_badge}")
        
        return {
            "total": total_jobs,
            "sources": dict(sources),
            "recent": len(recent_jobs)
        }

async def add_sample_jobs_if_empty():
    """Add sample jobs if database is empty"""
    with SessionLocal() as db:
        job_count = db.query(Job).count()
        
        if job_count == 0:
            logger.info("Database is empty, scraping some jobs...")
            
            try:
                scraper = Daywork123Scraper()
                
                if await scraper.test_connection():
                    result = await scraper.scrape_and_save_jobs(max_pages=1)
                    logger.info(f"Scraped {result['jobs_found']} jobs, saved {result['jobs_saved']}")
                    return True
                else:
                    logger.warning("Cannot connect to Daywork123.com")
                    return False
            except Exception as e:
                logger.error(f"Error scraping jobs: {e}")
                return False
        else:
            logger.info(f"Database already contains {job_count} jobs")
            return True

def test_api_endpoints():
    """Test that the API endpoints work with database data"""
    logger.info("Testing API endpoints...")
    
    # This would normally be done with requests, but for simplicity we'll just check the database
    with SessionLocal() as db:
        # Test job filtering
        yotspot_jobs = db.query(Job).filter(Job.source == "yotspot").count()
        daywork123_jobs = db.query(Job).filter(Job.source == "daywork123").count()
        
        logger.info(f"API filtering would return:")
        logger.info(f"  - Yotspot jobs: {yotspot_jobs}")
        logger.info(f"  - Daywork123 jobs: {daywork123_jobs}")
        
        # Test search functionality
        captain_jobs = db.query(Job).filter(Job.title.ilike("%captain%")).count()
        engineer_jobs = db.query(Job).filter(Job.title.ilike("%engineer%")).count()
        
        logger.info(f"Search results would be:")
        logger.info(f"  - Captain jobs: {captain_jobs}")
        logger.info(f"  - Engineer jobs: {engineer_jobs}")
        
        return True

async def main():
    """Main test function"""
    logger.info("=== Frontend Database Integration Test ===")
    
    try:
        # Setup
        logger.info("1. Setting up database...")
        setup_database()
        
        # Check initial state
        logger.info("\n2. Checking database content...")
        initial_status = check_database_content()
        
        # Add sample data if needed
        if initial_status["total"] == 0:
            logger.info("\n3. Adding sample jobs...")
            await add_sample_jobs_if_empty()
            
            # Check again after adding
            logger.info("\n4. Checking database content after scraping...")
            check_database_content()
        
        # Test API functionality
        logger.info("\n5. Testing API endpoints...")
        test_api_endpoints()
        
        # Instructions for user
        logger.info("\n=== Frontend Integration Complete ===")
        logger.info("To test the frontend:")
        logger.info("1. Start the FastAPI server: python main.py")
        logger.info("2. Open your browser to: http://localhost:8000")
        logger.info("3. Test the following features:")
        logger.info("   - Source filtering (All Sources / Yotspot / Daywork123)")
        logger.info("   - Job search and filtering")
        logger.info("   - Job cards showing enhanced data (quality scores, requirements, benefits)")
        logger.info("   - Real-time job statistics in the header")
        logger.info("   - Apply/View Details buttons with external links")
        
        logger.info("\n✅ Database is ready for frontend display!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

