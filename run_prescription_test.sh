#!/bin/bash
echo "Activating virtual environment..."
source .venv/bin/activate || source .venv/Scripts/activate

echo "Installing required packages..."
pip install -r requirements.txt

echo "Running prescription workflow test..."
python test_prescription_workflow.py 