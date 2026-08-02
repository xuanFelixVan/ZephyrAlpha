---
module_id: MOD-BT-019
title: "回测报告生成器蓝图 — HTML报告自动生成"
doc_type: blueprint
status: Active
version: "0.1.0"
design_maturity: production
build_status: stable
ttl: permanent
layer: L_BACKTEST
layer_name: backtest
functional_domain: backtest
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P2
blueprint_level: module
responsibility_domain: 
---

# MOD-BT-019 Report Generator — 回测报告生成器 蓝图

> **module_id**: MOD-BT-019 | **域**: D_BACKTEST | **层**: L_BACKTEST 回测引擎层
> **优先级**: P2 | **成熟度**: production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-BT-019 | **设计真源**: D:\临时工作区\依赖图\32-D-BACKTEST-回测引擎域.md §1 BT-19

## 1. 定位

回测报告生成器——将回测结果(BacktestResult)转换为结构化 HTML 报告。
包含汇总指标表、元数据、过拟合警告、可选的权益曲线 SVG 图和交易日志表。
纯标准库实现(无第三方依赖), 报告自包含(内联 CSS, 可离线打开)。

属 A 类基础设施(纯模板渲染+数据格式化, 逻辑明确), 格式为 C 类可调参数。
纯工具模块, 不依赖外部数据库, 数据由调用方传入。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 回测结果 dict (含 BacktestResult 标准字段) + 可选时序数据 | 来自 BT-02/09 回测引擎 |
| 输出 | HTML 报告字符串 (自包含, 可直接写入文件) | 供前端/归档/邮件消费 |

## 3. 报告结构

### 3.1 汇总指标表

| 指标 | 字段 | 格式 |
|------|------|------|
| 年化收益 | annual_return | 百分比 |
| 总收益 | total_return | 百分比 |
| Sharpe 比率 | sharpe_ratio | 2位小数 |
| 最大回撤 | max_drawdown | 百分比(负数) |
| 胜率 | win_rate | 百分比 |
| 交易次数 | trades_count | 整数 |

### 3.2 元数据

- 策略ID: strategy_id
- 回测区间: start_date → end_date
- 生成时间: timestamp
- 基准标的: benchmark_symbol (可选)

### 3.3 过拟合警告

- overfitting_flag = True 时显示红色警告框

### 3.4 可选内容

- 权益曲线: 内联 SVG 折线图 (需 equity_curve 数据)
- 交易日志: HTML 表格 (需 trade_log 数据, 最多展示前 N 条)

## 4. 关键不变量 (INVARIANTS)

- ReportConfig / ReportResult 为 frozen dataclass (不可变)
- 输入为 dict, 不强制依赖 BacktestResult 类 (松耦合)
- HTML 报告自包含: 内联 CSS, 无外部依赖, 可离线打开
- 缺失字段 → 显示 "N/A" (不报错)
- 空 equity_curve → 不渲染 SVG 区块
- 空 trade_log → 不渲染交易日志区块
- 报告编码 UTF-8

## 5. 错误契约

- `ReportError` (ZA-BT-0019): 输入非 dict / 缺少 strategy_id

## 6. 数据模型

```python
class ReportFormat(str, Enum):
    HTML = "html"
    TEXT = "text"

@dataclass(frozen=True)
class ReportConfig:
    format: ReportFormat = ReportFormat.HTML
    include_equity_curve: bool = True
    include_trade_log: bool = True
    max_trades_display: int = 50
    chart_width: int = 800
    chart_height: int = 300
```

## 7. API

```python
class BacktestReportGenerator:
    def __init__(self, config: ReportConfig | None = None) -> None: ...
    def generate(self, result: dict, equity_curve: list[dict] | None = None,
                 trade_log: list[dict] | None = None) -> str: ...
    @staticmethod
    def save_report(content: str, path: str | Path) -> Path: ...
```

## 8. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 标准库: `html`, `datetime`, `pathlib`
- 消费者: 前端归档 / 邮件分发 / 人工审查

## 9. 测试

- `tests/backtest/test_report_generator.py`
- 覆盖: 基本HTML生成、指标格式化、缺失字段N/A、过拟合警告、
  权益曲线SVG渲染、交易日志表格、空数据处理、TEXT格式、
  save_report文件写入、配置自定义、frozen不可变
