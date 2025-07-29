# 🚀 How to Run the Daywork123.com Scraper

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
# In your project directory
pip install -r requirements.txt
playwright install chromium
```

### 2. Test the Installation
```bash
# Run the test script to verify everything works
python test_daywork123_scraper.py
```

### 3. Run Individual Scrapers
```bash
# Scrape Daywork123.com (1 page)
python -c "from app.services.scraping_service import scrape_daywork123; import asyncio; print(asyncio.run(scrape_daywork123(max_pages=1)))"

# Scrape Yotspot.com (1 page)  
python -c "from app.services.scraping_service import scrape_yotspot; import asyncio; print(asyncio.run(scrape_yotspot(max_pages=1)))"

# Scrape all sources
python -c "from app.services.scraping_service import scrape_all_sources; import asyncio; print(asyncio.run(scrape_all_sources(max_pages=1)))"
```

## Detailed Usage Guide

### Method 1: Using the Test Script (Recommended for Testing)
```bash
# This runs comprehensive tests for all scrapers
python test_daywork123_scraper.py
```

### Method 2: Using the Scraping Service (Production)
```python
# Create a simple run script: run_scraper.py
import asyncio
from app.services.scraping_service import ScrapingService

async def main():
    service = ScrapingService()
    
    # Option A: Scrape Daywork123 only
    result = await service.scrape_source("daywork123", max_pages=3)
    print(f"Daywork123: Found {result['jobs_found']} jobs, {result['new_jobs']} new")
    
    # Option B: Scrape all sources
    results = await service.scrape_all_sources(max_pages=2)
    for result in results:
        print(f"{result['source']}: {result['jobs_found']} jobs found")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
python run_scraper.py
```

### Method 3: Interactive Python
```bash
# Start Python interactive mode
python

# Then run these commands:
from app.services.scraping_service import ScrapingService
import asyncio

service = ScrapingService()
result = asyncio.run(service.scrape_source("daywork123", max_pages=2))
print(result)
```

## Common Usage Patterns

### Check What's Available
```bash
# List all registered scrapers
python -c "from app.scrapers.registry import ScraperRegistry; print('Available scrapers:', ScraperRegistry.list_scrapers())"

# Check health of all sources
python -c "from app.services.scraping_service import ScrapingService; import asyncio; service = ScrapingService(); print(asyncio.run(service.health_check_all()))"
```

### Run with Custom Settings
```bash
# Create custom_run.py
import asyncio
from app.services.scraping_service import ScrapingService

async def custom_scrape():
    service = ScrapingService()
    
    # Scrape with filters
    filters = {"location": "Caribbean", "job_type": "deckhand"}
    
    # Scrape 5 pages from Daywork123
    result = await service.scrape_source("daywork123", max_pages=5)
    
    print(f"Scraped {result['jobs_found']} jobs from {result['source']}")
    print(f"New jobs: {result['new_jobs']}, Updated: {result['updated_jobs']}")
    print(f"Duration: {result['duration']} seconds")

if __name__ == "__main__":
    asyncio.run(custom_scrape())
```

## Troubleshooting Commands

### If Playwright Fails
```bash
# Install Playwright browsers
playwright install chromium

# On Linux, install dependencies
sudo playwright install-deps chromium
```

### If Dependencies Missing
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Install specific missing packages
pip install playwright aiohttp beautifulsoup4
```

### Test Database Connection
```bash
python -c "from app.database import SessionLocal; db = SessionLocal(); print('Database connected successfully')"
```

## Quick Debug Mode

### Check if Scrapers Are Registered
```bash
python -c "
from app.scrapers.registry import ScraperRegistry
scrapers = ScraperRegistry.list_scrapers()
print('Registered scrapers:', scrapers)
for name in scrapers:
    scraper = ScraperRegistry.get_scraper(name)
    print(f'{name}: {scraper.base_url}')
"
```

### Test Individual Components
```bash
# Test Daywork123 scraper directly
python -c "
from app.scrapers.daywork123 import Daywork123Scraper
import asyncio

async def test():
    scraper = Daywork123Scraper()
    is_working = await scraper.test_connection()
    print(f'Daywork123 accessible: {is_working}')

asyncio.run(test())
"
```

## Production Integration

### Add to Your Scheduler
```python
# In your scheduler.py or wherever you run scheduled tasks
from app.services.scraping_service import scrape_all_sources
import asyncio

async def scheduled_job():
    """Run this every 45 minutes"""
    results = await scrape_all_sources(max_pages=3)
    for result in results:
        print(f"{result['source']}: {result['jobs_found']} jobs")

# Run manually
asyncio.run(scheduled_job())
```

### API Endpoint Example
```python
# In your FastAPI routes
from fastapi import APIRouter
from app.services.scraping_service import ScrapingService

router = APIRouter()

@router.post("/api/scrape/daywork123")
async def trigger_daywork123_scraping(pages: int = 3):
    service = ScrapingService()
    return await service.scrape_source("daywork123", max_pages=pages)
```

## One-Line Commands Summary

```bash
# Install everything
pip install -r requirements.txt && playwright install chromium

# Test all scrapers
python test_daywork123_scraper.py

# Quick Daywork123 scrape
python -c "from app.services.scraping_service import scrape_daywork123; import asyncio; print(asyncio.run(scrape_daywork123(max_pages=1)))"

# Check system health
python -c "from app.services.scraping_service import ScrapingService; import asyncio; service = ScrapingService(); print(asyncio.run(service.health_check_all()))"