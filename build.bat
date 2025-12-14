@echo off
REM Build and Run Script for SAHASplit

echo ========================================
echo   SAHASplit - Build Script
echo ========================================
echo.

REM Step 1: Build Vue/Vite Frontend
echo [Step 1/3] Building Vue.js frontend...
cd frontend

if exist "node_modules" (
    echo   node_modules exists, skipping pnpm install
) else (
    echo   Installing pnpm dependencies...
    call pnpm install
    if errorlevel 1 (
        echo ERROR: pnpm install failed!
        cd ..
        exit /b 1
    )
)

echo   Running pnpm build...
call pnpm run build
if errorlevel 1 (
    echo ERROR: pnpm build failed!
    cd ..
    exit /b 1
)

cd ..
echo   Frontend build complete
echo.

REM Step 2: Check if dist directory exists
if exist "frontend\dist" (
    echo [Step 2/3] Frontend build found in frontend/dist/ directory
) else (
    echo ERROR: frontend/dist/ directory not found after build!
    exit /b 1
)
echo.

REM Step 3: Docker build and run
echo [Step 3/3] Building and starting Docker containers...
docker-compose down 2>nul
docker-compose up --build -d

if errorlevel 1 (
    echo.
    echo ERROR: Docker build failed!
    echo Check the error messages above.
    exit /b 1
)

echo.
echo ========================================
echo   SUCCESS!
echo ========================================
echo.
echo   Services are running!
echo   App: http://localhost:8012
echo   API: http://localhost:8012/api
echo   API Docs: http://localhost:8012/api/docs
echo.
echo   View logs:
echo   docker logs -f sahasplit-app
echo.
pause

