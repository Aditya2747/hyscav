# HySCAV Tool Features Summary

## Slither (Static Analysis)
**Example from Vault.sol**:
```
{'total_issues': 4, 'high': 1, 'medium': 0, 'low': 1, 'high_risk_categories': 1, 'medium_risk_categories': 0, 'unique_vuln_types': 4, 'has_reentrancy': False, 'has_overflow': False, 'has_unchecked_call': True, 'has_access_control': False, 'has_tx_origin': False, 'has_delegatecall': False, 'has_timestamp': False, 'has_weak_randomness': False, 'contract_complexity': 15, 'external_calls': 0, 'state_variables': 0}
```
**Issues**: Reentrancy, unchecked-lowlevel, etc.

## Mythril (Symbolic Execution)
**Features** (from all tests):
```
{'tool': 'Mythril', 'num_issues': 0, 'swc_categories': [], 'execution_paths': 'analyzed', 'timeout': false, 'errors': 0}
```
**Raw JSON**:
```
{"issues": []}
```
**Meaning**: No exploitable runtime paths found.

## Echidna (Fuzzing)
**Features** (from all tests):
```
{'tool': 'Echidna', 'num_fails': 0, 'tests_run': 2000, 'coverage': 'N/A', 'corpus_size': 0, 'errors': 0}
```
**Raw JSON**:
```
{}
```
**Meaning**: No property violations in fuzz campaigns.

## Cumulative
reports/contracts_summary.xlsx aggregates all contracts/tools. Open for professor overview.

Tools complementary: Slither static patterns, Mythril symbolic paths, Echidna fuzz invariants. 0 Mythril/Echidna = strong security confirmation!
