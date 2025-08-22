# Daywork123 Database Integration

This document describes the implementation of database saving functionality for the Daywork123 scraper in the YotCrew.app project.

## Overview

The Daywork123 scraper now includes comprehensive database saving functionality that allows scraped job data to be automatically saved to the `yacht_jobs.db` SQLite database. The implementation follows the existing pluggable scraper architecture and integrates seamlessly with the existing codebase.

## Architecture

### Components

1. **Enhanced Database Models** (`app/models.py`)
   - Updated `Job` model with new fields to match `UniversalJob`
   - Added support for JSON fields for requirements and benefits
   - Improved compatibility between database and scraping models

2. **Updated ScrapingService** (`app/services/scraping_service.py`)
   - Enhanced to handle new UniversalJob fields
   - Improved database saving logic with better error handling
   - Support for enum values from UniversalJob

3. **Enhanced Daywork123Scraper** (`app/scrapers/daywork123.py`)
   - Added `save_jobs_to_db()` method for direct database saving
   - Added `scrape_and_save_jobs()` method for complete workflow
   - Improved job data extraction and UniversalJob creation
   - Better error handling and logging

4. **Updated FastAPI Integration** (`main.py`)
   - Enhanced `/api/scrape` endpoint to support specific scrapers
   - Updated background task to use new scraping methods

## Key Features

### 1. Automatic Database Saving

```python
# Example: Scrape and save jobs automatically
scraper = Daywork123Scraper()
result = await scraper.scrape_and_save_jobs(max_pages=3)
print(f"Found {result['jobs_found']} jobs, saved {result['jobs_saved']}")
```

### 2. Duplicate Handling

The system automatically handles duplicate jobs by:
- Checking for existing jobs by `external_id` and `source`
- Updating existing jobs with new information
- Creating new records only for genuinely new jobs

### 3. Data Quality Scoring

Each job is assigned a quality score (0.0-1.0) based on:
- Completeness of required fields (60%)
- URL validity (20%)
- Description length (20%)

### 4. Comprehensive Error Handling

- Database connection errors are handled gracefully
- Individual job saving errors don't stop the entire process
- Detailed logging for debugging and monitoring

## Database Schema

The enhanced `Job` model includes these key fields:

```sql
-- Core job information
external_id VARCHAR(255) UNIQUE  -- Source-specific job ID
title VARCHAR(255) NOT NULL
company VARCHAR(255)
description TEXT

-- Location
location VARCHAR(255)
country VARCHAR(255)
region VARCHAR(255)

-- Vessel information
vessel_type VARCHAR(255)
vessel_size VARCHAR(255)
vessel_name VARCHAR(255)

-- Employment details
employment_type VARCHAR(255)
job_type VARCHAR(255)  -- For backward compatibility
department VARCHAR(255)
position_level VARCHAR(255)

-- Compensation
salary_range VARCHAR(255)
salary_currency VARCHAR(255)
salary_period VARCHAR(255)

-- Timing
start_date VARCHAR(255)
posted_date DATETIME
posted_at DATETIME  -- For backward compatibility

-- Content
requirements JSON  -- Array of requirement strings
benefits JSON      -- Array of benefit strings

-- Metadata
source VARCHAR(255)
source_url VARCHAR(255)
quality_score FLOAT
raw_data JSON      -- Original scraped data
scraped_at DATETIME
created_at DATETIME
updated_at DATETIME
```

## Usage Examples

### Basic Usage

```python
import asyncio
from app.scrapers.daywork123 import Daywork123Scraper

async def scrape_jobs():
    scraper = Daywork123Scraper()
    
    # Test connection
    if await scraper.test_connection():
        # Scrape and save
        result = await scraper.scrape_and_save_jobs(max_pages=2)
        print(f"Success: {result['success']}")
        print(f"Jobs found: {result['jobs_found']}")
        print(f"Jobs saved: {result['jobs_saved']}")

asyncio.run(scrape_jobs())
```

### Manual Control

```python
async def manual_scraping():
    scraper = Daywork123Scraper()
    
    # Collect jobs manually
    jobs = []
    async for job in scraper.scrape_jobs(max_pages=1):
        jobs.append(job)
        print(f"Found: {job.title}")
    
    # Save to database
    saved_count = await scraper.save_jobs_to_db(jobs)
    print(f"Saved {saved_count} jobs")
```

### Using ScrapingService

```python
from app.services.scraping_service import ScrapingService

async def use_service():
    service = ScrapingService()
    
    # Scrape specific source
    result = await service.scrape_source("daywork123", max_pages=3)
    
    # Or scrape all sources
    results = await service.scrape_all_sources(max_pages=2)
```

### FastAPI Integration

```bash
# Trigger scraping via API
curl -X POST "http://localhost:8000/api/scrape?source=daywork123&max_pages=2"

# Check scraping status
curl "http://localhost:8000/api/scrape/status"
```

