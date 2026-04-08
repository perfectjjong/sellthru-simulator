@echo off
chcp 65001 >nul 2>&1
echo ============================================
echo  SellThru Simulator API Cache Scheduler
echo  매주 수요일 09:00 자동 실행
echo ============================================
echo.

:: Get script directory
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Find Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python이 설치되어 있지 않습니다.
    pause
    exit /b 1
)

:: Task name
set "TASK_NAME=SellThru_API_Cache_Weekly"

:: Delete existing task if any
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1

:: Register new task: every Wednesday at 09:00
schtasks /Create /TN "%TASK_NAME%" ^
    /TR "python \"%SCRIPT_DIR%\api_cache_weather_oil.py\"" ^
    /SC WEEKLY /D WED /ST 09:00 ^
    /RL HIGHEST ^
    /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] 스케줄러 등록 완료!
    echo   작업 이름: %TASK_NAME%
    echo   실행 주기: 매주 수요일 09:00
    echo   실행 파일: %SCRIPT_DIR%\api_cache_weather_oil.py
    echo.

    :: Run once now to create initial cache
    echo [INFO] 초기 캐시 데이터 생성 중...
    python "%SCRIPT_DIR%\api_cache_weather_oil.py"
    echo.

    :: Deploy to GitHub Pages
    echo [INFO] GitHub Pages 배포 중...
    cd /d "%SCRIPT_DIR%"
    git add api_cache_data.json api_cache_weather_oil.py
    git commit -m "Add API cache data"
    git push
    echo.
    echo [DONE] 완료!
) else (
    echo.
    echo [ERROR] 스케줄러 등록 실패. 관리자 권한으로 실행해주세요.
)

echo.
pause
