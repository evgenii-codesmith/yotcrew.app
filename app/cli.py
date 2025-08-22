"""
Command-line interface for scheduler management.

This module provides a convenient way to manually control the scheduler,
check status, run jobs immediately, and update schedules.
"""
import argparse
import asyncio
import json
import sys
from typing import List

from .services.scheduler_service import SchedulerService
from .config import SchedulerConfig


def parse_time_list(time_str: str) -> List[int]:
    """
    Parse a comma-separated string of integers.
    
    Args:
        time_str: Comma-separated string (e.g., "6,7,8,9")
        
    Returns:
        List of integers
    """
    try:
        return [int(x.strip()) for x in time_str.split(',')]
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid time format: {e}")


async def cmd_status(args):
    """Check scheduler status."""
    service = SchedulerService()
    
    try:
        status = service.get_scheduler_status()
        
        if args.json:
            print(json.dumps(status, indent=2, default=str))
        else:
            print("=== Scheduler Status ===")
            print(f"Service Running: {status.get('service_running', False)}")
            print(f"Scheduler Running: {status.get('running', False)}")
            print(f"Total Jobs: {status.get('total_jobs', 0)}")
            print(f"Daywork123 Jobs: {status.get('daywork123_jobs', 0)}")
            
            config = status.get('config', {})
            print(f"Total Daily Runs: {config.get('total_daily_runs', 0)}")
            print(f"Max Pages per Run: {config.get('max_pages', 0)}")
            
            if 'error' in status:
                print(f"Error: {status['error']}")
                
    except Exception as e:
        error_msg = {"error": str(e)}
        if args.json:
            print(json.dumps(error_msg, indent=2))
        else:
            print(f"Error getting status: {e}")
        sys.exit(1)


async def cmd_run_now(args):
    """Run the Daywork123 scraper immediately."""
    service = SchedulerService()
    
    try:
        result = await service.run_daywork123_now(period=args.period)
        
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if result.get('success'):
                print("=== Scraping Completed Successfully ===")
                print(f"Period: {result.get('period', 'unknown')}")
                print(f"Jobs Found: {result.get('jobs_found', 0)}")
                print(f"Duration: {result.get('duration_seconds', 0):.2f} seconds")
                print(f"Max Pages: {result.get('max_pages', 0)}")
            else:
                print("=== Scraping Failed ===")
                print(f"Error: {result.get('error', 'Unknown error')}")
                print(f"Period: {result.get('period', 'unknown')}")
                
    except Exception as e:
        error_msg = {"error": str(e)}
        if args.json:
            print(json.dumps(error_msg, indent=2))
        else:
            print(f"Error running scraper: {e}")
        sys.exit(1)


