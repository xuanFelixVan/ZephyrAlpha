---
module_id: MOD-RK-011
title: "回撤实时追踪器蓝图 — 峰值谷值+三级阈值告警"
doc_type: blueprint
status: Active
version: "0.1.3"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P0
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-RK-011 Drawdown Real-Time Tracker — 回撤实时追踪器 蓝图

> **module_id**: MOD-RK-011 | **域**: D_RISK | **层**: L02 盘中实时监控
> **优先级**: P0 | **成熟度**: L1 🔵 骨架 → production | **对标能力**: C-032●
> **SSoT**: depgraph MOD-RK-011 | **设计真源**: D:\临时工作区\依赖图\11-D-RISK-风控域.md §1 RK-11, §4 E-RK-03

## 1. 定位

回撤实时追踪器——盘中实时跟踪组合净值的最大回撤(峰值/谷值), 三级阈值告警,
回撤恢复检测, 资金曲线诊断。产出 E-RK-03 DrawdownAlerted 事件, EMERGENCY 级触发
RK-17 Kill Switch。

与 POS-007 的区别: POS-007 是*仓位上限联动*(回撤→降仓, 行动导向);
RK-11 是*实时告警*(回撤→分级告警, 监控导向)。RK-11 产出告警事件给前端/自治/报告域。

属 A 类基础设施(峰值谷值计算+阈值判定+恢复检测, 逻辑明确), 阈值为 C 类可调参数。
阈值默认值真源=alert_threshold_registry.yaml（THD-DRAWDOWN-001/002/003，fail-closed 统读，2026-08-17 AI-THD-001）；显式传参可覆盖。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 组合净值 (实时, 来自 D-EX-CORE / RK-03 监控) | — |
| 输出 | DrawdownSnapshot (峰值/谷值/回撤/级别/恢复状态) | 联动 RK-17 |
| 事件 | E-RK-03 DrawdownAlerted | → D-FRONTEND, D-AUTONOMY, D-REPORTING |

## 3. 核心规则 (设计真源 §1 RK-11, §4 E-RK-03)

### 3.1 三级阈值

| 回撤幅度 | 告警级别 | 说明 |
|----------|----------|------|
| 5% ~ 10% | WARNING | 提醒关注 |
| 10% ~ 15% | CRITICAL | 严重回撤 |
| > 15% | EMERGENCY | 触发 Kill Switch |

(< 5% 为 NONE, 无告警)

### 3.2 峰值谷值跟踪

- peak: 高水位 (单调非减, 仅在新高时上移)
- trough: 自最近峰值以来的最低点 (peak 上移时重置)
- drawdown = (net_value - peak) / peak (≤ 0)

### 3.3 回撤恢复检测

- in_recovery: 当净值从谷底回升但尚未创新高时标记
- 恢复完成: 净值回到/超过峰值 (创新高) → 告警级别降为 NONE, 发恢复事件

### 3.4 事件触发策略

- 仅在告警级别*变化*时发射 E-RK-03 (避免盘中高频刷屏)
- 恢复(降级)也算级别变化, 发射恢复事件

## 4. 关键不变量 (INVARIANTS)

- peak 单调非减; trough ≤ peak; drawdown ≤ 0
- 告警级别由当前回撤唯一决定 (无状态依赖, 除事件去抖)
- EMERGENCY 级必须触发 Kill Switch 评估 (由消费者 RK-17 执行)
- 事件去抖: 连续相同级别不重复发射

## 5. 错误契约

- `InvalidDrawdownInputError` (ZA-RK-0003): 净值非正

## 6. 测试

- `tests/risk/test_drawdown_tracker.py`
- 覆盖: 峰值谷值跟踪、三级阈值、恢复检测、事件去抖、EMERGENCY触发、边界值

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: RK-17 Kill Switch (EMERGENCY 触发), D-FRONTEND, D-AUTONOMY, D-REPORTING
- 数据源: D-EX-CORE 组合净值, RK-03 Portfolio Risk Monitor

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-011`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-011` 的 3 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-011` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-011 | MOD-RK-011 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 3 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/risk/core/__init__.py` | ✅ 已实现 | |
| `src/zephyr/risk/core/drawdown_tracker.py` | ✅ 已实现 | |
| `src/zephyr/risk/core/var_backtester.py` | ✅ 已实现 | |

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


