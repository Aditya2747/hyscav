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
    output_file = os.path.join(
        temp_dir, f"slither_{uuid.uuid4().hex}.json"
    )

    command = [
        "slither",
        contract_path,
        "--json",
        output_file,
        "--disable-color"
    ]

    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False
    )

    if not os.path.exists(output_file):
        print("[SLITHER][ERROR] Slither did not produce JSON output")
        return None

    try:
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[SLITHER][ERROR] JSON read failed: {e}")
        data = None
    finally:
        os.remove(output_file)

    print("[SLITHER] Analysis completed")
    return data


def simplify_slither_issues(slither_data: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Simplify Slither analysis results into a standardized issue format.

    Args:
        slither_data (Optional[Dict[str, Any]]): Raw Slither analysis output

    Returns:
        List[Dict[str, Any]]: List of simplified vulnerability issues

    Example:
        >>> data = {"results": {"detectors": [{"check": "reentrancy", "impact": "high"}]}}
        >>> simplify_slither_issues(data)
        [{'tool': 'slither', 'title': 'reentrancy', 'severity': 'high', ...}]
    """
    if not slither_data or not isinstance(slither_data, dict):
        return []

    issues = []
    detectors = slither_data.get("results", {}).get("detectors", [])

    if not isinstance(detectors, list):
        logger.warning("Invalid detectors format in Slither data")
        return []

    for detector in detectors:
        if not isinstance(detector, dict):
            continue

        try:
            element = detector.get("elements", [{}])[0]
            if not isinstance(element, dict):
                element = {}

            source_map = element.get("source_mapping", {})
            if not isinstance(source_map, dict):
                source_map = {}

            issue = {
                "tool": "slither",
                "title": detector.get("check", "unknown"),
                "severity": detector.get("impact", "unknown"),
                "contract": element.get("contract", "unknown"),
                "function": element.get("name", "unknown"),
                "line": source_map.get("lines", []),
                "description": detector.get("description", "No description available")
            }
            issues.append(issue)
        except Exception as e:
            print(f"[SLITHER][WARNING] Error processing Slither detector: {e}")
            continue

    print(f"[SLITHER] Simplified {len(issues)} Slither issues")
    return issues


def export_slither_issues_to_csv(issues: List[Dict[str, Any]], output_path: str) -> bool:
    """
    Export Slither issues to CSV format.

    Args:
        issues: List of simplified Slither issues
        output_path: Path to save the CSV file

    Returns:
        bool: True if export successful, False otherwise
    """
    try:
        if not issues:
            print("No issues to export")
            return False

        # Define CSV headers
        headers = ['Tool', 'Title', 'Severity', 'Contract', 'Function', 'Line', 'Description']

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()

            for issue in issues:
                # Convert line list to string for CSV
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

        print(f"Exported {len(issues)} issues to CSV: {output_path}")
        return True

    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False


def export_slither_issues_to_excel(issues: List[Dict[str, Any]], output_path: str) -> bool:
    """
    Export Slither issues to Excel format.

    Args:
        issues: List of simplified Slither issues
        output_path: Path to save the Excel file

    Returns:
        bool: True if export successful, False otherwise
    """
    try:
        import pandas as pd
    except ImportError:
        print("pandas not installed. Install with: pip install pandas openpyxl")
        return False

    try:
        if not issues:
            print("No issues to export")
            return False

        # Prepare data for DataFrame
        data = []
        for issue in issues:
            # Convert line list to string for Excel
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

        # Export to Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Slither_Issues', index=False)

            # Auto-adjust column widths
            worksheet = writer.sheets['Slither_Issues']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                worksheet.column_dimensions[column_letter].width = adjusted_width

        print(f"Exported {len(issues)} issues to Excel: {output_path}")
        return True

    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return False
