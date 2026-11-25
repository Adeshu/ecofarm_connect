#!/bin/bash

# Sustainable Farming Platform - Setup Script
set -e

echo "🌱 Setting up Sustainable Farming Platform"
echo "=========================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing Python packages..."
pip install -r requirements.txt

# Setup database
echo "🗄️  Setting up database..."
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo "👤 Creating admin user..."
python manage.py createsuperuser

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Setup completed! Run: python manage.py runserver"
