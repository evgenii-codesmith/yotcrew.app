# Daywork123 Scheduler Documentation

## Overview

The Daywork123 scheduler is an advanced scheduling system that automates the scraping of job postings from Daywork123 using time-based intervals. It runs more frequently during morning and evening hours when job posting activity is typically higher.

## Features

- **Time-based scheduling**: Different frequencies for morning, day, and evening periods
- **Configurable intervals**: Easy customization through environment variables
- **Persistent job storage**: Uses SQLAlchemy for job persistence across restarts
- **Async execution**: Non-blocking scheduler operation
- **CLI management**: Command-line interface for manual control
- **Comprehensive logging**: Detailed logging for monitoring and debugging
- **Job status tracking**: Database records for all scraping activities

## Default Schedule

With default configuration, the scraper runs **18 times per day**:

### Morning (High Activity): 8 runs
- **Hours**: 6 AM, 7 AM, 8 AM, 9 AM
- **Minutes**: :00, :30
- **Frequency**: Every 30 minutes during morning hours

### Day (Lower Activity): 2 runs  
- **Hours**: 12 PM, 3 PM
- **Minutes**: :00
- **Frequency**: Less frequent during business hours

### Evening (High Activity): 8 runs
- **Hours**: 6 PM, 7 PM, 8 PM, 9 PM  
- **Minutes**: :00, :30
- **Frequency**: Every 30 minutes during evening hours

## Quick Start

### 1. Configuration

Copy the example environment file and customize:
```bash
cp scheduler.env.example .env
```

Key settings:
```env
# Database
SCHEDULER_DB_URL=sqlite:///./yacht_jobs.db

# Scraping
DAYWORK123_MAX_PAGES=5

# Morning schedule (6-9 AM, every 30 min)
DAYWORK123_MORNING_HOURS=6,7,8,9
DAYWORK123_MORNING_MINUTES=0,30

# Day schedule (12 PM, 3 PM)
DAYWORK123_DAY_HOURS=12,15
DAYWORK123_DAY_MINUTES=0

# Evening schedule (6-9 PM, every 30 min)
DAYWORK123_EVENING_HOURS=18,19,20,21
DAYWORK123_EVENING_MINUTES=0,30
```

### 2. Test the Implementation

```bash
python test_scheduler.py
```

### 3. CLI Usage

Check scheduler status:
```bash
python -m app.cli status
```

Run scraper immediately:
```bash
python -m app.cli run-now
```

Update morning schedule:
```bash
python -m app.cli update-morning --hours "7,8,9,10" --minutes "0,15,30,45"
```

List scheduled jobs:
```bash
python -m app.cli list-jobs
```

Show next runs:
```bash
python -m app.cli next-runs --limit 10
```

## Architecture

### Core Components

1. **`app/config.py`**: Configuration management with environment variable support
2. **`app/daywork_scheduler.py`**: Core scheduler implementation with APScheduler
3. **`app/services/scheduler_service.py`**: High-level service interface
4. **`app/cli.py`**: Command-line interface for management

### Key Classes

- **`SchedulerConfig`**: Manages all configuration parameters
- **`ScrapingScheduler`**: Core scheduler with job management
- **`SchedulerService`**: Service layer for common operations

## Integration

### Adding to Your Application

To integrate the scheduler with your application lifecycle:

```python
import asyncio
from app.services.scheduler_service import SchedulerService

# Global scheduler instance
scheduler_service = None

async def startup():
    """Application startup"""
    global scheduler_service
    scheduler_service = SchedulerService()
    await scheduler_service.start()
    print("Scheduler started")

async def shutdown():
    """Application shutdown"""
    global scheduler_service
    if scheduler_service:
        await scheduler_service.stop()
    print("Scheduler stopped")

# For FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    await startup()
    yield
    await shutdown()

app = FastAPI(lifespan=lifespan)
```

### Manual Operations

```python
from app.services.scheduler_service import SchedulerService

# Create service
service = SchedulerService()

# Get status
status = service.get_scheduler_status()

# Run immediately
result = await service.run_daywork123_now()

# Update schedule
result = await service.update_morning_schedule([7,8,9], [0,30])
```

## Configuration Options

### Schedule Customization

