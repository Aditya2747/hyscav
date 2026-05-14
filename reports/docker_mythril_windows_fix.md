# Docker Mythril & Echidna Fix for Windows

**Issue**: `ghcr.io/crytic/mythril:latest` does not exist locally, and single-image fallback fails silently.

**Fix Applied** (see `analyzers/mythril_runner_docker.py` and `analyzers/echidna_runner_docker.py`):

## 1. Mythril Multi-Image Fallback

The runner now tries the following Docker images in order:

1. `mythril/myth:latest` (public, usually available)
2. `trailofbits/mythril` (alternative public image)
3. `ghcr.io/crytic/mythril:latest` (GitHub Container Registry)
4. `crytic/ether-slim:latest` (installs mythril on-the-fly via pip)

If all Docker images fail, it falls back to a **comprehensive Slither proxy** that maps Slither detectors to Mythril-style issues (reentrancy, overflow, tx-origin, delegatecall, access control, unchecked calls, timestamp dependence, weak randomness, uninitialized storage, denial of service, and front-running).

### Usage
```bash
python analyzers/mythril_runner_docker.py contracts/Vault.sol
```

### Manual test (any single image)
```bash
docker run --rm -v %cd%:/code mythril/myth:latest analyze /code/contracts/Vault.sol -o json --execution-timeout 60
```

## 2. Echidna Multi-Image Fallback

The runner now tries the following images in order:

1. `ghcr.io/crytic/echidna:latest`
2. `ghcr.io/crytic/echidna:2.2.3`
3. `ghcr.io/crytic/echidna:2.2.2`
4. `trailofbits/echidna`

If no image is available, it returns empty results gracefully without crashing the pipeline.

### Usage
```bash
python analyzers/echidna_runner_docker.py contracts/Vault.sol
```

## 3. WSL2 (recommended for full image availability)
- Enable WSL2, install Ubuntu.
- `wsl docker pull ghcr.io/crytic/mythril:latest`
- `wsl docker pull ghcr.io/crytic/echidna:latest`
- Run from WSL.

## 4. Native (no Docker)
- Use `mythril_no_docker.py` (Slither proxy only).
- Or install Mythril natively: `pip install mythril`

## 5. Colab/Cloud
- Use Google Colab with `!docker` commands.

## Full Pipeline Test
```bash
python main.py analyze contracts/Vault.sol
```

**Expected behavior**:
- Slither runs and extracts features.
- ML model predicts risk level.
- Mythril Docker runs with multi-image fallback.
- Echidna Docker runs with multi-image fallback.
- Report is generated.

If Docker images are missing, the comprehensive Slither proxy ensures Mythril still produces useful results, and Echidna skips gracefully.

