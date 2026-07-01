import sys
import json
import requests
import os
import base64
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QInputDialog, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt, QPoint, QTimer, QRect
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen, QFont, QLinearGradient

# ==================== 配置 ====================
DEEPSEEK_USAGE_URL = "https://platform.deepseek.com/api/v0/usage/amount"
DEEPSEEK_BALANCE_URL = "https://platform.deepseek.com/api/v0/user/balance"
REFRESH_INTERVAL = 300000  # 5分钟
CONFIG_FILE = "deepseek_config.txt"
LOG_FILE = "deepseek_float.log"

# 日志：同时输出到文件和控制台
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("deepseek_float")

# 浏览器请求头（从浏览器抓包获取，Bearer Token 通过配置输入）
BROWSER_HEADERS = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://platform.deepseek.com/usage",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "x-client-bundle-id": "com.deepseek.chat",
    "x-client-locale": "zh_CN",
    "x-client-platform": "web",
    "x-client-timezone-offset": "28800",
    "x-client-version": "1.0.0",
}

# 浏览器 Cookie（cf_clearance 过期后需从浏览器重新抓取）
BROWSER_COOKIES = {
    "cf_clearance": "9_QqCsInOKGToZ76Fq82ZOlO17Hdr_Sdy_Y3N9M9N8k-1755693667-1.2.1.1-dDz6fwEC__gkKi34IA9c6A_8K_p8r3akNDJ1CJYXHRNFAWCkhk1kftTxR1tbyTCcVfhqX8y71sGn4kpKPq1Bnx1tO7W3_CHrLmGuHsFPRZZIiNoqFKJGwOvhwfihAU8Ro1EycA7HMba3RAY6XEgw_9EQvsSa90gyEaGU5KnvACAA3HXR5PJxnM5.lXI8680MJxV0ZabuEb8lr.k7zvOfgF5LvrjmNcXEapvMXiAQcJc",
    "smidV2": "202602022100301e8accffa18ff5cdf3fd4b0a6a167640001f8f8932cb8d650",
    "intercom-device-id-guh50jw4": "65355bdd-0394-479d-bb3d-cd94d1a11ef7",
    ".thumbcache_6b2e5483f9d858d7c661c5e276b6a6ae": "ZXnU9+SEmb44c0DcWrHYBJ7M0Xy4qZjB14htVBT6TL4XgHjw0CNnX+PIE9aSYV85DT3QHexzUbBcsJ8ASXdEyQ==",
    "HWWAFSESTIME": "1782179565612",
    "HWWAFSESID": "c8ec77f2f0550a6ecf",
}

# 模型名缩写
MODEL_SHORT = {
    "deepseek-v4-pro": "v4-pro",
    "deepseek-v4-flash": "v4-flash",
    "deepseek-chat & deepseek-reasoner": "chat/reasoner",
}
# =============================================

