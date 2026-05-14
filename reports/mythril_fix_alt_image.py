import os
import subprocess
contract = 'contracts/Vault.sol'
print(f"Testing alt Mythril image for {contract}")

# Try alternative public image
command = [
    "docker", "run", "--rm",
    "-v", f"{os.getcwd()}:/tmp",
    "trailofbits/mythril",  # Alt public
    "analyze", "/tmp/Vault.sol", 
    "-o", "json"
]

result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=300)
print("Alt Mythril output:")
print(result.stdout if result.stdout else result.stderr)
print("Return code:", result.returncode)

