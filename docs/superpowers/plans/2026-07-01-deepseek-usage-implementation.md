# DeepSeek Usage — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Open-source the DeepSeek API usage monitor on GitHub + publish a VS Code extension to the marketplace.

**Architecture:** Single repo with Python tools at root and VS Code extension under `vscode-ext/`. The extension uses StatusBarItem for the floating ball info and WebviewPanel for the detail panel — porting the same DeepSeek API calls from `deepseek_float.py` into TypeScript.

**Tech Stack:** Python 3, PyQt5 (desktop), TypeScript, VS Code Extension API, Node.js `https`

## Global Constraints

- MIT License
- All UI labels in Chinese (matching original app)
- VS Code extension targets VS Code ^1.85.0
- No extra npm dependencies beyond `@types/vscode` and `vsce`
- Python files stay at repo root (not in subdirectory)
- Remote desktop files (server.py, client.py, relay_*.py, etc.) removed from this repo

---

## File Structure

```
deepseek-usage/
├── README.md                        # Python project README (Chinese)
├── LICENSE                          # MIT
├── .gitignore                       # Python + Node + VS Code
├── deepseek_float.py                # PyQt5 desktop app (existing)
├── deepseek.py                      # CLI monitor (existing)
├── deepseek_float.spec              # PyInstaller spec (existing)
├── DeepSeek悬浮球.spec               # PyInstaller spec (existing)
├── DeepSeek助手.spec                  # PyInstaller spec (existing)
├── icon.ico                         # App icon (existing)
├── deepseek_config.txt              # Config file (FOR REFERENCE ONLY, not committed)
└── vscode-ext/
    ├── package.json                 # Extension manifest
    ├── tsconfig.json                # TypeScript config
    ├── .vscodeignore                # Packing ignore
    ├── CHANGELOG.md                 # Release notes
    ├── README.md                    # Extension README (Chinese)
    └── src/
        ├── extension.ts             # Entry point: activate, status bar, timer, commands
        ├── api.ts                   # DeepSeek HTTP client
        └── webview/
            ├── panel.ts             # WebviewPanel manager
            └── index.html           # Panel UI (HTML + CSS + vanilla JS)
```

---

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

### Task 2: README & License

**Files:**
- Create: `README.md`, `LICENSE`
- Modify: none

**Interfaces:** None (documentation)

- [ ] **Step 1: Create README.md**

```markdown
# DeepSeek API 用量监控

![VS Code](https://img.shields.io/badge/VS_Code-Extension-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)

DeepSeek API 用量实时监控工具，支持桌面端和 VS Code 内使用。

## ✨ 功能

| 功能 | 桌面版 (PyQt5) | VS Code 扩展 |
|------|:---:|:---:|
| 余额实时显示 | ✅ | ✅ |
| 缓存命中率 | ✅ | ✅ |
| 近7天用量趋势 | ✅ | ✅ |
| 按模型查看详情 | ✅ | ✅ |
| 悬浮球桌面显示 | ✅ | ❌ |
| 状态栏显示 | ❌ | ✅ |

## 🚀 快速开始

### 桌面版

```bash
pip install PyQt5 requests
python deepseek_float.py
```

启动后会提示输入 DeepSeek Bearer Token（从浏览器 F12 抓包获取）。

### VS Code 扩展

在 VS Code 扩展市场搜索 "DeepSeek Usage" 安装，或：

```bash
cd vscode-ext
npm install
npm run package
code --install-extension deepseek-usage-*.vsix
```

## 🔧 配置

| 参数 | 说明 | 获取方式 |
|------|------|---------|
| Bearer Token | 访问 platform.deepseek.com 的认证令牌 | F12 → Network → authorization 头 |
| API Key | DeepSeek API 密钥 (sk-xxx) | platform.deepseek.com/api_keys |
| cf_clearance | Cloudflare 验证 Cookie | F12 → Application → Cookies |

## 📦 打包桌面版

```bash
pip install pyinstaller
pyinstaller deepseek_float.spec
```

## 📄 许可证

MIT
```

- [ ] **Step 2: Create LICENSE (MIT)**

