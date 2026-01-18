# Database Schema Documentation

## 🗄️ Complete Database Schema

### Overview
The Pakistan Real Estate Analytics system uses a relational database schema optimized for property data storage, analysis, and reporting. The schema supports both PostgreSQL and SQLite backends.

## 📊 Database Tables

### 1. `property_listings` (Main Properties Table)

#### Purpose
Stores all scraped and cleaned property listing data with comprehensive metadata.

#### Schema Definition
```sql
CREATE TABLE property_listings (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Basic Property Information
    title VARCHAR(500) NOT NULL,
    city VARCHAR(100) NOT NULL,
    area VARCHAR(200) NULL,
    sector_block VARCHAR(200) NULL,
    full_address TEXT NULL,
    
    -- Price Information
    price_pkr FLOAT NULL,              -- Normalized price in PKR
    price_raw VARCHAR(200) NULL,       -- Original price string
    price_per_sqft FLOAT NULL,         -- Calculated price per sq ft
    
    -- Property Details
    property_type VARCHAR(100) NOT NULL,
    bedrooms INTEGER NULL,
    bathrooms INTEGER NULL,
    area_size FLOAT NULL,              -- Normalized to sq ft
    area_unit VARCHAR(50) NULL,        -- Original unit (Marla, Kanal, etc.)
    area_raw VARCHAR(100) NULL,        -- Original area string
    
    -- Contact Information
    agent_name VARCHAR(200) NULL,
    seller_name VARCHAR(200) NULL,
    contact_phone VARCHAR(50) NULL,
    contact_email VARCHAR(200) NULL,
    
    -- Metadata
    source_website VARCHAR(100) NOT NULL,
    source_url TEXT NULL,
    listing_id VARCHAR(100) NULL,      -- Original website listing ID
    date_posted DATETIME NULL,         -- When posted on website
    date_scraped DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Data Quality & Deduplication
    is_duplicate BOOLEAN DEFAULT FALSE,
    data_quality_score FLOAT DEFAULT 0.0,  -- 0-1 quality score
    content_hash VARCHAR(64) NULL,     -- For duplicate detection
    
    -- Indexes for Performance
    INDEX idx_city (city),
    INDEX idx_property_type (property_type),
    INDEX idx_price (price_pkr),
    INDEX idx_source (source_website),
    INDEX idx_duplicate (is_duplicate),
    INDEX idx_hash (content_hash),
    INDEX idx_date_scraped (date_scraped)
);
```

#### Field Descriptions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | INTEGER | Auto-increment primary key | 1001 |
| `title` | VARCHAR(500) | Property listing title | "3 Bed House in DHA, Karachi" |
| `city` | VARCHAR(100) | Standardized city name | "Karachi" |
| `area` | VARCHAR(200) | Neighborhood/area name | "DHA Phase 5" |
| `sector_block` | VARCHAR(200) | Specific sector/block | "Block A" |
| `full_address` | TEXT | Complete address | "DHA Phase 5, Block A, Karachi" |
| `price_pkr` | FLOAT | Normalized price in PKR | 15000000 |
| `price_raw` | VARCHAR(200) | Original price text | "1.5 Crore" |
| `price_per_sqft` | FLOAT | Price per square foot | 6250.00 |
| `property_type` | VARCHAR(100) | Standardized property type | "House", "Apartment", "Plot" |
| `bedrooms` | INTEGER | Number of bedrooms | 3 |
| `bathrooms` | INTEGER | Number of bathrooms | 2 |
| `area_size` | FLOAT | Area in square feet | 2400.0 |
| `area_unit` | VARCHAR(50) | Original area unit | "marla", "sq ft" |
| `area_raw` | VARCHAR(100) | Original area string | "10 Marla" |
| `agent_name` | VARCHAR(200) | Real estate agent name | "Ahmed Properties" |
| `seller_name` | VARCHAR(200) | Property seller name | "Muhammad Ali" |
| `contact_phone` | VARCHAR(50) | Contact phone number | "0300-1234567" |
| `contact_email` | VARCHAR(200) | Contact email | "agent@example.com" |
| `source_website` | VARCHAR(100) | Source website | "zameen.com" |
| `source_url` | TEXT | Original listing URL | "https://zameen.com/..." |
| `listing_id` | VARCHAR(100) | Website's listing ID | "12345" |
| `date_posted` | DATETIME | Original posting date | "2025-09-15 10:30:00" |
| `date_scraped` | DATETIME | When we scraped it | "2025-09-29 05:24:10" |
| `is_duplicate` | BOOLEAN | Duplicate flag | FALSE |
| `data_quality_score` | FLOAT | Quality score (0-1) | 0.85 |
| `content_hash` | VARCHAR(64) | SHA256 hash for dedup | "a1b2c3..." |

### 2. `scraping_sessions` (Scraping Audit Table)

#### Purpose
Tracks scraping operations for monitoring, debugging, and performance analysis.

#### Schema Definition
```sql
CREATE TABLE scraping_sessions (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Session Information
    website VARCHAR(100) NOT NULL,
    start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME NULL,
    
    -- Results
    properties_scraped INTEGER DEFAULT 0,
    properties_saved INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    
    -- Status & Logging
    status VARCHAR(50) DEFAULT 'running',  -- running, completed, failed
    log_file VARCHAR(500) NULL,
    
    -- Indexes
    INDEX idx_website (website),
    INDEX idx_start_time (start_time),
    INDEX idx_status (status)
);
```

