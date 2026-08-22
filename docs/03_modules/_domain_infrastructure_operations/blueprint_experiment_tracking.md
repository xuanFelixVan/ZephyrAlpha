---
module_id: MOD-OBS-001
submodule_path: src/zephyr/experiment_tracking
title: "Experiment Tracking 蓝图 — 单一 JSON 后端实验跟踪（MLflow 已退役）"
doc_type: blueprint
status: Active
version: "0.2.0"
layer: L0_infrastructure
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-08-07"
valid_from: "2026-08-07"
ttl: permanent
actual_disk_path: "src/zephyr/experiment_tracking/"
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
summary: "ZephyrAlpha 实验跟踪——单一 JSON 后端（FallbackBackend；enable_tracking=False→NullBackend no-op；MLflow 已于 2026-08-16 退役卸载）。所有零件（C1 / regime_detector / 特征管道 / 回测引擎 / 全链路）的运行统一记录到本地 JSON（logs/experiment_tracking_fallback/），人和 AI 通过 query 接口或 Panel「实验历史」Tab 查询、对比、追溯。M1 阶段：core tracker + c1_adapter + track 开关；M2 阶段（51 号）：MLflow 退役 + Panel 实验历史 Tab。"
tags: [experiment_tracking, json_backend, observability, c1-validation, regime-validation, fallback, panel, telemetry, infrastructure]
priority: P2
runtime_plane: cold
depends_on:
  - {target: "MOD-MASTER_BLUEPRINT", at: "全篇", why: "父蓝图——基础设施层归属"}
  - {target: "MOD-BT-001", at: "M1-3 c1_adapter", why: "C1 对比结果→tracking 适配器消费 C1ComparisonResult（TYPE_CHECKING 隔离，运行时鸭子类型）"}
references:
  - {id: "#ARCH-REGIME-DEADZONE-001", at: "全篇", why: "死区装饰器否决——实验跟踪记录 C1 验证结果"}
  - {id: "#ARCH-OBS-EXP-TRACK-001", at: "全篇", why: "可观测性架构决策——实验跟踪是可观测性子域"}
  - {id: "#ARCH-REGIME-C1-RUNNER-001", at: "M1-5", why: "c1_runner track 开关消费本蓝图 c1_adapter"}
ssot_claims:
  - claim: "实验跟踪统一入口唯一真源"
    scope: "src/zephyr/experiment_tracking/"
  - claim: "C1 结果→JSON 语义适配唯一真源"
    scope: "src/zephyr/experiment_tracking/adapters/c1_adapter.py"
last_updated: "2026-08-16"
last_verified: "2026-08-16"
codification_level: L3
codification_at: "2026-08-07"
generation: 1
functional_domain: operations
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
build_status: stable
design_maturity: production
responsibility_domain: 
---

# Experiment Tracking 蓝图 — 单一 JSON 后端实验跟踪（MLflow 已退役）

> module_id: MOD-OBS-001 | version: 0.2.0 | status: Active | layer: L0_infrastructure
> actual_disk_path: src/zephyr/experiment_tracking/ | generation: 1 | construction_progress: M1 完成 + M2 完成（51 号：MLflow 退役 + Panel 实验历史 Tab，2026-08-16）

## 概述

本蓝图描述 ZephyrAlpha 实验跟踪层——所有"零件"（C1 / regime_detector / 特征管道 / 回测引擎 /
全链路）的运行统一记录到本地 JSON（`logs/experiment_tracking_fallback/`），人和 AI 都能通过
`experiment_tracking.query` 接口或 Panel「实验历史」Tab 查询、对比、追溯历史实验。

**MLflow 退役（2026-08-16，51 号工作流 A）**：`_MLflowBackend` 类、query.py mlflow 分支、
config.py `tracking_uri`/`experiment_prefix` 字段已全部删除，`pip uninstall mlflow` 已执行。
退役根因：MLflow UI 是外部 UI（违反"集成新功能到现有 frontend"偏好），全量包依赖对单人
项目过重，pyproject 从未真正声明（51 号 §二.2）。

**命名说明**：包名 `experiment_tracking`（非 `observability`）——项目里 observability 是横切概念
（infrastructure/shared/security 各有 observability 子域），实验跟踪独占顶层 observability 会语义
混淆。详见 11_regime_backtest_validation_plan §2.3 命名冲突发现 + §9 决策 A。

