#!/usr/bin/env python3
"""Debug script to inspect website structure and fix scraper selectors"""
import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.scrapers.registry import ScraperRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_daywork123():
    """Debug Daywork123.com structure"""
    print("🔍 Debugging Daywork123.com structure...")
    
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # Show browser for debugging
            context = await browser.new_context()
            page = await context.new_page()
            
            # Navigate to the jobs page
            url = "https://www.daywork123.com/jobs"
            print(f"Navigating to: {url}")
            
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait a bit for content to load
            await asyncio.sleep(5)
            
            # Take a screenshot for debugging
            await page.screenshot(path="daywork123_debug.png")
            print("📸 Screenshot saved as: daywork123_debug.png")
            
            # Try to find job listings with different selectors
            selectors_to_try = [
                '.job-listing',
                '.job-card',
                '.job-item',
                'article',
                '[class*="job"]',
                '[class*="listing"]',
                '.card',
                '.item'
            ]
            
            for selector in selectors_to_try:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"✅ Found {len(elements)} elements with selector: {selector}")
                        
                        # Get some sample content
                        if len(elements) > 0:
                            sample_text = await elements[0].text_content()
                            print(f"   Sample content: {sample_text[:200]}...")
                    else:
                        print(f"❌ No elements found with selector: {selector}")
                except Exception as e:
                    print(f"❌ Error with selector {selector}: {e}")
            
            # Get page title and URL
            title = await page.title()
            current_url = page.url
            print(f"\n📄 Page title: {title}")
            print(f"🌐 Current URL: {current_url}")
            
            # Get page HTML for manual inspection
            html = await page.content()
            with open("daywork123_debug.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("📄 HTML saved as: daywork123_debug.html")
            
            await browser.close()
            
    except Exception as e:
        print(f"❌ Error debugging Daywork123: {e}")

async def debug_yotspot():
    """Debug Yotspot.com structure"""
    print("\n🔍 Debugging Yotspot.com structure...")
    
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            url = "https://www.yotspot.com/jobs"
            print(f"Fetching: {url}")
            
            async with session.get(url) as response:
                print(f"Status: {response.status}")
                print(f"Headers: {dict(response.headers)}")
                
                if response.status == 200:
                    html = await response.text()
                    
                    # Save HTML for inspection
                    with open("yotspot_debug.html", "w", encoding="utf-8") as f:
                        f.write(html)
                    print("📄 HTML saved as: yotspot_debug.html")
                    
                    # Try to parse with BeautifulSoup
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for job-related elements
                    job_selectors = [
                        '[class*="job"]',
                        '[class*="listing"]',
                        'article',
                        '.card',
                        '.item'
                    ]
                    
                    for selector in job_selectors:
                        elements = soup.select(selector)
                        if elements:
                            print(f"✅ Found {len(elements)} elements with selector: {selector}")
                            if len(elements) > 0:
                                sample_text = elements[0].get_text(strip=True)[:200]
                                print(f"   Sample content: {sample_text}...")
                        else:
                            print(f"❌ No elements found with selector: {selector}")
                    
                    # Get page title
                    title = soup.title.string if soup.title else "No title"
                    print(f"\n📄 Page title: {title}")
                    
                else:
                    print(f"❌ Failed to fetch page: {response.status}")
                    
    except Exception as e:
        print(f"❌ Error debugging Yotspot: {e}")

async def test_alternative_urls():
    """Test alternative URLs for the job sites"""
    print("\n🔍 Testing alternative URLs...")
    
    # Test different possible job URLs
    daywork123_urls = [
        "https://www.daywork123.com/jobs",
        "https://www.daywork123.com/job-listings",
        "https://www.daywork123.com/careers",
        "https://www.daywork123.com/positions",
        "https://www.daywork123.com"
    ]
    
    yotspot_urls = [
        "https://www.yotspot.com/jobs",
        "https://www.yotspot.com/job-listings",
        "https://www.yotspot.com/careers",
        "https://www.yotspot.com/positions",
        "https://www.yotspot.com"
    ]
    
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            print("Testing Daywork123 URLs:")
            for url in daywork123_urls:
                try:
                    async with session.get(url, timeout=10) as response:
                        print(f"  {url}: {response.status}")
                except Exception as e:
                    print(f"  {url}: Error - {e}")
            
            print("\nTesting Yotspot URLs:")
            for url in yotspot_urls:
                try:
                    async with session.get(url, timeout=10) as response:
                        print(f"  {url}: {response.status}")
                except Exception as e:
                    print(f"  {url}: Error - {e}")
                    
    except Exception as e:
        print(f"❌ Error testing URLs: {e}")

async def main():
    """Main debug function"""
    print("🐛 Yacht Jobs Scraper Debug Tool")
    print("=" * 50)
    
    try:
        # Test alternative URLs first
        await test_alternative_urls()
        
        # Debug individual sites
        await debug_daywork123()
        await debug_yotspot()
        
        print("\n✅ Debug complete! Check the generated files:")
        print("  - daywork123_debug.png (screenshot)")
        print("  - daywork123_debug.html (page source)")
        print("  - yotspot_debug.html (page source)")
        
    except KeyboardInterrupt:
        print("\nDebug interrupted by user")
    except Exception as e:
        print(f"Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 