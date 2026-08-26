---
module_id: MOD-BT-023
title: "回测异常诊断器蓝图 — 结果异常诊断+修复建议"
doc_type: blueprint
status: Active
version: "0.1.2"
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

# MOD-BT-023 Anomaly Diagnoser — 回测异常诊断器 蓝图

> **module_id**: MOD-BT-023 | **域**: D_BACKTEST | **层**: L_BACKTEST 回测引擎层
> **优先级**: P2 | **成熟度**: production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-BT-023 | **设计真源**: D:\临时工作区\依赖图\32-D-BACKTEST-回测引擎域.md §1 BT-23

## 1. 定位

回测异常诊断器——对回测结果指标执行异常检测, 输出诊断报告+修复建议。
覆盖性能异常(高Sharpe/高胜率/深回撤)、统计异常(交易不足/周期过短)、
一致性异常(高收益低Sharpe/负收益), 每条异常附带可操作修复建议。

属 A 类基础设施(纯阈值判定+报告生成, 逻辑明确), 阈值为 C 类可调参数。
纯工具模块, 不依赖外部数据库, 数据由调用方传入。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 回测结果 dict (含 BacktestResult 标准字段) | 来自 BT-02/09 回测引擎 |
| 输出 | DiagnosisReport (异常列表+严重度+pass/fail+修复建议) | 供人工审查 / BT-19 报告生成 |

## 3. 异常规则

### 3.1 性能异常

| 规则 | 条件 | 严重度 | 修复建议 |
|------|------|--------|---------|
| high_sharpe | sharpe > 3.0 | WARN | 检查过拟合: Walk-Forward + OOS验证 |
| high_win_rate | win_rate > 80% | WARN | 检查前瞻偏差: PIT铁律 + 截断重算 |
| deep_drawdown | max_dd < -50% | ERROR | 降低仓位/增加止损/分散标的 |
| negative_return | annual_return < 0 | WARN | 策略不盈利, 检查逻辑或市场适配 |

### 3.2 统计异常

| 规则 | 条件 | 严重度 | 修复建议 |
|------|------|--------|---------|
| few_trades | trades < 30 | WARN | 增加回测周期或降低交易频率阈值 |
| short_period | 天数 < 252 | WARN | 至少覆盖1年完整交易日 |

### 3.3 一致性异常

| 规则 | 条件 | 严重度 | 修复建议 |
|------|------|--------|---------|
| high_return_low_sharpe | return>20% 且 sharpe<0.5 | WARN | 收益不稳定, 检查波动率 |
| missing_benchmark | benchmark=None | INFO | 添加基准便于相对绩效评估 |

## 4. 关键不变量 (INVARIANTS)

- AnomalyConfig / Anomaly / DiagnosisReport 为 frozen dataclass (不可变)
- report.passed = (无 ERROR 级异常)
- 缺失字段 → 跳过对应检查 (不报错)
- 空结果 → 返回 passed=True 的空报告
- 纯阈值判定, 不修改输入

## 5. 错误契约

- `DiagnosisError` (ZA-BT-0023): 输入非 dict / 缺少 strategy_id

## 6. 测试

- `tests/backtest/test_anomaly_diagnoser.py`
- 覆盖: 各异常规则触发/不触发、严重度分级、修复建议、缺失字段跳过、
  空结果、passed判定、配置自定义、frozen不可变

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-BT-023`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-BT-023` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-BT-023` |
| 数据流图 (dataflow) | 1 个 Dataset / 2 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-BT-023 | MOD-BT-023 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 7. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 7.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/backtest/services/anomaly_diagnoser.py` | ✅ 已实现 | |

### 7.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/backtest/test_anomaly_diagnoser.py` | ✅ 已实现 | |

### 7.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §7（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


