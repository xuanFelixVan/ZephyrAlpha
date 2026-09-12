---
ttl: task_bound
---
﻿# L3-08 汇总件施工交付报告（candidate_pool_aggregator）

> **施工会话**：L3-08 汇总件施工（2026-09-11 晚批）
> **真源**：TDM-E-L3-08 节点（aggregation 结构位）+ 晨审 st-tdm-review-20260911 §7.1 裁定 + Owner 2026-09-11 立项批准
> **交付状态**：模块 + 37 单测全绿落码；落图归 TDM 增长轨（本会话不碰地图，wiring-news-ig-001 先例）
> **git**：未提交；新文件已 git add 同步索引

---

## §0 一句话给增长轨

新汇总件已按 C13 纯函数核范式落码（`src/zephyr/signal_ashare/core/candidate_pool_aggregator.py`
+ `tests/signal_ashare/test_candidate_pool_aggregator.py`，37 passed），TDM-E-L3-08
落图只需把 §4 规格卡填进预留坑位（module_ref=null 现挂）——**MOD id 待统筹登记**
（R21 格式冲突未解），module_ref 建议值已给，可先落 path 型引用。

---

## §1 设计要点

### 1.1 节点语义逐条对码（TDM-E-L3-08 algo_note）

| algo_note 语义 | 对码实现 |
|---|---|
| 双池合流 | 来源① `dual_pool_candidates`（短线池 fine_scoring_engine / 波段池 quant_short_term_strength_engine 产出，每条自带 sleeve 标签） |
| 策略链候选 | 来源② `strategy_chain_candidates`（打板/多因子/事件驱动三 sleeve 链产出，承接 TDM-E-L3-07-1/2/3 feed 边） |
| 否决后清单 | 来源③ `veto_marks`（negative_veto MOD-SIG-137 否决裁决留痕注入——**只标记不剔除**，一票否决裁决在上游，本件留痕不重复裁决） |
| 顺位排序 | 按 symbol 去重（保留顺位最优）→ 未否决在前按顺位分降序，vetoed 沉底留痕 |
| 最终候选池 10-20 只 | 容量真源写死默认 10-20（`DEFAULT_MIN_SIZE/MAX_SIZE`）；上限截断按顺位分保留；不足下限不硬凑（fail-open） |
| 带各自 sleeve 标签与顺位分 | `FinalPoolEntry.sleeves`（多来源命中按定义序合并）/`best_sleeve`（主标签）/`rank_score` |
| 喂 L4 买卖点层 | `entries` 未否决顺位前段即 L4 消费面；`to_dict()` JSON 直序列化 |

### 1.2 范式对齐（C13 intraday_tomorrow_forecast）

- **纯函数核零 IO**：三来源一律由调用方注入，本件不 import 上游三件（零依赖）；
- **鸭型镜像**：`PoolCandidateInput.from_fine_scored_entry`（ScoredEntry 姿态）/
  `from_mirror`（通用姿态）/`VetoMark.from_veto_verdict`（NegativeVetoVerdict 姿态），
  对齐 C13 `SimilarDayScenario.from_inference` 先例——不持有上游可变对象；
- **frozen+确定序**：同输入必同输出；tie-break 链全确定（rank_score 降→source_rank
  升(None=+inf)→sleeve 定义序→symbol 字典序），sleeve 定义序**仅 tie-break 用，
  无优先级语义**（algo_note 排序只认顺位分）；
- **无墙钟**：as_of 仅审计透传。

### 1.3 关键裁定（易踩坑）

1. **否决只标记不剔除**：vetoed 条目留在池中沉底（喂 L4 只取未否决顺位前段），
   不占容量名额，候选束外的否决留痕也照常透出（`vetoed_symbols` 不丢）——
   "否决后清单=最终候选池的组成部分"而非过滤条件。
2. **同 symbol 去重 vs fail-closed 边界**：跨束同 symbol 异 sleeve=合法合流去重
   （双池合流常态）；**完全重复 (symbol,sleeve) 对=fail-closed**（上游契约违反或
   同源束劈参数注入防线）。
3. **容量下限 fail-open**：不足 10 只不硬凑，notes 透出；上限截断只数未否决者，
   vetoed 不挤占名额。
4. **Tier 槽位仅预留**：`tier_slot=None` 恒定，分层归 TDM-E-L3-09
   pool_tier_maintenance，由调用方回填。

### 1.4 落点合规披露

- `signal_ashare/core/` 现存 5 文件（含 `__init__.py`），无"120 目录容量"规则
  （规则库实查：trae_010 的 120 是文档 1200 行拆分阈值；目录级容量上限无此规则）；
- 域级 ARCH-CAP-002（单域 production ≤150）：D_ASHARE_SIGNAL 实测
  production_nodes=150 恰达上限——**本件按同目录先例（pool_tier_maintenance
  MOD-SIG-139）标 design 态，不计入 production 计数，不推破上限**；正式登记
  module id 时保持 design 态即可，晋升 production 时需按 ARCH-CAP-002 走容量评估。

---

## §2 输出契约（FinalCandidatePool）

