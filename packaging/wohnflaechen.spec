# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller-Spezifikation für Wohnflächenberechnung (Windows & macOS)."""

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

ROOT = Path(SPECPATH).parent
SRC = ROOT / "src"

block_cipher = None

datas: list = []
binaries: list = []
hiddenimports: list = collect_submodules("wohnflaechen")

for package in ("weasyprint", "jinja2", "openpyxl", "pandas", "PIL"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(package)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

datas += [
    (
        str(SRC / "wohnflaechen/presentation/pdf/templates"),
        "wohnflaechen/presentation/pdf/templates",
    ),
    (
        str(SRC / "wohnflaechen/presentation/pdf/static"),
        "wohnflaechen/presentation/pdf/static",
    ),
]

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(SRC)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Wohnflaechenberechnung",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Wohnflaechenberechnung",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="Wohnflaechenberechnung.app",
        icon=None,
        bundle_identifier="de.novikov-plan-mass.wohnflaechenberechnung",
        info_plist={
            "CFBundleName": "Wohnflächenberechnung",
            "CFBundleDisplayName": "Wohnflächenberechnung",
            "NSHighResolutionCapable": True,
        },
    )
