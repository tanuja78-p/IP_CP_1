(() => {
"use strict";
const $ = id => document.getElementById(id);
const esc = v => String(v ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const num = v => { const n = Number(v); return Number.isFinite(n) ? n : null; };
const TIER_LABEL = {high:"HIGH", moderate:"MODERATE", low:"LOW"};
const TIER_COLOR = {high:"#d64545", moderate:"#d98a1b", low:"#16875d"};
const PHASES = ["Preparing image","Enhancing details","Inspecting regions","Estimating damage","Building report"];

let selectedFile = null, objectUrl = null, result = null, view = null, toastTimer = null;

/* ---------- small UI helpers ---------- */
function toast(msg, isErr){
  const t = $("toast"); t.textContent = msg; t.className = "toast" + (isErr ? " err" : ""); t.hidden = false;
  clearTimeout(toastTimer); toastTimer = setTimeout(() => t.hidden = true, 3800);
}
function setMessage(msg, isErr){ const el = $("uploadMessage"); el.textContent = msg; el.className = isErr ? "err" : ""; }
function setStep(n){
  document.querySelectorAll("#pipeline .pipeline-step").forEach(s => {
    const i = Number(s.dataset.step);
    s.classList.toggle("active", i === n);
    s.classList.toggle("done", i < n);
  });
}
function countUp(el, to, decimals, suffix){
  const start = performance.now(), dur = 900;
  const tick = now => {
    const p = Math.min(1, (now - start) / dur), e = 1 - Math.pow(1 - p, 3);
    el.textContent = (to * e).toFixed(decimals) + (suffix || "");
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

/* ---------- file handling ---------- */
function handleFile(file){
  if (!file) return;
  const ok = ["image/jpeg","image/png","image/bmp","image/webp"];
  if (!ok.includes(file.type)) { toast("Please choose a JPG, PNG, BMP or WEBP image.", true); return; }
  if (file.size > 25*1024*1024) { toast("Image must be smaller than 25 MB.", true); return; }
  selectedFile = file;
  if (objectUrl) URL.revokeObjectURL(objectUrl);
  objectUrl = URL.createObjectURL(file);
  const prev = $("selectedImagePreview"); prev.src = objectUrl; prev.style.display = "block";
  $("fileName").textContent = file.name; $("fileName").classList.add("has-file");
  $("fileDetails").textContent = (file.size/1024/1024).toFixed(2) + " MB | " + file.type;
  $("analyzeButton").disabled = false;
  $("uploadZone").classList.add("has-image");
  setMessage("Image ready for assessment.");
  setStep(1);
}

/* ---------- analysis call ---------- */
async function analyze(){
  if (!selectedFile) { toast("Please select a vehicle image first.", true); return; }
  const btn = $("analyzeButton");
  btn.disabled = true; btn.textContent = "Analyzing..."; btn.classList.add("busy");
  $("resultsSection").hidden = true;
  setStep(2);

  const prog = $("analysisProgress"), bar = $("progressBar"), list = $("phaseList");
  prog.hidden = false;
  list.innerHTML = PHASES.map((p,i) => `<li data-i="${i}">${p}</li>`).join("");
  let i = 0;
  const paint = () => {
    $("progressText").textContent = PHASES[i] + "...";
    bar.style.width = Math.min(92, 10 + i * 20) + "%";
    list.querySelectorAll("li").forEach((li, k) => { li.className = k < i ? "done" : (k === i ? "on" : ""); });
  };
  paint();
  const timer = setInterval(() => { if (i < PHASES.length - 1) { i++; paint(); } }, 1400);

  try {
    const form = new FormData(); form.append("image", selectedFile);
    const res = await fetch("/api/analyze", { method: "POST", body: form });
    let data; try { data = await res.json(); } catch { throw new Error("The server did not return a valid response."); }
    if (!res.ok || !data.success) throw new Error(data.error || "Analysis failed (HTTP " + res.status + ").");
    result = data;
    window.aim002LastResult = data;      // kept for any other script that reads it
    setStep(3);
    bar.style.width = "100%";
    await renderReport(data);
    setStep(4);
    setMessage("Assessment complete. Scroll down to read the report.");
  } catch (err) {
    console.error(err);
    setStep(1);
    setMessage(err.message || "Image processing failed.", true);
    toast(err.message || "Image processing failed. Check the Flask terminal.", true);
  } finally {
    clearInterval(timer);
    setTimeout(() => { prog.hidden = true; }, 500);
    btn.disabled = !selectedFile; btn.textContent = "Analyze Vehicle"; btn.classList.remove("busy");
  }
}

/* ---------- data helpers ---------- */
function tierOfIndicator(v){ return v >= 0.5 ? "high" : v >= 0.2 ? "moderate" : "low"; }
function tierFromText(s){
  s = String(s || "").toLowerCase();
  if (/(severe|high|major|critical)/.test(s)) return "high";
  if (/(moderate|medium)/.test(s)) return "moderate";
  if (/(low|minor|slight|light|none)/.test(s)) return "low";
  return null;
}
function findDims(obj, depth){
  if (!obj || typeof obj !== "object" || (depth || 0) > 4) return null;
  const w = num(obj.image_width ?? obj.img_width ?? obj.frame_width ?? obj.original_width ?? obj.width);
  const h = num(obj.image_height ?? obj.img_height ?? obj.frame_height ?? obj.original_height ?? obj.height);
  if (w > 50 && h > 50 && !("x" in obj && "y" in obj)) return {w, h};
  for (const k of ["image_size","original_size","size","shape","resolution"]) {
    const v = obj[k];
    if (Array.isArray(v) && v.length >= 2) {
      const a = num(v[0]), b = num(v[1]);
      if (a > 50 && b > 50) return k === "shape" ? {w: b, h: a} : {w: a, h: b};
    }
  }
  for (const k of Object.keys(obj)) {
    if (k === "regions") continue;
    const d = findDims(obj[k], (depth || 0) + 1); if (d) return d;
  }
  return null;
}
function normalizeRegions(p4){
  const raw = Array.isArray(p4.regions) ? p4.regions : [];
  return raw.map((r, idx) => {
    const bb = Array.isArray(r.bbox) ? r.bbox : null;
    const x = num(r.x ?? (bb && bb[0])), y = num(r.y ?? (bb && bb[1]));
    const w = num(r.width ?? r.w ?? (bb && bb[2])), h = num(r.height ?? r.h ?? (bb && bb[3]));
    let ind = num(r.damage_indicator ?? r.indicator ?? r.score);
    if (ind != null && ind > 1) ind = ind / 100;
    return { id: r.region_id ?? idx + 1, n: idx + 1, area: num(r.area ?? r.contour_area) ?? ((w && h) ? w*h : 0),
             x, y, w, h, ind: ind ?? 0, hasBox: [x,y,w,h].every(v => v != null) };
  });
}
const ROW = ["Upper","Middle","Lower"], COL = ["left","center","right"];
function zoneOf(r, ref){
  if (!r.hasBox) return null;
  const cx = (r.x + r.w/2) / ref.w, cy = (r.y + r.h/2) / ref.h;
  const c = Math.min(2, Math.max(0, Math.floor(cx * 3))), rw = Math.min(2, Math.max(0, Math.floor(cy * 3)));
  return { row: rw, col: c, key: rw*3 + c };
}
function zoneName(z){ return (z.row === 1 && z.col === 1) ? "Center of frame" : ROW[z.row] + "-" + COL[z.col]; }
function zonePhrase(z){ return (z.row === 1 && z.col === 1) ? "center of the photo" : ROW[z.row].toLowerCase() + "-" + COL[z.col] + " of the photo"; }
function sizeClass(a){ return a < 100 ? "tiny" : a < 1000 ? "small" : a < 5000 ? "medium" : "large"; }

function regionWhy(r){
  const sz = sizeClass(r.area), pct = (r.ind*100).toFixed(1);
  const t = tierOfIndicator(r.ind);
  const base = t === "high" ? "Strong damage signal" : t === "moderate" ? "Noticeable damage signal" : "Weak damage signal";
  const meaning = {
    tiny: "A very small mark, which often means a scratch, scuff, chip or a speck that may not be real damage.",
    small: "A small area, typical of a scratch, scrape or minor dent.",
    medium: "A medium-sized area, consistent with a dent, crease or paint damage across part of a panel.",
    large: "A large area, which can mean panel deformation or damage spread over a whole section."
  }[sz];
  return `${base} (${pct}%) on a ${sz} contour of ${Math.round(r.area)} px². ${meaning}`;
}
function regionAction(r){
  const t = tierOfIndicator(r.ind);
  if (t === "high") return "Photograph this spot up close first, then have it checked by a mechanic.";
  if (t === "moderate") return "Look for dents, scratches and surface deformation here.";
  return "Confirm whether this is real damage or just a reflection, shadow or dirt.";
}

/* ---------- build the report model ---------- */
function buildModel(data){
  const p4 = data.p4 || {};
  const regions = normalizeRegions(p4);
  let ref = findDims(data.p1) || findDims(data.p2) || findDims(data.p3) || findDims(p4) || null;
  return { data, p4, regions, ref };
}
async function ensureRef(m){
  const boxes = m.regions.filter(r => r.hasBox);
  const maxX = Math.max(0, ...boxes.map(r => r.x + r.w)), maxY = Math.max(0, ...boxes.map(r => r.y + r.h));
  if (!m.ref) {
    await new Promise(res => { const im = new Image(); im.onload = () => { m.ref = {w: im.naturalWidth, h: im.naturalHeight}; res(); }; im.onerror = res; im.src = objectUrl; });
  }
  if (!m.ref) m.ref = {w: Math.max(maxX, 1), h: Math.max(maxY, 1)};
  if (maxX > m.ref.w * 1.02 || maxY > m.ref.h * 1.02) m.ref = {w: Math.max(m.ref.w, maxX), h: Math.max(m.ref.h, maxY)};
}
function analyseZones(m){
  const zones = {};
  m.regions.forEach(r => {
    r.zone = zoneOf(r, m.ref);
    if (!r.zone) return;
    const z = zones[r.zone.key] || (zones[r.zone.key] = { ...r.zone, regions: [], weight: 0, max: 0 });
    z.regions.push(r); z.weight += r.ind * (1 + Math.log10(r.area + 1)); z.max = Math.max(z.max, r.ind);
  });
  m.zones = zones;
  m.topZone = Object.values(zones).sort((a,b) => b.weight - a.weight)[0] || null;
  m.topRegion = [...m.regions].sort((a,b) => b.ind - a.ind || b.area - a.area)[0] || null;
  const max = m.topRegion ? m.topRegion.ind : 0;
  const pct = num(m.p4.damage_percent);
  m.tier = tierFromText(m.p4.severity) || (pct != null ? (pct >= 15 ? "high" : pct >= 5 ? "moderate" : "low") : null) || (m.regions.length ? tierOfIndicator(max) : "none");
  if (!m.regions.length && !pct) m.tier = "none";
  m.counts = { high: 0, moderate: 0, low: 0 };
  m.regions.forEach(r => m.counts[tierOfIndicator(r.ind)]++);
}

/* ---------- text generation ---------- */
function narrativeHTML(m){
  const n = m.regions.length, pct = num(m.p4.damage_percent), sev = m.p4.severity ? String(m.p4.severity) : null;
  if (!n) {
    return `<p>The pipeline did not return any candidate damage regions for this photo${pct != null ? `, and estimates <b>${pct.toFixed(2)}%</b> of the surface as affected` : ""}.</p>
            <p>This does <b>not</b> prove the vehicle is undamaged. Small, dark or low-contrast damage can be missed. Try a sharper, evenly lit photo that shows the suspected area close-up.</p>`;
  }
  const parts = [];
  parts.push(`<p><b>What was found:</b> the analysis detected <b>${n} candidate damage region${n>1?"s":""}</b>${pct != null ? `, covering about <b>${pct.toFixed(2)}%</b> of the vehicle surface` : ""}${sev ? `. Overall severity is rated <b>${esc(sev)}</b>` : ""}. Of these, ${m.counts.high} show a high indicator, ${m.counts.moderate} moderate and ${m.counts.low} low.</p>`);
  if (m.topZone) {
    const z = m.topZone, inTop = z.regions.length;
    const share = Math.round(inTop / n * 100);
    parts.push(`<p><b>Where:</b> the damage concentrates in the <b>${zonePhrase(z)}</b>, which holds ${inTop} of ${n} regions (${share}%). ${z.row === 2 ? "That is the lower part of the frame, where bumpers, side skirts and wheels normally sit. " : z.row === 0 ? "That is the upper part of the frame, where the roof, windscreen and top of the body sit. " : "That is the middle band of the frame, where doors and side panels normally sit. "}${share >= 60 ? "Because the marks are grouped together, they may come from a single impact or scrape." : "The marks are spread out, so they may come from separate incidents or from several marks along one side."}</p>`);
  }
  if (m.topRegion) {
    const r = m.topRegion;
    parts.push(`<p><b>Strongest signal:</b> <b>Region ${esc(r.id)}</b> with a ${(r.ind*100).toFixed(1)}% damage indicator (${Math.round(r.area)} px²${r.zone ? ", " + zonePhrase(r.zone) : ""}). ${sizeClass(r.area)==="tiny"||sizeClass(r.area)==="small" ? "Regions this small usually point to surface damage such as scratches, scuffs or paint chips rather than major deformation." : "Its size suggests damage that is worth a close physical check."}</p>`);
  }
  return parts.join("");
}
function findingsList(m){
  const n = m.regions.length, out = [];
  if (!n) { out.push("No candidate regions were returned for this image."); return out; }
  const areas = m.regions.map(r => r.area).sort((a,b) => a - b), med = areas[Math.floor(areas.length/2)];
  out.push(`${n} candidate region${n>1?"s":""} found: ${m.counts.high} high, ${m.counts.moderate} moderate, ${m.counts.low} low.`);
  if (m.topZone) out.push(`Most affected area: ${zoneName(m.topZone)} (${m.topZone.regions.length} region${m.topZone.regions.length>1?"s":""}, peak indicator ${(m.topZone.max*100).toFixed(1)}%).`);
  if (m.topRegion) out.push(`Highest single region: Region ${m.topRegion.id} at ${(m.topRegion.ind*100).toFixed(1)}%.`);
  out.push(`Typical region size is ${Math.round(med)} px² (${sizeClass(med)}).`);
  const pct = num(m.p4.damage_percent); if (pct != null) out.push(`Estimated damaged surface: ${pct.toFixed(2)}% of the vehicle.`);
  const sc = num(m.p4.severity_score); if (sc != null) out.push(`Assessment score: ${sc.toFixed(3)}.`);
  return out;
}
function buildActions(m){
  const n = m.regions.length, acts = [], rows = new Set(Object.values(m.zones).map(z => z.row));
  const topIds = [...m.regions].sort((a,b) => b.ind - a.ind).slice(0,3).map(r => r.id);
  if (!n) {
    return [
      {t:"Retake the photo in better light", why:"No regions were detected. Glare, shadows or distance can hide damage from the algorithm."},
      {t:"Walk around the vehicle and check by eye", why:"An empty result is not proof of no damage, so a visual check is still needed."},
      {t:"Get a professional opinion if there was any collision", why:"Hidden and structural damage cannot be seen in a photograph."}
    ];
  }
  if (m.tier === "high") acts.push({t:"Avoid driving until it has been inspected", why:`${m.counts.high} region${m.counts.high!==1?"s":""} reached a high damage indicator, so steering, lights, wheels or structural parts could be affected.`, urgent:true});
  acts.push({t:"Compare the markers with the original photo", why:"The indicator is a feature-based score, not a confirmed result. Reflections, shadows and dirt can create false regions."});
  if (m.tier !== "low" && topIds.length) acts.push({t:`Take close-up photos of Region${topIds.length>1?"s":""} ${topIds.join(", ")}`, why:"These have the highest indicators and are the ones a workshop will want to see first."});
  if (rows.has(2)) acts.push({t:"Check the bumper, side skirts, wheels and underbody", why:"Some marked regions are in the lower part of the frame, where these parts are located."});
  if (rows.has(1)) acts.push({t:"Check doors, side panels and panel gaps", why:"Some marked regions are in the middle band of the frame, where doors and panels are located."});
  if (rows.has(0)) acts.push({t:"Check the roof, windscreen, bonnet and lights", why:"Some marked regions are in the upper part of the frame."});
  if (m.topZone && m.topZone.regions.length >= 3) acts.push({t:`Look at the ${zonePhrase(m.topZone)} for one shared cause`, why:`${m.topZone.regions.length} regions cluster there, which often means one impact or scrape.`});
  if (m.tier === "low") acts.push({t:"Keep an eye on it and fix it when convenient", why:"All signals are low, which usually means cosmetic marks."});
  else acts.push({t:"Request a repair estimate from a qualified workshop", why:"Moderate or high indicators mean the damage should be priced and checked in person."});
  acts.push({t:"Arrange a physical inspection before approving any repair", why:"Photos cannot show hidden or structural damage."});
  return acts.slice(0, 6);
}
function verdictText(m){
  const T = {
    none: ["i","No damage regions detected","Nothing was flagged, but that does not guarantee the vehicle is undamaged."],
    low: ["✓","Minor visible damage","Mostly cosmetic marks were flagged. A quick check is enough."],
    moderate: ["!","Moderate visible damage","Visible damage that probably needs repair. Inspect it in person."],
    high: ["!!","Significant visible damage","Strong damage signals. Get a professional inspection promptly."]
  };
  return T[m.tier] || T.none;
}
function summaryPlain(m){
  const el = document.createElement("div"); el.innerHTML = narrativeHTML(m);
  const acts = buildActions(m).map((a,i) => `${i+1}. ${a.t} - ${a.why}`).join("\n");
  return `AutoInspect AI - Damage Assessment\nFile: ${selectedFile ? selectedFile.name : ""}\nOverall: ${verdictText(m)[1]}\n\n${el.textContent}\n\nRecommended actions:\n${acts}\n\nPreliminary image-based assessment only.`;
}

/* ---------- rendering ---------- */
async function renderReport(data){
  const m = buildModel(data);
  await ensureRef(m);
  analyseZones(m);
  view = { m, sort: "priority", filter: null, showAll: false, tab: "original", active: null };

  const [icon, title] = verdictText(m);
  const vc = $("verdictCard"); vc.dataset.tier = m.tier;
  $("verdictIcon").textContent = icon;
  $("verdictLabel").textContent = m.tier === "none" ? "RESULT" : "OVERALL: " + (TIER_LABEL[m.tier] || "");
  $("verdictTitle").textContent = title;
  $("narrative").innerHTML = narrativeHTML(m);

  const pct = num(m.p4.damage_percent), sc = num(m.p4.severity_score);
  $("resultSeverity").textContent = m.p4.severity ? String(m.p4.severity) : (m.tier === "none" ? "None found" : (TIER_LABEL[m.tier] || "-"));
  $("resultScore").textContent = sc != null ? "score " + sc.toFixed(3) : "";
  const dEl = $("resultDamage"); pct != null ? countUp(dEl, pct, 2, "%") : (dEl.textContent = "N/A");
  const rc = m.regions.length || (num(m.p4.region_count) ?? 0);
  countUp($("resultRegions"), rc, 0, "");
  $("resultRegionsSub").textContent = m.regions.length ? `${m.counts.high} high | ${m.counts.moderate} moderate | ${m.counts.low} low` : "";
  $("resultArea").textContent = m.topZone ? zoneName(m.topZone) : "Not available";
  $("resultAreaSub").textContent = m.topZone ? `${m.topZone.regions.length} region${m.topZone.regions.length>1?"s":""}, peak ${(m.topZone.max*100).toFixed(1)}%` : "";

  $("findings").innerHTML = findingsList(m).map(f => `<li>${esc(f)}</li>`).join("");
  $("actionList").innerHTML = buildActions(m).map((a,i) =>
    `<li class="${a.urgent ? "urgent" : ""}" style="animation-delay:${i*70}ms"><b>${esc(a.t)}</b><small>Why: ${esc(a.why)}</small></li>`).join("");

  buildTabs(); renderStage(); renderZones(); renderRegions();

  const sec = $("resultsSection");
  sec.hidden = false; sec.classList.remove("reveal"); void sec.offsetWidth; sec.classList.add("reveal");
  setTimeout(() => sec.scrollIntoView({behavior:"smooth", block:"start"}), 80);
}

function artifactFor(tab){
  const a = (result && result.artifacts) || {};
  return { original: objectUrl, vehicle: a.vehicle, damage: a.candidate_mask || a.damage_mask, enhanced: a.enhanced }[tab] || "";
}
function buildTabs(){
  document.querySelectorAll("#tabs .tab").forEach(b => {
    const has = !!artifactFor(b.dataset.tab);
    b.disabled = !has; b.style.opacity = has ? "" : ".4"; b.style.cursor = has ? "" : "not-allowed";
    b.classList.toggle("active", b.dataset.tab === view.tab);
  });
}
function renderStage(){
  const img = $("stageImg"), src = artifactFor(view.tab);
  $("stageEmpty").hidden = !!src; $("stage").hidden = !src;
  if (!src) return;
  img.classList.add("swap");
  setTimeout(() => { img.src = src; img.onload = () => img.classList.remove("swap"); img.onerror = () => img.classList.remove("swap"); }, 120);
  drawMarkers();
}
function drawMarkers(){
  const m = view.m, box = $("markers");
  box.innerHTML = m.regions.filter(r => r.hasBox).map(r => {
    const t = tierOfIndicator(r.ind), cx = (r.x + r.w/2)/m.ref.w*100, cy = (r.y + r.h/2)/m.ref.h*100;
    const w = Math.max(r.w/m.ref.w*100, 1.6), h = Math.max(r.h/m.ref.h*100, 1.6*m.ref.w/m.ref.h);
    const top = m.topRegion && m.topRegion.id === r.id;
    const dim = view.filter != null && (!r.zone || r.zone.key !== view.filter);
    return `<div class="mk ${top ? "hi" : ""} ${dim ? "dim" : ""} ${view.active === r.id ? "active" : ""}" data-id="${esc(r.id)}" data-n="${esc(r.id)}"
      style="--c:${TIER_COLOR[t]};left:${cx}%;top:${cy}%;width:${w}%;height:${h}%;min-width:16px;min-height:16px">
      <span class="tip"><b>Region ${esc(r.id)}</b> - ${TIER_LABEL[t]}<br>${(r.ind*100).toFixed(1)}% indicator, ${Math.round(r.area)} px²${r.zone ? "<br>" + esc(zoneName(r.zone)) : ""}</span></div>`;
  }).join("");
  box.classList.toggle("off", !$("markerToggle").checked);
}
function renderZones(){
  const m = view.m; let html = "";
  for (let k = 0; k < 9; k++) {
    const z = m.zones[k], row = Math.floor(k/3), col = k%3;
    const label = (row === 1 && col === 1) ? "Center" : ROW[row] + " " + COL[col];
    if (!z) { html += `<div class="zone"><span>${label}</span></div>`; continue; }
    const t = tierOfIndicator(z.max), top = m.topZone && m.topZone.key === k;
    html += `<div class="zone has ${top ? "top" : ""} ${view.filter === k ? "sel" : ""}" data-k="${k}" style="--c:${TIER_COLOR[t]}"><div><b>${z.regions.length}</b>${label}</div></div>`;
  }
  $("zoneGrid").innerHTML = html;
  $("zoneClear").hidden = view.filter == null;
}
function sortedRegions(){
  const m = view.m; let list = [...m.regions];
  if (view.filter != null) list = list.filter(r => r.zone && r.zone.key === view.filter);
  if (view.sort === "size") list.sort((a,b) => b.area - a.area);
  else if (view.sort === "position") list.sort((a,b) => (a.y ?? 0) - (b.y ?? 0) || (a.x ?? 0) - (b.x ?? 0));
  else list.sort((a,b) => b.ind - a.ind || b.area - a.area);
  return list;
}
function renderRegions(){
  const m = view.m, all = sortedRegions(), LIMIT = 6;
  const list = view.showAll ? all : all.slice(0, LIMIT);
  $("regionSub").textContent = m.regions.length
    ? `Showing ${list.length} of ${all.length}${view.filter != null ? " in the selected area" : ""}. Click a card to find it on the photo.` : "";
  if (!m.regions.length) { $("regionList").innerHTML = `<p class="muted">No candidate regions were returned.</p>`; $("moreButton").hidden = true; return; }
  $("regionList").innerHTML = list.map((r, i) => {
    const t = tierOfIndicator(r.ind), top = m.topRegion && m.topRegion.id === r.id;
    return `<article class="rcard ${t} ${top ? "top" : ""} ${view.active === r.id ? "active" : ""}" data-id="${esc(r.id)}" style="animation-delay:${i*50}ms">
      <div class="rcard-top"><h4>Region ${esc(r.id)}${top ? `<span class="flag">MOST SEVERE</span>` : ""}</h4><span class="badge">${TIER_LABEL[t]}</span></div>
      <div class="rscore"><b>${(r.ind*100).toFixed(1)}%</b><small>damage indicator</small></div>
      <div class="bar"><i style="--w:${(r.ind*100).toFixed(1)}%" data-w="${(r.ind*100).toFixed(1)}"></i></div>
      <div class="rmeta"><span>Location<br><b>${r.zone ? esc(zoneName(r.zone)) : "Unknown"}</b></span><span>Contour area<br><b>${Math.round(r.area)} px²</b></span>
        <span>Position<br><b>${r.hasBox ? `x=${r.x}, y=${r.y}` : "N/A"}</b></span><span>Size<br><b>${r.hasBox ? `${r.w} x ${r.h} px` : "N/A"}</b></span></div>
      <p class="rwhy">${esc(regionWhy(r))}</p>
      <div class="ract"><b>Do this:</b> ${esc(regionAction(r))}</div></article>`;
  }).join("");
  requestAnimationFrame(() => document.querySelectorAll(".bar i").forEach(b => b.style.width = b.dataset.w + "%"));
  $("moreButton").hidden = all.length <= LIMIT;
  $("moreButton").textContent = view.showAll ? "Show fewer regions" : `Show all ${all.length} regions`;
}
function focusRegion(id, scrollCard){
  view.active = id;
  document.querySelectorAll(".mk").forEach(e => e.classList.toggle("active", e.dataset.id === String(id)));
  document.querySelectorAll(".rcard").forEach(e => e.classList.toggle("active", e.dataset.id === String(id)));
  if (scrollCard) { const c = document.querySelector(`.rcard[data-id="${CSS.escape(String(id))}"]`); if (c) c.scrollIntoView({behavior:"smooth", block:"center"}); }
}

/* ---------- events ---------- */
function openLightbox(){
  const clone = $("stage").cloneNode(true); clone.removeAttribute("id");
  clone.querySelectorAll("[id]").forEach(e => e.removeAttribute("id"));
  $("lightboxBody").innerHTML = ""; $("lightboxBody").appendChild(clone); $("lightbox").hidden = false;
}
function resetAll(){
  $("resultsSection").hidden = true; selectedFile = null; result = null; view = null;
  $("imageInput").value = ""; $("selectedImagePreview").style.display = "none";
  $("fileName").textContent = "No image selected"; $("fileName").classList.remove("has-file"); $("fileDetails").textContent = "";
  $("analyzeButton").disabled = true; $("uploadZone").classList.remove("has-image");
  setMessage("No image selected yet."); setStep(1);
  $("uploadSection").scrollIntoView({behavior:"smooth", block:"start"});
}

document.addEventListener("DOMContentLoaded", () => {
  const input = $("imageInput"), zone = $("uploadZone");
  $("selectImageButton").addEventListener("click", e => { e.preventDefault(); e.stopPropagation(); input.click(); });
  input.addEventListener("change", e => handleFile(e.target.files && e.target.files[0]));
  zone.addEventListener("click", e => { if (!e.target.closest("button")) input.click(); });
  zone.addEventListener("dragover", e => { e.preventDefault(); zone.classList.add("dragging"); });
  zone.addEventListener("dragleave", () => zone.classList.remove("dragging"));
  zone.addEventListener("drop", e => { e.preventDefault(); zone.classList.remove("dragging"); handleFile(e.dataTransfer.files && e.dataTransfer.files[0]); });
  zone.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); input.click(); } });
  $("analyzeButton").addEventListener("click", analyze);

  $("tabs").addEventListener("click", e => { const b = e.target.closest(".tab"); if (!b || b.disabled || !view) return; view.tab = b.dataset.tab; buildTabs(); renderStage(); });
  $("markerToggle").addEventListener("change", () => $("markers").classList.toggle("off", !$("markerToggle").checked));
  $("expandButton").addEventListener("click", openLightbox);
  $("lightboxClose").addEventListener("click", () => $("lightbox").hidden = true);
  $("lightbox").addEventListener("click", e => { if (e.target.id === "lightbox") $("lightbox").hidden = true; });
  document.addEventListener("keydown", e => { if (e.key === "Escape") $("lightbox").hidden = true; });

  $("markers").addEventListener("click", e => { const mk = e.target.closest(".mk"); if (mk) focusRegion(isNaN(mk.dataset.id) ? mk.dataset.id : Number(mk.dataset.id), true); });
  $("regionList").addEventListener("click", e => { const c = e.target.closest(".rcard"); if (c) focusRegion(isNaN(c.dataset.id) ? c.dataset.id : Number(c.dataset.id), false); });
  $("regionList").addEventListener("mouseover", e => { const c = e.target.closest(".rcard"); if (!c) return;
    document.querySelectorAll(".mk").forEach(k => k.classList.toggle("active", k.dataset.id === c.dataset.id)); });
  $("regionList").addEventListener("mouseleave", () => document.querySelectorAll(".mk").forEach(k => k.classList.toggle("active", view && String(view.active) === k.dataset.id)));

  $("zoneGrid").addEventListener("click", e => { const z = e.target.closest(".zone.has"); if (!z || !view) return;
    const k = Number(z.dataset.k); view.filter = view.filter === k ? null : k; view.showAll = true; renderZones(); renderRegions(); drawMarkers(); });
  $("zoneClear").addEventListener("click", () => { view.filter = null; renderZones(); renderRegions(); drawMarkers(); });
  $("sortControl").addEventListener("click", e => { const b = e.target.closest("button"); if (!b || !view) return;
    view.sort = b.dataset.sort; document.querySelectorAll("#sortControl button").forEach(x => x.classList.toggle("active", x === b)); renderRegions(); });
  $("moreButton").addEventListener("click", () => { view.showAll = !view.showAll; renderRegions(); });

  $("copyButton").addEventListener("click", async () => { if (!view) return;
    try { await navigator.clipboard.writeText(summaryPlain(view.m)); toast("Summary copied to clipboard."); } catch { toast("Could not copy. Select the text manually.", true); } });
  $("printButton").addEventListener("click", () => window.print());
  $("againButton").addEventListener("click", resetAll);
});
})();