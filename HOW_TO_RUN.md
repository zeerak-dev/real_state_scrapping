# 🚀 How to Run Everything - Complete Guide

## 📋 Quick Start (5 Minutes)

### Step 1: Verify Installation
```powershell
# Check if all dependencies are installed
python --version
# Should show: Python 3.8+ 

# Verify key packages
python -c "import streamlit, pandas, requests, sqlalchemy; print('All packages ready!')"
```

### Step 2: Start the Dashboard
```powershell
# Start the interactive web dashboard
streamlit run dashboard/app.py
```
- 🌐 **Dashboard URL**: `http://localhost:8501` (or :8502 if 8501 is busy)
- 📊 **Contains**: 51 sample properties across 4 cities
- ⚡ **Ready to use**: Charts, filtering, and CSV export

### Step 3: View Statistics
```powershell
# See formatted database statistics
python show_stats.py
```

**You're ready to go! The system is working with sample data.**

---

## 🔧 Detailed Setup Guide

### Prerequisites Check
```powershell
# 1. Python version (3.8 or higher required)
python --version

# 2. Pip installation
pip --version

# 3. Check if project files exist
dir *.py
dir requirements.txt
```

### Complete Installation
```powershell
# 1. Install all dependencies
pip install -r requirements.txt

# 2. Setup environment (already done with SQLite)
copy .env.example .env

# 3. Initialize database (creates SQLite file)
python main.py init

# 4. Add sample data for testing
python create_sample_data.py

# 5. Verify setup
python test_db.py
```

---

## 🏠 All Available Commands

### 📊 Dashboard & Analytics
```powershell
# Start interactive web dashboard
streamlit run dashboard/app.py

# View formatted statistics in terminal
python show_stats.py

# Run comprehensive system test
python quick_test.py
```

### 🗄️ Database Operations
```powershell
# Initialize database and create tables
python main.py init

# View database statistics
python main.py stats

# Test database configuration
python test_db.py
```

### 🕷️ Web Scraping
```powershell
# Scrape from both websites (default: 5 pages per city)
python main.py scrape

# Scrape from specific website only
python main.py scrape --websites zameen

# Limit pages per city
python main.py scrape --pages 2

# Scrape both websites with custom pages
python main.py scrape --websites zameen graana --pages 3
```

### ⏰ Scheduling & Automation
```powershell
# Run scraping once immediately
python scheduler.py --run-once

# Start daily automated scheduler (runs at 2:00 AM)
python scheduler.py --schedule

# Stop scheduler: Press Ctrl+C
```

### 📥 Data Export
```powershell
# Export all data to CSV
python main.py export

# Export with custom filename
python main.py export --filename my_properties.csv

# Export specific city data
python main.py export --city Karachi
```

### 🧪 Testing & Development
```powershell
# Create additional sample data
python create_sample_data.py

# Test database configuration
python test_db.py

# Run system health check
python quick_test.py
```

---

## 🌐 Using the Dashboard

### Accessing the Dashboard
1. Run: `streamlit run dashboard/app.py`
2. Open browser to: `http://localhost:8501`
3. If port 8501 is busy, try: `http://localhost:8502`

### Dashboard Features

#### 📊 **Analytics Section**
- **City Comparison**: Average prices across Karachi, Lahore, Islamabad, Rawalpindi
- **Price Distribution**: Interactive histograms showing price ranges
- **Top Areas**: Most expensive neighborhoods ranked
- **Property Types**: Distribution pie chart

#### 🔍 **Search & Filter**
- **City Filter**: Select specific city or "All"
- **Property Type**: House, Apartment, Plot, Commercial, etc.
- **Price Range**: Slider to set minimum and maximum price
- **Bedroom Count**: Filter by number of bedrooms

#### 📋 **Property Listings**
- **Sortable Table**: Sort by price, date, area size, quality score
- **Pagination**: Show 50/100/200/500 properties
- **Detailed View**: All property information in tabular format

#### 📥 **Export Options**
- **CSV Download**: Export filtered results
- **Date Stamped**: Files named with current date/time
- **All Fields**: Complete property data included

### Sample Dashboard Data
Current database contains:
- **51 Properties** across 4 cities
- **Price Range**: PKR 2.5M to 15M+
- **Property Types**: Houses, Apartments, Plots, Commercial
- **Quality Score**: All properties scored for data completeness

---

## 🔧 Configuration Options

