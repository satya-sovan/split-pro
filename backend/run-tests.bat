@echo off
echo Running tests...
cd /d C:\Dev\split-pro\backend
docker-compose exec backend pytest tests/ -v
pause

