---
module_id: MOD-RK-29
title: "流动性+相关性体制监控层蓝图 — 风险仪表盘快照与告警产出（C-004 ②监控层）MVP"
doc_type: blueprint
status: Active
version: "0.1.2"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P0
blueprint_level: module
blueprint_id: MOD-RK-29
domain_id: D_RISK
path: src/zephyr/risk/core/adaptive_risk_monitor.py
design_maturity: production
build_status: production
granularity: file
ai_autonomy: ai_modifiable
safety: M
stability: evolving
responsibility_domain: 
---

# MOD-RK-29 流动性+相关性体制监控层（Adaptive Risk Monitor）蓝图

> **module_id**: MOD-RK-29 | **域**: D_RISK | **层**: C-004 三层体系 ②监控层
> **优先级**: P0 | **来源**: CAND-RSK-035（B10-01217，AUD-DRAFT-001-DIGEST P0 波 W1c）

## 1. 定位

C-004 自适应风控三层体系的**②监控层能力底座**：盘中聚合两路风险体征——
- 流动性风险：非流动标的占比分级（复用 MOD-RK-08 LiquidityMonitor 产出的指标）
- 相关性体制：组合平均成对相关三档 regime（复用 MOD-POS-012 assess_correlation_regime）

产出**风险仪表盘快照**（RiskWatchSnapshot，供 CTR-P1-008 风险仪表盘消费）+
**告警数据**（MonitoringAlert，级别语义对齐 MOD-RK-06 AlertGenerator.AlertLevel；
发送接线由编排层/调用方完成，本模块不直接触达通道——MVP 边界）。

**底座复用裁定（W1c 同族整合）**：不重复实现 Amihud/萎缩比率/相关矩阵算法；
与 C-045 拥挤度（MOD-RK-13/MOD-RK-32）正交——本模块管"流动性+相关性体制"，
不管拥挤度响应。

## 2. 输入 / 输出

| 方向 | 内容 | 契约 |
|------|------|------|
| 输入 | LiquidityWatchInput 序列（标的级流动性指标）+ 收益矩阵（相关性，可空） | — |
| 输出 | RiskWatchSnapshot(illiquid_ratio/liquidity_level/correlation_regime/overall_severity/alerts/…) | frozen dataclass |

## 3. 核心规则

1. 流动性分级：illiquid_ratio ≥ illiquid_ratio_red → red 告警；≥ yellow → yellow 告警。
2. 相关性体制：regime=HIGH → orange 告警（分散失效预警，透传 MOD-POS-012 warnings）。
3. 综合严重度 = 各维度最严重档（normal < yellow < orange < red）。
4. 无相关性输入 → correlation_regime="NA"（不参与取严）。
5. 纯函数无 IO；Fail-Closed 配置/输入校验（InvalidRiskWatchConfigError /
   InvalidLiquidityWatchInputError）。

## 4. 依赖

| 依赖 | 模块 | 类型 |
|------|------|------|
| 流动性指标源 | MOD-RK-08 liquidity_monitor | import_depends（契约对齐） |
| 相关性体制 | MOD-POS-012 correlation_regime_monitor | import_depends |
| 告警级别语义 | MOD-RK-06 alert_generator | import_depends（AlertLevel 对齐） |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-29`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-29` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-29` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-29 | MOD-RK-29 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 5. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 5.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 5.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §5（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


