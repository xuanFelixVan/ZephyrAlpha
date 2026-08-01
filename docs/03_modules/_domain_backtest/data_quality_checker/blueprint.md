---
module_id: MOD-BT-022
title: "回测数据质量检查器蓝图 — 缺失检测+异常检测+一致性检查"
doc_type: blueprint
status: Active
version: "0.1.0"
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

# MOD-BT-022 Data Quality Checker — 回测数据质量检查器 蓝图

> **module_id**: MOD-BT-022 | **域**: D_BACKTEST | **层**: L_BACKTEST 回测引擎层
> **优先级**: P2 | **成熟度**: L1 🔵 骨架 → production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-BT-022 | **设计真源**: D:\临时工作区\依赖图\32-D-BACKTEST-回测引擎域.md §1 BT-22 + blueprint.md §5.1 L697

## 1. 定位

回测数据质量检查器——回测前/后对 OHLCV 数据执行质量检查, 输出结构化质量报告。
覆盖三大维度: 缺失检测(NaN/交易日gaps) + 异常检测(价格/成交量/OHLC逻辑) + 一致性检查(前复权连续性)。

属 A 类基础设施(纯 pandas 检查+阈值判定+报告生成, 逻辑明确), 阈值为 C 类可调参数。
纯工具模块, 不依赖外部数据库, 数据由调用方传入。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | OHLCV DataFrame (MultiIndex [symbol, date] 或单标的) + 检查配置 | 来自 BT-06 data_handler 或直接传入 |
| 输出 | DataQualityReport (问题列表+严重度+pass/fail+统计) | 供 BT-17 scheduler / BT-21 param_analyzer 消费 |

## 3. 核心规则 (设计真源 §1 BT-22, blueprint.md L697 P1-13)

### 3.1 缺失检测 (Missing)

| 检查项 | 规则 | 严重度 |
|--------|------|--------|
| NaN 字段 | open/high/low/close/volume 含 NaN | ERROR (close/volume) / WARN (open/high/low) |
| 交易日 gaps | 按交易日历检测缺失日期 (非周末/非节假日) | WARN |
| 时间戳不连续 | 相邻 bar 时间间隔异常 | WARN |

### 3.2 异常检测 (Anomaly)

| 检查项 | 规则 | 严重度 |
|--------|------|--------|
| 单日涨跌幅异常 | abs(pct_change) > price_anomaly_threshold (默认 0.20) | WARN |
| 零成交量 | volume == 0 (非停牌) | WARN |
| 异常放量 | volume > mean × volume_spike_multiplier (默认 10) | WARN |
| 负值检测 | open/high/low/close/volume < 0 | ERROR |
| OHLC 逻辑违背 | high < low / high < open / high < close / low > open / low > close | ERROR |

### 3.3 一致性检查 (Consistency)

| 检查项 | 规则 | 严重度 |
|--------|------|--------|
| 前复权连续性 | 相邻 bar 收盘价跳变 > 阈值 (排除涨跌停) | WARN |

### 3.4 严重度分级

- **ERROR**: 必须修复 (负值/OHLC逻辑违背/close缺失) → report.passed = False
- **WARN**: 建议检查 (异常波动/少量缺失/gaps) → 记入 report.warnings
- **INFO**: 提示信息 → 记入 report.info

## 4. 关键不变量 (INVARIANTS)

- 纯 pandas/numpy 操作, 不依赖外部数据库 (数据由调用方传入)
- 检查不修改输入数据 (只读)
- report.passed = (无 ERROR 级问题)
- 单标的与多标的 (MultiIndex) 均支持
- 空 DataFrame → 返回 passed=True 的空报告 (不报错)

## 5. 错误契约

- `InvalidDataFormatError` (ZA-BT-0022): 输入非 DataFrame / 缺少必需列

## 6. 测试

- `tests/backtest/test_data_quality_checker.py`
- 覆盖: NaN检测(各字段)、交易日gaps、价格异常、零成交量、异常放量、负值、OHLC逻辑违背、前复权连续性、多标的、空DataFrame、输入校验、严重度聚合

## 7. 依赖

- `pandas`, `numpy` (数据处理)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 可选消费: MOD-BT-006 data_handler (数据来源)
- 消费者: MOD-BT-017 scheduler (回测前质量门禁) / MOD-BT-021 param_analyzer
