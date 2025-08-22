#!/usr/bin/env python3
"""
Use the existing daywork123_scraper.py to scrape jobs and save to database
Modified to only scrape jobs from the last week
"""
import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta
import dateparser
import re

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import the existing scraper
from daywork123_scraper import Daywork123Scraper

# Import database components
from app.database import SessionLocal
from app.models import Job

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_posted_date(date_str):
    """Parse posted date string to datetime object"""
    if not date_str or date_str.strip() == "":
        return None
    
    try:
        # Try to parse the date using dateparser
        parsed_date = dateparser.parse(date_str)
        if parsed_date:
            return parsed_date
        
        # Fallback: try common date formats
        date_formats = [
            "%Y/%m/%d",
            "%m/%d/%Y", 
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%m-%d-%Y",
            "%d-%m-%Y"
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
                
    except Exception as e:
        logger.warning(f"Could not parse date '{date_str}': {e}")
    
    return None

def is_job_from_last_week(scraped_job):
    """Check if job was posted in the last 7 days"""
    posted_date_str = scraped_job.get('posted_date', '')
    
    if not posted_date_str:
        logger.debug(f"No posted date for job {scraped_job.get('id', 'unknown')}")
        return False
    
    posted_date = parse_posted_date(posted_date_str)
    
    if not posted_date:
        logger.debug(f"Could not parse posted date '{posted_date_str}' for job {scraped_job.get('id', 'unknown')}")
        return False
    
    # Calculate if job is from last week
    one_week_ago = datetime.now() - timedelta(days=7)
    is_recent = posted_date >= one_week_ago
    
    if is_recent:
        logger.info(f"✅ Job from last week: {scraped_job.get('title', 'Unknown')} (posted: {posted_date_str})")
    else:
        logger.debug(f"⏰ Job too old: {scraped_job.get('title', 'Unknown')} (posted: {posted_date_str})")
    
    return is_recent

def convert_to_db_job(scraped_job):
    """Convert scraped job data to database Job model"""
    
    # Create a proper external_id
    external_id = f"dw123_{scraped_job.get('id', 'unknown')}"
    
    # Parse the posted date
    posted_date = parse_posted_date(scraped_job.get('posted_date', ''))
    
    # Map job data to database fields
    db_job = Job(
        external_id=external_id,
        title=scraped_job.get('title', 'Unknown Title'),
        company=scraped_job.get('company', 'Unknown Company'),
        location=scraped_job.get('location', 'Unknown Location'),
        description=scraped_job.get('title', 'No description available'),
        
        # Set daywork123 as source
        source='daywork123',
        source_url=scraped_job.get('source_url', ''),
        
        # Default values for new fields
        vessel_type=None,
        vessel_size=None,
        vessel_name=None,
        employment_type='daywork',  # Default for Daywork123
        job_type='daywork',
        department=None,
        position_level=None,
        
        # Salary fields (daywork123 doesn't provide salary info)
        salary_range=None,
        salary_currency=None,
        salary_period=None,
        
        # Content fields
        requirements=[],  # Empty array for now
        benefits=[],      # Empty array for now
        
        # Location fields
        country=None,
        region=None,
        
        # Metadata
        quality_score=scraped_job.get('quality_score', 0.5),
        raw_data=scraped_job,  # Store original scraped data
        
        # Timestamps
        posted_date=posted_date or datetime.utcnow(),
        scraped_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    return db_job

def save_jobs_to_database(scraped_jobs):
    """Save scraped jobs to database"""
    if not scraped_jobs:
        logger.warning("No jobs to save")
        return 0
    
    logger.info(f"Saving {len(scraped_jobs)} jobs to database...")
    saved_count = 0
    updated_count = 0
    
    with SessionLocal() as db:
        for scraped_job in scraped_jobs:
            try:
                external_id = f"dw123_{scraped_job.get('id', 'unknown')}"
                
                # Check if job already exists
                existing_job = db.query(Job).filter(
                    Job.external_id == external_id,
                    Job.source == 'daywork123'
                ).first()
                
                if existing_job:
                    # Update existing job
                    existing_job.title = scraped_job.get('title', existing_job.title)
                    existing_job.company = scraped_job.get('company', existing_job.company)
                    existing_job.location = scraped_job.get('location', existing_job.location)
                    existing_job.source_url = scraped_job.get('source_url', existing_job.source_url)
                    existing_job.quality_score = scraped_job.get('quality_score', existing_job.quality_score)
                    existing_job.raw_data = scraped_job
                    existing_job.updated_at = datetime.utcnow()
                    updated_count += 1
                    logger.debug(f"Updated job: {existing_job.title}")
                else:
                    # Create new job
                    new_job = convert_to_db_job(scraped_job)
                    db.add(new_job)
                    saved_count += 1
                    logger.debug(f"Added new job: {new_job.title}")
                    
            except Exception as e:
                logger.error(f"Error processing job {scraped_job.get('id', 'unknown')}: {e}")
                continue
        
        try:
            db.commit()
            logger.info(f"✅ Database operation completed: {saved_count} new, {updated_count} updated")
        except Exception as e:
            logger.error(f"Error committing to database: {e}")
            db.rollback()
            return 0
    
    return saved_count + updated_count

async def main():
    """Main function to scrape and save jobs"""
    print("=" * 60)
    print("🔄 Daywork123 Scraper → Database Integration")
    print("=" * 60)
    
    # Configure the scraper
    BASE_URL = "https://www.daywork123.com/jobannouncementlist.aspx"
    MAX_PAGES = 2  # Scrape 2 pages for good sample
    
    try:
        # Initialize and run the existing scraper
        logger.info("🚀 Starting Daywork123 scraper...")
        scraper = Daywork123Scraper(base_url=BASE_URL)
        
        # Scrape jobs using the existing scraper
        await scraper.scrape_jobs(max_pages=MAX_PAGES)
        
        # Get the scraped jobs
        all_scraped_jobs = scraper.jobs
        
        logger.info(f"📊 Initial scraping completed:")
        logger.info(f"   Total jobs found: {len(all_scraped_jobs)}")
        
        if not all_scraped_jobs:
            logger.warning("No jobs were scraped. This might be due to:")
            logger.warning("- Website blocking requests")
            logger.warning("- Changes in website structure")
            logger.warning("- Network connectivity issues")
            return
        
        # Filter jobs from last week only
        logger.info("🔍 Filtering jobs from last week...")
        recent_jobs = [job for job in all_scraped_jobs if is_job_from_last_week(job)]
        
        logger.info(f"📊 Date filtering completed:")
        logger.info(f"   Total jobs scraped: {len(all_scraped_jobs)}")
        logger.info(f"   Jobs from last week: {len(recent_jobs)}")
        logger.info(f"   Filtered out: {len(all_scraped_jobs) - len(recent_jobs)} older jobs")
        
        if not recent_jobs:
            logger.warning("⚠️  No jobs from the last week found!")
            logger.info("This might mean:")
            logger.info("- No new jobs posted recently")
            logger.info("- Date parsing issues")
            logger.info("- Website date format changes")
            
            # Show sample dates for debugging
            logger.info("Sample posted dates from scraped jobs:")
            for i, job in enumerate(all_scraped_jobs[:5]):
                posted_date = job.get('posted_date', 'No date')
                logger.info(f"   {i+1}. {job.get('title', 'No title')} - Posted: {posted_date}")
            return
        
        # Use only recent jobs
        scraped_jobs = recent_jobs
        
        # Show sample of scraped jobs
        logger.info("📋 Sample scraped jobs:")
        for i, job in enumerate(scraped_jobs[:3]):
            logger.info(f"   {i+1}. {job.get('title', 'No title')} @ {job.get('company', 'No company')}")
        
        # Save to database
        logger.info("💾 Saving jobs to database...")
        total_saved = save_jobs_to_database(scraped_jobs)
        
        if total_saved > 0:
            # Verify database content
            with SessionLocal() as db:
                total_jobs = db.query(Job).count()
                daywork123_jobs = db.query(Job).filter(Job.source == 'daywork123').count()
                
                logger.info(f"📋 Database verification:")
                logger.info(f"   Total jobs in database: {total_jobs}")
                logger.info(f"   Daywork123 jobs: {daywork123_jobs}")
            
            print("\n🎉 SUCCESS!")
            print(f"✅ Scraped {len(scraped_jobs)} jobs from Daywork123.com")
            print(f"✅ Saved/updated {total_saved} jobs to database")
            print("✅ Ready to view jobs on the frontend")
            
            print("\n📋 Next steps:")
            print("1. Start the application: python main.py")
            print("2. Open browser: http://localhost:8000")
            print("3. Filter by 'Daywork123' to see scraped jobs")
            print("4. View JSON: curl 'http://localhost:8000/api/jobs?source=daywork123'")
        else:
            print("\n❌ Failed to save jobs to database")
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
