import subprocess
import json
import os
import tempfile
import uuid
import csv
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def run_slither(contract_path):
    print("[SLITHER] Running static analysis...")

    temp_dir = tempfile.gettempdir()
    output_file = os.path.join(temp_dir, f"slither_{uuid.uuid4().hex}.json")

    # Use absolute path to avoid issues
    abs_path = os.path.abspath(contract_path)
    contract_dir = os.path.dirname(abs_path)
    
    # Strategy 1: Use shell=True for Windows compatibility
    print(f"[SLITHER] Analyzing {os.path.basename(abs_path)}...")
    command = f'slither "{abs_path}" --json "{output_file}" --disable-color'
    
    result = subprocess.run(
        command, 
        shell=True,
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    
    if result.returncode != 0:
        # Strategy 2: Try with --skip-compilation-check
        print("[SLITHER] Retry with --skip-compilation-check...")
        command = f'slither "{abs_path}" --json "{output_file}" --disable-color --skip-compilation-check'
        
        result = subprocess.run(
            command, 
            shell=True,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
    
    # Check for output file
    if not os.path.exists(output_file):
        # Try to get error info
        stderr_output = result.stderr.decode('utf-8', errors='replace') if result.stderr else ""
        stdout_output = result.stdout.decode('utf-8', errors='replace') if result.stdout else ""
        
        # Sometimes slither outputs to stdout even on success
        if stdout_output and "analyzed" in stdout_output:
            print("[SLITHER] Analysis completed (stdout)")
        else:
            print(f"[SLITHER][ERROR] No JSON output. stderr: {stderr_output[:200]}")
            return None

    try:
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        # Check if there's text output we can parse
        stdout_output = result.stdout.decode('utf-8', errors='replace') if result.stdout else ""
        if stdout_output and "result(s) found" in stdout_output:
            print("[SLITHER] Analysis had text output, but no JSON")
            # Could add text parsing here
            return None
        print(f"[SLITHER][ERROR] JSON parse failed: {e}")
        data = None
    finally:
        try:
            os.remove(output_file)
        except:
            pass

    print("[SLITHER] Analysis completed")
    return data


def simplify_slither_issues(slither_data: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not slither_data or not isinstance(slither_data, dict):
        return []
    
    issues = []
    for detector in slither_data.get("results", {}).get("detectors", []):
        if not isinstance(detector, dict):
            continue
        element = detector.get("elements", [{}])[0] if detector.get("elements") else {}
        source_map = element.get("source_mapping", {}) if element else {}
        
        issue = {
            "tool": "slither",
            "title": detector.get("check", "unknown"),
            "severity": detector.get("impact", "unknown"),
            "contract": element.get("contract", "unknown"),
            "function": element.get("name", "unknown"),
            "line": source_map.get("lines", []) if source_map else [],
            "description": detector.get("description", "No description")
        }
        issues.append(issue)
    
    print(f"[SLITHER] Simplified {len(issues)} issues")
    return issues


def export_slither_issues_to_csv(issues: List[Dict[str, Any]], output_path: str) -> bool:
    try:
        if not issues:
            print("No issues to export")
            return False
        headers = ['Tool', 'Title', 'Severity', 'Contract', 'Function', 'Line', 'Description']
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for issue in issues:
                line_str = ', '.join(map(str, issue.get('line', []))) if issue.get('line') else ''
                writer.writerow({
                    'Tool': issue.get('tool', ''),
                    'Title': issue.get('title', ''),
                    'Severity': issue.get('severity', ''),
                    'Contract': issue.get('contract', ''),
                    'Function': issue.get('function', ''),
                    'Line': line_str,
                    'Description': issue.get('description', '')
                })
        print(f"Exported {len(issues)} issues to CSV")
        return True
    except Exception as e:
        print(f"CSV export error: {e}")
        return False


def export_slither_issues_to_excel(issues: List[Dict[str, Any]], output_path: str) -> bool:
    try:
        import pandas as pd
    except ImportError:
        print("pandas not installed")
        return False
    
    try:
        if not issues:
            print("No issues to export")
            return False
        data = []
        for issue in issues:
            line_str = ', '.join(map(str, issue.get('line', []))) if issue.get('line') else ''
            data.append({
                'Tool': issue.get('tool', ''),
                'Title': issue.get('title', ''),
                'Severity': issue.get('severity', ''),
                'Contract': issue.get('contract', ''),
                'Function': issue.get('function', ''),
                'Line': line_str,
                'Description': issue.get('description', '')
            })
        df = pd.DataFrame(data)
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Slither_Issues', index=False)
        print(f"Exported {len(issues)} issues to Excel")
        return True
    except Exception as e:
        print(f"Excel export error: {e}")
        return False
