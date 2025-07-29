# 🛥️ Daywork123.com Scraper Setup Guide

This guide provides step-by-step instructions for setting up the Daywork123.com scraper in your yacht jobs platform.

## 📋 Prerequisites

- Python 3.11+ (recommended)
- Conda environment (recommended) or virtualenv
- Git

## 🚀 Quick Setup

### 1. Environment Setup

```bash
# Activate your conda environment
conda activate yachtjobs

# Install new dependencies
pip install -r requirements.txt

# Install Playwright browsers (for Daywork123.com)
playwright install chromium
```

### 2. Database Migration

The new scrapers use the existing database schema. No migration needed.

### 3. Test the Installation

```bash
# Test the scraper installation
python test_daywork123_scraper.py

# Test individual scrapers
python -c "from app.services.scraping_service import scrape_daywork123; import asyncio; print(asyncio.run(scrape_daywork123(max_pages=1)))"
```

## 🔧 Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Scraping Configuration
SCRAPER_INTERVAL_MINUTES=45
MAX_SCRAPING_PAGES=5
MIN_REQUEST_DELAY=2.0
MAX_REQUEST_DELAY=5.0

# Anti-detection settings
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=30000
```

### Custom Filters

You can configure custom filters for each scraper:

```python
# Example: Filter by location and job type
filters = {
    "location": "Caribbean",
    "job_type": "daywork",
    "vessel_size": "50-100m"
}
```

## 📊 Usage Examples

### Basic Usage

```python
import asyncio
from app.services.scraping_service import ScrapingService

async def main():
    service = ScrapingService()
    
    # Scrape Daywork123.com
    result = await service.scrape_source("daywork123", max_pages=3)
    print(f"Found {result['jobs_found']} jobs")
    
    # Scrape all sources
    results = await service.scrape_all_sources(max_pages=2)
    for result in results:
        print(f"{result['source']}: {result['jobs_found']} jobs")

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Usage

```python
from app.scrapers.registry import ScraperRegistry

# Get specific scraper
scraper = ScraperRegistry.get_scraper("daywork123")

# Test connection
is_working = await scraper.test_connection()

# Get supported filters
filters = scraper.get_supported_filters()
```

## 🔍 Monitoring and Debugging

### Health Checks

```bash
# Check all scrapers
python -c "from app.services.scraping_service import ScrapingService; import asyncio; service = ScrapingService(); print(asyncio.run(service.health_check_all()))"
```

### Log Files

Logs are written to the console by default. Configure logging in your application:

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
```

## 🧪 Testing

### Run All Tests

```bash
python test_daywork123_scraper.py
```

### Test Individual Components

```bash
# Test scraper registry
python -c "from app.scrapers.registry import ScraperRegistry; print(ScraperRegistry.list_scrapers())"

# Test database integration
python -c "from app.services.scraping_service import ScrapingService; import asyncio; service = ScrapingService(); print(service.get_scraper_stats())"
```

## 🚨 Troubleshooting

### Common Issues

#### Playwright Not Found
```bash
pip install playwright
playwright install chromium
```

#### Permission Errors
```bash
# On Linux/macOS
sudo playwright install-deps chromium

# On Windows (run as Administrator)
playwright install chromium
```

#### Connection Timeouts
- Check internet connection
- Verify target websites are accessible
- Increase timeout values in configuration

#### Database Issues
- Ensure database file exists: `yacht_jobs.db`
- Check database permissions
- Verify SQLAlchemy models are up to date

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('app.scrapers').setLevel(logging.DEBUG)
```

## 🔄 Integration with Existing System

### Update Scheduler

Modify your scheduler to use the new scraping service:

```python
from app.services.scraping_service import scrape_all_sources

# In your scheduler
async def scheduled_scraping():
    results = await scrape_all_sources(max_pages=3)
    # Process results...
```

### API Endpoints

Update your FastAPI endpoints:

```python
from fastapi import APIRouter
from app.services.scraping_service import ScrapingService

router = APIRouter()

@router.post("/api/scrape/daywork123")
async def scrape_daywork123_endpoint(max_pages: int = 3):
    service = ScrapingService()
    return await service.scrape_source("daywork123", max_pages)
```

## 📈 Performance Optimization

### Rate Limiting

The scrapers include built-in rate limiting:
- Daywork123: 2.5s delay between pages
- Yotspot: 2.0s delay between pages
- 30s delay between different sources

### Concurrent Scraping

For production use, consider:

```python
import asyncio
from app.services.scraping_service import ScrapingService

async def concurrent_scraping():
    service = ScrapingService()
    
    # Run scrapers concurrently
    tasks = [
        service.scrape_source("daywork123", max_pages=2),
        service.scrape_source("yotspot", max_pages=2)
    ]
    
    results = await asyncio.gather(*tasks)
    return results
```

## 🔒 Security Considerations

### Anti-Detection Measures

The Daywork123 scraper includes:
- Randomized user agents
- Realistic browser fingerprints
- Human-like delays
- Stealth mode scripts

### Rate Limiting

Respectful scraping with:
- Configurable delays
- Page limits
- Connection pooling
- Error handling

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs for specific error messages
3. Test with the provided test script
4. Check website accessibility manually

## 🎯 Next Steps

1. Run the test script to verify installation
2. Configure your environment variables
3. Test individual scrapers
4. Integrate with your scheduler
5. Monitor logs for any issues
6. Scale up gradually

## 📝 Changelog

- **v1.0.0**: Initial Daywork123.com scraper implementation
- **v1.1.0**: Added pluggable architecture with Yotspot support
- **v1.2.0**: Enhanced anti-detection measures
- **v1.3.0**: Added comprehensive testing suite