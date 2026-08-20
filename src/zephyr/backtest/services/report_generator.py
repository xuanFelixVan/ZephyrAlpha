# [BLUEPRINT] MOD-BT-019 | docs/03_modules/_domain_backtest/report_generator/blueprint.md
# [MODULE] zephyr.backtest.services.report_generator
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 前端归档 ; 邮件分发 ; 人工审查
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ReportConfig/Result frozen不可变; HTML自包含内联CSS; 缺失字段显示N/A不报错; UTF-8编码
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ReportError(ZA-BT-0019)
# [TESTS] tests/backtest/test_report_generator.py
# [A_module] module_id=MOD-BT-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_BACKTEST — Backtest Report Generator (回测报告生成器)

将回测结果(BacktestResult)转换为结构化 HTML 报告。
包含汇总指标表、元数据、过拟合警告、可选的权益曲线 SVG 图和交易日志表。
纯标准库实现, 报告自包含(内联 CSS), 可离线打开。

属 A 类基础设施(纯模板渲染+数据格式化), 纯基础层不涉及策略。

设计真源: depgraph MOD-BT-019
蓝图: docs/03_modules/_domain_backtest/report_generator/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 回测结果字典 dict
#   fields: strategy_id + annual_return + total_return + sharpe_ratio + max_drawdown + win_rate + trades_count + overfitting_flag + 时间区间/基准
#   code: result
# - id: I2
#   name: 权益曲线 list[dict]
#   fields: timestamp + equity
#   code: equity_curve
# - id: I3
#   name: 交易日志 list[dict]
#   fields: timestamp + symbol + side + price + quantity + commission
#   code: trade_log
# - id: I4
#   name: 报告配置 ReportConfig frozen
#   fields: format + include_equity_curve + include_trade_log + max_trades_display + chart_width/height
#   code: ReportConfig
# 层: 算法
# - id: A1
#   name_zh: ① 输入校验与格式分发
#   name_en: generate
#   intro: 校验result必须是dict且有strategy_id，按配置分发HTML或TEXT渲染
#   desc: isinstance校验 → strategy_id非空校验 → format==TEXT走文本否则走HTML
#   inputs: I1 I2 I3 I4
#   outputs: 报告字符串
# - id: A2
#   name_zh: ② HTML报告组装
#   name_en: _generate_html
#   intro: 拼自包含HTML：头部元信息+指标表+过拟合警告+可选SVG图和交易表
#   desc: html.escape转义 → 汇总指标表6行 → overfitting_flag触发红色警告 → 内联CSS模板
#   inputs: I1 I2 I3
#   outputs: HTML字符串
#   invariant: 缺失字段显示N/A不报错; UTF-8自包含
# - id: A3
#   name_zh: ③ 权益曲线SVG坐标映射
#   name_en: _build_equity_svg
#   intro: 把equity序列归一化映射成SVG折线坐标点
#   desc: values=float(equity) → min/max归一化 → x=padding+i/(n-1)×plot_w, y反向映射plot_h → polyline
#   inputs: I2 I4
#   outputs: SVG片段
# - id: A4
#   name_zh: ④ 交易日志表截断渲染
#   name_en: _build_trade_table
#   intro: 交易日志截断到max_trades_display条渲染成HTML表
#   desc: trade_log[:max] → 逐行转义填6列表 → 超出时附截断说明
#   inputs: I3 I4
#   outputs: 交易表HTML
# - id: A5
#   name_zh: ⑤ 数值格式化辅助
#   name_en: _fmt_percent/_fmt_float/_fmt_int/_fmt_datetime
#   intro: 百分比/浮点/整数/日期统一格式化，异常值兜底N/A
#   desc: float(value)×100保留2位 / 保留4位小数 / int转换 / datetime strftime，异常返回N/A
#   inputs: I1
#   outputs: 格式化字符串
# 层: 输出
# - id: O1
#   name_zh: 回测报告字符串 HTML/TEXT
#   name_en: report_str
#   intro: 自包含HTML或纯文本报告，可直接离线打开
#   invariant: HTML内联CSS; 缺失字段N/A
#   downstream: 前端归档 ; 邮件分发 ; 人工审查
# - id: O2
#   name_zh: 落盘报告文件 Path
#   name_en: save_report
#   intro: 报告写入磁盘文件并返回Path
#   downstream: 前端归档 ; 邮件分发
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# I1 --> A2
# I2 --> A2
# I3 --> A2
# I2 --> A3
# I4 --> A3
# I3 --> A4
# I4 --> A4
# I1 --> A5
# A1 --> A2
# A2 --> A3
# A2 --> A4
# A2 --> A5
# A2 --> O1
# A1 --> O1
# O1 --> O2
"""

from __future__ import annotations

import html
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "ReportError",
    "ReportFormat",
    "ReportConfig",
    "BacktestReportGenerator",
]

_logger = logging.getLogger(__name__)


class ReportError(ZephyrBaseError):
    """报告生成异常——输入非法。"""

    error_code = "ZA-BT-0019"


class ReportFormat(str, Enum):
    """报告输出格式。"""

    HTML = "html"
    TEXT = "text"


@dataclass(frozen=True)
class ReportConfig:
    """报告配置——不可变。

    Attributes:
        format: 输出格式 (HTML/TEXT)。
        include_equity_curve: 是否包含权益曲线 SVG。
        include_trade_log: 是否包含交易日志表。
        max_trades_display: 交易日志最大显示条数。
        chart_width: SVG 图表宽度 (像素)。
        chart_height: SVG 图表高度 (像素)。
    """

    format: ReportFormat = ReportFormat.HTML
    include_equity_curve: bool = True
    include_trade_log: bool = True
    max_trades_display: int = 50
    chart_width: int = 800
    chart_height: int = 300

    def __post_init__(self) -> None:
        if self.max_trades_display <= 0:
            raise ReportError(
                f"max_trades_display must be > 0, got {self.max_trades_display}",
                details={"max_trades_display": self.max_trades_display},
            )
        if self.chart_width <= 0 or self.chart_height <= 0:
            raise ReportError(
                f"chart dimensions must be > 0, got width={self.chart_width} height={self.chart_height}",
            )


class BacktestReportGenerator:
    """回测报告生成器——HTML/TEXT 报告自动生成。

    Usage:
        gen = BacktestReportGenerator()
        html_report = gen.generate(
            result={"strategy_id": "strat_a", "sharpe_ratio": 1.5, ...},
            equity_curve=[{"timestamp": "2024-01-01", "equity": 1.0}, ...],
            trade_log=[{"symbol": "000001", "side": "buy", ...}, ...],
        )
        BacktestReportGenerator.save_report(html_report, "report.html")
    """

    def __init__(self, config: ReportConfig | None = None) -> None:
        self._config = config if config is not None else ReportConfig()

    @property
    def config(self) -> ReportConfig:
        """配置 (只读)。"""
        return self._config

    # ------------------------------------------------------------------
    # 公开 API
    # ------------------------------------------------------------------
    def generate(
        self,
        result: dict,
        equity_curve: list[dict] | None = None,
        trade_log: list[dict] | None = None,
    ) -> str:
        """生成回测报告。

        Args:
            result: 回测结果字典 (含 BacktestResult 标准字段)。
            equity_curve: 权益曲线 [{timestamp, equity}, ...] (可选)。
            trade_log: 交易日志 [{timestamp, symbol, side, price, quantity, ...}, ...] (可选)。

        Returns:
            报告字符串 (HTML 或 TEXT, 取决于 config.format)。

        Raises:
            ReportError: result 非 dict / 缺少 strategy_id。
        """
        if not isinstance(result, dict):
            raise ReportError(f"result must be a dict, got {type(result).__name__}")
        if not result.get("strategy_id"):
            raise ReportError("result.strategy_id 不能为空")

        if self._config.format == ReportFormat.TEXT:
            return self._generate_text(result, equity_curve, trade_log)
        return self._generate_html(result, equity_curve, trade_log)

    @staticmethod
    def save_report(content: str, path: str | Path) -> Path:
        """将报告内容写入文件。

        Args:
            content: 报告内容。
            path: 文件路径。

        Returns:
            写入的文件 Path 对象。
        """
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        _logger.info("报告已保存: %s", p)
        return p

    # ------------------------------------------------------------------
    # HTML 生成
    # ------------------------------------------------------------------
    def _generate_html(
        self,
        result: dict,
        equity_curve: list[dict] | None,
        trade_log: list[dict] | None,
    ) -> str:
        """生成 HTML 报告。"""
        strategy_id = html.escape(str(result.get("strategy_id", "N/A")))
        timestamp = self._fmt_datetime(result.get("timestamp"))
        start_date = self._fmt_datetime(result.get("start_date"))
        end_date = self._fmt_datetime(result.get("end_date"))
        benchmark = result.get("benchmark_symbol")
        benchmark_html = html.escape(str(benchmark)) if benchmark else "N/A"

        metrics_rows = self._build_metrics_table(result)
        overfitting_alert = self._build_overfitting_alert(result)
        equity_svg = self._build_equity_svg(equity_curve) if self._config.include_equity_curve and equity_curve else ""
        trade_table = self._build_trade_table(trade_log) if self._config.include_trade_log and trade_log else ""

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>回测报告 — {strategy_id}</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", Roboto, sans-serif; margin: 2rem; color: #333; }}
  h1 {{ color: #1a1a2e; border-bottom: 2px solid #16213e; padding-bottom: 0.5rem; }}
  h2 {{ color: #16213e; margin-top: 1.5rem; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
  th, td {{ border: 1px solid #ddd; padding: 0.5rem 0.75rem; text-align: left; }}
  th {{ background-color: #16213e; color: white; }}
  tr:nth-child(even) {{ background-color: #f8f9fa; }}
  .alert {{ background-color: #fee; border: 1px solid #c33; border-radius: 4px; padding: 1rem; margin: 1rem 0; color: #c33; }}
  .meta {{ color: #666; font-size: 0.9rem; margin-bottom: 1rem; }}
  .metric-value {{ font-weight: bold; }}
  .positive {{ color: #2a9d4f; }}
  .negative {{ color: #d62828; }}
  svg {{ max-width: 100%; height: auto; }}
</style>
</head>
<body>
<h1>回测报告 — {strategy_id}</h1>
<div class="meta">
  <p>回测区间: {start_date} → {end_date} | 基准: {benchmark_html} | 生成时间: {timestamp}</p>
</div>
{overfitting_alert}
<h2>汇总指标</h2>
<table>
<thead><tr><th>指标</th><th>值</th></tr></thead>
<tbody>
{metrics_rows}
</tbody>
</table>
{equity_svg}
{trade_table}
</body>
</html>"""

    def _build_metrics_table(self, result: dict) -> str:
        """构建指标表 HTML 行。"""
        rows = [
            ("年化收益", self._fmt_percent(result.get("annual_return"))),
            ("总收益", self._fmt_percent(result.get("total_return"))),
            ("Sharpe 比率", self._fmt_float(result.get("sharpe_ratio"))),
            ("最大回撤", self._fmt_percent(result.get("max_drawdown"))),
            ("胜率", self._fmt_percent(result.get("win_rate"))),
            ("交易次数", self._fmt_int(result.get("trades_count"))),
        ]
        html_rows = []
        for label, value in rows:
            css = ""
            val_str = str(value)
            if val_str.startswith("-") and label != "最大回撤":
                css = "negative"
            elif val_str.startswith("+") or (
                label in ("年化收益", "总收益", "Sharpe 比率", "胜率") and val_str not in ("N/A", "0.00%", "0.00")
            ):
                css = "positive"
            html_rows.append(
                f'  <tr><td>{html.escape(label)}</td><td class="metric-value {css}">{html.escape(val_str)}</td></tr>'
            )
        return "\n".join(html_rows)

    def _build_overfitting_alert(self, result: dict) -> str:
        """构建过拟合警告 HTML。"""
        if result.get("overfitting_flag"):
            return '<div class="alert">⚠️ 过拟合警告: 该回测结果可能存在过拟合, 请谨慎参考。</div>'
        return ""

    def _build_equity_svg(self, equity_curve: list[dict]) -> str:
        """构建权益曲线 SVG 图。"""
        if not equity_curve:
            return ""
        w = self._config.chart_width
        h = self._config.chart_height
        padding = 40
        plot_w = w - 2 * padding
        plot_h = h - 2 * padding

        values = []
        for point in equity_curve:
            try:
                values.append(float(point.get("equity", 0)))
            except (TypeError, ValueError):
                values.append(0.0)
        if not values:
            return ""

        min_v = min(values)
        max_v = max(values)
        range_v = max_v - min_v if max_v != min_v else 1.0
        n = len(values)

        points = []
        for i, v in enumerate(values):
            x = padding + (i / max(n - 1, 1)) * plot_w
            y = padding + plot_h - ((v - min_v) / range_v) * plot_h
            points.append(f"{x:.1f},{y:.1f}")

        polyline_points = " ".join(points)
        return f"""
<h2>权益曲线</h2>
<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{w}" height="{h}" fill="#fafafa" stroke="#ddd"/>
  <line x1="{padding}" y1="{padding}" x2="{padding}" y2="{h - padding}" stroke="#999"/>
  <line x1="{padding}" y1="{h - padding}" x2="{w - padding}" y2="{h - padding}" stroke="#999"/>
  <text x="{padding}" y="{padding - 10}" font-size="11" fill="#666">{self._fmt_float(max_v)}</text>
  <text x="{padding}" y="{h - padding + 15}" font-size="11" fill="#666">{self._fmt_float(min_v)}</text>
  <polyline points="{polyline_points}" fill="none" stroke="#16213e" stroke-width="2"/>
</svg>"""

    def _build_trade_table(self, trade_log: list[dict]) -> str:
        """构建交易日志 HTML 表。"""
        if not trade_log:
            return ""
        trades = trade_log[: self._config.max_trades_display]
        header = "<tr><th>时间</th><th>标的</th><th>方向</th><th>价格</th><th>数量</th><th>佣金</th></tr>"
        rows = []
        for t in trades:
            rows.append(
                "<tr>"
                f"<td>{html.escape(str(t.get('timestamp', 'N/A')))}</td>"
                f"<td>{html.escape(str(t.get('symbol', 'N/A')))}</td>"
                f"<td>{html.escape(str(t.get('side', 'N/A')))}</td>"
                f"<td>{self._fmt_float(t.get('price'))}</td>"
                f"<td>{self._fmt_float(t.get('quantity'))}</td>"
                f"<td>{self._fmt_float(t.get('commission'))}</td>"
                "</tr>"
            )
        truncated_note = ""
        if len(trade_log) > self._config.max_trades_display:
            truncated_note = (
                f'<p class="meta">仅展示前 {self._config.max_trades_display} 条, 共 {len(trade_log)} 条交易</p>'
            )
        return f"""
<h2>交易日志</h2>
<table>
<thead>{header}</thead>
<tbody>
{chr(10).join(rows)}
</tbody>
</table>
{truncated_note}"""

    # ------------------------------------------------------------------
    # TEXT 生成
    # ------------------------------------------------------------------
    def _generate_text(
        self,
        result: dict,
        equity_curve: list[dict] | None,
        trade_log: list[dict] | None,
    ) -> str:
        """生成纯文本报告。"""
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append(f"回测报告 — {result.get('strategy_id', 'N/A')}")
        lines.append("=" * 60)
        lines.append(
            f"回测区间: {self._fmt_datetime(result.get('start_date'))} → {self._fmt_datetime(result.get('end_date'))}"
        )
        lines.append(f"生成时间: {self._fmt_datetime(result.get('timestamp'))}")
        benchmark = result.get("benchmark_symbol")
        lines.append(f"基准标的: {benchmark if benchmark else 'N/A'}")
        if result.get("overfitting_flag"):
            lines.append("⚠️ 过拟合警告: 该回测结果可能存在过拟合")
        lines.append("")
        lines.append("汇总指标:")
        lines.append(f"  年化收益:   {self._fmt_percent(result.get('annual_return'))}")
        lines.append(f"  总收益:     {self._fmt_percent(result.get('total_return'))}")
        lines.append(f"  Sharpe:     {self._fmt_float(result.get('sharpe_ratio'))}")
        lines.append(f"  最大回撤:   {self._fmt_percent(result.get('max_drawdown'))}")
        lines.append(f"  胜率:       {self._fmt_percent(result.get('win_rate'))}")
        lines.append(f"  交易次数:   {self._fmt_int(result.get('trades_count'))}")
        if equity_curve:
            lines.append(f"\n权益曲线: {len(equity_curve)} 个数据点")
        if trade_log:
            lines.append(f"交易日志: {len(trade_log)} 条交易")
        lines.append("=" * 60)
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 格式化辅助
    # ------------------------------------------------------------------
    @staticmethod
    def _fmt_percent(value: object) -> str:
        """格式化为百分比。"""
        if value is None:
            return "N/A"
        try:
            return f"{float(value) * 100:.2f}%"
        except (TypeError, ValueError):
            return "N/A"

    @staticmethod
    def _fmt_float(value: object) -> str:
        """格式化为浮点数。"""
        if value is None:
            return "N/A"
        try:
            return f"{float(value):.4f}"
        except (TypeError, ValueError):
            return "N/A"

    @staticmethod
    def _fmt_int(value: object) -> str:
        """格式化为整数。"""
        if value is None:
            return "N/A"
        try:
            return str(int(value))
        except (TypeError, ValueError):
            return "N/A"

    @staticmethod
    def _fmt_datetime(value: object) -> str:
        """格式化日期时间。"""
        if value is None:
            return "N/A"
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return str(value)
