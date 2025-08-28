"""
Configuration module for the scheduler functionality.

This module defines all configuration parameters for the APScheduler integration,
including time-based intervals for different periods of the day.
"""
import os
from typing import List


class SchedulerConfig:
    """Configuration class for scheduler settings with time-based intervals."""
    
    # Database Configuration - Use same database as main application
    DB_URL: str = os.getenv('SCHEDULER_DB_URL', 'sqlite:///./yacht_jobs.db')
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Daywork123 Scraper Configuration
    DAYWORK123_MAX_PAGES: int = int(os.getenv('DAYWORK123_MAX_PAGES', '5'))
    
    # Time-based interval definitions
    # Morning hours: High activity period (6 AM - 9 AM)
    MORNING_HOURS: List[int] = [
        int(h) for h in os.getenv('DAYWORK123_MORNING_HOURS', '6,7,8,9').split(',')
    ]
    MORNING_MINUTES: List[int] = [
        int(m) for m in os.getenv('DAYWORK123_MORNING_MINUTES', '0,30').split(',')
    ]
    
    # Day hours: Lower activity period (12 PM - 3 PM)
    DAY_HOURS: List[int] = [
        int(h) for h in os.getenv('DAYWORK123_DAY_HOURS', '12,15').split(',')
    ]
    DAY_MINUTES: List[int] = [
        int(m) for m in os.getenv('DAYWORK123_DAY_MINUTES', '0').split(',')
    ]
    
    # Evening hours: High activity period (6 PM - 9 PM)
    EVENING_HOURS: List[int] = [
        int(h) for h in os.getenv('DAYWORK123_EVENING_HOURS', '18,19,20,21').split(',')
    ]
    EVENING_MINUTES: List[int] = [
        int(m) for m in os.getenv('DAYWORK123_EVENING_MINUTES', '0,30').split(',')
    ]
    
    # Scheduler Job Configuration
    COALESCE: bool = os.getenv('SCHEDULER_COALESCE', 'true').lower() == 'true'
    MAX_INSTANCES: int = int(os.getenv('SCHEDULER_MAX_INSTANCES', '1'))
    MISFIRE_GRACE_TIME: int = int(os.getenv('SCHEDULER_MISFIRE_GRACE_TIME', '300'))  # 5 minutes
    
    # Job Store Configuration
    JOBSTORE_TABLE_NAME: str = os.getenv('SCHEDULER_JOBSTORE_TABLE', 'apscheduler_jobs')
    
    @classmethod
    def get_cron_schedule_string(cls, hours: List[int], minutes: List[int]) -> str:
        """
        Generate a cron schedule string from hours and minutes lists.
        
        Args:
            hours: List of hours (0-23)
            minutes: List of minutes (0-59)
            
        Returns:
            Cron schedule string for use with APScheduler
        """
        hours_str = ','.join(map(str, hours))
        minutes_str = ','.join(map(str, minutes))
        return f"{minutes_str} {hours_str} * * *"
    
    @classmethod
    def get_morning_schedule(cls) -> str:
        """Get the cron schedule string for morning scraping."""
        return cls.get_cron_schedule_string(cls.MORNING_HOURS, cls.MORNING_MINUTES)
    
    @classmethod
    def get_day_schedule(cls) -> str:
        """Get the cron schedule string for daytime scraping."""
        return cls.get_cron_schedule_string(cls.DAY_HOURS, cls.DAY_MINUTES)
    
    @classmethod
    def get_evening_schedule(cls) -> str:
        """Get the cron schedule string for evening scraping."""
        return cls.get_cron_schedule_string(cls.EVENING_HOURS, cls.EVENING_MINUTES)
    
    @classmethod
    def get_all_schedules(cls) -> dict:
        """Get all schedule strings as a dictionary."""
        return {
            'morning': cls.get_morning_schedule(),
            'day': cls.get_day_schedule(),
            'evening': cls.get_evening_schedule()
        }
    
    @classmethod
    def get_total_daily_runs(cls) -> int:
        """Calculate the total number of scraping runs per day."""
        morning_runs = len(cls.MORNING_HOURS) * len(cls.MORNING_MINUTES)
        day_runs = len(cls.DAY_HOURS) * len(cls.DAY_MINUTES)
        evening_runs = len(cls.EVENING_HOURS) * len(cls.EVENING_MINUTES)
        return morning_runs + day_runs + evening_runs
    
    @classmethod
    def validate_config(cls) -> bool:
        """
        Validate the configuration parameters.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        # Validate hours (0-23)
        all_hours = cls.MORNING_HOURS + cls.DAY_HOURS + cls.EVENING_HOURS
        if not all(0 <= h <= 23 for h in all_hours):
            return False
        
        # Validate minutes (0-59)
        all_minutes = cls.MORNING_MINUTES + cls.DAY_MINUTES + cls.EVENING_MINUTES
        if not all(0 <= m <= 59 for m in all_minutes):
            return False
        
        # Validate max pages
        if cls.DAYWORK123_MAX_PAGES <= 0:
            return False
        
        # Validate max instances
        if cls.MAX_INSTANCES <= 0:
            return False
        
        return True
    
    @classmethod
    def print_schedule_summary(cls) -> None:
        """Print a summary of the current schedule configuration."""
        print("=== Scheduler Configuration Summary ===")
        print(f"Database URL: {cls.DB_URL}")
        print(f"Max Pages per Run: {cls.DAYWORK123_MAX_PAGES}")
        print(f"Total Daily Runs: {cls.get_total_daily_runs()}")
        print()
        
        print("Morning Schedule:")
        print(f"  Hours: {cls.MORNING_HOURS}")
        print(f"  Minutes: {cls.MORNING_MINUTES}")
        print(f"  Runs: {len(cls.MORNING_HOURS) * len(cls.MORNING_MINUTES)}")
        print()
        
        print("Day Schedule:")
        print(f"  Hours: {cls.DAY_HOURS}")
        print(f"  Minutes: {cls.DAY_MINUTES}")
        print(f"  Runs: {len(cls.DAY_HOURS) * len(cls.DAY_MINUTES)}")
        print()
        
        print("Evening Schedule:")
        print(f"  Hours: {cls.EVENING_HOURS}")
        print(f"  Minutes: {cls.EVENING_MINUTES}")
        print(f"  Runs: {len(cls.EVENING_HOURS) * len(cls.EVENING_MINUTES)}")
        print()
        
        print("Cron Schedules:")
        schedules = cls.get_all_schedules()
        for period, schedule in schedules.items():
            print(f"  {period.capitalize()}: {schedule}")
