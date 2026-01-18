# API Documentation & Usage Guide

## 📚 Complete API Documentation

### Overview
This document provides comprehensive documentation for all components of the Pakistan Real Estate Analytics system, including APIs, command-line interfaces, and programmatic usage.

## 🖥️ Command Line Interface (CLI)

### Main Application Commands

#### Database Operations
```bash
# Initialize database and create tables
python main.py init

# View database statistics
python main.py stats
```

#### Scraping Operations
```bash
# Scrape from all websites (default 5 pages per city)
python main.py scrape

# Scrape from specific websites
python main.py scrape --websites zameen graana

# Limit pages per city
python main.py scrape --pages 3

# Scrape from single website with custom pages
python main.py scrape --websites zameen --pages 2
```

#### Data Export
```bash
# Export all data to CSV
python main.py export

# Export with custom filename
python main.py export --filename my_properties.csv

# Export specific city data
python main.py export --city Karachi --filename karachi_data.csv
```

### Scheduler Commands
```bash
# Run scraping job once immediately
python scheduler.py --run-once

# Start daily automated scheduler (runs at 2:00 AM)
python scheduler.py --schedule
```

### Utility Scripts
```bash
# Display formatted statistics
python show_stats.py

# Create sample data for testing
python create_sample_data.py

# Test database configuration
python test_db.py

# Run comprehensive system test
python quick_test.py
```

### Dashboard
```bash
# Start interactive web dashboard
streamlit run dashboard/app.py

# Start dashboard on specific port
streamlit run dashboard/app.py --server.port 8080

# Start dashboard without browser auto-open
streamlit run dashboard/app.py --server.headless true
```

## 🐍 Python API Usage

### Database Operations API

#### Basic Database Setup
```python
from database import db_ops, db_manager

# Initialize database
db_ops.create_tables()

# Get database session
session = db_manager.get_session()
```

#### Property Data Operations
```python
from database.operations import db_ops

# Insert single property
property_data = {
    'title': '3 Bed House in DHA',
    'city': 'Karachi',
    'price_pkr': 5000000,
    'property_type': 'House',
    'bedrooms': 3,
    'area_size': 1200,
    'source_website': 'zameen.com'
}
property_id = db_ops.insert_property(property_data)

# Bulk insert properties
properties_list = [property_data1, property_data2, ...]
inserted_count, duplicate_count = db_ops.bulk_insert_properties(properties_list)

# Get properties by city
karachi_properties = db_ops.get_properties_by_city('Karachi', limit=50)

# Search properties with filters
filtered_properties = db_ops.search_properties(
    city='Karachi',
    property_type='House',
    min_price=3000000,
    max_price=10000000,
    bedrooms=3,
    limit=20
)

# Get price statistics
stats = db_ops.get_price_statistics()
for stat in stats:
    print(f"{stat['city']}: {stat['avg_price']:,.0f} PKR")

# Get top expensive areas
top_areas = db_ops.get_top_expensive_areas(limit=10)
```

### Scraping API

#### Zameen.com Scraper
```python
from scrapers import ZameenScraper

# Initialize scraper
scraper = ZameenScraper()

# Scrape specific city
karachi_properties = scraper.scrape_property_listings('Karachi', max_pages=3)

# Scrape all target cities
all_properties = scraper.scrape_all_cities(max_pages_per_city=2)

# Clean up
scraper.close()
```

#### Graana.com Scraper
```python
from scrapers import GraanaScraper

# Initialize scraper
scraper = GraanaScraper()

# Scrape properties
lahore_properties = scraper.scrape_property_listings('Lahore', max_pages=2)

# Close scraper session
scraper.close()
```

### Data Cleaning API

