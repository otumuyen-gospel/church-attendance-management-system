@echo off
REM Start Django server with HTTPS support
REM Simple method without requiring runserver_plus or Werkzeug

echo.
echo ================================================
echo Face Recognition Server - HTTPS Startup
echo ================================================
echo.

REM Check if certs exist
if not exist "certs\localhost.crt" (
    echo Generating SSL certificates...
    python generate_cert.py
    if errorlevel 1 (
        echo Failed to generate certificates!
        pause
        exit /b 1
    )
)

echo.
echo Starting HTTPS server...
echo.

REM Run the simple HTTPS server
python run_https.py

pause
