---
module_id: MOD-POS-007
title: "资金曲线管理器蓝图 — 回撤分级动态调仓上限"
doc_type: blueprint
status: Active
version: "0.1.1"
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

# MOD-POS-007 Capital Curve Manager — 资金曲线管理器 蓝图

> **module_id**: MOD-POS-007 | **域**: D_POSITION | **层**: L03 仓位管理
> **优先级**: P0 | **成熟度**: L1 🔵 骨架 → production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-POS-007 | **设计真源**: D:\临时工作区\依赖图\07-D-POSITION-仓位管理域.md §1.3 POS-07

## 1. 定位

资金曲线管理器——跟踪已实现盈亏驱动的净值曲线, 根据回撤分级动态调整仓位上限,
并在盈利期扩张、亏损期收缩资金基础。产出 E-POS-04 CapitalCurveUpdated 事件,
联动 POS-01 仓位上限引擎。

属 A 类基础设施(回撤计算+分级+缩放系数, 逻辑明确), 阈值与扩张步长为 C 类可调参数。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 已实现盈亏 / 当前净值 | 来自 D-EX-CORE 成交回报 |
| 输出 | CapitalCurveSnapshot (仓位上限+缩放系数+回撤分级) | 联动 POS-01 |
| 事件 | E-POS-04 CapitalCurveUpdated | → D-RISK, D-PF-CORE, D-POS-01 |

## 3. 核心规则 (设计真源 §1.3 POS-07)

### 3.1 回撤分级 → 仓位上限

| 回撤幅度 | 级别 | 仓位上限 | 仅防御 |
|----------|------|----------|--------|
| < 5% | NORMAL | 100% | 否 |
| 5% ~ 10% | WARNING | 80% | 否 |
| 10% ~ 15% | CRITICAL | 50% | 否 |
| > 15% | EMERGENCY | 30% | 是(禁止新开仓) |

### 3.2 盈利扩张

- 每次净值创新高 → 资金基础扩张 +5% (复利累计)
- 最大不超过框架硬上限 (默认 2.0x 初始本金)

### 3.3 亏损收缩

- 回撤 > 5% → 缩减 10% (contraction = 0.9)
- 回撤 > 10% → 缩减 20% (contraction = 0.8)

### 3.4 恢复条件

- 净值回到回撤前高点 → 解除收缩, 保留已累计的扩张因子

### 3.5 本金=当前净值

- 仓位 sizing 的本金基准 = 当前净值 (天然复利)

## 4. 关键不变量 (INVARIANTS)

- 回撤 = (net_value - peak) / peak, 恒 ≤ 0
- peak 单调非减 (只在新高时上移)
- position_cap 仅由 drawdown_level 决定, 不可被盈利扩张放大
- EMERGENCY 级 defensive_only=True, 禁止新开仓
- capital_curve_discount 受框架硬上限封顶

## 5. 错误契约

- `InvalidCapitalCurveInputError` (ZA-POS-0005): 净值非正、盈亏快照非法

## 6. 测试

- `tests/position/test_capital_curve_manager.py`
- 覆盖: 四级回撤分级、盈利扩张复利+封顶、亏损收缩、恢复解除、事件触发、边界值

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: MOD-POS-001 (Position Sizing Engine), MOD-POS-008 (Drawdown Controller)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-POS-007`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-POS-007` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-POS-007` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-POS-007 | MOD-POS-007 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 8.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §8（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