#### Clean Property Data
```python
from data_cleaning import data_cleaner

# Clean single property
property_data = {
    'title': 'Beautiful House',
    'price_raw': '1.5 Crore',
    'area_raw': '10 Marla',
    'city': 'karachi'
}

cleaned_property = data_cleaner.clean_single_property(property_data)
print(f"Cleaned price: {cleaned_property['price_pkr']}")  # 15000000
print(f"Cleaned area: {cleaned_property['area_size']}")   # 2722.5 sq ft

# Clean multiple properties
raw_properties = [property1, property2, property3]
cleaned_properties = data_cleaner.clean_properties_data(raw_properties)

# Generate cleaning report
report = data_cleaner.generate_cleaning_report(raw_properties, cleaned_properties)
print(f"Cleaned {report['cleaned_count']} properties")
print(f"Average quality score: {report['quality_stats']['average_quality']}")
```

### Configuration API

#### Settings Management
```python
from config.settings import Config, setup_logging

# Initialize configuration
config = Config()

# Access settings
print(f"Database type: {config.DB_TYPE}")
print(f"Target cities: {config.TARGET_CITIES}")
print(f"Scraping delay: {config.SCRAPING_DELAY_MIN}-{config.SCRAPING_DELAY_MAX}s")

# Setup logging
logger = setup_logging()
logger.info("Application started")
```

## 📊 Dashboard API

### Programmatic Dashboard Access
```python
from dashboard.app import DashboardApp

# Initialize dashboard
app = DashboardApp()

# Load property data
df = app.load_property_data()

# Get summary statistics
stats = app.get_summary_stats(df)

# Create charts programmatically
price_chart = app.create_price_distribution_chart(df, city_filter='Karachi')
city_chart = app.create_city_comparison_chart(df)
areas_chart = app.create_top_areas_chart(df, limit=10)
type_chart = app.create_property_type_chart(df)
```

## 🔧 Configuration Options

### Environment Variables (.env)
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=real_estate_pakistan
DB_USER=postgres
DB_PASSWORD=your_password
DB_TYPE=postgresql  # or sqlite, mysql

# Scraping Configuration
SCRAPING_DELAY_MIN=2        # Minimum delay between requests (seconds)
SCRAPING_DELAY_MAX=5        # Maximum delay between requests (seconds)
MAX_RETRIES=3               # Maximum retry attempts
REQUEST_TIMEOUT=30          # Request timeout (seconds)

# Scheduling
SCHEDULE_HOUR=2             # Daily scraping hour (24-hour format)
SCHEDULE_MINUTE=0           # Daily scraping minute

# Logging
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
LOG_FILE_MAX_SIZE=10485760  # 10MB
LOG_FILE_BACKUP_COUNT=5
```

### Advanced Configuration
```python
# Custom scraper settings
scraper_config = {
    'user_agents': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    ],
    'target_cities': ['Karachi', 'Lahore', 'Islamabad'],
    'request_delay': (2, 5),
    'max_retries': 3,
    'timeout': 30
}
```

## 📈 Analytics API Examples

### Price Analysis
```python
# Calculate price statistics
def analyze_prices(city=None):
    if city:
        properties = db_ops.get_properties_by_city(city, limit=1000)
    else:
        # Get all properties logic here
        pass
    
    prices = [p.price_pkr for p in properties if p.price_pkr]
    
    if prices:
        import statistics
        return {
            'count': len(prices),
            'average': statistics.mean(prices),
            'median': statistics.median(prices),
            'min': min(prices),
            'max': max(prices),
            'std_dev': statistics.stdev(prices) if len(prices) > 1 else 0
        }

# Usage
karachi_analysis = analyze_prices('Karachi')
print(f"Average price in Karachi: PKR {karachi_analysis['average']:,.0f}")
```

### Market Trends
```python
# Analyze market trends over time
def analyze_trends():
    from datetime import datetime, timedelta
    import pandas as pd
    
    # Get properties from last 30 days
    cutoff_date = datetime.now() - timedelta(days=30)
    
    session = db_manager.get_session()
    recent_properties = session.query(PropertyListing).filter(
        PropertyListing.date_scraped >= cutoff_date,
        PropertyListing.is_duplicate == False,
        PropertyListing.price_pkr.isnot(None)
    ).all()
    session.close()
    
    # Convert to pandas DataFrame for analysis
    data = [{
        'date': p.date_scraped.date(),
        'city': p.city,
        'price': p.price_pkr,
        'property_type': p.property_type
    } for p in recent_properties]
    
    df = pd.DataFrame(data)
    
    # Daily average prices
    daily_avg = df.groupby('date')['price'].mean()
    
    return daily_avg

