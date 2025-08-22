"""
Advanced scheduler for Daywork123 scraper with time-based intervals.

This module implements a comprehensive scheduling system using APScheduler that
runs the Daywork123 scraper at different frequencies throughout the day.
"""
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED
from apscheduler.triggers.cron import CronTrigger

from .config import SchedulerConfig
from .scrapers.registry import ScraperRegistry
from .database import SessionLocal
from .models import ScrapingJob


async def run_daywork123_scraping_job(period: str, hour: int, minute: int, max_pages: int = 5):
    """
    Standalone function to execute the Daywork123 scraping task.
    
    This function is separate from the scheduler class to avoid serialization issues.
    
    Args:
        period: Time period ('morning', 'day', 'evening')
        hour: Hour when the job was scheduled
        minute: Minute when the job was scheduled
        max_pages: Maximum pages to scrape
    """
    start_time = datetime.now()
    db = SessionLocal()
    scraping_job = None
    
    try:
        logger.info(f"Starting Daywork123 scraping - {period} ({hour:02d}:{minute:02d})")
        
        # Create scraping job record
        scraping_job = ScrapingJob(
            status="started",
            started_at=start_time,
            scraper_type=f"daywork123_{period}",
            job_id=f"daywork123_{period}_{hour:02d}_{minute:02d}"
        )
        db.add(scraping_job)
        db.commit()
        
        # Get the Daywork123 scraper from registry
        scraper_registry = ScraperRegistry()
        scraper = scraper_registry.get_scraper('daywork123')
        
        if not scraper:
            raise ValueError("Daywork123 scraper not found in registry")
        
        # Run the scraper
        jobs_found = await scraper.scrape_and_save_jobs(max_pages=max_pages)
        
        # Update scraping job with results
        scraping_job.status = "completed"
        scraping_job.completed_at = datetime.now()
        scraping_job.jobs_found = len(jobs_found) if jobs_found else 0
        scraping_job.new_jobs = len(jobs_found) if jobs_found else 0  # This would need proper new job detection
        db.commit()
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Daywork123 scraping completed - {period} "
            f"({hour:02d}:{minute:02d}) - "
            f"Found {len(jobs_found) if jobs_found else 0} jobs in {duration:.2f}s"
        )
        
    except Exception as e:
        logger.error(f"Error in Daywork123 scraping - {period} ({hour:02d}:{minute:02d}): {e}")
        
        # Update scraping job with error
        if scraping_job:
            try:
                scraping_job.status = "failed"
                scraping_job.completed_at = datetime.now()
                scraping_job.error_message = str(e)
                db.commit()
            except Exception as db_error:
                logger.error(f"Error updating scraping job status: {db_error}")
                
    finally:
        db.close()


logger = logging.getLogger(__name__)


