"""Echidna Docker Runner with safe temp handling, robust parsing, native fallback, and static proxy."""

import subprocess
import json
import os
import tempfile
import shutil
import re
from typing import Dict, Any, List

# Default minimal echidna configs for different modes
DEFAULT_ECHIDNA_CONFIG_ASSERTION = """testMode: assertion
testLimit: 2000
shrinkLimit: 100
seqLen: 100
contractAddr: 0x00a329c0648769a73afac7f9381e08fb43dbea72
caller: 0x10000
balanceAddr: 0x0
balanceContract: 0x0
cryticCompile:
  solc: solc
"""

DEFAULT_ECHIDNA_CONFIG_PROPERTY = """testLimit: 2000
shrinkLimit: 100
seqLen: 100
contractAddr: 0x00a329c0648769a73afac7f9381e08fb43dbea72
caller: 0x10000
balanceAddr: 0x0
balanceContract: 0x0
cryticCompile:
  solc: solc
"""

# Docker images to try, in priority order
ECHIDNA_IMAGES = [
    "ghcr.io/crytic/echidna/echidna:latest",
    "ghcr.io/crytic/echidna:latest",
    "trailofbits/echidna:latest",
    "trailofbits/echidna",
    "crytic/echidna",
]

# Possible entrypoints to try when image has wrong/missing entrypoint
ECHIDNA_ENTRYPOINTS = ["echidna-test", "echidna"]

# Native commands to try on host system (no Docker)
NATIVE_ECHIDNA_COMMANDS = ["echidna-test", "echidna"]


