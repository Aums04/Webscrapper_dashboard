@echo off
setlocal enabledelayedexpansion
echo Starting AI News Scraper Enhanced Version...
echo.

REM Check if we're in the enhanced_version directory
if not exist enhanced_scraper.py (
    echo Please run this script from the enhanced_version directory
    pause
    exit /b 1
)

REM Create assets directories if they don't exist
if not exist assets mkdir assets
if not exist assets\csv mkdir assets\csv
if not exist assets\json mkdir assets\json

REM Activate virtual environment (check parent directory first)
if exist ..\env\Scripts\activate.bat (
    echo Found virtual environment in parent directory
    call ..\env\Scripts\activate.bat
) else if exist env\Scripts\activate.bat (
    echo Found local virtual environment
    call env\Scripts\activate.bat
) else (
    echo Creating new virtual environment...
    python -m venv env
    call env\Scripts\activate.bat
)

REM Install/update requirements
echo Installing dependencies...
pip install -r requirements.txt

:menu
echo.
echo ========================================
echo Select scraping mode:
echo   1. Single-site scraping (enhanced_scraper.py)
echo   2. Multi-site scraping (multi_site_scraper.py)
echo   3. Both (run both modes)
echo   4. Exit
echo ========================================
set /p mode=Enter your choice (1/2/3/4): 

if "%mode%"=="1" goto single
if "%mode%"=="2" goto multi
if "%mode%"=="3" goto both
if "%mode%"=="4" goto end
echo Invalid choice. Please try again.
goto menu

:single
echo.
echo Running single-site scraper...
python enhanced_scraper.py
echo.
echo Generating analysis report for single-site data...
python analyze_data.py
goto finish

:multi
echo.
echo Running multi-site scraper...
python multi_site_scraper.py
echo.
echo Generating analysis report for multi-site data...
python analyze_data.py --multi
goto finish

:both
echo.
echo Running single-site scraper...
python enhanced_scraper.py
echo.
echo Running multi-site scraper...
python multi_site_scraper.py
echo.
echo Generating analysis report for single-site data...
python analyze_data.py
echo.
echo Generating analysis report for multi-site data...
python analyze_data.py --multi
goto finish

:finish
echo.
echo ========================================
echo Scraping complete! Check the assets folder for results.
echo. 
echo Available files:
echo - assets\csv\ainews.csv (Single-site CSV data)
echo - assets\json\ainews.json (Single-site JSON data)
echo - assets\csv\ai_ml_multisite_YYYY-MM-DD.csv (Multi-site CSV data)
echo - assets\json\ai_ml_multisite_YYYY-MM-DD.json (Multi-site JSON data)
echo - analysis_report.txt (Single-site analysis)
echo - analysis_report.txt (Multi-site analysis, overwritten each run)
echo - scraper.log (Scraping logs)
echo.
echo To view the dashboard, run: python dashboard.py
echo Then open http://localhost:5000 in your browser
echo ========================================
echo.
pause

:end
endlocal
