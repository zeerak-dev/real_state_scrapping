#!/usr/bin/env python3
"""
Pakistan Real Estate Analytics Dashboard
Main application file for scraping, cleaning, and managing property data
"""

import argparse
import logging
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import setup_logging, Config
from scrapers import ZameenScraper, GraanaScraper
from data_cleaning import data_cleaner
from database import db_ops, db_manager

# Setup logging
logger = setup_logging()

class RealEstateAnalytics:
    def __init__(self):
        self.config = Config()
        self.scrapers = {
            'zameen': ZameenScraper(),
            'graana': GraanaScraper()
        }
        
    def initialize_database(self):
        """Initialize the database and create tables"""
        try:
            logger.info("Initializing database...")
            db_ops.create_tables()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def scrape_data(self, websites=None, max_pages=5):
        """Scrape data from specified websites"""
        if websites is None:
            websites = ['zameen', 'graana']
        
        all_properties = []
        
        for website in websites:
            if website not in self.scrapers:
                logger.warning(f"Unknown website: {website}")
                continue
                
            try:
                logger.info(f"Starting scraping from {website}.com")
                
                # Create scraping session record
                session_id = db_ops.create_scraping_session(website)
                
                # Scrape properties
                scraper = self.scrapers[website]
                properties = scraper.scrape_all_cities(max_pages_per_city=max_pages)
                
                # Update session with results
                db_ops.update_scraping_session(
                    session_id,
                    properties_scraped=len(properties),
                    status='completed',
                    end_time=datetime.utcnow()
                )
                
                all_properties.extend(properties)
                logger.info(f"Scraped {len(properties)} properties from {website}.com")
                
                # Close scraper
                scraper.close()
                
            except Exception as e:
                logger.error(f"Error scraping from {website}: {str(e)}")
                db_ops.update_scraping_session(
                    session_id,
                    status='failed',
                    end_time=datetime.utcnow()
                )
                continue
        
        return all_properties
    
    def clean_and_save_data(self, properties):
        """Clean scraped data and save to database"""
        if not properties:
            logger.warning("No properties to clean")
            return 0
        
        logger.info(f"Cleaning {len(properties)} properties...")
        
        # Clean the data
        cleaned_properties = data_cleaner.clean_properties_data(properties)
        
        # Generate cleaning report
        report = data_cleaner.generate_cleaning_report(properties, cleaned_properties)
        logger.info(f"Cleaning completed. Report: {report}")
        
        # Save to database
        if cleaned_properties:
            inserted, duplicates = db_ops.bulk_insert_properties(cleaned_properties)
            logger.info(f"Saved {inserted} properties to database. {duplicates} duplicates skipped.")
            return inserted
        
        return 0
    
    def export_to_csv(self, filename=None, city_filter=None):
        """Export data to CSV file"""
        if filename is None:
            filename = f"properties_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            import pandas as pd
            
            # Get properties from database
            if city_filter:
                properties = db_ops.get_properties_by_city(city_filter, limit=10000)
            else:
                # Get all properties - we'll need to modify db_ops to support this
                session = db_manager.get_session()
                properties = session.query(db_ops.PropertyListing).filter(
                    db_ops.PropertyListing.is_duplicate == False
                ).limit(10000).all()
                session.close()
            
            if not properties:
                logger.warning("No properties found for export")
                return None
            
            # Convert to DataFrame
            data = []
            for prop in properties:
                data.append({
                    'id': prop.id,
                    'title': prop.title,
                    'city': prop.city,
                    'area': prop.area,
                    'sector_block': prop.sector_block,
                    'price_pkr': prop.price_pkr,
                    'price_per_sqft': prop.price_per_sqft,
                    'property_type': prop.property_type,
                    'bedrooms': prop.bedrooms,
                    'bathrooms': prop.bathrooms,
                    'area_size': prop.area_size,
                    'area_unit': prop.area_unit,
                    'agent_name': prop.agent_name,
                    'contact_phone': prop.contact_phone,
                    'source_website': prop.source_website,
                    'date_scraped': prop.date_scraped,
                    'data_quality_score': prop.data_quality_score
                })
            
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            
            logger.info(f"Exported {len(data)} properties to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            return None
    
    def get_statistics(self):
        """Get database statistics"""
        try:
            stats = db_ops.get_price_statistics()
            top_areas = db_ops.get_top_expensive_areas()
            
            logger.info("=== PROPERTY STATISTICS ===")
            for city_stat in stats:
                logger.info(f"{city_stat['city']}: {city_stat['total_properties']} properties, "
                           f"Avg: PKR {city_stat['avg_price']:,.0f}")
            
            logger.info("\n=== TOP 5 EXPENSIVE AREAS ===")
            for i, area in enumerate(top_areas[:5], 1):
                logger.info(f"{i}. {area['area']}, {area['city']}: PKR {area['avg_price']:,.0f} "
                           f"({area['property_count']} properties)")
            
            return {'city_stats': stats, 'top_areas': top_areas}
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return None

def main():
    parser = argparse.ArgumentParser(description='Pakistan Real Estate Analytics')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Initialize command
    init_parser = subparsers.add_parser('init', help='Initialize database')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape property data')
    scrape_parser.add_argument('--websites', nargs='+', choices=['zameen', 'graana'], 
                              default=['zameen', 'graana'], help='Websites to scrape')
    scrape_parser.add_argument('--pages', type=int, default=5, 
                              help='Maximum pages per city to scrape')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export data to CSV')
    export_parser.add_argument('--filename', help='Output CSV filename')
    export_parser.add_argument('--city', help='Filter by city')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize the application
    app = RealEstateAnalytics()
    
    try:
        if args.command == 'init':
            app.initialize_database()
            logger.info("Database initialization completed")
            
        elif args.command == 'scrape':
            # Initialize database if needed
            app.initialize_database()
            
            # Scrape data
            properties = app.scrape_data(args.websites, args.pages)
            
            # Clean and save data
            saved_count = app.clean_and_save_data(properties)
            
            logger.info(f"Scraping completed. {saved_count} properties saved to database.")
            
        elif args.command == 'export':
            filename = app.export_to_csv(args.filename, args.city)
            if filename:
                print(f"Data exported to: {filename}")
            
        elif args.command == 'stats':
            app.get_statistics()
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()