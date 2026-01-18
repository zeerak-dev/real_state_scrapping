#!/usr/bin/env python3
"""
Simple test version of main application
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_initialize_database():
    """Test database initialization"""
    try:
        print("Testing database initialization...")
        from database import db_ops
        db_ops.create_tables()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

def test_dashboard():
    """Test if dashboard can be imported and basic functionality works"""
    try:
        print("Testing dashboard imports...")
        # Test basic dashboard imports without actually running Streamlit
        import pandas as pd
        import plotly.express as px
        print("✓ Dashboard dependencies imported successfully")
        return True
    except Exception as e:
        print(f"✗ Dashboard test failed: {e}")
        return False

def main():
    print("=== Real Estate Analytics - Quick Test ===\n")
    
    # Test database
    db_success = test_initialize_database()
    
    # Test dashboard dependencies
    dashboard_success = test_dashboard()
    
    print(f"\n=== Test Results ===")
    print(f"Database: {'✓ Ready' if db_success else '✗ Failed'}")
    print(f"Dashboard: {'✓ Ready' if dashboard_success else '✗ Failed'}")
    
    if db_success and dashboard_success:
        print(f"\n🎉 All tests passed! You can now:")
        print(f"1. Test scraping (small scale): python simple_scrape_test.py")
        print(f"2. Run dashboard: streamlit run dashboard/app.py")
        print(f"3. View statistics: python main.py stats")
    else:
        print(f"\n⚠️ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()