```
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 3: Commit**

```bash
cd /c/wangyu_PyP
git add README.md LICENSE
git commit -m "docs: add README and MIT license"
```

---

### Task 3: VS Code Extension Scaffold

**Files:**
- Create: `vscode-ext/package.json`, `vscode-ext/tsconfig.json`, `vscode-ext/.vscodeignore`, `vscode-ext/README.md`, `vscode-ext/CHANGELOG.md`

**Interfaces:** None (scaffold)

- [ ] **Step 1: Create `vscode-ext/package.json`**

```json
{
  "name": "deepseek-usage",
  "displayName": "DeepSeek Usage",
  "description": "DeepSeek API 用量实时监控 — 余额、缓存命中率、7天用量趋势",
  "version": "0.1.0",
  "publisher": "your-publisher-id",
  "license": "MIT",
  "engines": {
    "vscode": "^1.85.0"
  },
  "categories": [
    "Other"
  ],
  "keywords": ["deepseek", "api", "usage", "monitor"],
  "activationEvents": [
    "onStartupFinished"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "deepseekUsage.showPanel",
        "title": "DeepSeek: 显示用量面板"
      },
      {
        "command": "deepseekUsage.refresh",
        "title": "DeepSeek: 刷新数据"
      },
      {
        "command": "deepseekUsage.configure",
        "title": "DeepSeek: 配置 API Token"
      }
    ],
    "configuration": {
      "title": "DeepSeek Usage",
      "properties": {
        "deepseekUsage.bearerToken": {
          "type": "string",
          "default": "",
          "description": "DeepSeek platform Bearer Token"
        },
        "deepseekUsage.apiKey": {
          "type": "string",
          "default": "",
          "description": "DeepSeek API Key (sk-xxx)"
        },
        "deepseekUsage.cfClearance": {
          "type": "string",
          "default": "",
          "description": "Cloudflare cf_clearance cookie"
        },
        "deepseekUsage.refreshInterval": {
          "type": "number",
          "default": 300000,
          "description": "自动刷新间隔（毫秒）"
        }
      }
    }
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./",
    "package": "vsce package"
  },
  "devDependencies": {
    "@types/vscode": "^1.85.0",
    "typescript": "^5.3.0",
    "@vscode/vsce": "^2.22.0"
  }
}
```

- [ ] **Step 2: Create `vscode-ext/tsconfig.json`**

```json
{
  "compilerOptions": {
    "module": "commonjs",
    "target": "ES2020",
    "outDir": "out",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "out"]
}
```

- [ ] **Step 3: Create `vscode-ext/.vscodeignore`**

```
.vscode/**
node_modules/**
src/**
tsconfig.json
!out/**
```

- [ ] **Step 4: Create `vscode-ext/README.md`**

```markdown
# DeepSeek Usage — VS Code 扩展

VS Code 中实时监控 DeepSeek API 用量余额与缓存效率。

## 功能

- **状态栏显示**：余额 + 缓存命中率，一目了然
- **用量详情面板**：近7天趋势、按模型切换查看
- **自动刷新**：默认每5分钟自动更新
- **手动刷新**：点击面板中的刷新按钮或运行命令

## 使用

1. 安装扩展后，状态栏显示 `💰 -- 📊 --%`
2. 点击状态栏打开用量详情面板
3. 首次使用需要配置 Bearer Token
4. 可选配置 API Key（显示余额）和 cf_clearance

## 配置

| 设置项 | 说明 |
|--------|------|
| `deepseekUsage.bearerToken` | DeepSeek platform 的 Bearer Token |
| `deepseekUsage.apiKey` | API Key (sk-xxx)，用于显示余额 |
| `deepseekUsage.cfClearance` | Cloudflare cf_clearance Cookie |
| `deepseekUsage.refreshInterval` | 刷新间隔（毫秒，默认300000） |

## 发布

```bash
npm install
npm run package
vsce publish
```
```

- [ ] **Step 5: Create `vscode-ext/CHANGELOG.md`**

```markdown
# Change Log

## 0.1.0

- 初始发布
- 状态栏显示余额和缓存命中率
- 用量详情面板（7天趋势、模型切换）
- 自动刷新配置
```

- [ ] **Step 6: Install dependencies**

```bash
cd /c/wangyu_PyP/vscode-ext
npm install
```

- [ ] **Step 7: Commit**

```bash
cd /c/wangyu_PyP
git add vscode-ext/
git commit -m "feat: add VS Code extension scaffold"
```

---

### Task 4: api.ts — DeepSeek HTTP Client

**Files:**
- Create: `vscode-ext/src/api.ts`

**Interfaces:**
- Produces:
  - `UsageDay` interface
  - `BalanceInfo` interface
  - `fetchUsageHistory(bearerToken: string, cfClearance: string): Promise<UsageDay[]>`
  - `getBalance(bearerToken: string, apiKey?: string): Promise<BalanceInfo | null>`

- [ ] **Step 1: Create `vscode-ext/src/api.ts`**

```typescript
import * as https from 'https';

export interface UsageDay {
  date: string;
  total_tokens: number;
  cache_hit_tokens: number;
  cache_miss_tokens: number;
  model_usage: Record<string, number>;
  model_detail: Record<string, {
    tokens: number;
    cache_hit: number;
    cache_miss: number;
    requests: number;
  }>;
}

export interface BalanceInfo {
  total: number;
  granted: number;
  topped_up: number;
}

interface UsageAmount {
  prompt_tokens: number;
  cache_hit_tokens: number;
  cache_miss_tokens: number;
  response_tokens: number;
  requests: number;
}

const DEEPSEEK_USAGE_URL = 'https://platform.deepseek.com/api/v0/usage/amount';
const DEEPSEEK_BALANCE_URL = 'https://platform.deepseek.com/api/v0/user/balance';
const BROWSER_HEADERS: Record<string, string> = {
  'accept': '*/*',
  'accept-language': 'zh-CN,zh;q=0.9',
  'cache-control': 'no-cache',
  'pragma': 'no-cache',
  'referer': 'https://platform.deepseek.com/usage',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  'x-client-bundle-id': 'com.deepseek.chat',
  'x-client-locale': 'zh_CN',
  'x-client-platform': 'web',
  'x-client-version': '1.0.0',
};

