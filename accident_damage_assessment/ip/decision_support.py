def build_decision_support(p4):
    """
    Convert P4 assessment information into user-facing decision support.

    This is a rule-based recommendation layer.
    It is not a medical, insurance, repair-cost, or legal decision.
    """

    if not isinstance(p4, dict):
        raise ValueError("P4 result must be a dictionary.")

    severity = str(p4.get("severity", "Unknown"))
    severity_score = float(p4.get("severity_score", 0.0) or 0.0)
    damage_percent = float(p4.get("damage_percent", 0.0) or 0.0)
    region_count = int(p4.get("region_count", 0) or 0)
    validated = bool(p4.get("severity_validated", False))

    severity_lower = severity.lower()

    if severity_lower == "high" or damage_percent >= 15 or severity_score >= 0.65:
        title = "Prompt professional inspection recommended"
        level = "HIGH_ATTENTION"
        message = (
            "The image analysis indicates a comparatively substantial "
            "amount of detected damage. A professional inspection is "
            "recommended before deciding on repair."
        )

    elif severity_lower == "moderate" or damage_percent >= 5 or severity_score >= 0.35:
        title = "Professional inspection recommended"
        level = "INSPECTION_RECOMMENDED"
        message = (
            "Multiple or moderate damage indicators were detected. "
            "A professional inspection is recommended to confirm the "
            "extent of the damage."
        )

    elif region_count > 0:
        title = "Visual inspection recommended"
        level = "VISUAL_INSPECTION"
        message = (
            "Potential damage regions were detected, but the estimated "
            "affected area is relatively limited. Review the highlighted "
            "areas and consider a professional inspection if necessary."
        )

    else:
        title = "No significant candidate region detected"
        level = "LOW_DETECTION"
        message = (
            "The current image did not produce significant damage "
            "candidate regions. This does not guarantee that the vehicle "
            "is undamaged."
        )

    if not validated:
        confidence_note = (
            "The current severity assessment is provisional because "
            "validated severity ground-truth labels are not available."
        )
    else:
        confidence_note = (
            "The severity result is based on the validated classification "
            "configuration."
        )

    factors = [
        f"{region_count} candidate region(s) detected",
        f"{damage_percent:.2f}% estimated affected area",
        f"{severity} severity assessment",
        f"{severity_score:.3f} assessment score",
    ]

    return {
        "level": level,
        "title": title,
        "message": message,
        "factors": factors,
        "provisional": not validated,
        "confidence_note": confidence_note,
    }
