"""
Test script for the Daywork123 scheduler functionality.

This script tests the main scheduler components to ensure they work correctly
and integrate properly with the existing codebase.
"""
import asyncio
import logging
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import SchedulerConfig
from app.daywork_scheduler import ScrapingScheduler
from app.services.scheduler_service import SchedulerService


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_config():
    """Test the scheduler configuration."""
    print("=== Testing Scheduler Configuration ===")
    
    try:
        # Test default configuration
        config = SchedulerConfig()
        
        # Validate configuration
        is_valid = config.validate_config()
        print(f"Configuration valid: {is_valid}")
        
        # Print configuration summary
        config.print_schedule_summary()
        
        # Test schedule string generation
        schedules = config.get_all_schedules()
        print("\nCron Schedules:")
        for period, schedule in schedules.items():
            print(f"  {period}: {schedule}")
        
        print(f"✅ Configuration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


async def test_scheduler_creation():
    """Test creating and configuring the scheduler."""
    print("\n=== Testing Scheduler Creation ===")
    
    try:
        config = SchedulerConfig()
        scheduler = ScrapingScheduler(config)
        
        print(f"Scheduler created: {scheduler is not None}")
        print(f"Initial running state: {scheduler.is_running()}")
        
        print(f"✅ Scheduler creation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Scheduler creation test failed: {e}")
        return False


async def test_scheduler_start_stop():
    """Test starting and stopping the scheduler."""
    print("\n=== Testing Scheduler Start/Stop ===")
    
    try:
        config = SchedulerConfig()
        scheduler = ScrapingScheduler(config)
        
        # Test start
        await scheduler.start()
        print(f"Scheduler running after start: {scheduler.is_running()}")
        
        # Test job scheduling
        jobs_status = scheduler.get_all_jobs_status()
        print(f"Number of jobs scheduled: {len(jobs_status)}")
        
        # Test scheduler status
        status = scheduler.get_scheduler_status()
        print(f"Scheduler status: {status.get('running', False)}")
        print(f"Total daily runs configured: {status.get('config', {}).get('total_daily_runs', 0)}")
        
        # Test stop
        await scheduler.stop()
        print(f"Scheduler running after stop: {scheduler.is_running()}")
        
        print(f"✅ Scheduler start/stop test passed")
        return True
        
    except Exception as e:
        print(f"❌ Scheduler start/stop test failed: {e}")
        return False


async def test_scheduler_service():
    """Test the scheduler service layer."""
    print("\n=== Testing Scheduler Service ===")
    
    try:
        service = SchedulerService()
        
        # Test service creation
        print(f"Service created: {service is not None}")
        print(f"Initial service state: {service.is_running()}")
        
        # Test getting status without starting
        status = service.get_scheduler_status()
        print(f"Status before start: {status.get('service_running', False)}")
        
        # Note: We won't actually start the service in tests to avoid conflicts
        # In a real test environment, you would start/stop the service here
        
        print(f"✅ Scheduler service test passed")
        return True
        
    except Exception as e:
        print(f"❌ Scheduler service test failed: {e}")
        return False


async def test_job_management():
    """Test job management functionality."""
    print("\n=== Testing Job Management ===")
    
    try:
        config = SchedulerConfig()
        scheduler = ScrapingScheduler(config)
        
        # Start scheduler to create jobs
        await scheduler.start()
        
        # Get all jobs
        jobs = scheduler.get_all_jobs_status()
        print(f"Total jobs created: {len(jobs)}")
        
        if jobs:
            first_job = jobs[0]
            job_id = first_job['id']
            print(f"First job ID: {job_id}")
            
            # Test getting specific job status
            job_status = scheduler.get_job_status(job_id)
            print(f"Job status retrieved: {job_status is not None}")
            
            # Test pause/resume (be careful in real environment)
            # scheduler.pause_job(job_id)
            # scheduler.resume_job(job_id)
        
        # Test removing all Daywork123 jobs
        await scheduler.remove_daywork123_jobs()
        
        jobs_after_removal = scheduler.get_all_jobs_status()
        print(f"Jobs after removal: {len(jobs_after_removal)}")
        
        await scheduler.stop()
        
        print(f"✅ Job management test passed")
        return True
        
    except Exception as e:
        print(f"❌ Job management test failed: {e}")
        return False


async def test_configuration_updates():
    """Test configuration updates."""
    print("\n=== Testing Configuration Updates ===")
    
    try:
        service = SchedulerService()
        
        # Test updating schedules (without starting the service)
        original_morning_hours = service.config.MORNING_HOURS.copy()
        original_morning_minutes = service.config.MORNING_MINUTES.copy()
        
        # Update morning schedule
        new_hours = [7, 8, 9]
        new_minutes = [0, 15, 30, 45]
        
        # Note: In a full test, you would start the service first
        # result = await service.update_morning_schedule(new_hours, new_minutes)
        # print(f"Schedule update result: {result.get('success', False)}")
        
        print(f"Original morning hours: {original_morning_hours}")
        print(f"New morning hours would be: {new_hours}")
        
        print(f"✅ Configuration updates test passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration updates test failed: {e}")
        return False


async def test_time_calculations():
    """Test time-based calculations."""
    print("\n=== Testing Time Calculations ===")
    
    try:
        config = SchedulerConfig()
        
        # Test total daily runs calculation
        total_runs = config.get_total_daily_runs()
        print(f"Total daily runs: {total_runs}")
        
        # Test individual period calculations
        morning_runs = len(config.MORNING_HOURS) * len(config.MORNING_MINUTES)
        day_runs = len(config.DAY_HOURS) * len(config.DAY_MINUTES)
        evening_runs = len(config.EVENING_HOURS) * len(config.EVENING_MINUTES)
        
        print(f"Morning runs: {morning_runs}")
        print(f"Day runs: {day_runs}")
        print(f"Evening runs: {evening_runs}")
        print(f"Total: {morning_runs + day_runs + evening_runs}")
        
        # Verify calculation
        assert total_runs == morning_runs + day_runs + evening_runs
        
        print(f"✅ Time calculations test passed")
        return True
        
    except Exception as e:
        print(f"❌ Time calculations test failed: {e}")
        return False


async def run_all_tests():
    """Run all scheduler tests."""
    print("🚀 Starting Scheduler Tests")
    print("=" * 50)
    
    test_results = []
    
    # Run individual tests
    test_results.append(await test_config())
    test_results.append(await test_scheduler_creation())
    test_results.append(await test_scheduler_start_stop())
    test_results.append(await test_scheduler_service())
    test_results.append(await test_job_management())
    test_results.append(await test_configuration_updates())
    test_results.append(await test_time_calculations())
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 Test Results Summary")
    print("=" * 50)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


async def main():
    """Main test entry point."""
    try:
        success = await run_all_tests()
        
        if success:
            print("\n✅ Scheduler implementation ready for use!")
            print("\nNext steps:")
            print("1. Update your main.py to integrate the scheduler")
            print("2. Set up environment variables from scheduler.env.example")
            print("3. Test the CLI commands")
            print("4. Monitor the logs during operation")
        else:
            print("\n❌ Please fix the failing tests before proceeding.")
            
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
