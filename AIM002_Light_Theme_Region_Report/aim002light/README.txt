AIM002 — Light Theme + Region-wise Damage Report

INSTALL
1. Extract this ZIP.
2. Open PowerShell in the extracted folder.
3. Run:
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\INSTALL_REGION_REPORT.ps1
4. Restart Flask and hard-refresh the browser (Ctrl+Shift+R).

The installer backs up index.html and style.css in a timestamped folder inside the project. It removes the old 3D viewer section/script, adds region report cards, and applies a light palette.

IMPORTANT DATA CONNECTION
The report UI is ready to render region-wise data. It listens for this browser event after your existing analysis API returns its JSON result:

window.dispatchEvent(new CustomEvent('aim002:analysis-complete', { detail: result }));

The result should contain one of these array keys: regions, region_results, regional_damage, damage_regions, region_analysis, or areas. Each region item should ideally contain name/region/area, damage_percentage/percentage/score, severity/level, and optionally description/recommendation/next_step.

Example:
window.dispatchEvent(new CustomEvent('aim002:analysis-complete', {detail:{regions:[
 {name:'Front Bumper',damage_percentage:72,severity:'High',recommendation:'Inspect for deformation and replace damaged mounting clips.'},
 {name:'Left Door',damage_percentage:34,severity:'Moderate'},
 {name:'Rear Panel',damage_percentage:12,severity:'Low'}
]}}));

If the current backend does not return region-wise values, the report cannot infer genuine region scores. To connect it accurately, share accident_damage_assessment/static/app.js and the Python file that returns the /api/analyze response; then the event can be added at the exact response-handling point.
