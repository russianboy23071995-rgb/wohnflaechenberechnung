# Wohnflächenberechnung Professional

Desktop-Anwendung für Wohn- und Nutzflächenberechnungen nach WoFlV.

**NOVIKOV | PLAN & MAß**

## Funktionen

- Projekt anlegen und speichern
- Excel-Import (Archicad)
- Raum-Pool mit Bearbeitung und Drag & Drop
- Geschossverwaltung
- Flächenarten und Anrechnungsfaktoren
- Objekttexte und Vorbemerkungen
- PDF-Export im Corporate Design
- Summenberechnung mit permanenter Zusammenfassung

## Entwicklung

```bash
pip install -e .
python main.py
```

Projektdaten werden unter `~/.novikov_wohnflaechen/projects.db` gespeichert.

### PDF-Export (Entwicklung)

- **Windows:** GTK3-Runtime installieren ([WeasyPrint-Doku](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows))
- **macOS:** `brew install pango gdk-pixbuf libffi cairo`

## Desktop-App bauen

Die App wird mit **PyInstaller** als eigenständiges Programm gebündelt (kein Python auf dem Zielrechner nötig).

| Plattform | Build nur auf | Ergebnis |
|-----------|---------------|----------|
| Windows   | Windows       | `dist/Wohnflaechenberechnung/Wohnflaechenberechnung.exe` |
| macOS     | macOS         | `dist/Wohnflaechenberechnung.app` |

### Windows

1. Python 3.11+ installieren
2. Optional für PDF: [GTK3-Runtime Win64](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer) installieren
3. Im Projektordner:

```powershell
.\scripts\build_windows.ps1
```

Die fertige App liegt in `dist\Wohnflaechenberechnung\`. Den gesamten Ordner kopieren (z. B. auf einen anderen PC) und `Wohnflaechenberechnung.exe` starten.

### macOS

1. Python 3.11+ und optional Homebrew
2. Für PDF-Export: `brew install pango gdk-pixbuf libffi cairo`
3. Im Projektordner:

```bash
chmod +x scripts/build_mac.sh
./scripts/build_mac.sh
```

Die App liegt in `dist/Wohnflaechenberechnung.app`. Per Doppelklick oder `open dist/Wohnflaechenberechnung.app` starten.

Beim ersten Start unter macOS kann Gatekeeper eine Warnung anzeigen — App über „Systemeinstellungen → Datenschutz & Sicherheit“ freigeben oder mit Codesigning/Notarization für Verteilung vorbereiten.

### Verteilung

- **Windows:** Ordner `dist\Wohnflaechenberechnung` als ZIP packen
- **macOS:** `.app` in ZIP packen oder mit `hdiutil` ein DMG erstellen

## Architektur

```
src/wohnflaechen/
├── domain/          # Entitäten, Enums, Repository-Interfaces
├── application/     # Use Cases / Services
├── infrastructure/  # SQLite, Excel-Import
└── presentation/    # PySide6 UI, PDF
```
