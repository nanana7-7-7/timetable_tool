@echo off
cd /d %~dp0
python timetable.py --next
if %ERRORLEVEL% neq 0 (
  echo.
  echo Something went wrong. Check config.json and libraries.
)
echo.
pause
