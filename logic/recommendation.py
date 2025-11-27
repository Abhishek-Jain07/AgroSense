# logic/recommendation.py
def interpret_level(val_kind, val):
    # convert categorical to approximate numeric ranges or flags if needed
    if val_kind == "numeric":
        return val
    else:
        # categorical: return a sentinel, e.g. -1 or None or leave as level
        return val  # keep as "Low"/"Medium"/"High"

def recommend(soil_type, moisture, organic, n, p, k, season, chunks):
    soil_type = soil_type.title()
    moisture = moisture.title()
    organic = organic.title()
    # n, p, k may be numeric or level
    # Interpret values
    N = interpret_level(n[0], n[1])
    P = interpret_level(p[0], p[1])
    K = interpret_level(k[0], k[1])

    # basic crop selection
    possible = []
    for c in chunks:
        if soil_type in c.get("soil_tags", []):
            txt = c.get("text", "").lower()
            for crop in ["maize", "millet", "pearlmillet", "bajra", "sorghum", "groundnut", "pigeonpea", "wheat", "salt-tolerant", "millet", "pulses"]:
                if crop in txt:
                    possible.append(crop.capitalize())
    possible = list(dict.fromkeys(possible))

    # fertilizer logic improved
    fert = []
    soil_improve = []
    if N == "Low" or (isinstance(N, (int, float)) and N < 30):
        fert.append("Apply Urea (for N) + FYM/compost if organic is Poor or Average")
    if P == "Low" or (isinstance(P, (int, float)) and P < 15):
        fert.append("Apply DAP or SSP (for P)")
    if K == "Low" or (isinstance(K, (int, float)) and K < 40):
        fert.append("Apply MOP (for K)")
    if organic in ("Poor",):
        soil_improve.append("Add 4–6 t/acre FYM or green-manure (e.g. Dhaincha)")
    if moisture == "Low":
        soil_improve.append("Use mulching or drip/sprinkler to conserve moisture")

    care = []
    if "Maize" in possible:
        care.append("Sow June–July, 3–4 irrigations, weed control early")
    elif "Wheat" in possible:
        care.append("Sow Nov–Dec, split N application, 4–5 irrigations if floodplain soil")
    else:
        care.append("Ensure timely irrigation, good drainage, organic matter addition")

    return {
        "crops": possible[:3] or ["Millets / Pulses (fallback)"],
        "fertilizer": fert,
        "soil_improvement": soil_improve,
        "care_tips": care
    }
