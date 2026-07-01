import requests
import json
import time
import getpass
from datetime import datetime, timedelta
import sys
from decimal import Decimal, InvalidOperation

# ==================== 配置 ====================
DEEPSEEK_API_BASE = "https://api.deepseek.com"


# =============================================

class DeepSeekMonitor:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # 用于模拟用量趋势的数据
        self.usage_history = self._generate_mock_usage()

    def _generate_mock_usage(self):
        """生成模拟的最近7天用量数据 (单位: Token)"""
        data = []
        today = datetime.now()
        for i in range(7, 0, -1):
            date = today - timedelta(days=i)
            # 随机生成一些用量数据
            total_tokens = 1000 + (i * 200) + (hash(str(date)) % 500)
            cache_hit = int(total_tokens * (0.3 + (hash(str(date)) % 50) / 100))
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "total_tokens": total_tokens,
                "cache_hit_tokens": cache_hit,
                "cache_miss_tokens": total_tokens - cache_hit
            })
        return data

    def get_balance(self):
        """获取账户余额"""
        try:
            response = requests.get(
                f"{DEEPSEEK_API_BASE}/user/balance",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if data.get('is_available'):
                # DeepSeek 余额接口可能返回多币种，直接取第一条会导致显示不准确。
                # 这里优先选择 CNY；若没有 CNY 再回退到第一条可用记录。
                balance_infos = data.get('balance_infos') or []
                if not balance_infos:
                    return None

                balance_info = next(
                    (item for item in balance_infos if str(item.get('currency', '')).upper() == 'CNY'),
                    balance_infos[0]
                )

                # 接口字段有时是字符串或空值，统一做安全数值转换，避免异常导致显示为 0。
                def safe_decimal(value):
                    try:
                        return float(Decimal(str(value if value is not None else 0)))
                    except (InvalidOperation, ValueError, TypeError):
                        return 0.0

                return {
                    "currency": str(balance_info.get('currency', 'CNY')).upper(),
                    "total": safe_decimal(balance_info.get('total_balance', 0)),
                    "granted": safe_decimal(balance_info.get('granted_balance', 0)),
                    "topped_up": safe_decimal(balance_info.get('topped_up_balance', 0))
                }
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取余额失败: {e}")
            return None

    def get_cache_hit_rate(self):
        """计算缓存命中率 (基于模拟数据)"""
        total_hit = sum(d['cache_hit_tokens'] for d in self.usage_history)
        total_miss = sum(d['cache_miss_tokens'] for d in self.usage_history)
        total = total_hit + total_miss

        if total == 0:
            return 0.0
        return (total_hit / total) * 100

    def display_dashboard(self):
        """显示仪表盘"""
        # 清屏 (可选)
        # os.system('cls' if os.name == 'nt' else 'clear')

        print("\n" + "=" * 50)
        print("   DeepSeek API 用量监控仪表盘")
        print("=" * 50)

        # 1. 显示余额
        balance = self.get_balance()
        if balance:
            currency = balance.get('currency', 'CNY')
            print("\n💰 账户余额:")
            print(f"  总余额:     {balance['total']:.2f} {currency}")
            print(f"  赠送余额:   {balance['granted']:.2f} {currency}")
            print(f"  充值余额:   {balance['topped_up']:.2f} {currency}")
        else:
            print("\n💰 账户余额: 获取失败")

        # 2. 显示缓存命中率
        hit_rate = self.get_cache_hit_rate()
        print(f"\n📊 缓存命中率 (近7天): {hit_rate:.2f}%")

        # 3. 显示近7天用量趋势
        print("\n📈 近7天Token用量趋势:")
        print("-" * 50)
        print(f"{'日期':<12} {'总用量':<10} {'命中':<10} {'未命中':<10}")
        print("-" * 50)
        for day in self.usage_history:
            print(
                f"{day['date']:<12} {day['total_tokens']:<10,} {day['cache_hit_tokens']:<10,} {day['cache_miss_tokens']:<10,}")
        print("-" * 50)

        # 4. 汇总统计
        total_usage = sum(d['total_tokens'] for d in self.usage_history)
        print(f"\n📋 近7天汇总:")
        print(f"  总Token消耗: {total_usage:,}")
        print(f"  日均消耗:    {total_usage // 7:,}")
        print("=" * 50 + "\n")


def main():
    print("=" * 50)
    print("   DeepSeek API 用量监控工具")
    print("=" * 50)

    # 安全地获取API Key
    api_key = input("请输入你的 DeepSeek API Key 进行测试: ")
    if not api_key:
        print("❌ API Key 不能为空!")
        sys.exit(1)

    monitor = DeepSeekMonitor(api_key)

    # 主循环
    while True:
        monitor.display_dashboard()

        # 等待用户操作
        print("按 Enter 键刷新，或输入 'q' 退出...")
        choice = input().strip().lower()
        if choice == 'q':
            print("👋 退出程序")
            break


if __name__ == "__main__":
    main()