```python
FinalCandidatePool:
    as_of: str                      # 审计透传（调用方交易日）
    entries: tuple[FinalPoolEntry]  # 最终池：未否决按顺位分降序在前 + vetoed 沉底留痕
    capacity: int                   # 容量上限生效值（默认 20）
    actual_size: int                # 未否决保留数（L4 消费面大小）
    truncated_out: tuple[str]       # 上限截断出池名单（按顺位；可喂 L3-09 Tier3 雷达池）
    vetoed_symbols: tuple[str]      # 否决标记清单（含候选束外纯留痕）
    notes: tuple[str]               # 容量/否决/截断诊断
FinalPoolEntry:
    symbol / sleeves / best_sleeve / rank_score / source_rank
    vetoed: bool / veto_reasons: tuple[str]
    tier_slot: int | None           # 恒 None，TDM-E-L3-09 回填
```

入参契约：`aggregate_candidate_pool(dual_pool_candidates, strategy_chain_candidates,
veto_marks, as_of, config)`。ERROR_CONTRACT：完全重复对/未知 sleeve/非有限分数/
空 symbol/负 source_rank/容量配置越界/空 as_of/空否决原因 →
`CandidatePoolInputError`（fail-closed）；空候选来源 → 空池（fail-open，否决留痕照常透出）。

---

## §3 上游对接方式（下游消费面同步给 Tier 维护件）

### 3.1 上游三来源 → 本件

- **短线池**：`fine_scoring_engine.score_fine(...).top` → `PoolCandidateInput.from_fine_scored_entry(entry, SleeveKind.SHORT_TERM)`（symbol/z_score/rank 零转换直映）；
- **波段池**：`quant_short_term_strength_engine` 产出 `QuantStrengthResult.total_score`（0-100）→ `PoolCandidateInput.from_mirror(result, SleeveKind.SWING, score_attr="total_score")`（**口径注意**：z_score 与 0-100 分不可直接混排，调用方须先归一化到统一顺位口径——如截面 z 化，这是调用方注入职责，本件不代做）；
- **策略链**：`pf_core.strategies` 三链权重 dict 输出 → 按 `generate_target_weights` 返回的 `{symbol: weight}` 构造（score_attr 指向 final_score/weight 字段，sleeve 分别 DABAN/MULTIFACTOR/EVENT_DRIVEN）；
- **否决后清单**：`negative_veto.apply_negative_veto(facts).verdict` → `VetoMark.from_veto_verdict(verdict, symbol)`（vetoed=False → None 自然跳过）。

### 3.2 本件 → 下游

- **TDM-E-L4 买卖点层**：消费 `entries` 中未否决段（`actual_size` 条，顺位分降序）；
- **TDM-E-L3-09 pool_tier_maintenance**：`truncated_out` 可作 Tier3 雷达池增量；
  `entries[*].tier_slot` 由该件回填后本件条目即可直接转 `PoolEntry`；
- **下游 pool_tier_maintenance.py 头部 CONSUMERS** 现记"TDM-E-L3-08 候选池输出
  （Tier 标签消费，待接线）"——本件交付后该待接线项升级为"可接线（对接面见本报告 §3.2）"，
  修改其头部 CONSUMERS 注释属下游文件变更，本会话未动（留给该件 Owner 或增长轨接线批）。

---

## §4 给增长轨的落图建议（TDM-E-L3-08）

```yaml
# TDM-E-L3-08 候选池输出（现 module_ref: null）建议：
module_ref: src/zephyr/signal_ashare/core/candidate_pool_aggregator.py
# module_id：待统筹登记（R21 格式冲突未解，本件头部 [BLUEPRINT] 按接线先例
#   wiring-news-ig-001 标"待统筹登记"）；登记后建议形如 MOD-SIG-140（下一个
#   signal_ashare/core 序号，前例 MOD-SIG-139=pool_tier_maintenance），以统筹批裁定为准
# algo_refs：negative_veto（MOD-SIG-137，否决裁决上游）可同步补挂 algo_refs
```

- 图上 `TDM-E-L3-07-1/2/3 → L3-08` 与 `L3-05 → L3-08` feed 边已存在，本件三来源
  形参与边一一对应，无需改边；
- `L3-08 → L3-09` feed 边已存在，对应 §3.2 Tier 槽位回填对接面；
- 头部 `[BLUEPRINT]` 注释已按接线先例标注"待统筹登记 + spec 引用本任务与晨审 §7.1
  裁定"，蓝图文档（docs/03_modules/_domain_signal/candidate_pool_aggregator/blueprint.md）
  属登记批随行件，本会话未代建（避免 id 未定先落蓝图）。

---

## §5 测试与验收

- `tests/signal_ashare/test_candidate_pool_aggregator.py`：**37 passed**
  （解释器 C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe，pytest）；
- 红蓝手法覆盖：红-边界（空来源/容量端点/tie-break 链三级）/红-契约（完全重复对
  fail-closed/未知 sleeve/非有限分数/空否决原因）/红-前视（无墙钟 as_of 透传）/
  红-竞态（乱序注入确定性/frozen 不可变）/红-容灾（空来源 fail-open/否决留痕不丢）；
- 任务指定七项全覆盖：三来源合并、去重保留最优、顺位排序、空来源 fail-open、
  否决清单不丢只标记、10-20 截断、（加验）序列化/镜像辅助函数。
