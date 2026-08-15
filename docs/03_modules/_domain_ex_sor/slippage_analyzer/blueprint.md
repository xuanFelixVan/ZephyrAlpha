---
module_id: MOD-EX_SOR_EXT-001
submodule_path: src/zephyr/ex_sor/services/slippage_analyzer.py
title: "滑点分析器蓝图 — 多基准滑点计算+三因子归因+平方根冲击预测"
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

# MOD-EX_SOR_EXT-001 Slippage Analyzer — 滑点分析器 蓝图

> **module_id**: MOD-EX_SOR_EXT-001 | **域**: D_EX_SOR | **层**: L2 执行路由
> **优先级**: P2 | **成熟度**: production | **建设标记**: ✅可建(①) | **设计标签**: XS-EXT-01
> **SSoT**: depgraph MOD-EX_SOR_EXT-001 | **设计真源**: D:\临时工作区\依赖图\09-D-EX-SOR-执行路由域.md §2.1 XS-EXT-01
> **代码**: src/zephyr/ex_sor/services/slippage_analyzer.py | **测试**: tests/ex_sor/test_slippage_analyzer.py

## 1. 定位

滑点分析器——成交后评估"实际成交价"相对"预期基准价"的偏离（滑点），是 TCA（交易成本分析）的核心组件。

大白话：你下单时心里有个"理想价"（比如下单瞬间的市场价），但实际成交价往往比理想价差一点，这个差就是"滑点"。本模块算出滑点有多少、为什么会滑（冲击/时机/价差三类原因）、以及根据订单大小预测会滑多少。

属 D-EX-SOR §2.1 补充子模块（滑点与质量分析），P2 优先级，①可建（无门禁阻塞）。纯计算模块，无 I/O 副作用，Decimal 守恒。

## 2. 输入 / 输出

| 方向 | 内容 |
|------|------|
| 输入 | 订单元信息(order_id/symbol/side) + 成交记录列表(SlippageFillRecord) + 基准价格映射(SlippageBenchmark→Decimal) + 可选归因输入(adv/volatility/start_price/end_price/spread_bps) |
| 输出 | SlippageResult（多基准滑点指标 + 三因子归因 + 预测滑点 + 元信息） |

## 3. 核心设计

### 3.1 滑点符号约定（统一不变量）

```
BUY  → slippage_bps = (avg_fill - benchmark) / benchmark × 10000   正值=买贵了=成本
SELL → slippage_bps = (benchmark - avg_fill) / benchmark × 10000   正值=卖便宜了=成本
```

正值统一表示"成本"（执行不利），负值表示"有利"。这是跨模块对齐 EXT-002 质量评分的前提。

### 3.2 多基准滑点计算

支持 5 类基准（SlippageBenchmark 枚举）：

| 基准 | 含义 | 典型用途 |
|------|------|---------|
| ARRIVAL | 到达价（下单时刻市场价） | 最常用，反映执行全程滑点 |
| VWAP | 成交量加权均价 | 对标市场成交分布 |
| TWAP | 时间加权均价 | 对标均匀执行 |
| PREV_CLOSE | 前收盘价 | 隔夜跳空评估 |
| DECISION | 决策价（信号生成时价） | 反映信号→执行全链路滑点 |

加权平均成交价 = Σ(price×qty) / Σ(qty)，Decimal 精度，四舍五入到 4 位小数。

### 3.3 三因子归因模型（Phase 1 简化版）

将总滑点分解为市场冲击/时机/价差三因子 + 残差：

```
market_impact_bps = impact_coeff × sqrt(participation_rate) × volatility_bps
                    participation_rate = order_qty / adv
timing_bps        = (end_price - start_price) / start_price × 10000 × sign(side)
                    BUY: 价格上涨→时机成本(正); SELL: 价格下跌→时机成本(正)
spread_bps        = half_spread_bps（估计，默认 10bps ≈ 0.1%）
residual_bps      = total_slippage - (impact + timing + spread)   吸收模型误差
```

- `impact_coeff` 默认 0.142（≈1/(2×√(2π)) 量级，Almgren-Chriss 简化经验值）
- 归因以 ARRIVAL 基准为总滑点（若无则取 DECISION，再退化为第一个）

### 3.4 平方根冲击预测器（SquareRootImpactPredictor）

```
predicted_bps = coeff × sqrt(order_size / adv) × volatility_bps + half_spread
```

理论对标：平方根法则（Grinold & Kahn；Almgren-Thum et al.）。预测值非负，四舍五入到 0.01 bps。
需 adv + volatility 同时提供，否则跳过预测（predicted_slippage_bps=None）。

`SlippagePredictor` 为 Protocol 接口，可替换为更复杂模型（如 Almgren-Chriss 全模型、非参数估计）。

## 4. 数据结构

