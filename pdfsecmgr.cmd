@echo off
:: Set the exact, absolute path to your Python project
set "PROJECT_DIR=C:\Users\USER\code\PDF-Security-Mgr"

:: Navigate to the project folder regardless of where this script is called from
cd /d "%PROJECT_DIR%"

echo [INFO] Preparing to start PDF Security Suite...

:: Activate the virtual environment if it exists
IF EXIST "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [INFO] Activated 'venv'
) ELSE IF EXIST ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo [INFO] Activated '.venv'
) ELSE IF EXIST "env\Scripts\activate.bat" (
    call env\Scripts\activate.bat
    echo [INFO] Activated 'env'
) ELSE (
    echo [WARNING] No virtual environment found. Attempting to run globally...
)

:: Run the Python application
python main.py

:: Keep the window open if the app crashes so you can read any errors
pause