---
module_id: MOD-POS-003
title: "仓位漂移监控器蓝图 — 两级阈值+三级监控频率"
doc_type: blueprint
status: Active
version: "0.1.3"
design_maturity: production
ttl: permanent
layer: L03_position
layer_name: position
functional_domain: position
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-POS-003 Position Drift Monitor — 仓位漂移监控器 蓝图

> **module_id**: MOD-POS-003 | **域**: D_POSITION | **层**: L03 仓位管理
> **优先级**: P0 | **成熟度**: L1 🔵 骨架 → production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-POS-003 | **设计真源**: D:\临时工作区\依赖图\07-D-POSITION-仓位管理域.md §1.1 POS-03, §4 E-POS-02

## 1. 定位

仓位漂移监控器——监控实际持仓权重与目标权重的偏离，超阈值产出 E-POS-02 DriftDetected 事件。
消费 SELL-00 持仓分级决定监控频率。

属 A 类基础设施(漂移计算+阈值判定+分级，逻辑明确)，阈值为 C 类可调参数。
依据: 07-D-POSITION §1.1 POS-03, §4 E-POS-02

## 2. 不变量 (INVARIANTS)

- **组合漂移 > ±2% 触发再平衡评估**: |实际总仓位 - 目标总仓位| > portfolio_threshold
- **单标的漂移 > ±3% 触发标的级评估**: |实际权重 - 目标权重| > symbol_threshold
- **漂移阈值可配置**: 默认设计值 2%/3%，C 类可调
- **三级监控频率**: WATCH(实时秒级) / MONITOR(5分钟级) / HOLD(仅重大事件)
- **事件可审计**: 每次超阈值产出 DriftDetectedEvent

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| InvalidDriftInputError | ZA-POS-0004 | 权重越界、标的集合不一致等输入非法 |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 消费 | MOD-POS-002 仓位状态机 | PositionState | 持仓状态影响监控频率 |
| 消费 | SELL-00 持仓分级 | TriageLevel | WATCH/MONITOR/HOLD 决定频率 |
| 产出 | MOD-POS-004 再平衡引擎 | E-POS-02 DriftDetected | 触发再平衡评估 |
| 产出 | D-GOVERNANCE | DriftDetectedEvent | 审计追溯 |

## 5. 关键数据模型

- **DriftScope**: PORTFOLIO (组合级) / SYMBOL (标的级)
- **TriageLevel**: WATCH (红/秒级) / MONITOR (黄/5min) / HOLD (绿/重大事件)
- **DriftAlert**: scope / symbol / drift_pct / threshold / triage_level
- **DriftResult**: alerts / max_drift / portfolio_drift / triage_level
- **E-POS-02 DriftDetectedEvent**: scope / symbol / drift / threshold / timestamp

## 6. 接口

```python
monitor = PositionDriftMonitor()
result = monitor.check(
    targets={"000001.SZ": 0.05, "600000.SH": 0.03},   # 目标权重
    actuals={"000001.SZ": 0.08, "600000.SH": 0.025},   # 实际权重
    triage_levels={"000001.SZ": TriageLevel.WATCH},     # 持仓分级
    now=t,
)
# result.alerts → [DriftAlert(scope=SYMBOL, symbol="000001.SZ", drift_pct=0.03, ...)]
```

可调参数 (DriftConfig):
- portfolio_drift_threshold=0.02 (组合 ±2%)
- symbol_drift_threshold=0.03 (单标的 ±3%)

## 7. 设计决策

| 决策 | 理由 |
|------|------|
| 两级阈值 (组合/标的) | 组合漂移影响整体再平衡，标的漂移影响单标的调整 |
| 三级监控频率 | 与 SELL-00 持仓分级对齐，资源按风险分配 |
| 阈值可配置 | 不同策略/市场状态阈值不同，C 类可调 |
| 只检测不执行 | 漂移监控是"发现者"，执行由 POS-004 再平衡引擎决定 |

## 8. 测试计划

- 组合漂移超阈值 → PORTFOLIO alert
- 单标的漂移超阈值 → SYMBOL alert
- 双级同时触发
- 三级监控频率映射 (WATCH/MONITOR/HOLD)
- 阈值可配置
- 输入校验 (权重越界/标的不一致抛错)
- 无漂移时不产出 alert

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-POS-003`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-POS-003` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-POS-003` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-POS-003 | MOD-POS-003 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 9. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 9.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 9.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §9（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


