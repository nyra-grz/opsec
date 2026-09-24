# Installs opsec for Windows. Run in PowerShell:
#   irm https://raw.githubusercontent.com/nyra-grz/opsec/main/install.ps1 | iex
# Uninstall:
#   & ([scriptblock]::Create((irm https://raw.githubusercontent.com/nyra-grz/opsec/main/install.ps1))) -Uninstall
param(
  [switch]$Uninstall,
  [string]$BaseUrl = 'https://raw.githubusercontent.com/nyra-grz/opsec/main'
)

$ErrorActionPreference = 'Stop'
$dir = Join-Path $env:LOCALAPPDATA 'opsec'
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
$parts = @($userPath -split ';' | Where-Object { $_ })

if ($Uninstall) {
  Remove-Item -Recurse -Force $dir -ErrorAction SilentlyContinue
  [Environment]::SetEnvironmentVariable('Path', (($parts | Where-Object { $_ -ne $dir }) -join ';'), 'User')
  Write-Host 'opsec removed.'
  return
}

# --- Python detection ------------------------------------------------------

# Returns @{ Exe = <path>; Pre = @(<extra args>) } for a Python >= 3.8, or $null.
function Find-OpsecPython {
  $candidates = @()

  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py) { $candidates += , @{ Exe = $py.Source; Pre = @('-3') } }

  $p = Get-Command python -ErrorAction SilentlyContinue
  if ($p) { $candidates += , @{ Exe = $p.Source; Pre = @() } }

  $p3 = Get-Command python3 -ErrorAction SilentlyContinue
  if ($p3) { $candidates += , @{ Exe = $p3.Source; Pre = @() } }

  # Default per-user install locations that the launcher/PATH may not expose yet.
  foreach ($ver in @('Python313', 'Python312', 'Python311', 'Python310', 'Python39', 'Python38')) {
    $exe = Join-Path $env:LOCALAPPDATA "Programs\Python\$ver\python.exe"
    if (Test-Path $exe) { $candidates += , @{ Exe = $exe; Pre = @() } }
  }

  foreach ($c in $candidates) {
    try {
      & $c.Exe $c.Pre -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" 2>$null
      if ($LASTEXITCODE -eq 0) { return $c }
    } catch { }
  }
  return $null
}

$python = Find-OpsecPython

if (-not $python) {
  Write-Host 'Python 3.8+ not found - installing it now...'

  # 1) winget
  if (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host 'Trying to install Python with winget...'
    winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
    $python = Find-OpsecPython
  }

  # 2) Chocolatey
  if (-not $python -and (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host 'Trying to install Python with Chocolatey...'
    choco install python -y
    $python = Find-OpsecPython
  }

  # 3) Official python.org installer (pinned version, silent).
  if (-not $python) {
    Write-Host 'Downloading the official Python 3.12.9 installer...'
    $installer = Join-Path $env:TEMP 'python-3.12.9-amd64.exe'
    try {
      Invoke-WebRequest 'https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe' -OutFile $installer -UseBasicParsing
      Write-Host 'Running the Python installer (silent, ~1 minute)...'
      Start-Process -FilePath $installer -ArgumentList '/quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1' -Wait
    } catch {
      Write-Host "Python installer failed: $_"
    }
    $python = Find-OpsecPython
  }

  if (-not $python) {
    Write-Host 'Could not install Python automatically.' -ForegroundColor Red
    Write-Host 'Install Python 3.8 or newer from https://www.python.org/downloads/ and re-run the installer.' -ForegroundColor Red
    exit 1
  }
}

# Absolute interpreter path, recorded for the shim's last-resort fallback.
$lastResort = $python.Exe
try {
  $resolved = & $python.Exe $python.Pre -c "import sys; print(sys.executable)" 2>$null
  if ($LASTEXITCODE -eq 0 -and $resolved) { $lastResort = "$resolved".Trim() }
} catch { }

# --- Install ---------------------------------------------------------------

New-Item -ItemType Directory -Force $dir | Out-Null
Invoke-WebRequest "$BaseUrl/opsec.py" -OutFile (Join-Path $dir 'opsec.py') -UseBasicParsing

# The .cmd shim makes "opsec" work in cmd and PowerShell, and runs opsec.py with
# a real Python interpreter: prefer `py -3`, then `python`, then `python3`, and
# finally the absolute interpreter path recorded at install time.
$shim = @"
@echo off
where py >nul 2>nul || goto opsec_try_python
py -3 "%~dp0opsec.py" %*
exit /b %errorlevel%

:opsec_try_python
where python >nul 2>nul || goto opsec_try_python3
python "%~dp0opsec.py" %*
exit /b %errorlevel%

:opsec_try_python3
where python3 >nul 2>nul || goto opsec_try_fallback
python3 "%~dp0opsec.py" %*
exit /b %errorlevel%

:opsec_try_fallback
"$lastResort" "%~dp0opsec.py" %*
"@
Set-Content -Encoding ASCII (Join-Path $dir 'opsec.cmd') $shim

if ($parts -notcontains $dir) {
  [Environment]::SetEnvironmentVariable('Path', (($parts + $dir) -join ';'), 'User')
}
if (($env:Path -split ';') -notcontains $dir) { $env:Path += ";$dir" }

Write-Host ''
Write-Host 'Done. Run it with:  opsec' -ForegroundColor Green
Write-Host 'Quit with Ctrl+C. Open a new terminal window if "opsec" is not found.'
