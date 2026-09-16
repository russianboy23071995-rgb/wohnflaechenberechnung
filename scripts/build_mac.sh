#!/usr/bin/env bash
# Baut die macOS-Desktop-App (.app) mit PyInstaller.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Projekt: $ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 nicht gefunden." >&2
  exit 1
fi

echo "==> Abhängigkeiten installieren..."
python3 -m pip install -e ".[build]" --quiet

if ! python3 -c "import weasyprint" 2>/dev/null; then
  echo "Hinweis: WeasyPrint benötigt oft Homebrew-Bibliotheken:"
  echo "  brew install pango gdk-pixbuf libffi cairo"
fi

echo "==> PyInstaller-Build starten..."
python3 -m PyInstaller packaging/wohnflaechen.spec --noconfirm --clean

APP_PATH="dist/Wohnflaechenberechnung.app"
if [[ -d "$APP_PATH" ]]; then
  echo ""
  echo "Build fertig: $ROOT/$APP_PATH"
  echo "Starten mit: open \"$APP_PATH\""
else
  DIST_DIR="$ROOT/dist/Wohnflaechenberechnung"
  if [[ -d "$DIST_DIR" ]]; then
    echo ""
    echo "Build fertig: $DIST_DIR"
  else
    echo "Build-Verzeichnis nicht gefunden." >&2
    exit 1
  fi
fi