function httpGet(url: string, headers: Record<string, string>): Promise<string> {
  return new Promise((resolve, reject) => {
    https.get(url, { headers }, (res) => {
      let data = '';
      res.on('data', (chunk: string) => data += chunk);
      res.on('end', () => {
        if (res.statusCode !== 200) {
          reject(new Error(`HTTP ${res.statusCode}: ${data.slice(0, 200)}`));
        } else {
          resolve(data);
        }
      });
    }).on('error', reject);
  });
}

function extractAmounts(usageList: any[] | undefined): UsageAmount {
  const result: UsageAmount = {
    prompt_tokens: 0,
    cache_hit_tokens: 0,
    cache_miss_tokens: 0,
    response_tokens: 0,
    requests: 0,
  };
  const typeMap: Record<string, keyof UsageAmount> = {
    PROMPT_TOKEN: 'prompt_tokens',
    PROMPT_CACHE_HIT_TOKEN: 'cache_hit_tokens',
    PROMPT_CACHE_MISS_TOKEN: 'cache_miss_tokens',
    RESPONSE_TOKEN: 'response_tokens',
    REQUEST: 'requests',
  };
  for (const item of usageList || []) {
    const key = typeMap[item.type];
    if (key) {
      result[key] += parseInt(String(item.amount), 10) || 0;
    }
  }
  return result;
}

