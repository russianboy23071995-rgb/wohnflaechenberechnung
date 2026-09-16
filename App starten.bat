@echo off
cd /d "%~dp0"
echo Starte NOVIKOV Auftragsverwaltung ...
python main.py
if errorlevel 1 (
    echo.
    echo Start fehlgeschlagen. Ist Python installiert?
    echo Alternativ: Doppelklick auf
    echo dist\Wohnflaechenberechnung\Wohnflaechenberechnung.exe
    pause
)
