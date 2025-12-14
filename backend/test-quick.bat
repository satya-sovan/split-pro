@echo off
echo Rebuilding backend...
cd /d C:\Dev\split-pro\backend
docker-compose build backend
docker-compose up -d
echo.
echo Running tests...
docker-compose exec backend pytest tests/ -v --tb=short
pause

