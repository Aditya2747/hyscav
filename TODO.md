# HySCAV TODO

## Automation Progress
Plan approved by user.
- [x] Edit reports/report_generator.py to append to contracts_summary.xlsx (completed)
- [x] Test with Bank.sol (completed)
- [x] Test with ReentrancyTest.sol (completed)
- [x] Verify table format (completed)

## Git Update Progress
- [x] Create branch blackboxai/update-project
- [x] git add -A
- [x] git commit & push

## Vulnerability Testing Pipeline
- [ ] Update main.py for pipeline CLI (--fetch --run --evaluate --all)
- [ ] pipeline/fetcher.py (Etherscan + SmartBugs clone/parse)
- [ ] pipeline/hyscav_runner.py (subprocess main.py analyze, parse JSON/stdout)
- [ ] pipeline/slither_runner.py (slither --json, map categories)
- [ ] pipeline/mythril_runner.py (myth analyze -o json)
- [ ] pipeline/evaluator.py (metrics F1 table)
- [ ] Test pipeline on SmartBugs dataset

