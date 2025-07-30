import asyncio
from datetime import datetime, timedelta
import logging
import re
import pprint
from playwright.async_api import async_playwright, TimeoutError

# --- Configuration ---
BASE_URL = "https://www.yotspot.com"
JOB_SEARCH_URL = f"{BASE_URL}/job-search.html"
MAX_PAGES = 5  # Reduced to focus on recent jobs
MAX_JOB_AGE_DAYS = 3  # Only jobs from last 3 days
REQUEST_DELAY = 1.0 
HEADLESS_BROWSER = True # Set to False to watch the scraper work
OUTPUT_FILE_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE_NAME = f"yotspot_recent_3days.{OUTPUT_FILE_TIMESTAMP}.md"

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class YotspotScraper:
    """
    A robust, production-grade scraper for Yotspot.com, architected to use
    Playwright for the entire process to handle anti-scraping measures.
    This version uses a resilient, multi-selector strategy to handle
    inconsistent page layouts.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.jobs = []
        self.job_card_selector = "div.job-item--list"
        # --- ARCHITECT'S NOTE: This is the key architectural change. ---
        # Each field now has a LIST of possible selectors to try.
        self.job_detail_selectors = {
            "title": [
                "div.job-profile-v2__title h1", 
                "div.hgroup--job h1",
                "h1.job-title",
                "h1",
                ".job-profile h1",
                "div.job-header h1"
            ],
            "company": [
                "div.job-profile-v2__company a", 
                "li.company a",
                ".company-name",
                ".employer",
                "div.company a"
            ],
            "location": [
                "div.job-profile-v2__summary-item--location span", 
                "aside.job-profile__sidebar li.location span",
                ".location",
                ".job-location",
                "div.location",
                "span.location"
            ],
            "description": [
                "div.job-profile-v2__description", 
                "div.job-profile__description",
                ".job-description",
                ".description",
                "div.description",
                "article.job-content"
            ],
            "salary": [
                "div.job-profile-v2__summary-item--salary", 
                "aside.job-profile__sidebar li.salary",
                ".salary",
                ".compensation",
                "div.salary"
            ]
        }
        logger.info("YotspotScraper (Playwright Edition) initialized with resilient selectors.")

    def _normalize_date(self, date_str: str) -> datetime:
        if not date_str: return datetime.now() - timedelta(days=999)
        date_str = date_str.lower().replace('posted ', '').strip()
        if "today" in date_str or "hour" in date_str: return datetime.now()
        if "yesterday" in date_str: return datetime.now() - timedelta(days=1)
        match = re.search(r'(\d+)\s+days?', date_str)
        if match: return datetime.now() - timedelta(days=int(match.group(1)))
        try:
            cleaned_date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
            return datetime.strptime(cleaned_date_str, '%d %b %Y')
        except ValueError:
            logger.debug(f"Could not parse date: '{date_str}'")
            return datetime.now() - timedelta(days=999)

    def _clean_description(self, description: str) -> str:
        """Remove unwanted navigation elements from job description"""
        if not description or description == "N/A":
            return description
        
        # List of unwanted navigation elements to remove
        unwanted_elements = [
            "Login to Apply",
            "Overview",
            "Summary", 
            "Language & Visas",
            "Qualifications",
            "Location",
            "Search",
            "About",
            "More from",
            "View all",
            "Click to show map",
            "HOMEPORT",
            "DESTINATION", 
            "CURRENT LOCATION"
        ]
        
        # Remove each unwanted element
        cleaned_description = description
        for element in unwanted_elements:
            # Use regex to remove the element and any surrounding whitespace
            pattern = rf'\s*{re.escape(element)}\s*'
            cleaned_description = re.sub(pattern, '\n', cleaned_description, flags=re.IGNORECASE)
        
        # Clean up multiple newlines and extra whitespace
        cleaned_description = re.sub(r'\n\s*\n', '\n\n', cleaned_description)
        cleaned_description = re.sub(r'^\s+|\s+$', '', cleaned_description, flags=re.MULTILINE)
        
        return cleaned_description.strip()

    async def scrape_jobs(self, max_pages: int):
        logger.info("Starting Playwright-based scrape.")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=HEADLESS_BROWSER)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            urls_to_scrape = []
            keep_paginating = True

            # Phase 1: Discover all recent job URLs
            for page_num in range(1, max_pages + 1):
                if not keep_paginating: break
                page_url = f"{JOB_SEARCH_URL}?p={page_num}"
                logger.info(f"Discovering jobs on page {page_num}: {page_url}")
                try:
                    await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
                    
                    # Wait for any job-related content to load
                    await page.wait_for_load_state('networkidle', timeout=15000)
                    
                    # Try multiple selectors for job cards
                    job_cards = []
                    selectors_to_try = [
                        "div.job-item--list",
                        ".job-item",
                        ".job-listing",
                        "div[class*='job']",
                        "article.job"
                    ]
                    
                    for selector in selectors_to_try:
                        try:
                            await page.wait_for_selector(selector, timeout=5000)
                            job_cards = await page.locator(selector).all()
                            if job_cards:
                                logger.info(f"Found {len(job_cards)} job cards using selector: {selector}")
                                break
                        except:
                            continue
                    
                    if not job_cards:
                        logger.warning(f"No job cards found on page {page_num}")
                        break
                    
                    for card in job_cards:
                        try:
                            # Try to get date from various locations
                            date_str = ""
                            date_selectors = [
                                "ul.job-item__info li:last-child",
                                ".job-date",
                                ".posted-date",
                                "span.date"
                            ]
                            
                            for date_selector in date_selectors:
                                try:
                                    date_locator = card.locator(date_selector).first
                                    if await date_locator.count() > 0:
                                        date_str = await date_locator.inner_text()
                                        break
                                except:
                                    continue
                            
                            job_date = self._normalize_date(date_str)
                            days_old = (datetime.now() - job_date).days
                            if days_old > MAX_JOB_AGE_DAYS:
                                logger.info(f"Stopping pagination - found job {days_old} days old (older than {MAX_JOB_AGE_DAYS} days)")
                                keep_paginating = False
                                continue
                            
                            # Try to get job link from various locations
                            link_selectors = [
                                "div.job-item__position a",
                                ".job-title a",
                                "h3 a",
                                "a[href*='job-profile']",
                                "a"
                            ]
                            
                            relative_url = None
                            for link_selector in link_selectors:
                                try:
                                    link_locator = card.locator(link_selector).first
                                    if await link_locator.count() > 0:
                                        relative_url = await link_locator.get_attribute('href')
                                        if relative_url and 'job-profile' in relative_url:
                                            break
                                except:
                                    continue
                            
                            if relative_url:
                                if not relative_url.startswith('http'):
                                    relative_url = f"{self.base_url}{relative_url}"
                                urls_to_scrape.append(relative_url)
                                
                        except Exception as e:
                            logger.debug(f"Error processing job card: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error during job discovery on page {page_num}: {e}")
                    break
                await asyncio.sleep(REQUEST_DELAY)

            logger.info(f"Discovery complete. Found {len(urls_to_scrape)} recent job URLs to scrape.")

            # Phase 2: Scrape details for each discovered URL
            for url in urls_to_scrape:
                try:
                    logger.info(f"Scraping detail from: {url}")
                    await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    await page.wait_for_load_state('networkidle', timeout=15000)
                    
                    # Wait for any content to load
                    await page.wait_for_selector('body', timeout=10000)

                    job_details = {"source_url": url}
                    
                    # Try to extract job details with multiple fallback strategies
                    for key, selector_list in self.job_detail_selectors.items():
                        text_content = "N/A"
                        
                        # Try each selector in the list
                        for selector in selector_list:
                            try:
                                element = page.locator(selector).first
                                if await element.count() > 0:
                                    text_content = (await element.inner_text()).strip()
                                    if text_content:
                                        break
                            except:
                                continue
                        
                        # If no selector worked, try a more generic approach
                        if text_content == "N/A":
                            if key == "title":
                                # Try to find any h1 tag
                                try:
                                    h1_element = page.locator("h1").first
                                    if await h1_element.count() > 0:
                                        text_content = (await h1_element.inner_text()).strip()
                                except:
                                    pass
                            elif key == "description":
                                # Try to find any content area
                                try:
                                    content_selectors = [
                                        "main",
                                        "article",
                                        ".content",
                                        ".main-content",
                                        "div[class*='content']"
                                    ]
                                    for content_selector in content_selectors:
                                        try:
                                            content_element = page.locator(content_selector).first
                                            if await content_element.count() > 0:
                                                text_content = (await content_element.inner_text()).strip()
                                                if len(text_content) > 50:  # Ensure it's substantial content
                                                    break
                                        except:
                                            continue
                                except:
                                    pass
                        
                        job_details[key] = text_content
                    
                    # Clean up the description by removing unwanted navigation elements
                    if job_details.get('description'):
                        job_details['description'] = self._clean_description(job_details['description'])
                    
                    # Extract job ID from URL
                    id_match = re.search(r'/job-profile/(\d+)\.html', url)
                    job_details['id'] = id_match.group(1) if id_match else "N/A"
                    
                    # Only add jobs that have at least a title
                    if job_details.get('title') and job_details['title'] != "N/A":
                        job_details['quality_score'] = self._calculate_quality_score(**job_details)
                        self.jobs.append(job_details)
                        logger.info(f"Successfully scraped job: {job_details['title'][:50]}...")
                    else:
                        logger.warning(f"Skipping job with no title: {url}")
                    
                    await asyncio.sleep(REQUEST_DELAY)
                    
                except TimeoutError:
                    logger.error(f"Timeout: Could not load page {url}")
                except Exception as e:
                    logger.error(f"Error scraping detail for {url}: {e}")
            
            await browser.close()
            logger.info(f"Scraping finished. Successfully processed {len(self.jobs)} jobs.")

    def _calculate_quality_score(self, **kwargs) -> float:
        score = 0.0
        required_fields = ['title', 'company', 'location', 'description']
        for field in required_fields:
            if kwargs.get(field) and kwargs[field] not in ["N/A", ""]:
                score += 1
        return round(score / len(required_fields), 2)

    def print_jobs(self):
        logger.info(f"Printing {len(self.jobs)} jobs to the console.")
        print("\n" + "="*60)
        print(f"Found {len(self.jobs)} jobs on Yotspot.com (last {MAX_JOB_AGE_DAYS} days only)")
        print("="*60 + "\n")
        if not self.jobs:
            print("No recent jobs found in this run.")
            return
        for job in sorted(self.jobs, key=lambda j: j.get('id', '0'), reverse=True):
            pprint.pprint(job)
            print("-" * 20)

    def save_to_markdown(self, filename: str):
        logger.info(f"Saving {len(self.jobs)} jobs to {filename}.")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Yotspot.com Job Listings (Last {MAX_JOB_AGE_DAYS} Days)\n\n")
            f.write(f"*Scraped on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            f.write(f"*Total Jobs Found: {len(self.jobs)}*\n\n")
            f.write("---\n\n")
            if not self.jobs:
                f.write("No recent jobs found in this run.\n")
                return
            for job in sorted(self.jobs, key=lambda j: j.get('id', '0'), reverse=True):
                f.write(f"## {job['title']}\n\n")
                f.write(f"- **ID:** {job['id']}\n")
                f.write(f"- **Company:** {job['company']}\n")
                f.write(f"- **Location:** {job['location']}\n")
                f.write(f"- **Salary:** {job['salary']}\n")
                f.write(f"- **Quality Score:** {job['quality_score']}\n")
                f.write(f"- **Source URL:** [{job['source_url']}]({job['source_url']})\n\n")
                f.write("### Description\n")
                description = job.get('description', '')[:500] if job.get('description') else 'No description available'
                f.write(f"```\n{description}...\n```\n\n")
                f.write("---\n\n")
        logger.info("Successfully saved jobs to Markdown file.")

async def main():
    scraper = YotspotScraper(base_url=BASE_URL)
    await scraper.scrape_jobs(max_pages=MAX_PAGES)
    scraper.print_jobs()
    scraper.save_to_markdown(OUTPUT_FILE_NAME)

if __name__ == "__main__":
    asyncio.run(main())