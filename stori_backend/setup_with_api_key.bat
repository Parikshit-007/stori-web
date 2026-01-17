@echo off
echo ============================================
echo STORI NBFC - Complete Setup with API Key
echo ============================================
echo.

echo Step 1: Creating virtual environment...
python -m venv venv

echo Step 2: Activating virtual environment...
call venv\Scripts\activate

echo Step 3: Installing dependencies...
pip install -r requirements.txt

echo Step 4: Creating .env file...
if not exist .env (
    copy env_template.txt .env
    echo .env file created
) else (
    echo .env file already exists
)

echo Step 5: Running migrations...
python manage.py makemigrations
python manage.py migrate

echo Step 6: Generating permanent API key...
python manage.py generate_api_key admin "Production API Key"

echo.
echo ============================================
echo Setup complete!
echo ============================================
echo.
echo Your permanent API key has been generated above.
echo SAVE IT SECURELY - you'll use it for all API requests!
echo.
echo Usage:
echo   Add header to all requests: X-API-Key: your_key
echo.
echo To run server:
echo   python manage.py runserver 8000
echo.
echo For more details, see AUTHENTICATION_GUIDE.txt
echo.
pause

