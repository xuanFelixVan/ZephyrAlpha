---
module_id: MOD-RK-23
title: "策略偏离监控器蓝图 — 实盘 vs 回测净值偏离双口径持续度量（55 号 G26 §3.4）"
doc_type: blueprint
status: Active
version: "0.1.20"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-15"
last_updated: "2026-08-15"
priority: P1
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-RK-23 Strategy Deviation Monitor — 策略偏离监控器 蓝图

> **module_id**: MOD-RK-23 | **域**: D_RISK | **层**: L02 风控
> **优先级**: P1 | **成熟度**: production | **设计真源**: 55_monitoring_review.md §3.4（G26 决策三）

## 1. 定位

D_RISK 域监控导向设施（drawdown_tracker 同族）——每日收盘后持续度量**实盘净值 vs 同期回测净值**的偏离度。

组装缺口（非从零实现）：decision_gate.monitor_backtest_live_deviation 提供 Sharpe 单口径阈值判定（30%/50%）但无编排调用方；PLV 规约管上线后短期验证；position_drift_monitor 管仓位内部漂移。"实盘 vs 回测"主线持续度量无执行体——本模块闭合该缺口，与 50 号（experiment_tracking 供基准）/54 号（归因供周复盘）正交。

## 2. 输入 / 输出

| 方向 | 契约 | 类型 |
|------|------|------|
| 输入 | live_returns / backtest_returns 日收益序列（尾部对齐） | Sequence[float] |
| 输入 | 阈值（THD-DEVIATION-001/002/003） | alert_threshold_registry.yaml（fail-closed） |
| 输入 | 回测基准（可选桥） | experiment_tracking run artifact nav_curve_experiment.csv |
| 输出 | DeviationVerdict（双口径+action 快照） | frozen dataclass |
| 输出 | DeviationAlertedEvent（仅级别变化发射） | frozen dataclass |

## 3. 核心规则

- 累计收益：cum = ∏(1+r) − 1（尾部对齐窗口）
- 相对偏差：|cum_live − cum_bt| / |cum_bt|；|cum_bt| < 1e-12 时 cum_live≈0 → 0.0，否则 inf（必触发 RETIRE）
- 日收益相关：Pearson；零方差序列 → None（无定义，不标注）
- action 分级（语义对齐 decision_gate）：deviation > 0.50 → RETIRE；> 0.30 → WARN；否则 OK
- correlation_below_floor（默认 0.5，注册表 pending_adjudication）只标注不升级 action——周报复盘"偏离与告警事件"段消费
- 样本不足（< min_samples=5）：sufficient_data=False 且 action=OK（只登记不判定）

## 4. 关键不变量 (INVARIANTS)

- 阈值唯一真源 = alert_threshold_registry.yaml（fail-closed，禁止码内第二真源兜底）
- 事件去抖 = 仅 action 级别变化时发射（首评 OK 不发射；降级也发射）
- 本模块永不写策略状态（监控只产出 verdict/event，退役评审归 strategy_retirement_evaluator）
- 基准供给桥失败一律降级 None（监控链路不阻断业务）

## 5. 错误契约

| 异常 | 触发 |
|------|------|
| InvalidDeviationInputError | 输入非数值/NaN/Inf/空序列/min_samples<2 |
| DeviationConfigError | 注册表缺失/畸形/缺条目/阈值非数值/warn≥retire |

## 6. 数据模型

- `DeviationVerdict`：strategy_id / evaluated_at / sample_size / sufficient_data / cum_return_live / cum_return_backtest / cum_relative_deviation / daily_return_correlation / correlation_below_floor / action / thresholds（快照）/ note
- `DeviationAlertedEvent`：strategy_id / previous_action / new_action / verdict / emitted_at
- `DeviationAction`：OK / WARN / RETIRE

## 7. API

- `StrategyDeviationMonitor(registry_path=None, min_samples=5)`
- `evaluate(strategy_id, live_returns, backtest_returns, now=None) -> DeviationVerdict`
- `on_deviation_alerted(listener)` / `get_latest_verdicts() -> dict[str, DeviationVerdict]`
- `load_backtest_returns_from_experiment(run_id, artifact_suffix="nav_curve_experiment.csv") -> list[float] | None`（staticmethod，lazy import）

## 8. 依赖

- zephyr.shared.io.paths（REPO_ROOT）/ PyYAML（注册表加载）
- zephyr.experiment_tracking.query（可选桥，lazy import，50 号基准供给）
- 消费方：MOD-RPT-009 ReviewOrchestrator（周复盘偏离段）

## 9. 测试

tests/risk/core/test_strategy_deviation_monitor.py——阈值加载/三档判定/双口径/事件去抖/边界（样本不足/零回测累计/零方差/尾部对齐/NaN 拒绝）/fail-closed/基准供给桥降级，44 项三件套全绿（2026-08-15）。

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。

### 10.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/core/test_deviation_attribution.py` | ✅ 已实现 | |
| `tests/risk/core/test_strategy_deviation_monitor.py` | ✅ 已实现 | |

### 10.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §10（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-23`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-23` 的 4 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-23` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-23 | MOD-RK-23 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 4 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