export async function fetchUsageHistory(
  bearerToken: string,
  cfClearance: string
): Promise<UsageDay[]> {
  const now = new Date();
  const endDate = now.toISOString().slice(0, 10);
  const start = new Date(now);
  start.setDate(start.getDate() - 6);
  const startDate = start.toISOString().slice(0, 10);

  const headers: Record<string, string> = {
    ...BROWSER_HEADERS,
    authorization: `Bearer ${bearerToken}`,
    cookie: `cf_clearance=${cfClearance}`,
  };

  const url = `${DEEPSEEK_USAGE_URL}?month=${now.getMonth() + 1}&year=${now.getFullYear()}`;
  const raw = await httpGet(url, headers);
  const data = JSON.parse(raw);

  if (data.code !== 0) {
    throw new Error(`API error: ${data.msg || 'unknown'}`);
  }

  const daysData: any[] = data?.data?.biz_data?.days || [];
  const normDict: Record<string, UsageDay> = {};

  for (const day of daysData) {
    const dateStr = String(day.date || '').slice(0, 10);
    if (dateStr < startDate || dateStr > endDate) continue;

    let dayTotal = 0, dayCacheHit = 0, dayCacheMiss = 0;
    const modelDetail: Record<string, UsageDay['model_detail'][string]> = {};

    for (const entry of day.data || []) {
      const modelName = entry.model || 'unknown';
      const amts = extractAmounts(entry.usage);
      const total = amts.prompt_tokens + amts.cache_hit_tokens + amts.cache_miss_tokens + amts.response_tokens;
      modelDetail[modelName] = {
        tokens: total,
        cache_hit: amts.cache_hit_tokens,
        cache_miss: amts.cache_miss_tokens,
        requests: amts.requests,
      };
      dayTotal += total;
      dayCacheHit += amts.cache_hit_tokens;
      dayCacheMiss += amts.cache_miss_tokens;
    }

    const modelUsage: Record<string, number> = {};
    for (const [m, d] of Object.entries(modelDetail)) {
      modelUsage[m] = d.tokens;
    }

    normDict[dateStr] = {
      date: dateStr,
      total_tokens: dayTotal,
      cache_hit_tokens: dayCacheHit,
      cache_miss_tokens: dayCacheMiss,
      model_usage: modelUsage,
      model_detail: modelDetail,
    };
  }

  // Fill missing days with zeros
  const result: UsageDay[] = [];
  const cursor = new Date(start);
  const end = new Date(endDate);
  while (cursor <= end) {
    const ds = cursor.toISOString().slice(0, 10);
    result.push(normDict[ds] || {
      date: ds, total_tokens: 0,
      cache_hit_tokens: 0, cache_miss_tokens: 0,
      model_usage: {}, model_detail: {},
    });
    cursor.setDate(cursor.getDate() + 1);
  }

  return result;
}

export async function getBalance(
  bearerToken: string,
  apiKey?: string
): Promise<BalanceInfo | null> {
  // Try API Key first (most reliable)
  if (apiKey) {
    try {
      const raw = await httpGet('https://api.deepseek.com/user/balance', {
        authorization: `Bearer ${apiKey}`,
        'content-type': 'application/json',
      });
      const data = JSON.parse(raw);
      if (data.is_available && data.balance_infos?.length) {
        const info = data.balance_infos[0];
        return {
          total: parseFloat(info.total_balance || '0'),
          granted: parseFloat(info.granted_balance || '0'),
          topped_up: parseFloat(info.topped_up_balance || '0'),
        };
      }
    } catch {
      // Fall through to platform API
    }
  }

  // Fallback: platform API with Bearer Token
  try {
    const url = 'https://platform.deepseek.com/api/v0/user/balance';
    const raw = await httpGet(url, {
      ...BROWSER_HEADERS,
      authorization: `Bearer ${bearerToken}`,
    });
    const data = JSON.parse(raw);
    if (data.is_available && data.balance_infos?.length) {
      const info = data.balance_infos[0];
      return {
        total: parseFloat(info.total_balance || '0'),
        granted: parseFloat(info.granted_balance || '0'),
        topped_up: parseFloat(info.topped_up_balance || '0'),
      };
    }
  } catch {
    // Give up
  }

  return null;
}
```

- [ ] **Step 2: Commit**

```bash
cd /c/wangyu_PyP
git add vscode-ext/src/api.ts
git commit -m "feat: add DeepSeek HTTP client"
```

---

### Task 5: webview/panel.ts — WebviewPanel Manager

**Files:**
- Create: `vscode-ext/src/webview/panel.ts`

**Interfaces:**
- Consumes: `UsageDay`, `BalanceInfo` from api.ts
- Produces: `UsagePanel` class with `show()`, `update(balance, history, modelTotals)`, `dispose()`
- Message protocol (extension → webview): `{ type: 'update', balance, usageHistory, modelTotals }`
- Message protocol (webview → extension): `{ type: 'refresh' }`, `{ type: 'configure' }`

- [ ] **Step 1: Create `vscode-ext/src/webview/panel.ts`**

```typescript
import * as vscode from 'vscode';
import { UsageDay, BalanceInfo } from '../api';
import * as path from 'path';

export class UsagePanel {
  private static instance: UsagePanel | undefined;
  private panel: vscode.WebviewPanel | undefined;
  private balance?: BalanceInfo | null;
  private usageHistory: UsageDay[] = [];
  private modelTotals: Record<string, number> = {};

  static show(): UsagePanel {
    if (!UsagePanel.instance) {
      UsagePanel.instance = new UsagePanel();
    }
    UsagePanel.instance.panel?.reveal(vscode.ViewColumn.Beside);
    return UsagePanel.instance;
  }

