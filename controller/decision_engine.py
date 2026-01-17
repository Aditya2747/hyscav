def decide_next_stage(risk_level):
    risk_level = risk_level.upper()  # normalize once

    if risk_level == "HIGH":
        return ["Mythril", "Echidna"]
    elif risk_level == "MEDIUM":
        return ["Mythril", "Echidna"]
    else:
        return ["Slither"]
