#!/usr/bin/env python3
"""
Example usage of Daywork123Scraper with database saving functionality

This script demonstrates how to use the enhanced Daywork123Scraper
to scrape jobs and save them to the database.
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
from app.services.scraping_service import ScrapingService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def example_basic_scraping():
    """Example 1: Basic scraping with database saving"""
    logger.info("=== Example 1: Basic Scraping ===")
    
    # Create scraper instance
    scraper = Daywork123Scraper()
    
    # Test connection first
    if not await scraper.test_connection():
        logger.error("Cannot connect to Daywork123.com")
        return
    
    # Scrape and save jobs (1 page for demo)
    result = await scraper.scrape_and_save_jobs(max_pages=1)
    
    logger.info(f"Scraping completed:")
    logger.info(f"  - Jobs found: {result['jobs_found']}")
    logger.info(f"  - Jobs saved: {result['jobs_saved']}")
    logger.info(f"  - Duration: {result['duration']:.2f} seconds")
    logger.info(f"  - Success: {result['success']}")
    
    return result

async def example_manual_save():
    """Example 2: Manual scraping and saving"""
    logger.info("\n=== Example 2: Manual Scraping and Saving ===")
    
    scraper = Daywork123Scraper()
    
    # Collect jobs manually
    jobs = []
    async for job in scraper.scrape_jobs(max_pages=1):
        jobs.append(job)
        logger.info(f"Found job: {job.title} at {job.company}")
    
    logger.info(f"Collected {len(jobs)} jobs")
    
    # Save jobs to database
    if jobs:
        saved_count = await scraper.save_jobs_to_db(jobs)
        logger.info(f"Saved {saved_count} jobs to database")
        return saved_count
    
    return 0

async def example_using_service():
    """Example 3: Using the ScrapingService"""
    logger.info("\n=== Example 3: Using ScrapingService ===")
    
    service = ScrapingService()
    
    # Scrape specific source
    result = await service.scrape_source("daywork123", max_pages=1)
    
    logger.info(f"Service scraping result:")
    logger.info(f"  - Source: {result['source']}")
    logger.info(f"  - Jobs found: {result['jobs_found']}")
    logger.info(f"  - New jobs: {result['new_jobs']}")
    logger.info(f"  - Updated jobs: {result['updated_jobs']}")
    logger.info(f"  - Duration: {result['duration']:.2f} seconds")
    
    return result

def check_database_status():
    """Check current database status"""
    logger.info("\n=== Database Status ===")
    
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    with SessionLocal() as db:
        # Count total jobs
        total_jobs = db.query(Job).count()
        logger.info(f"Total jobs in database: {total_jobs}")
        
        # Count by source
        dw123_jobs = db.query(Job).filter(Job.source == "daywork123").count()
        yotspot_jobs = db.query(Job).filter(Job.source == "yotspot").count()
        
        logger.info(f"  - Daywork123 jobs: {dw123_jobs}")
        logger.info(f"  - Yotspot jobs: {yotspot_jobs}")
        
        # Recent jobs
        recent_jobs = db.query(Job).order_by(Job.created_at.desc()).limit(5).all()
        
        if recent_jobs:
            logger.info("Recent jobs:")
            for job in recent_jobs:
                logger.info(f"  - {job.title} ({job.source}) - {job.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        return {
            "total": total_jobs,
            "daywork123": dw123_jobs,
            "yotspot": yotspot_jobs,
            "recent": len(recent_jobs)
        }

async def example_health_check():
    """Example 4: Health check for scrapers"""
    logger.info("\n=== Example 4: Health Check ===")
    
    service = ScrapingService()
    
    # Health check all scrapers
    health_status = await service.health_check_all()
    
    for scraper_name, status in health_status.items():
        logger.info(f"{scraper_name}:")
        logger.info(f"  - Accessible: {status.get('accessible', False)}")
        logger.info(f"  - Status: {status.get('status', 'unknown')}")
        if status.get('error'):
            logger.info(f"  - Error: {status['error']}")

async def main():
    """Main example function"""
    logger.info("YotCrew.app Daywork123 Scraper Examples")
    logger.info("=" * 50)
    
    try:
        # Check initial database status
        db_status = check_database_status()
        
        # Example 1: Basic scraping
        await example_basic_scraping()
        
        # Example 2: Manual scraping
        await example_manual_save()
        
        # Example 3: Using service
        await example_using_service()
        
        # Example 4: Health check
        await example_health_check()
        
        # Final database status
        logger.info("\n=== Final Status ===")
        final_status = check_database_status()
        
        # Show changes
        new_jobs = final_status["total"] - db_status["total"]
        if new_jobs > 0:
            logger.info(f"Added {new_jobs} new jobs during examples")
        
    except Exception as e:
        logger.error(f"Error in examples: {e}")
        raise

if __name__ == "__main__":
    # Run examples
    asyncio.run(main())

