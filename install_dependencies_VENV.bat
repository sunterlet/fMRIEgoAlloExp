@echo off
echo === fMRI Navigation Experiment - Virtual Environment Installer ===
echo.
echo This script will create a virtual environment called "Sun-Navigation"
echo and install all required packages for the fMRI experiments.
echo.
echo This ensures your experiments don't interfere with other users.
echo.
pause

echo Creating virtual environment "Sun-Navigation"...
python -m venv Sun-Navigation

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to create virtual environment!
    echo Please make sure Python is installed and venv module is available.
    echo.
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call Sun-Navigation\Scripts\activate.bat

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to activate virtual environment!
    echo.
    pause
    exit /b 1
)

echo.
echo Upgrading pip in virtual environment...
python -m pip install --upgrade pip

echo.
echo Installing dependencies in virtual environment...
python install_dependencies.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo.
    call Sun-Navigation\Scripts\deactivate.bat
    pause
    exit /b 1
)

echo.
echo Creating activation script for easy access...
echo @echo off > run_experiments.bat
echo echo Activating Sun-Navigation environment... >> run_experiments.bat
echo call Sun-Navigation\Scripts\activate.bat >> run_experiments.bat
echo echo. >> run_experiments.bat
echo echo Virtual environment is now active! >> run_experiments.bat
echo echo You can now run your fMRI experiments. >> run_experiments.bat
echo echo. >> run_experiments.bat
echo echo To deactivate, type: deactivate >> run_experiments.bat
echo echo. >> run_experiments.bat
echo cmd /k >> run_experiments.bat

echo.
echo === Installation Complete! ===
echo.
echo Virtual environment "Sun-Navigation" has been created with all dependencies.
echo.
echo To use the environment:
echo 1. Double-click "run_experiments.bat" to activate the environment
echo 2. Or manually run: Sun-Navigation\Scripts\activate.bat
echo 3. Then run your experiments: python snake.py practice
echo.
echo To deactivate the environment, type: deactivate
echo.
pause 