#!/bin/sh
set -eu

APP_NAME="Minecraft Mod Translator Gemini"
SPEC_FILE="Minecraft Mod Translator Gemini.spec"

rm -rf dist

python3 -m PyInstaller \
  --noconfirm \
  --clean \
  "$SPEC_FILE"

rm -rf build

printf 'Built app bundle: dist/%s.app\n' "$APP_NAME"
