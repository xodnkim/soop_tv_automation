@echo off
setlocal EnableDelayedExpansion

:: ================================================================
:: EDIT THESE TWO VALUES FOR YOUR ENVIRONMENT
:: ================================================================
set DEVICE_NAME=LG_SMART
set APP_ID=com.soop.stg.app

echo ================================================================
echo  DEVICE_NAME : %DEVICE_NAME%
echo  APP_ID      : %APP_ID%
echo ================================================================
echo.

echo [1/2] Closing existing app (if any)...
call ares-launch -d %DEVICE_NAME% -c %APP_ID% >nul 2>&1
timeout /t 2 /nobreak >nul
echo.

echo [2/2] Launching app in debug mode...
echo ================================================================
echo  * NOTE: The TV debug bridge needs to stay running.
echo  * Do NOT close this window!
echo  * Look for the "Application Debugging - http://..." URL below.
echo ================================================================
echo.
call ares-inspect -d %DEVICE_NAME% %APP_ID%
