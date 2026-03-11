#!/usr/bin/env python3
"""
Script to run Slither analysis and export issues to CSV or Excel format.

Usage:
    python export_slither_issues.py <contract_path> [--format csv|excel] [--output output_file]

Example:
    python export_slither_issues.py contracts/Bank.sol --format csv --output slither_issues.csv
    python export_slither_issues.py contracts/Bank.sol --format excel --output slither_issues.xlsx
"""

import argparse
import os
import sys
from analyzers.slither_runner import run_slither, simplify_slither_issues, export_slither_issues_to_csv, export_slither_issues_to_excel


def main():
    parser = argparse.ArgumentParser(description='Export Slither analysis results to CSV or Excel')
    parser.add_argument('contract_path', help='Path to the Solidity contract file')
    parser.add_argument('--format', choices=['csv', 'excel'], default='csv',
                       help='Output format (default: csv)')
    parser.add_argument('--output', '-o', help='Output file path (default: auto-generated)')

    args = parser.parse_args()

    # Validate contract path
    if not os.path.exists(args.contract_path):
        print(f"Error: Contract file not found: {args.contract_path}")
        sys.exit(1)

    if not args.contract_path.endswith('.sol'):
        print(f"Error: File must be a Solidity contract (.sol): {args.contract_path}")
        sys.exit(1)

    # Generate default output path if not provided
    if not args.output:
        base_name = os.path.splitext(os.path.basename(args.contract_path))[0]
        extension = 'csv' if args.format == 'csv' else 'xlsx'
        args.output = f"slither_issues_{base_name}.{extension}"

    print(f"Running Slither analysis on: {args.contract_path}")

    # Run Slither analysis
    slither_data = run_slither(args.contract_path)
    if slither_data is None:
        print("Error: Slither analysis failed")
        sys.exit(1)

    # Simplify issues
    issues = simplify_slither_issues(slither_data)
    print(f"Found {len(issues)} issues")

    if not issues:
        print("No issues found to export")
        sys.exit(0)

    # Export based on format
    success = False
    if args.format == 'csv':
        success = export_slither_issues_to_csv(issues, args.output)
    elif args.format == 'excel':
        success = export_slither_issues_to_excel(issues, args.output)

    if success:
        print(f"Successfully exported issues to: {args.output}")
    else:
        print("Failed to export issues")
        sys.exit(1)


if __name__ == '__main__':
    main()
