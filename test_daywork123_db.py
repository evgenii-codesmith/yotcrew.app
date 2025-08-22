#!/usr/bin/env python3
"""
Test script for Daywork123Scraper database saving functionality
"""
import asyncio
import logging
import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.database import engine, Base, SessionLocal
from app.models import Job
from app.scrapers.daywork123 import Daywork123Scraper
from app.scrapers.base import UniversalJob, JobSource, EmploymentType, Department, VesselType

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_database():
    """Create database tables if they don't exist"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise

def test_job_saving():
    """Test saving UniversalJob objects to database"""
    logger.info("Testing job saving functionality...")
    
    # Create test jobs
    test_jobs = [
        UniversalJob(
            external_id="test_dw123_001",
            title="Test Captain Position",
            company="Test Yacht Company",
            source=JobSource.DAYWORK123,
            source_url="https://www.daywork123.com/test",
            location="Monaco",
            description="Test captain position for testing database saving",
            employment_type=EmploymentType.PERMANENT,
            department=Department.DECK,
            vessel_type=VesselType.MOTOR_YACHT,
            vessel_size="50-74m",
            salary_range="€8,000 - €12,000/month",
            salary_currency="EUR",
            posted_date=datetime.utcnow(),
            requirements=["Valid certificates", "5+ years experience"],
            benefits=["Competitive salary", "Travel opportunities"],
            quality_score=0.85,
            raw_data={"test": True, "source": "unit_test"}
        ),
        UniversalJob(
            external_id="test_dw123_002", 
            title="Test Chief Engineer",
            company="Test Marine Services",
            source=JobSource.DAYWORK123,
            source_url="https://www.daywork123.com/test2",
            location="Fort Lauderdale",
            description="Test chief engineer position for testing",
            employment_type=EmploymentType.ROTATIONAL,
            department=Department.ENGINEERING,
            vessel_type=VesselType.SUPER_YACHT,
            vessel_size="75m+",
            salary_range="$7,000 - $10,000/month",
            salary_currency="USD",
            posted_date=datetime.utcnow(),
            requirements=["Engineering degree", "Marine experience"],
            benefits=["Health insurance", "Rotation schedule"],
            quality_score=0.90,
            raw_data={"test": True, "source": "unit_test"}
        )
    ]
    
    # Test saving jobs
    scraper = Daywork123Scraper()
    
    async def run_test():
        saved_count = await scraper.save_jobs_to_db(test_jobs)
        logger.info(f"Saved {saved_count} test jobs to database")
        return saved_count
    
    return asyncio.run(run_test())

def verify_database_content():
    """Verify that jobs were saved correctly"""
    logger.info("Verifying database content...")
    
    with SessionLocal() as db:
        # Count total jobs
        total_jobs = db.query(Job).count()
        logger.info(f"Total jobs in database: {total_jobs}")
        
        # Count Daywork123 jobs
        dw123_jobs = db.query(Job).filter(Job.source == JobSource.DAYWORK123).count()
        logger.info(f"Daywork123 jobs in database: {dw123_jobs}")
        
        # Get test jobs
        test_jobs = db.query(Job).filter(Job.external_id.like("test_dw123_%")).all()
        logger.info(f"Test jobs found: {len(test_jobs)}")
        
        for job in test_jobs:
            logger.info(f"  - {job.title} ({job.external_id}) - Quality: {job.quality_score}")
        
        return len(test_jobs)

def test_duplicate_handling():
    """Test that duplicate jobs are handled correctly"""
    logger.info("Testing duplicate job handling...")
    
    # Create a duplicate job
    duplicate_job = UniversalJob(
        external_id="test_dw123_001",  # Same as first test job
        title="Updated Test Captain Position",  # Updated title
        company="Updated Test Yacht Company",  # Updated company
        source=JobSource.DAYWORK123,
        source_url="https://www.daywork123.com/test_updated",
        location="Monte Carlo",  # Updated location
        description="Updated test captain position description",
        employment_type=EmploymentType.PERMANENT,
        department=Department.DECK,
        vessel_type=VesselType.MOTOR_YACHT,
        vessel_size="50-74m",
        salary_range="€9,000 - €13,000/month",  # Updated salary
        salary_currency="EUR",
        posted_date=datetime.utcnow(),
        requirements=["Valid certificates", "7+ years experience"],  # Updated requirements
        benefits=["Competitive salary", "Travel opportunities", "Health insurance"],
        quality_score=0.90,  # Updated score
        raw_data={"test": True, "source": "duplicate_test", "updated": True}
    )
    
    scraper = Daywork123Scraper()
    
    async def run_duplicate_test():
        saved_count = await scraper.save_jobs_to_db([duplicate_job])
        logger.info(f"Processed {saved_count} duplicate job")
        return saved_count
    
    return asyncio.run(run_duplicate_test())

def test_real_scraping(max_pages=1):
    """Test real scraping and database saving (optional)"""
    logger.info(f"Testing real scraping with {max_pages} page(s)...")
    
    scraper = Daywork123Scraper()
    
    async def run_real_test():
        try:
            # Test connection first
            if not await scraper.test_connection():
                logger.warning("Cannot connect to Daywork123.com - skipping real scraping test")
                return {"success": False, "reason": "connection_failed"}
            
            # Run scraping with database saving
            result = await scraper.scrape_and_save_jobs(max_pages=max_pages)
            logger.info(f"Real scraping result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in real scraping test: {e}")
            return {"success": False, "error": str(e)}
    
    return asyncio.run(run_real_test())

def cleanup_test_data():
    """Clean up test data from database"""
    logger.info("Cleaning up test data...")
    
    with SessionLocal() as db:
        # Delete test jobs
        deleted_count = db.query(Job).filter(Job.external_id.like("test_dw123_%")).delete()
        db.commit()
        logger.info(f"Deleted {deleted_count} test jobs")
        return deleted_count

def main():
    """Main test function"""
    logger.info("=== Daywork123Scraper Database Saving Tests ===")
    
    try:
        # Setup
        logger.info("1. Setting up database...")
        setup_database()
        
        # Test 1: Basic job saving
        logger.info("\n2. Testing job saving...")
        saved_count = test_job_saving()
        assert saved_count == 2, f"Expected 2 jobs saved, got {saved_count}"
        
        # Test 2: Verify database content
        logger.info("\n3. Verifying database content...")
        test_jobs_count = verify_database_content()
        assert test_jobs_count >= 2, f"Expected at least 2 test jobs, found {test_jobs_count}"
        
        # Test 3: Duplicate handling
        logger.info("\n4. Testing duplicate job handling...")
        duplicate_result = test_duplicate_handling()
        assert duplicate_result == 1, f"Expected 1 duplicate processed, got {duplicate_result}"
        
        # Verify duplicate was updated, not added
        with SessionLocal() as db:
            updated_job = db.query(Job).filter(Job.external_id == "test_dw123_001").first()
            assert updated_job is not None, "Updated job not found"
            assert "Updated" in updated_job.title, "Job was not updated properly"
            assert updated_job.salary_range == "€9,000 - €13,000/month", "Salary was not updated"
            logger.info("✓ Duplicate handling works correctly")
        
        # Test 4: Real scraping (optional)
        user_input = input("\nDo you want to test real scraping from Daywork123.com? (y/N): ").strip().lower()
        if user_input in ['y', 'yes']:
            logger.info("\n5. Testing real scraping...")
            real_result = test_real_scraping(max_pages=1)
            if real_result.get("success"):
                logger.info(f"✓ Real scraping successful: {real_result['jobs_found']} jobs found, {real_result['jobs_saved']} saved")
            else:
                logger.warning(f"Real scraping failed or skipped: {real_result}")
        
        # Final verification
        logger.info("\n6. Final database verification...")
        final_count = verify_database_content()
        
        logger.info(f"\n=== All Tests Completed Successfully ===")
        logger.info(f"Database contains {final_count} test jobs")
        
        # Cleanup
        cleanup_choice = input("\nDo you want to clean up test data? (Y/n): ").strip().lower()
        if cleanup_choice not in ['n', 'no']:
            cleanup_test_data()
            logger.info("Test data cleaned up")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise
    except AssertionError as e:
        logger.error(f"Assertion failed: {e}")
        raise

if __name__ == "__main__":
    main()

