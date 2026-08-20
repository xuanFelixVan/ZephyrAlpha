---
module_id: MOD-RK-13
title: "拥挤度监控器蓝图 — 跨参与者因子拥挤度检测"
doc_type: blueprint
status: Active
version: "0.1.0"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-05"
last_updated: "2026-08-17"
blueprint_level: module
blueprint_id: MOD-RK-13
domain_id: D_RISK
path: src/zephyr/risk/core/crowding_monitor.py
design_maturity: production
build_status: stable
granularity: file
ai_autonomy: ai_modifiable
safety: L
stability: evolving
responsibility_domain: 
---

# MOD-RK-13 拥挤度监控器 (CrowdingMonitor)

## 1. 定位

D_RISK 域 A 类基础设施——跨参与者因子拥挤度检测。

与 MOD-RK-07 (concentration_monitor) 的区分:
- concentration_monitor: 组合内集中度 (HHI) — "我的组合多集中"
- crowding_monitor: 跨策略拥挤度 — "全市场多少人挤在同一因子上"

## 2. 输入/输出

| 方向 | 契约 | 类型 |
|------|------|------|
| 输入 | strategy_positions: {strategy_id: {symbol: weight}} | dict |
| 输入 | factor_exposures: {strategy_id: float} (可选) | dict |
| 输出 | CrowdingMetrics | frozen dataclass |

## 3. 核心规则

### 3.1 持仓重叠度 (Position Overlap)

加权和 Jaccard 变体:
```
overlap = Σ_min(w_s) / Σ_max(w_s)   for all symbols across strategies
```
- Σ_min: 每个标的在所有策略中的最小权重之和（交集）
- Σ_max: 每个标的在所有策略中的最大权重之和（并集）
- 范围 [0, 1]，1=所有策略持仓完全相同

### 3.2 方向一致性 (Direction Consensus)

```
consensus = |Σ sign(exposure_i)| / n_strategies
```
- 1.0 = 所有策略同方向（全部做多或全部做空）
- 0.0 = 完全对冲

### 3.3 拥挤度评分

```
crowding_score = 0.5 × overlap + 0.5 × consensus
is_crowded = crowding_score > threshold (默认 0.6)
```

## 4. 契约

| 契约ID | 方向 | 描述 |
|--------|------|------|
| CTR-P1-019 | 消费 | 策略持仓快照 |
| CTR-P1-020 | 生产 | CrowdingMetrics 拥挤度指标 |

## 5. 依赖

| 依赖 | 类型 | 用途 |
|------|------|------|
| zephyr.risk.risk_manager_base | import | RiskCheckResult 类型 |

## 6. 验收标准

- [x] 持仓重叠度计算正确（手工验证）
- [x] 方向一致性计算正确
- [x] 单元测试 ≥ 15 个
- [ ] 延迟 < 50ms（10 策略 × 100 标的）
- [ ] 接入编排器

## 7. 施工步骤

- S1: depgraph 登记 ✓
- S2: 五图对齐 ✓
- S3: 写代码（持仓重叠度 + 方向一致性 + 拥挤评分）
- S4: 测试
- S5: 状态转换 + 验收
- S6: 接入编排器

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-13`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-13` 的 5 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-13` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-13 | MOD-RK-13 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 5 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/core/test_crowding_monitor.py` | ✅ 已实现 | |
| `tests/risk/core/test_orchestrator_crowding_integration.py` | ✅ 已实现 | |

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
