# HySCAV - Smart Contract Vulnerability Analyzer (ML + Tools)

## 🎯 Status: Complete
- ✅ ML trained (Slither features → RF model)
- ✅ Pipeline: Slither + ML + Mythril/Echidna
- ✅ SmartBugs dataset + reports
- ✅ Docker ready

## 🚀 Quick Start
```bash
python main.py analyze contracts/Bank.sol
```
Output: risk HIGH, report.xlsx.

## 🔧 Tools Setup (Mythril/Echidna)
Docker daemon running (`docker ps` OK).

1. **Run setup**:
```bash
setup_tools.bat
```
- GitHub PAT (github.com/settings/tokens → classic).
- Pulls mythril/echidna.
- Tests full pipeline.

2. **Manual**:
```
docker login ghcr.io -u USER -p PAT
docker pull ghcr.io/crytic/mythril:latest
docker pull ghcr.io/crytic/echidna:latest
python main.py analyze contracts/ReentrancyTest.sol
```

## 📊 ML + Dataset
- `python ml/train_model.py` → model.pkl/dataset.csv
- SmartBugs 143 contracts (reports/smartbugs_cumulative_report.xlsx)

## 📈 Reports
reports/*.xlsx – cumulative vulns/scores.

**Production ready** – full vuln scanner!
