#!/bin/bash

# DataVault Financial Services - Nuclia API Integration Setup
# Author: David Kim
# Date: July 2024

echo "==================================="
echo "DataVault Nuclia Integration Setup"
echo "==================================="
echo ""

# Step 1: Create Python virtual environment
echo "Step 1: Creating Python virtual environment..."
python3 -m venv venv

# Step 2: Activate virtual environment
echo "Step 2: Activating virtual environment..."
source venv/bin/activate

# Step 3: Upgrade pip
echo "Step 3: Upgrading pip..."
pip install --upgrade pip --quiet

# Step 4: Install required packages
echo "Step 4: Installing Nuclia SDK and dependencies..."

pip install nuclia --quiet
echo "  ✓ Nuclia SDK installed"

pip install python-dotenv --quiet
echo "  ✓ Python-dotenv installed (for environment variables)"

# Requests removed - using Nuclia SDK only

pip install pytest pytest-cov --quiet
echo "  ✓ Testing frameworks installed"

pip install schedule --quiet
echo "  ✓ Schedule installed (for automation)"

pip install pandas --quiet
echo "  ✓ Pandas installed (for data processing)"

# Step 5: Create requirements.txt
echo "Step 5: Generating requirements.txt..."
pip freeze > requirements.txt
echo "  ✓ requirements.txt created"

# Step 6: Create .env template
echo "Step 6: Creating .env template..."
cat > .env.template << 'EOF'
# Nuclia API Configuration
NUCLIA_API_KEY=your_api_key_here
NUCLIA_ACCOUNT_ID=ata-learning
NUCLIA_ZONE=aws-us-east-2-1
NUCLIA_KB_ID=investmentinsights

# RSS Feed URLs
RSS_YAHOO_FINANCE=https://feeds.finance.yahoo.com/rss/2.0/headline
RSS_MARKETWATCH=https://feeds.content.dowjones.io/public/rss/RSSMarketsMain
EOF
echo "  ✓ .env.template created"

echo ""
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Copy .env.template to .env"
echo "2. Add your Nuclia API key to .env"
echo "3. Run: source venv/bin/activate"
echo "4. Test: python test_nuclia_integration.py"
echo ""
echo "Virtual environment packages:"
pip list | grep -E "nuclia|pandas|schedule|pytest"