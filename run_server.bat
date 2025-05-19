@echo off
echo Activating virtual environment...
call .venv\Scripts\activate

echo Installing required packages...
pip install -r requirements.txt

echo Running Django development server...
python manage.py runserver

pause 