@echo off
REM ============================================
REM FINLY Build Script for Windows
REM ============================================

echo.
echo ========================================
echo    FINLY - Windows Build
echo ========================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

REM Check if npm dependencies are installed
if not exist "node_modules" (
    echo [INFO] Installing dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
)

echo [INFO] Building FINLY for Windows...
npm run build

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo    Build successful!
    echo ========================================
    echo.
    echo Find your portable exe at:
    echo    dist\FINLY-Portable.exe
    echo.
) else (
    echo.
    echo [ERROR] Build failed!
)

pause