| 类型 | 角色 | 关键字段 |
|------|------|---------|
| `SlippageFillRecord` | 单笔成交记录（frozen） | fill_id, price, quantity, timestamp, side |
| `SlippageBenchmark` | 基准类型枚举 | ARRIVAL/VWAP/TWAP/PREV_CLOSE/DECISION |
| `SlippageMetric` | 单基准滑点指标 | benchmark, benchmark_price, avg_fill_price, slippage_bps, side |
| `SlippageAttribution` | 三因子归因+残差 | market_impact_bps, timing_bps, spread_bps, residual_bps; `.total_attributed_bps` |
| `SlippageResult` | 分析结果（frozen） | order_id, symbol, side, total_quantity, avg_fill_price, metrics[], attribution, predicted_slippage_bps, analyzed_at; `.metric_for(bench)` |

## 5. 公开 API

```python
class SlippageAnalyzer:
    def __init__(self, predictor: SlippagePredictor | None = None,
                 half_spread_bps: Decimal = Decimal("10")) -> None
    def analyze(self, order_id, symbol, side, fills, benchmarks, *,
                adv=None, volatility=None, start_price=None, end_price=None,
                spread_bps=None, now=None) -> SlippageResult
    def get_history(self, symbol: str | None = None) -> list[SlippageResult]
    def clear_history(self) -> None
    @property
    def history(self) -> list[SlippageResult]
```

`SquareRootImpactPredictor.predict(order_size, adv, volatility, spread_bps) -> Decimal`

## 6. 不变量与约束

| # | 不变量 | 来源 |
|---|--------|------|
| 1 | 滑点符号约定：BUY/SELL 正值=成本 | `[INVARIANTS]` 头 |
| 2 | 归因分量和 ≈ 总滑点（残差吸收误差） | `[INVARIANTS]` |
| 3 | 预测值非负 | `[INVARIANTS]` |
| 4 | 成交价/数量必须为正（SlippageFillRecord.__post_init__） | 输入校验 |
| 5 | 基准价格必须为正 | 输入校验 |
| 6 | Decimal 全程精度，禁 float 参与金额/价格运算 | 项目铁律 |

## 7. 错误契约

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| `SlippageAnalyzerError` | ZA-XS-EXT-0001 | 通用基类 |
| `InsufficientFillsError` | ZA-XS-EXT-0001-IF | 无成交记录或总量为零 |
| `InvalidBenchmarkError` | ZA-XS-EXT-0001-IB | 基准价格≤0、未提供基准、ADV≤0（预测时） |

## 8. 依赖关系

| 依赖模块 | 依赖类型 | 依赖内容 |
|---------|---------|---------|
| `zephyr.shared.contracts.enums.order_enums` | 必须 | OrderSide |
| `zephyr.shared.foundation.errors` | 必须 | ZephyrBaseError 基类 |

无外部服务依赖（纯计算，无 DB/网络/文件 I/O）。

## 9. 消费者

| 消费者 | 消费方式 | 契约 |
|--------|---------|------|
| MOD-EX_SOR_EXT-002 (ExecutionQualityScorer) | 消费 SlippageResult → price + impact 维度评分 | EXT-002 `score_from_results` |
| MOD-EX-CORE (执行质量报告) | 消费滑点指标生成 TCA 报告 | D-EX-CORE §140 |

## 10. 已实现代码路径

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/ex_sor/services/slippage_analyzer.py` | ✅ 已实现 | 572 行，build_status=stable |
| `tests/ex_sor/test_slippage_analyzer.py` | ✅ 已实现 | 49 用例，全过 |

## 11. 设计真源映射

| 设计文档条目 | 本模块实现 |
|-------------|-----------|
| §2.1 XS-EXT-01 实际vs预期滑点 | 多基准 SlippageMetric |
| §2.1 XS-EXT-01 滑点归因 | SlippageAttribution 三因子+残差 |
| §2.1 XS-EXT-01 滑点预测 | SquareRootImpactPredictor |
| §2.1 XS-EXT-01 基准比较 | SlippageBenchmark 5 类 |
| §13.1 Almgren-Chriss | impact_coeff + sqrt(participation) |
| §17.2 R-118 Liquidity & Slippage Simulator | 本模块为执行后分析（S5 试运行层消费方） |

## 12. 变更记录

| 日期 | 版本 | 变更摘要 |
|------|------|---------|
| 2026-08-02 | 0.1.0 | 初版落地：多基准滑点+三因子归因+平方根预测；类名由 FillRecord 改为 SlippageFillRecord 解决冲突；module_id 由非法 MOD-XS-EXT-001 改为派生轨 MOD-EX_SOR_EXT-001 |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-EX_SOR_EXT-001`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-EX_SOR_EXT-001` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-EX_SOR_EXT-001` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-EX_SOR_EXT-001 | MOD-EX_SOR_EXT-001 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 13. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 13.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/ex_sor/test_slippage_analyzer.py` | ✅ 已实现 | |

### 13.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §13（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
