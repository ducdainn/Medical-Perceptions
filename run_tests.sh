#!/bin/bash
echo "Activating virtual environment..."
source .venv/bin/activate || source .venv/Scripts/activate

echo "Installing required packages..."
pip install -r requirements.txt

echo "Running tests..."
python test_login_register.py 