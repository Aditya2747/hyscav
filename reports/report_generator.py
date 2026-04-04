"""Report generator module for HySCAV.

This module generates Excel reports containing analysis results,
including vulnerability findings, risk assessments, and tool execution details.
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    import pandas as pd
except ImportError:
    raise ImportError("pandas and openpyxl required. Install with: pip install pandas openpyxl")

logger = logging.getLogger(__name__)


def update_master_summary(
    contract_path: str,
    features: Dict[str, Any],
    risk_level: str,
    risk_score: float,
    total_issues: int,
    key_vuln: str,
    report_file: str
):
    """
    Append analysis results to master summary Excel file.
    """
    import pandas as pd
    from datetime import datetime
    import os
    
    master_path = "reports/contracts_summary.xlsx"
    os.makedirs(os.path.dirname(master_path), exist_ok=True)
    
    contract_name = os.path.basename(contract_path)
    
    new_row = pd.DataFrame([{
        'Timestamp': datetime.now().strftime('%m-%d-%Y %H:%M'),
        'Contract': contract_name,
        'Total Issues': total_issues,
        'High': features.get('high', 0),
        'Risk Score': round(risk_score, 1),
        'Risk Level': risk_level,
        'Key Vulnerability': key_vuln,
        'Report File': os.path.basename(report_file)
    }])
    
    try:
        existing_df = pd.read_excel(master_path, sheet_name='Summary')
        summary_df = pd.concat([existing_df, new_row], ignore_index=True)
        summary_df.to_excel(master_path, sheet_name='Summary', index=False)
        print(f"[MASTER SUMMARY] Appended to Excel: {master_path}")
    except FileNotFoundError:
        summary_df = new_row
        summary_df.to_excel(master_path, sheet_name='Summary', index=False)
        print(f"[MASTER SUMMARY] Created Excel: {master_path}")
    except Exception as e:
        print(f"[MASTER SUMMARY] Excel error: {e}, fallback to CSV")
        csv_path = "reports/contracts_summary.csv"
        try:
            existing_df = pd.read_csv(csv_path)
            summary_df = pd.concat([existing_df, new_row], ignore_index=True)
        except FileNotFoundError:
            summary_df = new_row
        summary_df.to_csv(csv_path, index=False)
        print(f"[MASTER SUMMARY] Fallback CSV: {csv_path}")


def generate_report(
    contract_path: str,
    features: Dict[str, Any],
    risk_level: str,
    risk_score: float,
    tools_run: List[str],
    issues: List[Dict[str, Any]]
) -> str:
    """
    Generate an Excel report with analysis results.

    This function creates a comprehensive report containing:
    - Contract information
    - Static analysis features
    - Risk assessment results
    - Tools that were executed
    - Vulnerability details

    Args:
        contract_path (str): Path to the analyzed Solidity contract
        features (Dict[str, Any]): Feature dictionary from feature extraction
        risk_level (str): Risk level ("HIGH", "MEDIUM", "LOW")
        risk_score (float): Numeric risk score
        tools_run (List[str]): List of analysis tools that were executed
        issues (List[Dict[str, Any]]): List of vulnerability issues found

    Returns:
        str: Path to the generated report file

    Example:
        >>> report_path = generate_report(
        ...     "contracts/Bank.sol",
        ...     {"high": 1, "medium": 2, "low": 3},
        ...     "HIGH", 7.0,
        ...     ["Slither", "Mythril"],
        ...     [{"tool": "slither", "title": "reentrancy"}]
        ... )
        >>> print(report_path)
        reports/report_Bank.sol.xlsx
    """
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
        f"report_{os.path.basename(contract_path)}.xlsx"
    )

    try:
        vuln_data = []
        for issue in issues:
            line = issue.get('line', [])
            if isinstance(line, list):
                line_str = ', '.join(map(str, line))
            else:
                line_str = str(line)
            
            vuln_data.append({
                'Tool': issue.get('tool', ''),
                'Title': issue.get('title', ''),
                'Severity': issue.get('severity', ''),
                'Contract': issue.get('contract', ''),
                'Function': issue.get('function', ''),
                'Line': line_str,
                'Description': issue.get('description', '')
            })
        
        df_vulns = pd.DataFrame(vuln_data) if vuln_data else pd.DataFrame()
        
        summary_data = [{
            'Contract': report['contract'],
            'Timestamp': report['timestamp'],
            'Risk Level': risk_level,
            'Risk Score': risk_score,
            'Total Issues': len(issues),
            'High': features.get('high', 0),
            'Medium': features.get('medium', 0),
            'Low': features.get('low', 0),
            'Tools Executed': ', '.join(tools_run)
        }]
        df_summary = pd.DataFrame(summary_data)
        
        with pd.ExcelWriter(report_file, engine='openpyxl') as writer:
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            if not df_vulns.empty:
                df_vulns.to_excel(writer, sheet_name='Vulnerabilities', index=False)
            
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        logger.info(f"[REPORT] Report generated: {report_file}")
        
        # Auto-update master summary
        key_vuln = "None"
        for issue in issues:
            if issue.get('severity', '').lower() == 'high':
                key_vuln = issue.get('title', 'Unknown High')
                break
            if 'reentrancy' in str(issue.get('title', '')).lower():
                key_vuln = issue.get('title', 'Reentrancy')
                break
        
        update_master_summary(
            contract_path, 
            features, 
            risk_level, 
            risk_score, 
            len(issues),
            key_vuln,
            report_file
        )
    
    except Exception as e:
        logger.error(f"[REPORT] Failed to generate report: {e}")
        raise

    return report_file