# Usage
trends = analyze_trends()
print("Recent price trends:")
for date, price in trends.items():
    print(f"{date}: PKR {price:,.0f}")
```

## 🛠️ Error Handling

### Exception Types
```python
# Custom exceptions (you can add these to your code)
class ScrapingError(Exception):
    """Raised when scraping fails"""
    pass

class DataCleaningError(Exception):
    """Raised when data cleaning fails"""
    pass

class DatabaseError(Exception):
    """Raised when database operations fail"""
    pass

# Usage example
try:
    properties = scraper.scrape_all_cities()
    cleaned_properties = data_cleaner.clean_properties_data(properties)
    inserted, duplicates = db_ops.bulk_insert_properties(cleaned_properties)
except ScrapingError as e:
    logger.error(f"Scraping failed: {e}")
except DataCleaningError as e:
    logger.error(f"Data cleaning failed: {e}")
except DatabaseError as e:
    logger.error(f"Database error: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

## 📝 Logging and Monitoring

### Logging Usage
```python
import logging
from config.settings import setup_logging

# Setup logging
logger = setup_logging()

# Log levels
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")

# Structured logging
logger.info("Scraping completed", extra={
    'website': 'zameen.com',
    'properties_found': 150,
    'duration_seconds': 45.2
})
```

### Performance Monitoring
```python
import time
from datetime import datetime

def monitor_scraping_performance(func):
    """Decorator to monitor scraping performance"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_datetime = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            status = 'success'
            error_msg = None
        except Exception as e:
            result = None
            status = 'failed'
            error_msg = str(e)
            raise
        finally:
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"Function {func.__name__} completed", extra={
                'status': status,
                'duration_seconds': duration,
                'start_time': start_datetime.isoformat(),
                'error': error_msg
            })
        
        return result
    return wrapper

# Usage
@monitor_scraping_performance
def scrape_with_monitoring():
    return scraper.scrape_all_cities()
```

## 🔍 Testing API

### Unit Testing Examples
```python
import unittest
from database import db_ops
from data_cleaning import data_cleaner

class TestDataCleaning(unittest.TestCase):
    
    def test_price_normalization(self):
        """Test price normalization"""
        test_cases = [
            ('1.5 Crore', 15000000),
            ('50 Lakh', 5000000),
            ('500 Thousand', 500000)
        ]
        
        for input_price, expected_output in test_cases:
            result = data_cleaner.normalize_price(input_price)
            self.assertEqual(result, expected_output)
    
    def test_area_normalization(self):
        """Test area normalization to sq ft"""
        test_cases = [
            ('10 Marla', 2722.5),
            ('1 Kanal', 5445),
            ('1200 sq ft', 1200)
        ]
        
        for input_area, expected_output in test_cases:
            result = data_cleaner.normalize_area(input_area)
            self.assertAlmostEqual(result, expected_output, places=1)

if __name__ == '__main__':
    unittest.main()
```

## 🚀 Deployment Examples

### Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "dashboard/app.py", "--server.address", "0.0.0.0"]
```

### Production Deployment
```bash
# Production setup script
#!/bin/bash

# Install system dependencies
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib python3-pip

# Create database
sudo -u postgres createdb real_estate_pakistan

# Install Python dependencies
pip3 install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with production values

# Initialize database
python3 main.py init

# Setup systemd service for scheduler
sudo cp deployment/real-estate-scheduler.service /etc/systemd/system/
sudo systemctl enable real-estate-scheduler
sudo systemctl start real-estate-scheduler

# Setup nginx for dashboard
sudo cp deployment/nginx.conf /etc/nginx/sites-available/real-estate-dashboard
sudo ln -s /etc/nginx/sites-available/real-estate-dashboard /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

This API documentation provides comprehensive guidance for using all components of the Pakistan Real Estate Analytics system programmatically and through command-line interfaces.