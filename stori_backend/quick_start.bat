@echo off
echo ============================================
echo STORI NBFC - Django Backend Quick Start
echo ============================================
echo.

echo Step 1: Creating virtual environment...
python -m venv venv

echo Step 2: Activating virtual environment...
call venv\Scripts\activate

echo Step 3: Installing dependencies...
pip install -r requirements.txt

echo Step 4: Creating .env file...
copy env_template.txt .env

echo Step 5: Running migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo ============================================
echo Setup complete!
echo ============================================
echo.
echo Next steps:
echo 1. Edit .env file with your database credentials
echo 2. Create superuser: python manage.py createsuperuser
echo 3. Run server: python manage.py runserver 8000
echo.
echo Press any key to exit...
pause >nul