class DetailPanel(QWidget):
    """弹出式详细面板"""

    def _short(self, name):
        return MODEL_SHORT.get(name, name)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(460, 500)

        self._current_model = "__all__"
        self._all_history = []
        self._all_models = []

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        # 标题栏
        title_layout = QHBoxLayout()
        title_label = QLabel("📊 DeepSeek 用量详情")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("background: transparent; color: white; border: none; font-size: 14px;")
        close_btn.clicked.connect(self.hide)
        title_layout.addWidget(close_btn)
        layout.addLayout(title_layout)

        # 余额 & 缓存命中率
        self.balance_label = QLabel("💰 余额: -- CNY")
        self.balance_label.setStyleSheet("color: #00FF00; font-size: 13px; font-weight: bold;")
        layout.addWidget(self.balance_label)

        self.hit_label = QLabel("📊 缓存命中率: --%")
        self.hit_label.setStyleSheet("color: #FFA500; font-size: 13px;")
        layout.addWidget(self.hit_label)

        # 模型切换页签
        self.tab_layout = QHBoxLayout()
        self.tab_layout.setSpacing(4)
        self.tab_buttons = {}
        layout.addLayout(self.tab_layout)

        # 表格
        self.table = QTableWidget(7, 4)
        self.table.setHorizontalHeaderLabels(["日期", "Token", "缓存命中", "请求数"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.setColumnWidth(0, 90)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 70)
        self.table.setStyleSheet("""
            QTableWidget {
                background: rgba(40,40,40,180);
                color: white;
                gridline-color: #555;
                border-radius: 5px;
                font-size: 12px;
            }
            QHeaderView::section {
                background: #333;
                color: #ddd;
                padding: 4px;
            }
        """)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        # 汇总
        self.summary_label = QLabel("📋 近7天总消耗: -- Token | 日均: --")
        self.summary_label.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        layout.addWidget(self.summary_label)

        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #2E8B57;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background: #3CB371; }
        """)
        refresh_btn.clicked.connect(self.parent.update_data)
        layout.addWidget(refresh_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background: rgba(30, 30, 40, 230);
                border-radius: 15px;
            }
        """)

    def _build_tabs(self, models):
        """重建模型页签按钮"""
        # 清空旧按钮
        for btn in self.tab_buttons.values():
            self.tab_layout.removeWidget(btn)
            btn.deleteLater()
        self.tab_buttons.clear()

        all_models = ["__all__"] + sorted(models)
        for i, m in enumerate(all_models):
            label = "全部" if m == "__all__" else self._short(m)
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setChecked(m == self._current_model)
            btn.setFixedHeight(22)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {'#2E8B57' if m == self._current_model else '#444'};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 0 8px;
                    font-size: 11px;
                }}
                QPushButton:hover {{ background: {'#3CB371' if m == self._current_model else '#555'}; }}
            """)
            btn.clicked.connect(lambda checked, model=m: self._on_tab_click(model))
            self.tab_layout.addWidget(btn)
            self.tab_buttons[m] = btn
        self.tab_layout.addStretch()

    def _on_tab_click(self, model):
        self._current_model = model
        # 更新按钮样式
        for m, btn in self.tab_buttons.items():
            btn.setChecked(m == model)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {'#2E8B57' if m == model else '#444'};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 0 8px;
                    font-size: 11px;
                }}
                QPushButton:hover {{ background: {'#3CB371' if m == model else '#555'}; }}
            """)
        self._refresh_table()

    def _refresh_table(self):
        """根据当前选中的模型刷新表格"""
        self.table.setRowCount(len(self._all_history))
        for row, day in enumerate(self._all_history):
            self.table.setItem(row, 0, QTableWidgetItem(day['date'][5:]))  # MM-DD
            if self._current_model == "__all__":
                total = day['total_tokens']
                hit = day['cache_hit_tokens']
                miss = day['cache_miss_tokens']
                prompt_total = hit + miss
                hit_pct = (hit / prompt_total * 100) if prompt_total > 0 else 0
                self.table.setItem(row, 1, QTableWidgetItem(f"{total:,}"))
                self.table.setItem(row, 2, QTableWidgetItem(f"{hit_pct:.0f}%"))
                reqs = sum(
                    day.get('model_detail', {}).get(m, {}).get('requests', 0)
                    for m in day.get('model_detail', {})
                )
                self.table.setItem(row, 3, QTableWidgetItem(str(reqs) if reqs else "-"))
            else:
                md = day.get('model_detail', {}).get(self._current_model, {})
                total = md.get('tokens', 0)
                hit = md.get('cache_hit', 0)
                miss = md.get('cache_miss', 0)
                prompt_total = hit + miss
                hit_pct = (hit / prompt_total * 100) if prompt_total > 0 else 0
                self.table.setItem(row, 1, QTableWidgetItem(f"{total:,}"))
                self.table.setItem(row, 2, QTableWidgetItem(f"{hit_pct:.0f}%"))
                self.table.setItem(row, 3, QTableWidgetItem(str(md.get('requests', 0)) if md.get('requests') else "-"))

        # 更新命中率标签 & 汇总
        if self._current_model == "__all__":
            total_hit = sum(d['cache_hit_tokens'] for d in self._all_history)
            total_miss = sum(d['cache_miss_tokens'] for d in self._all_history)
            prompt_total = total_hit + total_miss
            hit_rate = (total_hit / prompt_total * 100) if prompt_total > 0 else 0
            self.hit_label.setText(f"📊 缓存命中率: {hit_rate:.1f}%")
            total_usage = sum(d['total_tokens'] for d in self._all_history)
        else:
            total_hit = sum(
                d.get('model_detail', {}).get(self._current_model, {}).get('cache_hit', 0)
                for d in self._all_history
            )
            total_miss = sum(
                d.get('model_detail', {}).get(self._current_model, {}).get('cache_miss', 0)
                for d in self._all_history
            )
            prompt_total = total_hit + total_miss
            hit_rate = (total_hit / prompt_total * 100) if prompt_total > 0 else 0
            total_usage = sum(
                d.get('model_detail', {}).get(self._current_model, {}).get('tokens', 0)
                for d in self._all_history
            )
            self.hit_label.setText(f"📊 {self._short(self._current_model)} 命中率: {hit_rate:.1f}%")

        avg = total_usage // 7 if len(self._all_history) > 0 else 0
        self.summary_label.setText(f"📋 近7天总消耗: {total_usage:,} Token | 日均: {avg:,}")

    def update_display(self, balance, usage_history, model_totals, usage_notice=""):
        if balance:
            self.balance_label.setText(f"💰 余额: {balance['total']:.2f} CNY (赠送: {balance['granted']:.2f})")
        else:
            self.balance_label.setText("💰 余额: 获取失败")

        self._all_history = usage_history
        all_models = sorted(model_totals.keys())
        if all_models != self._all_models:
            self._all_models = all_models
            self._build_tabs(all_models)
        # 确保当前选中模型还存在
        if self._current_model != "__all__" and self._current_model not in all_models:
            self._current_model = "__all__"

        self._refresh_table()


