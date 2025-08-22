#!/usr/bin/env python3
"""
Scrape jobs from Daywork123 and save to database
"""
import asyncio
import logging
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.scrapers.daywork123 import Daywork123Scraper
from app.database import SessionLocal
from app.models import Job

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def scrape_and_save_jobs():
    """Scrape Daywork123 and save jobs to database"""
    logger.info("🚀 Starting Daywork123 scraping...")
    
    scraper = Daywork123Scraper()
    
    # Test connection first
    logger.info("Testing connection to Daywork123.com...")
    if not await scraper.test_connection():
        logger.warning("⚠️  Cannot connect to Daywork123.com")
        logger.info("This might be due to:")
        logger.info("- Network connectivity issues")
        logger.info("- Website blocking requests")
        logger.info("- Site temporarily unavailable")
        return False
    
    logger.info("✅ Connection successful!")
    
    # Scrape and save jobs
    logger.info("Scraping jobs from Daywork123.com (2 pages)...")
    result = await scraper.scrape_and_save_jobs(max_pages=2)
    
    if result['success']:
        logger.info(f"✅ Scraping completed successfully!")
        logger.info(f"   📊 Jobs found: {result['jobs_found']}")
        logger.info(f"   💾 Jobs saved: {result['jobs_saved']}")
        logger.info(f"   ⏱️  Duration: {result['duration']:.2f} seconds")
        
        # Verify database content
        with SessionLocal() as db:
            total_jobs = db.query(Job).count()
            daywork123_jobs = db.query(Job).filter(Job.source == 'daywork123').count()
            
            logger.info(f"📋 Database verification:")
            logger.info(f"   Total jobs: {total_jobs}")
            logger.info(f"   Daywork123 jobs: {daywork123_jobs}")
            
            # Show sample jobs
            sample_jobs = db.query(Job).limit(3).all()
            if sample_jobs:
                logger.info("📝 Sample scraped jobs:")
                for job in sample_jobs:
                    quality_icon = "⭐" if job.quality_score >= 0.8 else "✨" if job.quality_score >= 0.6 else "💫"
                    logger.info(f"   {quality_icon} {job.title} @ {job.company} ({job.location})")
        
        return True
    else:
        logger.error(f"❌ Scraping failed!")
        for error in result.get('errors', []):
            logger.error(f"   Error: {error}")
        return False

async def main():
    """Main function"""
    print("=" * 60)
    print("🔄 YotCrew.app - Daywork123 Scraper")
    print("=" * 60)
    
    try:
        success = await scrape_and_save_jobs()
        
        if success:
            print("\n🎉 Scraping completed successfully!")
            print("✅ Real jobs from Daywork123.com are now in the database")
            print("✅ Ready to start the application and view jobs")
            print("\nNext steps:")
            print("1. Start the application: python main.py")
            print("2. Open browser: http://localhost:8000")
            print("3. See the scraped jobs rendered on the frontend!")
        else:
            print("\n❌ Scraping failed - check the logs above")
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

