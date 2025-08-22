"""
Scheduler service layer for managing scraping automation.

This module provides a high-level interface to the scheduler functionality,
making it easier to use from other parts of the application.
"""
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from ..daywork_scheduler import ScrapingScheduler, run_daywork123_scraping_job
from ..config import SchedulerConfig
from ..scrapers.registry import ScraperRegistry


logger = logging.getLogger(__name__)


class SchedulerService:
    """
    High-level service for managing the scraping scheduler.
    
    This service provides a simplified interface to the scheduler functionality
    and handles common operations like starting, stopping, and monitoring jobs.
    """
    
    def __init__(self, config: SchedulerConfig = None):
        """
        Initialize the scheduler service.
        
        Args:
            config: Configuration object, defaults to SchedulerConfig
        """
        self.config = config or SchedulerConfig()
        self.scheduler = ScrapingScheduler(self.config)
        self._running = False
        
    async def start(self):
        """Start the scheduler service."""
        try:
            if self._running:
                logger.warning("Scheduler service is already running")
                return
                
            await self.scheduler.start()
            self._running = True
            logger.info("Scheduler service started successfully")
            
        except Exception as e:
            logger.error(f"Error starting scheduler service: {e}")
            raise
            
    async def stop(self):
        """Stop the scheduler service."""
        try:
            if not self._running:
                logger.warning("Scheduler service is not running")
                return
                
            await self.scheduler.stop()
            self._running = False
            logger.info("Scheduler service stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping scheduler service: {e}")
            raise
            
    def get_scheduler_status(self) -> Dict:
        """
        Get comprehensive scheduler status information.
        
        Returns:
            Dictionary with scheduler status, job information, and configuration
        """
        try:
            status = self.scheduler.get_scheduler_status()
            status.update({
                'service_running': self._running,
                'last_updated': datetime.now().isoformat()
            })
            return status
        except Exception as e:
            logger.error(f"Error getting scheduler status: {e}")
            return {
                'service_running': False,
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }
            
    async def run_daywork123_now(self, period: str = 'manual') -> Dict:
        """
        Execute the Daywork123 scraper immediately.
        
        Args:
            period: Period identifier for logging purposes
            
        Returns:
            Dictionary with execution results
        """
        try:
            start_time = datetime.now()
            logger.info(f"Running Daywork123 scraper manually ({period})")
            
            # Use the standalone function to run the scraper
            # We use current time for hour/minute since this is a manual run
            current_hour = start_time.hour
            current_minute = start_time.minute
            
            await run_daywork123_scraping_job(
                period=period,
                hour=current_hour,
                minute=current_minute,
                max_pages=self.config.DAYWORK123_MAX_PAGES
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            result = {
                'success': True,
                'period': period,
                'started_at': start_time.isoformat(),
                'duration_seconds': duration,
                'max_pages': self.config.DAYWORK123_MAX_PAGES
            }
            
            logger.info(
                f"Manual Daywork123 scraping completed - "
                f"Duration: {duration:.2f}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error running Daywork123 scraper manually: {e}")
            return {
                'success': False,
                'error': str(e),
                'period': period,
                'started_at': start_time.isoformat() if 'start_time' in locals() else None
            }
            
    async def update_daywork123_schedule(
        self,
        morning_hours: List[int] = None,
        morning_minutes: List[int] = None,
        day_hours: List[int] = None,
        day_minutes: List[int] = None,
        evening_hours: List[int] = None,
        evening_minutes: List[int] = None
    ) -> Dict:
        """
        Update the complete Daywork123 schedule with new time periods.
        
        Args:
            morning_hours: New morning hours (0-23)
            morning_minutes: New morning minutes (0-59)
            day_hours: New day hours (0-23)
            day_minutes: New day minutes (0-59)
            evening_hours: New evening hours (0-23)
            evening_minutes: New evening minutes (0-59)
            
        Returns:
            Dictionary with update results
        """
        try:
            # Update configuration if new values provided
            if morning_hours is not None:
                self.config.MORNING_HOURS = morning_hours
            if morning_minutes is not None:
                self.config.MORNING_MINUTES = morning_minutes
            if day_hours is not None:
                self.config.DAY_HOURS = day_hours
            if day_minutes is not None:
                self.config.DAY_MINUTES = day_minutes
            if evening_hours is not None:
                self.config.EVENING_HOURS = evening_hours
            if evening_minutes is not None:
                self.config.EVENING_MINUTES = evening_minutes
            
            # Validate new configuration
            if not self.config.validate_config():
                raise ValueError("Invalid schedule configuration")
            
            # Reschedule jobs
            await self.scheduler.schedule_daywork123_scraper()
            
            result = {
                'success': True,
                'updated_at': datetime.now().isoformat(),
                'new_schedule': {
                    'morning_hours': self.config.MORNING_HOURS,
                    'morning_minutes': self.config.MORNING_MINUTES,
                    'day_hours': self.config.DAY_HOURS,
                    'day_minutes': self.config.DAY_MINUTES,
                    'evening_hours': self.config.EVENING_HOURS,
                    'evening_minutes': self.config.EVENING_MINUTES
                },
                'total_daily_runs': self.config.get_total_daily_runs()
            }
            
            logger.info(f"Daywork123 schedule updated - {result['total_daily_runs']} runs per day")
            return result
            
        except Exception as e:
            logger.error(f"Error updating Daywork123 schedule: {e}")
            return {
                'success': False,
                'error': str(e),
                'updated_at': datetime.now().isoformat()
            }
            
    async def update_morning_schedule(
        self,
        hours: List[int],
        minutes: List[int]
    ) -> Dict:
        """
        Update only the morning scraping schedule.
        
        Args:
            hours: New morning hours (0-23)
            minutes: New morning minutes (0-59)
            
        Returns:
            Dictionary with update results
        """
        return await self.update_daywork123_schedule(
            morning_hours=hours,
            morning_minutes=minutes
        )
        
    async def update_day_schedule(
        self,
        hours: List[int],
        minutes: List[int]
    ) -> Dict:
        """
        Update only the daytime scraping schedule.
        
        Args:
            hours: New day hours (0-23)
            minutes: New day minutes (0-59)
            
        Returns:
            Dictionary with update results
        """
        return await self.update_daywork123_schedule(
            day_hours=hours,
            day_minutes=minutes
        )
        
    async def update_evening_schedule(
        self,
        hours: List[int],
        minutes: List[int]
    ) -> Dict:
        """
        Update only the evening scraping schedule.
        
        Args:
            hours: New evening hours (0-23)
            minutes: New evening minutes (0-59)
            
        Returns:
            Dictionary with update results
        """
        return await self.update_daywork123_schedule(
            evening_hours=hours,
            evening_minutes=minutes
        )
        
    def get_jobs_status(self) -> List[Dict]:
        """
        Get status information for all Daywork123 jobs.
        
        Returns:
            List of dictionaries with job information
        """
        try:
            return self.scheduler.get_all_jobs_status()
        except Exception as e:
            logger.error(f"Error getting jobs status: {e}")
            return []
            
    def pause_job(self, job_id: str) -> Dict:
        """
        Pause a specific job.
        
        Args:
            job_id: ID of the job to pause
            
        Returns:
            Dictionary with operation result
        """
        try:
            success = self.scheduler.pause_job(job_id)
            return {
                'success': success,
                'job_id': job_id,
                'action': 'pause',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error pausing job {job_id}: {e}")
            return {
                'success': False,
                'job_id': job_id,
                'action': 'pause',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    def resume_job(self, job_id: str) -> Dict:
        """
        Resume a specific job.
        
        Args:
            job_id: ID of the job to resume
            
        Returns:
            Dictionary with operation result
        """
        try:
            success = self.scheduler.resume_job(job_id)
            return {
                'success': success,
                'job_id': job_id,
                'action': 'resume',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error resuming job {job_id}: {e}")
            return {
                'success': False,
                'job_id': job_id,
                'action': 'resume',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    def remove_job(self, job_id: str) -> Dict:
        """
        Remove a specific job.
        
        Args:
            job_id: ID of the job to remove
            
        Returns:
            Dictionary with operation result
        """
        try:
            success = self.scheduler.remove_job(job_id)
            return {
                'success': success,
                'job_id': job_id,
                'action': 'remove',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error removing job {job_id}: {e}")
            return {
                'success': False,
                'job_id': job_id,
                'action': 'remove',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """
        Get status information for a specific job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            Dictionary with job information or None if not found
        """
        try:
            return self.scheduler.get_job_status(job_id)
        except Exception as e:
            logger.error(f"Error getting job status for {job_id}: {e}")
            return None
            
    def is_running(self) -> bool:
        """Check if the scheduler service is running."""
        return self._running and self.scheduler.is_running()
        
    async def restart(self):
        """Restart the scheduler service."""
        try:
            logger.info("Restarting scheduler service")
            await self.stop()
            await self.start()
            logger.info("Scheduler service restarted successfully")
        except Exception as e:
            logger.error(f"Error restarting scheduler service: {e}")
            raise
            
    def get_next_runs(self, limit: int = 10) -> List[Dict]:
        """
        Get information about the next scheduled runs.
        
        Args:
            limit: Maximum number of next runs to return
            
        Returns:
            List of dictionaries with next run information
        """
        try:
            jobs = self.scheduler.get_all_jobs_status()
            next_runs = []
            
            for job in jobs:
                if job.get('next_run_time'):
                    next_runs.append({
                        'job_id': job['id'],
                        'job_name': job['name'],
                        'next_run_time': job['next_run_time'],
                        'period': job.get('kwargs', {}).get('period', 'unknown')
                    })
            
            # Sort by next run time
            next_runs.sort(key=lambda x: x['next_run_time'])
            
            return next_runs[:limit]
            
        except Exception as e:
            logger.error(f"Error getting next runs: {e}")
            return []