class FloatingBall(QWidget):
    """圆形悬浮球"""
    def __init__(self, bearer_token, api_key=""):
        super().__init__()
        self.bearer_token = bearer_token
        self.api_key = api_key
        self.usage_history = []
        self.model_totals = {}
        self.usage_notice = ""
        self.balance = None
        self.hit_rate = 0.0

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(80, 80)

        self.detail_panel = DetailPanel(self)
        self.detail_panel.hide()

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("color: white; font-weight: bold; font-size: 11px; background: transparent;")
        self.label.setGeometry(0, 20, 80, 40)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(REFRESH_INTERVAL)

        self.update_data()

        self._dragging = False
        self._press_pos = QPoint()
        self.drag_position = QPoint()

    def _safe_int(self, value):
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return 0

    def _build_headers(self):
        """构建带 Bearer Token 的请求头"""
        headers = dict(BROWSER_HEADERS)
        headers["authorization"] = f"Bearer {self.bearer_token}"
        return headers

    def _extract_usage_amounts(self, usage_list):
        """从 platform API 的 usage 数组中提取各类 token 数量"""
        result = {
            "prompt_tokens": 0,
            "cache_hit_tokens": 0,
            "cache_miss_tokens": 0,
            "response_tokens": 0,
            "requests": 0,
        }
        type_map = {
            "PROMPT_TOKEN": "prompt_tokens",
            "PROMPT_CACHE_HIT_TOKEN": "cache_hit_tokens",
            "PROMPT_CACHE_MISS_TOKEN": "cache_miss_tokens",
            "RESPONSE_TOKEN": "response_tokens",
            "REQUEST": "requests",
        }
        for item in (usage_list or []):
            key = type_map.get(item.get("type", ""))
            if key:
                result[key] += self._safe_int(item.get("amount", 0))
        result["total_tokens"] = (
            result["prompt_tokens"] + result["cache_hit_tokens"] +
            result["cache_miss_tokens"] + result["response_tokens"]
        )
        return result

    def _fetch_usage_history(self):
        """从 platform.deepseek.com 拉取近7天真实用量"""
        now = datetime.now()
        end_date = now.strftime("%Y-%m-%d")
        start_date = (now - timedelta(days=6)).strftime("%Y-%m-%d")

        log.info(f"[用量] 开始拉取 {start_date} ~ {end_date} 的用量数据...")
        try:
            url = f"{DEEPSEEK_USAGE_URL}?month={now.month}&year={now.year}"
            log.info(f"[用量] 请求 {url}")
            response = requests.get(
                DEEPSEEK_USAGE_URL,
                headers=self._build_headers(),
                params={"month": now.month, "year": now.year},
                cookies=BROWSER_COOKIES,
                timeout=10
            )
            log.info(f"[用量] HTTP {response.status_code}")
            if response.status_code != 200:
                self.usage_notice = f"用量接口返回 HTTP {response.status_code}"
                log.info(f"[用量] 响应内容: {response.text[:300]}")
                return []

            data = response.json()
            log.info(f"[用量] code={data.get('code')}, msg={data.get('msg', '')}")
            if data.get("code") != 0:
                self.usage_notice = f"用量接口错误: {data.get('msg', 'unknown')}"
                return []

            days_data = data.get("data", {}).get("biz_data", {}).get("days", [])
            log.info(f"[用量] 获取到 {len(days_data)} 天数据")
            if not days_data:
                self.usage_notice = "用量接口返回空数据"
                return []

            # 解析每天数据，按模型汇总
            norm_dict = {}
            for day in (days_data or []):
                date_str = str(day.get("date", ""))[:10]
                if date_str < start_date or date_str > end_date:
                    continue

                day_total = 0
                day_cache_hit = 0
                day_cache_miss = 0
                model_usage = {}
                model_detail = {}

                for model_entry in day.get("data", []):
                    model_name = model_entry.get("model", "unknown")
                    amounts = self._extract_usage_amounts(model_entry.get("usage", []))
                    mt = amounts["total_tokens"]
                    if mt > 0:
                        model_usage[model_name] = mt
                    model_detail[model_name] = {
                        "tokens": mt,
                        "cache_hit": amounts["cache_hit_tokens"],
                        "cache_miss": amounts["cache_miss_tokens"],
                        "requests": amounts["requests"],
                    }
                    day_total += mt
                    day_cache_hit += amounts["cache_hit_tokens"]
                    day_cache_miss += amounts["cache_miss_tokens"]

                norm_dict[date_str] = {
                    "date": date_str,
                    "total_tokens": day_total,
                    "cache_hit_tokens": day_cache_hit,
                    "cache_miss_tokens": day_cache_miss,
                    "model_usage": model_usage,
                    "model_detail": model_detail,
                }

            # 按日期顺序填充，缺失日期补零
            result = []
            current = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            while current <= end:
                ds = current.strftime("%Y-%m-%d")
                if ds in norm_dict:
                    result.append(norm_dict[ds])
                else:
                    result.append({
                        "date": ds, "total_tokens": 0,
                        "cache_hit_tokens": 0, "cache_miss_tokens": 0,
                        "model_usage": {}, "model_detail": {},
                    })
                current += timedelta(days=1)

            self.usage_notice = ""
            return result

        except requests.exceptions.RequestException as e:
            self.usage_notice = f"用量接口请求失败: {str(e)[:50]}"
            log.info(f"[用量] 请求异常: {e}")
            return []
        except Exception as e:
            self.usage_notice = f"用量数据解析失败: {str(e)[:50]}"
            log.exception(f"[用量] 解析异常: {e}")
            return []

    def _build_model_totals(self, usage_history):
        totals = defaultdict(int)
        for day in usage_history:
            for model, tokens in day.get('model_usage', {}).items():
                totals[model] += self._safe_int(tokens)
        return dict(totals)

    def get_balance(self):
        """获取余额。有 API Key 走 api.deepseek.com，否则尝试 platform cookie"""
        # 优先用 API Key（最可靠）
        if self.api_key:
            try:
                url = "https://api.deepseek.com/user/balance"
                log.info(f"[余额] 使用 API Key 请求 {url} ...")
                resp = requests.get(
                    url,
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    timeout=10
                )
                log.info(f"[余额] HTTP {resp.status_code}")
                if resp.status_code == 200:
                    data = resp.json()
                    log.info(f"[余额] 响应: {json.dumps(data, ensure_ascii=False)[:300]}")
                    if data.get('is_available'):
                        info = data['balance_infos'][0]
                        return {
                            "total": float(info.get('total_balance', 0)),
                            "granted": float(info.get('granted_balance', 0)),
                            "topped_up": float(info.get('topped_up_balance', 0))
                        }
                else:
                    log.info(f"[余额] 失败: {resp.text[:200]}")
            except Exception as e:
                log.info(f"[余额] API Key 请求异常: {e}")

        # 兜底：用浏览器 token 尝试 platform 接口
        if not self.api_key:
            log.info("[余额] 无 API Key，尝试浏览器 Cookie 方式...")
        for url in [
            "https://platform.deepseek.com/api/v0/user/balance",
            "https://platform.deepseek.com/api/v0/billing/balance",
        ]:
            try:
                log.info(f"[余额] 请求 {url} ...")
                resp = requests.get(
                    url,
                    headers=self._build_headers(),
                    cookies=BROWSER_COOKIES,
                    timeout=10
                )
                log.info(f"[余额] HTTP {resp.status_code}")
                if resp.status_code == 200:
                    data = resp.json()
                    log.info(f"[余额] 响应: {json.dumps(data, ensure_ascii=False)[:300]}")
                    if data.get('is_available'):
                        info = data['balance_infos'][0]
                        return {
                            "total": float(info.get('total_balance', 0)),
                            "granted": float(info.get('granted_balance', 0)),
                            "topped_up": float(info.get('topped_up_balance', 0))
                        }
                else:
                    log.info(f"[余额] 失败: {resp.text[:200]}")
            except Exception as e:
                log.info(f"[余额] 请求异常: {e}")

        log.info("[余额] 所有方式均失败")
        return None

    def get_cache_hit_rate(self):
        total_hit = sum(d['cache_hit_tokens'] for d in self.usage_history)
        total_miss = sum(d['cache_miss_tokens'] for d in self.usage_history)
        total = total_hit + total_miss
        return (total_hit / total * 100) if total > 0 else 0.0

    def update_data(self):
        log.info("=" * 40)
        log.info(f"[更新] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 开始刷新数据...")
        self.usage_history = self._fetch_usage_history()
        self.model_totals = self._build_model_totals(self.usage_history)
        self.balance = self.get_balance()
        self.hit_rate = self.get_cache_hit_rate()

        if self.balance:
            text = f"💰 {self.balance['total']:.1f}\n📊 {self.hit_rate:.1f}%"
            log.info(f"[更新] 余额={self.balance['total']:.2f}, 命中率={self.hit_rate:.1f}%")
        else:
            text = "💰 --\n📊 --%"
            log.info(f"[更新] 余额获取失败, 命中率={self.hit_rate:.1f}%")
        self.label.setText(text)

        self.detail_panel.update_display(
            self.balance,
            self.usage_history,
            self.model_totals,
            self.usage_notice
        )
        log.info(f"[更新] 完成，共 {len(self.usage_history)} 天用量数据")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QLinearGradient(0, 0, 80, 80)
        gradient.setColorAt(0, QColor(60, 100, 200))
        gradient.setColorAt(1, QColor(30, 50, 120))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(200, 200, 255, 100), 1))
        painter.drawEllipse(0, 0, 80, 80)

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(255, 255, 255, 50), 2))
        painter.drawEllipse(5, 5, 70, 70)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._press_pos = event.globalPos()
            self._dragging = False
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if not self._dragging:
                delta = event.globalPos() - self._press_pos
                if abs(delta.x()) > 3 or abs(delta.y()) > 3:
                    self._dragging = True
            if self._dragging:
                self.move(event.globalPos() - self.drag_position)
                if self.detail_panel.isVisible():
                    self.update_panel_position()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self._dragging:
                # 单击：切换面板
                if not self.detail_panel.isVisible():
                    self.detail_panel.show()
                    self.update_panel_position()
                else:
                    self.detail_panel.hide()
            self._dragging = False
            event.accept()

    def update_panel_position(self):
        pos = self.frameGeometry().topRight()
        screen_geometry = QApplication.desktop().availableGeometry()
        x = pos.x() + 10
        y = pos.y()
        if x + self.detail_panel.width() > screen_geometry.width():
            x = pos.x() - 10 - self.detail_panel.width()
        if y + self.detail_panel.height() > screen_geometry.height():
            y = screen_geometry.height() - self.detail_panel.height()
        self.detail_panel.move(x, y)


