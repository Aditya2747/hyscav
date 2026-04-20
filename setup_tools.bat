@echo off
REM Mythril + Echidna Docker Setup for Windows

echo 1. Docker daemon running? docker ps
docker ps

echo 2. Login GitHub (create PAT at github.com/settings/tokens)
set /p USERNAME=GitHub username: 
set /p TOKEN=GitHub PAT: 
docker login ghcr.io -u %USERNAME% -p %TOKEN%

echo 3. Pull images...
docker pull ghcr.io/crytic/mythril:latest
docker pull ghcr.io/crytic/echidna:latest

echo 4. Test HySCAV...
python main.py analyze contracts/ReentrancyTest.sol

echo Setup done! Check report_ReentrancyTest.sol.xlsx
pause

