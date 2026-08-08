---
module_id: MOD-EX_SOR_EXT-002
submodule_path: src/zephyr/ex_sor/services/execution_quality_scorer.py
title: "执行质量评分器蓝图 — 四维评分+加权汇总+评定"
doc_type: blueprint
status: Active
version: "0.1.1"
design_maturity: production
build_status: stable
ttl: permanent
layer: L2_domain
layer_name: execution_routing
functional_domain: execution
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P2
blueprint_level: module
responsibility_domain: 
---

# MOD-EX_SOR_EXT-002 Execution Quality Scorer — 执行质量评分器 蓝图

> **module_id**: MOD-EX_SOR_EXT-002 | **域**: D_EX_SOR | **层**: L2 执行路由
> **优先级**: P2 | **成熟度**: production | **建设标记**: ✅可建(①) | **设计标签**: XS-EXT-02
> **SSoT**: depgraph MOD-EX_SOR_EXT-002 | **设计真源**: D:\临时工作区\依赖图\09-D-EX-SOR-执行路由域.md §2.1 XS-EXT-02 + §140 执行质量评分
> **代码**: src/zephyr/ex_sor/services/execution_quality_scorer.py | **测试**: tests/ex_sor/test_execution_quality_scorer.py

## 1. 定位

执行质量评分器——从执行结果提取四维度指标（价格/时间/成本/市场影响），各维度归一化到 [0,1] 评分，加权求和得总体评分与评定（good/acceptable/poor）。

大白话：一笔订单执行得好不好，不能只看一个方面。本模块从四个角度打分——价格（滑点大不大）、时间（执行快不快）、成本（总费用高不高）、冲击（对市场影响大不大），每项 0~1 分，加权汇总后给出"好/及格/差"的总评。是 EXT-001 滑点分析和 EXT-003 成本分析的下游聚合器。

属 D-EX-SOR §2.1 补充子模块，P2 优先级，①可建。纯计算模块。**EXT 三件套的聚合层**——消费 EXT-001 的 SlippageResult 和 EXT-003 的 TransactionCostResult。

## 2. 输入 / 输出

| 方向 | 内容 |
|------|------|
| 输入 | 订单元信息 + 四维原始指标(slippage_bps / duration_seconds / total_cost_bps / impact_bps，至少一个) |
| 输出 | ExecutionQualityResult（总体评分[0,1] + 评定 + 各维度评分 + 权重） |

支持两种入口：
- `score()`：直接传原始指标
- `score_from_results()`：从 EXT-001/EXT-003 结果对象提取指标后评分

## 3. 核心设计

### 3.1 四维度评分模型

每个维度：`score = max(0, 1 - raw_value / threshold)`（raw 越小越好，达到 threshold 得 0 分）

| 维度 | QualityDimension | 含义 | 默认最差阈值 | 评分公式 |
|------|-----------------|------|------------|---------|
| 价格 | PRICE | 滑点越小越好 | 50 bps | max(0, 1 - |slippage_bps| / 50) |
| 时间 | TIME | 执行越快越好 | 300 秒 | max(0, 1 - duration / 300) |
| 成本 | COST | 总成本越低越好 | 30 bps | max(0, 1 - |cost_bps| / 30) |
| 影响 | IMPACT | 冲击越小越好 | 20 bps | max(0, 1 - |impact_bps| / 20) |

阈值由 `QualityBenchmarkProvider`（Protocol）提供，可替换为动态阈值（如按市场状态调整）。默认 `DefaultBenchmarkProvider` 为静态阈值。

### 3.2 权重与加权汇总

```
overall = Σ(score_i × weight_i) / Σ(weight_i)    （仅对已提供指标的维度求和）
```

默认权重（QualityWeights，价格优先）：

| 维度 | 权重 | 理由 |
|------|------|------|
| PRICE | 0.35 | 价格是执行质量核心 |
| TIME | 0.25 | 执行速度次之 |
| COST | 0.25 | 总成本 |
| IMPACT | 0.15 | 市场影响相对间接 |

约束：权重和必须 = 1.0（±1e-6 容差），且非负。
缺失维度自动从分母排除（按已提供维度归一化），避免缺指标拉低总分。

### 3.3 评定（verdict）

| 评定 | 阈值 | 含义 |
|------|------|------|
| good | overall ≥ 0.8 | 执行优秀 |
| acceptable | 0.5 ≤ overall < 0.8 | 可接受 |
| poor | overall < 0.5 | 执行差 |

单维度评分也用同一阈值评定。

## 4. 数据结构

| 类型 | 角色 | 关键字段 |
|------|------|---------|
| `QualityDimension` | 评分维度枚举 | PRICE/TIME/COST/IMPACT |
| `QualityWeights` | 四维权重（frozen） | price_weight, time_weight, cost_weight, impact_weight; `.weight_for(dim)` |
| `ExecutionDimensionScore` | 单维度评分 | dimension, score[0,1], raw_value, threshold, verdict |
| `ExecutionQualityResult` | 评分结果（frozen） | order_id, symbol, side, overall_score, verdict, dimension_scores[], weights; `.score_for(dim)` |
| `QualityBenchmarkProvider` | 阈值提供者 Protocol | price_threshold_bps/time_threshold_s/cost_threshold_bps/impact_threshold_bps |
| `DefaultBenchmarkProvider` | 默认静态阈值实现 | 50/300/30/20 |

## 5. 公开 API

