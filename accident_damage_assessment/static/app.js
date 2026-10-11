(function () {

    "use strict";

    let selectedFile = null;


    // =========================================================
    // HELPERS
    // =========================================================

    function get(id) {
        return document.getElementById(id);
    }


    function num(value) {

        if (
            value === undefined ||
            value === null ||
            value === ""
        ) {
            return "N/A";
        }

        const n = Number(value);

        return Number.isFinite(n)
            ? n.toFixed(2)
            : String(value);
    }


    function esc(value) {

        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    // =========================================================
    // DECISION SUPPORT
    // =========================================================

    function getDecision(severity, damagePercent, regionCount) {

        const level =
            String(severity || "")
                .toLowerCase();

        const damage =
            Number(damagePercent || 0);

        const regions =
            Number(regionCount || 0);


        // HIGH INTENSITY
        if (
            level.includes("high") ||
            damage >= 15
        ) {

            return {

                label: "HIGH DAMAGE INTENSITY",

                title:
                    "Professional inspection should be arranged before normal use.",

                summary:
                    "The image-based assessment indicates a relatively high concentration or extent of visible damage. The affected areas should not be treated as cosmetic damage without further inspection.",

                why:
                    `Estimated affected area: ${damage.toFixed(2)}%. ` +
                    `The system detected ${regions} damage region(s), with a ${severity} severity assessment.`,

                actions: [
                    "Have the vehicle inspected by a qualified automotive professional.",
                    "Check the damaged body panels for deformation, cracks, sharp edges, or displaced components.",
                    "Check nearby lights, mirrors, bumpers, wheels, and visible fittings for secondary damage.",
                    "If the impact area is near a wheel, suspension component, door frame, or other critical area, request a detailed mechanical inspection.",
                    "Do not rely on the image assessment alone to determine whether the vehicle is safe to drive."
                ],

                className: "decision-high"
            };
        }


        // MODERATE INTENSITY
        if (
            level.includes("moderate") ||
            damage >= 5
        ) {

            return {

                label: "MODERATE DAMAGE INTENSITY",

                title:
                    "Detailed inspection and repair assessment recommended.",

                summary:
                    "The system detected a noticeable amount of visible damage. The highlighted regions should be examined to determine whether the damage is limited to the exterior or extends to nearby components.",

                why:
                    `Estimated affected area: ${damage.toFixed(2)}%. ` +
                    `The system detected ${regions} damage region(s), with a ${severity} severity assessment.`,

                actions: [
                    "Inspect each highlighted region closely for dents, cracks, scratches, deformation, or missing parts.",
                    "Check the alignment of nearby body panels, doors, bonnet, boot, and bumpers.",
                    "Inspect nearby lights, mirrors, sensors, and visible fittings if they are close to a highlighted region.",
                    "Obtain a professional repair estimate before deciding whether cosmetic repair is sufficient.",
                    "If the vehicle shows unusual steering, braking, vibration, warning lights, or fluid leakage, arrange a professional inspection."
                ],

                className: "decision-moderate"
            };
        }


        // LOW INTENSITY
        return {

            label: "LOW DAMAGE INTENSITY",

            title:
                "Visual inspection of the highlighted areas is recommended.",

            summary:
                "The image-based assessment indicates a relatively limited visible damage area. The detected regions should still be checked because image analysis cannot determine hidden or mechanical damage.",

            why:
                `Estimated affected area: ${damage.toFixed(2)}%. ` +
                `The system detected ${regions} damage region(s), with a ${severity} severity assessment.`,

            actions: [
                "Inspect the highlighted regions for visible scratches, dents, cracks, or surface deformation.",
                "Check that nearby panels, lights, mirrors, and fittings are properly aligned and attached.",
                "Document the damaged areas with photographs before repair.",
                "For apparently cosmetic damage, obtain a repair estimate if required.",
                "Seek professional inspection if any mechanical or safety-related symptom is noticed."
            ],

            className: "decision-low"
        };
    }


    // =========================================================
    // IMAGE CARD
    // =========================================================

    function imageCard(title, url, filename) {

        return `
            <div style="
                background:#ffffff;
                border:1px solid #e1e5ea;
                border-radius:12px;
                padding:10px;
                box-sizing:border-box;
                min-width:0;
            ">

                <div style="
                    font-size:14px;
                    font-weight:700;
                    color:#111827;
                    margin-bottom:7px;
                ">
                    ${esc(title)}
                </div>

                ${
                    filename
                    ?
                    `<div style="
                        font-size:11px;
                        color:#6b7280;
                        margin-bottom:7px;
                        overflow:hidden;
                        text-overflow:ellipsis;
                        white-space:nowrap;
                    " title="${esc(filename)}">
                        ${esc(filename)}
                    </div>`
                    :
                    ""
                }

                ${
                    url
                    ?
                    `<img
                        src="${url}"
                        alt="${esc(title)}"
                        style="
                            width:100%;
                            height:200px;
                            object-fit:contain;
                            display:block;
                            background:#f4f5f7;
                            border-radius:9px;
                        "
                    >`
                    :
                    `<div style="
                        height:200px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        background:#f4f5f7;
                        border-radius:9px;
                        color:#6b7280;
                        font-size:12px;
                    ">
                        Image unavailable
                    </div>`
                }

            </div>
        `;
    }


    // =========================================================
    // DISPLAY RESULTS
    // =========================================================

    function showResults(result) {

        console.log("AIM002: rendering final results", result);

        const p4 =
            result.p4 || {};

        const artifacts =
            result.artifacts || {};

        const regions =
            Array.isArray(p4.regions)
                ? p4.regions
                : [];


        let old =
            get("aim002LiveResults");

        if (old) {
            old.remove();
        }


        const box =
            document.createElement("div");

        box.id =
            "aim002LiveResults";


        box.style.cssText = `
            display:block !important;
            visibility:visible !important;
            opacity:1 !important;
            width:calc(100% - 40px) !important;
            max-width:1400px !important;
            margin:35px auto !important;
            padding:25px !important;
            box-sizing:border-box !important;
            background:#f8fafc !important;
            color:#111827 !important;
            position:relative !important;
            z-index:999999 !important;
        `;


        const severity =
            p4.severity || "Not available";


        const damagePercent =
            p4.damage_percent !== undefined
                ? Number(p4.damage_percent)
                : 0;


        const regionCount =
            p4.region_count !== undefined
                ? Number(p4.region_count)
                : regions.length;


        const score =
            p4.severity_score !== undefined
                ? Number(p4.severity_score)
                : null;


        const decision =
            getDecision(
                severity,
                damagePercent,
                regionCount
            );


        let selectedUrl =
            "";

        if (selectedFile) {
            selectedUrl =
                URL.createObjectURL(
                    selectedFile
                );
        }


        const selectedName =
            selectedFile
                ? selectedFile.name
                : (
                    result.input_filename ||
                    "Selected image"
                );


        // =====================================================
        // HTML
        // =====================================================

        box.innerHTML = `

            <h2 style="
                margin:0 0 22px 0;
                font-size:25px;
            ">
                Assessment Results
            </h2>


            <!-- SUMMARY -->

            <div style="
                display:grid;
                grid-template-columns:repeat(4,1fr);
                gap:12px;
                margin-bottom:28px;
            ">

                <div style="
                    background:white;
                    border:1px solid #e5e7eb;
                    border-radius:11px;
                    padding:14px;
                ">
                    <div style="
                        font-size:11px;
                        color:#6b7280;
                    ">
                        Severity
                    </div>

                    <div style="
                        margin-top:5px;
                        font-size:21px;
                        font-weight:800;
                    ">
                        ${esc(severity)}
                    </div>
                </div>


                <div style="
                    background:white;
                    border:1px solid #e5e7eb;
                    border-radius:11px;
                    padding:14px;
                ">
                    <div style="
                        font-size:11px;
                        color:#6b7280;
                    ">
                        Estimated Damage
                    </div>

                    <div style="
                        margin-top:5px;
                        font-size:21px;
                        font-weight:800;
                    ">
                        ${damagePercent.toFixed(2)}%
                    </div>
                </div>


                <div style="
                    background:white;
                    border:1px solid #e5e7eb;
                    border-radius:11px;
                    padding:14px;
                ">
                    <div style="
                        font-size:11px;
                        color:#6b7280;
                    ">
                        Damage Regions
                    </div>

                    <div style="
                        margin-top:5px;
                        font-size:21px;
                        font-weight:800;
                    ">
                        ${regionCount}
                    </div>
                </div>


                <div style="
                    background:white;
                    border:1px solid #e5e7eb;
                    border-radius:11px;
                    padding:14px;
                ">
                    <div style="
                        font-size:11px;
                        color:#6b7280;
                    ">
                        Assessment Score
                    </div>

                    <div style="
                        margin-top:5px;
                        font-size:21px;
                        font-weight:800;
                    ">
                        ${
                            score !== null
                                ? score.toFixed(3)
                                : "N/A"
                        }
                    </div>
                </div>

            </div>


            <!-- VISUAL ANALYSIS -->

            <h3 style="
                margin:0 0 12px 0;
                font-size:19px;
            ">
                Visual Analysis
            </h3>


            <div style="
                display:grid;
                grid-template-columns:repeat(4,1fr);
                gap:12px;
                margin-bottom:28px;
            ">

                ${imageCard(
                    "Selected Image",
                    selectedUrl,
                    selectedName
                )}

                ${imageCard(
                    "Vehicle Segmentation",
                    artifacts.vehicle,
                    ""
                )}

                ${imageCard(
                    "Detected Damage",
                    artifacts.candidate_mask,
                    ""
                )}

                ${imageCard(
                    "Enhanced Image",
                    artifacts.enhanced,
                    ""
                )}

            </div>


            <!-- REGION INFORMATION -->

            <h3 style="
                margin:0 0 12px 0;
                font-size:19px;
            ">
                Region Damage Information
            </h3>


            <div style="
                display:grid;
                grid-template-columns:repeat(4,1fr);
                gap:10px;
                margin-bottom:30px;
            ">

                ${
                    regions.length === 0
                    ?
                    `
                    <div style="
                        background:white;
                        border:1px solid #e5e7eb;
                        border-radius:10px;
                        padding:12px;
                        font-size:12px;
                    ">
                        No detected damage regions.
                    </div>
                    `
                    :
                    regions.map(function (r, i) {

                        return `
                            <div style="
                                background:white;
                                border:1px solid #e2e6eb;
                                border-radius:10px;
                                padding:11px;
                                box-sizing:border-box;
                                min-width:0;
                            ">

                                <div style="
                                    font-size:13px;
                                    font-weight:800;
                                    margin-bottom:7px;
                                ">
                                    Region ${i + 1}
                                </div>

                                <div style="
                                    font-size:11px;
                                    line-height:1.55;
                                    color:#4b5563;
                                ">

                                    <div>
                                        <strong>Area:</strong>
                                        ${num(r.area)}
                                    </div>

                                    <div>
                                        <strong>Perimeter:</strong>
                                        ${num(r.perimeter)}
                                    </div>

                                    <div>
                                        <strong>Position:</strong>
                                        (${num(r.x)}, ${num(r.y)})
                                    </div>

                                    <div>
                                        <strong>Size:</strong>
                                        ${num(r.width)}
                                        ×
                                        ${num(r.height)}
                                    </div>

                                    ${
                                        r.aspect_ratio !== undefined
                                        ?
                                        `<div>
                                            <strong>Aspect:</strong>
                                            ${num(r.aspect_ratio)}
                                         </div>`
                                        :
                                        ""
                                    }

                                    ${
                                        r.solidity !== undefined
                                        ?
                                        `<div>
                                            <strong>Solidity:</strong>
                                            ${num(r.solidity)}
                                         </div>`
                                        :
                                        ""
                                    }

                                    ${
                                        r.circularity !== undefined
                                        ?
                                        `<div>
                                            <strong>Circularity:</strong>
                                            ${num(r.circularity)}
                                         </div>`
                                        :
                                        ""
                                    }

                                </div>

                            </div>
                        `;

                    }).join("")
                }

            </div>


            <!-- DECISION SUPPORT -->

            <div style="
                background:#ffffff;
                border:1px solid #dfe4ea;
                border-radius:13px;
                padding:18px;
                margin-bottom:28px;
            ">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    gap:10px;
                    flex-wrap:wrap;
                    margin-bottom:9px;
                ">

                    <h3 style="
                        margin:0;
                        font-size:19px;
                    ">
                        What To Do Next
                    </h3>

                    <span style="
                        padding:5px 9px;
                        border-radius:15px;
                        background:#f3f4f6;
                        font-size:10px;
                        font-weight:800;
                    ">
                        ${decision.label}
                    </span>

                </div>


                <h4 style="
                    margin:7px 0;
                    font-size:15px;
                ">
                    ${decision.title}
                </h4>


                <p style="
                    margin:7px 0;
                    font-size:12px;
                    line-height:1.6;
                    color:#4b5563;
                ">
                    ${decision.summary}
                </p>


                <div style="
                    margin:10px 0;
                    padding:9px 11px;
                    border-radius:9px;
                    background:#f8fafc;
                    font-size:11px;
                    line-height:1.55;
                ">
                    <strong>Assessment basis:</strong>
                    ${decision.why}
                </div>


                <div style="
                    font-size:12px;
                    font-weight:700;
                    margin:10px 0 6px 0;
                ">
                    Recommended next steps
                </div>


                <ul style="
                    margin:0;
                    padding-left:19px;
                    font-size:11px;
                    line-height:1.7;
                    color:#374151;
                ">

                    ${
                        decision.actions.map(
                            function (action) {
                                return `
                                    <li>
                                        ${action}
                                    </li>
                                `;
                            }
                        ).join("")
                    }

                </ul>


                <div style="
                    margin-top:11px;
                    font-size:10px;
                    color:#6b7280;
                    line-height:1.5;
                ">
                    This is provisional image-based decision support.
                    It does not establish hidden mechanical or structural
                    damage and should not replace a qualified vehicle inspection.
                </div>

            </div>


            <!-- SHORT TECHNICAL INFORMATION -->

            <h3 style="
                margin:0 0 10px 0;
                font-size:19px;
            ">
                Technical Information
            </h3>


            <div style="
                display:grid;
                grid-template-columns:repeat(3,1fr);
                gap:10px;
                font-size:11px;
            ">

                <div style="
                    background:white;
                    border:1px solid #e5e7eb;
                    border-radius:10px;
                    padding:12px;
                ">
                    <strong>Input</strong><br><br>

                    File:
                    ${esc(selectedName)}
                    <br>

                    Size:
                    ${
                        selectedFile
                            ? (
                                selectedFile.size /
                                1024 /
                                1024
                              ).toFixed(2) + " MB"
                            : "N/A"
                    }
                </div>


                <div style="
                    background:white;
                    border:1px solid #e5e7eb;
                    border-radius:10px;
                    padding:12px;
                ">
                    <strong>Measurements</strong><br><br>

                    Vehicle Area:
                    ${num(p4.vehicle_area)}
                    <br>

                    Damage Area:
                    ${num(p4.damage_area)}
                    <br>

                    Damage:
                    ${damagePercent.toFixed(2)}%
                </div>


                <div style="
                    background:white;
                    border:1px solid #e5e7eb;
                    border-radius:10px;
                    padding:12px;
                ">
                    <strong>Method</strong><br><br>

                    Severity:
                    ${esc(severity)}
                    <br>

                    Method:
                    ${esc(
                        p4.severity_method ||
                        "Not specified"
                    )}
                    <br>

                    Validated:
                    ${
                        p4.severity_validated === true
                            ? "Yes"
                            : "No"
                    }
                </div>

            </div>

        `;


        document.body.appendChild(box);


        setTimeout(function () {

            box.scrollIntoView({
                behavior:"smooth",
                block:"start"
            });

        }, 100);
    }


    // =========================================================
    // ANALYSIS
    // =========================================================

    async function runAnalysis() {

        if (!selectedFile) {

            alert(
                "Please select an image first."
            );

            return;
        }


        const button =
            get("analyzeButton");


        if (button) {

            button.disabled = true;

            button.textContent =
                "Analyzing...";
        }


        const form =
            new FormData();

        form.append(
            "image",
            selectedFile
        );


        try {

            console.log(
                "AIM002: sending image..."
            );


            const response =
                await fetch(
                    "/api/analyze",
                    {
                        method:"POST",
                        body:form
                    }
                );


            const result =
                await response.json();


            console.log(
                "AIM002 API response:",
                result
            );


            if (!response.ok) {

                throw new Error(
                    result.error ||
                    "Analysis failed."
                );
            }


            showResults(result);

        }
        catch (error) {

            console.error(
                "AIM002 analysis error:",
                error
            );


            alert(
                "Analysis failed:\n\n" +
                error.message
            );

        }
        finally {

            if (button) {

                button.disabled = false;

                button.textContent =
                    "Analyze Image";
            }
        }
    }


    // =========================================================
    // INITIALIZATION
    // =========================================================

    function initialize() {

        console.log(
            "AIM002 frontend initialized."
        );


        const input =
            get("imageInput");

        const select =
            get("selectImageButton");

        const analyze =
            get("analyzeButton");


        if (!input) {

            console.error(
                "imageInput not found."
            );

            return;
        }


        if (select) {

            select.onclick =
                function (event) {

                    event.preventDefault();

                    input.click();
                };
        }


        input.onchange =
            function () {

                const file =
                    input.files &&
                    input.files[0];


                if (!file) {
                    return;
                }


                if (!file.type.startsWith("image/")) {

                    alert(
                        "Please select an image file."
                    );

                    input.value = "";

                    return;
                }


                if (
                    file.size >
                    25 * 1024 * 1024
                ) {

                    alert(
                        "Image must be smaller than 25 MB."
                    );

                    input.value = "";

                    return;
                }


                selectedFile =
                    file;


                console.log(
                    "Selected:",
                    file.name
                );


                const name =
                    get("fileName");


                if (name) {

                    name.textContent =
                        file.name;
                }


                const preview =
                    get("selectedImagePreview");


                if (preview) {

                    preview.src =
                        URL.createObjectURL(
                            file
                        );

                    preview.style.display =
                        "block";
                }


                if (analyze) {

                    analyze.disabled =
                        false;
                }
            };


        if (analyze) {

            analyze.onclick =
                function (event) {

                    event.preventDefault();

                    runAnalysis();
                };
        }
    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initialize
        );

    }
    else {

        initialize();
    }

})();
