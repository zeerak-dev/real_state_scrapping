import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

load_dotenv()

Base = declarative_base()

class PropertyListing(Base):
    __tablename__ = 'property_listings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic property info
    title = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    area = Column(String(200), nullable=True)
    sector_block = Column(String(200), nullable=True)
    full_address = Column(Text, nullable=True)
    
    # Price information
    price_pkr = Column(Float, nullable=True, index=True)
    price_raw = Column(String(200), nullable=True)  # Original price string
    price_per_sqft = Column(Float, nullable=True)
    
    # Property details
    property_type = Column(String(100), nullable=False, index=True)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    area_size = Column(Float, nullable=True)  # Normalized to Sq. Ft.
    area_unit = Column(String(50), nullable=True)  # Original unit (Marla, Kanal, etc.)
    area_raw = Column(String(100), nullable=True)  # Original area string
    
    # Contact information
    agent_name = Column(String(200), nullable=True)
    seller_name = Column(String(200), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    contact_email = Column(String(200), nullable=True)
    
    # Metadata
    source_website = Column(String(100), nullable=False, index=True)
    source_url = Column(Text, nullable=True)
    listing_id = Column(String(100), nullable=True)  # Original listing ID from website
    date_posted = Column(DateTime, nullable=True)
    date_scraped = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Data quality flags
    is_duplicate = Column(Boolean, default=False, index=True)
    data_quality_score = Column(Float, default=0.0)  # 0-1 score based on completeness
    
    # Hash for duplicate detection
    content_hash = Column(String(64), nullable=True, index=True)
    
    def __repr__(self):
        return f"<PropertyListing(id={self.id}, title='{self.title[:50]}...', city='{self.city}', price={self.price_pkr})>"

class ScrapingSession(Base):
    __tablename__ = 'scraping_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    website = Column(String(100), nullable=False)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    properties_scraped = Column(Integer, default=0)
    properties_saved = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    status = Column(String(50), default='running')  # running, completed, failed
    log_file = Column(String(500), nullable=True)
    
    def __repr__(self):
        return f"<ScrapingSession(id={self.id}, website='{self.website}', status='{self.status}')>"

# Database configuration
class DatabaseConfig:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.database = os.getenv('DB_NAME', 'real_estate_pakistan')
        self.username = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', '')
        self.db_type = os.getenv('DB_TYPE', 'postgresql')  # postgresql or mysql
        
    def get_connection_string(self):
        if self.db_type == 'postgresql':
            return f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.db_type == 'mysql':
            return f"mysql+mysqlconnector://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.db_type == 'sqlite':
            # For SQLite, database is the file path
            return f"sqlite:///{self.database}"
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

# Database connection manager
class DatabaseManager:
    def __init__(self):
        self.config = DatabaseConfig()
        self.engine = create_engine(
            self.config.get_connection_string(),
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()
        
    def close_connection(self):
        """Close the database connection"""
        self.engine.dispose()

# Singleton instance
db_manager = DatabaseManager()