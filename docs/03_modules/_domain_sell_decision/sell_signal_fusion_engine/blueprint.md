---
module_id: MOD-SELL-007
title: "卖出信号融合引擎蓝图 — 多信号加权融合+多时间框架共振"
doc_type: blueprint
status: Active
version: "0.1.3"
design_maturity: production
build_status: production
ttl: permanent
layer: L03_sell_decision
layer_name: sell_decision
functional_domain: sell_decision
responsibility_domain: 
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P0
blueprint_level: module
---

# MOD-SELL-007 | Sell Signal Fusion Engine 卖出信号融合引擎

> **域**: D_SELL_DECISION | **层**: L03 卖出决策 | **优先级**: P0 | **safety**: M | **ai_autonomy**: ai_modifiable
> **状态**: stable | **版本**: 0.1.0 | **SSoT**: depgraph MOD-SELL-007 (node 7604392)

## 1. 模块定位

卖出信号融合引擎——多卖出信号加权融合为综合卖出意愿(0~1)+融合置信度, 支持多时间框架共振增强, 产出 FusedSellDecision 喂给 SELL-08/09。

插入位置: D-SELL-DECISION 融合仲裁层(第三层)入口, 消费 SELL-01 的 SellSignal, 产出 FusedSellDecision。

依据: `D:\临时工作区\依赖图\31-D-SELL-DECISION-卖出决策域.md` §1.4 SELL-07, §4 E-SELL-01

## 2. 不变量 (INVARIANTS)

- **综合意愿∈[0,1]**: 0=无卖出意愿, 1=最大卖出意愿
- **融合置信度∈[0,1]**: 反映信号一致性(一致性高→置信度高)
- **多信号加权**: 各信号 confidence × weight 加权平均, 权重按 signal_type 默认(强制类权重高)
- **多时间框架共振**: 同标的同方向多时间框架信号 → 权重 ×1.5(v6.0)
- **一致性检查**: 同方向占比 >80%=HIGH / 50-80%=MEDIUM / <50%=LOW
- **隔离故障**: 单标的融合异常不阻断其他标的
- **策略可注入**: 默认加权平均, 贝叶斯/Dempster-Shafer 可选注入(预留)

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| InvalidFusionInputError | ZA-SELL-0007 | 输入信号列表为空或含非法值 |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 消费 | MOD-SELL-001 SellSignalCollector | SellSignal | 卖出信号(含 signal_type/timeframe) |
| 产出 | MOD-SELL-008 SellConflictArbitrator | FusedSellDecision | 融合意愿→仲裁(增强消费) |
| 产出 | MOD-SELL-009 SellUrgencyScorer | FusedSellDecision | 融合意愿→紧迫度(增强消费) |
| 产出 | D-POSITION | E-SELL-01 SellSignalFused | 融合完成事件 |
| 产出 | D-SIGNAL | E-SELL-01 | 融合结果反馈 |

## 5. 融合算法

### 默认: 加权平均 (WeightedAverageFusion)
```
willingness = Σ(confidence_i × weight_i × resonance_boost_i) / Σ(weight_i × resonance_boost_i)
confidence = willingness × consistency_factor
```

### signal_type 默认权重
| signal_type | weight | 说明 |
|-------------|:------:|------|
| MAIN_FORCE_DISTRIBUTION | 1.5 | 主力出货权重大 |
| BREAKOUT_FAILURE | 1.5 | 突破失败权重大 |
| FUNDAMENTAL | 1.2 | 基本面恶化 |
| TECHNICAL | 1.0 | 技术面 |
| VOLUME_PRICE_DIVERGENCE | 1.0 | 量价背离 |
| RELATIVE_STRENGTH | 0.8 | 相对强弱 |
| OPPORTUNITY_COST | 0.6 | 机会成本(止盈, 权重低) |
| TIME_STOP | 0.6 | 时间止损(权重低) |

### 多时间框架共振 (v6.0)
同标的同方向(SellDirection)多时间框架信号 → 该信号权重 ×1.5

### 一致性因子
| 同方向占比 | consistency | confidence 因子 |
|-----------|-------------|:--------------:|
| > 80% | HIGH | ×1.0 |
| 50-80% | MEDIUM | ×0.8 |
| < 50% | LOW | ×0.5 |

## 6. 接口

### 输入
```python
engine.fuse(
    sell_signals: list[SellSignal],
    now: datetime | None = None,
) -> list[FusedSellDecision]
```

### 输出数据模型
```python
@dataclass(frozen=True)
class FusedSellDecision:
    symbol: str
    willingness: float                # [0,1] 综合卖出意愿
    confidence: float                 # [0,1] 融合置信度
    contributing_signals: list[SellSignal]
    consistency: ConsistencyLevel     # HIGH/MEDIUM/LOW
    fusion_method: FusionMethod       # WEIGHTED_AVG/BAYESIAN/DEMPSTER_SHAFER
    dominant_signal_type: SellSignalType
    resonance_enhanced: bool          # 是否经多时间框架共振增强
    reason: str
    timestamp: datetime
```

## 7. 事件

| 事件ID | 事件名 | 触发条件 | 消费者 |
|--------|--------|---------|--------|
| E-SELL-01 | SellSignalFused | 卖出信号融合完成 | D-POSITION, D-SIGNAL |

## 8. 设计决策

| 决策 | 理由 |
|------|------|
| 默认加权平均融合 | A类可建, 逻辑明确; 贝叶斯/D-S 需参数标定(B类) |
| signal_type 权重差异化 | 强制类(主力/突破)应主导融合意愿 |
| 多时间框架共振 ×1.5 | v6.0 核心架构, 多周期共振增强信号可信度 |
| 一致性影响置信度 | 信号分歧→置信度低, 需 SELL-08 仲裁 |
| FusionStrategy 协议可注入 | 预留贝叶斯/D-S 接口, 后续学习系统接入 |
| 产出 FusedSellDecision | SELL-08/09 可增强消费(当前基于 SellSignal 工作) |

## 9. 测试计划

- 单信号融合(willingness=confidence)
- 多信号加权平均
- signal_type 权重差异化(主力>止盈)
- 多时间框架共振增强
- 一致性三档(HIGH/MEDIUM/LOW)
- 融合置信度计算
- 多标的混合
- 输入校验(空列表抛错)
- 单标的异常隔离
- 自定义融合策略注入
- 自定义权重映射
- 事件发布(E-SELL-01)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SELL-007`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SELL-007` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SELL-007` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SELL-007 | MOD-SELL-007 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 10.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

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


