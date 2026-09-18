---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——候选池输出
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：候选池输出（P40）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/core/candidate_pool_aggregator.py`
- TDM 节点: TDM-E-L3-08（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）；MOD-SIG-142，Owner 2026-09-11 立项
- 生产调用方: **0（唯一命中=`signal_ashare/__init__.py:122` 包门面再导出；头注自declared 落图归 TDM 增长轨接线，wiring-news-ig-001 先例；[MATURITY] design 诚实）**
- 测试文件: `tests/signal_ashare/test_candidate_pool_aggregator.py`（37 用例，本班次实跑 37/37 绿）

## 1 对象快照

431 行纯函数聚合器：三来源（双池合流/策略链/否决标记）→ 同 symbol 去重（顺位最优，tie-break 四级链全确定）→ 顺位排序（未否决前/vetoed 沉底）→ 容量截断（10-20，否决不占容量，不足下限不硬凑，截断项进 truncated_out 审计）。零 import 鸭型镜像（from_mirror/from_fine_scored_entry姿态转换）；ERROR_CONTRACT fail-closed 七类+空来源 fail-open 否决留痕透出。设计纪律为 P-lane 最佳之一（INVARIANTS 逐条可对码）。测试覆盖：去重/排序/截断/否决/非法输入。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 逻辑①：优先键 `(-score, rank(None=inf), sleeve 序, symbol)`（:262-268）四级 tie-break 全确定无平票；最终排序 vetoed 沉底（:271-280,396）；截断只出 truncated_out 不入池（:402-404,418-419）——三段语义与 INVARIANTS 逐条对码一致 | candidate_pool_aggregator.py:262-281,396-419 | 通过 | 对照 :10 INVARIANTS 逐条 |
| A 深度 | 边界②：rank_score 非有限/负 rank/空 symbol/空 reasons/容量越界/空 as_of 全 fail-closed raise（:127-137,179-183,105-110,371-372）；(symbol,sleeve) 完全重复对 fail-closed（:293-297 防上游契约违反）；空来源 fail-open 但否决留痕透出（:378-391） | :127-137,179-183,293-297,371-391 | 通过 | 37 tests 已覆盖 |
| A 深度 | **口径③：跨 sleeve 分数不可比直接混排——docstring 自declared"上游分数体系不一，z_score/0-100 分/权重均可，调用方负责口径统一"（:117-119）而最终排序直接按 rank_score 全局比（:276）——短线池 z≈±3 与波段池 0-100 分混排时波段池系统性碾压**；声明诚实但"统一口径承载"无人认领（调用方全体待接线），接线时若漏标准化=池序系统性偏置 | :117-119,276 | P2(接线期必修) | 构造 z=2.9（short_term）与 60 分（swing）两候选观察排序 |
| B 上游 | checklist #6 断供：纯注入零 IO；否决裁决在上游 negative_veto（本件只留痕不重复裁决 :29-31）——职责单一正确；veto_marks 束外 symbol 留痕透出（:388-389）防丢 | :29-31,388-389 | 通过 | — |
| C 下游 | **孤儿裁定：生产零调用方**（门面再导出非消费）；下游=L4 买卖点层（只取未否决顺位前段）+L3-09 Tier 回填（tier_slot 预留 None）——下游全部待接线；爆炸半径=全 sleeve 合流后的最终池（决策链咽喉位） | :122（门面）声明 | P1(接线期) | `grep -rn "aggregate_candidate_pool" src/ --include=*.py` 仅门面 |
| D 旁系 | checklist #4 双承载：容量 10-20 真源=TDM 节点 algo_note（:89-91 单点承载已查无第二处）；SLEEVE_ORDER 与三 sleeve 链（P37/P39/multifactor）的 strategy_id 词表是两套命名（short_term/swing/daban/multifactor/event_driven vs daban-sleeve/eventdriven-sleeve）——**sleeve 标签词表与 sleeve 策略 id 词表不统一**，接线装配时的映射层缺失 | :67-87 vs strategies/__init__.py:24 | P3 | 对照两词表 |
| E 对抗 | 五问：①静默失败=无（fail-closed 全 raise，fail-open 有 notes）②假阳性=跨源分数不可比（上述 P2）③断供=空来源空池有 notes④重触发幂等（frozen+纯函数）⑤时序=as_of 审计透传无墙钟（正确） | :371-419 | 通过（附口径 P2） | — |
| F 新鲜度 | 候选池聚合/多源去重/容量控制为选股系统工程常规（无独立统计前沿面）；否决留痕不剔除的"标记-沉底"审计设计为良好工程实践=**对等已有（工程常规）** | 工程常规结论（无独立检索面，声明式） | 通过（声明式） | — |

## 3 SOTA 对照

- 对等已有：多源候选聚合+确定性去重排序为选股工程常规；无立卡/驳回项。

## 4 缺陷清单

1. P2（接线期必修）：跨 sleeve rank_score 不可比混排（自declared 调用方统一而统一承载无人认领）——建议接线裁定时定唯一标准化点（如各 sleeve 出口 z-score 化或百分位化后再入池）；验证法=§2 A 轴构造两源候选对拍。
2. P1（接线期）：零生产调用方孤儿（design 态声明诚实）；验证法=§2 C 轴 grep。
3. P3：sleeve 标签词表（本件枚举）与 sleeve 策略 id（daban-sleeve 等）两套命名缺映射层；验证法=对照 strategies/__init__。

## 5 挂起疑问

- negative_veto（MOD-SIG-137=G03 域）与 vete_marks 注入的装配点在哪个编排件——两件均待接线，接线顺序须 negative_veto 先行（否则否决标记恒空=闸门空转，G03 报告已预警同题）。

## 6 完备性自评

六轴全查（F 声明式）。长尾：①from_fine_scored_entry 仅镜像 fine_scoring_engine 一族，波段池 quant 引擎的姿态镜像缺（上游产出适配面不全）②37 测试无跨源分数不可比的警示 case③min_size=10 下限在候选荒日的语义（空池 vs 硬凑）已择 fail-open 但 Owner 未裁定确认。

## 7 收口裁定（收口方填）
