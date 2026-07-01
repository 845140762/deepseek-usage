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
