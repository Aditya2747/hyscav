import subprocess
import json
import os
import tempfile
import uuid
import re
from typing import Dict, Any, List

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Comprehensive mapping from Slither detector checks to Mythril-style issues
SLITHER_TO_MYTHRIL_MAP = {
    "reentrancy-eth": {"title": "Reentrancy", "severity": "high", "swc_id": "107"},
    "reentrancy-no-eth": {"title": "Reentrancy", "severity": "high", "swc_id": "107"},
    "reentrancy-unlimited-gas": {"title": "Reentrancy", "severity": "high", "swc_id": "107"},
    "arithmetic": {"title": "Integer Overflow and Underflow", "severity": "high", "swc_id": "101"},
    "integer-overflow": {"title": "Integer Overflow and Underflow", "severity": "high", "swc_id": "101"},
    "integer-underflow": {"title": "Integer Overflow and Underflow", "severity": "high", "swc_id": "101"},
    "overflow-simple-add": {"title": "Integer Overflow and Underflow", "severity": "high", "swc_id": "101"},
    "tx-origin": {"title": "Use of tx.origin", "severity": "medium", "swc_id": "115"},
    "tx-origin-usage": {"title": "Use of tx.origin", "severity": "medium", "swc_id": "115"},
    "unchecked-low-level-call": {"title": "Unchecked Call Return Value", "severity": "medium", "swc_id": "104"},
    "unchecked-transfer": {"title": "Unchecked Call Return Value", "severity": "medium", "swc_id": "104"},
    "unused-return": {"title": "Unchecked Call Return Value", "severity": "medium", "swc_id": "104"},
    "delegatecall": {"title": "Dangerous Delegatecall", "severity": "high", "swc_id": "112"},
    "controlled-delegatecall": {"title": "Dangerous Delegatecall", "severity": "high", "swc_id": "112"},
    "timestamp": {"title": "Timestamp Dependency", "severity": "low", "swc_id": "116"},
    "block-timestamp": {"title": "Timestamp Dependency", "severity": "low", "swc_id": "116"},
    "weak-randomness": {"title": "Weak Randomness", "severity": "medium", "swc_id": "120"},
    "suicidal": {"title": "Access Control", "severity": "high", "swc_id": "106"},
    "unprotected-selfdestruct": {"title": "Access Control", "severity": "high", "swc_id": "106"},
    "external-function": {"title": "Access Control", "severity": "low", "swc_id": "106"},
    "uninitialized-storage": {"title": "Uninitialized Storage Pointer", "severity": "high", "swc_id": "109"},
    "uninitialized-state": {"title": "Uninitialized Storage Pointer", "severity": "high", "swc_id": "109"},
    "uninitialized-local": {"title": "Uninitialized Storage Pointer", "severity": "medium", "swc_id": "109"},
    "dos": {"title": "Denial of Service", "severity": "medium", "swc_id": "113"},
    "missing-calls": {"title": "Denial of Service", "severity": "medium", "swc_id": "113"},
    "front-running": {"title": "Front-Running", "severity": "medium", "swc_id": "114"},
    "bad-randomness": {"title": "Weak Randomness", "severity": "medium", "swc_id": "120"},
}

# Docker images to try, in priority order
MYTHRIL_IMAGES = [
    {"image": "mythril/myth:latest", "cmd_format": "standard"},
    {"image": "trailofbits/mythril", "cmd_format": "standard"},
    {"image": "ghcr.io/crytic/mythril:latest", "cmd_format": "standard"},
    {"image": "crytic/ether-slim:latest", "cmd_format": "ether_slim"},
]


def _build_docker_cmd(image_config: Dict[str, str], contract_path: str, contract_name: str) -> List[str]:
    """Build the Docker command for a given image configuration."""
    fmt = image_config.get("cmd_format", "standard")
    image = image_config["image"]

    if fmt == "ether_slim":
        return [
            "docker", "run", "--rm",
            "-v", f"{PROJECT_DIR}:/code",
            image,
            "sh", "-c",
            f"pip install mythril && myth analyze /code/{contract_name} -o json --execution-timeout 60"
        ]
    else:
        return [
            "docker", "run", "--rm",
            "-v", f"{PROJECT_DIR}:/code",
            image,
            "analyze", f"/code/{contract_name}",
            "-o", "json",
            "--execution-timeout", "60"
        ]


def parse_mythril_output(text: str) -> List[Dict[str, Any]]:
    """Parse Mythril's plain-text output into structured issues."""
    issues = []
    sections = re.split(r'==== ', text)[1:]
    for section in sections:
        lines = section.strip().split('\n')
        if lines:
            title = lines[0].strip()
            swc_match = re.search(r'SWC ID: (\d+)', section)
            swc_id = swc_match.group(1) if swc_match else ''
            severity_match = re.search(r'Severity: (\w+)', section)
            severity = severity_match.group(1) if severity_match else 'medium'
            description = 'Mythril detected ' + title
            issues.append({
                'title': title,
                'severity': severity,
                'description': description,
                'swc_id': swc_id
            })
    return issues


