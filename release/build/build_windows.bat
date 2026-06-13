@echo off
setlocal

if exist dist rmdir /s /q dist

pyinstaller --noconfirm --clean "Minecraft Mod Translator Gemini.spec"

if exist build rmdir /s /q build

endlocal
