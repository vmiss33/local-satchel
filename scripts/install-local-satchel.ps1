<#
.SYNOPSIS
Installs Local Satchel for the current Windows user.

.DESCRIPTION
This script is intended to be the simple Windows install path for non-developers.
It creates an app-managed Python virtual environment under LocalAppData, installs
Local Satchel into it, and creates a `satchel.cmd` launcher under
LocalAppData\LocalSatchel\bin.

Examples:
  powershell -ExecutionPolicy Bypass -File .\scripts\install-local-satchel.ps1
  powershell -ExecutionPolicy Bypass -File .\scripts\install-local-satchel.ps1 -SourcePath C:\Users\you\Downloads\local-satchel
  powershell -ExecutionPolicy Bypass -File .\scripts\install-local-satchel.ps1 -SourceUrl https://github.com/vmiss33/local-satchel/archive/refs/heads/main.zip
#>

param(
    [string]$SourcePath,
    [string]$SourceUrl = "https://github.com/vmiss33/local-satchel/archive/refs/heads/main.zip",
    [switch]$SkipPathUpdate
)

$ErrorActionPreference = "Stop"

function Write-Step($Message) {
    Write-Host "==> $Message"
}

function Find-Python {
    $candidates = @(
        "py -3",
        "python"
    )

    foreach ($candidate in $candidates) {
        $parts = $candidate -split " "
        $exe = $parts[0]
        $args = @($parts | Select-Object -Skip 1) + @("--version")
        try {
            $versionOutput = & $exe @args 2>&1
            if ($LASTEXITCODE -eq 0 -and "$versionOutput" -match "Python 3\.(1[0-9]|[2-9][0-9])") {
                return $parts
            }
        }
        catch {
            continue
        }
    }

    return $null
}

function Install-PythonIfMissing {
    $python = Find-Python
    if ($python) {
        return $python
    }

    $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
    if (-not $winget) {
        throw "Local Satchel needs Python 3.10 or newer. Install Python from https://www.python.org/downloads/windows/ and re-run this installer."
    }

    Write-Step "Python 3.10+ was not found. Installing Python with Windows Package Manager."
    & winget.exe install --exact --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        throw "Python install failed. Install Python from https://www.python.org/downloads/windows/ and re-run this installer."
    }

    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
    $python = Find-Python
    if (-not $python) {
        throw "Python was installed, but this terminal cannot find it yet. Open a new PowerShell window and re-run the Local Satchel installer."
    }
    return $python
}

function Resolve-SourcePath {
    param(
        [string]$RequestedSourcePath,
        [string]$RequestedSourceUrl,
        [string]$InstallRoot
    )

    if ($RequestedSourcePath) {
        $resolved = Resolve-Path $RequestedSourcePath
        return $resolved.Path
    }

    if ($PSScriptRoot) {
        $repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
        if (Test-Path (Join-Path $repoRoot "pyproject.toml")) {
            return $repoRoot.Path
        }
    }

    $downloadRoot = Join-Path $InstallRoot "download"
    $zipPath = Join-Path $downloadRoot "local-satchel.zip"
    $extractRoot = Join-Path $downloadRoot "extract"
    New-Item -ItemType Directory -Force -Path $downloadRoot | Out-Null
    if (Test-Path $extractRoot) {
        Remove-Item -Recurse -Force $extractRoot
    }
    New-Item -ItemType Directory -Force -Path $extractRoot | Out-Null

    Write-Step "Downloading Local Satchel from $RequestedSourceUrl"
    Invoke-WebRequest -Uri $RequestedSourceUrl -OutFile $zipPath
    Expand-Archive -Path $zipPath -DestinationPath $extractRoot -Force

    $project = Get-ChildItem -Path $extractRoot -Directory | Select-Object -First 1
    if (-not $project) {
        throw "Downloaded archive did not contain a project directory."
    }
    return $project.FullName
}

$installRoot = Join-Path $env:LOCALAPPDATA "LocalSatchel"
$appRoot = Join-Path $installRoot "app"
$venvPath = Join-Path $appRoot "venv"
$binPath = Join-Path $installRoot "bin"
$launcherPath = Join-Path $binPath "satchel.cmd"

Write-Host "Local Satchel installer"
Write-Host "Pack, run, and connect local AI models."
Write-Host ""

New-Item -ItemType Directory -Force -Path $appRoot, $binPath | Out-Null

$python = Install-PythonIfMissing
$source = Resolve-SourcePath -RequestedSourcePath $SourcePath -RequestedSourceUrl $SourceUrl -InstallRoot $installRoot

Write-Step "Using source: $source"
Write-Step "Creating app environment: $venvPath"
& $python[0] @($python | Select-Object -Skip 1) -m venv $venvPath

$venvPython = Join-Path $venvPath "Scripts\python.exe"
$venvSatchel = Join-Path $venvPath "Scripts\satchel.exe"

Write-Step "Installing Local Satchel"
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install $source

if (-not (Test-Path $venvSatchel)) {
    throw "Install finished, but satchel.exe was not created at $venvSatchel"
}

$launcher = @"
@echo off
"$venvSatchel" %*
"@
Set-Content -Path $launcherPath -Value $launcher -Encoding ASCII

if (-not $SkipPathUpdate) {
    $currentUserPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $pathEntries = @()
    if ($currentUserPath) {
        $pathEntries = $currentUserPath -split ";" | Where-Object { $_ }
    }
    if ($pathEntries -notcontains $binPath) {
        $newUserPath = (($pathEntries + $binPath) -join ";")
        [Environment]::SetEnvironmentVariable("Path", $newUserPath, "User")
        Write-Step "Added launcher folder to your user PATH: $binPath"
    }
}

Write-Step "Checking this PC"
& $launcherPath check

Write-Host ""
Write-Host "Local Satchel is installed."
Write-Host "Open a new terminal, then run:"
Write-Host "  satchel check"
Write-Host "  satchel pack recommended"
Write-Host "  satchel run"
Write-Host "  satchel test"
Write-Host "  satchel connect hermes"
Write-Host "  satchel stop"
Write-Host ""
Write-Host "If this terminal cannot find 'satchel' yet, use:"
Write-Host "  $launcherPath check"