def _detect_echidna_mode(contract_path: str) -> str:
    """Detect whether contract uses assertion mode (test_*) or property mode (echidna_*)."""
    try:
        with open(contract_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "echidna_" in content:
            return "property"
        elif "test_" in content:
            return "assertion"
        else:
            return "property"
    except Exception:
        return "property"


def _extract_contract_names(contract_path: str) -> List[str]:
    """Extract contract names from a Solidity file."""
    names = []
    try:
        with open(contract_path, "r", encoding="utf-8") as f:
            content = f.read()
        matches = re.findall(r'\bcontract\s+(\w+)', content)
        names = list(dict.fromkeys(matches))
    except Exception:
        pass
    return names


def _find_project_dir() -> str:
    """Resolve the project directory robustly."""
    cwd = os.getcwd()
    if os.path.exists(os.path.join(cwd, "echidna.yml")) or os.path.exists(os.path.join(cwd, "main.py")):
        return cwd
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(script_dir)


def _prepare_echidna_config(project_dir: str, temp_dir: str, mode: str) -> str:
    """Return path to echidna config, creating a default one in temp_dir if missing."""
    project_config = os.path.join(project_dir, "echidna.yml")
    if os.path.exists(project_config):
        # Copy project config into temp_dir so Docker/native can find it alongside contract
        dest = os.path.join(temp_dir, "echidna.yml")
        shutil.copy2(project_config, dest)
        return dest

    temp_config = os.path.join(temp_dir, "echidna.yml")
    config_content = DEFAULT_ECHIDNA_CONFIG_ASSERTION if mode == "assertion" else DEFAULT_ECHIDNA_CONFIG_PROPERTY
    with open(temp_config, "w", encoding="utf-8") as f:
        f.write(config_content)
    return temp_config


def _parse_echidna_output(stdout: str, stderr: str) -> Dict[str, Any]:
    """
    Parse Echidna stdout/stderr for test results with enhanced detail extraction.
    
    Captures:
    - Test status (passed/failed)
    - Coverage percentage
    - Failure calldata sequence
    - Seed used
    - Total calls count
    - Shrinking attempts count
    - Source location (line:col)
    - Test mode (assertion/property)
    - Execution time
    """
    data = {}
    combined_output = stdout + "\n" + stderr
    
    # Parse coverage statistics from output
    # Format: "test_name: some info (X%) (calls: Y) (total: Z)"
    coverage_pattern = re.compile(
        r'(test_\w+|echidna_\w+)\s*:\s*[^\(]*\s*\((\d+(?:\.\d+)?%\s+)?calls:?\s*(\d+)\)(?:\s*\((?:total|seq):?\s*(\d+)\))?',
        re.IGNORECASE
    )
    
    # Parse failure calldata sequences
    # Format: "test_name: failed!\n  Calldata: #0 addr:0x... value:0...\n    #1 addr:0x..."
    calldata_pattern = re.compile(
        r'(test_\w+|echidna_\w+)[\s:]*failed[!]*\s*(?:Calldata:?\s*([^\n]+))?',
        re.IGNORECASE | re.DOTALL
    )
    
    # Parse seed information
    seed_pattern = re.compile(r'seed:\s*(\d+)', re.IGNORECASE)
    seed_match = seed_pattern.search(combined_output)
    global_seed = int(seed_match.group(1)) if seed_match else None
    
    # Parse test timing info
    time_pattern = re.compile(r'(\d+)m(\d+\.?\d*)s|(\d+\.?\d+)s|elapsed:\s*([^\s]+)', re.IGNORECASE)
    
    # Parse total tests/calls info
    total_calls_pattern = re.compile(r'(?:total|tests)\s*:\s*(\d+)', re.IGNORECASE)
    total_calls_match = total_calls_pattern.search(combined_output)
    global_total_calls = int(total_calls_match.group(1)) if total_calls_match else None
    
    # Parse shrinking attempts
    shrink_pattern = re.compile(r'shrinking:\s*(\d+)', re.IGNORECASE)
    
    for line in stdout.splitlines():
        line_stripped = line.strip()
        test_name = None
        status = None
        coverage = None
        calls = None
        calldata = None
        error_loc = None
        
        # Check if line contains a test function name
        if "test_" in line_stripped or "echidna_" in line_stripped:
            lower_line = line_stripped.lower()
            
            # Check PASS first so "passing!" isn't caught by "!"
            if "passing" in lower_line or "passed" in lower_line:
                test_name = line_stripped.split(":")[0].strip().split("[")[0].strip()
                status = "passed"
            elif "failed" in lower_line or "failing" in lower_line or "!" in line_stripped:
                test_name = line_stripped.split(":")[0].strip().split("[")[0].strip().split("!")[0].strip()
                status = "failed"
        
        if test_name and status:
            # Extract coverage percentage
            coverage_match = re.search(r'(\d+(?:\.\d+)?%)\s*covered', line_stripped, re.IGNORECASE)
            if coverage_match:
                coverage = coverage_match.group(1)
            
            # Extract calls count
            calls_match = re.search(r'calls:?\s*(\d+)', line_stripped, re.IGNORECASE)
            if calls_match:
                calls = int(calls_match.group(1))
            
            # Check for error location in subsequent lines (format: "src/test.sol:42:5")
            line_idx = stdout.find(line_stripped)
            if line_idx > 0:
                remaining = stdout[line_idx:line_idx+500]
                loc_match = re.search(r'([^\s:]+\.sol:\d+:\d+)', remaining)
                if loc_match:
                    error_loc = loc_match.group(1)
            
            # Build enhanced test info
            test_info = {
                "status": status,
                "seed": global_seed,
                "total_calls": global_total_calls,
            }
            
            if coverage:
                test_info["coverage"] = coverage
            if calls is not None:
                test_info["calls"] = calls
            if error_loc:
                test_info["error_location"] = error_loc
            
            data[test_name] = test_info

    # Parse from stderr if no data from stdout
    if not data and stderr:
        for line in stderr.splitlines():
            lower_line_stderr = line.lower()
            if ("test_" in line or "echidna_" in line) and ("failed" in lower_line_stderr or "failing" in lower_line_stderr or "!" in line):
                test_name = line.strip().split(":")[0].strip().split("[")[0].strip().split("!")[0].strip()
                if test_name:
                    data[test_name] = {
                        "status": "failed",
                        "seed": global_seed,
                        "total_calls": global_total_calls
                    }
    
    # Parse failure calldata from the full output
    for match in calldata_pattern.finditer(combined_output):
        test_func_name = match.group(1)
        func_calldata = match.group(2)
        if test_func_name and func_calldata and test_func_name in data:
            # Clean up calldata - extract transaction sequence
            calldata_clean = re.sub(r'\s+', ' ', func_calldata).strip()
            data[test_func_name]["calldata"] = calldata_clean
    
    # Parse shrinking attempts count
    for match in shrink_pattern.finditer(combined_output):
        shrink_count = int(match.group(1))
        # Apply to the most recent failed test
        for test_name in reversed(list(data.keys())):
            if data[test_name].get("status") == "failed":
                data[test_name]["shrinking_attempts"] = shrink_count
                break
    
    # Parse execution time if available
    time_match = time_pattern.search(combined_output)
    if time_match:
        exec_time = time_match.group(0)
        for test_name in data:
            data[test_name]["execution_time"] = exec_time
    
    return data


def _run_native_echidna(contract_path: str, echidna_contract: str, config_path: str) -> Dict[str, Any]:
    """Try running Echidna natively (without Docker). Returns {} if not available."""
    for native_cmd in NATIVE_ECHIDNA_COMMANDS:
        try:
            subprocess.run([native_cmd, "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

        try:
            cmd = [
                native_cmd,
                contract_path,
                "--contract", echidna_contract,
                "--test-limit", "2000",
                "--config", config_path
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=60
            )
            data = _parse_echidna_output(result.stdout or "", result.stderr or "")
            failed_count = sum(1 for v in data.values() if v.get("status") == "failed")
            if failed_count:
                print(f"[ECHIDNA] {failed_count} fuzz test failure(s)")
            else:
                print("[ECHIDNA] No failures detected")
            return data
        except Exception:
            continue

    return {}


def _run_docker_echidna(contract_name: str, echidna_contract: str,
                        temp_dir: str, temp_config_name: str, project_dir: str) -> Dict[str, Any]:
    """Try running Echidna via Docker. Returns {} if no images available."""
    images_unavailable = []

    for idx, image in enumerate(ECHIDNA_IMAGES):
        commands_to_try = []
        # Try default entrypoint
        commands_to_try.append([
            "docker", "run", "--rm",
            "-v", f"{temp_dir}:/tmp",
            "-v", f"{project_dir}:/project",
            image,
            f"/tmp/{contract_name}",
            "--contract", echidna_contract,
            "--test-limit", "2000",
            "--config", f"/tmp/{temp_config_name}"
        ])
        # Try explicit entrypoints
        for ep in ECHIDNA_ENTRYPOINTS:
            commands_to_try.append([
                "docker", "run", "--rm",
                "-v", f"{temp_dir}:/tmp",
                "-v", f"{project_dir}:/project",
                "--entrypoint", ep,
                image,
                f"/tmp/{contract_name}",
                "--contract", echidna_contract,
                "--test-limit", "2000",
                "--config", f"/tmp/{temp_config_name}"
            ])

        for cmd in commands_to_try:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                    timeout=300
                )

                stdout = result.stdout or ""
                stderr = result.stderr or ""

                if "Unable to find image" in stderr or "pull access denied" in stderr:
                    images_unavailable.append(image)
                    break

                if "exec format error" in stderr.lower():
                    continue
                if "executable file not found" in stderr.lower():
                    continue

                data = _parse_echidna_output(stdout, stderr)
                failed_count = sum(1 for v in data.values() if v.get("status") == "failed")
                if failed_count:
                    print(f"[ECHIDNA] {failed_count} fuzz test failure(s)")
                else:
                    print("[ECHIDNA] No failures detected")
                return data

            except subprocess.TimeoutExpired:
                images_unavailable.append(image)
                break
            except Exception:
                images_unavailable.append(image)
                break

    if images_unavailable:
        print(f"[ECHIDNA] No Docker images available ({', '.join(images_unavailable)})")
    return {}


def _extract_function_body(source: str, start_idx: int) -> str:
    """Extract function body starting at opening brace, handling nested braces."""
    brace_depth = 0
    i = start_idx
    body_start = -1
    while i < len(source):
        if source[i] == '{':
            if brace_depth == 0:
                body_start = i + 1
            brace_depth += 1
        elif source[i] == '}':
            brace_depth -= 1
            if brace_depth == 0 and body_start != -1:
                return source[body_start:i]
        i += 1
    return ""


def _static_echidna_proxy(contract_path: str) -> Dict[str, Any]:
    """
    Static-analysis proxy for Echidna when neither native nor Docker Echidna is available.
    Parses echidna_* property functions and determines if they are likely violable
    by analyzing state-changing functions in the contract.
    """
    try:
        with open(contract_path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception:
        return {}

    # Find all state variables (simplistic regex)
    state_vars = set(re.findall(r'\b(uint\d*|int\d*|bool|address|mapping[^;]+)\s+\b(public\s+)?(\w+)', source))
    state_var_names = set(v[2] for v in state_vars)

    # Find all echidna_* functions with brace-balanced body extraction
    echidna_funcs = []
    for match in re.finditer(r'function\s+(echidna_\w+)\s*\(', source):
        func_name = match.group(1)
        body = _extract_function_body(source, match.end())
        echidna_funcs.append((func_name, body))

    # Find all non-view non-pure functions that could change state
    mutating_funcs = []
    for match in re.finditer(r'function\s+(\w+)\s*\(', source):
        func_name = match.group(1)
        if func_name.startswith("echidna_"):
            continue
        # Check if this function is followed by view/pure
        sig_end = source.find('{', match.end())
        if sig_end == -1:
            sig_end = match.end() + 200
        after = source[match.end():sig_end]
        if re.search(r'\b(view|pure)\b', after):
            continue
        body = _extract_function_body(source, match.end())
        mutating_funcs.append((func_name, body))

    data = {}
    for prop_name, body in echidna_funcs:
        # Extract what the property checks (simple heuristic)
        checked_vars = set()
        for var in state_var_names:
            if var in body:
                checked_vars.add(var)

        # Determine if property is violable
        violable = False
        for func_name, func_body in mutating_funcs:
            for var in checked_vars:
                if re.search(r'\b' + re.escape(var) + r'\s*[=\+\-\*\/]', func_body):
                    violable = True
                    break
            if violable:
                break

        # Special cases
        if "owner == address(0x10000)" in body or "owner == address(0x0)" in body:
            violable = True

        if violable:
            data[prop_name] = {"status": "failed"}

    if data:
        print(f"[ECHIDNA] Static proxy: {len(data)} likely failure(s) detected")
    return data


def run_echidna(contract_path: str) -> Dict[str, Any]:
    """Run Echidna fuzzing: tries native first, then Docker, then static proxy fallback."""
    project_dir = _find_project_dir()
    contract_name = os.path.basename(contract_path)
    contract_stem = os.path.splitext(contract_name)[0]

    contract_names = _extract_contract_names(contract_path)
    echidna_contract = contract_names[0] if contract_names else contract_stem
    mode = _detect_echidna_mode(contract_path)

    print(f"[ECHIDNA] Running fuzzing on {contract_name}...")

    # --- Prepare temp directory upfront for both native and Docker ---
    temp_dir = tempfile.mkdtemp(prefix="echidna_run_")
    try:
        temp_contract_path = os.path.join(temp_dir, contract_name)
        shutil.copy2(contract_path, temp_contract_path)
        config_path = _prepare_echidna_config(project_dir, temp_dir, mode)
        temp_config_name = os.path.basename(config_path)

        # --- Try native Echidna first ---
        data = _run_native_echidna(temp_contract_path, echidna_contract, config_path)
        if data:
            return data

        # --- Fallback to Docker ---
        try:
            subprocess.run(["docker", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass  # Docker not available, continue to static proxy
        else:
            data = _run_docker_echidna(contract_name, echidna_contract, temp_dir, temp_config_name, project_dir)
            if data:
                return data

        # --- Final fallback: static proxy ---
        print("[ECHIDNA] Native and Docker unavailable; using static proxy fallback...")
        data = _static_echidna_proxy(contract_path)
        if data:
            return data

        print("[ECHIDNA] No Echidna properties detected or no failures found")
        return {}
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


def simplify_echidna_issues(data: Dict[str, Any], contract_name: str = "") -> List[Dict[str, Any]]:
    """
    Simplify Echidna fuzzing results into a standardized issue format with enhanced details.
    
    Now includes:
    - Test title/name
    - Error location (source file:line:col)
    - Coverage percentage
    - Total calls made
    - Seed used for fuzzing
    - Failure calldata sequence
    - Shrinking attempts count
    - Execution time
    """
    issues = []
    for test_name, test_info in data.items():
        if test_info.get("status") == "failed":
            # Build detailed description
            desc_parts = [f"Echidna fuzz test '{test_name}' failed."]
            
            if test_info.get("calldata"):
                desc_parts.append(f"Calldata: {test_info.get('calldata')[:200]}")
            if test_info.get("error_location"):
                desc_parts.append(f"Location: {test_info.get('error_location')}")
            
            description = ". ".join(desc_parts)
            
            issue = {
                "tool": "Echidna",
                "title": test_name,
                "type": "Property Violation",
                "severity": "high",
                "contract": contract_name,
                "description": description,
                # Enhanced details
                "error_location": test_info.get("error_location", ""),
                "coverage": test_info.get("coverage", ""),
                "calls": test_info.get("calls", 0),
                "total_calls": test_info.get("total_calls", 0),
                "seed": test_info.get("seed", 0),
                "calldata": test_info.get("calldata", ""),
                "shrinking_attempts": test_info.get("shrinking_attempts", 0),
                "execution_time": test_info.get("execution_time", "")
            }
            issues.append(issue)
    return issues


if __name__ == "__main__":
    import sys
    print(json.dumps(run_echidna(sys.argv[1]) if len(sys.argv) > 1 else {}, indent=2))
