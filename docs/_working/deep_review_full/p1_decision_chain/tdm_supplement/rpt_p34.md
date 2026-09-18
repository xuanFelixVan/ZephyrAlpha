---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——双策略合流体检
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：双策略合流体检（P34）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_fundamental/router/signal_conflict_resolver.py`
- TDM 节点: TDM-E-L3-03-3（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）
- 生产调用方: **0（唯一命中=`router/__init__.py:19-22` 包再导出；同族上游 signal_priority_router.py:5 头注自证"经 2026-09-05 AI-08 审计实证未接线——接线待排期"）**
- 测试文件: `tests/signal_fundamental/router/test_signal_conflict_resolver.py`（13 用例，本班次实跑 13/13 绿）

## 1 对象快照

181 行纯函数裁定器（MOD-SIG-010，21 号选股引擎 memo §3.3）：同 symbol 多信号冲突消解规则链 R1 风险否决（≥0.8 绝对优先）→R2 置信度差（≥0.15）→R3 时效（created_seq）→R4 来源优先级表→R5 DEFER 挂起；单方向组直通（全 LONG→ADOPT/全 EXIT→REJECT）；A 股二元方向空间（无 SHORT）；全程留痕 rule_applied/winner/losers；confidence 越界与方向非法 ValueError。测试覆盖：规则链全分支+边界。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 逻辑①：规则链首命中即终局与文档一致；`_best` 排序键 `(-conf,-seq,id)`（:97-99）确定性平局裁决；R2 用 `abs(diff)>=margin` 后按符号定向（:140-146）正确；输出动作空间 {ADOPT,REJECT,DEFER} 与"不能做空"约束自洽（EXIT 胜=REJECT 非 SHORT，:54 注释声明） | signal_conflict_resolver.py:97-99,140-164 | 通过 | 逐分支对照 docstring |
| A 深度 | 边界②：**confidence 校验 `not 0.0<=c<=1.0`（:176）对 NaN 判 True→ValueError——NaN 被显式拒绝（与 P33 形成正确对照）**；direction 白名单外 raise（:178-179）；空输入→空列表；输出组序 sorted(groups) 确定性（:181） | :172-181 | 通过 | 传 NaN confidence 观察 ValueError |
| A 深度 | 语义③：R1 风险否决仅在冲突路径（longs 与 exits 均非空）可达——**单方向组直通路径完全绕过 R1**：若 RISK 类信号被误配 direction=LONG（:80 默认 LONG），可经"no_conflict"ADOPT 胜出，INVARIANTS"风险否决绝对优先"（:8）在该路径失效；触发前提=上游 kind/direction 配置错误，属契约脆弱面非现行缺陷 | :104-125,127 | P3 | 构造 [RISK kind+LONG dir conf0.9] 单信号组观察 ADOPT |
| B 上游 | checklist #6 断供：输入=装配好的信号列表无数据源；confidence/dir 畸形有校验、created_seq/source 无校验（乱序 seq 只影响 R3 公平性，非安全性） | :174-180 | 通过 | — |
| C 下游 | **孤儿裁定：生产零调用方**（兄弟件头注互认未接线）；接线后下游=sleeve 编排/StrategyBook——DEFER 输出（:164）的下游处理语义未定义（挂起等下一信号，谁消费谁排队无承载）——接线时必须裁定 DEFER 的落点 | grep 证据；:164 | P1(接线期)+P3(DEFER 语义) | `grep -rn "resolve_conflicts" src/ --include=*.py`（仅同名异物命中） |
| D 旁系 | checklist #4 双承载：同名异物三处（intelligence/cross_agent_conflict_detector、position/firm_risk_aggregator._resolve_conflicts 均为各自域私有裁定逻辑）——职责不同（报告冲突/权重冲突 vs 信号方向冲突）非重复实现；与 sell_decision/core/sell_conflict_arbitrator.py（E04，已审域）同为裁定器但方向空间不同（买卖 vs LONG/EXIT）——裁定器家族共 4 处，语义边界清晰无同式两算 | grep 证据 | 通过 | grep `conflict` src/ 逐个核语义 |
| E 对抗 | 五问：①静默失败=无（非法 raise，平局 DEFER 显式）②假阳性=RISK/LOW conf + 高 conf OPPORTUNITY → R2 ADOPT（0.9 vs 0.3 差 0.6）——低置信风险信号不否决符合设计，但"风险信号置信度该不该进同一置信度标尺"隐式假设未文档化③断供=N/A④重触发幂等⑤时序=created_seq 同值时 R4 兜底，链路封闭无死角 | :127,140-146 | 通过 | — |
| F 新鲜度 | 规则优先级链式裁定（风控一票否决+置信度阈值+时效+来源优先级）为多信号融合工程的常规确定性手法，非统计算法无文献对照面；本轴按受阻/不适用如实记：**无独立 SOTA 检索面（规则引擎类），对照结论=对等已有（工程常规）** | 不适用声明（非统计算法） | 通过（声明式） | — |

## 3 SOTA 对照

- 对等已有：确定性规则链+风控否决优先，与选股引擎 memo §3.3 及通用信号融合实践一致；无立卡/驳回项。

## 4 缺陷清单

1. P1（接线期）：零生产调用方孤儿（上游 router 同批未接线=整族待装配）；DEFER 输出无下游承载语义——接线裁定必答项；验证法=§2 C 轴 grep。
2. P3：单方向组直通绕过 R1 风险否决（kind/direction 配错的脆弱面）——建议 R1 提到分组后无条件执行（RISK∧conf≥门槛即 REJECT 无论方向组合）；验证法=§2 A 轴构造。
3. P3：MATURITY=production 与未接线现实不符（V06/P28 同族标签失实案）；建议改 testing。

## 5 挂起疑问

- RISK 类信号置信度与 OPPORTUNITY 置信度是否同一标尺（跨标尺差值比较的语义前提）——建议接线时在 docstring 声明。

## 6 完备性自评

六轴全查（F 为声明式不适用+受阻诚实记）。长尾：①`signal_priority_router`（同包上游）未审（不在本批对象集）②source_priority 默认空表——生产装配时的优先级表来源未约定③13 测试无 RISK/LONG 误配 case。

## 7 收口裁定（收口方填）
