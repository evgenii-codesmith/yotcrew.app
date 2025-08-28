"""Daywork123.com scraper with anti-detection measures"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, AsyncIterator
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse
from sqlalchemy.orm import Session

try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available. Install with: pip install playwright")

from .base import BaseScraper, UniversalJob, JobSource, EmploymentType, Department, VesselType
from .registry import register_scraper
from ..database import SessionLocal
from ..models import Job

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
                            universal_job = await self._extract_job_from_element(element, page)
                            if universal_job:
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
    
    async def _extract_job_from_element(self, element, page) -> Optional[UniversalJob]:
        """Extract job data from a single job element (table row) and return UniversalJob"""
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
            if not job_id:
                return None
            
            # Correct field mapping based on actual table structure:
            # Cell 0: Job ID  
            # Cell 1: Date
            # Cell 2: Company
            # Cell 3: Job Title/Description
            # Cell 4: Location
            
            # Extract company from cell 2
            company = cell_texts[2] if len(cell_texts) > 2 else "Daywork123"
            
            # Extract title/description from cell 3
            title_description = cell_texts[3] if len(cell_texts) > 3 else ""
            if not title_description or len(title_description) < 10:
                return None
            
            # Extract location from cell 4
            location = cell_texts[4] if len(cell_texts) > 4 else "Unknown"
            
            # Parse title from title_description
            # First line or first sentence is often the actual job title
            lines = title_description.split('\n')
            first_line = lines[0].strip()
            
            # Extract title (look for job titles at the beginning)
            if first_line.startswith('POSITION:'):
                # Format: "POSITION: Mate [9 DAYS]"
                title = first_line.replace('POSITION:', '').strip()
                title = title.split('[')[0].strip()  # Remove brackets like [9 DAYS]
            elif ':' in first_line and len(first_line.split(':')[0]) < 30:
                # Format: "Job title: Captain for a CAL 33' Sailboat"
                title = first_line.split(':', 1)[1].strip()
            else:
                # Use first line as title, limit length
                title = first_line[:100] if first_line else "Position Available"
            
            # Use the full title_description as description
            description = title_description
            
            # Date is in cell 1 (was being used as title)
            date_posted_str = cell_texts[1] if len(cell_texts) > 1 else ""
            
            # Try to get the job URL from any cell with a link
            job_url = f"{self.base_url}/JobAnnouncementList.aspx"  # Default
            try:
                for i, cell in enumerate(cells[:5]):  # Check first 5 cells for links
                    link_elem = await cell.query_selector('a')
                    if link_elem:
                        href = await link_elem.get_attribute('href')
                        if href and not href.startswith('javascript:'):
                            job_url = urljoin(self.base_url, href)
                            break
            except Exception:
                pass  # Use default URL
            
            # Parse date
            posted_date = self._parse_date(date_posted_str) if date_posted_str else datetime.utcnow()
            
            # Parse employment type from title
            employment_type = self._detect_employment_type(title)
            
            # Parse department from title
            department = self._detect_department(title)
            
            # Parse vessel type (if any info available)
            vessel_type = self._detect_vessel_type(title + " " + description)
            
            # Ensure all fields respect database constraints
            title = title[:255] if title else ""  # title field is 255 chars
            company = company[:100] if company else "Daywork123"  # company field is 100 chars
            location = location[:100] if location else "Unknown"  # location field is 100 chars
            description = description[:2000] if description else f"Job ID: {job_id} - Position available via Daywork123.com"  # description field is 2000 chars
            
            # Ensure minimum description length
            if len(description) < 10:
                description = f"Job ID: {job_id} - {title} position available via Daywork123.com"
            
            # Calculate quality score
            quality_score = self._calculate_quality_score({
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'url': job_url,
                'external_id': job_id
            })
            
            # Create raw data for debugging
            raw_data = {
                'job_id': job_id,
                'cell_texts': cell_texts,
                'extraction_timestamp': datetime.utcnow().isoformat(),
                'page_url': page.url if page else None
            }
            
            # Create UniversalJob object
            universal_job = UniversalJob(
                external_id=f"dw123_{job_id}",
                title=title,
                company=company,
                source=JobSource.DAYWORK123,
                source_url=job_url,
                location=location,
                description=description,
                employment_type=employment_type,
                department=department,
                vessel_type=vessel_type,
                posted_date=posted_date,
                requirements=[],
                benefits=[],
                quality_score=quality_score,
                raw_data=raw_data
            )
            
            return universal_job
            
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
    
    async def save_jobs_to_db(self, jobs: List[UniversalJob]) -> int:
        """Save scraped jobs to yacht_jobs.db
        
        Args:
            jobs: List of UniversalJob objects to save
            
        Returns:
            Number of jobs successfully saved
        """
        if not jobs:
            return 0
            
        saved_count = 0
        
        with SessionLocal() as db:
            for job in jobs:
                try:
                    # Check if job already exists
                    existing_job = db.query(Job).filter(
                        Job.external_id == job.external_id,
                        Job.source == job.source
                    ).first()
                    
                    if existing_job:
                        # Update existing job
                        existing_job.title = job.title
                        existing_job.company = job.company
                        existing_job.location = job.location
                        existing_job.country = job.country
                        existing_job.region = job.region
                        existing_job.description = job.description
                        existing_job.salary_range = job.salary_range
                        existing_job.salary_currency = job.salary_currency
                        existing_job.salary_period = job.salary_period
                        existing_job.employment_type = job.employment_type.value if hasattr(job.employment_type, 'value') else job.employment_type
                        existing_job.job_type = job.employment_type.value if hasattr(job.employment_type, 'value') else job.employment_type
                        existing_job.department = job.department.value if hasattr(job.department, 'value') else job.department
                        existing_job.vessel_type = job.vessel_type.value if hasattr(job.vessel_type, 'value') else job.vessel_type
                        existing_job.vessel_size = job.vessel_size
                        existing_job.vessel_name = job.vessel_name
                        existing_job.position_level = job.position_level
                        existing_job.start_date = job.start_date
                        existing_job.requirements = job.requirements
                        existing_job.benefits = job.benefits
                        existing_job.posted_date = job.posted_date
                        existing_job.quality_score = job.quality_score
                        existing_job.raw_data = job.raw_data
                        existing_job.updated_at = datetime.utcnow()
                        
                        logger.debug(f"Updated existing job: {job.title}")
                    else:
                        # Create new job
                        db_job = Job(
                            external_id=job.external_id,
                            title=job.title,
                            company=job.company,
                            location=job.location,
                            country=job.country,
                            region=job.region,
                            description=job.description,
                            source=job.source,
                            source_url=str(job.source_url),
                            salary_range=job.salary_range,
                            salary_currency=job.salary_currency,
                            salary_period=job.salary_period,
                            employment_type=job.employment_type.value if hasattr(job.employment_type, 'value') else job.employment_type,
                            job_type=job.employment_type.value if hasattr(job.employment_type, 'value') else job.employment_type,
                            department=job.department.value if hasattr(job.department, 'value') else job.department,
                            vessel_type=job.vessel_type.value if hasattr(job.vessel_type, 'value') else job.vessel_type,
                            vessel_size=job.vessel_size,
                            vessel_name=job.vessel_name,
                            position_level=job.position_level,
                            start_date=job.start_date,
                            requirements=job.requirements,
                            benefits=job.benefits,
                            posted_date=job.posted_date,
                            posted_at=job.posted_date,
                            quality_score=job.quality_score,
                            raw_data=job.raw_data,
                            scraped_at=job.scraped_at,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        db.add(db_job)
                        logger.debug(f"Added new job: {job.title}")
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Error saving job {job.title}: {e}")
                    continue
            
            try:
                db.commit()
                logger.info(f"Successfully saved {saved_count} jobs to database")
            except Exception as e:
                logger.error(f"Error committing jobs to database: {e}")
                db.rollback()
                return 0
        
        return saved_count
    
    async def scrape_and_save_jobs(self, max_pages: int = 5, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Scrape jobs and save them to database
        
        Args:
            max_pages: Maximum number of pages to scrape
            filters: Optional filters to apply
            
        Returns:
            Dictionary with scraping results
        """
        start_time = datetime.utcnow()
        jobs_list = []
        
        try:
            # Collect all jobs from scraping
            async for job in self.scrape_jobs(max_pages, filters):
                jobs_list.append(job)
            
            # Save to database
            saved_count = await self.save_jobs_to_db(jobs_list)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            result = {
                "source": self.source_name,
                "jobs_found": len(jobs_list),
                "jobs_saved": saved_count,
                "duration": duration,
                "timestamp": datetime.utcnow(),
                "success": True,
                "errors": []
            }
            
            logger.info(f"Daywork123 scraping completed: {len(jobs_list)} found, {saved_count} saved")
            return result
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error in Daywork123 scrape_and_save_jobs: {e}")
            
            return {
                "source": self.source_name,
                "jobs_found": 0,
                "jobs_saved": 0,
                "duration": duration,
                "timestamp": datetime.utcnow(),
                "success": False,
                "errors": [str(e)]
            }