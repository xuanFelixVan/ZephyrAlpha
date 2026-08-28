---
module_id: MOD-SELL-006
title: "置换与再平衡卖出蓝图 — 机会成本驱动+组合权重偏离驱动"
doc_type: blueprint
status: Active
version: "0.1.3"
ttl: permanent
design_maturity: production
layer: L03_sell_decision
layer_name: sell_decision
functional_domain: sell_decision
responsibility_domain: 
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P1
blueprint_level: module
---

# MOD-SELL-006 | Replacement & Rebalance Seller 置换与再平衡卖出

> **域**: D_SELL_DECISION | **层**: L03 卖出决策 | **优先级**: P1 | **safety**: M | **ai_autonomy**: ai_modifiable
> **状态**: stable | **版本**: 0.1.0 | **SSoT**: depgraph MOD-SELL-006 (node 7604391)

## 1. 模块定位

置换与再平衡卖出器——两种被动卖出驱动: ① 机会成本驱动(候选池有更优标的→卖A买B) ② 组合再平衡驱动(权重偏离>阈值→被动卖出超配)。产出 ReplacementRebalanceOrder 喂给 SELL-01 收集器第⑥类信号源。

依据: `D:\临时工作区\依赖图\31-D-SELL-DECISION-卖出决策域.md` §1.2 SELL-06

## 2. 不变量 (INVARIANTS)

- **再平衡触发**: current_weight - target_weight > threshold → REDUCE(超配卖出)
- **置换触发**: candidate_score - current_score > score_threshold → REPLACE(卖A买B)
- **低配不触发**: current < target 需买入, 非本模块职责
- **严格大于**: 偏离==阈值不触发(保守原则)
- **confidence ∈ [0,1]**: 随偏离/评分差递增, 上限0.9
- **REPLACEMENT 必须 replace_with**: 置换指令必须指定目标标的
- **不可变值对象**: ReplacementRebalanceOrder frozen=True

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| InvalidRebalanceInputError | ZA-SELL-0006 | symbol空 / 权重越界 / 评分越界 / 阈值≤0 / REPLACEMENT无replace_with |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 依赖 | zephyr.shared.foundation.errors | ZephyrBaseError | 错误基类 |
| 依赖 | MOD-SELL-001 SellSignalCollector | SellDirection | 复用卖出方向枚举 |
| 消费 | D-PF-CORE 组合权重 | current_weight/target_weight | 再平衡输入 |
| 消费 | D-FACTOR/D-SELECT 候选评分 | current_score/candidate_score | 置换输入 |
| 产出 | MOD-SELL-001 收集器 | ReplacementRebalanceOrder→第⑥类信号 | 机会成本/再平衡信号源 |
| 产出 | MOD-SELL-007 融合引擎 | ReplacementRebalanceOrder | 融合消费 |

## 5. 触发逻辑

### 再平衡(权重偏离)
```
drift = current_weight - target_weight
if drift > threshold:  # 严格大于
    → REDUCE (超配卖出)
    confidence = min(0.5 + drift, 0.9)
```

### 置换(机会成本)
```
score_diff = candidate_score - current_score
if score_diff > score_threshold:  # 严格大于
    → REPLACE (卖A买B)
    confidence = min(0.6 + score_diff, 0.9)
```

### 默认阈值
| 参数 | 默认值 | 说明 |
|------|:------:|------|
| rebalance_threshold | 0.05(5%) | 权重偏离阈值 |
| replacement_score_threshold | 0.20(20%) | 评分差阈值 |

## 6. 接口

### 输入
```python
# 再平衡
seller.evaluate_rebalance(symbol, current_weight, target_weight, now=None) -> Order | None
# 置换
seller.evaluate_replacement(symbol, current_score, replace_with, candidate_score, now=None) -> Order | None
```

### 输出数据模型
```python
@dataclass(frozen=True)
class ReplacementRebalanceOrder:
    symbol: str
    order_type: SellOrderType       # REPLACEMENT/REBALANCE
    current_weight: float           # [0,1] (置换时复用存评分)
    target_weight: float            # [0,1] (置换时复用存候选评分)
    direction: SellDirection        # REDUCE/REPLACE
    confidence: float               # [0,1]
    reason: str
    replace_with: str               # 置换目标(仅REPLACEMENT)
    metadata: dict                  # drift/score_diff/threshold
    timestamp: datetime
```

## 7. 设计决策

| 决策 | 理由 |
|------|------|
| A类基础设施(纯比较逻辑) | 不涉及"候选池怎么排序"(D-SELECT职责), 只定义触发契约 |
| 严格大于触发 | 偏离==阈值不触发, 保守原则(避免边界频繁触发) |
| 低配不触发卖出 | 低配需买入, 属买入决策域, 非本模块职责 |
| 置信度随偏离/评分差递增 | 偏离越大→信号越强, 但上限0.9(不超强制类) |
| REPLACEMENT 必须 replace_with | 置换必须指定买什么, 否则无意义 |
| 置换复用 weight 字段存评分 | 减少数据模型数量, 语义通过 order_type 区分 |
| 事件回调可注入 | 预留事件发布接口 |

## 8. 测试计划

- 再平衡超配触发 + 未超配不触发 + ==阈值不触发
- 低配不触发
- 再平衡置信度递增 + 上限0.9
- 置换候选更优触发 + 不够优不触发
- 置换置信度递增 + 上限0.9
- 输入校验(symbol空/权重越界/评分越界/replace_with空)
- 构造器校验(阈值≤0/评分阈值负)
- Order校验(REPLACEMENT无replace_with/权重越界/置信度越界)
- 事件回调触发 + 故障隔离
- 时钟注入
- 自定义阈值(再平衡/置换)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SELL-006`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SELL-006` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SELL-006` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SELL-006 | MOD-SELL-006 | ✅ |
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


