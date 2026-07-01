import * as vscode from 'vscode';
import { UsageDay, BalanceInfo } from '../api';

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
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${csp} 'unsafe-inline'; script-src ${csp} 'unsafe-inline';">
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
    <h2>\u{1f4ca} DeepSeek 用量详情</h2>
    <button class="close-btn" onclick="sendMsg('close')">✕</button>
  </div>
  <div class="balance" id="balance">\u{1f4b0} 余额: -- CNY</div>
  <div class="hit-rate" id="hitRate">\u{1f4ca} 缓存命中率: --%</div>
  <div class="tabs" id="tabs"></div>
  <table>
    <thead><tr><th>日期</th><th>Token</th><th>缓存命中</th><th>请求数</th></tr></thead>
    <tbody id="tableBody"></tbody>
  </table>
  <div class="summary" id="summary">\u{1f4cb} 近7天总消耗: -- Token | 日均: --</div>
  <div class="error" id="notice"></div>
  <button class="refresh-btn" onclick="sendMsg('refresh')">\u{1f504} 刷新</button>

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
        balance ? \`\u{1f4b0} 余额: \${balance.total.toFixed(2)} CNY (赠送: \${balance.granted.toFixed(2)})\` : '\u{1f4b0} 余额: 获取失败';

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
          ? \`\u{1f4ca} 缓存命中率: \${hitRate.toFixed(1)}%\`
          : \`\u{1f4ca} \${short(currentModel)} 命中率: \${hitRate.toFixed(1)}%\`;

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
      document.getElementById('summary').textContent = \`\u{1f4cb} 近7天总消耗: \${totalUsage.toLocaleString()} Token | 日均: \${avg.toLocaleString()}\`;

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
