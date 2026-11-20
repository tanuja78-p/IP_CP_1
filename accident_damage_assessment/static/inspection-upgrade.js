
(() => {
  "use strict";

  const state = {
    file: null,
    result: null,
    regions: [],
    selected: -1,
    objectUrl: null
  };

  const $ = (id) => document.getElementById(id);
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, c => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c]));
  const n = (v,d=0) => Number.isFinite(Number(v)) ? Number(v).toLocaleString(undefined,{maximumFractionDigits:d}) : "N/A";

  function artifact(result, key) {
    const value = result?.artifacts?.[key];
    return value || "";
  }

  function ensureInputFix() {
    const input = $("imageInput");
    if (!input) return;
    input.addEventListener("change", () => setSelectedFile(input.files?.[0]), {capture:true});
    const button = $("selectImageButton");
    if (button) button.addEventListener("click", e => {
      e.preventDefault();
      e.stopImmediatePropagation();
      input.click();
    }, {capture:true});
  }

  function setSelectedFile(file) {
    if (!file) return;
    if (!file.type.startsWith("image/")) return;
    if (file.size > 25 * 1024 * 1024) return;
    state.file = file;
    if (state.objectUrl) URL.revokeObjectURL(state.objectUrl);
    state.objectUrl = URL.createObjectURL(file);
    const preview = $("selectedImagePreview");
    if (preview) {
      preview.src = state.objectUrl;
      preview.style.display = "block";
    }
    const name = $("fileName");
    if (name) {
      name.textContent = file.name;
      name.classList.add("has-file");
    }
    const analyze = $("analyzeButton");
    if (analyze) analyze.disabled = false;
    const zone = $("uploadZone");
    if (zone) zone.classList.add("has-image");
  }

  function installFetchBridge() {
    const originalFetch = window.fetch;
    if (originalFetch.__aim002Bridge) return;
    async function wrappedFetch(...args) {
      const response = await originalFetch(...args);
      try {
        const url = typeof args[0] === "string" ? args[0] : args[0]?.url || "";
        if (url.includes("/api/analyze") && response.ok) {
          const clone = response.clone();
          clone.json().then(result => {
            if (result?.success) {
              state.result = result;
              state.regions = Array.isArray(result?.p4?.regions) ? result.p4.regions : [];
              renderInspection();
              window.dispatchEvent(new CustomEvent("aim002:analysis-complete", {detail: result}));
            }
          }).catch(() => {});
        }
      } catch (_) {}
      return response;
    }
    wrappedFetch.__aim002Bridge = true;
    window.fetch = wrappedFetch;
  }

  function buildUI() {
    if ($("aimInspectionResults")) return;
    const anchor = $("aim002ResultsAnchor") || $("aim002-vehicle-3d") || document.querySelector("main") || document.body;
    const section = document.createElement("section");
    section.id = "aimInspectionResults";
    section.className = "aim-inspection-results";
    section.innerHTML = `
      <div class="aim-inspection-head">
        <div>
          <div class="aim-inspection-kicker">COMPUTER VISION · ACTUAL IMAGE ANALYSIS</div>
          <h2>Damage Inspection Workspace</h2>
          <p>The uploaded photograph and returned AIM002 regions are the authoritative inspection view.</p>
        </div>
        <div class="aim-analysis-status" id="aimAnalysisStatus">WAITING FOR ANALYSIS</div>
      </div>

      <div class="aim-analysis-grid">
        <div class="aim-analysis-main">
          <div class="aim-view-tabs">
            <button class="aim-view-tab active" data-aim-view="overlay">Damage Overlay</button>
            <button class="aim-view-tab" data-aim-view="original">Original</button>
            <button class="aim-view-tab" data-aim-view="mask">Damage Mask</button>
          </div>
          <div class="aim-image-stage" id="aimImageStage">
            <div class="aim-canvas-placeholder" id="aimImagePlaceholder">Run an assessment to inspect detected regions.</div>
            <img id="aimBaseImage" class="aim-base-image" alt="Vehicle analysis source image" hidden>
            <canvas id="aimOverlayCanvas" class="aim-overlay-canvas" hidden></canvas>
          </div>
          <div class="aim-stage-caption">
            <span id="aimStageCaption">No analysis loaded</span>
            <span id="aimZoomCaption">Click a region to focus it</span>
          </div>
        </div>

        <aside class="aim-analysis-side">
          <div class="aim-side-title">Detected Regions <span id="aimRegionCount">0</span></div>
          <div class="aim-region-list" id="aimRegionList">
            <div class="aim-note">No regions returned yet.</div>
          </div>
          <div class="aim-region-detail" id="aimRegionDetail">
            <div class="aim-detail-title">Select a detected region</div>
            <div class="aim-note">The panel will show the coordinates, dimensions and area returned by P4.</div>
          </div>
        </aside>
      </div>

      <div class="aim-visual-strip">
        <div class="aim-visual-card">
          <h3>Edge Structure</h3>
          <p>Local image-gradient view generated from the uploaded photograph. This is a visual edge aid, not a separate damage prediction.</p>
          <canvas id="aimEdgeCanvas" class="aim-edge-canvas"></canvas>
        </div>
        <div class="aim-visual-card">
          <h3>Pipeline Damage Output</h3>
          <p>Returned damage-mask artifact from the AIM002 analysis pipeline.</p>
          <img id="aimMaskImage" alt="AIM002 damage mask" hidden>
        </div>
      </div>

      <div class="aim-note">
        <strong>Interpretation:</strong> red outlines and region boxes correspond to regions returned by the AIM002 response. The edge map is an image-processing visualization. The 3D vehicle remains a navigation/inspection aid and should not be treated as an independent detector.
      </div>
    `;
    if (anchor.id === "aim002ResultsAnchor") anchor.after(section);
    else anchor.after(section);

    section.querySelectorAll("[data-aim-view]").forEach(btn => {
      btn.addEventListener("click", () => {
        section.querySelectorAll("[data-aim-view]").forEach(b => b.classList.toggle("active", b === btn));
        drawMain(btn.dataset.aimView);
      });
    });
  }

  function renderInspection() {
    buildUI();
    const result = state.result;
    const base = $("aimBaseImage");
    const placeholder = $("aimImagePlaceholder");
    if (!result || !state.file) return;

    $("aimAnalysisStatus").textContent = "ANALYSIS COMPLETE";
    $("aimRegionCount").textContent = `· ${state.regions.length}`;
    placeholder.hidden = true;
    base.hidden = false;
    base.src = state.objectUrl;
    $("aimStageCaption").textContent = `${result.input_filename || state.file.name} · ${state.regions.length} detected region(s)`;

    base.onload = () => {
      drawMain("overlay");
      drawEdges(base);
    };

    const mask = $("aimMaskImage");
    const maskUrl = artifact(result,"candidate_mask") || artifact(result,"damage_mask");
    if (maskUrl) {
      mask.hidden = false;
      mask.src = maskUrl;
    } else {
      mask.hidden = true;
    }

    renderRegionList();
  }

  function renderRegionList() {
    const list = $("aimRegionList");
    if (!state.regions.length) {
      list.innerHTML = `<div class="aim-note">The pipeline returned no individual regions. The damage percentage/mask may still contain useful output.</div>`;
      return;
    }
    list.innerHTML = state.regions.map((r,i) => `
      <button class="aim-region-button ${i===state.selected?'active':''}" data-region-index="${i}">
        <span class="aim-region-number">${String(i+1).padStart(2,"0")}</span>
        <span><strong>Region ${i+1}</strong><small>X ${n(r.x)} · Y ${n(r.y)} · ${n(r.width)} × ${n(r.height)}</small></span>
        <span class="aim-region-area">${n(r.area)} px²</span>
      </button>
    `).join("");
    list.querySelectorAll("[data-region-index]").forEach(btn => btn.addEventListener("click", () => {
      state.selected = Number(btn.dataset.regionIndex);
      renderRegionList();
      renderRegionDetail();
      drawMain("overlay");
      window.dispatchEvent(new CustomEvent("aim002:region-selected", {detail:{index:state.selected, region:state.regions[state.selected], result:state.result}}));
      document.getElementById("aimImageStage")?.scrollIntoView({behavior:"smooth",block:"center"});
    }));
  }

  function renderRegionDetail() {
    const box = $("aimRegionDetail");
    const r = state.regions[state.selected];
    if (!r) {
      box.innerHTML = `<div class="aim-detail-title">Select a detected region</div><div class="aim-note">Click a region to focus the corresponding location on the uploaded image.</div>`;
      return;
    }
    box.innerHTML = `
      <div class="aim-detail-title">Region ${String(state.selected+1).padStart(2,"0")}</div>
      <div class="aim-detail-grid">
        <div class="aim-detail-cell"><span>Position</span><b>${n(r.x)} , ${n(r.y)}</b></div>
        <div class="aim-detail-cell"><span>Size</span><b>${n(r.width)} × ${n(r.height)}</b></div>
        <div class="aim-detail-cell"><span>Area</span><b>${n(r.area)} px²</b></div>
        <div class="aim-detail-cell"><span>Perimeter</span><b>${n(r.perimeter)} px</b></div>
        <div class="aim-detail-cell"><span>Aspect</span><b>${n(r.aspect_ratio,2)}</b></div>
        <div class="aim-detail-cell"><span>Solidity</span><b>${n(r.solidity,2)}</b></div>
      </div>`;
  }

  function fitCanvas(canvas, image) {
    const rect = image.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const w = Math.max(1, Math.round(rect.width));
    const h = Math.max(1, Math.round(rect.height));
    canvas.width = Math.round(w*dpr);
    canvas.height = Math.round(h*dpr);
    canvas.style.width = `${w}px`;
    canvas.style.height = `${h}px`;
    const ctx = canvas.getContext("2d");
    ctx.setTransform(dpr,0,0,dpr,0,0);
    return {ctx,w,h};
  }

  function imageGeometry(image, canvas) {
    const iw=image.naturalWidth, ih=image.naturalHeight;
    const rect=image.getBoundingClientRect();
    const cw=rect.width, ch=rect.height;
    const scale=Math.min(cw/iw,ch/ih);
    const dw=iw*scale, dh=ih*scale;
    return {scale,ox:(cw-dw)/2,oy:(ch-dh)/2,iw,ih};
  }

  function drawMain(mode) {
    const image=$("aimBaseImage"), canvas=$("aimOverlayCanvas");
    if (!image || !state.result || !image.complete) return;
    const {ctx,w,h}=fitCanvas(canvas,image);
    ctx.clearRect(0,0,w,h);
    const g=imageGeometry(image,canvas);
    if (mode === "original") {
      canvas.hidden=true;
      $("aimZoomCaption").textContent="Original uploaded photograph";
      return;
    }
    canvas.hidden=false;
    if (mode === "mask") {
      const mask=$("aimMaskImage");
      if (!mask || mask.hidden || !mask.complete) {
        $("aimZoomCaption").textContent="Damage mask unavailable";
        return;
      }
      ctx.globalAlpha=.72;
      ctx.drawImage(mask,0,0,w,h);
      ctx.globalAlpha=1;
      $("aimZoomCaption").textContent="Returned pipeline damage mask";
      return;
    }
    ctx.strokeStyle="#ff4d55";
    ctx.fillStyle="rgba(255,55,65,.08)";
    ctx.lineWidth=2;
    state.regions.forEach((r,i)=>{
      const x=g.ox+Number(r.x||0)*g.scale;
      const y=g.oy+Number(r.y||0)*g.scale;
      const rw=Number(r.width||0)*g.scale;
      const rh=Number(r.height||0)*g.scale;
      const active=i===state.selected;
      ctx.strokeStyle=active?"#ffb52e":"#ff4d55";
      ctx.lineWidth=active?3:2;
      ctx.fillStyle=active?"rgba(255,181,46,.13)":"rgba(255,77,85,.07)";
      ctx.fillRect(x,y,rw,rh);
      ctx.strokeRect(x,y,rw,rh);
      ctx.fillStyle=active?"#ffb52e":"#ff4d55";
      ctx.fillRect(x,y,28,18);
      ctx.fillStyle="#07101a";
      ctx.font="700 10px Arial";
      ctx.fillText(String(i+1).padStart(2,"0"),x+7,y+13);
    });
    if (state.selected >= 0 && state.regions[state.selected]) {
      const r=state.regions[state.selected];
      const x=g.ox+Number(r.x||0)*g.scale, y=g.oy+Number(r.y||0)*g.scale;
      const rw=Number(r.width||0)*g.scale, rh=Number(r.height||0)*g.scale;
      ctx.strokeStyle="#fff";
      ctx.setLineDash([6,4]);
      ctx.strokeRect(x-4,y-4,rw+8,rh+8);
      ctx.setLineDash([]);
      $("aimZoomCaption").textContent=`Focused on Region ${String(state.selected+1).padStart(2,"0")}`;
    } else {
      $("aimZoomCaption").textContent="Click a region to focus it";
    }
  }

  function drawEdges(image) {
    const canvas=$("aimEdgeCanvas");
    if (!canvas || !image?.complete) return;
    const rect=canvas.getBoundingClientRect();
    const w=Math.max(320,Math.round(rect.width)), h=Math.max(220,Math.round(rect.height));
    const dpr=window.devicePixelRatio||1;
    canvas.width=w*dpr; canvas.height=h*dpr;
    const ctx=canvas.getContext("2d");
    ctx.setTransform(dpr,0,0,dpr,0,0);
    const scale=Math.min(w/image.naturalWidth,h/image.naturalHeight);
    const iw=Math.max(1,Math.round(image.naturalWidth*scale)), ih=Math.max(1,Math.round(image.naturalHeight*scale));
    const ox=(w-iw)/2, oy=(h-ih)/2;
    const off=document.createElement("canvas"); off.width=iw; off.height=ih;
    const octx=off.getContext("2d",{willReadFrequently:true});
    octx.drawImage(image,0,0,iw,ih);
    const data=octx.getImageData(0,0,iw,ih), src=data.data;
    const out=octx.createImageData(iw,ih), dst=out.data;
    const gray=new Uint8Array(iw*ih);
    for(let i=0,p=0;i<src.length;i+=4,p++) gray[p]=(0.299*src[i]+0.587*src[i+1]+0.114*src[i+2])|0;
    for(let y=1;y<ih-1;y++) for(let x=1;x<iw-1;x++){
      const p=y*iw+x;
      const gx=-gray[p-iw-1]+gray[p-iw+1]-2*gray[p-1]+2*gray[p+1]-gray[p+iw-1]+gray[p+iw+1];
      const gy=-gray[p-iw-1]-2*gray[p-iw]-gray[p-iw+1]+gray[p+iw-1]+2*gray[p+iw]+gray[p+iw+1];
      const mag=Math.min(255,Math.sqrt(gx*gx+gy*gy)*1.5);
      const q=p*4; dst[q]=mag; dst[q+1]=mag; dst[q+2]=mag; dst[q+3]=255;
    }
    octx.putImageData(out,0,0);
    ctx.fillStyle="#02050a"; ctx.fillRect(0,0,w,h);
    ctx.drawImage(off,ox,oy);
  }

  function resize() {
    if (state.result && $("aimBaseImage")?.complete) {
      drawMain(document.querySelector(".aim-view-tab.active")?.dataset.aimView || "overlay");
      drawEdges($("aimBaseImage"));
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    buildUI();
    ensureInputFix();
    installFetchBridge();
    window.addEventListener("resize", resize);
    window.addEventListener("aim002:region-selected", e => {
      const detail=e.detail;
      document.querySelectorAll("[data-damage-select]").forEach(btn => {
        const title=(btn.dataset.title||"").toLowerCase();
        const region=detail?.region||{};
        if (title.includes(String(region.name||"").toLowerCase())) btn.click();
      });
    });
  });
})();
