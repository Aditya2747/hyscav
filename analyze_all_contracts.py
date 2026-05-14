"""
Analyze all contracts in contracts/ folder and generate Excel reports.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyzers.slither_runner import run_slither, simplify_slither_issues
from controller.feature_extractor import extract_slither_features
from ml.risk_model import predict_risk


def analyze_contract(contract_path: str) -> dict:
    """Analyze a single contract and return results."""
    print(f"Analyzing {os.path.basename(contract_path)}...")
    
    slither_data = run_slither(contract_path)
    
    if slither_data is None:
        return None
    
    issues = simplify_slither_issues(slither_data)
    features = extract_slither_features(slither_data)
    level, score = predict_risk(features)
    
    return {
        'contract': os.path.basename(contract_path),
        'path': contract_path,
        'slither_issues': len(issues),
        'high': features.get('high', 0),
        'medium': features.get('medium', 0),
        'low': features.get('low', 0),
        'unique_vuln_types': features.get('unique_vuln_types', 0),
        'has_reentrancy': features.get('has_reentrancy', False),
        'has_overflow': features.get('has_overflow', False),
        'has_unchecked_call': features.get('has_unchecked_call', False),
        'has_access_control': features.get('has_access_control', False),
        'has_tx_origin': features.get('has_tx_origin', False),
        'has_delegatecall': features.get('has_delegatecall', False),
        'risk_level': level,
        'risk_score': score,
        'issues': issues
    }


def analyze_all_contracts() -> pd.DataFrame:
    """Analyze all contracts in contracts/ folder."""
    contracts_dir = 'contracts'
    results = []
    
    files = sorted(os.listdir(contracts_dir))
    total = len([f for f in files if f.endswith('.sol')])
    
    print(f"Found {total} Solidity contracts")
    print("=" * 50)
    
    for i, filename in enumerate(files):
        if not filename.endswith('.sol'):
            continue
            
        contract_path = os.path.join(contracts_dir, filename)
        print(f"[{i+1}/{total}] {filename}")
        
        result = analyze_contract(contract_path)
        
        if result:
            results.append(result)
        else:
            print(f"  Skipped (Slither failed)")
    
    return pd.DataFrame(results)


def generate_training_report():
    """Generate report of contracts used to train the model."""
    print("\n" + "=" * 60)
    print("Generating Training Data Report")
    print("=" * 60)
    
    # Read training data
    if not os.path.exists('dataset.csv'):
        print("ERROR: dataset.csv not found. Run retrain_model.py first.")
        return None
    
    df = pd.read_csv('dataset.csv')
    
    # Generate Excel report
    output_path = 'reports/model_training_report.xlsx'
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Summary sheet
        summary = pd.DataFrame({
            'Metric': [
                'Total Samples',
                'LOW Risk Samples',
                'MEDIUM Risk Samples',
                'HIGH Risk Samples',
                'SmartBugs Contracts',
                'Local Contracts',
                'Test Samples'
            ],
            'Value': [
                len(df),
                len(df[df['label'] == 0]),
                len(df[df['label'] == 1]),
                len(df[df['label'] == 2]),
                43,  # SmartBugs
                16,  # Local
                5    # Test
            ]
        })
        summary.to_excel(writer, sheet_name='Summary', index=False)
        
        # Full training data
        df.to_excel(writer, sheet_name='Training Data', index=False)
        
        # Statistics by category
        if 'contract' in df.columns:
            # Extract category from contract name
            df_cat = df.copy()
            df_cat['source'] = df_cat['contract'].apply(
                lambda x: 'SmartBugs' if '/' in x else ('Test' if x.startswith('test_') else 'Local')
            )
            
            stats = df_cat.groupby('source').agg({
                'label': ['count', 'mean'],
                'high': 'sum',
                'medium': 'sum'
            }).round(2)
            stats.to_excel(writer, sheet_name='Stats by Source')
    
    print(f"Training report saved: {output_path}")
    return output_path


def main():
    """Main function."""
    print("=" * 60)
    print("HySCAV Contract Analysis Report Generator")
    print("=" * 60)
    
    # Analyze all contracts
    print("\n[1] Analyzing all contracts...")
    df = analyze_all_contracts()
    
    if df is None or len(df) == 0:
        print("No contracts analyzed")
        return
    
    print(f"\nAnalyzed {len(df)} contracts")
    
    # Save full analysis to Excel
    output_path = 'reports/all_contracts_analyzed.xlsx'
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Main results (without issues list for Excel)
        main_cols = ['contract', 'slither_issues', 'high', 'medium', 'low', 
                    'unique_vuln_types', 'risk_level', 'risk_score']
        
        # Add vulnerability flags
        vuln_flags = ['has_reentrancy', 'has_overflow', 'has_unchecked_call',
                     'has_access_control', 'has_tx_origin', 'has_delegatecall']
        
        df_main = df[main_cols + vuln_flags].copy()
        df_main.to_excel(writer, sheet_name='Summary', index=False)
        
        # Summary by risk level
        risk_summary = df.groupby('risk_level').agg({
            'contract': 'count',
            'risk_score': 'mean',
            'slither_issues': 'sum'
        }).round(2)
        risk_summary.columns = ['count', 'avg_score', 'total_issues']
        risk_summary.to_excel(writer, sheet_name='By Risk Level')
        
        # High risk contracts
        high_risk = df[df['risk_level'] == 'HIGH'][['contract', 'risk_score', 'slither_issues']]
        high_risk.to_excel(writer, sheet_name='HIGH Risk', index=False)
        
        # Vulnerability flags summary
        vuln_summary = pd.DataFrame({
            'Vulnerability': ['Reentrancy', 'Overflow', 'Unchecked Call', 
                              'Access Control', 'tx.origin', 'Delegatecall'],
            'Count': [
                df['has_reentrancy'].sum(),
                df['has_overflow'].sum(),
                df['has_unchecked_call'].sum(),
                df['has_access_control'].sum(),
                df['has_tx_origin'].sum(),
                df['has_delegatecall'].sum()
            ]
        })
        vuln_summary.to_excel(writer, sheet_name='Vulnerability Types', index=False)
    
    print(f"\nFull analysis saved: {output_path}")
    
    # Generate training report
    print("\n[2] Generating training data report...")
    generate_training_report()
    
    print("\n" + "=" * 60)
    print("Reports generated successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
