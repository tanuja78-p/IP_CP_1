$ErrorActionPreference = "Stop"
$root = "C:\Users\tanuj\Documents\AIM002_Member1_Starter_Implementation"
$source = Join-Path $PSScriptRoot "accident_damage_assessment"
$target = Join-Path $root "accident_damage_assessment"
if (-not (Test-Path $target)) { throw "Project folder not found: $target" }
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backup = Join-Path $root "frontend_backup_$stamp"
New-Item -ItemType Directory -Path $backup -Force | Out-Null
foreach ($rel in @("templates\index.html","static\style.css","static\app.js")) {
  $dest = Join-Path $target $rel
  $src = Join-Path $source $rel
  if (-not (Test-Path $src)) { throw "Patch file missing: $src" }
  if (Test-Path $dest) {
    $backupDest = Join-Path $backup $rel
    New-Item -ItemType Directory -Path (Split-Path $backupDest -Parent) -Force | Out-Null
    Copy-Item $dest $backupDest -Force
  }
  Copy-Item $src $dest -Force
}
Write-Host "`nFrontend updated successfully." -ForegroundColor Green
Write-Host "Backup saved at: $backup"
Write-Host "Now start the app using the .venv311 environment and test /api/health."
