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
      getBalance(cfg.bearerToken, cfg.apiKey).catch(() => null as BalanceInfo | null),
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
    console.error('DeepSeek refresh error:', String(err));
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
