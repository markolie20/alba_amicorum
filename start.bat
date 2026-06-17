@echo off
set PATH=C:\Program Files\PostgreSQL\18\bin;%PATH%
set PROJECT=C:\Users\molie\Documents\School\ADS\Minor\innovative_data_vis\alba_amicorum

start "Backend" cmd /k "cd /d "%PROJECT%" && .venv\Scripts\activate.bat && uvicorn backend.api.main:app --reload"
start "Frontend" cmd /k "cd /d "%PROJECT%\client" && npm run dev"
