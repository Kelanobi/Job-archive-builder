@echo off
setlocal
cd /d "%~dp0\.."
py -3.12 -m pip install -r requirements-dev.txt
py -3.12 -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name "Qualitrol Job Archive - Kelvin" ^
  --icon "assets\branding\qualitrol-q.ico" ^
  --add-data "assets\branding\qualitrol-q.ico;assets\branding" ^
  --collect-all customtkinter ^
  --hidden-import win32com.client ^
  main.py
if errorlevel 1 exit /b 1
echo Built: dist\Qualitrol Job Archive - Kelvin.exe
