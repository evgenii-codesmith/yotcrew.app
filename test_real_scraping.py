#!/usr/bin/env python3
"""Test real scraping with updated URLs and selectors"""
import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.scrapers.registry import ScraperRegistry
from app.services.scraping_service import ScrapingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_real_scraping():
    """Test real scraping with updated URLs"""
    print("🔍 Testing real scraping with updated URLs...")
    
    service = ScrapingService()
    
    # Test each scraper individually
    for scraper_name in ScraperRegistry.list_scrapers():
        print(f"\n📋 Testing {scraper_name.value} scraper...")
        try:
            # Test with max_pages=1 to avoid overwhelming the sites
            result = await service.scrape_source(scraper_name, max_pages=1)
            print(f"✅ {scraper_name.value}: Found {result['jobs_found']} jobs")
            print(f"   New jobs: {result['new_jobs']}, Updated: {result['updated_jobs']}")
            
            if result['errors']:
                print(f"   Errors: {result['errors']}")
                
        except Exception as e:
            print(f"❌ {scraper_name.value}: Error - {e}")
    
    print("\n🎯 Testing complete!")

if __name__ == "__main__":
    asyncio.run(test_real_scraping()) 