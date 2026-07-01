### Task 1: Clean Up Repo & Git Init

**Files:**
- Remove: `server.py`, `client.py`, `relay_server.py`, `relay_common.py`, `game.cs`, `import requests.py`, `test.py`
- Create: `.gitignore`
- Modify: none

**Interfaces:** None (infrastructure only)

- [ ] **Step 1: Delete remote desktop files**

```bash
rm /c/wangyu_PyP/server.py
rm /c/wangyu_PyP/client.py
rm /c/wangyu_PyP/relay_server.py
rm /c/wangyu_PyP/relay_common.py
rm /c/wangyu_PyP/game.cs
rm /c/wangyu_PyP/import\ requests.py
rm /c/wangyu_PyP/test.py
```

- [ ] **Step 2: Create `.gitignore`**

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
env/

# Build
build/
dist/
*.spec

# Config (contains real tokens)
deepseek_config.txt

# Logs
*.log

# IDE
.idea/
.vscode/settings.json

# VS Code extension
vscode-ext/node_modules/
vscode-ext/out/
vscode-ext/*.vsix
```

- [ ] **Step 3: Initialize git**

```bash
cd /c/wangyu_PyP
git init
git add -A
git commit -m "Initial commit: DeepSeek API usage monitor

- deepseek_float.py: PyQt5 desktop floating ball app
- deepseek.py: CLI usage monitor
- vscode-ext/: VS Code extension (scaffold)"
```

Expected: `git log --oneline` shows one commit.

---