```python
class ExecutionQualityScorer:
    def __init__(self, weights: QualityWeights | None = None,
                 benchmark: QualityBenchmarkProvider | None = None) -> None
    def score(self, order_id, symbol, side, *,
              slippage_bps=None, duration_seconds=None,
              total_cost_bps=None, impact_bps=None,
              now=None) -> ExecutionQualityResult
    def score_from_results(self, order_id, symbol, side, *,
                           slippage_bps=None, duration_seconds=None,
                           total_cost_bps=None, impact_bps=None,
                           now=None) -> ExecutionQualityResult
    def get_history(self, symbol=None, min_score=None) -> list[ExecutionQualityResult]
    def average_score(self, symbol: str | None = None) -> float
    def clear_history(self) -> None
    @property
    def history(self) -> list[ExecutionQualityResult]
    @property
    def weights(self) -> QualityWeights
```

## 6. 不变量与约束

| # | 不变量 | 来源 |
|---|--------|------|
| 1 | 各维度评分 ∈ [0, 1] | `[INVARIANTS]` + ExecutionDimensionScore.__post_init__ |
| 2 | 权重和 = 1.0（±1e-6） | `[INVARIANTS]` + QualityWeights.__post_init__ |
| 3 | overall = Σ(score_i × weight_i) / Σ(weight_i) | `[INVARIANTS]` |
| 4 | 评定：good≥0.8 / acceptable≥0.5 / poor<0.5 | `[INVARIANTS]` |
| 5 | 至少一个维度指标（否则 InsufficientMetricsError） | 输入校验 |
| 6 | 权重非负 | QualityWeights.__post_init__ |

## 7. 错误契约

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| `QualityScorerError` | ZA-XS-EXT-0002 | 通用基类；评分越界 [0,1] |
| `InvalidWeightsError` | ZA-XS-EXT-0002-IW | 权重和≠1.0 或含负值 |
| `InsufficientMetricsError` | ZA-XS-EXT-0002-IM | 无任何维度指标 |

## 8. 依赖关系

| 依赖模块 | 依赖类型 | 依赖内容 |
|---------|---------|---------|
| `zephyr.shared.contracts.enums.order_enums` | 必须 | OrderSide |
| `zephyr.shared.foundation.errors` | 必须 | ZephyrBaseError 基类 |
| `zephyr.ex_sor.services.slippage_analyzer` | 可选（消费） | SlippageResult（score_from_results 提取 slippage/impact） |
| `zephyr.ex_sor.services.transaction_cost_optimizer` | 可选（消费） | TransactionCostResult（score_from_results 提取 cost） |

注：EXT-002 在 `score_from_results` 中接受已提取的指标值，不硬依赖 EXT-001/003 的类型导入（解耦），但语义上消费二者结果。

## 9. 消费者

| 消费者 | 消费方式 | 契约 |
|--------|---------|------|
| MOD-EX-CORE (执行质量报告) | 消费 ExecutionQualityResult 生成质量报告 | D-EX-CORE §140 |
| MOD-XS-011 (算法选择器) | 消费评分作为算法选择反馈环 | XS-011 算法效果评估 |

## 10. 已实现代码路径

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/ex_sor/services/execution_quality_scorer.py` | ✅ 已实现 | 515 行，build_status=stable |
| `tests/ex_sor/test_execution_quality_scorer.py` | ✅ 已实现 | 47 用例，全过 |

## 11. 设计真源映射

| 设计文档条目 | 本模块实现 |
|-------------|-----------|
| §2.1 XS-EXT-02 价格维度 | PRICE 维度（滑点） |
| §2.1 XS-EXT-02 时间维度 | TIME 维度（执行速度） |
| §2.1 XS-EXT-02 成本维度 | COST 维度（总交易成本） |
| §2.1 XS-EXT-02 市场影响维度 | IMPACT 维度 |
| §2.1 XS-EXT-02 历史追踪 | history + get_history + average_score |
| §140 执行质量评分 | 四维评分 + 加权 + 评定 |
| §258 C-046 执行质量分析 | 本模块为 C-046 能力落地 |

## 12. EXT 三件套协作关系

```
EXT-001 SlippageAnalyzer ──┐  slippage_bps + impact_bps
                           ├──→ EXT-002 ExecutionQualityScorer ──→ overall_score + verdict
EXT-003 TransactionCostOptimizer ─┘  total_cost_bps
                                     + duration_seconds (外部传入)
```

EXT-002 是聚合层：EXT-001 提供价格+冲击维度，EXT-003 提供成本维度，时间维度由执行调度器（XS-04）传入。
三者共同构成 D-EX-SOR 的 TCA（交易成本分析）子能力，对应能力项 C-046。

## 13. 变更记录

| 日期 | 版本 | 变更摘要 |
|------|------|---------|
| 2026-08-02 | 0.1.0 | 初版落地：四维评分(价格/时间/成本/冲击)+加权汇总+good/acceptable/poor 评定；类名由 DimensionScore 改为 ExecutionDimensionScore 解决冲突；module_id 由非法 MOD-XS-EXT-002 改为派生轨 MOD-EX_SOR_EXT-002 |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-EX_SOR_EXT-002`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-EX_SOR_EXT-002` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-EX_SOR_EXT-002` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-EX_SOR_EXT-002 | MOD-EX_SOR_EXT-002 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 14. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 14.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/ex_sor/test_execution_quality_scorer.py` | ✅ 已实现 | |

### 14.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §14（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
