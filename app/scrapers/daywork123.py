"""Daywork123.com scraper with anti-detection measures"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, AsyncIterator
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse

try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available. Install with: pip install playwright")

from .base import BaseScraper, UniversalJob, JobSource, EmploymentType, Department, VesselType
from .registry import register_scraper

logger = logging.getLogger(__name__)

@register_scraper
class Daywork123Scraper(BaseScraper):
    """Production-grade Daywork123.com scraper with anti-detection"""
    
    def __init__(self):
        self.config = {
            'max_retries': 3,
            'request_delay': 2.5,
            'user_agents': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        }
    
    @property
    def source_name(self) -> str:
        return JobSource.DAYWORK123
    
    @property
    def base_url(self) -> str:
        return "https://www.daywork123.com"
    
    async def scrape_jobs(self, 
                         max_pages: int = 5,
                         filters: Optional[Dict[str, Any]] = None) -> AsyncIterator[UniversalJob]:
        """Scrape jobs from Daywork123.com"""
        logger.info(f"Starting Daywork123 scraper for {max_pages} pages")
        
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                )
                page = await context.new_page()
                
                # Navigate to jobs page
                await page.goto(f"{self.base_url}/JobAnnouncementList.aspx", wait_until='networkidle')
                
                for page_num in range(1, max_pages + 1):
                    logger.info(f"Scraping Daywork123 page {page_num}")
                    
                    if page_num > 1:
                        # Navigate to next page
                        next_url = f"{self.base_url}/JobAnnouncementList.aspx?page={page_num}"
                        await page.goto(next_url, wait_until='networkidle')
                    
                    # Wait for job listings to load (table structure)
                    await page.wait_for_selector('#ContentPlaceHolder1_RepJobAnnouncement', timeout=10000)
                    
                    # Extract job listings from table rows
                    job_elements = await page.query_selector_all('#ContentPlaceHolder1_RepJobAnnouncement tr:not(.head)')
                    
                    # Extract all job data immediately to avoid context issues
                    jobs_found = 0
                    for element in job_elements:
                        try:
                            job_data = await self._extract_job_from_element(element, page)
                            if job_data:
                                # Convert to UniversalJob and yield
                                universal_job = UniversalJob(**job_data)
                                yield universal_job
                                jobs_found += 1
                        except Exception as e:
                            logger.error(f"Error extracting job element: {e}")
                            continue
                    
                    logger.info(f"Page {page_num}: Found {jobs_found} jobs")
                    
                    if jobs_found == 0:
                        logger.warning(f"No jobs found on page {page_num}, stopping pagination")
                        break
                    
                    # Add delay between pages
                    if page_num < max_pages:
                        await asyncio.sleep(2)
                
                await browser.close()
                
        except Exception as e:
            logger.error(f"Error in Daywork123 scraper: {e}")
            raise
    
    async def _extract_job_from_element(self, element, page) -> Optional[Dict[str, Any]]:
        """Extract job data from a single job element (table row)"""
        try:
            # Extract all data immediately to avoid context issues
            cells = await element.query_selector_all('td')
            if len(cells) < 3:  # Need at least ID, title, and other info
                return None
            
            # Extract all text content immediately
            cell_texts = []
            for cell in cells:
                try:
                    text = await cell.text_content()
                    cell_texts.append(text.strip() if text else "")
                except Exception:
                    cell_texts.append("")
            
            if len(cell_texts) < 3:
                return None
            
            # Extract job ID from first cell
            job_id = cell_texts[0] if cell_texts else ""
            
            # Extract title and link from second cell
            title_cell = cells[1] if len(cells) > 1 else None
            if not title_cell:
                return None
            
            # Try to get the link from the title cell
            try:
                link_elem = await title_cell.query_selector('a')
                if link_elem:
                    href = await link_elem.get_attribute('href')
                    job_url = urljoin(self.base_url, href) if href else ""
                    title = cell_texts[1] if len(cell_texts) > 1 else ""
                else:
                    job_url = ""
                    title = cell_texts[1] if len(cell_texts) > 1 else ""
            except Exception:
                job_url = ""
                title = cell_texts[1] if len(cell_texts) > 1 else ""
            
            if not title:
                return None
            
            # Extract other information from remaining cells
            location = cell_texts[2] if len(cell_texts) > 2 else ""
            company = "Daywork123"  # Default company name
            date_posted = cell_texts[4] if len(cell_texts) > 4 else ""
            
            # Try to extract company name from the job description if it's short enough
            if len(cell_texts) > 3 and cell_texts[3]:
                potential_company = cell_texts[3][:50]  # Limit to 50 chars
                if len(potential_company) <= 100:
                    company = potential_company
            
            # Create job data
            job_data = {
                'external_id': f"dw123_{job_id}",
                'title': title,
                'company': company,
                'source': JobSource.DAYWORK123,
                'source_url': job_url if job_url else f"{self.base_url}/JobAnnouncementList.aspx",
                'location': location,
                'date_posted': date_posted,
                'description': f"Job ID: {job_id}",
                'employment_type': None,
                'department': None,
                'vessel_type': None,
                'salary_min': None,
                'salary_max': None,
                'salary_currency': None,
                'requirements': [],
                'benefits': [],
                'contact_info': {}
            }
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error extracting job element: {e}")
            return None
    
    async def _get_job_details(self, job_url: str, page) -> Dict[str, Any]:
        """Get detailed job information from job page"""
        try:
            await page.goto(job_url, wait_until='networkidle')
            
            # Extract detailed description
            desc_elem = await page.query_selector('.job-details, .full-description')
            full_description = await desc_elem.text_content() if desc_elem else ""
            
            # Extract requirements
            req_elem = await page.query_selector('.requirements, .job-requirements')
            requirements_text = await req_elem.text_content() if req_elem else ""
            requirements = self._parse_requirements(requirements_text)
            
            # Extract benefits
            benefits_elem = await page.query_selector('.benefits, .job-benefits')
            benefits_text = await benefits_elem.text_content() if benefits_elem else ""
            benefits = self._parse_benefits(benefits_text)
            
            # Extract vessel info
            vessel_elem = await page.query_selector('.vessel-info, .yacht-details')
            vessel_info = await vessel_elem.text_content() if vessel_elem else ""
            
            return {
                'full_description': full_description,
                'requirements': requirements,
                'benefits': benefits,
                'vessel_info': vessel_info
            }
            
        except Exception as e:
            logger.error(f"Error getting job details: {e}")
            return {}
    
    def _normalize_job(self, raw_job: Dict[str, Any]) -> UniversalJob:
        """Convert raw job data to UniversalJob format"""
        # Parse employment type
        employment_type = self._detect_employment_type(raw_job.get('title', ''))
        
        # Parse department
        department = self._detect_department(raw_job.get('title', ''))
        
        # Parse vessel type
        vessel_type = self._detect_vessel_type(raw_job.get('vessel_info', ''))
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(raw_job)
        
        return UniversalJob(
            external_id=raw_job.get('external_id', ''),
            title=raw_job.get('title', ''),
            company=raw_job.get('company', ''),
            source=self.source_name,
            source_url=raw_job.get('url', ''),
            location=raw_job.get('location', ''),
            vessel_type=vessel_type,
            employment_type=employment_type,
            department=department,
            salary_range=raw_job.get('salary'),
            description=raw_job.get('full_description', raw_job.get('description', '')),
            requirements=raw_job.get('requirements', []),
            benefits=raw_job.get('benefits', []),
            posted_date=raw_job.get('posted_date'),
            quality_score=quality_score,
            raw_data=raw_job
        )
    
    def _extract_job_id(self, url: str) -> str:
        """Extract job ID from URL"""
        if not url:
            return ""
        match = re.search(r'/jobs/(\d+)', url)
        return match.group(1) if match else url
    
    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse posted date from text"""
        if not date_text:
            return None
        
        # Handle relative dates like "2 days ago", "1 week ago"
        import dateparser
        try:
            return dateparser.parse(date_text, settings={'RETURN_AS_TIMEZONE_AWARE': False})
        except:
            return datetime.utcnow()
    
    def _parse_requirements(self, text: str) -> List[str]:
        """Parse requirements from text"""
        if not text:
            return []
        
        # Split by common delimiters
        requirements = re.split(r'[•·\-\n]', text)
        return [req.strip() for req in requirements if req.strip()]
    
    def _parse_benefits(self, text: str) -> List[str]:
        """Parse benefits from text"""
        if not text:
            return []
        
        benefits = re.split(r'[•·\-\n]', text)
        return [benefit.strip() for benefit in benefits if benefit.strip()]
    
    def _detect_employment_type(self, title: str) -> Optional[EmploymentType]:
        """Detect employment type from job title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['daywork', 'day work', 'daily']):
            return EmploymentType.DAYWORK
        elif any(word in title_lower for word in ['rotational', 'rotation']):
            return EmploymentType.ROTATIONAL
        elif any(word in title_lower for word in ['seasonal', 'season']):
            return EmploymentType.SEASONAL
        elif any(word in title_lower for word in ['contract', 'temporary']):
            return EmploymentType.TEMPORARY
        else:
            return EmploymentType.PERMANENT
    
    def _detect_department(self, title: str) -> Optional[Department]:
        """Detect department from job title"""
        title_lower = title.lower()
        
        deck_keywords = ['deckhand', 'bosun', 'mate', 'captain', 'officer', 'deck']
        interior_keywords = ['stewardess', 'steward', 'interior', 'housekeeping', 'butler']
        engineering_keywords = ['engineer', 'mechanic', 'eto', 'technical']
        galley_keywords = ['chef', 'cook', 'galley', 'kitchen']
        
        if any(keyword in title_lower for keyword in deck_keywords):
            return Department.DECK
        elif any(keyword in title_lower for keyword in interior_keywords):
            return Department.INTERIOR
        elif any(keyword in title_lower for keyword in engineering_keywords):
            return Department.ENGINEERING
        elif any(keyword in title_lower for keyword in galley_keywords):
            return Department.GALLEY
        else:
            return Department.OTHER
    
    def _detect_vessel_type(self, text: str) -> Optional[VesselType]:
        """Detect vessel type from text"""
        text_lower = text.lower()
        
        if 'sailing' in text_lower or 'sail' in text_lower:
            return VesselType.SAILING_YACHT
        elif 'catamaran' in text_lower:
            return VesselType.CATAMARAN
        elif 'superyacht' in text_lower or 'super yacht' in text_lower:
            return VesselType.SUPER_YACHT
        elif 'expedition' in text_lower:
            return VesselType.EXPEDITION
        else:
            return VesselType.MOTOR_YACHT
    
    def _calculate_quality_score(self, job: Dict[str, Any]) -> float:
        """Calculate data quality score (0-1)"""
        score = 0.0
        
        # Completeness (60%)
        required_fields = ['title', 'company', 'location', 'description']
        completeness = sum(1 for field in required_fields if job.get(field)) / len(required_fields)
        score += completeness * 0.6
        
        # URL validity (20%)
        if job.get('url') and job.get('external_id'):
            score += 0.2
        
        # Description length (20%)
        description = job.get('description', '')
        if len(description) > 100:
            score += 0.2
        elif len(description) > 50:
            score += 0.1
        
        return min(1.0, score)
    
    async def test_connection(self) -> bool:
        """Test Daywork123.com accessibility"""
        if not PLAYWRIGHT_AVAILABLE:
            return False
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                response = await page.goto(self.base_url, timeout=10000)
                await browser.close()
                
                return response.status == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_supported_filters(self) -> List[str]:
        """Return supported filter parameters"""
        return ["location", "date_range", "job_type", "vessel_size", "salary_range"]