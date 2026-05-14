# Fix ghcr.io Login for Mythril/Echidna

**Error**: "denied: denied" - PAT invalid/missing scopes.

**Step-by-step**:

1. **Create PAT**:
   - github.com/settings/tokens → **Generate new token (classic)**
   - Scopes: `read:packages`
   - Copy token (ghp_... )

2. **Login**:
   ```
   docker logout ghcr.io
   docker login ghcr.io -u USERNAME
   ```
   - Username: your GitHub username (Aditya2747)
   - Password: PAT (no echo)

3. **Test**:
   ```
   docker pull ghcr.io/crytic/mythril:latest
   docker pull ghcr.io/crytic/echidna:latest
   ```

4. **Run**:
   `python main.py analyze contracts/Vault.sol`

**Alternative** (no PAT):
- Use `mythril_no_docker.py` (slither proxy)
- Or public Docker Hub mythril (if available).

Complete login → Mythril runs fully!