### Database Configuration (`.env` file)
```bash
# Current setup (SQLite - no additional setup needed)
DB_TYPE=sqlite
DB_NAME=real_estate_pakistan.db

# For PostgreSQL (production)
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=real_estate_pakistan
DB_USER=postgres
DB_PASSWORD=your_password

# For MySQL (alternative)
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=real_estate_pakistan
DB_USER=root
DB_PASSWORD=your_password
```

### Scraping Configuration
```bash
# Delays between requests (seconds)
SCRAPING_DELAY_MIN=2
SCRAPING_DELAY_MAX=5

# Retry settings
MAX_RETRIES=3
REQUEST_TIMEOUT=30

# Daily scheduling (24-hour format)
SCHEDULE_HOUR=2          # 2:00 AM
SCHEDULE_MINUTE=0
```

### Logging Configuration
```bash
# Log levels: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Log file rotation
LOG_FILE_MAX_SIZE=10485760  # 10MB
LOG_FILE_BACKUP_COUNT=5
```

---

## 🚨 Troubleshooting

### Common Issues & Solutions

#### **Dashboard won't start**
```powershell
# Check if port is busy
netstat -an | findstr 8501

# Try different port
streamlit run dashboard/app.py --server.port 8080

# Check dependencies
pip list | findstr streamlit
```

#### **Database errors**
```powershell
# Reinitialize database
del real_estate_pakistan.db
python main.py init

# Check database file exists
dir *.db

# Test database connection
python test_db.py
```

#### **Scraping returns no data**
- **Expected behavior**: Websites have anti-scraping protection
- **Solution**: Use sample data for testing
- **Production**: Would require proxy servers and advanced techniques

#### **Import errors**
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python path
python -c "import sys; print(sys.path)"
```

### Performance Issues
- **Dashboard slow**: Reduce data size or add caching
- **Scraping timeout**: Increase `REQUEST_TIMEOUT` in `.env`
- **Database queries slow**: Indexes are already optimized

---

## 🎯 Usage Scenarios

### **Scenario 1: Real Estate Analysis**
```powershell
# Start dashboard for interactive analysis
streamlit run dashboard/app.py
# Use filters to analyze specific areas or price ranges
# Export results for presentations
```

### **Scenario 2: Daily Data Collection**
```powershell
# Set up automated daily scraping
python scheduler.py --schedule
# Runs automatically at 2:00 AM daily
# Check logs in logs/ directory
```

### **Scenario 3: Data Export for Reports**
```powershell
# Export all data
python main.py export

# Export specific city for focused analysis  
python main.py export --city "Karachi" --filename "karachi_analysis.csv"
```

### **Scenario 4: Development & Testing**
```powershell
# Add more test data
python create_sample_data.py

# Run system health checks
python quick_test.py

# View detailed statistics
python show_stats.py
```

---

## 📈 Expected Results

### **Dashboard Analytics**
When you open `http://localhost:8501`, you'll see:
- **4 Interactive Charts** with real property data
- **51 Properties** across Karachi, Lahore, Islamabad, Rawalpindi
- **Price Range**: PKR 2,591,675 to PKR 15,158,154
- **Search Filters** working with live data

### **Statistics Output**
Running `python show_stats.py` shows:
```
🏙️ CITY-WISE STATISTICS:
🏠 Islamabad    | Properties:  12 | Avg Price: PKR    7,803,202
🏠 Karachi      | Properties:  14 | Avg Price: PKR    6,772,379  
🏠 Lahore       | Properties:   8 | Avg Price: PKR    7,737,653
🏠 Rawalpindi   | Properties:  17 | Avg Price: PKR    5,262,797

💰 TOP EXPENSIVE AREAS:
1. Cantt, Lahore       | Avg: PKR  9,158,154 (4 properties)
2. F-8, Islamabad      | Avg: PKR  7,317,691 (5 properties)
...
```

### **CSV Export Results**
Exported files contain 17 columns:
- Property details (title, city, area, type)
- Pricing (PKR amount, price per sq ft)
- Specifications (bedrooms, bathrooms, area size)
- Contact information (agent, phone)
- Metadata (source, date, quality score)

---

## 🎉 Success Indicators

### ✅ **System is Working When:**
- Dashboard loads at `http://localhost:8501` without errors
- Statistics show data for 4 cities (Islamabad, Karachi, Lahore, Rawalpindi)
- Charts display with property data
- CSV export downloads successfully
- Database file `real_estate_pakistan.db` exists (36KB+)

### ✅ **Ready for Production When:**
- PostgreSQL database configured
- Automated scheduler running
- Error handling tested
- Log files being generated in `logs/` directory

---

**🏠 Your Pakistan Real Estate Analytics system is ready to analyze the property market! 📊**