@echo off
REM Stott Exam - Account Manager. Double-click this file, no terminal needed.
REM Uses the Cosmos DB key in api\local.settings.json (that file stays on
REM your laptop only - it is never uploaded to GitHub).
chcp 65001 >nul
cd /d "%~dp0api"
where node >nul 2>nul
if errorlevel 1 (
  echo Node.js not found. Please install Node.js first.
  pause
  exit /b 1
)

:MENU
echo.
echo  ===== Stott Exam - Account Manager =====
echo   1. List accounts
echo   2. Create account
echo   3. Reset password (when someone forgets it)
echo   4. Disable account
echo   5. Enable account
echo   0. Exit
echo.
choice /c 123450 /n /m "Press 0-5: "
if errorlevel 6 exit /b 0
if errorlevel 5 goto ENABLE
if errorlevel 4 goto DISABLE
if errorlevel 3 goto RESET
if errorlevel 2 goto CREATE
goto LIST

:LIST
echo.
node scripts\stott_admin.js list
pause
goto MENU

:CREATE
echo.
echo  TIP: password must be 6+ characters.
set /p alogin=Login - lowercase, no spaces:
set /p aname=Full name:
set /p apass=Password:
node scripts\stott_admin.js create "%alogin%" "%aname%" "%apass%"
pause
goto MENU

:RESET
echo.
echo  TIP: new password must be 6+ characters.
set /p rlogin=Login to reset:
set /p rpass=New password:
node scripts\stott_admin.js reset "%rlogin%" "%rpass%"
pause
goto MENU

:DISABLE
echo.
set /p dlogin=Login to disable:
node scripts\stott_admin.js disable "%dlogin%"
pause
goto MENU

:ENABLE
echo.
set /p elogin=Login to enable:
node scripts\stott_admin.js enable "%elogin%"
pause
goto MENU
