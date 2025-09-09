@echo off
echo === Enhanced fMRI Navigation Experiment - Dependency Installer ===
echo.
echo This script will check for Python installation and install all required packages.
echo.
pause

python install_dependencies_enhanced.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Installation failed! Please check the error messages above.
    echo.
    echo If Python is not installed, please download it from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
) else (
    echo.
    echo Installation completed successfully!
    echo.
    echo You can now run your fMRI experiments.
    echo.
)

echo Press any key to exit...
pause > nul 