# DeepSeek Usage Monitor — VS Code Extension Design

## Overview

Port the existing PyQt5 desktop app (`deepseek_float.py`) into a VS Code extension that monitors DeepSeek API usage directly from the editor.

## Repository Structure

Single GitHub repo: `deepseek-usage` containing both the original Python tools and the VS Code extension:

```
deepseek-usage/
├── README.md
├── LICENSE
├── .gitignore
├── deepseek_float.py              # PyQt5 desktop app
├── deepseek.py                    # CLI monitor
├── deepseek_config.txt
├── icon.ico
├── deepseek_float.spec
└── vscode-ext/                    # VS Code extension
    ├── package.json
    ├── tsconfig.json
    ├── CHANGELOG.md
    ├── README.md
    ├── src/
    │   ├── extension.ts           # Entry point
    │   ├── api.ts                 # DeepSeek HTTP client
    │   └── webview/
    │       ├── panel.ts           # WebviewPanel manager
    │       └── index.html         # Panel UI
    └── .vscodeignore
```

## Architecture & Data Flow

```
extension.ts (activate)
    │
    ├── StatusBarItem ←─────────────┐
    │   (always visible)            │
    │                               │
    ├── setInterval(300000) ───→ api.ts ──→ DeepSeek API
    │                               │
    └── onClick ──→ WebviewPanel    │
                    ↑ data ─────────┘
```

- Extension activates on `onStartupFinished`
- Immediately fetches balance + usage history
- Updates status bar text: `💰 XX.X 📊 XX%`
- Opens WebviewPanel on click (lazy: same instance, toggle)
- Refreshes every 5 minutes regardless of panel state
- Webview receives data via `postMessage`

## Webview Panel UI

Layout (matches original DetailPanel exactly):

```
┌─────────────────────────────────────┐
│ 📊 DeepSeek 用量详情            ✕   │
├─────────────────────────────────────┤
│ 💰 余额: 12.50 CNY (赠送: 5.00)     │
│ 📊 缓存命中率: 42.3%               │
├─────────────────────────────────────┤
│ [全部] [v4-pro] [v4-flash] [...]    │
├─────────────────────────────────────┤
│ 日期    Token    缓存命中  请求数    │
│ 06-25  125,436   42%       138      │
│ 06-26   98,231   51%       107      │
│ ...                                 │
├─────────────────────────────────────┤
│ 📋 近7天总消耗: 1,234,567 Token     │
│ 日均: 176,366                       │
├─────────────────────────────────────┤
│           [🔄 刷新]                 │
└─────────────────────────────────────┘
```

- Dark theme: `#1E1E28` background, white text
- Webview is pure HTML + CSS + vanilla JS (no framework)
- Receives data as JSON from extension host via `postMessage`
- Sends commands back via `vscode.postMessage` (refresh, etc.)

## Configuration

VS Code settings (`settings.json`):

```json
{
  "deepseekUsage.bearerToken": "",
  "deepseekUsage.apiKey": "",
  "deepseekUsage.cfClearance": "",
  "deepseekUsage.refreshInterval": 300000
}
```

Stored in VS Code `settings.json` (plaintext, matching the original base64 approach).

First-run flow: no token configured → click status bar → prompt for token + optional API Key + optional cf_clearance.

## Commands

| Command | Title | Action |
|---------|-------|--------|
| `deepseekUsage.showPanel` | DeepSeek: 显示用量面板 | Toggle WebviewPanel |
| `deepseekUsage.refresh` | DeepSeek: 刷新数据 | Force refresh all data |
| `deepseekUsage.configure` | DeepSeek: 配置 API Token | Show config input |

## Error Handling

| Error | UI |
|-------|----|
| Network failure | Status: `⚠️ 网络错误`, auto-retry next cycle |
| Token expired/missing | Status: `🔑 需配置`, click opens config |
| API returns error | Panel shows Chinese error message |
| cf_clearance expired | Status: `⚠️ Cookie 过期`, prompt to update |

## API Client (api.ts)

Ports directly from `deepseek_float.py` methods:

- `fetchUsageHistory(bearerToken, cfClearance)` → maps to `_fetch_usage_history()`
- `getBalance(bearerToken, apiKey)` → maps to `get_balance()`
- Same URL endpoints, same header construction, same response parsing

Uses Node.js `https` module (no extra dependencies).

## Publishing

- GitHub: MIT license, public repo
- VS Code Marketplace: packaged via `vsce`, published under a publisher ID
- Marketplace tags: `deepseek`, `api`, `usage`, `monitor`
