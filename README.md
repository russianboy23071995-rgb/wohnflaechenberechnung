# Wohnflächenberechnung Professional

Desktop-Anwendung für Wohn- und Nutzflächenberechnungen nach WoFlV.

**NOVIKOV | PLAN & MAß**

## MVP Version 1

- Projekt anlegen und speichern
- Excel-Import (Archicad)
- Raum-Pool mit Bearbeitung
- Geschossverwaltung
- Flächenarten und Anrechnungsfaktoren
- Objekttexte
- Summenberechnung (ohne PDF-Export)

## Installation

```bash
pip install -e .
```

## Start

```bash
python main.py
```

## Architektur

```
src/wohnflaechen/
├── domain/          # Entitäten, Enums, Repository-Interfaces
├── application/     # Use Cases / Services
├── infrastructure/  # SQLite, Excel-Import
└── presentation/    # PySide6 UI
```
