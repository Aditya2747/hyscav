def decide_next_stage(risk_level):
    if risk_level == "HIGH":
        return ["Mythril", "Manticore", "Echidna"]
    elif risk_level == "MEDIUM":
        return ["Mythril", "Echidna"]
    else:
        return ["Slither"]
