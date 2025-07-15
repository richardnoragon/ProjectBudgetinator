@echo off
REM Static Analysis Runner for ProjectBudgetinator
REM This batch file runs all static analysis tools

echo ============================================================
echo ProjectBudgetinator Static Analysis
echo ============================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Create build directory if it doesn't exist
if not exist "build" mkdir build

echo.
echo Installing/updating static analysis tools...
python -m pip install -r requirements.txt

echo.
echo ============================================================
echo Running MyPy (Type Checking)
echo ============================================================
python -m mypy src/ --config-file mypy.ini
set MYPY_EXIT=%ERRORLEVEL%

echo.
echo ============================================================
echo Running Pylint (Code Quality)
echo ============================================================
python -m pylint src/ --rcfile .pylintrc
set PYLINT_EXIT=%ERRORLEVEL%

echo.
echo ============================================================
echo Running Flake8 (Style and Basic Errors)
echo ============================================================
python -m flake8 src/ --config .flake8
set FLAKE8_EXIT=%ERRORLEVEL%

echo.
echo ============================================================
echo Running Bandit (Security Scanning)
echo ============================================================
python -m bandit -r src/ -c .bandit -f txt
set BANDIT_EXIT=%ERRORLEVEL%

echo.
echo ============================================================
echo Running Black (Code Formatting Check)
echo ============================================================
python -m black --check --diff src/
set BLACK_EXIT=%ERRORLEVEL%

echo.
echo ============================================================
echo Running isort (Import Sorting Check)
echo ============================================================
python -m isort --check-only --diff src/
set ISORT_EXIT=%ERRORLEVEL%

echo.
echo ============================================================
echo STATIC ANALYSIS SUMMARY
echo ============================================================
echo.

if %MYPY_EXIT%==0 (
    echo MyPy:   PASSED
) else (
    echo MyPy:   FAILED (Exit Code: %MYPY_EXIT%^)
)

if %PYLINT_EXIT%==0 (
    echo Pylint: PASSED
) else (
    echo Pylint: FAILED (Exit Code: %PYLINT_EXIT%^)
)

if %FLAKE8_EXIT%==0 (
    echo Flake8: PASSED
) else (
    echo Flake8: FAILED (Exit Code: %FLAKE8_EXIT%^)
)

if %BANDIT_EXIT%==0 (
    echo Bandit: PASSED
) else (
    echo Bandit: FAILED (Exit Code: %BANDIT_EXIT%^)
)

if %BLACK_EXIT%==0 (
    echo Black:  PASSED
) else (
    echo Black:  FAILED (Exit Code: %BLACK_EXIT%^)
)

if %ISORT_EXIT%==0 (
    echo isort:  PASSED
) else (
    echo isort:  FAILED (Exit Code: %ISORT_EXIT%^)
)

echo.
REM Calculate overall result
set /a TOTAL_ERRORS=%MYPY_EXIT%+%PYLINT_EXIT%+%FLAKE8_EXIT%+%BANDIT_EXIT%+%BLACK_EXIT%+%ISORT_EXIT%

if %TOTAL_ERRORS%==0 (
    echo Overall Result: ALL PASSED ✓
    echo.
    echo No issues found! Your code follows all configured standards.
) else (
    echo Overall Result: SOME FAILED ✗
    echo.
    echo Please review the output above and fix any issues.
    echo.
    echo To automatically fix formatting issues, run:
    echo   python -m black src/
    echo   python -m isort src/
)

echo.
echo Analysis complete. Results saved to build/ directory.
echo ============================================================

REM Keep window open
pause
