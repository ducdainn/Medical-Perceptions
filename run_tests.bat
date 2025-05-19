@echo off
echo Activating virtual environment...
call .venv\Scripts\activate

echo Installing required packages...
pip install -r requirements.txt

echo Running tests...
python test_login_register.py

pause 