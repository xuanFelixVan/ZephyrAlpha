---
module_id: MOD-PF-007
title: "绩效归因引擎蓝图 — Brinson 三因子 + 因子/风险归因 + 降级检测"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
layer: L02_portfolio_core
layer_name: portfolio_core
functional_domain: portfolio_core
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

# MOD-PF-007 Performance Attribution Engine — 绩效归因引擎 蓝图

> **module_id**: MOD-PF-007 | **域**: D_PF_CORE | **层**: L02 组合构建核心
> **优先级**: P0 | **成熟度**: design | **SSoT**: depgraph node 7820845
> **设计真源**: D:\临时工作区\依赖图\12-D-PF-CORE-组合构建域.md §1.2 PC-10

## 1. 定位

绩效归因引擎——Brinson 三因子分解 + 因子/风险归因 + 策略降级检测:
- Brinson 三因子: 配置效应 + 选择效应 + 交互效应
- 因子归因: 各因子对组合收益的贡献分解
- 风险归因: 复用 MOD-RK-16 RiskDecomposer 分解风险来源
- 策略降级检测: IC 衰减 >50% → 权重归 0; 拥挤检测 ρ>0.8/0.9
- 实现 AttributionEngineBase OCP 契约 (D_REPORTING 可替换 DefaultAttributionEngine)

属 A 类基础设施(数学归因模型, 无策略决策), 归因结果供 D_REPORTING 消费。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | portfolio_id + period + 持仓历史 + 因子收益 | CTR-006 (PositionSnapshot) |
| 输出 | PerformanceAttributionReport | CTR-P1-009 |
| 依赖 | RiskDecomposer(MOD-RK-16) | import_depends |
| 依赖 | StrategyCorrelationGate(MOD-PA-004) | import_depends |
| 依赖 | PerformanceAttributionReport(CTR-P1-009) | contract |

## 3. 核心规则

### 3.1 Brinson 三因子分解

```
total_return = allocation_effect + selection_effect + interaction_effect

allocation_effect = Σ (w_p,i - w_b,i) × r_b,i    (配置效应)
selection_effect  = Σ w_b,i × (r_p,i - r_b,i)     (选择效应)
interaction_effect = Σ (w_p,i - w_b,i) × (r_p,i - r_b,i)  (交互效应)
```

- w_p,i: 组合中行业 i 权重, w_b,i: 基准中行业 i 权重
- r_p,i: 组合中行业 i 收益, r_b,i: 基准中行业 i 收益

### 3.2 因子归因

- 分解各因子(factor_id)对组合超额收益的贡献
- factor_contribution[i] = exposure_i × factor_return_i
- 汇总为 factor_contributions: Dict[str, float]

### 3.3 风险归因 (复用 MOD-RK-16)

- 调用 RiskDecomposer.decompose() 获取风险来源分解
- 输出: 系统性风险 vs idiosyncratic 风险占比
- 因子风险贡献: 各 Barra 因子的风险贡献

### 3.4 策略降级检测

| 检测项 | 阈值 | 动作 |
|--------|------|------|
| IC 衰减 | >50% (近期 IC / 历史均值) | 权重归 0 + 标记降级 |
| 策略拥挤 | ρ>0.8 | 权重减半 |
| 策略拥挤 | ρ>0.9 | 仅保留 IC 最高策略 |

- 降级检测结果附加在 PerformanceAttributionReport 的扩展字段

## 4. 关键不变量 (INVARIANTS)

- total_return = allocation + selection + interaction (守恒)
- factor_contributions 各值之和 ≈ selection_effect (因子归因解释选择效应)
- 降级检测不修改组合权重(仅标记建议, 由 PC-01 执行)
- 实现 AttributionEngineBase OCP 契约 (可被 D_REPORTING 替换)
- 交易成本拖累 transaction_cost_drag ≥ 0

## 5. 错误契约

- `AttributionDataIncompleteError`: 持仓历史/因子收益缺失
- `RiskDecompositionUnavailable`: RK-16 不可用(降级为跳过风险归因)
- `ICDecayDetectionError`: IC 数据不足(降级为跳过降级检测)

## 6. 测试

- `tests/pf_core/test_performance_attribution_engine.py`
- 覆盖: Brinson 三因子守恒、因子归因分解、风险归因(RK-16 复用)、IC 衰减降级、拥挤检测、OCP 契约实现、退化场景(空持仓/单标的)、幂等性

## 7. 依赖

- `zephyr.reporting.analytics_base` (AttributionEngineBase, OCP 契约)
- `zephyr.risk.core.risk_decomposition` (MOD-RK-16, 风险归因复用)
- `zephyr.pf_alloc.core.strategy_correlation_gate` (MOD-PA-004, 拥挤检测复用)
- `zephyr.shared.contracts.performance_attribution_report` (CTR-P1-009, 输出契约)
- 消费者: D_REPORTING (归因报告消费), D_GOV_ENFORCEMENT (降级检测审计)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-PF-007`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-PF-007` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-PF-007` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-PF-007 | MOD-PF-007 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
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
