@echo off
echo Activating virtual environment...
call .venv\Scripts\activate

echo Installing required packages...
pip install -r requirements.txt

echo Running prescription workflow test...
python test_prescription_workflow.py

pause