# ========== 配置管理 ==========
CONFIG_KEYS = ["bearer_token", "api_key", "cf_clearance"]

def load_config():
    """加载配置，返回 dict"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                cfg = json.loads(base64.b64decode(f.read().strip()).decode())
                return cfg if isinstance(cfg, dict) else {}
        except:
            return {}
    return {}

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w") as f:
            f.write(base64.b64encode(json.dumps(cfg).encode()).decode())
    except:
        pass

def update_cookies_from_config(cfg):
    """用配置文件里的 cf_clearance 更新全局 Cookie"""
    if cfg.get("cf_clearance"):
        BROWSER_COOKIES["cf_clearance"] = cfg["cf_clearance"]

def main():
    app = QApplication(sys.argv)

    cfg = load_config()
    bearer_token = cfg.get("bearer_token", "")
    api_key = cfg.get("api_key", "")
    update_cookies_from_config(cfg)

    # 首次运行或缺少 Bearer Token
    if not bearer_token:
        bearer_token, ok = QInputDialog.getText(
            None,
            "DeepSeek 用量助手 — Bearer Token",
            "请输入浏览器中抓取的 Bearer Token\n（打开 platform.deepseek.com → F12 → Network → 找 authorization 字段）:",
            echo=QLineEdit.Password
        )
        if not ok or not bearer_token.strip():
            QMessageBox.warning(None, "提示", "Bearer Token 不能为空，程序退出。")
            sys.exit(1)
        bearer_token = bearer_token.strip()
        cfg["bearer_token"] = bearer_token

    # 首次运行或缺少 API Key（余额可选）
    if not api_key:
        api_key, ok = QInputDialog.getText(
            None,
            "DeepSeek 用量助手 — API Key（可选）",
            "请输入 DeepSeek API Key（sk-xxx）用于显示余额：\n（留空则跳过余额，可在 deepseek_config.txt 中手动添加）:",
            echo=QLineEdit.Password
        )
        if ok and api_key.strip():
            api_key = api_key.strip()
            cfg["api_key"] = api_key

    # 询问 cf_clearance（可选，但用量接口可能因过期而 40003）
    if not cfg.get("cf_clearance"):
        cf_val, ok = QInputDialog.getText(
            None,
            "DeepSeek 用量助手 — cf_clearance（可选）",
            "请输入浏览器 Cookie 中的 cf_clearance 值：\n（F12 → Application → Cookies → cf_clearance）\n（留空使用内置值）:",
            echo=QLineEdit.Password
        )
        if ok and cf_val.strip():
            cfg["cf_clearance"] = cf_val.strip()

    save_config(cfg)
    update_cookies_from_config(cfg)

    if bearer_token:
        log.info(f"配置加载: bearer_token={'***'+bearer_token[-4:]}, api_key={'有' if api_key else '无'}, cf_clearance={'有' if cfg.get('cf_clearance') else '内置'}")

    ball = FloatingBall(bearer_token, api_key)
    ball.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
