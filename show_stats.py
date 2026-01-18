#!/usr/bin/env python3
"""
Simple stats viewer for the real estate database
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_ops

def show_statistics():
    """Display database statistics"""
    try:
        print("=== 📊 Pakistan Real Estate Analytics - Statistics ===\n")
        
        # City statistics
        city_stats = db_ops.get_price_statistics()
        print("🏙️  CITY-WISE STATISTICS:")
        print("-" * 60)
        for stat in city_stats:
            print(f"🏠 {stat['city']:<12} | Properties: {stat['total_properties']:>3} | Avg Price: PKR {stat['avg_price']:>12,.0f}")
        
        print(f"\n💰 TOP EXPENSIVE AREAS:")
        print("-" * 60)
        top_areas = db_ops.get_top_expensive_areas(10)
        for i, area in enumerate(top_areas, 1):
            print(f"{i:>2}. {area['area']}, {area['city']:<12} | Avg: PKR {area['avg_price']:>10,.0f} ({area['property_count']} properties)")
        
        # Total summary
        total_properties = sum(stat['total_properties'] for stat in city_stats)
        avg_overall = sum(stat['avg_price'] * stat['total_properties'] for stat in city_stats) / total_properties if total_properties > 0 else 0
        
        print(f"\n📈 OVERALL SUMMARY:")
        print("-" * 60)
        print(f"Total Properties: {total_properties}")
        print(f"Average Price: PKR {avg_overall:,.0f}")
        print(f"Cities Covered: {len(city_stats)}")
        
        print(f"\n✅ Database is working perfectly!")
        print(f"🌐 Dashboard available at: http://localhost:8501")
        
    except Exception as e:
        print(f"Error displaying statistics: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    show_statistics()