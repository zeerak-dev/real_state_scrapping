import time
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import RealEstateAnalytics
from config.settings import setup_logging, Config

logger = setup_logging()

class ScheduledScraper:
    def __init__(self):
        self.config = Config()
        self.app = RealEstateAnalytics()
        self.scheduler = BlockingScheduler()
        
    def daily_scraping_job(self):
        """Daily scraping job"""
        try:
            logger.info("Starting scheduled scraping job...")
            
            # Initialize database if needed
            self.app.initialize_database()
            
            # Scrape data from all websites
            properties = self.app.scrape_data(['zameen', 'graana'], max_pages=3)
            
            # Clean and save data
            saved_count = self.app.clean_and_save_data(properties)
            
            logger.info(f"Scheduled scraping completed. {saved_count} properties saved.")
            
            # Generate statistics
            self.app.get_statistics()
            
        except Exception as e:
            logger.error(f"Error in scheduled scraping job: {str(e)}")
    
    def setup_scheduler(self):
        """Setup the scheduler with daily job"""
        # Schedule daily scraping at configured time
        self.scheduler.add_job(
            self.daily_scraping_job,
            CronTrigger(
                hour=self.config.SCHEDULE_HOUR,
                minute=self.config.SCHEDULE_MINUTE,
                timezone='Asia/Karachi'
            ),
            id='daily_scraping',
            name='Daily Property Scraping',
            replace_existing=True
        )
        
        logger.info(f"Scheduler configured to run daily at {self.config.SCHEDULE_HOUR:02d}:{self.config.SCHEDULE_MINUTE:02d} PKT")
    
    def run_scheduler(self):
        """Run the scheduler"""
        try:
            logger.info("Starting scheduler...")
            self.setup_scheduler()
            
            # Print next scheduled run
            next_run = self.scheduler.get_jobs()[0].next_run_time
            logger.info(f"Next scheduled run: {next_run}")
            
            # Start the scheduler
            self.scheduler.start()
            
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            self.scheduler.shutdown()
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")
            self.scheduler.shutdown()

def run_once():
    """Run scraping job once immediately"""
    logger.info("Running scraping job immediately...")
    scraper = ScheduledScraper()
    scraper.daily_scraping_job()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Real Estate Scraping Scheduler')
    parser.add_argument('--run-once', action='store_true', 
                       help='Run scraping job once immediately')
    parser.add_argument('--schedule', action='store_true',
                       help='Start the scheduler for daily runs')
    
    args = parser.parse_args()
    
    if args.run_once:
        run_once()
    elif args.schedule:
        scraper = ScheduledScraper()
        scraper.run_scheduler()
    else:
        print("Usage:")
        print("  --run-once    Run scraping job immediately")
        print("  --schedule    Start scheduler for daily runs")

if __name__ == "__main__":
    main()