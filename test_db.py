#!/usr/bin/env python3
"""
Simple test script to verify database configuration
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("=== Testing Database Configuration ===")
    
    # Test imports
    print("1. Testing imports...")
    from config.settings import Config, setup_logging
    from database.models import db_manager, PropertyListing, ScrapingSession
    from database.operations import db_ops
    print("✓ All imports successful")
    
    # Test configuration
    print("\n2. Testing configuration...")
    config = Config()
    print(f"✓ Database type: {os.getenv('DB_TYPE', 'not set')}")
    print(f"✓ Database name: {os.getenv('DB_NAME', 'not set')}")
    
    # Test database connection
    print("\n3. Testing database connection...")
    db_config = db_manager.config
    connection_string = db_config.get_connection_string()
    print(f"✓ Connection string: {connection_string}")
    
    # Create tables
    print("\n4. Creating database tables...")
    db_ops.create_tables()
    print("✓ Database tables created successfully")
    
    # Test basic database operations
    print("\n5. Testing database operations...")
    
    # Insert a test property
    test_property = {
        'title': 'Test Property',
        'city': 'Karachi',
        'area': 'Test Area',
        'price_pkr': 5000000,
        'property_type': 'House',
        'bedrooms': 3,
        'bathrooms': 2,
        'area_size': 1200,
        'source_website': 'test.com',
        'source_url': 'https://test.com/property/1'
    }
    
    property_id = db_ops.insert_property(test_property)
    if property_id:
        print(f"✓ Test property inserted with ID: {property_id}")
        
        # Test statistics
        stats = db_ops.get_price_statistics()
        print(f"✓ Price statistics retrieved: {len(stats)} cities")
        
        print("\n=== Database Setup Complete! ===")
        print("Your database is ready for the real estate scraper.")
    else:
        print("✗ Failed to insert test property")
        
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()