#### Field Descriptions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | INTEGER | Session ID | 1 |
| `website` | VARCHAR(100) | Target website | "zameen.com" |
| `start_time` | DATETIME | Session start time | "2025-09-29 02:00:00" |
| `end_time` | DATETIME | Session end time | "2025-09-29 02:45:30" |
| `properties_scraped` | INTEGER | Total properties found | 150 |
| `properties_saved` | INTEGER | Successfully saved | 142 |
| `errors_count` | INTEGER | Number of errors | 3 |
| `status` | VARCHAR(50) | Session status | "completed" |
| `log_file` | VARCHAR(500) | Log file path | "logs/scraper_20250929.log" |

## 🔍 Database Queries Examples

### Common Analytics Queries

#### 1. Average Price by City
```sql
SELECT 
    city,
    COUNT(*) as total_properties,
    AVG(price_pkr) as avg_price,
    MIN(price_pkr) as min_price,
    MAX(price_pkr) as max_price
FROM property_listings 
WHERE price_pkr IS NOT NULL 
  AND is_duplicate = FALSE
GROUP BY city
ORDER BY avg_price DESC;
```

#### 2. Top Expensive Areas
```sql
SELECT 
    city,
    area,
    AVG(price_pkr) as avg_price,
    COUNT(*) as property_count
FROM property_listings 
WHERE price_pkr IS NOT NULL 
  AND area IS NOT NULL 
  AND is_duplicate = FALSE
GROUP BY city, area
HAVING COUNT(*) >= 3
ORDER BY avg_price DESC
LIMIT 10;
```

#### 3. Property Type Distribution
```sql
SELECT 
    property_type,
    COUNT(*) as count,
    AVG(price_pkr) as avg_price,
    AVG(area_size) as avg_area
FROM property_listings 
WHERE is_duplicate = FALSE
GROUP BY property_type
ORDER BY count DESC;
```

#### 4. Recent Scraping Performance
```sql
SELECT 
    website,
    DATE(start_time) as scrape_date,
    SUM(properties_scraped) as total_scraped,
    SUM(properties_saved) as total_saved,
    SUM(errors_count) as total_errors,
    COUNT(*) as sessions
FROM scraping_sessions 
WHERE start_time >= DATE('now', '-7 days')
GROUP BY website, DATE(start_time)
ORDER BY scrape_date DESC;
```

#### 5. Data Quality Analysis
```sql
SELECT 
    CASE 
        WHEN data_quality_score >= 0.8 THEN 'High Quality'
        WHEN data_quality_score >= 0.6 THEN 'Medium Quality'
        ELSE 'Low Quality'
    END as quality_level,
    COUNT(*) as count,
    ROUND(AVG(data_quality_score), 2) as avg_score
FROM property_listings 
WHERE is_duplicate = FALSE
GROUP BY quality_level
ORDER BY avg_score DESC;
```

## 🚀 Performance Optimizations

### Indexes
- **City Index**: Fast city-based filtering
- **Price Index**: Efficient price range queries  
- **Property Type Index**: Quick property type searches
- **Date Index**: Time-based analysis
- **Hash Index**: Duplicate detection
- **Composite Indexes**: Multi-field queries

### Query Optimization Tips
1. Always include `is_duplicate = FALSE` for analytics
2. Use date ranges for better performance
3. Consider LIMIT clauses for large datasets
4. Use appropriate data types for comparisons

## 🔧 Database Setup Commands

### SQLite (Development)
```sql
-- Database file: real_estate_pakistan.db
-- Automatically created by SQLAlchemy
```

### PostgreSQL (Production)
```sql
-- Create Database
CREATE DATABASE real_estate_pakistan;

-- Create User
CREATE USER re_analytics WITH PASSWORD 'your_secure_password';

-- Grant Permissions
GRANT ALL PRIVILEGES ON DATABASE real_estate_pakistan TO re_analytics;

-- Connect and create tables
\c real_estate_pakistan;
-- Tables will be created by SQLAlchemy migrations
```

### MySQL (Alternative)
```sql
-- Create Database
CREATE DATABASE real_estate_pakistan CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create User
CREATE USER 're_analytics'@'localhost' IDENTIFIED BY 'your_secure_password';

-- Grant Permissions
GRANT ALL PRIVILEGES ON real_estate_pakistan.* TO 're_analytics'@'localhost';
FLUSH PRIVILEGES;
```

## 📊 Data Validation Rules

### Required Fields
- `title`: Must not be empty
- `city`: Must be one of target cities
- `property_type`: Must be standardized type
- `source_website`: Must be valid source

### Data Quality Scoring
The system calculates quality scores based on:
- **Important Fields (70%)**: title, city, price, property_type, area_size
- **Optional Fields (30%)**: area, bedrooms, bathrooms, agent_name, contact_phone

### Duplicate Detection
Content hashing based on:
- Property title
- City and area
- Price information  
- Property size
- Key characteristics

## 🔄 Database Maintenance

### Regular Maintenance Tasks
1. **Cleanup Duplicates**: Remove flagged duplicates
2. **Update Statistics**: Refresh database statistics
3. **Archive Old Data**: Move old scraping sessions
4. **Backup Database**: Regular backup schedule
5. **Monitor Performance**: Query performance analysis

### Backup Strategy
```bash
# SQLite Backup
cp real_estate_pakistan.db backup_$(date +%Y%m%d).db

# PostgreSQL Backup
pg_dump real_estate_pakistan > backup_$(date +%Y%m%d).sql

# MySQL Backup
mysqldump real_estate_pakistan > backup_$(date +%Y%m%d).sql
```