  private constructor() {
    this.panel = vscode.window.createWebviewPanel(
      'deepseekUsage',
      'DeepSeek 用量详情',
      vscode.ViewColumn.Beside,
      { enableScripts: true, retainContextWhenHidden: true }
    );
    this.panel.webview.html = this.getHtml();
    this.panel.webview.onDidReceiveMessage(msg => {
      if (msg.type === 'refresh') {
        vscode.commands.executeCommand('deepseekUsage.refresh');
      } else if (msg.type === 'configure') {
        vscode.commands.executeCommand('deepseekUsage.configure');
      }
    });
    this.panel.onDidDispose(() => {
      UsagePanel.instance = undefined;
      this.panel = undefined;
    });
    // Push initial data if available
    if (this.usageHistory.length > 0) {
      this.postUpdate();
    }
  }

  update(balance: BalanceInfo | null, history: UsageDay[], totals: Record<string, number>) {
    this.balance = balance;
    this.usageHistory = history;
    this.modelTotals = totals;
    if (this.panel) {
      this.postUpdate();
    }
  }

  private postUpdate() {
    this.panel?.webview.postMessage({
      type: 'update',
      balance: this.balance,
      usageHistory: this.usageHistory,
      modelTotals: this.modelTotals,
    });
  }

  dispose() {
    this.panel?.dispose();
    UsagePanel.instance = undefined;
    this.panel = undefined;
  }

