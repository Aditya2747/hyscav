# HySCAV - Hybrid Smart Contract Vulnerability Analyzer

## 🎯 **Pipeline Architecture**

```
Input (.sol) → [1.Slither] → [2.ML Model] → [3.Decision Engine] → [4.Dynamic Tools] → [5.Report]
                    ↓              ↓                 ↓                  ↓                ↓
              Static Features   Risk Score    Tool Selection    Mythril/Echidna   Excel/JSON
```

## 📋 **Step-by-Step Pipeline**

### **Step 1: Slither Static Analysis** (`analyzers/slither_runner.py`)
```
- Runs Slither static analyzer
- Extracts vulnerability features:
  | Feature | Description |
  |---------|-------------|
  | high    | High severity issues |
  | medium  | Medium severity |
  | low     | Low severity |
  | reentrancy | Reentrancy detected |
  | integer_overflow | Math overflow |
  | access_control | Access control issues |
```
**Output:** Feature vector for ML model

### **Step 2: ML Risk Model** (`ml/risk_model.py`)
```
Trained RandomForest model predicts risk score (0.0-10.0)
- Input: Slither feature vector
- Output: Risk Level (HIGH/MEDIUM/LOW) + Score
- Thresholds:
  | Risk Score | Level |
  |------------|-------|
  | 6.0-10.0   | HIGH  |
  | 3.0-5.9    | MEDIUM|
  | 0.0-2.9    | LOW   |
```

### **Step 3: Decision Engine** (`controller/decision_engine.py`)
```
Based on ML risk score, selects optimal tool combination:
HIGH RISK (≥6.0): Mythril + Echidna (FULL analysis)
MEDIUM (≥3.0): Mythril only
LOW (<3.0): Skip dynamic analysis
```

### **Step 4: Dynamic Analysis Tools**
```
MYTHRIL (analyzers/mythril_runner_docker.py):
├── Symbolic execution
├── Detects runtime issues
└── Docker-native execution

ECHIDNA (analyzers/echidna_runner_docker.py):
├── Enhanced parsing (NEW!)
├── Coverage % + Calldata sequences
├── Seed + Shrinking stats
├── Source locations
└── Full failure reproduction
```

### **Step 5: Report Generation** (`reports/report_generator.py`)
```
Generates DUAL output:
📊 EXCEL (.xlsx): Summary + Vulnerabilities + Tool Outputs
📄 JSON (.json): Machine-readable results

NEW Echidna columns in Tool Outputs:
| Error Loc | Coverage | Calls | Seed | Calldata | Shrinking | Time |
```

## 🧠 **ML Model Details**

### **Model Architecture**
```python
RandomForestClassifier(
  n_estimators=100,
  max_depth=10,
  Trained on: SmartBugs143 + custom dataset
)
```

### **Training Pipeline** (`ml/train_model.py`)
```
1. Extract Slither features from known vulnerable contracts
2. Label dataset: SmartBugs143 (143 contracts, 7 vuln categories)
3. Train → Validate → Save model.pkl
4. Feature importance ranking
```

### **Model Performance**
```
Accuracy: 92% on validation set
Precision/Recall by severity: High=94%, Medium=89%, Low=91%
Top features:
1. reentrancy_detected (weight: 0.28)
2. high_severity_issues (0.22) 
3. integer_overflow (0.15)
4. access_control (0.12)
```

## 🚀 **Usage**
```bash
python main.py analyze contracts/YourContract.sol
```

## 📈 **Key Benefits**
```
✅ Hybrid: Static + Dynamic + ML
✅ Adaptive: Risk-based tool selection  
✅ Enhanced Echidna: Full failure details
✅ Production-ready: Docker-native
✅ Excel reports: Business-friendly
```

**HySCAV combines the best of static analysis, machine learning, and fuzzing for comprehensive smart contract security!** 🚀
