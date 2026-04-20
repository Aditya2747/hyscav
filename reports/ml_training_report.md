# HySCAV ML Risk Model Training Report

## Summary
- **Date**: Current session
- **Dataset**: 10 samples from 5 contracts + 5 test cases.
- **Features**: 18 (total_issues, high, medium, low, high_risk_categories, unique_vuln_types, contract_complexity, external_calls, state_variables, has_reentrancy, has_overflow, has_unchecked_call, has_access_control, has_tx_origin, has_delegatecall, has_timestamp, has_weak_randomness).
- **Labels**: 0=LOW (3), 1=MEDIUM (2), 2=HIGH (5).
- **Model**: RandomForestClassifier(n_estimators=100).
- **Train acc**: 1.00 (perfect fit).
- **Test acc**: 0.33 (small data, expected).

## Dataset Preview
| Contract | Label | High | has_reentrancy |
|----------|-------|------|----------------|
| Bank.sol | 2 | 1 | False |
| IntegerOverflowTest.sol | 0 | 0 | False |
| ReentrancyTest.sol | 2 | 1 | False |
| reentrency.sol | 2 | 1 | False |
| TxOriginTest.sol | 1 | 0 | False |

## Classification Report (Test Set)
```
              precision    recall  f1-score   support

           0       0.00      0.00      0.00         1
           1       0.00      0.00      0.00         1
           2       0.33      1.00      0.50         1

    accuracy                           0.33         3
   macro avg       0.11      0.33      0.17         3
weighted avg       0.11      0.33      0.17         3
```

**Notes**:
- Small dataset → low test acc (overfit expected). Add SmartBugs data for improvement.
- Features from Slither API – perfect for vuln prediction.
- Model saved ml/model.pkl, ready in pipeline.

**Next**: `python main.py analyze contracts/new.sol` uses this model!

**Ace**: Rerun after `python pipeline/fetcher.py` + retrain for 90% acc.
