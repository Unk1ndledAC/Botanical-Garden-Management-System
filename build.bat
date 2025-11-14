@echo off
pyinstaller -F -w ^
  --add-data "schema.sql;." ^
  --add-data "botanic;botanic" ^
  main.py
echo.
echo Packaging completed, saved to ./dist/main.exe
pause