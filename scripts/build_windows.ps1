#Requires -Version 5.1
<#
.SYNOPSIS
    Baut die Windows-Desktop-App mit PyInstaller.

.DESCRIPTION
    Erzeugt dist\Wohnflaechenberechnung\ mit Wohnflaechenberechnung.exe.
    Für PDF-Export werden GTK3-Runtime-DLLs ins Build-Verzeichnis kopiert,
    falls die Runtime installiert ist.
#>
param(
    [switch]$SkipGtkCopy
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "==> Projekt: $Root"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python nicht gefunden. Bitte Python 3.11+ installieren."
}

Write-Host "==> Abhängigkeiten installieren..."
python -m pip install -e ".[build]" --quiet

Write-Host "==> PyInstaller-Build starten..."
python -m PyInstaller packaging/wohnflaechen.spec --noconfirm --clean

$DistDir = Join-Path $Root "dist\Wohnflaechenberechnung"
if (-not (Test-Path $DistDir)) {
    throw "Build-Verzeichnis nicht gefunden: $DistDir"
}

if (-not $SkipGtkCopy) {
    $GtkCandidates = @(
        "${env:ProgramFiles}\GTK3-Runtime Win64\bin",
        "${env:ProgramFiles(x86)}\GTK3-Runtime Win64\bin"
    )
    $GtkBin = $GtkCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

    if ($GtkBin) {
        Write-Host "==> GTK3-Runtime gefunden: $GtkBin"
        Copy-Item -Path (Join-Path $GtkBin "*.dll") -Destination $DistDir -Force
        Write-Host "    DLLs kopiert (PDF-Export)."
    } else {
        Write-Warning @"
GTK3-Runtime nicht gefunden. Die App startet, aber PDF-Export kann fehlschlagen.
Installieren: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
Danach dieses Skript erneut ausführen oder DLLs manuell nach $DistDir kopieren.
"@
    }
}

Write-Host ""
Write-Host "Build fertig: $DistDir"
Write-Host "Starten mit: $(Join-Path $DistDir 'Wohnflaechenberechnung.exe')"
