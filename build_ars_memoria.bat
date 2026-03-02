@echo off
echo Binding the Ars Memoria...
pyinstaller --noconfirm --onefile --windowed --icon="ars_sigil.ico" --add-data "Scriptorium.html;." --add-data "Tabula Scripta.html;." main.py
echo.
echo Build Complete! Check the 'dist' folder.
pause