import pandas as pd
import numpy as np
import logging
import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

class DataCleaner:
    def __init__(self):
        # Price conversion mappings
        self.price_patterns = {
            'crore': 10000000,
            'lakh': 100000,
            'thousand': 1000,
            'k': 1000,
            'million': 1000000
        }
        
        # Area conversion to sq ft
        self.area_conversions = {
            'marla': 272.25,
            'kanal': 5445,
            'sq ft': 1,
            'sqft': 1,
            'square feet': 1,
            'sq m': 10.764,  # square meters to sq ft
            'sq meter': 10.764,
            'yard': 9,       # square yards to sq ft
            'acre': 43560    # acres to sq ft
        }
        
        # Property type standardization
        self.property_type_mapping = {
            'house': ['house', 'home', 'bungalow', 'villa', 'cottage', 'townhouse'],
            'apartment': ['apartment', 'flat', 'unit', 'condo'],
            'plot': ['plot', 'land', 'residential plot', 'commercial plot', 'vacant land'],
            'commercial': ['shop', 'office', 'warehouse', 'building', 'commercial space'],
            'farmhouse': ['farmhouse', 'farm house'],
            'penthouse': ['penthouse', 'penthouse apartment'],
            'studio': ['studio', 'studio apartment']
        }
    
    def clean_properties_data(self, properties: List[Dict]) -> List[Dict]:
        """Clean and normalize a list of property dictionaries"""
        logger.info(f"Starting data cleaning for {len(properties)} properties")
        
        cleaned_properties = []
        
        for prop in properties:
            try:
                cleaned_prop = self.clean_single_property(prop)
                if self.is_valid_property(cleaned_prop):
                    cleaned_properties.append(cleaned_prop)
            except Exception as e:
                logger.error(f"Error cleaning property {prop.get('title', 'Unknown')}: {str(e)}")
                continue
        
        # Remove duplicates
        cleaned_properties = self.remove_duplicates(cleaned_properties)
        
        logger.info(f"Data cleaning completed. {len(cleaned_properties)} valid properties after cleaning")
        return cleaned_properties
    
    def clean_single_property(self, property_data: Dict) -> Dict:
        """Clean a single property record"""
        cleaned = property_data.copy()
        
        # Clean and normalize price
        cleaned['price_pkr'] = self.normalize_price(property_data.get('price_raw', ''))
        
        # Clean and normalize area
        if property_data.get('area_raw'):
            cleaned['area_size'] = self.normalize_area(property_data['area_raw'])
        
        # Standardize property type
        cleaned['property_type'] = self.standardize_property_type(property_data.get('property_type', ''))
        
        # Clean location data
        cleaned.update(self.clean_location_data(property_data))
        
        # Clean contact information
        cleaned.update(self.clean_contact_info(property_data))
        
        # Clean title
        cleaned['title'] = self.clean_text(property_data.get('title', ''))
        
        # Calculate price per sq ft
        if cleaned.get('price_pkr') and cleaned.get('area_size'):
            cleaned['price_per_sqft'] = cleaned['price_pkr'] / cleaned['area_size']
        
        # Add data quality score
        cleaned['data_quality_score'] = self.calculate_quality_score(cleaned)
        
        return cleaned
    
    def normalize_price(self, price_text: str) -> Optional[float]:
        """Normalize price to PKR amount"""
        if not price_text or isinstance(price_text, (int, float)):
            return float(price_text) if price_text else None
        
        try:
            # Remove currency symbols and clean text
            price_clean = re.sub(r'[^\d.,\w\s]', '', str(price_text).lower().strip())
            price_clean = re.sub(r'\s+', ' ', price_clean)  # Remove extra spaces
            
            # Handle different price formats
            for unit, multiplier in self.price_patterns.items():
                if unit in price_clean:
                    # Extract number before the unit
                    pattern = rf'(\d+(?:\.\d+)?)\s*{unit}'
                    match = re.search(pattern, price_clean)
                    if match:
                        number = float(match.group(1))
                        return number * multiplier
            
            # If no unit found, try to extract direct number
            numbers = re.findall(r'\d+(?:\.\d+)?', price_clean.replace(',', ''))
            if numbers:
                return float(numbers[0])
            
        except (ValueError, AttributeError) as e:
            logger.warning(f"Could not normalize price '{price_text}': {str(e)}")
        
        return None
    
    def normalize_area(self, area_text: str) -> Optional[float]:
        """Normalize area to square feet"""
        if not area_text or isinstance(area_text, (int, float)):
            return float(area_text) if area_text else None
        
        try:
            area_clean = str(area_text).lower().strip()
            
            # Extract number and unit
            pattern = r'(\d+(?:\.\d+)?)\s*(marla|kanal|sq\s*ft|sqft|square\s*feet|sq\s*m|sq\s*meter|yard|acre)'
            match = re.search(pattern, area_clean)
            
            if match:
                size = float(match.group(1))
                unit = match.group(2).replace(' ', '')
                
                # Convert to square feet
                multiplier = self.area_conversions.get(unit, 1)
                return size * multiplier
            
            # If no unit found, assume square feet
            numbers = re.findall(r'\d+(?:\.\d+)?', area_clean)
            if numbers:
                return float(numbers[0])
                
        except (ValueError, AttributeError) as e:
            logger.warning(f"Could not normalize area '{area_text}': {str(e)}")
        
        return None
    
    def standardize_property_type(self, property_type: str) -> str:
        """Standardize property type"""
        if not property_type:
            return "Other"
        
        prop_type_clean = str(property_type).lower().strip()
        
        for standard_type, variations in self.property_type_mapping.items():
            for variation in variations:
                if variation in prop_type_clean:
                    return standard_type.title()
        
        return property_type.title() if property_type else "Other"
    
    def clean_location_data(self, property_data: Dict) -> Dict:
        """Clean and standardize location data"""
        cleaned_location = {}
        
        # Clean city name
        city = property_data.get('city', '').strip().title()
        if city:
            # Standardize major city names
            city_mappings = {
                'Karachi': ['karachi', 'krchi', 'khi'],
                'Lahore': ['lahore', 'lhr', 'lahore city'],
                'Islamabad': ['islamabad', 'isb', 'islamabad capital'],
                'Rawalpindi': ['rawalpindi', 'rwp', 'pindi'],
                'Faisalabad': ['faisalabad', 'fsd', 'lyallpur']
            }
            
            for standard_name, variations in city_mappings.items():
                if city.lower() in variations:
                    city = standard_name
                    break
            
            cleaned_location['city'] = city
        
        # Clean area name
        area = property_data.get('area', '').strip().title()
        if area:
            cleaned_location['area'] = area
        
        # Clean sector/block
        sector = property_data.get('sector_block', '').strip().title()
        if sector:
            cleaned_location['sector_block'] = sector
        
        # Clean full address
        full_address = property_data.get('full_address', '').strip()
        if full_address:
            cleaned_location['full_address'] = full_address
        
        return cleaned_location
    
    def clean_contact_info(self, property_data: Dict) -> Dict:
        """Clean contact information"""
        cleaned_contact = {}
        
        # Clean phone number
        phone = property_data.get('contact_phone', '')
        if phone:
            # Remove all non-digit characters except +
            phone_clean = re.sub(r'[^\d+]', '', str(phone))
            if len(phone_clean) >= 10:  # Minimum valid phone length
                cleaned_contact['contact_phone'] = phone_clean
        
        # Clean email
        email = property_data.get('contact_email', '')
        if email and '@' in email:
            cleaned_contact['contact_email'] = email.lower().strip()
        
        # Clean agent name
        agent = property_data.get('agent_name', '').strip().title()
        if agent:
            cleaned_contact['agent_name'] = agent
        
        # Clean seller name
        seller = property_data.get('seller_name', '').strip().title()
        if seller:
            cleaned_contact['seller_name'] = seller
        
        return cleaned_contact
    
    def clean_text(self, text: str) -> str:
        """Clean text fields"""
        if not text:
            return ""
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', str(text).strip())
        
        # Remove special characters but keep basic punctuation
        cleaned = re.sub(r'[^\w\s\-.,()\/]', '', cleaned)
        
        return cleaned
    
    def is_valid_property(self, property_data: Dict) -> bool:
        """Check if property has minimum required data"""
        required_fields = ['title', 'city']
        
        for field in required_fields:
            if not property_data.get(field):
                return False
        
        # At least one of price or area should be available
        if not property_data.get('price_pkr') and not property_data.get('area_size'):
            return False
        
        return True
    
    def calculate_quality_score(self, property_data: Dict) -> float:
        """Calculate data quality score (0-1)"""
        important_fields = ['title', 'city', 'price_pkr', 'property_type', 'area_size']
        optional_fields = ['area', 'bedrooms', 'bathrooms', 'agent_name', 'contact_phone']
        
        important_score = sum(1 for field in important_fields if property_data.get(field))
        optional_score = sum(1 for field in optional_fields if property_data.get(field))
        
        # Important fields weight 70%, optional fields 30%
        score = (important_score / len(important_fields)) * 0.7 + \
                (optional_score / len(optional_fields)) * 0.3
        
        return round(score, 2)
    
    def remove_duplicates(self, properties: List[Dict]) -> List[Dict]:
        """Remove duplicate properties based on content similarity"""
        logger.info(f"Removing duplicates from {len(properties)} properties")
        
        unique_properties = []
        seen_hashes = set()
        
        for prop in properties:
            # Create content hash
            hash_content = f"{prop.get('title', '')}" \
                          f"{prop.get('city', '')}" \
                          f"{prop.get('area', '')}" \
                          f"{prop.get('price_pkr', '')}" \
                          f"{prop.get('area_size', '')}"
            
            content_hash = hashlib.sha256(hash_content.encode()).hexdigest()
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                prop['content_hash'] = content_hash
                unique_properties.append(prop)
        
        duplicates_removed = len(properties) - len(unique_properties)
        logger.info(f"Removed {duplicates_removed} duplicates. {len(unique_properties)} unique properties remain")
        
        return unique_properties
    
    def generate_cleaning_report(self, original_data: List[Dict], cleaned_data: List[Dict]) -> Dict:
        """Generate a report of the cleaning process"""
        report = {
            'original_count': len(original_data),
            'cleaned_count': len(cleaned_data),
            'removed_count': len(original_data) - len(cleaned_data),
            'cleaning_timestamp': datetime.utcnow(),
            'quality_stats': {},
            'price_stats': {},
            'area_stats': {}
        }
        
        if cleaned_data:
            # Quality score statistics
            quality_scores = [prop.get('data_quality_score', 0) for prop in cleaned_data]
            report['quality_stats'] = {
                'average_quality': np.mean(quality_scores),
                'min_quality': np.min(quality_scores),
                'max_quality': np.max(quality_scores)
            }
            
            # Price statistics
            prices = [prop.get('price_pkr') for prop in cleaned_data if prop.get('price_pkr')]
            if prices:
                report['price_stats'] = {
                    'properties_with_price': len(prices),
                    'average_price': np.mean(prices),
                    'median_price': np.median(prices),
                    'min_price': np.min(prices),
                    'max_price': np.max(prices)
                }
            
            # Area statistics
            areas = [prop.get('area_size') for prop in cleaned_data if prop.get('area_size')]
            if areas:
                report['area_stats'] = {
                    'properties_with_area': len(areas),
                    'average_area': np.mean(areas),
                    'median_area': np.median(areas),
                    'min_area': np.min(areas),
                    'max_area': np.max(areas)
                }
        
        return report

# Global instance
data_cleaner = DataCleaner()