**后端机制**（核心设计）：两 backend 自动选择，业务零感知——
  - `enable_tracking=False`（`ZEPHYR_EXPERIMENT_TRACKING=0`）→ `_NullBackend`（no-op，全局关闭）
  - 否则 → `FallbackBackend`（写 `logs/experiment_tracking_fallback/{component}/{run_id}/run_meta.json`）
  - 所有 `log_*` 调用包 try/except，失败只记 stderr 不抛——**tracking 失败绝不崩业务回测**

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint_construction_template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint_construction_template.md)

## M1 阶段范围（已完成）

| 子任务 | 文件 | 说明 |
|--------|------|------|
| M1-1 core | `experiment_tracker.py` | ExperimentTracker 主类 + RunContext + 三 backend + 单例工厂 |
| M1-2 fallback | `fallback_tracker.py` | FallbackBackend（JSON 降级，同接口） |
| M1-2 config | `config.py` | ExperimentTrackingConfig（不可变，环境变量覆盖） |
| M1-2 models | `models.py` | RunSummary / RunDetail（屏蔽双源差异） |
| M1-2 query | `query.py` | list_runs / get_run / compare_runs（屏蔽 mlflow vs JSON） |
| M1-3 c1_adapter | `adapters/c1_adapter.py` | C1ComparisonResult → mlflow run（params/metrics/artifacts/tags） |
| M1-5 track 开关 | `backtest/regime_validation/c1_runner.py` | `track=True` 时 lazy import c1_adapter 自动记录 |
| M1-7 测试 | `tests/experiment_tracking/` | test_experiment_tracker + test_c1_adapter（桩） |
| M1-8 治理登记 | 本蓝图 + 3 registry + depgraph + ARCH | 6 条 plain_zh + capability + ARCH-OBS-EXP-TRACK-001 |

## Zephyr 语义 → MLflow 映射

| Zephyr 语义 | MLflow 概念 | 说明 |
|-------------|-------------|------|
| component（零件类型） | experiment 名（`zephyr-{component}`） | 如 `zephyr-c1-validation` |
| 一次运行 | run（`run_name={component}_{mode}_{timestamp}`） | |
| 指标 | metrics（`baseline_`/`experiment_` 前缀） | 如 `baseline_sharpe` / `experiment_maxdd` |
| 配置 | params | C1 门槛 / 模式 / 策略名 / 数据日期范围 |
| 产物 | artifacts（nav CSV / report MD / ...） | `nav_curve_baseline.csv` / `c1_summary.md` |
| 语义标签 | tags | `component` / `mode` / `passed` / `veto_reason` |

## 文件清单（6 核心文件）

| 文件 | 职责 | 关键符号 |
|------|------|----------|
| `__init__.py` | 包入口（re-export 公共 API） | ExperimentTracker / get_tracker / RunContext / ... |
| `config.py` | 配置（不可变 dataclass + 环境变量覆盖） | ExperimentTrackingConfig / load_config |
| `models.py` | 数据模型（屏蔽双源差异） | RunSummary / RunDetail |
| `experiment_tracker.py` | 跟踪器主类（三 backend + 单例） | ExperimentTracker / RunContext / get_tracker / reset_tracker |
| `fallback_tracker.py` | 降级 backend（JSON 实现） | FallbackBackend |
| `query.py` | 查询接口（屏蔽 mlflow vs JSON） | list_runs / get_run / compare_runs |
| `adapters/c1_adapter.py` | C1 结果适配器（M1-3） | track_c1_result |
| `adapters/__init__.py` | 适配器包入口 | __all__ = ["c1_adapter"] |

## M3 adapter 契约（后续阶段）

各 adapter 把领域对象 → MLflow 语义，核心 tracker 零件无关：

| adapter | 领域对象 | 触发点 | 阶段 |
|---------|----------|--------|------|
| c1_adapter | C1ComparisonResult | c1_runner track=True | **M1-3（已完成）** |
| regime_adapter | RegimeDetectionResult | regime orchestrator | M3 |
| feature_adapter | FeaturePipelineResult | feature builder | M3 |
| backtest_adapter | BacktestResult | backtest engine | M3 |
| full_chain_adapter | FullChainResult | 全链路编排 | M3 |

