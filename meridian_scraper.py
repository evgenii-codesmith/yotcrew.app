#!/usr/bin/env python3
"""
Meridian Go Job Board Scraper
Scrapes job listings from https://www.meridiango.com/jobs with pagination support
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
from typing import List, Dict, Optional
import logging
from urllib.parse import urljoin, urlparse
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MeridianScraper:
    def __init__(self, base_url: str = "https://www.meridiango.com"):
        self.base_url = base_url
        self.jobs_url = f"{base_url}/jobs"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_total_pages(self) -> int:
        """Get the total number of pages available"""
        try:
            response = self.session.get(self.jobs_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for pagination elements
            pagination = soup.find('nav', {'aria-label': 'pagination'}) or soup.find('ul', class_=re.compile('pagination'))
            if pagination:
                page_links = pagination.find_all('a', href=re.compile(r'page=\d+'))
                if page_links:
                    # Extract page numbers from href attributes
                    page_numbers = []
                    for link in page_links:
                        href = link.get('href', '')
                        match = re.search(r'page=(\d+)', href)
                        if match:
                            page_numbers.append(int(match.group(1)))
                    return max(page_numbers) if page_numbers else 1
            
            # Alternative: look for "Last" button or total pages indicator
            last_link = soup.find('a', text=re.compile(r'Last|»|>>'))
            if last_link and last_link.get('href'):
                href = last_link['href']
                match = re.search(r'page=(\d+)', href)
                if match:
                    return int(match.group(1))
                    
            return 1  # Default to 1 page if no pagination found
            
        except Exception as e:
            logger.error(f"Error getting total pages: {e}")
            return 1
    
    def scrape_job_listings(self, page: int = 1) -> List[Dict[str, str]]:
        """Scrape job listings from a specific page"""
        jobs = []
        
        try:
            url = f"{self.jobs_url}?page={page}" if page > 1 else self.jobs_url
            logger.info(f"Scraping page {page}: {url}")
            
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job listings - adjust selectors based on actual HTML structure
            job_cards = soup.find_all('div', class_=re.compile('job|listing|position|card'))
            
            if not job_cards:
                # Try alternative selectors
                job_cards = soup.find_all('article', class_=re.compile('job|listing'))
                
            if not job_cards:
                # Try finding by data attributes
                job_cards = soup.find_all('div', {'data-job-id': True})
                
            logger.info(f"Found {len(job_cards)} job cards on page {page}")
            
            for card in job_cards:
                job_data = self.extract_job_data(card)
                if job_data:
                    jobs.append(job_data)
                    
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping page {page}: {e}")
            return []
    
    def extract_job_data(self, card) -> Optional[Dict[str, str]]:
        """Extract job data from a single job card element"""
        try:
            job_data = {}
            
            # Job title
            title_elem = card.find('h2') or card.find('h3') or card.find('a', class_=re.compile('title|job-title'))
            if not title_elem:
                title_elem = card.find('a', href=re.compile(r'/jobs/\d+'))
            job_data['title'] = title_elem.get_text(strip=True) if title_elem else 'N/A'
            
            # Job URL
            link_elem = title_elem.find('a') if title_elem else card.find('a', href=re.compile(r'/jobs/\d+'))
            if link_elem and link_elem.get('href'):
                job_data['url'] = urljoin(self.base_url, link_elem['href'])
            else:
                job_data['url'] = 'N/A'
            
            # Company name
            company_elem = card.find(class_=re.compile('company|employer')) or card.find('span', class_=re.compile('company'))
            job_data['company'] = company_elem.get_text(strip=True) if company_elem else 'Meridian Go'
            
            # Location
            location_elem = card.find(class_=re.compile('location|place')) or card.find('span', class_=re.compile('location'))
            job_data['location'] = location_elem.get_text(strip=True) if location_elem else 'N/A'
            
            # Job type (Full-time, Part-time, etc.)
            type_elem = card.find(class_=re.compile('type|employment')) or card.find('span', class_=re.compile('type'))
            job_data['job_type'] = type_elem.get_text(strip=True) if type_elem else 'N/A'
            
            # Posted date
            date_elem = card.find(class_=re.compile('date|posted')) or card.find('time')
            job_data['posted_date'] = date_elem.get_text(strip=True) if date_elem else 'N/A'
            
            # Salary (if available)
            salary_elem = card.find(class_=re.compile('salary|pay|compensation'))
            job_data['salary'] = salary_elem.get_text(strip=True) if salary_elem else 'N/A'
            
            # Description snippet
            desc_elem = card.find(class_=re.compile('description|summary')) or card.find('p')
            job_data['description'] = desc_elem.get_text(strip=True)[:200] + '...' if desc_elem else 'N/A'
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error extracting job data: {e}")
            return None
    
    def scrape_all_jobs(self, max_pages: Optional[int] = None) -> List[Dict[str, str]]:
        """Scrape all job listings across all pages"""
        all_jobs = []
        
        total_pages = self.get_total_pages()
        if max_pages:
            total_pages = min(total_pages, max_pages)
            
        logger.info(f"Total pages to scrape: {total_pages}")
        
        for page in range(1, total_pages + 1):
            page_jobs = self.scrape_job_listings(page)
            all_jobs.extend(page_jobs)
            
            # Add delay to be respectful
            if page < total_pages:
                time.sleep(1)
        
        logger.info(f"Total jobs scraped: {len(all_jobs)}")
        return all_jobs
    
    def save_to_json(self, jobs: List[Dict[str, str]], filename: str = "meridian_jobs.json"):
        """Save jobs to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(jobs)} jobs to {filename}")
    
    def save_to_csv(self, jobs: List[Dict[str, str]], filename: str = "meridian_jobs.csv"):
        """Save jobs to CSV file"""
        if not jobs:
            logger.warning("No jobs to save")
            return
            
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=jobs[0].keys())
            writer.writeheader()
            writer.writerows(jobs)
        logger.info(f"Saved {len(jobs)} jobs to {filename}")

def main():
    """Main execution function"""
    scraper = MeridianScraper()
    
    # Scrape all jobs
    jobs = scraper.scrape_all_jobs()
    
    # Save results
    if jobs:
        scraper.save_to_json(jobs)
        scraper.save_to_csv(jobs)
        
        # Print summary
        print(f"\nScraping completed successfully!")
        print(f"Total jobs found: {len(jobs)}")
        print(f"First 5 jobs:")
        for i, job in enumerate(jobs[:5], 1):
            print(f"{i}. {job['title']} at {job['company']} - {job['location']}")
    else:
        print("No jobs found. The website structure might have changed.")

if __name__ == "__main__":
    main()