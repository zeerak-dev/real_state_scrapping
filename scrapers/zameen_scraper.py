import requests
import time
import random
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, parse_qs, urlparse
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import re
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Config

logger = logging.getLogger(__name__)

class ZameenScraper:
    def __init__(self):
        self.base_url = "https://www.zameen.com"
        self.session = requests.Session()
        self.current_user_agent_index = 0
        
        # Headers to mimic real browser
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        self.rotate_user_agent()
    
    def rotate_user_agent(self):
        """Rotate user agent to avoid detection"""
        user_agent = Config.USER_AGENTS[self.current_user_agent_index % len(Config.USER_AGENTS)]
        self.session.headers.update({'User-Agent': user_agent})
        self.current_user_agent_index += 1
        logger.debug(f"Rotated user agent: {user_agent[:50]}...")
    
    def random_delay(self):
        """Add random delay between requests"""
        delay = random.uniform(Config.SCRAPING_DELAY_MIN, Config.SCRAPING_DELAY_MAX)
        time.sleep(delay)
        logger.debug(f"Delayed {delay:.2f} seconds")
    
    def make_request(self, url: str, max_retries: int = None) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        if max_retries is None:
            max_retries = Config.MAX_RETRIES
            
        for attempt in range(max_retries + 1):
            try:
                self.random_delay()
                self.rotate_user_agent()
                
                response = self.session.get(
                    url, 
                    timeout=Config.REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    # Rate limited - wait longer
                    wait_time = (2 ** attempt) * 60  # Exponential backoff
                    logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.warning(f"HTTP {response.status_code} for {url}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries:
                    time.sleep((2 ** attempt) * 5)  # Exponential backoff
                
        logger.error(f"Failed to fetch {url} after {max_retries + 1} attempts")
        return None
    
    def get_city_search_url(self, city: str, property_type: str = "", page: int = 1) -> str:
        """Generate search URL for specific city and property type"""
        city_urls = {
            'karachi': 'https://www.zameen.com/Homes/Karachi-1-1.html',
            'lahore': 'https://www.zameen.com/Homes/Lahore-5-1.html',
            'islamabad': 'https://www.zameen.com/Homes/Islamabad-2-1.html',
            'rawalpindi': 'https://www.zameen.com/Homes/Rawalpindi-3-1.html',
            'faisalabad': 'https://www.zameen.com/Homes/Faisalabad-17-1.html'
        }
        
        base_url = city_urls.get(city.lower(), city_urls['karachi'])
        
        if page > 1:
            base_url = base_url.replace('.html', f'_{page}.html')
            
        return base_url
    
    def extract_property_info(self, property_element) -> Optional[Dict]:
        """Extract property information from a property listing element"""
        try:
            property_data = {
                'source_website': 'zameen.com',
                'date_scraped': datetime.utcnow()
            }
            
            # Title
            title_elem = property_element.find('h2', class_='PropertyCardstyle__Title-sc-1gn7nk4-14')
            if not title_elem:
                title_elem = property_element.find('h2', class_='_0e0175ed')
            property_data['title'] = title_elem.get_text(strip=True) if title_elem else "N/A"
            
            # Price
            price_elem = property_element.find('span', class_='PriceInfo__MainPricestyle-sc-6cgfz4-0')
            if not price_elem:
                price_elem = property_element.find('span', class_='_f6ac4fc3')
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                property_data['price_raw'] = price_text
                property_data['price_pkr'] = self.parse_price(price_text)
            
            # Location
            location_elem = property_element.find('div', class_='PropertyCard__Addressstyle-sc-1gn7nk4-7')
            if not location_elem:
                location_elem = property_element.find('div', class_='_8c067c68')
            if location_elem:
                location_text = location_elem.get_text(strip=True)
                property_data.update(self.parse_location(location_text))
            
            # Property type, bedrooms, bathrooms, area
            details_section = property_element.find('div', class_='PropertyCard__SubHeading-sc-1gn7nk4-13')
            if not details_section:
                details_section = property_element.find('div', class_='_4f2ff36d')
            
            if details_section:
                details_text = details_section.get_text(strip=True)
                property_data.update(self.parse_property_details(details_text))
            
            # Property URL
            link_elem = property_element.find('a', href=True)
            if link_elem:
                property_data['source_url'] = urljoin(self.base_url, link_elem['href'])
                # Extract listing ID from URL
                url_parts = link_elem['href'].split('-')
                if url_parts:
                    property_data['listing_id'] = url_parts[-1].replace('.html', '')
            
            # Agent/Seller (from detailed page if needed)
            agent_elem = property_element.find('div', class_='AgentInfo')
            if agent_elem:
                property_data['agent_name'] = agent_elem.get_text(strip=True)
            
            return property_data
            
        except Exception as e:
            logger.error(f"Error extracting property info: {str(e)}")
            return None
    
    def parse_price(self, price_text: str) -> Optional[float]:
        """Convert price text to PKR amount"""
        try:
            # Remove currency symbols and spaces
            price_clean = re.sub(r'[^\d.,\w\s]', '', price_text.lower())
            
            # Extract number and unit
            if 'crore' in price_clean:
                number = float(re.findall(r'[\d.]+', price_clean)[0])
                return number * 10000000  # 1 crore = 10 million
            elif 'lakh' in price_clean:
                number = float(re.findall(r'[\d.]+', price_clean)[0])
                return number * 100000  # 1 lakh = 100 thousand
            elif 'thousand' in price_clean or 'k' in price_clean:
                number = float(re.findall(r'[\d.]+', price_clean)[0])
                return number * 1000
            else:
                # Direct number
                numbers = re.findall(r'[\d,]+', price_clean)
                if numbers:
                    return float(numbers[0].replace(',', ''))
            
        except (ValueError, IndexError):
            logger.warning(f"Could not parse price: {price_text}")
            
        return None
    
    def parse_location(self, location_text: str) -> Dict:
        """Parse location information"""
        location_data = {}
        
        # Split location by commas
        parts = [part.strip() for part in location_text.split(',')]
        
        if parts:
            # Last part is usually the city
            for city in Config.TARGET_CITIES:
                if city.lower() in location_text.lower():
                    location_data['city'] = city
                    break
            else:
                location_data['city'] = parts[-1] if parts else "Unknown"
            
            # First part is usually the area/sector
            if len(parts) > 1:
                location_data['area'] = parts[0]
                if len(parts) > 2:
                    location_data['sector_block'] = parts[1]
            
            location_data['full_address'] = location_text
        
        return location_data
    
    def parse_property_details(self, details_text: str) -> Dict:
        """Parse property details like type, bedrooms, etc."""
        details_data = {}
        
        # Property type
        property_types = ['house', 'flat', 'apartment', 'plot', 'commercial', 'shop', 'office']
        for prop_type in property_types:
            if prop_type in details_text.lower():
                details_data['property_type'] = prop_type.title()
                break
        else:
            details_data['property_type'] = "Other"
        
        # Bedrooms
        bed_match = re.search(r'(\d+)\s*bed', details_text.lower())
        if bed_match:
            details_data['bedrooms'] = int(bed_match.group(1))
        
        # Bathrooms
        bath_match = re.search(r'(\d+)\s*bath', details_text.lower())
        if bath_match:
            details_data['bathrooms'] = int(bath_match.group(1))
        
        # Area
        area_match = re.search(r'(\d+(?:\.\d+)?)\s*(marla|kanal|sq\s*ft|sqft)', details_text.lower())
        if area_match:
            size = float(area_match.group(1))
            unit = area_match.group(2).replace(' ', '')
            details_data['area_raw'] = f"{size} {unit}"
            details_data['area_unit'] = unit
            details_data['area_size'] = self.convert_to_sqft(size, unit)
        
        return details_data
    
    def convert_to_sqft(self, size: float, unit: str) -> float:
        """Convert area to square feet"""
        conversions = {
            'marla': 272.25,     # 1 marla = 272.25 sq ft
            'kanal': 5445,       # 1 kanal = 5445 sq ft
            'sqft': 1,           # Already in sq ft
            'sq ft': 1,
            'sqft': 1
        }
        
        multiplier = conversions.get(unit.lower(), 1)
        return size * multiplier
    
    def scrape_property_listings(self, city: str, max_pages: int = 10) -> List[Dict]:
        """Scrape property listings for a specific city"""
        logger.info(f"Starting to scrape {city} properties from Zameen.com")
        
        properties = []
        page = 1
        
        while page <= max_pages:
            try:
                url = self.get_city_search_url(city, page=page)
                logger.info(f"Scraping page {page}: {url}")
                
                response = self.make_request(url)
                if not response:
                    logger.error(f"Failed to fetch page {page}")
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find property listings
                property_elements = soup.find_all('article', class_='_8cb584f9')
                if not property_elements:
                    property_elements = soup.find_all('div', class_='PropertyCardstyle__Container-sc-1gn7nk4-0')
                
                if not property_elements:
                    logger.warning(f"No property elements found on page {page}")
                    break
                
                logger.info(f"Found {len(property_elements)} properties on page {page}")
                
                for element in property_elements:
                    property_data = self.extract_property_info(element)
                    if property_data:
                        properties.append(property_data)
                
                # Check if there's a next page
                next_button = soup.find('a', {'aria-label': 'Next'})
                if not next_button or 'disabled' in next_button.get('class', []):
                    logger.info("No more pages available")
                    break
                
                page += 1
                
            except Exception as e:
                logger.error(f"Error scraping page {page}: {str(e)}")
                break
        
        logger.info(f"Scraped {len(properties)} properties from {city}")
        return properties
    
    def scrape_all_cities(self, max_pages_per_city: int = 5) -> List[Dict]:
        """Scrape properties from all target cities"""
        all_properties = []
        
        for city in Config.TARGET_CITIES:
            try:
                city_properties = self.scrape_property_listings(city, max_pages_per_city)
                all_properties.extend(city_properties)
                
                # Longer delay between cities
                time.sleep(random.uniform(10, 20))
                
            except Exception as e:
                logger.error(f"Error scraping {city}: {str(e)}")
                continue
        
        return all_properties
    
    def close(self):
        """Close the scraping session"""
        self.session.close()
        logger.info("Zameen scraper session closed")