async def cmd_update_schedule(args):
    """Update the complete scraping schedule."""
    service = SchedulerService()
    
    try:
        # Parse the time arguments
        kwargs = {}
        if args.morning_hours:
            kwargs['morning_hours'] = parse_time_list(args.morning_hours)
        if args.morning_minutes:
            kwargs['morning_minutes'] = parse_time_list(args.morning_minutes)
        if args.day_hours:
            kwargs['day_hours'] = parse_time_list(args.day_hours)
        if args.day_minutes:
            kwargs['day_minutes'] = parse_time_list(args.day_minutes)
        if args.evening_hours:
            kwargs['evening_hours'] = parse_time_list(args.evening_hours)
        if args.evening_minutes:
            kwargs['evening_minutes'] = parse_time_list(args.evening_minutes)
        
        result = await service.update_daywork123_schedule(**kwargs)
        
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if result.get('success'):
                print("=== Schedule Updated Successfully ===")
                schedule = result.get('new_schedule', {})
                print(f"Morning: {schedule.get('morning_hours')} at {schedule.get('morning_minutes')}")
                print(f"Day: {schedule.get('day_hours')} at {schedule.get('day_minutes')}")
                print(f"Evening: {schedule.get('evening_hours')} at {schedule.get('evening_minutes')}")
                print(f"Total Daily Runs: {result.get('total_daily_runs', 0)}")
            else:
                print("=== Schedule Update Failed ===")
                print(f"Error: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        error_msg = {"error": str(e)}
        if args.json:
            print(json.dumps(error_msg, indent=2))
        else:
            print(f"Error updating schedule: {e}")
        sys.exit(1)


async def cmd_update_morning(args):
    """Update the morning scraping schedule."""
    service = SchedulerService()
    
    try:
        hours = parse_time_list(args.hours)
        minutes = parse_time_list(args.minutes)
        
        result = await service.update_morning_schedule(hours, minutes)
        
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if result.get('success'):
                print("=== Morning Schedule Updated Successfully ===")
                schedule = result.get('new_schedule', {})
                print(f"Morning Hours: {schedule.get('morning_hours')}")
                print(f"Morning Minutes: {schedule.get('morning_minutes')}")
                print(f"Total Daily Runs: {result.get('total_daily_runs', 0)}")
            else:
                print("=== Morning Schedule Update Failed ===")
                print(f"Error: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        error_msg = {"error": str(e)}
        if args.json:
            print(json.dumps(error_msg, indent=2))
        else:
            print(f"Error updating morning schedule: {e}")
        sys.exit(1)


async def cmd_update_day(args):
    """Update the daytime scraping schedule."""
    service = SchedulerService()
    
    try:
        hours = parse_time_list(args.hours)
        minutes = parse_time_list(args.minutes)
        
        result = await service.update_day_schedule(hours, minutes)
        
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if result.get('success'):
                print("=== Day Schedule Updated Successfully ===")
                schedule = result.get('new_schedule', {})
                print(f"Day Hours: {schedule.get('day_hours')}")
                print(f"Day Minutes: {schedule.get('day_minutes')}")
                print(f"Total Daily Runs: {result.get('total_daily_runs', 0)}")
            else:
                print("=== Day Schedule Update Failed ===")
                print(f"Error: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        error_msg = {"error": str(e)}
        if args.json:
            print(json.dumps(error_msg, indent=2))
        else:
            print(f"Error updating day schedule: {e}")
        sys.exit(1)


async def cmd_update_evening(args):
    """Update the evening scraping schedule."""
    service = SchedulerService()
    
    try:
        hours = parse_time_list(args.hours)
        minutes = parse_time_list(args.minutes)
        
        result = await service.update_evening_schedule(hours, minutes)
        
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if result.get('success'):
                print("=== Evening Schedule Updated Successfully ===")
                schedule = result.get('new_schedule', {})
                print(f"Evening Hours: {schedule.get('evening_hours')}")
                print(f"Evening Minutes: {schedule.get('evening_minutes')}")
                print(f"Total Daily Runs: {result.get('total_daily_runs', 0)}")
            else:
                print("=== Evening Schedule Update Failed ===")
                print(f"Error: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        error_msg = {"error": str(e)}
        if args.json:
            print(json.dumps(error_msg, indent=2))
        else:
            print(f"Error updating evening schedule: {e}")
        sys.exit(1)


async def cmd_list_jobs(args):
    """List all scheduled jobs."""
    service = SchedulerService()
    
    try:
        jobs = service.get_jobs_status()
        
        if args.json:
            print(json.dumps(jobs, indent=2, default=str))
        else:
            print("=== Scheduled Jobs ===")
            if not jobs:
                print("No jobs scheduled")
            else:
                for job in jobs:
                    print(f"ID: {job.get('id')}")
                    print(f"  Name: {job.get('name')}")
                    print(f"  Next Run: {job.get('next_run_time')}")
                    print(f"  Trigger: {job.get('trigger')}")
                    kwargs = job.get('kwargs', {})
                    if kwargs:
                        print(f"  Period: {kwargs.get('period', 'unknown')}")
                    print()
                    
    except Exception as e:
        error_msg = {"error": str(e)}
        if args.json:
            print(json.dumps(error_msg, indent=2))
        else:
            print(f"Error listing jobs: {e}")
        sys.exit(1)


async def cmd_next_runs(args):
    """Show next scheduled runs."""
    service = SchedulerService()
    
    try:
        next_runs = service.get_next_runs(limit=args.limit)
        
        if args.json:
            print(json.dumps(next_runs, indent=2, default=str))
        else:
            print(f"=== Next {args.limit} Scheduled Runs ===")
            if not next_runs:
                print("No upcoming runs scheduled")
            else:
                for run in next_runs:
                    print(f"{run.get('next_run_time')} - {run.get('job_name')} ({run.get('period')})")
                    
    except Exception as e:
        error_msg = {"error": str(e)}
        if args.json:
            print(json.dumps(error_msg, indent=2))
        else:
            print(f"Error getting next runs: {e}")
        sys.exit(1)


def create_parser():
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Scheduler CLI for Daywork123 scraper automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check scheduler status
  python -m app.cli status

  # Run scraper immediately
  python -m app.cli run-now

  # Update complete schedule
  python -m app.cli update-schedule --morning-hours "6,7,8,9" --morning-minutes "0,30"

  # Update only morning schedule
  python -m app.cli update-morning --hours "6,7,8,9,10" --minutes "0,30"

  # List all jobs
  python -m app.cli list-jobs

  # Show next 5 runs
  python -m app.cli next-runs --limit 5

Time formats:
  Hours: 0-23 (comma-separated, e.g., "6,7,8,9")
  Minutes: 0-59 (comma-separated, e.g., "0,30")
        """
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check scheduler status')
    status_parser.set_defaults(func=cmd_status)
    
    # Run now command
    run_parser = subparsers.add_parser('run-now', help='Run scraper immediately')
    run_parser.add_argument(
        '--period',
        default='manual',
        help='Period identifier for logging (default: manual)'
    )
    run_parser.set_defaults(func=cmd_run_now)
    
    # Update complete schedule command
    update_parser = subparsers.add_parser('update-schedule', help='Update complete scraping schedule')
    update_parser.add_argument('--morning-hours', help='Morning hours (e.g., "6,7,8,9")')
    update_parser.add_argument('--morning-minutes', help='Morning minutes (e.g., "0,30")')
    update_parser.add_argument('--day-hours', help='Day hours (e.g., "12,15")')
    update_parser.add_argument('--day-minutes', help='Day minutes (e.g., "0")')
    update_parser.add_argument('--evening-hours', help='Evening hours (e.g., "18,19,20,21")')
    update_parser.add_argument('--evening-minutes', help='Evening minutes (e.g., "0,30")')
    update_parser.set_defaults(func=cmd_update_schedule)
    
    # Update morning schedule command
    morning_parser = subparsers.add_parser('update-morning', help='Update morning scraping schedule')
    morning_parser.add_argument('--hours', required=True, help='Morning hours (e.g., "6,7,8,9")')
    morning_parser.add_argument('--minutes', required=True, help='Morning minutes (e.g., "0,30")')
    morning_parser.set_defaults(func=cmd_update_morning)
    
    # Update day schedule command
    day_parser = subparsers.add_parser('update-day', help='Update daytime scraping schedule')
    day_parser.add_argument('--hours', required=True, help='Day hours (e.g., "12,15")')
    day_parser.add_argument('--minutes', required=True, help='Day minutes (e.g., "0")')
    day_parser.set_defaults(func=cmd_update_day)
    
    # Update evening schedule command
    evening_parser = subparsers.add_parser('update-evening', help='Update evening scraping schedule')
    evening_parser.add_argument('--hours', required=True, help='Evening hours (e.g., "18,19,20,21")')
    evening_parser.add_argument('--minutes', required=True, help='Evening minutes (e.g., "0,30")')
    evening_parser.set_defaults(func=cmd_update_evening)
    
    # List jobs command
    jobs_parser = subparsers.add_parser('list-jobs', help='List all scheduled jobs')
    jobs_parser.set_defaults(func=cmd_list_jobs)
    
    # Next runs command
    next_parser = subparsers.add_parser('next-runs', help='Show next scheduled runs')
    next_parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Number of next runs to show (default: 10)'
    )
    next_parser.set_defaults(func=cmd_next_runs)
    
    return parser


async def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        await args.func(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        error_msg = {"error": str(e)}
        if args.json:
            print(json.dumps(error_msg, indent=2))
        else:
            print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
