import hashlib
import logging
from datetime import datetime
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Tuple
from .models import PropertyListing, ScrapingSession, db_manager

logger = logging.getLogger(__name__)

class DatabaseOperations:
    def __init__(self):
        self.db_manager = db_manager
        
    def create_tables(self):
        """Initialize database tables"""
        try:
            self.db_manager.create_tables()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise
            
    def generate_content_hash(self, property_data: Dict) -> str:
        """Generate a hash for duplicate detection"""
        # Create hash based on key fields that should be unique
        hash_string = f"{property_data.get('title', '')}" \
                     f"{property_data.get('city', '')}" \
                     f"{property_data.get('area', '')}" \
                     f"{property_data.get('price_raw', '')}" \
                     f"{property_data.get('property_type', '')}" \
                     f"{property_data.get('bedrooms', '')}" \
                     f"{property_data.get('area_size', '')}"
        
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def calculate_data_quality_score(self, property_data: Dict) -> float:
        """Calculate data quality score based on field completeness"""
        important_fields = ['title', 'city', 'price_pkr', 'property_type', 'area_size']
        optional_fields = ['area', 'bedrooms', 'bathrooms', 'agent_name', 'contact_phone']
        
        important_score = sum(1 for field in important_fields if property_data.get(field))
        optional_score = sum(1 for field in optional_fields if property_data.get(field))
        
        # Important fields weight 70%, optional fields 30%
        score = (important_score / len(important_fields)) * 0.7 + \
                (optional_score / len(optional_fields)) * 0.3
        
        return round(score, 2)
    
    def insert_property(self, property_data: Dict) -> Optional[int]:
        """Insert a single property listing"""
        session = self.db_manager.get_session()
        try:
            # Generate content hash and quality score
            content_hash = self.generate_content_hash(property_data)
            quality_score = self.calculate_data_quality_score(property_data)
            
            # Check for duplicates
            existing = session.query(PropertyListing).filter_by(content_hash=content_hash).first()
            if existing:
                logger.debug(f"Duplicate property found: {property_data.get('title', 'Unknown')[:50]}")
                return existing.id
            
            # Create new property listing
            property_listing = PropertyListing(
                title=property_data.get('title'),
                city=property_data.get('city'),
                area=property_data.get('area'),
                sector_block=property_data.get('sector_block'),
                full_address=property_data.get('full_address'),
                price_pkr=property_data.get('price_pkr'),
                price_raw=property_data.get('price_raw'),
                price_per_sqft=property_data.get('price_per_sqft'),
                property_type=property_data.get('property_type'),
                bedrooms=property_data.get('bedrooms'),
                bathrooms=property_data.get('bathrooms'),
                area_size=property_data.get('area_size'),
                area_unit=property_data.get('area_unit'),
                area_raw=property_data.get('area_raw'),
                agent_name=property_data.get('agent_name'),
                seller_name=property_data.get('seller_name'),
                contact_phone=property_data.get('contact_phone'),
                contact_email=property_data.get('contact_email'),
                source_website=property_data.get('source_website'),
                source_url=property_data.get('source_url'),
                listing_id=property_data.get('listing_id'),
                date_posted=property_data.get('date_posted'),
                content_hash=content_hash,
                data_quality_score=quality_score
            )
            
            session.add(property_listing)
            session.commit()
            
            logger.info(f"Property inserted: ID {property_listing.id}")
            return property_listing.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting property: {str(e)}")
            return None
        finally:
            session.close()
    
    def bulk_insert_properties(self, properties_data: List[Dict]) -> Tuple[int, int]:
        """Insert multiple properties in bulk"""
        session = self.db_manager.get_session()
        inserted_count = 0
        duplicate_count = 0
        
        try:
            for property_data in properties_data:
                content_hash = self.generate_content_hash(property_data)
                
                # Check for duplicates
                existing = session.query(PropertyListing).filter_by(content_hash=content_hash).first()
                if existing:
                    duplicate_count += 1
                    continue
                
                # Prepare property object
                property_data['content_hash'] = content_hash
                property_data['data_quality_score'] = self.calculate_data_quality_score(property_data)
                
                property_listing = PropertyListing(**property_data)
                session.add(property_listing)
                inserted_count += 1
            
            session.commit()
            logger.info(f"Bulk insert completed: {inserted_count} inserted, {duplicate_count} duplicates")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error in bulk insert: {str(e)}")
        finally:
            session.close()
            
        return inserted_count, duplicate_count
    
    def get_properties_by_city(self, city: str, limit: int = 100) -> List[PropertyListing]:
        """Get properties by city"""
        session = self.db_manager.get_session()
        try:
            properties = session.query(PropertyListing)\
                .filter(PropertyListing.city.ilike(f'%{city}%'))\
                .filter(PropertyListing.is_duplicate == False)\
                .limit(limit).all()
            return properties
        finally:
            session.close()
    
    def get_price_statistics(self) -> Dict:
        """Get price statistics by city"""
        session = self.db_manager.get_session()
        try:
            from sqlalchemy import func
            
            stats = session.query(
                PropertyListing.city,
                func.count(PropertyListing.id).label('total_properties'),
                func.avg(PropertyListing.price_pkr).label('avg_price'),
                func.min(PropertyListing.price_pkr).label('min_price'),
                func.max(PropertyListing.price_pkr).label('max_price')
            ).filter(
                PropertyListing.price_pkr.isnot(None),
                PropertyListing.is_duplicate == False
            ).group_by(PropertyListing.city).all()
            
            return [
                {
                    'city': stat.city,
                    'total_properties': stat.total_properties,
                    'avg_price': float(stat.avg_price) if stat.avg_price else 0,
                    'min_price': float(stat.min_price) if stat.min_price else 0,
                    'max_price': float(stat.max_price) if stat.max_price else 0
                }
                for stat in stats
            ]
        finally:
            session.close()
    
    def get_top_expensive_areas(self, limit: int = 10) -> List[Dict]:
        """Get top expensive areas"""
        session = self.db_manager.get_session()
        try:
            from sqlalchemy import func
            
            areas = session.query(
                PropertyListing.city,
                PropertyListing.area,
                func.avg(PropertyListing.price_pkr).label('avg_price'),
                func.count(PropertyListing.id).label('property_count')
            ).filter(
                PropertyListing.price_pkr.isnot(None),
                PropertyListing.area.isnot(None),
                PropertyListing.is_duplicate == False
            ).group_by(
                PropertyListing.city, PropertyListing.area
            ).having(
                func.count(PropertyListing.id) >= 3  # At least 3 properties for reliable average
            ).order_by(
                func.avg(PropertyListing.price_pkr).desc()
            ).limit(limit).all()
            
            return [
                {
                    'city': area.city,
                    'area': area.area,
                    'avg_price': float(area.avg_price),
                    'property_count': area.property_count
                }
                for area in areas
            ]
        finally:
            session.close()
    
    def search_properties(self, city: str = None, property_type: str = None, 
                         min_price: float = None, max_price: float = None,
                         bedrooms: int = None, limit: int = 50) -> List[PropertyListing]:
        """Search properties with filters"""
        session = self.db_manager.get_session()
        try:
            query = session.query(PropertyListing).filter(PropertyListing.is_duplicate == False)
            
            if city:
                query = query.filter(PropertyListing.city.ilike(f'%{city}%'))
            if property_type:
                query = query.filter(PropertyListing.property_type.ilike(f'%{property_type}%'))
            if min_price:
                query = query.filter(PropertyListing.price_pkr >= min_price)
            if max_price:
                query = query.filter(PropertyListing.price_pkr <= max_price)
            if bedrooms:
                query = query.filter(PropertyListing.bedrooms == bedrooms)
                
            return query.order_by(PropertyListing.date_scraped.desc()).limit(limit).all()
        finally:
            session.close()
    
    def create_scraping_session(self, website: str) -> int:
        """Create a new scraping session"""
        session = self.db_manager.get_session()
        try:
            scraping_session = ScrapingSession(website=website)
            session.add(scraping_session)
            session.commit()
            return scraping_session.id
        finally:
            session.close()
    
    def update_scraping_session(self, session_id: int, **kwargs):
        """Update scraping session"""
        session = self.db_manager.get_session()
        try:
            scraping_session = session.query(ScrapingSession).get(session_id)
            if scraping_session:
                for key, value in kwargs.items():
                    setattr(scraping_session, key, value)
                session.commit()
        finally:
            session.close()

# Global instance
db_ops = DatabaseOperations()