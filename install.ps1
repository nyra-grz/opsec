# Installs opsec for Windows. Run in PowerShell:
#   irm https://raw.githubusercontent.com/nyra-grz/opsec/main/install.ps1 | iex
# Uninstall:
#   & ([scriptblock]::Create((irm https://raw.githubusercontent.com/nyra-grz/opsec/main/install.ps1))) -Uninstall
param([switch]$Uninstall)

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

New-Item -ItemType Directory -Force $dir | Out-Null
Invoke-WebRequest 'https://raw.githubusercontent.com/nyra-grz/opsec/main/opsec.ps1' -OutFile (Join-Path $dir 'opsec.ps1') -UseBasicParsing

# the .cmd shim makes "opsec" work in cmd and PowerShell without touching the execution policy
Set-Content -Encoding ASCII (Join-Path $dir 'opsec.cmd') @'
@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0opsec.ps1" %*
'@

if ($parts -notcontains $dir) {
  [Environment]::SetEnvironmentVariable('Path', (($parts + $dir) -join ';'), 'User')
}
if (($env:Path -split ';') -notcontains $dir) { $env:Path += ";$dir" }

Write-Host ''
Write-Host 'Done. Run it with:  opsec   (or "sudo opsec" on Windows 11 with sudo enabled)' -ForegroundColor Green
Write-Host 'Quit with Ctrl+C. Open a new terminal window if "opsec" is not found.'
