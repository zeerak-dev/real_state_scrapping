# Pakistan Real Estate Analytics Dashboard

## Overview
A comprehensive real estate analytics dashboard that scrapes data from major Pakistani property websites (Zameen.com, Graana.com) and provides insights through an interactive dashboard.

## Features
- 🏠 Multi-website scraping (Zameen.com, Graana.com)
- 🗃️ PostgreSQL/MySQL database integration
- 🧹 Automated data cleaning and normalization
- 📊 Interactive Streamlit dashboard
- 📅 Daily automated scraping
- 📈 Price trends and analytics
- 🔍 Advanced search and filtering
- 📥 CSV export functionality

## Project Structure
```
real state scrapping/
├── scrapers/           # Web scrapers for different websites
├── database/          # Database models and operations
├── data_cleaning/     # Data cleaning and normalization
├── dashboard/         # Streamlit dashboard
├── config/           # Configuration files
├── logs/             # Application logs
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## Setup Instructions

### 1. Clone and Setup
```bash
# Navigate to project directory
cd "real state scrapping"

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup
#### For PostgreSQL (Recommended):
```bash
# Install PostgreSQL
# Create database
createdb real_estate_pakistan
```

#### For MySQL (Alternative):
```sql
CREATE DATABASE real_estate_pakistan;
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and update:
```bash
cp .env.example .env
```

Edit `.env` with your database credentials:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=real_estate_pakistan
DB_USER=your_username
DB_PASSWORD=your_password
DB_TYPE=postgresql
```

### 4. Initialize Database
```bash
python main.py init
```

### 5. Run the Application

#### Scrape Data (One-time):
```bash
# Scrape from both websites (5 pages per city)
python main.py scrape

# Scrape from specific website
python main.py scrape --websites zameen --pages 3
```

#### Run Dashboard:
```bash
streamlit run dashboard/app.py
```

#### Export Data:
```bash
# Export all data
python main.py export

# Export specific city
python main.py export --city Karachi --filename karachi_properties.csv
```

#### Scheduled Scraping:
```bash
# Run once immediately
python scheduler.py --run-once

# Start daily scheduler
python scheduler.py --schedule
```

### 6. View Statistics:
```bash
python main.py stats
```

## Data Sources
- **Zameen.com**: Property listings across Pakistan
- **Graana.com**: Real estate marketplace

## Analytics Features
- Average property prices by city
- Top 10 most expensive areas
- Price distribution graphs
- Property type analysis
- Search filters (City + Property Type)

## Technical Features
- Anti-scraping protection (user-agent rotation, delays)
- Pagination handling
- Data deduplication
- Error handling and logging
- Automated scheduling

## Author
Real Estate Analytics Team