## Testing

### Unit Tests

Run the comprehensive test suite:

```bash
python test_daywork123_db.py
```

The test suite includes:
- Basic job saving functionality
- Duplicate handling verification
- Database content verification
- Real scraping tests (optional)
- Error handling tests

### Example Usage

Run the example script to see all functionality:

```bash
python example_usage.py
```

## Database Migration

If upgrading from an older version, you may need to add new columns:

```sql
-- Add new columns to existing jobs table
ALTER TABLE jobs ADD COLUMN vessel_name VARCHAR(255);
ALTER TABLE jobs ADD COLUMN employment_type VARCHAR(255);
ALTER TABLE jobs ADD COLUMN position_level VARCHAR(255);
ALTER TABLE jobs ADD COLUMN salary_currency VARCHAR(255);
ALTER TABLE jobs ADD COLUMN salary_period VARCHAR(255);
ALTER TABLE jobs ADD COLUMN posted_date DATETIME;
ALTER TABLE jobs ADD COLUMN requirements JSON;
ALTER TABLE jobs ADD COLUMN benefits JSON;
ALTER TABLE jobs ADD COLUMN country VARCHAR(255);
ALTER TABLE jobs ADD COLUMN region VARCHAR(255);
ALTER TABLE jobs ADD COLUMN quality_score FLOAT DEFAULT 0.0;
ALTER TABLE jobs ADD COLUMN raw_data JSON;
ALTER TABLE jobs ADD COLUMN scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP;
```

## Configuration

### Environment Variables

```bash
# Database URL (optional, defaults to SQLite)
DATABASE_URL=sqlite:///./yacht_jobs.db

# For PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost/yachtjobs
```

### Scraper Configuration

The Daywork123Scraper includes these configuration options:

```python
config = {
    'max_retries': 3,
    'request_delay': 2.5,
    'user_agents': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
        # ... more user agents
    ]
}
```

## Monitoring and Logging

### Logging Levels

- **INFO**: Successful operations and progress updates
- **DEBUG**: Detailed scraping and saving information
- **WARNING**: Non-fatal issues (e.g., connection problems)
- **ERROR**: Fatal errors that prevent operation

### Example Log Output

```
2024-01-15 10:30:00 - daywork123 - INFO - Starting Daywork123 scraper for 2 pages
2024-01-15 10:30:05 - daywork123 - INFO - Page 1: Found 15 jobs
2024-01-15 10:30:10 - daywork123 - INFO - Page 2: Found 12 jobs
2024-01-15 10:30:12 - daywork123 - INFO - Successfully saved 27 jobs to database
2024-01-15 10:30:12 - daywork123 - INFO - Daywork123 scraping completed: 27 found, 25 saved
```

## Performance Considerations

### Database Performance

- Uses SQLite by default for simplicity
- Can be configured to use PostgreSQL for production
- Includes proper indexes on `external_id` and `source` fields
- JSON fields are supported natively by modern databases

### Scraping Performance

- Respects rate limits with configurable delays
- Uses Playwright for reliable web scraping
- Includes retry logic for failed requests
- Efficient memory usage with async generators

### Scalability

- Designed to handle thousands of jobs
- Database operations are batched for efficiency
- Background task support for API integration
- Proper error isolation prevents cascading failures

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```
   Solution: Check DATABASE_URL and ensure database is accessible
   ```

2. **Playwright Not Available**
   ```
   Solution: Install Playwright: pip install playwright && playwright install
   ```

3. **Jobs Not Saving**
   ```
   Solution: Check logs for specific errors, verify database schema
   ```

4. **Duplicate Jobs**
   ```
   This is expected behavior - duplicates are updated, not re-created
   ```

### Debug Mode

Enable debug logging for detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

### Planned Features

1. **Enhanced Data Extraction**
   - Extract more detailed job requirements
   - Better salary parsing
   - Company logo extraction

2. **Advanced Filtering**
   - Location-based filtering
   - Salary range filtering
   - Job type filtering

3. **Data Quality Improvements**
   - Machine learning-based job categorization
   - Automated duplicate detection
   - Content quality scoring

4. **Performance Optimizations**
   - Parallel page processing
   - Incremental updates
   - Smart scheduling

## Contributing

When contributing to the database saving functionality:

1. **Follow the existing patterns** in the codebase
2. **Add comprehensive tests** for new features
3. **Update documentation** as needed
4. **Handle errors gracefully** with proper logging
5. **Maintain backward compatibility** where possible

## Support

For issues related to database saving functionality:

1. Check the logs for specific error messages
2. Run the test suite to verify functionality
3. Review this documentation for configuration options
4. Check the example scripts for usage patterns

---

**Last Updated**: January 2024  
**Version**: 1.0.0  
**Compatible With**: YotCrew.app v1.0+

