@echo off
echo ================================================
echo Shot Ledger - Optimized Build Script
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/5] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing anyway...
)

echo.
echo [2/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo.
    echo Troubleshooting:
    echo 1. Try: pip install --upgrade setuptools wheel
    echo 2. Run: python -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo [3/5] Installing PyInstaller and dependencies...
pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo.
echo [4/5] Building executable...
echo This may take 1-3 minutes...
echo.

REM Clean previous builds
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul
if exist ShotLedger.spec del /q ShotLedger.spec 2>nul

REM Build dengan optimasi untuk Windows
pyinstaller --onefile --windowed --name "ShotLedger" ^
    --add-data "ui;ui" ^
    --add-data "utils;utils" ^
    --icon "favicon.ico" 2>nul || echo (No icon found, building without icon...) ^
    --hidden-import "customtkinter" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL._tkinter_finder" ^
    --hidden-import "cv2" ^
    --hidden-import "pandas" ^
    --hidden-import "openpyxl" ^
    --hidden-import "openpyxl.styles" ^
    --hidden-import "openpyxl.worksheet" ^
    --hidden-import "numpy" ^
    --hidden-import "tkinter" ^
    --hidden-import "os" ^
    --hidden-import "sys" ^
    --hidden-import "pathlib" ^
    --hidden-import "json" ^
    --hidden-import "threading" ^
    --hidden-import "datetime" ^
    --exclude-module "torch" ^
    --exclude-module "torchvision" ^
    --exclude-module "torchaudio" ^
    --exclude-module "tensorflow" ^
    --exclude-module "transformers" ^
    --exclude-module "matplotlib" ^
    --collect-all "customtkinter" ^
    --collect-all "PIL" ^
    main.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo.
    echo Common solutions:
    echo 1. Close all Python processes: taskkill /f /im python.exe 2>nul
    echo 2. Delete build/dist folders: rmdir /s /q build dist
    echo 3. Run as Administrator
    echo 4. Try: pyinstaller --clean
    echo.
    pause
    exit /b 1
)

echo.
echo [5/5] Cleaning up...
if exist build rmdir /s /q build 2>nul
if exist ShotLedger.spec del /q ShotLedger.spec 2>nul
if exist __pycache__ rmdir /s /q __pycache__ 2>nul

echo.
echo ================================================
echo BUILD COMPLETED SUCCESSFULLY! 🎉
echo ================================================
echo.
echo 📁 Output: dist\ShotLedger.exe
echo.
echo 📏 File Size:
for /f "tokens=3" %%a in ('dir dist\ShotLedger.exe ^| find "ShotLedger.exe"') do (
    echo   Size: %%a bytes
)
echo.
echo ⚡ Quick Test:
echo   Run: dist\ShotLedger.exe
echo.
echo 📦 To create installer:
echo   1. Download Inno Setup: https://jrsoftware.org/isdl.php
echo   2. Create installer.iss (template below)
echo   3. Compile with Inno Setup
echo.
echo ================================================
echo Inno Setup Script Template (save as installer.iss):
echo ================================================
echo [Setup]
echo AppName=Shot Ledger
echo AppVersion=1.0.0
echo DefaultDirName={autopf}\ShotLedger
echo DefaultGroupName=Shot Ledger
echo OutputDir=Installer
echo OutputBaseFilename=ShotLedger_Setup
echo Compression=lzma2
echo SolidCompression=yes
echo 
echo [Files]
echo Source: "dist\ShotLedger.exe"; DestDir: "{app}"
echo Source: "README.md"; DestDir: "{app}"; Flags: isreadme
echo 
echo [Icons]
echo Name: "{group}\Shot Ledger"; Filename: "{app}\ShotLedger.exe"
echo Name: "{autodesktop}\Shot Ledger"; Filename: "{app}\ShotLedger.exe"
echo Name: "{group}\Uninstall Shot Ledger"; Filename: "{uninstallexe}"
echo ================================================
echo.
pause