#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from pipeline.fetcher import ContractFetcher
from pipeline.slither_runner import SlitherRunner
from pipeline.mythril_runner import MythrilRunner
from pipeline.hyscav_runner import HySCAVRunner
from pipeline.evaluator import Evaluator

def main():
    parser = argparse.ArgumentParser(description="Smart Contract Vulnerability Testing Pipeline")
    parser.add_argument("--contracts-dir", default="contracts", help="Contracts folder")
    parser.add_argument("--results-dir", default="results", help="Results folder")
    parser.add_argument("--etherscan-key", help="Etherscan API key")
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--fetch", action="store_true", help="Fetch contracts")
    group.add_argument("--run", action="store_true", help="Run all tools")
    group.add_argument("--evaluate", action="store_true", help="Evaluate metrics")
    group.add_argument("--all", action="store_true", help="Run full pipeline")
    
    args = parser.parse_args()
    
    contracts_path = Path(args.contracts_dir)
    results_path = Path(args.results_dir)
    
    if args.fetch or args.all:
        fetcher = ContractFetcher(contracts_path, args.etherscan_key)
        fetcher.run()
    
    if args.run or args.all:
        print("Running hy-scav...")
        hyscav = HySCAVRunner(results_path)
        hyscav.run_all(contracts_path)
        
        print("Running Slither...")
        slither = SlitherRunner(results_path)
        slither.run_all(contracts_path)
        
        print("Running Mythril...")
        mythril = MythrilRunner(results_path)
        mythril.run_all(contracts_path)
    
    if args.evaluate or args.all:
        evaluator = Evaluator(results_path)
        evaluator.run()

if __name__ == "__main__":
    main()

