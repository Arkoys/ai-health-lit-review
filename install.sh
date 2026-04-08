#!/bin/bash
set -e

echo "=========================================="
echo "AI Health Literature Review - Installer"
echo "=========================================="
echo ""

# Check Python
echo "1. Checking Python..."
python3 --version || { echo "Python 3 not found! Please install Python 3.10+"; exit 1; }

# Create virtual environment
echo "2. Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   Virtual environment created"
else
    echo "   Virtual environment already exists"
fi

# Activate venv and install dependencies
echo "3. Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "   Dependencies installed"

# Create necessary directories
echo "4. Creating data directories..."
mkdir -p data logs outputs/digests
touch logs/.gitkeep data/.gitkeep outputs/.gitkeep

# Check for .env file
echo "5. Environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "   Created .env file from .env.example"
    echo "   ⚠️  You MUST edit .env and add your API keys!"
else
    echo "   .env file already exists"
fi

# Create cron job
echo "6. Setting up daily cron job..."
CRON_JOB="0 8 * * * cd $(pwd) && source venv/bin/activate && python run_daily.py >> logs/cron_$(date +\%Y\%m\%d).log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "ai-health-lit-review"; then
    echo "   Cron job already exists. Skipping."
else
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "   Cron job added: runs daily at 08:00"
fi

echo ""
echo "=========================================="
echo "Installation complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys (at least GEMINI_API_KEY)"
echo "2. Test the system:"
echo "   source venv/bin/activate"
echo "   python run_daily.py --test-summarize"
echo "   python run_daily.py --test-email"
echo "   python run_daily.py --test-telegram"
echo "3. Run full daily digest:"
echo "   python run_daily.py"
echo ""
echo "Logs are in ./logs/"
echo "Database is in ./data/papers.db"
echo "Digests are in ./outputs/digests/"
echo ""