  private getHtml(): string {
    const panel = this.panel!;
    const csp = panel.webview.cspSource;
    return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${csp} 'unsafe-inline'; script-src ${csp};">
  <title>DeepSeek 用量</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #1E1E28;
      color: #fff;
      padding: 12px;
      font-size: 13px;
    }
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .header h2 { font-size: 15px; }
    .close-btn { background: none; border: none; color: #888; cursor: pointer; font-size: 16px; }
    .close-btn:hover { color: #fff; }
    .balance { color: #00FF00; font-weight: bold; font-size: 14px; margin: 4px 0; }
    .hit-rate { color: #FFA500; font-size: 13px; margin: 4px 0; }
    .tabs { display: flex; gap: 4px; flex-wrap: wrap; margin: 8px 0; }
    .tab-btn {
      background: #444; color: #fff; border: none; border-radius: 4px;
      padding: 3px 10px; font-size: 11px; cursor: pointer;
    }
    .tab-btn.active { background: #2E8B57; }
    .tab-btn:hover { opacity: 0.85; }
    table {
      width: 100%; border-collapse: collapse; margin: 8px 0;
      background: rgba(40,40,40,0.7); border-radius: 5px;
    }
    th, td { padding: 5px 8px; text-align: left; border-bottom: 1px solid #555; }
    th { color: #ddd; font-size: 11px; }
    td { font-size: 12px; }
    .summary { color: #ccc; font-size: 12px; margin: 6px 0; }
    .refresh-btn {
      background: #2E8B57; color: #fff; border: none; border-radius: 5px;
      padding: 5px 16px; font-weight: bold; cursor: pointer; margin: 8px auto;
      display: block;
    }
    .refresh-btn:hover { background: #3CB371; }
    .error { color: #ff6b6b; font-size: 12px; margin: 4px 0; }
  </style>
</head>
<body>
  <div class="header">
    <h2>📊 DeepSeek 用量详情</h2>
    <button class="close-btn" onclick="sendMsg('close')">✕</button>
  </div>
  <div class="balance" id="balance">💰 余额: -- CNY</div>
  <div class="hit-rate" id="hitRate">📊 缓存命中率: --%</div>
  <div class="tabs" id="tabs"></div>
  <table>
    <thead><tr><th>日期</th><th>Token</th><th>缓存命中</th><th>请求数</th></tr></thead>
    <tbody id="tableBody"></tbody>
  </table>
  <div class="summary" id="summary">📋 近7天总消耗: -- Token | 日均: --</div>
  <div class="error" id="notice"></div>
  <button class="refresh-btn" onclick="sendMsg('refresh')">🔄 刷新</button>

  <script>
    const vscode = acquireVsCodeApi();
    let state = vscode.getState() || { currentModel: '__all__', allHistory: [], balance: null, modelTotals: {} };

    function sendMsg(type) {
      if (type === 'close') {
        vscode.postMessage({ type: 'close' });
        return;
      }
      vscode.postMessage({ type });
    }

    function render() {
      const { currentModel, allHistory, balance, modelTotals } = state;
      const modelShort = { 'deepseek-v4-pro': 'v4-pro', 'deepseek-v4-flash': 'v4-flash', 'deepseek-chat & deepseek-reasoner': 'chat/reasoner' };
      const short = (n) => modelShort[n] || n;

      // Balance
      document.getElementById('balance').textContent =
        balance ? \`💰 余额: \${balance.total.toFixed(2)} CNY (赠送: \${balance.granted.toFixed(2)})\` : '💰 余额: 获取失败';

      // Hit rate & total
      let totalHit = 0, totalMiss = 0, totalUsage = 0;
      if (currentModel === '__all__') {
        totalHit = allHistory.reduce((s, d) => s + d.cache_hit_tokens, 0);
        totalMiss = allHistory.reduce((s, d) => s + d.cache_miss_tokens, 0);
        totalUsage = allHistory.reduce((s, d) => s + d.total_tokens, 0);
      } else {
        for (const d of allHistory) {
          const md = d.model_detail[currentModel] || {};
          totalHit += md.cache_hit || 0;
          totalMiss += md.cache_miss || 0;
          totalUsage += md.tokens || 0;
        }
      }
      const promptTotal = totalHit + totalMiss;
      const hitRate = promptTotal > 0 ? (totalHit / promptTotal * 100) : 0;
      document.getElementById('hitRate').textContent =
        currentModel === '__all__'
          ? \`📊 缓存命中率: \${hitRate.toFixed(1)}%\`
          : \`📊 \${short(currentModel)} 命中率: \${hitRate.toFixed(1)}%\`;

      // Tabs
      const models = Object.keys(modelTotals).sort();
      const allModels = ['__all__', ...models];
      const tabsEl = document.getElementById('tabs');
      tabsEl.innerHTML = allModels.map(m => \`<button class="tab-btn\${m === currentModel ? ' active' : ''}" data-model="\${m}">\${m === '__all__' ? '全部' : short(m)}</button>\`).join('');
      tabsEl.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          state.currentModel = btn.dataset.model;
          vscode.setState(state);
          render();
        });
      });

      // Table
      const tbody = document.getElementById('tableBody');
      tbody.innerHTML = allHistory.map(d => {
        let token, hitPct, reqs;
        if (currentModel === '__all__') {
          token = d.total_tokens.toLocaleString();
          const p = d.cache_hit_tokens + d.cache_miss_tokens;
          hitPct = p > 0 ? (d.cache_hit_tokens / p * 100).toFixed(0) + '%' : '-';
          reqs = Object.values(d.model_detail).reduce((s, md) => s + (md.requests || 0), 0);
        } else {
          const md = d.model_detail[currentModel] || {};
          token = (md.tokens || 0).toLocaleString();
          const p = (md.cache_hit || 0) + (md.cache_miss || 0);
          hitPct = p > 0 ? ((md.cache_hit || 0) / p * 100).toFixed(0) + '%' : '-';
          reqs = md.requests || 0;
        }
        return \`<tr><td>\${d.date.slice(5)}</td><td>\${token}</td><td>\${hitPct}</td><td>\${reqs || '-'}</td></tr>\`;
      }).join('');

      // Summary
      const avg = allHistory.length > 0 ? Math.floor(totalUsage / 7) : 0;
      document.getElementById('summary').textContent = \`📋 近7天总消耗: \${totalUsage.toLocaleString()} Token | 日均: \${avg.toLocaleString()}\`;

      // Notice
      document.getElementById('notice').textContent = '';
    }

    window.addEventListener('message', event => {
      const msg = event.data;
      if (msg.type === 'update') {
        state.balance = msg.balance;
        state.allHistory = msg.usageHistory || [];
        state.modelTotals = msg.modelTotals || {};
        if (state.currentModel !== '__all__' && !(state.currentModel in state.modelTotals)) {
          state.currentModel = '__all__';
        }
        vscode.setState(state);
        render();
      }
    });

    render();
  </script>
</body>
</html>`;
  }
}
```

Note: The webview HTML is embedded inline in panel.ts (via `getHtml()` method) — no separate file to load at runtime. This avoids needing to resolve file paths for the webview.

- [ ] **Step 2: Commit**

```bash
cd /c/wangyu_PyP
git add vscode-ext/src/webview/panel.ts
git commit -m "feat: add WebviewPanel manager"
```

---

### Task 6: extension.ts — Entry Point

**Files:**
- Create: `vscode-ext/src/extension.ts`

**Interfaces:**
- Consumes: `fetchUsageHistory`, `getBalance` from api.ts; `UsagePanel` from webview/panel.ts
- Produces: extension `activate`/`deactivate`

- [ ] **Step 1: Create `vscode-ext/src/extension.ts`**

```typescript
import * as vscode from 'vscode';
import { fetchUsageHistory, getBalance, UsageDay, BalanceInfo } from './api';
import { UsagePanel } from './webview/panel';

let statusBarItem: vscode.StatusBarItem;
let timer: NodeJS.Timeout | undefined;
let panel: UsagePanel | undefined;
let latestBalance: BalanceInfo | null = null;
let latestHistory: UsageDay[] = [];
let latestTotals: Record<string, number> = {};

function getConfig() {
  const config = vscode.workspace.getConfiguration('deepseekUsage');
  return {
    bearerToken: config.get<string>('bearerToken', ''),
    apiKey: config.get<string>('apiKey', ''),
    cfClearance: config.get<string>('cfClearance', ''),
    interval: config.get<number>('refreshInterval', 300000),
  };
}

async function refreshData() {
  const cfg = getConfig();

  if (!cfg.bearerToken) {
    statusBarItem.text = '$(key) DeepSeek: 需配置';
    statusBarItem.command = 'deepseekUsage.configure';
    return;
  }

  statusBarItem.text = '$(sync~spin) DeepSeek: 刷新中...';
  statusBarItem.command = 'deepseekUsage.showPanel';

  try {
    const [history, balance] = await Promise.all([
      fetchUsageHistory(cfg.bearerToken, cfg.cfClearance).catch(() => [] as UsageDay[]),
      getBalance(cfg.bearerToken, cfg.apiKey),
    ]);

    latestHistory = history;
    latestBalance = balance;

    // Build model totals
    const totals: Record<string, number> = {};
    for (const day of history) {
      for (const [model, tokens] of Object.entries(day.model_usage)) {
        totals[model] = (totals[model] || 0) + tokens;
      }
    }
    latestTotals = totals;

    // Compute hit rate
    const totalHit = history.reduce((s, d) => s + d.cache_hit_tokens, 0);
    const totalMiss = history.reduce((s, d) => s + d.cache_miss_tokens, 0);
    const promptTotal = totalHit + totalMiss;
    const hitRate = promptTotal > 0 ? (totalHit / promptTotal * 100) : 0;

    // Update status bar
    if (balance) {
      statusBarItem.text = `💰 ${balance.total.toFixed(1)} 📊 ${hitRate.toFixed(1)}%`;
    } else {
      statusBarItem.text = `💰 -- 📊 ${hitRate.toFixed(1)}%`;
    }
    statusBarItem.command = 'deepseekUsage.showPanel';

    // Push to panel if open
    panel?.update(balance, history, totals);

  } catch (err: any) {
    statusBarItem.text = '$(warning) DeepSeek: 获取失败';
    statusBarItem.command = 'deepseekUsage.showPanel';
    console.error('DeepSeek refresh error:', err.message);
  }
}

async function configureToken() {
  const token = await vscode.window.showInputBox({
    prompt: '请输入 DeepSeek platform Bearer Token',
    password: true,
    placeHolder: '从浏览器 F12 → Network → authorization 头获取',
  });
  if (token !== undefined) {
    const config = vscode.workspace.getConfiguration('deepseekUsage');
    await config.update('bearerToken', token, vscode.ConfigurationTarget.Global);
  }

  const apiKey = await vscode.window.showInputBox({
    prompt: '请输入 DeepSeek API Key（可选，用于显示余额）',
    password: true,
    placeHolder: 'sk-xxx（留空跳过）',
  });
  if (apiKey !== undefined) {
    const config = vscode.workspace.getConfiguration('deepseekUsage');
    await config.update('apiKey', apiKey, vscode.ConfigurationTarget.Global);
  }

  const cfVal = await vscode.window.showInputBox({
    prompt: '请输入 cf_clearance（可选，用量接口需要）',
    password: true,
    placeHolder: '从浏览器 F12 → Application → Cookies 获取（留空跳过）',
  });
  if (cfVal !== undefined) {
    const config = vscode.workspace.getConfiguration('deepseekUsage');
    await config.update('cfClearance', cfVal, vscode.ConfigurationTarget.Global);
  }

  refreshData();
}

export function activate(context: vscode.ExtensionContext) {
  // Create status bar item
  statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  statusBarItem.text = '$(key) DeepSeek: 需配置';
  statusBarItem.command = 'deepseekUsage.configure';
  statusBarItem.tooltip = 'DeepSeek API 用量监控 — 点击配置';
  statusBarItem.show();

  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand('deepseekUsage.showPanel', () => {
      panel = UsagePanel.show();
      panel.update(latestBalance, latestHistory, latestTotals);
    }),
    vscode.commands.registerCommand('deepseekUsage.refresh', () => {
      refreshData();
    }),
    vscode.commands.registerCommand('deepseekUsage.configure', () => {
      configureToken();
    })
  );

  // Initial data fetch
  refreshData();

  // Periodic refresh
  const cfg = getConfig();
  timer = setInterval(refreshData, cfg.interval);

  // Listen for config changes
  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration(e => {
      if (e.affectsConfiguration('deepseekUsage')) {
        if (timer) clearInterval(timer);
        const newCfg = getConfig();
        timer = setInterval(refreshData, newCfg.interval);
      }
    })
  );

  context.subscriptions.push({ dispose: () => { if (timer) clearInterval(timer); } });
}

export function deactivate() {
  if (timer) clearInterval(timer);
  panel?.dispose();
}
```

- [ ] **Step 2: Compile to verify**

```bash
cd /c/wangyu_PyP/vscode-ext
npx tsc --noEmit
```

Expected: No compilation errors.

- [ ] **Step 3: Commit**

```bash
cd /c/wangyu_PyP
git add vscode-ext/src/extension.ts
git commit -m "feat: add extension entry point, status bar, and commands"
```

---

### Task 7: Compile & Test in VS Code

**Files:** None

- [ ] **Step 1: Full compile**

```bash
cd /c/wangyu_PyP/vscode-ext
npx tsc
```

Expected: Generates `vscode-ext/out/extension.js`, `vscode-ext/out/api.js`, `vscode-ext/out/webview/panel.js`

- [ ] **Step 2: Load extension in VS Code Extension Development Host**

```bash
cd /c/wangyu_PyP/vscode-ext
code --extensionDevelopmentPath=.
```

Expected: VS Code opens a new window with the extension loaded. Status bar shows the DeepSeek item.

- [ ] **Step 3: Configure and test**

In the development host:
1. Run command `DeepSeek: 配置 API Token` from Command Palette
2. Enter your Bearer Token
3. Verify status bar updates with balance and hit rate
4. Click status bar to open the detail panel
5. Verify table shows 7 days of data
6. Verify model tabs work
7. Run `DeepSeek: 刷新数据` to test manual refresh
8. Close panel and verify status bar still updates

- [ ] **Step 4: Commit**

```bash
cd /c/wangyu_PyP
git add -A
git commit -m "chore: compile and verify extension"
```

---

### Task 8: GitHub & Marketplace Publishing

**Files:** None (GitHub + marketplace operations)

**Prerequisites:** GitHub account, VS Marketplace publisher account

- [ ] **Step 1: Create GitHub repo**

```bash
# Create repo on GitHub first, then:
cd /c/wangyu_PyP
git remote add origin https://github.com/<your-username>/deepseek-usage.git
git push -u origin main
```

- [ ] **Step 2: Create a publisher on VS Code Marketplace**

```bash
# Install vsce if not done
cd /c/wangyu_PyP/vscode-ext
npm install -g @vscode/vsce

# Create publisher (interactive)
vsce create-publisher <your-publisher-id>
# Or login if already created
vsce login <your-publisher-id>
```

- [ ] **Step 3: Package and publish**

```bash
cd /c/wangyu_PyP/vscode-ext
npm run package
# This generates deepseek-usage-0.1.0.vsix

# Publish to marketplace
vsce publish
```

- [ ] **Step 4: Update README with marketplace badge**

After publishing, add the VS Code marketplace version badge and install link to the root `README.md`.