**High Frequency (24 runs/day)**:
```env
DAYWORK123_MORNING_HOURS=6,7,8,9
DAYWORK123_MORNING_MINUTES=0,30
DAYWORK123_DAY_HOURS=10,12,14,16
DAYWORK123_DAY_MINUTES=0,30
DAYWORK123_EVENING_HOURS=18,19,20,21
DAYWORK123_EVENING_MINUTES=0,30
```

**Medium Frequency (12 runs/day)**:
```env
DAYWORK123_MORNING_HOURS=7,8,9
DAYWORK123_MORNING_MINUTES=0
DAYWORK123_DAY_HOURS=12,15
DAYWORK123_DAY_MINUTES=0
DAYWORK123_EVENING_HOURS=18,19,20,21
DAYWORK123_EVENING_MINUTES=0
```

**Low Frequency (6 runs/day)**:
```env
DAYWORK123_MORNING_HOURS=8
DAYWORK123_MORNING_MINUTES=0
DAYWORK123_DAY_HOURS=12,15
DAYWORK123_DAY_MINUTES=0
DAYWORK123_EVENING_HOURS=19,21
DAYWORK123_EVENING_MINUTES=0
```

### Advanced Options

```env
# Job behavior
SCHEDULER_COALESCE=true              # Skip overlapping jobs
SCHEDULER_MAX_INSTANCES=1            # Max concurrent instances
SCHEDULER_MISFIRE_GRACE_TIME=300     # 5 minute grace period

# Performance
DAYWORK123_MAX_PAGES=5               # Pages per scraping run

# Logging
LOG_LEVEL=INFO                       # DEBUG, INFO, WARNING, ERROR
```

## Monitoring

### Database Tables

The scheduler creates these database tables:
- `apscheduler_jobs`: Scheduled job definitions
- `scraping_jobs`: Execution history and results

### Log Messages

Key log patterns to monitor:
```
INFO - Scheduler started successfully
INFO - Scheduled 18 Daywork123 scraping jobs per day  
INFO - Starting Daywork123 scraping - morning (07:00)
INFO - Daywork123 scraping completed - morning (07:00) - Found 15 jobs in 12.34s
ERROR - Error in Daywork123 scraping - morning (07:00): Connection timeout
```

### Status Monitoring

```python
service = SchedulerService()
status = service.get_scheduler_status()

print(f"Running: {status['running']}")
print(f"Total jobs: {status['total_jobs']}")
print(f"Daily runs: {status['config']['total_daily_runs']}")
```

## Troubleshooting

### Common Issues

**Scheduler not starting**:
- Check database connectivity
- Verify configuration validity
- Check file permissions

**Jobs not running**:
- Verify scheduler is running: `python -m app.cli status`
- Check next run times: `python -m app.cli next-runs`
- Review logs for errors

**High memory usage**:
- Reduce `DAYWORK123_MAX_PAGES`
- Check for database growth
- Monitor log file sizes

**Performance issues**:
- Reduce scraping frequency
- Optimize database queries
- Check network connectivity

### Debug Mode

Enable debug logging:
```env
LOG_LEVEL=DEBUG
```

This provides detailed information about:
- Job scheduling and execution
- Database operations
- Scraper activity
- Configuration loading

## Best Practices

### Production Deployment

1. **Use external database**: PostgreSQL or MySQL instead of SQLite
2. **Monitor resources**: Set up alerts for CPU, memory, disk usage
3. **Log rotation**: Configure log rotation to prevent disk issues
4. **Backup strategy**: Regular backups of job data and configuration
5. **Health checks**: Implement health check endpoints

### Security

1. **Environment variables**: Never commit sensitive data to git
2. **Database access**: Use restricted database users
3. **Network security**: Limit outbound connections if possible
4. **Log sanitization**: Avoid logging sensitive information

### Performance

1. **Reasonable frequency**: Don't over-scrape target sites
2. **Error handling**: Graceful degradation on failures
3. **Resource limits**: Set appropriate memory and CPU limits
4. **Database maintenance**: Regular cleanup of old job records

## Support

For issues or questions:
1. Check logs for error messages
2. Run `python test_scheduler.py` to verify setup
3. Use `python -m app.cli status` to check current state
4. Review configuration against examples in `scheduler.env.example`

## Future Enhancements

Potential improvements:
- Web dashboard for schedule management
- Email/webhook notifications for failures
- Metrics collection and monitoring
- Multi-scraper support
- Dynamic schedule adjustment based on results
- Rate limiting and respect for robots.txt