class ScrapingScheduler:
    """
    Advanced scheduler for automating scraping tasks with time-based intervals.
    
    This scheduler creates multiple cron jobs for different periods of the day:
    - Morning: High frequency scraping during morning hours
    - Day: Lower frequency scraping during daytime hours  
    - Evening: High frequency scraping during evening hours
    """
    
    def __init__(self, config: SchedulerConfig = None):
        """
        Initialize the scraping scheduler.
        
        Args:
            config: Configuration object, defaults to SchedulerConfig
        """
        self.config = config or SchedulerConfig()
        self.scheduler = None
        self._setup_scheduler()
        
    def _setup_scheduler(self):
        """Setup the APScheduler with appropriate configuration."""
        # Configure job store for persistence
        jobstores = {
            'default': SQLAlchemyJobStore(
                url=self.config.DB_URL,
                tablename=self.config.JOBSTORE_TABLE_NAME
            )
        }
        
        # Configure executor for async execution
        executors = {
            'default': AsyncIOExecutor()
        }
        
        # Configure job defaults
        job_defaults = {
            'coalesce': self.config.COALESCE,
            'max_instances': self.config.MAX_INSTANCES,
            'misfire_grace_time': self.config.MISFIRE_GRACE_TIME
        }
        
        # Create the scheduler
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        
        # Add event listeners
        self.scheduler.add_listener(self._job_executed_listener, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error_listener, EVENT_JOB_ERROR)
        self.scheduler.add_listener(self._job_missed_listener, EVENT_JOB_MISSED)
        
    def _job_executed_listener(self, event):
        """Handle job execution events."""
        logger.info(f"Job {event.job_id} executed successfully")
        
    def _job_error_listener(self, event):
        """Handle job error events."""
        logger.error(f"Job {event.job_id} failed: {event.exception}")
        
    def _job_missed_listener(self, event):
        """Handle missed job events."""
        logger.warning(f"Job {event.job_id} was missed")
        
    async def start(self):
        """Start the scheduler and schedule default jobs."""
        try:
            # Validate configuration
            if not self.config.validate_config():
                raise ValueError("Invalid scheduler configuration")
            
            # Start the scheduler
            self.scheduler.start()
            logger.info("Scheduler started successfully")
            
            # Schedule the default Daywork123 scraper jobs
            await self.schedule_daywork123_scraper()
            
            # Print configuration summary
            self.config.print_schedule_summary()
            
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
            raise
            
    async def stop(self):
        """Stop the scheduler gracefully."""
        try:
            if self.scheduler and self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                logger.info("Scheduler stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
            
    async def schedule_daywork123_scraper(self):
        """
        Schedule Daywork123 scraper jobs with time-based intervals.
        
        Creates three separate cron jobs:
        - Morning: High frequency during morning hours
        - Day: Lower frequency during daytime hours
        - Evening: High frequency during evening hours
        """
        try:
            # Remove existing Daywork123 jobs
            await self.remove_daywork123_jobs()
            
            # Schedule morning jobs
            for hour in self.config.MORNING_HOURS:
                for minute in self.config.MORNING_MINUTES:
                    job_id = f'daywork123_morning_{hour:02d}_{minute:02d}'
                    self.scheduler.add_job(
                        func=run_daywork123_scraping_job,
                        trigger=CronTrigger(hour=hour, minute=minute),
                        id=job_id,
                        name=f'Daywork123 Morning Scraping ({hour:02d}:{minute:02d})',
                        kwargs={
                            'period': 'morning', 
                            'hour': hour, 
                            'minute': minute,
                            'max_pages': self.config.DAYWORK123_MAX_PAGES
                        },
                        replace_existing=True
                    )
            
            # Schedule day jobs
            for hour in self.config.DAY_HOURS:
                for minute in self.config.DAY_MINUTES:
                    job_id = f'daywork123_day_{hour:02d}_{minute:02d}'
                    self.scheduler.add_job(
                        func=run_daywork123_scraping_job,
                        trigger=CronTrigger(hour=hour, minute=minute),
                        id=job_id,
                        name=f'Daywork123 Day Scraping ({hour:02d}:{minute:02d})',
                        kwargs={
                            'period': 'day', 
                            'hour': hour, 
                            'minute': minute,
                            'max_pages': self.config.DAYWORK123_MAX_PAGES
                        },
                        replace_existing=True
                    )
            
            # Schedule evening jobs
            for hour in self.config.EVENING_HOURS:
                for minute in self.config.EVENING_MINUTES:
                    job_id = f'daywork123_evening_{hour:02d}_{minute:02d}'
                    self.scheduler.add_job(
                        func=run_daywork123_scraping_job,
                        trigger=CronTrigger(hour=hour, minute=minute),
                        id=job_id,
                        name=f'Daywork123 Evening Scraping ({hour:02d}:{minute:02d})',
                        kwargs={
                            'period': 'evening', 
                            'hour': hour, 
                            'minute': minute,
                            'max_pages': self.config.DAYWORK123_MAX_PAGES
                        },
                        replace_existing=True
                    )
            
            total_jobs = self.config.get_total_daily_runs()
            logger.info(f"Scheduled {total_jobs} Daywork123 scraping jobs per day")
            
        except Exception as e:
            logger.error(f"Error scheduling Daywork123 scraper: {e}")
            raise
            

            
    async def remove_daywork123_jobs(self):
        """Remove all Daywork123 scraper jobs."""
        try:
            jobs_to_remove = []
            for job in self.scheduler.get_jobs():
                if job.id.startswith('daywork123_'):
                    jobs_to_remove.append(job.id)
            
            for job_id in jobs_to_remove:
                self.scheduler.remove_job(job_id)
                
            logger.info(f"Removed {len(jobs_to_remove)} existing Daywork123 jobs")
            
        except Exception as e:
            logger.error(f"Error removing Daywork123 jobs: {e}")
            
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """
        Get status information for a specific job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            Dictionary with job information or None if not found
        """
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                return {
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time,
                    'trigger': str(job.trigger),
                    'kwargs': job.kwargs
                }
        except Exception as e:
            logger.error(f"Error getting job status for {job_id}: {e}")
        return None
        
    def get_all_jobs_status(self) -> List[Dict]:
        """
        Get status information for all scheduled jobs.
        
        Returns:
            List of dictionaries with job information
        """
        jobs_status = []
        try:
            for job in self.scheduler.get_jobs():
                if job.id.startswith('daywork123_'):
                    jobs_status.append({
                        'id': job.id,
                        'name': job.name,
                        'next_run_time': job.next_run_time,
                        'trigger': str(job.trigger),
                        'kwargs': job.kwargs
                    })
        except Exception as e:
            logger.error(f"Error getting jobs status: {e}")
        return jobs_status
        
    def pause_job(self, job_id: str) -> bool:
        """
        Pause a specific job.
        
        Args:
            job_id: ID of the job to pause
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Job {job_id} paused")
            return True
        except Exception as e:
            logger.error(f"Error pausing job {job_id}: {e}")
            return False
            
    def resume_job(self, job_id: str) -> bool:
        """
        Resume a specific job.
        
        Args:
            job_id: ID of the job to resume
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Job {job_id} resumed")
            return True
        except Exception as e:
            logger.error(f"Error resuming job {job_id}: {e}")
            return False
            
    def remove_job(self, job_id: str) -> bool:
        """
        Remove a specific job.
        
        Args:
            job_id: ID of the job to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Job {job_id} removed")
            return True
        except Exception as e:
            logger.error(f"Error removing job {job_id}: {e}")
            return False
            
    def is_running(self) -> bool:
        """Check if the scheduler is running."""
        return self.scheduler and self.scheduler.running
        
    def get_scheduler_status(self) -> Dict:
        """
        Get overall scheduler status.
        
        Returns:
            Dictionary with scheduler status information
        """
        try:
            return {
                'running': self.is_running(),
                'total_jobs': len(self.scheduler.get_jobs()) if self.scheduler else 0,
                'daywork123_jobs': len([j for j in self.scheduler.get_jobs() if j.id.startswith('daywork123_')]) if self.scheduler else 0,
                'config': {
                    'morning_hours': self.config.MORNING_HOURS,
                    'morning_minutes': self.config.MORNING_MINUTES,
                    'day_hours': self.config.DAY_HOURS,
                    'day_minutes': self.config.DAY_MINUTES,
                    'evening_hours': self.config.EVENING_HOURS,
                    'evening_minutes': self.config.EVENING_MINUTES,
                    'max_pages': self.config.DAYWORK123_MAX_PAGES,
                    'total_daily_runs': self.config.get_total_daily_runs()
                }
            }
        except Exception as e:
            logger.error(f"Error getting scheduler status: {e}")
            return {'running': False, 'error': str(e)}
