import requests
from bs4 import BeautifulSoup
import time
import random
import logging
from datetime import datetime
from typing import List, Dict, Any
import re
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class YotspotScraper:
    def __init__(self):
        self.base_url = "https://www.yotspot.com"
        self.search_url = f"{self.base_url}/job-search.html"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def _respectful_delay(self, min_delay: float = 2.0, max_delay: float = 5.0):
        """Add random delay between requests to be respectful"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _parse_job_card(self, job_element) -> Dict[str, Any]:
        """Parse individual job card from HTML"""
        try:
            job_data = {}
            
            # Extract job title
            title_elem = job_element.find('h3') or job_element.find('h4') or job_element.find('a')
            if title_elem:
                job_data['title'] = title_elem.get_text(strip=True)
                # Extract external ID from URL if present
                if title_elem.find('a'):
                    href = title_elem.find('a').get('href', '')
                    job_id_match = re.search(r'#(\d+)', href)
                    if job_id_match:
                        job_data['external_id'] = job_id_match.group(1)
            
            # Extract job details (usually in list items or divs)
            details = job_element.find_all(['li', 'div', 'span'])
            
            for detail in details:
                text = detail.get_text(strip=True)
                if not text:
                    continue
                
                # Parse different job attributes
                if 'Starting' in text and any(month in text for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                    job_data['start_date'] = text
                elif any(job_type in text for job_type in ['Permanent', 'Temporary', 'Rotational', 'Seasonal', 'Contract']):
                    job_data['job_type'] = text
                elif 'Motor Yacht' in text or 'Sailing Yacht' in text or 'Chase Boat' in text:
                    job_data['vessel_type'] = text
                elif 'm (' in text and 'ft)' in text:  # e.g., "36m (118ft)"
                    job_data['vessel_size'] = text
                elif any(currency in text for currency in ['USD', 'EUR', 'GBP', '$', '€', '£']):
                    job_data['salary_range'] = text
                    if 'Per Month' in text or 'per month' in text:
                        job_data['salary_per'] = 'month'
                    elif 'Per Day' in text or 'per day' in text:
                        job_data['salary_per'] = 'day'
                    elif 'Per Year' in text or 'per year' in text:
                        job_data['salary_per'] = 'year'
                elif any(location in text for location in ['United States', 'France', 'Italy', 'Spain', 'Greece', 'Monaco', 'Germany', 'United Kingdom']):
                    job_data['location'] = text
            
            # Extract "View Job" link for source URL
            view_job_link = job_element.find('a', text=re.compile(r'View Job', re.I))
            if view_job_link:
                job_data['source_url'] = urljoin(self.base_url, view_job_link.get('href', ''))
            
            # Set posted date to now if we don't have it
            job_data['posted_at'] = datetime.now()
            
            # Generate external_id if not found
            if 'external_id' not in job_data:
                job_data['external_id'] = f"yotspot_{hash(job_data.get('title', '') + str(job_data['posted_at']))}"
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error parsing job card: {e}")
            return {}
    
    def _extract_job_details(self, job_url: str) -> Dict[str, Any]:
        """Extract detailed job information from job detail page"""
        try:
            self._respectful_delay()
            response = self.session.get(job_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {}
            
            # Extract job description
            description_elem = soup.find('div', class_=re.compile(r'description|content|detail'))
            if description_elem:
                details['description'] = description_elem.get_text(strip=True)
            
            # Extract company name
            company_elem = soup.find('div', class_=re.compile(r'company|employer'))
            if company_elem:
                details['company'] = company_elem.get_text(strip=True)
            
            return details
            
        except Exception as e:
            logger.error(f"Error extracting job details from {job_url}: {e}")
            return {}
    
    async def scrape_jobs(self, max_pages: int = 5) -> List[Dict[str, Any]]:
        """Scrape jobs from Yotspot"""
        all_jobs = []
        
        try:
            logger.info("Starting Yotspot scraping...")
            
            for page in range(1, max_pages + 1):
                logger.info(f"Scraping page {page}")
                
                # Add delay between pages
                if page > 1:
                    self._respectful_delay(3.0, 6.0)
                
                # Get page
                params = {'page': page} if page > 1 else {}
                response = self.session.get(self.search_url, params=params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job listings - these might be in various containers
                job_elements = []
                
                # Try different selectors that might contain job listings
                selectors = [
                    'div[class*="job"]',
                    'div[class*="position"]',
                    'div[class*="listing"]',
                    'article',
                    'li[class*="job"]',
                    '.job-card',
                    '.position-card'
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)
                    if elements:
                        job_elements = elements
                        break
                
                # If no specific job containers found, look for elements with "View Job" links
                if not job_elements:
                    view_job_links = soup.find_all('a', text=re.compile(r'View Job', re.I))
                    job_elements = [link.find_parent() for link in view_job_links if link.find_parent()]
                
                logger.info(f"Found {len(job_elements)} job elements on page {page}")
                
                if not job_elements:
                    logger.warning(f"No job elements found on page {page}, stopping")
                    break
                
                # Parse each job
                page_jobs = []
                for job_elem in job_elements:
                    job_data = self._parse_job_card(job_elem)
                    if job_data and job_data.get('title'):
                        # Get additional details if we have a source URL
                        if job_data.get('source_url'):
                            additional_details = self._extract_job_details(job_data['source_url'])
                            job_data.update(additional_details)
                        
                        page_jobs.append(job_data)
                
                all_jobs.extend(page_jobs)
                logger.info(f"Scraped {len(page_jobs)} jobs from page {page}")
                
                # If no jobs found on this page, stop
                if not page_jobs:
                    break
            
            logger.info(f"Scraping completed. Total jobs found: {len(all_jobs)}")
            return all_jobs
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return all_jobs
    
    def scrape_job_details(self, job_id: str) -> Dict[str, Any]:
        """Scrape detailed information for a specific job"""
        try:
            job_url = f"{self.base_url}/job-detail/{job_id}"
            return self._extract_job_details(job_url)
        except Exception as e:
            logger.error(f"Error scraping job details for {job_id}: {e}")
            return {}
    
    def test_scraping(self) -> Dict[str, Any]:
        """Test the scraper with a single page"""
        try:
            response = self.session.get(self.search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            return {
                "status": "success",
                "url": self.search_url,
                "title": soup.title.get_text() if soup.title else "No title",
                "total_links": len(soup.find_all('a')),
                "view_job_links": len(soup.find_all('a', text=re.compile(r'View Job', re.I)))
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            } 