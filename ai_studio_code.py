import asyncio
from datetime import datetime, timedelta
import logging
import re
import pprint
import aiohttp
from bs4 import BeautifulSoup

# --- Configuration ---
# Based on the architectural specifications for the YotCrew.app platform.
BASE_URL = "https://www.yotspot.com"
JOB_SEARCH_URL = f"{BASE_URL}/job-search.html"
MAX_PAGES = 10  # Maximum number of pages to check before stopping.
MAX_JOB_AGE_DAYS = 3 # Core requirement: Only scrape jobs posted within the last 3 days.
REQUEST_DELAY = 1.5  # Respectful delay between requests.
HEADLESS_BROWSER = True # Not used for aiohttp, but kept for consistency.
OUTPUT_FILE_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE_NAME = f"yotspot.{OUTPUT_FILE_TIMESTAMP}.md"

# --- Logging Setup ---
# As per spec for monitoring and observability.
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
    A production-grade scraper for Yotspot.com, using aiohttp for efficient,
    asynchronous HTTP requests and BeautifulSoup for HTML parsing.
    This scraper is designed to fetch only recent jobs (last 3 days).
    """

    def __init__(self, base_url: str):
        """Initializes the scraper."""
        self.base_url = base_url
        self.jobs = []
        # CSS selectors identified from Yotspot.com's structure
        self.job_card_selector = "div.job-search-result"
        self.job_detail_selectors = {
            "title": "h1.job-title",
            "company": "li.company-name a",
            "location": "li.location span",
            "description": "div.job-description",
            "salary": "li.salary"
        }
        logger.info("YotspotScraper initialized.")

    def _normalize_date(self, date_str: str) -> datetime:
        """
        Parses relative date strings from Yotspot (e.g., "1 day ago")
        into an absolute datetime object.
        """
        if not date_str:
            return datetime.now() - timedelta(days=99) # Return a very old date if not found

        date_str = date_str.lower()
        
        if "today" in date_str or "hour" in date_str or "minute" in date_str:
            return datetime.now()
        
        if "yesterday" in date_str:
            return datetime.now() - timedelta(days=1)
            
        match = re.search(r'(\d+)\s+day', date_str)
        if match:
            days_ago = int(match.group(1))
            return datetime.now() - timedelta(days=days_ago)

        # If the format is not recognized, assume it's old.
        return datetime.now() - timedelta(days=99)

    async def _scrape_job_detail(self, session, job_url: str) -> dict:
        """Scrapes the detailed information from a single job page."""
        try:
            async with session.get(job_url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch job detail page {job_url}, status: {response.status}")
                    return None
                
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                job_details = {
                    "source_url": job_url
                }

                for key, selector in self.job_detail_selectors.items():
                    element = soup.select_one(selector)
                    job_details[key] = element.text.strip() if element else "N/A"
                
                # Extract external ID from URL
                id_match = re.search(r'/job/(\d+)/', job_url)
                job_details['id'] = id_match.group(1) if id_match else "N/A"
                
                return job_details

        except Exception as e:
            logger.error(f"Error scraping detail for {job_url}: {e}", exc_info=True)
            return None

    async def scrape_jobs(self, max_pages: int):
        """
        Main method to orchestrate the scraping process.
        It launches a session, handles pagination, filters by date,
        and scrapes job details.
        """
        logger.info(f"Starting scrape for jobs posted in the last {MAX_JOB_AGE_DAYS} days.")
        async with aiohttp.ClientSession(headers={'User-Agent': 'Mozilla/5.0'}) as session:
            for page_num in range(1, max_pages + 1):
                page_url = f"{JOB_SEARCH_URL}?p={page_num}"
                logger.info(f"Scraping job listings from page {page_num}: {page_url}")
                
                try:
                    async with session.get(page_url) as response:
                        if response.status != 200:
                            logger.error(f"Failed to load page {page_num}, status: {response.status}. Stopping.")
                            break
                        content = await response.text()
                except Exception as e:
                    logger.error(f"Network error on page {page_num}: {e}. Stopping.", exc_info=True)
                    break

                soup = BeautifulSoup(content, 'html.parser')
                job_cards = soup.select(self.job_card_selector)

                if not job_cards:
                    logger.warning(f"No job cards found on page {page_num}. Stopping pagination.")
                    break
                
                keep_paginating = True
                detail_tasks = []

                for card in job_cards:
                    posted_date_element = card.select_one("div.posted-date")
                    posted_date_str = posted_date_element.text.strip() if posted_date_element else ""
                    
                    job_posted_date = self._normalize_date(posted_date_str)
                    
                    if (datetime.now() - job_posted_date).days >= MAX_JOB_AGE_DAYS:
                        logger.info(f"Found job older than {MAX_JOB_AGE_DAYS} days ('{posted_date_str}'). Stopping pagination.")
                        keep_paginating = False
                        break # Stop processing cards on this page

                    job_link_element = card.select_one("h3 a")
                    if job_link_element and job_link_element.get('href'):
                        detail_url = f"{self.base_url}{job_link_element['href']}"
                        # Add the detail scraping task to a list to run concurrently
                        detail_tasks.append(self._scrape_job_detail(session, detail_url))

                # Run all detail scraping tasks for the current page concurrently
                if detail_tasks:
                    logger.info(f"Fetching details for {len(detail_tasks)} recent jobs from page {page_num}.")
                    scraped_details = await asyncio.gather(*detail_tasks)
                    for job_detail in scraped_details:
                        if job_detail:
                            job_detail['quality_score'] = self._calculate_quality_score(**job_detail)
                            self.jobs.append(job_detail)
                
                if not keep_paginating:
                    break # Stop the main pagination loop
                
                await asyncio.sleep(REQUEST_DELAY) # Respectful delay
        
        logger.info(f"Scraping finished. Found {len(self.jobs)} total jobs.")


    def _calculate_quality_score(self, **kwargs) -> float:
        """Calculates a data quality score based on field completeness."""
        score = 0.0
        required_fields = ['title', 'company', 'location', 'description']
        total_weight = 1.0
        weight_per_field = total_weight / len(required_fields)
        
        for field in required_fields:
            if kwargs.get(field) and kwargs[field] != "N/A":
                score += weight_per_field
                
        return round(score, 2)

    def print_jobs(self):
        """Prints the scraped job data to the console."""
        logger.info(f"Printing {len(self.jobs)} jobs to the console.")
        print("\n" + "="*60)
        print(f"Found {len(self.jobs)} jobs on Yotspot.com (last {MAX_JOB_AGE_DAYS} days)")
        print("="*60 + "\n")

        if not self.jobs:
            print("No recent jobs found in this run.")
            return

        for job in self.jobs:
            pprint.pprint(job)
            print("-" * 20)

        logger.info("Finished printing jobs.")


    def save_to_markdown(self, filename: str):
        """Saves the scraped job data to a Markdown file."""
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
                f.write(f"```\n{job['description'][:500]}...\n```\n\n")
                f.write("---\n\n")
        logger.info("Successfully saved jobs to Markdown file.")


async def main():
    """Main function to run the scraper."""
    scraper = YotspotScraper(base_url=BASE_URL)
    await scraper.scrape_jobs(max_pages=MAX_PAGES)
    scraper.print_jobs()
    scraper.save_to_markdown(OUTPUT_FILE_NAME)

if __name__ == "__main__":
    # Ensure you have installed the necessary dependencies:
    # pip install aiohttp beautifulsoup4
    
    # To run the script:
    # python yotspot_scraper.py
    
    asyncio.run(main())