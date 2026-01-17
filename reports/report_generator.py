import json
import os
from datetime import datetime


def generate_report(
    contract_path,
    features,
    risk_level,
    risk_score,
    tools_run,
    issues
):
    report = {
        "contract": os.path.basename(contract_path),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "static_analysis_features": features,

        "risk_assessment": {
            "risk_level": risk_level,
            "risk_score": risk_score
        },

        "tools_executed": tools_run,

        "vulnerabilities": {
            "total": len(issues),
            "details": issues
        }
    }

    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)

    report_file = os.path.join(
        report_dir,
        f"report_{os.path.basename(contract_path)}.json"
    )

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print(f"[REPORT] Report generated: {report_file}")
