$ErrorActionPreference = 'Stop'
$root = 'C:\Users\tanuj\Documents\AIM002_Member1_Starter_Implementation'
$app = Join-Path $root 'accident_damage_assessment'
$template = Join-Path $app 'templates\index.html'
$css = Join-Path $app 'static\style.css'
$js = Join-Path $app 'static\region-report.js'
if (!(Test-Path $template)) { throw "Template not found: $template" }
if (!(Test-Path $css)) { throw "Stylesheet not found: $css" }
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$backup = Join-Path $root "region_report_backup_$stamp"
New-Item -ItemType Directory -Path $backup -Force | Out-Null
Copy-Item $template (Join-Path $backup 'index.html')
Copy-Item $css (Join-Path $backup 'style.css')
$patch = $PSScriptRoot
$html = Get-Content $template -Raw
# Remove the previous 3D section and its script include.
$html = [regex]::Replace($html, '(?s)\s*<!-- AIM002 interactive 3D vehicle inspection -->.*?</section>\s*<script src="/static/vehicle-3d\.js" defer></script>', '')
$html = [regex]::Replace($html, '(?s)\s*<section id="aim002-vehicle-3d".*?</section>\s*<script src="/static/vehicle-3d\.js" defer></script>', '')
$html = [regex]::Replace($html, '\s*<script[^>]+src="/static/vehicle-3d\.js"[^>]*></script>', '')
if ($html -notmatch 'id="aim002-region-report"') {
  $section = Get-Content (Join-Path $patch 'region-report.html') -Raw
  if ($html -match '</body>') { $html = $html -replace '</body>', ($section + "`r`n</body>") } else { $html += "`r`n$section" }
}
if ($html -notmatch '/static/region-report.js') {
  $replacement = '<script src="/static/region-report.js" defer></script>' + [Environment]::NewLine + '</body>'
  $html = $html.Replace('</body>', $replacement)
}
Set-Content $template $html -Encoding UTF8
$style = Get-Content $css -Raw
# Remove appended old 3D styles if present.
$style = [regex]::Replace($style, '(?s)/\* AIM002 interactive vehicle inspection viewer \*/.*$', '')
$style = [regex]::Replace($style, '(?s)/\* AIM002 interactive 3D vehicle inspection viewer \*/.*$', '')
$style = [regex]::Replace($style, '(?s)/\* AIM002 light theme \+ regional damage report \*/.*$', '')
$light = Get-Content (Join-Path $patch 'region-report.css') -Raw
Set-Content $css ($style + "`r`n" + $light) -Encoding UTF8
Copy-Item (Join-Path $patch 'region-report.js') $js -Force
Write-Host "`n3D vehicle viewer removed. Region-wise damage report and light theme installed." -ForegroundColor Green
Write-Host "Backup saved at: $backup"
Write-Host 'Restart Flask and hard-refresh the browser (Ctrl+Shift+R).'
Write-Host 'Note: the report listens for the event aim002:analysis-complete. See README for backend integration.'
