import os
import logging
import colorlog
from datetime import datetime

class Config:
    # Database settings
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'real_estate_pakistan')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_TYPE = os.getenv('DB_TYPE', 'postgresql')
    
    # Scraping settings
    SCRAPING_DELAY_MIN = int(os.getenv('SCRAPING_DELAY_MIN', '2'))
    SCRAPING_DELAY_MAX = int(os.getenv('SCRAPING_DELAY_MAX', '5'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
    
    # Scheduling settings
    SCHEDULE_HOUR = int(os.getenv('SCHEDULE_HOUR', '2'))
    SCHEDULE_MINUTE = int(os.getenv('SCHEDULE_MINUTE', '0'))
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE_MAX_SIZE = int(os.getenv('LOG_FILE_MAX_SIZE', '10485760'))  # 10MB
    LOG_FILE_BACKUP_COUNT = int(os.getenv('LOG_FILE_BACKUP_COUNT', '5'))
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    
    # User agents for scraping
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    ]
    
    # Target cities
    TARGET_CITIES = ['Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Faisalabad']
    
    # Property type mappings
    PROPERTY_TYPE_MAPPINGS = {
        'house': ['house', 'home', 'bungalow', 'villa', 'cottage'],
        'flat': ['flat', 'apartment', 'unit'],
        'plot': ['plot', 'land', 'residential plot', 'commercial plot'],
        'commercial': ['shop', 'office', 'warehouse', 'building'],
        'other': ['farmhouse', 'penthouse', 'studio']
    }

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs(Config.LOGS_DIR, exist_ok=True)
    
    # Create formatters
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
    
    # Console handler
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    # File handler
    from logging.handlers import RotatingFileHandler
    log_file = os.path.join(Config.LOGS_DIR, f'scraper_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=Config.LOG_FILE_MAX_SIZE,
        backupCount=Config.LOG_FILE_BACKUP_COUNT
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
    root_logger.addHandler(file_handler)
    
    return root_logger