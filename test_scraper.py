#!/usr/bin/env python3
"""
Test script for the Yotspot scraper
"""

import asyncio
import sys
import os

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scraper import YotspotScraper

async def test_scraper():
    """Test the Yotspot scraper"""
    scraper = YotspotScraper()
    
    print("🧪 Testing Yotspot scraper...")
    print("=" * 50)
    
    # Test basic connection
    print("1. Testing website connection...")
    test_result = scraper.test_scraping()
    print(f"   Status: {test_result.get('status', 'unknown')}")
    if test_result.get('title'):
        print(f"   Page title: {test_result['title']}")
    if test_result.get('view_job_links'):
        print(f"   Found {test_result['view_job_links']} 'View Job' links")
    
    if test_result.get('status') == 'error':
        print(f"   Error: {test_result.get('error')}")
        print("\n❌ Connection test failed. Check your internet connection.")
        return
    
    print("   ✅ Connection successful!")
    
    # Test scraping a small number of jobs
    print("\n2. Testing job scraping (1 page only)...")
    try:
        jobs = await scraper.scrape_jobs(max_pages=1)
        
        if jobs:
            print(f"   ✅ Successfully scraped {len(jobs)} jobs!")
            print("\n📋 Sample jobs found:")
            
            for i, job in enumerate(jobs[:3], 1):  # Show first 3 jobs
                print(f"\n   Job {i}:")
                print(f"   Title: {job.get('title', 'N/A')}")
                print(f"   Company: {job.get('company', 'N/A')}")
                print(f"   Location: {job.get('location', 'N/A')}")
                print(f"   Vessel: {job.get('vessel_type', 'N/A')} - {job.get('vessel_size', 'N/A')}")
                print(f"   Salary: {job.get('salary_range', 'N/A')}")
                print(f"   Type: {job.get('job_type', 'N/A')}")
                
                if i == 3 and len(jobs) > 3:
                    print(f"\n   ... and {len(jobs) - 3} more jobs")
        else:
            print("   ⚠️  No jobs found. This might be normal if:")
            print("      - The website structure has changed")
            print("      - There are no current job postings")
            print("      - The selectors need updating")
            
    except Exception as e:
        print(f"   ❌ Scraping failed: {e}")
        return
    
    print("\n" + "=" * 50)
    print("🎉 Scraper test completed!")
    
    if jobs:
        print(f"✅ Found {len(jobs)} jobs successfully")
        print("\n💡 Tips:")
        print("   - Run 'python create_sample_data.py' to add sample data")
        print("   - Start the app with 'uvicorn main:app --reload'")
        print("   - Visit http://localhost:8000 to see the dashboard")
    else:
        print("⚠️  No jobs found, but you can still test with sample data")
        print("   - Run 'python create_sample_data.py' to add sample data")

if __name__ == "__main__":
    asyncio.run(test_scraper()) 