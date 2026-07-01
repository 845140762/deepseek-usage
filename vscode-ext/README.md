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
