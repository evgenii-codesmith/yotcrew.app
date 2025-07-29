"""Yotspot.com scraper refactored for pluggable architecture"""
import asyncio
import logging
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime
import re
from urllib.parse import urljoin

from .base import BaseScraper, UniversalJob, JobSource, EmploymentType, Department, VesselType
from .registry import register_scraper

logger = logging.getLogger(__name__)

@register_scraper
class YotspotScraper(BaseScraper):
    """Refactored Yotspot.com scraper implementing pluggable interface"""
    
    def __init__(self):
        self.config = {
            'max_retries': 3,
            'request_delay': 2.0,
            'timeout': 30,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        }
    
    @property
    def source_name(self) -> str:
        return JobSource.YOTSPOT
    
    @property
    def base_url(self) -> str:
        return "https://www.yotspot.com"
    
    async def scrape_jobs(self, max_pages: int = 5, filters: Optional[Dict[str, Any]] = None):
        """Scrape jobs from Yotspot.com using aiohttp"""
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config['timeout']),
            headers=self.config['headers']
        ) as session:
            
            for page in range(1, max_pages + 1):
                logger.info(f"Scraping Yotspot page {page}")
                
                try:
                    jobs = await self._scrape_page(session, page, filters)
                    for job in jobs:
                        yield self._normalize_job(job)
                        
                    # Add delay between pages
                    if page < max_pages:
                        await asyncio.sleep(self.config['request_delay'])
                        
                except Exception as e:
                    logger.error(f"Error scraping page {page}: {e}")
                    continue
    
    async def _scrape_page(self, session: aiohttp.ClientSession, page: int, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Scrape a single page of job listings"""
        url = f"{self.base_url}/job-search.html?page={page}"
        
        # Add filters to URL if provided
        if filters:
            params = []
            if filters.get('location'):
                params.append(f"location={filters['location']}")
            if filters.get('department'):
                params.append(f"department={filters['department']}")
            if params:
                url += "&" + "&".join(params)
        
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"HTTP {response.status} for {url}")
                    return []
                
                html = await response.text()
                return await self._parse_job_listings(html)
                
        except Exception as e:
            logger.error(f"Error fetching page {page}: {e}")
            return []
    
    async def _parse_job_listings(self, html: str) -> List[Dict[str, Any]]:
        """Parse job listings from HTML"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            jobs = []
            job_cards = soup.find_all('div', class_='job-item')
            
            if not job_cards:
                # Try alternative selectors
                job_cards = soup.find_all('div', class_=re.compile(r'job-listing|job-card'))
                if not job_cards:
                    job_cards = soup.find_all('article', class_=re.compile(r'job'))
                    if not job_cards:
                        job_cards = soup.find_all('div', attrs={'data-job-id': True})
            
            for card in job_cards:
                job_data = self._extract_job_data(card)
                if job_data:
                    jobs.append(job_data)
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error parsing job listings: {e}")
            return []
    
    def _extract_job_data(self, card) -> Optional[Dict[str, Any]]:
        """Extract job data from a single job card"""
        try:
            job_data = {}
            
            # Job title and URL - look for the position link
            title_elem = card.find('div', class_='job-item__position')
            if title_elem:
                title_link = title_elem.find('a')
                if title_link:
                    job_data['title'] = title_link.get_text(strip=True)
                    job_data['url'] = urljoin(self.base_url, title_link.get('href', ''))
                else:
                    return None
            else:
                return None
            
            # Company name - default for yotspot
            job_data['company'] = "Yotspot"
            
            # Location - extract from job-item__info
            location = "Unknown"
            info_list = card.find('ul', class_='job-item__info')
            if info_list:
                info_items = info_list.find_all('li')
                for item in info_items:
                    item_text = item.get_text(strip=True)
                    # Look for location patterns
                    if any(loc in item_text.lower() for loc in ['miami', 'fort lauderdale', 'caribbean', 'mediterranean', 'europe']):
                        location = item_text
                        break
            
            job_data['location'] = location
            
            # Job type - extract from job-item__info
            job_type = None
            if info_list:
                for item in info_list.find_all('li'):
                    item_text = item.get_text(strip=True)
                    if any(type_word in item_text.lower() for type_word in ['permanent', 'temporary', 'contract', 'seasonal']):
                        job_type = item_text
                        break
            
            job_data['job_type'] = job_type
            
            # Posted date - extract from job-item__info
            posted_date = None
            if info_list:
                for item in info_list.find_all('li'):
                    item_text = item.get_text(strip=True)
                    if 'posted' in item_text.lower() or any(date_indicator in item_text.lower() for date_indicator in ['2024', '2025', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']):
                        posted_date = self._parse_date(item_text)
                        break
            
            job_data['posted_date'] = posted_date
            
            # Salary - extract from job-item__info
            salary = None
            if info_list:
                for item in info_list.find_all('li'):
                    item_text = item.get_text(strip=True)
                    if any(currency in item_text.lower() for currency in ['eur', 'usd', 'gbp', '€', '$', '£']):
                        salary = item_text
                        break
            
            job_data['salary'] = salary
            
            # Description - use title as description for now
            job_data['description'] = job_data.get('title', '')
            
            # Extract job ID from URL
            job_data['external_id'] = self._extract_job_id(job_data.get('url', ''))
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error extracting job data: {e}")
            return None
    
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
        
        try:
            from dateparser import parse
            return parse(date_text, settings={'RETURN_AS_TIMEZONE_AWARE': False})
        except:
            return datetime.utcnow()
    
    def _normalize_job(self, raw_job: Dict[str, Any]) -> UniversalJob:
        """Convert raw job data to UniversalJob format"""
        # Parse employment type
        employment_type = self._detect_employment_type(raw_job.get('job_type', ''))
        
        # Parse department
        department = self._detect_department(raw_job.get('title', ''))
        
        # Parse vessel type
        vessel_type = self._detect_vessel_type(raw_job.get('description', ''))
        
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
            description=raw_job.get('description', ''),
            posted_date=raw_job.get('posted_date'),
            quality_score=quality_score,
            raw_data=raw_job
        )
    
    def _detect_employment_type(self, job_type: str) -> Optional[EmploymentType]:
        """Detect employment type from job type text"""
        job_type_lower = job_type.lower() if job_type else ""
        
        if 'permanent' in job_type_lower:
            return EmploymentType.PERMANENT
        elif 'temporary' in job_type_lower:
            return EmploymentType.TEMPORARY
        elif 'rotational' in job_type_lower:
            return EmploymentType.ROTATIONAL
        elif 'seasonal' in job_type_lower:
            return EmploymentType.SEASONAL
        elif 'contract' in job_type_lower:
            return EmploymentType.CONTRACT
        else:
            return EmploymentType.PERMANENT
    
    def _detect_department(self, title: str) -> Optional[Department]:
        """Detect department from job title"""
        title_lower = title.lower() if title else ""
        
        deck_keywords = ['deckhand', 'bosun', 'mate', 'captain', 'officer', 'deck', 'skipper']
        interior_keywords = ['stewardess', 'steward', 'interior', 'housekeeping', 'butler', 'chief stewardess']
        engineering_keywords = ['engineer', 'mechanic', 'eto', 'technical', 'chief engineer']
        galley_keywords = ['chef', 'cook', 'galley', 'kitchen', 'sous chef', 'head chef']
        
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
    
    def _detect_vessel_type(self, description: str) -> Optional[VesselType]:
        """Detect vessel type from description"""
        desc_lower = description.lower() if description else ""
        
        if 'sailing' in desc_lower or 'sail' in desc_lower:
            return VesselType.SAILING_YACHT
        elif 'catamaran' in desc_lower:
            return VesselType.CATAMARAN
        elif 'superyacht' in desc_lower or 'super yacht' in desc_lower:
            return VesselType.SUPER_YACHT
        elif 'expedition' in desc_lower:
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
        if len(description) > 200:
            score += 0.2
        elif len(description) > 100:
            score += 0.1
        
        return min(1.0, score)
    
    async def test_connection(self) -> bool:
        """Test Yotspot.com accessibility"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, timeout=10) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_supported_filters(self) -> List[str]:
        """Return supported filter parameters"""
        return ["location", "department", "vessel_type", "salary_range", "experience_level"]