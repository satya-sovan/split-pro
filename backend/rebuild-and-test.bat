@echo off
echo Rebuilding backend container...
cd /d C:\Dev\split-pro\backend
docker-compose down
docker-compose build backend
docker-compose up -d
echo.
echo Container rebuilt successfully!
echo To run tests, execute: docker-compose exec backend pytest tests/ -v


