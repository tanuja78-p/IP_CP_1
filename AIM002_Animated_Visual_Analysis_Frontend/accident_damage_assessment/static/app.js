(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  const state = { file: null, result: null, urls: {}, view: "original", objectUrl: null, toastTimer: null };

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
  }
  function number(value, digits=2) {
    if (value === null || value === undefined || value === "" || !Number.isFinite(Number(value))) return "N/A";
    return Number(value).toLocaleString(undefined, {maximumFractionDigits: digits});
  }
  function getSeverity(result) {
    const p4 = result?.p4 || {};
    return String(p4.severity || "Not available");
  }
  function toast(message) {
    const el = $("toast"); if (!el) return;
    el.textContent = message; el.classList.add("show");
    clearTimeout(state.toastTimer); state.toastTimer = setTimeout(() => el.classList.remove("show"), 3200);
  }
  function setProgress(on, text="Analyzing image…") {
    $("analysisProgress").hidden = !on;
    $("progressText").textContent = text;
    $("analyzeButton").disabled = on || !state.file;
    $("selectImageButton").disabled = on;
    $("uploadMessage").textContent = on ? "Please keep this page open while processing." : (state.file ? "Image ready for assessment." : "No image selected yet.");
  }
  function selectFile(file) {
    if (!file) return;
    if (!file.type.startsWith("image/")) { toast("Please choose a valid image file."); return; }
    if (file.size > 25 * 1024 * 1024) { toast("Image is larger than 25 MB. Choose a smaller image."); return; }
    state.file = file; state.result = null;
    document.body.classList.add("has-selected-image");
    if (state.objectUrl) URL.revokeObjectURL(state.objectUrl);
    state.objectUrl = URL.createObjectURL(file);
    $("selectedImagePreview").src = state.objectUrl;
    $("fileName").textContent = file.name;
    $("fileDetails").textContent = `${(file.size/1024/1024).toFixed(2)} MB · ${file.type || "Image file"}`;
    $("fileRow").hidden = false; $("dropZone").classList.add("has-file");
    $("analyzeButton").disabled = false;
    $("uploadMessage").textContent = "Ready when you are.";
    $("imageViewStatus").textContent = "Input image selected";
    setViewer("original");
    resetReport();
  }
  function clearFile() {
    state.file = null; state.result = null;
    document.body.classList.remove("has-selected-image");
    if (state.objectUrl) URL.revokeObjectURL(state.objectUrl);
    state.objectUrl = null;
    $("imageInput").value = ""; $("fileRow").hidden = true; $("analyzeButton").disabled = true;
    $("uploadMessage").textContent = "No image selected yet.";
    $("imageViewStatus").textContent = "Waiting for analysis";
    resetSummary(); resetReport(); setViewer("original");
  }
  function resetSummary() {
    $("severityScore").textContent = "—"; $("severityValue").textContent = "Awaiting image";
    $("severityDescription").textContent = "Run an assessment to view the estimated severity.";
    $("damagePercentValue").textContent = "—"; $("regionCountValue").textContent = "—";
    $("vehicleAreaValue").textContent = "—"; $("damageAreaValue").textContent = "—";
    $("damageMeterLabel").textContent = "Not assessed"; $("damageMeterFill").style.width = "0%";
    $("regionBadge").textContent = "0"; $("regionList").innerHTML = '<div class="muted-empty">Detected regions will be listed here after analysis.</div>';
    ["p1Status","p2Status","p3Status","p4Status"].forEach(id => { $(id).textContent = "Pending"; $(id).parentElement.classList.remove("done"); });
    $("resultId").textContent = "Not generated"; $("printReportButton").disabled = true;
  }
  function resetReport() {
    $("reportContent").className = "report-empty";
    $("reportContent").innerHTML = '<div class="report-empty-mark">✓</div><div><strong>Report not generated yet</strong><p>After analysis, this section will show the severity, damage estimate, findings, and recommended next steps.</p></div>';
    resetSummary();
  }
  function artifactUrl(key) {
    const value = state.urls[key];
    if (!value) return "";
    return value.startsWith("http") ? value : value;
  }
  function setViewer(view) {
    state.view = view;
    document.querySelectorAll(".viewer-tab").forEach(btn => btn.classList.toggle("active", btn.dataset.view === view));
    const img = $("mainResultImage"), empty = document.querySelector(".viewer-empty"), unavailable = $("imageUnavailable");
    let src = "";
    if (view === "original") src = state.objectUrl || "";
    else if (view === "vehicle") src = artifactUrl("vehicle");
    else if (view === "damage") src = artifactUrl("candidate_mask") || artifactUrl("damage_mask");
    else if (view === "enhanced") src = artifactUrl("enhanced");
    else if (["falsecolor","grayscale","edges"].includes(view)) src = state.objectUrl || "";
    $("viewerCaption").textContent = ({original: state.file?.name || "Original image", vehicle:"Vehicle segmentation output", damage:"Candidate damage mask", enhanced:"Enhanced image", falsecolor:"False-colour visual filter · preview only", grayscale:"Grayscale visual filter · preview only", edges:"High-contrast edge-style preview · preview only"})[view];
    $("openImageButton").disabled = !src;
    $("imageViewStatus").textContent = state.result ? "Analysis output" : (state.file ? "Input image selected" : "Waiting for analysis");
    if (!src) { img.hidden = true; img.removeAttribute("src"); empty.hidden = view !== "original" || !!state.file; unavailable.hidden = !state.result || view === "original"; if (view === "original" && state.file) { img.src = state.objectUrl; img.hidden = false; empty.hidden = true; unavailable.hidden = true; } return; }
    empty.hidden = true; unavailable.hidden = true; img.hidden = false;
    img.classList.toggle("visual-filter-falsecolor", view === "falsecolor");
    img.classList.toggle("visual-filter-grayscale", view === "grayscale");
    img.classList.toggle("visual-filter-edges", view === "edges");
    img.onerror = () => { img.hidden = true; unavailable.hidden = true; empty.hidden = true; $("viewerCaption").textContent = "Output image unavailable"; $("openImageButton").disabled = true; };
    img.onload = () => { img.hidden = false; };
    img.src = src;
  }
  function renderRegions(regions, fallbackCount) {
    const list = $("regionList");
    $("regionBadge").textContent = String(fallbackCount ?? regions.length);
    if (!regions.length) { list.innerHTML = '<div class="muted-empty">No individual regions were returned by the pipeline. This does not necessarily mean there is no damage.</div>'; return; }
    list.innerHTML = regions.map((r,i) => `<div class="region-row"><div class="region-number">${String(i+1).padStart(2,"0")}</div><div><strong>Region ${i+1}</strong><small>Position: ${escapeHtml(number(r.x,0))}, ${escapeHtml(number(r.y,0))} · Size: ${escapeHtml(number(r.width,0))} × ${escapeHtml(number(r.height,0))}</small></div><span class="region-value">${escapeHtml(number(r.area,0))} px²</span></div>`).join("");
  }
  function recommendations(severity, percent, regionCount) {
    const s = severity.toLowerCase();
    if (s.includes("high") || percent >= 15) return {label:"Priority inspection",title:"Arrange a professional inspection promptly",summary:"The image-based estimate indicates a potentially substantial visible damage area. Do not rely on the image alone to determine roadworthiness.",actions:["Photograph the affected areas from multiple angles.","Have a qualified repair professional inspect structural and safety-related components.","Avoid driving if steering, lights, wheels, airbags, or structural parts may be affected."]};
    if (s.includes("moderate") || percent >= 5) return {label:"Inspection advised",title:"Review the affected areas",summary:"The estimate suggests visible damage that may need repair. A physical inspection is needed to determine its true extent.",actions:["Capture close-up and wide-angle photographs.","Check nearby panels, lights, sensors, and alignment.","Request a repair estimate from a qualified workshop."]};
    return {label:"Review recommended",title:"Review the image and confirm condition",summary:"The system estimates a lower visible damage level, but small or hidden damage may not be detected reliably.",actions:["Inspect the vehicle in good lighting.","Check for hidden damage and functional issues.","Seek a professional opinion if the vehicle was involved in a collision."]};
  }
  function renderReport(result) {
    const p1=result.p1||{},p2=result.p2||{},p3=result.p3||{},p4=result.p4||{};
    const regions=Array.isArray(p4.regions)?p4.regions:[];
    const severity=getSeverity(result);
    const percent=Number(p4.damage_percent ?? 0);
    const score=p4.severity_score !== undefined && p4.severity_score !== null ? Number(p4.severity_score) : null;
    const count=Number(p4.region_count ?? regions.length);
    const advice=recommendations(severity,Number.isFinite(percent)?percent:0,count);
    const severityClass=severity.toLowerCase().includes("high")?"high":severity.toLowerCase().includes("moderate")?"moderate":severity.toLowerCase().includes("low")?"low":"";
    $("severityScore").textContent=score===null||!Number.isFinite(score)?"N/A":number(score,3);
    $("severityValue").textContent=severity;
    $("severityDescription").textContent=advice.summary;
    $("severityRing").style.borderColor=severityClass==="high"?"var(--red)":severityClass==="moderate"?"var(--amber)":severityClass==="low"?"var(--green)":"#313b54";
    $("damagePercentValue").textContent=`${number(percent)}%`;
    $("regionCountValue").textContent=number(count,0);
    $("vehicleAreaValue").textContent=number(p4.vehicle_area,0);
    $("damageAreaValue").textContent=number(p4.damage_area,0);
    $("damageMeterLabel").textContent=`${number(percent)}% estimated`;
    $("damageMeterFill").style.width=`${Math.max(0,Math.min(100,Number.isFinite(percent)?percent:0))}%`;
    renderRegions(regions,count);
    $("recommendationContent").innerHTML=`<div class="recommendation-title">${escapeHtml(advice.title)}</div><p class="recommendation-summary">${escapeHtml(advice.summary)}</p><ul class="recommendation-list">${advice.actions.map(a=>`<li>${escapeHtml(a)}</li>`).join("")}</ul><div class="basis-note">Guidance is based on the image-derived severity and damage estimate. It is not a safety certification or repair quote.</div>`;
    const stages=[["p1Status",p1],["p2Status",p2],["p3Status",p3],["p4Status",p4]];
    stages.forEach(([id,obj])=>{const el=$(id);const ok=Object.keys(obj||{}).length>0;el.textContent=ok?"Returned":"No details";el.parentElement.classList.toggle("done",ok);});
    $("resultId").textContent=result.result_id||"Not provided";
    $("printReportButton").disabled=false;
    const fileName=state.file?.name||result.input_filename||"Uploaded image";
    $("reportContent").className="report-content";
    $("reportContent").innerHTML=`
      <div class="report-lead"><div><span class="section-kicker">ASSESSMENT RESULT</span><h4>Vehicle damage summary</h4><p>File: ${escapeHtml(fileName)} · Generated ${escapeHtml(new Date().toLocaleString())}</p></div><span class="severity-tag ${severityClass}">${escapeHtml(severity)} severity</span></div>
      <div class="report-columns">
        <div>
          <div class="report-block"><h5>OVERALL FINDING</h5><p>${escapeHtml(advice.summary)}</p></div>
          <div class="report-block"><h5>KEY MEASUREMENTS</h5><ul><li>Estimated damage proportion: ${escapeHtml(number(percent))}%</li><li>Severity score: ${score===null?"Not returned":escapeHtml(number(score,3))}</li><li>Detected region count: ${escapeHtml(number(count,0))}</li><li>Vehicle pixel area: ${escapeHtml(number(p4.vehicle_area,0))}</li><li>Damage pixel area: ${escapeHtml(number(p4.damage_area,0))}</li></ul></div>
        </div>
        <div>
          <div class="report-block"><h5>RECOMMENDED ACTION</h5><p><strong>${escapeHtml(advice.title)}</strong></p><ul>${advice.actions.map(a=>`<li>${escapeHtml(a)}</li>`).join("")}</ul></div>
          <div class="report-block"><h5>METHOD & LIMITATIONS</h5><p>Severity method: ${escapeHtml(p4.severity_method||"Not specified")}. Validation flag: ${p4.severity_validated===true?"Yes":p4.severity_validated===false?"No":"Not returned"}. The result reflects image processing outputs only; lighting, angle, occlusion, image quality, and hidden damage can affect accuracy.</p></div>
        </div>
      </div>
      <div class="report-footer-note"><strong>Important limitation:</strong> This is a preliminary computer-vision assessment, not a confirmed insurance valuation, structural diagnosis, or roadworthiness decision. Have the vehicle examined by a qualified professional before making repair or safety decisions.</div>`;
  }
  async function runAnalysis() {
    if (!state.file) { toast("Choose a vehicle image first."); return; }
    setProgress(true);
    document.body.classList.add("is-analyzing");
    document.body.classList.remove("analysis-complete");
    try {
      const form=new FormData(); form.append("image",state.file);
      const response=await fetch("/api/analyze",{method:"POST",body:form});
      let result; try { result=await response.json(); } catch { throw new Error("The server returned an unreadable response. Check the Flask terminal."); }
      if (!response.ok || !result.success) throw new Error(result.error||`Analysis failed (HTTP ${response.status}).`);
      state.result=result; state.urls=result.artifacts||{};
      renderReport(result); setViewer("original"); $("imageViewStatus").textContent="Analysis complete";
      document.body.classList.remove("is-analyzing");
      document.body.classList.add("analysis-complete");
      $("uploadMessage").textContent="Assessment complete. Review the report below.";
      toast("Assessment completed successfully.");
      $("report").scrollIntoView({behavior:"smooth",block:"start"});
    } catch (err) {
      console.error("AIM002 analysis error:",err);
      toast(err.message||"Analysis failed. Check the Flask terminal.");
    } finally { setProgress(false); document.body.classList.remove("is-analyzing"); }
  }
  function initialize() {
    $("selectImageButton").addEventListener("click",()=> $("imageInput").click());
    $("dropZone").addEventListener("click",e=>{if(e.target.closest("button"))return;$("imageInput").click();});
    $("dropZone").addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();$("imageInput").click();}});
    $("imageInput").addEventListener("change",e=>selectFile(e.target.files?.[0]));
    $("analyzeButton").addEventListener("click",runAnalysis);
    $("removeImageButton").addEventListener("click",clearFile);
    const dz=$("dropZone");
    ["dragenter","dragover"].forEach(ev=>dz.addEventListener(ev,e=>{e.preventDefault();dz.classList.add("dragging");}));
    ["dragleave","drop"].forEach(ev=>dz.addEventListener(ev,e=>{e.preventDefault();dz.classList.remove("dragging");}));
    dz.addEventListener("drop",e=>selectFile(e.dataTransfer?.files?.[0]));
    document.querySelectorAll(".viewer-tab").forEach(btn=>btn.addEventListener("click",()=>setViewer(btn.dataset.view)));
    $("openImageButton").addEventListener("click",()=>{const img=$("mainResultImage");if(!img.hidden&&img.src)window.open(img.src,"_blank","noopener");});
    $("printReportButton").addEventListener("click",()=>window.print());
    $("themeToggle").addEventListener("click",()=>document.body.classList.toggle("light-mode"));
    document.querySelectorAll(".nav-item").forEach(a=>a.addEventListener("click",()=>{document.querySelectorAll(".nav-item").forEach(n=>n.classList.remove("active"));a.classList.add("active");}));
    $("mainResultImage").addEventListener("error",()=>{if(state.view!=="original"){$("mainResultImage").hidden=true;$("imageUnavailable").hidden=false;$("viewerCaption").textContent="Output image unavailable";$("openImageButton").disabled=true;}});
  }
  document.addEventListener("DOMContentLoaded",initialize);
})();