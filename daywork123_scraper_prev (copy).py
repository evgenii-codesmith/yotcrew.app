import asyncio
import time
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError
from bs4 import BeautifulSoup
import logging
import re
import pprint

# --- Configuration ---
# In a real application, this would come from a config file or environment variables
# as specified in your documents (e.g., daywork123_scraper_spec.md).
BASE_URL = "https://www.daywork123.com/jobannouncementlist.aspx"
MAX_PAGES = 1  # Limit for this demonstration, your spec allows for more.
REQUEST_DELAY = 2.5  # Respectful delay between requests as per your spec.
HEADLESS_BROWSER = True # Set to False for debugging to see the browser UI.
OUTPUT_FILE_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE_NAME = f"daywork123.{OUTPUT_FILE_TIMESTAMP}.md"

# --- Logging Setup ---
# As per your spec for monitoring and observability.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Daywork123Scraper:
    """
    A production-grade scraper for Daywork123.com, built according to the
    provided architectural specifications. It uses Playwright for robust,
    anti-detection browser automation.
    """

    def __init__(self, base_url: str):
        """Initializes the scraper with the target URL."""
        self.base_url = base_url
        self.jobs = []
        # FIX: Corrected job table selector based on provided HTML
        self.job_table_selector = '#ContentPlaceHolder1_RepJobAnnouncement'
        logger.info("Daywork123Scraper initialized.")

    async def scrape_jobs(self, max_pages: int):
        """
        Main method to orchestrate the scraping process.
        It launches a browser, handles pagination, and extracts job data.
        """
        logger.info(f"Starting scrape for up to {max_pages} pages.")
        async with async_playwright() as p:
            # Launch browser with anti-detection measures as per spec
            browser = await p.chromium.launch(headless=HEADLESS_BROWSER)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
            )
            # Add stealth script to avoid detection
            await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            page = await context.new_page()

            try:
                for page_num in range(1, max_pages + 1):
                    logger.info(f"Scraping page {page_num}...")
                    page_loaded_successfully = await self._navigate_to_page(page, page_num)

                    if not page_loaded_successfully:
                        logger.error(f"Failed to load page {page_num} or find job table. Stopping.")
                        break
                    
                    content = await page.content()
                    new_jobs = self._parse_jobs(content)

                    if not new_jobs:
                        logger.warning(f"No jobs found on page {page_num} while parsing. Stopping pagination.")
                        break
                    
                    self.jobs.extend(new_jobs)
                    logger.info(f"Found {len(new_jobs)} jobs on page {page_num}. Total jobs: {len(self.jobs)}.")

                    # Respectful delay
                    await asyncio.sleep(REQUEST_DELAY)

            except Exception as e:
                logger.error(f"An error occurred during scraping: {e}", exc_info=True)
            finally:
                await browser.close()
                logger.info("Browser closed. Scraping finished.")

    async def _navigate_to_page(self, page, page_num: int) -> bool:
        """
        Navigates to a specific page number on the website and waits for the
        job table to be visible. Returns True on success, False on failure.
        """
        try:
            if page_num == 1:
                # FIX: Changed wait_until to 'domcontentloaded' for initial page load
                await page.goto(self.base_url, wait_until='domcontentloaded')
            else:
                # Find the link for the next page and click it
                pagination_link_selector = f'a[href*="Page${page_num}"]'
                await page.click(pagination_link_selector)
            
            # FIX: Increased timeout for waiting for the job table selector
            await page.wait_for_selector(self.job_table_selector, timeout=30000) # 30 second timeout
            return True
        except TimeoutError:
            logger.error(f"Timeout occurred waiting for job table or pagination link on page {page_num}.")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during navigation to page {page_num}: {e}")
            return False


    def _parse_jobs(self, html_content: str) -> list:
        """
        Parses the HTML content of a job list page to extract job details.
        Uses BeautifulSoup for robust HTML parsing.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        job_listings = []
        
        # Find the main table containing the jobs
        job_table = soup.select_one(self.job_table_selector)
        if not job_table:
            # This check is now redundant due to the wait_for_selector, but good for safety.
            logger.warning("Could not find job table in the parsed HTML.")
            return []

        # Find all job rows, skipping the header row
        job_rows = job_table.find_all('tr')[1:]

        for row in job_rows:
            cells = row.find_all('td')
            if len(cells) < 6:
                continue

            try:
                # Extract data based on the table structure
                job_title_link = cells[0].find('a')
                job_title = cells[3].text.strip() # The "Work Type" column contains the job description/title
                
                # The source URL is constructed from the base URL and the link's href
                job_url = f"https://www.daywork123.com/{job_title_link['href']}" if job_title_link and job_title_link.get('href') else "N/A"
                
                # Extracting other fields, adjusted based on the new HTML structure
                company = cells[2].text.strip()
                location = cells[4].text.strip()
                job_type = "" # The previous 'Job Type' column is now the job description
                posted_date_str = cells[1].text.strip()
                
                # A simple quality score as per the spec
                quality_score = self._calculate_quality_score(
                    title=job_title, company=company, location=location
                )

                job_listings.append({
                    'title': job_title,
                    'company': company,
                    'location': location,
                    'job_type': job_type,
                    'posted_date': posted_date_str,
                    'source_url': job_url,
                    'quality_score': quality_score
                })
            except (AttributeError, IndexError) as e:
                logger.error(f"Error parsing a job row: {e}. Row content: {row}")

        return job_listings
        
    def _calculate_quality_score(self, **kwargs) -> float:
        """
        Calculates a data quality score based on field completeness.
        This is a simplified version of the algorithm in your spec.
        """
        score = 0.0
        required_fields = ['title', 'company', 'location']
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
        print(f"Found {len(self.jobs)} jobs on Daywork123.com")
        print("="*60 + "\n")

        if not self.jobs:
            print("No jobs found in this run.")
            return

        for i, job in enumerate(self.jobs, 1):
            pprint.pprint(job)
            print("-" * 20)

        logger.info("Finished printing jobs.")


    def save_to_markdown(self, filename: str):
        """Saves the scraped job data to a Markdown file."""
        logger.info(f"Saving {len(self.jobs)} jobs to {filename}.")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Daywork123.com Job Listings\n\n")
            f.write(f"*Scraped on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            f.write(f"*Total Jobs Found: {len(self.jobs)}*\n\n")
            f.write("---\n\n")

            if not self.jobs:
                f.write("No jobs found in this run.\n")
                return

            for job in self.jobs:
                f.write(f"## {job['title']}\n\n")
                f.write(f"- **Company:** {job['company']}\n")
                f.write(f"- **Location:** {job['location']}\n")
                f.write(f"- **Job Type:** {job['job_type']}\n")
                f.write(f"- **Posted Date:** {job['posted_date']}\n")
                f.write(f"- **Quality Score:** {job['quality_score']}\n")
                f.write(f"- **Source URL:** [{job['source_url']}]({job['source_url']})\n\n")
                f.write("---\n\n")
        logger.info("Successfully saved jobs to Markdown file.")


async def main():
    """Main function to run the scraper."""
    scraper = Daywork123Scraper(base_url=BASE_URL)
    await scraper.scrape_jobs(max_pages=MAX_PAGES)
    scraper.print_jobs()
    scraper.save_to_markdown(OUTPUT_FILE_NAME) # Uncommented this line

if __name__ == "__main__":
    # Ensure you have installed the necessary dependencies:
    # pip install playwright beautifulsoup4
    # And install the browser binaries:
    # playwright install chromium
    
    # To run the script:
    # python your_script_name.py
    
    asyncio.run(main())