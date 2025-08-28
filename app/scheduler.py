from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from datetime import datetime
from .database import SessionLocal
from .models import Job, ScrapingJob
from .scrapers.yotspot import YotspotScraper

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
scraper = YotspotScraper()

def scheduled_scrape_job():
    """Scheduled function to scrape jobs"""
    db = SessionLocal()
    try:
        logger.info("Starting scheduled job scraping...")
        
        # Create scraping job record
        scraping_job = ScrapingJob(
            status="started",
            started_at=datetime.now(),
            scraper_type="yotspot_scheduled"
        )
        db.add(scraping_job)
        db.commit()
        
        # Run scraper
        jobs_found = []
        try:
            # Note: We need to make this async-compatible or run in sync mode
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            jobs_found = loop.run_until_complete(scraper.scrape_jobs(max_pages=3))
        except Exception as e:
            logger.error(f"Error in scheduled scraping: {e}")
            jobs_found = []
        
        # Save jobs to database
        new_jobs = 0
        for job_data in jobs_found:
            try:
                existing_job = db.query(Job).filter(Job.external_id == job_data["external_id"]).first()
                if not existing_job:
                    job = Job(**job_data)
                    db.add(job)
                    new_jobs += 1
            except Exception as e:
                logger.error(f"Error saving job: {e}")
                continue
        
        db.commit()
        
        # Update scraping job
        scraping_job.status = "completed"
        scraping_job.completed_at = datetime.now()
        scraping_job.jobs_found = len(jobs_found)
        scraping_job.new_jobs = new_jobs
        db.commit()
        
        logger.info(f"Scheduled scraping completed. Found {len(jobs_found)} jobs, {new_jobs} new")
        
    except Exception as e:
        logger.error(f"Error in scheduled scrape: {e}")
        # Update scraping job with error
        try:
            scraping_job = db.query(ScrapingJob).filter(ScrapingJob.id == scraping_job.id).first()
            if scraping_job:
                scraping_job.status = "failed"
                scraping_job.completed_at = datetime.now()
                scraping_job.error_message = str(e)
                db.commit()
        except:
            pass
    finally:
        db.close()

def start_scheduler():
    """Start the background scheduler"""
    try:
        # Schedule job scraping every 45 minutes
        scheduler.add_job(
            func=scheduled_scrape_job,
            trigger=IntervalTrigger(minutes=45),
            id='scrape_jobs',
                            name='Scrape jobs for YotCrew.app',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Scheduler started - jobs will be scraped every 45 minutes")
        
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")

def stop_scheduler():
    """Stop the background scheduler"""
    try:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}") 