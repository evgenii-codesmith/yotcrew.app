# 🚀 Quick Start Guide - Daywork123 Scraper

## 🔍 System Overview

Your project has a modern, production-ready scraping system with multiple ways to run the Daywork123 scraper:

- **Main scraper**: `app/scrapers/daywork123.py` - Modern, production-ready scraper with Playwright
- **Scheduler**: `app/daywork_scheduler.py` - Advanced scheduling with time-based intervals
- **CLI interface**: `app/cli.py` - Command-line management tools
- **Web API**: `main.py` - HTTP endpoints for manual triggering
- **Service layer**: `app/services/` - Unified scraping and scheduling services

---

## 🚀 Manual Scraping Methods

### 1. **Via Command Line Interface (Recommended)**

```bash
# Run Daywork123 scraper immediately
python -m app.cli run-now

# Run with custom period identifier
python -m app.cli run-now --period "manual_test"

# Check scheduler status
python -m app.cli status

# Get JSON output
python -m app.cli run-now --json
```

### 2. **Via Web API**

```bash
# Start the web application first
python main.py

# Then trigger scraping via API
curl -X POST "http://localhost:8000/api/scrape?source=daywork123&max_pages=3"

# Or scrape all sources
curl -X POST "http://localhost:8000/api/scrape?source=all&max_pages=5"
```

### 3. **Via Web Dashboard**

```bash
# Start the web app
python main.py
# Open browser to http://localhost:8000
# Click the manual scrape button in the dashboard
```

### 4. **Via Python Script (Direct)**

```python
import asyncio
from app.scrapers.daywork123 import Daywork123Scraper

async def run_scraper():
    scraper = Daywork123Scraper()
    result = await scraper.scrape_and_save_jobs(max_pages=5)
    print(f"Found {result['jobs_found']} jobs, saved {result['jobs_saved']}")

asyncio.run(run_scraper())
```

### 5. **Via Scraping Service**

```python
import asyncio
from app.services.scraping_service import scrape_daywork123

async def run():
    result = await scrape_daywork123(max_pages=3)
    print(result)

asyncio.run(run())
```

---

## ⏰ Scheduler-Based Automation

### Current Automatic Schedule

Your scheduler runs **18 times daily** with different frequencies:

- **Morning (6-10 AM)**: Every 30 minutes (6:00, 6:30, 7:00, 7:30, 8:00, 8:30, 9:00, 9:30, 10:00, 10:30)
- **Day (12 PM, 3 PM)**: Twice during midday (12:00, 15:00)  
- **Evening (6-9 PM)**: Every 30 minutes (18:00, 18:30, 19:00, 19:30, 20:00, 20:30, 21:00, 21:30)

### Scheduler Management Commands

```bash
# Check current scheduler status
python -m app.cli status

# List all scheduled jobs
python -m app.cli list-jobs

# Show next 10 upcoming runs
python -m app.cli next-runs --limit 10

# Update complete schedule
python -m app.cli update-schedule \
  --morning-hours "6,7,8,9" \
  --morning-minutes "0,30" \
  --evening-hours "18,19,20,21" \
  --evening-minutes "0,30"

# Update only morning schedule
python -m app.cli update-morning --hours "6,7,8,9,10" --minutes "0,30"

# Update only evening schedule  
python -m app.cli update-evening --hours "17,18,19,20,21" --minutes "0,30"

# Update only day schedule
python -m app.cli update-day --hours "12,15" --minutes "0"
```

### Starting/Stopping the Scheduler

The scheduler automatically starts when you run the main application:

```bash
# Start web app (includes scheduler)
python main.py
```

Or you can manage it programmatically:

```python
from app.services.scheduler_service import SchedulerService

# Start scheduler service
service = SchedulerService()
await service.start()

# Stop scheduler service
await service.stop()

# Run scraper immediately via service
result = await service.run_daywork123_now()
```

---

## 🛠️ Configuration

The scheduler configuration is in `app/config.py`:

```python
# Default settings (current)
MORNING_HOURS = [6, 7, 8, 9, 10]           # Hours 6-10 AM
MORNING_MINUTES = [0, 30]                   # :00 and :30 minutes
DAY_HOURS = [12, 15]                        # 12 PM, 3 PM
DAY_MINUTES = [0]                           # Only :00 minutes
EVENING_HOURS = [18, 19, 20, 21]           # Hours 6-9 PM  
EVENING_MINUTES = [0, 30]                   # :00 and :30 minutes
DAYWORK123_MAX_PAGES = 1                    # Pages to scrape per run
```

---

## 📊 Monitoring & Status

```bash
# Check scraping status
curl http://localhost:8000/api/scrape/status

# View job statistics
curl http://localhost:8000/api/jobs/stats

# Get health check
curl http://localhost:8000/health

# View recent jobs from daywork123
curl "http://localhost:8000/api/jobs?source=daywork123&limit=10"
```

---

## 🚨 Quick Start Commands

```bash
# 1. Quick manual run (most common)
python -m app.cli run-now

# 2. Start the full system with web interface + scheduler
python main.py

# 3. Check if everything is working
python -m app.cli status
python -m app.cli next-runs --limit 5
```

---

## 🔄 How Everything Works

### 🔄 Automated System
- **Daywork123**: Runs 18x daily (morning/evening peaks, slower midday)
- **Yotspot**: Every 45 minutes via background scheduler
- **Storage**: SQLite database with job deduplication

### 🛠️ Manual Control
- **Web Dashboard**: Real-time job browsing with filters
- **API Endpoints**: Trigger scraping, check status
- **CLI Tools**: Direct scraper management

### 📊 Data Flow
1. **Scrapers** → Extract jobs from yacht job sites
2. **Database** → Store with deduplication (external_id check)
3. **Web App** → Display with Alpine.js + HTMX interactivity
4. **Scheduler** → Automatic background updates

### 🎯 Key Files
- `main.py` - Web app & API
- `app/cli.py` - Command line tools
- `app/daywork_scheduler.py` - Automated scheduling
- `app/scrapers/daywork123.py` - Modern Daywork123 scraper
- `app/services/` - Service layer for scraping and scheduling

---

## 📋 Examples & Use Cases

### Quick Test Run
```bash
# Just test the scraper once
python -m app.cli run-now --period "test"
```

### Full Production Setup
```bash
# Start the complete system
python main.py
# Visit http://localhost:8000 for the web interface
```

### Custom Schedule Update
```bash
# Change to scrape every hour during business hours
python -m app.cli update-schedule \
  --morning-hours "9,10,11" \
  --morning-minutes "0" \
  --day-hours "12,13,14,15,16" \
  --day-minutes "0" \
  --evening-hours "17,18" \
  --evening-minutes "0"
```

### View Results
```bash
# See what was scraped
curl "http://localhost:8000/api/jobs?source=daywork123&page=1&limit=5"
```

---

**Note**: The scraper automatically saves jobs to your SQLite database (`yacht_jobs.db`) with deduplication based on external ID, so you won't get duplicates when running multiple times.

**That's it!** Start with `python main.py` for the full system or `python -m app.cli run-now` for a quick test.

# Quick manual run (most common)
python -m app.cli run-now

# Start full web application
python main.py
# Visit http://localhost:8000 to browse the 756 scraped jobs

# Check status
python -m app.cli status