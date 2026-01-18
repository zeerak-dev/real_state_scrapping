#!/usr/bin/env python3
"""
Add sample data to test the dashboard
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_ops

def create_sample_data():
    """Create sample property data for testing"""
    cities = ['Karachi', 'Lahore', 'Islamabad', 'Rawalpindi']
    areas_by_city = {
        'Karachi': ['DHA', 'Clifton', 'Gulshan', 'PECHS', 'Nazimabad'],
        'Lahore': ['DHA', 'Model Town', 'Gulberg', 'Johar Town', 'Cantt'],
        'Islamabad': ['F-6', 'F-7', 'F-8', 'E-7', 'G-9'],
        'Rawalpindi': ['Bahria Town', 'PWD', 'Committee Chowk', 'Saddar', 'Cantt']
    }
    property_types = ['House', 'Apartment', 'Plot', 'Commercial']
    websites = ['zameen.com', 'graana.com']
    
    sample_properties = []
    
    for i in range(50):  # Create 50 sample properties
        city = random.choice(cities)
        area = random.choice(areas_by_city[city])
        prop_type = random.choice(property_types)
        website = random.choice(websites)
        
        # Generate realistic prices based on city and type
        base_prices = {
            'Karachi': {'House': 8000000, 'Apartment': 4000000, 'Plot': 3000000, 'Commercial': 12000000},
            'Lahore': {'House': 6000000, 'Apartment': 3500000, 'Plot': 2500000, 'Commercial': 10000000},
            'Islamabad': {'House': 12000000, 'Apartment': 5000000, 'Plot': 4000000, 'Commercial': 15000000},
            'Rawalpindi': {'House': 5000000, 'Apartment': 3000000, 'Plot': 2000000, 'Commercial': 8000000}
        }
        
        base_price = base_prices[city][prop_type]
        price_variation = random.uniform(0.7, 1.8)  # ±30% to +80%
        price = int(base_price * price_variation)
        
        # Generate other attributes
        bedrooms = random.choice([2, 3, 4, 5]) if prop_type in ['House', 'Apartment'] else None
        bathrooms = random.choice([2, 3, 4]) if bedrooms else None
        area_size = random.randint(800, 2500) if prop_type != 'Plot' else random.randint(5000, 10000)
        
        property_data = {
            'title': f'{bedrooms} Bed {prop_type} in {area}, {city}' if bedrooms else f'{prop_type} in {area}, {city}',
            'city': city,
            'area': area,
            'price_pkr': price,
            'property_type': prop_type,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'area_size': area_size,
            'area_unit': 'sq ft' if prop_type != 'Plot' else 'sq ft',
            'price_per_sqft': price / area_size if area_size else None,
            'agent_name': f'Agent {random.randint(1, 20)}',
            'contact_phone': f'0300-{random.randint(1000000, 9999999)}',
            'source_website': website,
            'source_url': f'https://{website}/property/{i+1000}',
            'date_posted': datetime.now() - timedelta(days=random.randint(1, 30)),
            'date_scraped': datetime.now()
        }
        
        sample_properties.append(property_data)
    
    return sample_properties

def main():
    print("Creating sample data for testing...")
    
    try:
        # Ensure database is initialized
        db_ops.create_tables()
        
        # Create and insert sample data
        sample_properties = create_sample_data()
        inserted, duplicates = db_ops.bulk_insert_properties(sample_properties)
        
        print(f"✓ Inserted {inserted} sample properties")
        print(f"  ({duplicates} duplicates skipped)")
        
        # Show some statistics
        stats = db_ops.get_price_statistics()
        print(f"\n📊 Database now contains data for {len(stats)} cities:")
        for stat in stats:
            print(f"  - {stat['city']}: {stat['total_properties']} properties, Avg: PKR {stat['avg_price']:,.0f}")
        
        print(f"\n🎉 Sample data created successfully!")
        print(f"You can now run the dashboard: streamlit run dashboard/app.py")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()