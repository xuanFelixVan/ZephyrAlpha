---
ttl: permanent
doc_type: architecture_view
generator: generate_trading_flow_diagram.py
flow_stage: stock_selection
---

# 选股决策流

> flow_stage: `stock_selection` | 映射层: ['L0', 'L1', 'L2A'] | 产出契约: `candidate_pool`

## 大白话讲这个流程

选股是"从全市场 5000+ 标的里筛出今天值得关注的 10 只"。
用多层漏斗，每一层砍掉一批，最后剩下的进候选池：
  第一层：流动性过滤——砍掉成交量太低、没法买的
  第二层：基本面过滤——砍掉财务有问题的（ST/退市预警/财报异常）
  第三层：因子打分——用因子工厂产出的因子给标的打分，留下高分池
  第四层：信号生成——对高分池生成买卖信号（Insight）
  第五层：风控预筛——砍掉触及风控红线的（持仓超限/禁止标的）
  第六层：候选池——最终可买入标的清单
漏斗的每一层都对应 decisiongraph 的具体决策节点，可追溯。


## 流程框图

```
全市场 5000+
    │ ① 流动性过滤（成交量/换手）
    ▼
  ~800
    │ ② 基本面过滤（ST/财报/退市）
    ▼
  ~200
    │ ③ 因子打分（factor_value 排序）
    ▼
  ~50
    │ ④ 信号生成（Insight: 方向/置信度）
    ▼
  ~20
    │ ⑤ 风控预筛（持仓超限/禁止标的）
    ▼
  ~10 → 候选池 candidate_pool

```

## 运营态节点（实盘主链路）

_（暂无已标定节点，待 Phase B 全量标定）_


## 指挥 AI 提示

改选股流时，先查 decisiongraph 里 flow_stage=stock_selection 的节点，
定位到具体层（L0/L1/L2A）和 module_id，再改对应代码。
常见改动：调整漏斗某层的阈值、增删因子、改信号生成逻辑。
注意：选股产出的是 candidate_pool，不是订单——信号仓位分离铁律。


## 子流程

### 流动性过滤

按成交量/换手率过滤，砍掉流动性不足的标的。

模块锚点: `MOD-MKT_DATA`

### 基本面过滤

按 ST 标记/财报异常/退市预警过滤。

模块锚点: `MOD-L02-001`

### 因子打分

用因子工厂产出的 factor_value 给标的打分排序。

模块锚点: `MOD-L02-001`

### 信号生成

对高分池生成 Insight（方向/置信度/时间跨度）。

模块锚点: `MOD-L02-001`

## 附录1·待施工（设计态节点）

| node_id | 决策名称 | 节点类型 | layer | module_id | path |
|---|---|---|---|---|---|
| 190 | 末位淘汰 IC-Based Factor Replacement | signal | L2A | - | `decision/factor/fc_01` |
| 191 | 批量裁剪 Batch Factor Pruning | signal | L2A | - | `decision/factor/fc_02` |
| 192 | Multi-Source Priority Router 多源优先级路由 | signal | L2A | - | `decision/data/dt_01` |
| 193 | Cross-Source Reconciler 多源对账 | signal | L2A | - | `decision/data/dt_02` |
| 194 | Multi-Timeframe Fusion 跨频率融合 | signal | L2A | - | `decision/data/dt_03` |


## 附录2·未来增强（候选库）

_从 candidate_module_registry.yaml 按 target_track 归类到本阶段；基础设施类候选（回测/仿真/灾备/死域）见 [总览](trading_flow_index.md) 跨阶段附录_

| 候选ID | 名称 | 状态 | 优先级 | 卡在哪问 | 解决什么痛点 |
|---|---|---|---|---|---|
| CAND-AISA-001 | AI Sentiment Analyzer / AI 舆情分析器 | candidate | P1 | pending | A 股受政策与舆情驱动性强,缺乏结构化舆情信号导致政策行情响应滞后 |
| CAND-SIG-002 | ML-driven Signal Synthesizer / ML驱动信号合成 | deferred | P2 | q2 | 因子数增多后,等权/固定IC加权无法捕捉因子间非线性关系 |
| CAND-FAC-001 | Factor Cache / 因子缓存 | deferred | P2 | q2 | 因子数量增长后,每日全量重算导致计算延迟>50ms |

