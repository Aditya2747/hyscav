# Smart Contract Vulnerability Testing Pipeline

## Setup
```bash
pip install -r pipeline/requirements.txt
pip install slither-analyzer mythril  # if not already
```

## Usage
```bash
# Full pipeline on SmartBugs + Etherscan contracts
python pipeline/main.py --all --etherscan-key=YOUR_KEY

# Steps
python pipeline/main.py --fetch --etherscan-key=YOUR_KEY  # download contracts
python pipeline/main.py --run  # hyscav + slither + mythril
python pipeline/main.py --evaluate  # F1 metrics table

# Custom dirs
python pipeline/main.py --run --contracts-dir my_contracts --results-dir my_results
```

## Structure
- `contracts/` : .sol files + metadata.json (source/labels)
- `results/` : hyscav_results.json, slither_results.json, mythril_results.json, evaluation_report.json

Categories tracked: reentrancy, integer_overflow, access_control, etc.

See TODO.md for progress.