adapter 契约统一：`track_xxx_result(result, *, ...args, extra_tags=None) -> str`（返回 run_id）。
循环依赖规避：领域类型仅 `TYPE_CHECKING` 导入，运行时全鸭子类型；调用方 lazy import adapter。

## INVARIANTS

1. **lazy import mlflow**——模块加载时不拉入 mlflow，仅 `start_run` 时按需 import
2. **三 backend 同接口**——`_MLflowBackend` / `FallbackBackend` / `_NullBackend` 实现相同方法签名
3. **tracking 失败不崩业务**——所有 `log_*` 包 try/except，失败只记 stderr 不抛
4. **RunContext 不吞异常**——业务异常正常传播（`__exit__` return False），仅 tracking 调用吞错
5. **配置不可变**——`ExperimentTrackingConfig` 为 frozen dataclass
6. **数据模型不可变**——`RunSummary` / `RunDetail` 为 frozen dataclass，屏蔽 mlflow vs JSON 差异
7. **enable_tracking=False → 全局 no-op**——`_NullBackend` 所有方法空实现，run_id="null-run"
8. **循环依赖规避**——adapter 领域类型仅 TYPE_CHECKING，运行时鸭子类型；调用方 lazy import

## ERROR_CONTRACT

| 错误场景 | 处理 | error_code |
|----------|------|------------|
| tracking 调用失败 | stderr warning 不抛（不崩业务） | — |
| RunContext 内业务异常 | 正常传播（不吞） | — |
| mlflow 未装 | 降级 FallbackBackend（JSON） | — |
| mlflow 初始化失败 | 降级 FallbackBackend（JSON） | — |
| 查询失败 | 返回空列表/None 不抛 | — |
| 单 run JSON 解析失败 | 跳过该 run | — |

## 降级路径

```
enable_tracking=False ──► _NullBackend (no-op, run_id="null-run")
        │
        ▼ true
mlflow 可用？ ──no──► FallbackBackend (JSON: logs/experiment_tracking_fallback/)
        │
        ▼ yes
_MLflowBackend (SQLite: logs/mlflow.db, mlflow ui 可查)
        │
        ▼ 初始化失败
FallbackBackend (JSON 降级)
```

## 依赖方向

```
backtest.regime_validation.c1_runner ──(track=True, lazy import)──► experiment_tracking.adapters.c1_adapter
                                                                          │
                                                                          ▼
                                                                   experiment_tracking.experiment_tracker
                                                                          │ (TYPE_CHECKING only)
                                                                   backtest.regime_validation.c1_comparator
```

循环依赖规避：`c1_runner`（backtest 域）在 `track=True` 时 lazy import `c1_adapter`；
`c1_adapter` 需引用 `C1ComparisonResult`/`C1ShrinkageComparator`（backtest 域）类型——仅
`TYPE_CHECKING` 下导入（静态检查用），运行时全鸭子类型（属性访问）。故 runtime 无 backtest→
experiment_tracking→backtest 包级循环。

## 测试

| 测试文件 | 覆盖 |
|----------|------|
| `tests/experiment_tracking/test_experiment_tracker.py` | 三 backend 选择 / RunContext 语义 / 单例 / 降级 / 配置 |
| `tests/experiment_tracking/test_c1_adapter.py` | track_c1_result 完整流程 / params/metrics/artifacts 提取 / comparator=None 跳过 nav |
| `.runtime/_smoke_c1_track.py` | 端到端冒烟：run_c1_mock(track=True) 产出 run + track=False 向后兼容 |

## 治理登记

- **module_id**: MOD-OBS-001
- **domain**: D_INFRA_TELEMETRY
- **depgraph**: 设计态节点 path=`src/zephyr/experiment_tracking/` granularity=directory
- **plain_zh**: 6 条（config / models / experiment_tracker / fallback_tracker / query / c1_adapter）
- **capability**: experiment_tracking（capability_canonical_file_registry.yaml）
- **ARCH**: #ARCH-OBS-EXP-TRACK-001（architecture_issue_registry.yaml）

依据: 11_regime_backtest_validation_plan §3 ② + backtest_observability_mlflow_plan.md M1
SSoT: depgraph MOD-OBS-001
Version: 0.1.0

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-OBS-001`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-OBS-001` 的 18 个 file 节点 | production | `extract_depgraph.py --modules MOD-OBS-001` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-OBS-001 | MOD-OBS-001 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 18 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