def parse_mythril_json(json_text: str) -> Dict[str, Any]:
    """Parse Mythril JSON output. Returns {'issues': [...]} or raises ValueError."""
    data = json.loads(json_text)
    issues = []
    for issue in data.get("issues", []):
        issues.append({
            'title': issue.get("title", "Unknown"),
            'severity': issue.get("severity", "medium").lower(),
            'description': issue.get("description", ""),
            'swc_id': str(issue.get("swc-id", "")),
            'line': issue.get("lineno", None),
        })
    return {'issues': issues}


def run_slither_simple(contract_path: str) -> Dict[str, Any]:
    """Run Slither and return raw JSON data."""
    temp_dir = tempfile.gettempdir()
    output_file = os.path.join(temp_dir, f"slither_{uuid.uuid4().hex}.json")
    command = [
        "slither",
        contract_path,
        "--json", output_file,
        "--disable-color"
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            os.remove(output_file)
            return data
        except Exception:
            if os.path.exists(output_file):
                os.remove(output_file)
    return {}


def slither_proxy_fallback(contract_path: str) -> Dict[str, Any]:
    """Comprehensive Slither-based fallback when all Mythril Docker images fail."""
    slither_data = run_slither_simple(contract_path)
    detectors = slither_data.get("results", {}).get("detectors", []) if slither_data else []

    issues = []
    seen_titles = set()

    for detector in detectors:
        if not isinstance(detector, dict):
            continue
        check = detector.get("check", "").lower()
        mapping = None
        if check in SLITHER_TO_MYTHRIL_MAP:
            mapping = SLITHER_TO_MYTHRIL_MAP[check]
        else:
            for key, val in SLITHER_TO_MYTHRIL_MAP.items():
                if key in check or check in key:
                    mapping = val
                    break

        if mapping:
            title = mapping["title"]
            if title not in seen_titles:
                seen_titles.add(title)
                issues.append({
                    "title": title + " (proxy)",
                    "severity": mapping["severity"],
                    "description": f"Slither proxy detected {title} via '{check}' detector",
                    "swc_id": mapping["swc_id"]
                })

    if issues:
        print(f"[MYTHRIL] Slither proxy: {len(issues)} issue(s)")
    else:
        print("[MYTHRIL] Slither proxy: no issues")
    return {"issues": issues}


def run_mythril(contract_path: str) -> Dict[str, Any]:
    """Run Mythril analysis using Docker, with multiple image fallbacks."""
    contract_name = os.path.basename(contract_path)

    # Verify Docker is available
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[MYTHRIL] Docker unavailable; using Slither proxy fallback")
        return slither_proxy_fallback(contract_path)

    images_tried = []
    for img_config in MYTHRIL_IMAGES:
        image = img_config["image"]
        cmd = _build_docker_cmd(img_config, contract_path, contract_name)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            stderr = result.stderr or ""

            # Image not present locally
            if "Unable to find image" in stderr or "pull access denied" in stderr or "not found" in stderr.lower():
                images_tried.append(image)
                continue

            # Got stdout — try to parse
            if result.stdout:
                try:
                    data = parse_mythril_json(result.stdout)
                    print(f"[MYTHRIL] {len(data['issues'])} issue(s) via {image}")
                    return data
                except (json.JSONDecodeError, ValueError):
                    issues = parse_mythril_output(result.stdout)
                    if issues:
                        print(f"[MYTHRIL] {len(issues)} issue(s) via {image} (text mode)")
                        return {"issues": issues}
                    else:
                        print("[MYTHRIL] No issues detected")
                        return {"issues": []}
            else:
                if result.returncode == 0:
                    print("[MYTHRIL] No issues detected")
                else:
                    images_tried.append(image)
                    continue

        except subprocess.TimeoutExpired:
            images_tried.append(image)
            continue
        except Exception:
            images_tried.append(image)
            continue

    # All images failed — fallback to Slither
    if images_tried:
        print(f"[MYTHRIL] Images unavailable ({', '.join(images_tried)}); falling back to Slither proxy")
    return slither_proxy_fallback(contract_path)


def simplify_mythril_issues(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Simplify Mythril analysis results into a standardized issue format."""
    issues = []
    for issue in data.get("issues", []):
        issues.append({
            "tool": "Mythril",
            "title": issue.get("title", "Mythril issue"),
            "severity": issue.get("severity", "medium"),
            "description": issue.get("description", ""),
            "location": str(issue.get("location", ""))
        })
    return issues


if __name__ == "__main__":
    import sys
    data = run_mythril(sys.argv[1]) if len(sys.argv) > 1 else {"issues": []}
    print(json.dumps(data, indent=2))

