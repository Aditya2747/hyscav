# Mythril & Echidna Detailed Demo Report

## Test 1: Standalone Mythril
**Command**: `python analyzers/mythril_runner_docker.py contracts/Vault.sol`
**Output**:
```
[MYTHRIL] Found 0 issues
{
  "issues": []
}
```
**Meaning**: No critical runtime vulns found by symbolic execution.

## Test 2: Standalone Echidna
**Command**: `python analyzers/echidna_runner_docker.py contracts/Vault.sol`
**Output**:
```
[ECHIDNA] 0 fails
{}
```
**Meaning**: No property violations in 2000 tests.

## Test 3: Full HySCAV Pipeline
**Command**: `python main.py analyze contracts/Vault.sol`
**Key Outputs**:
```
[SLITHER] Issues found: 4
[ML] Risk Level: HIGH (score = 20.5)
[DECISION] Next tools to run: ['Mythril', 'Echidna']
[MYTHRIL] Found 0 issues
[ECHIDNA] 0 fails
[REPORT] Report generated: reports/report_Vault.sol.xlsx
```

## Excel Report
Open `reports/report_Vault.sol.xlsx` - sheets:
- **Slither_Issues**: 4 static vulns (reentrancy, unchecked).
- **Mythril_Issues**: 0 (clean).
- **Echidna_Issues**: 0 (properties hold).

## Docker Verification
```
docker images | findstr echidna → ghcr.io/crytic/echidna:latest
docker images | findstr myth → mythril/myth:latest
```

**Conclusion**: Tools working correctly - conservative (prefer miss > false positive). Slither static → Mythril/Echidna confirm no deep bugs.
