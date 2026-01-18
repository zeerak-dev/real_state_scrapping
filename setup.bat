#!/bin/bash
# Windows installation script for Pakistan Real Estate Analytics

echo "=== Pakistan Real Estate Analytics Setup ==="
echo ""

# Check if Python is installed
python --version
if [ $? -ne 0 ]; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

echo "1. Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "2. Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from template"
    echo "Please edit .env file with your database credentials"
else
    echo ".env file already exists"
fi

echo ""
echo "3. Creating log directory..."
mkdir -p logs

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your database credentials"
echo "2. Setup PostgreSQL/MySQL database"
echo "3. Run: python main.py init"
echo "4. Run: python main.py scrape"
echo "5. Run: streamlit run dashboard/app.py"
echo ""
echo "For detailed instructions, see README.md"