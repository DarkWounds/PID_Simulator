@echo off
rem Porneste simulatorul PID: serverul FastAPI + pagina web in browser.
rem Dublu-click pe acest fisier. Opresti serverul inchizand fereastra neagra (sau Ctrl+C).
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Nu gasesc Python. Instaleaza-l de pe python.org si bifeaza "Add Python to PATH".
    pause
    exit /b
)

rem La prima rulare instaleaza pachetele din requirements.txt
python -c "import fastapi, uvicorn" >nul 2>nul
if errorlevel 1 (
    echo Instalez pachetele necesare (doar prima data^)...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Instalarea a esuat. Verifica conexiunea la internet.
        pause
        exit /b
    )
)

rem Deschide browserul dupa 2 secunde, cat porneste serverul
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8000"

echo Serverul porneste pe http://127.0.0.1:8000  (inchide fereastra ca sa-l opresti)
python -m uvicorn main:app --port 8000

echo.
echo Serverul s-a oprit. Daca a aparut o eroare de port, inseamna ca simulatorul ruleaza deja in alta fereastra.
pause
