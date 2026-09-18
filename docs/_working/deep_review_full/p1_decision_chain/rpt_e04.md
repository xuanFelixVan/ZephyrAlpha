---
ttl: task_bound
doc_type: report
title: 深度审查报告——买卖冲突仲裁器（E04）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：买卖冲突仲裁器（E04）

- 状态: **已审**
- 级别: P1｜类型: 卖出族仲裁（#309 挂起族）
- 基线 commit: 2fa92002c3（工作树 bf65648609；本文件自基线零变更，锚点双有效）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- **裁定#309 约束声明**：卖出族整族挂起（ruling_registry.yaml:3833-3839）——审查照常，施工受裁定约束。
- 入口锚点: `src/zephyr/sell_decision/core/sell_conflict_arbitrator.py:249(arbitrate)/:297(_arbitrate_one)/:118(BuySignal)`
- 接线现状（grep 实证）：包外零导入——引用仅包内（sell_urgency_scorer.py:57 消费 ArbitrationResult/ConflictLevel）+`__init__` 再出口+测试；族级结构性空转同 E01。
- 测试文件: tests/sell_decision/test_sell_conflict_arbitrator.py
- 材料包缺项: 无

## 1 对象快照

- 范围：买卖冲突检测→分级（STRONG/WEAK/NONE）→卖出优先裁决（0/1 tick 延迟）→事件发布；BuySignal 轻量契约。
- 测试覆盖概况：专测在位。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 卖出优先铁律实现正确：冲突时 winning_side 恒 SELL（:340），买入方永不胜出；冲突只调制卖出延迟（强 0/弱 1 tick）——保守原则兑现 | sell_conflict_arbitrator.py:319-346 | 已查无（正面） | — |
| A | **风控标识子串匹配脆弱**：`"RISK" in source.upper()`（:361）——source 含 RISK 子串即判强冲突立即执行；名为 "RISKPREMIUM-*"/"MARKET-RISK-MODEL" 的非风控来源会被误判强冲突（假强→跳过观察期）；metadata risk_force 布尔通道才是精确通道 | sell_conflict_arbitrator.py:197-198, :359-363 | P2 | source="RISKPREMIUM-X" 的技术信号 → STRONG |
| A | 弱冲突延迟 1 tick 期间**买入信号处置未定义**：本模块只裁卖方延迟，买方是否照常执行在结果里无裁决字段（winning_side=SELL 但 buy_signals 原样附回）——"仲裁器"实为"卖方延迟调制器"，跨域买方语义缺口靠 D-PF-CORE 消费约定（未在本层闭合） | sell_conflict_arbitrator.py:336-346 | P3 | 读结果契约：无 buy 侧 verdict 字段 |
| A | 分级仅看类型集合+风控标记，不看你我信号强度/数量（buy_count 只进 reason 文案 :326/:333）——"1 个技术弱卖 vs 5 个高置信买入"与"5 卖 vs 1 买"同为 WEAK——强度盲仲裁；设计文档口径如此（类型驱动 MVP），接电后建议加强度维度 | sell_conflict_arbitrator.py:350-357 | P3 | 构造两场景对照 |
| A.3 | 专测在位；空 sell 列表→[] 静默（与 E02 一致、与 E01 raise 相反——族内空输入行为三态并存） | sell_conflict_arbitrator.py:277-293 | P3 | 空列表对照三兄弟 |
| B | 上游 SellSignal.metadata（risk_force 键）契约未在本件校验（缺键 .get 默认 False 安全）；BuySignal __post_init__ 自校验 [0,1]（:138-142）fail-closed | sell_conflict_arbitrator.py:138-142, :363 | 已查无 | — |
| C | 下游：urgency scorer 消费 verdict；D-EX-CORE/D-PF-CORE 为头注规划消费方（未接电）；**事件只对冲突发布**（:289-290）——NO_CONFLICT 直通卖不进事件流，事件驱动消费方看不见直通卖出（静默缺口，接电前置项） | sell_conflict_arbitrator.py:288-290 | P3 | 无冲突构造观察无事件 |
| C | 单标的异常隔离=该标的从结果静默消失（:291-292）——同 E01 家族模式 | sell_conflict_arbitrator.py:291-292 | P3 | 注入异常复演 |
| D | delay_ticks 的"tick"定义未在本模块锚定（秒级/事件循环拍？）——跨模块语义依赖消费方自悟（隐式契约无文档，deep_review B 轴定义命中） | sell_conflict_arbitrator.py:200-201, :330 | P3 | grep tick 消费方定义 |
| E | 重放/重入：无状态+clock 注入；回调异常隔离（:379-383）；仲裁结论可从 reason 文案+字段完整重建审计——审计可追溯 INVARIANT 兑现 | sell_conflict_arbitrator.py:367-383 | 已查无 | — |
| E | A 股口径：**STRONG"立即执行"与 T+1 约束的冲突**——当日买入份额不可当日卖，强冲突 0 延迟裁决在 T+1 下部分不可执行（执行面须二次过滤，本层无 T+1 感知）；跌停日立即执行同样受流动性约束——两处执行面前置项 | 设计边界 | P3（接电前置登记） | 读执行规划器职责对照 |

## 3 SOTA 对照

1. **买卖冲突卖出优先（对等已有）**：风险优先/退出优先于进入是风控工程保守原则（多层防御体系常规；与本仓 D-SELL §1.4 优先级链声明一致）；分级延迟执行（immediate vs observe）类似订单执行里的参与策略分级。
2. **类型驱动冲突分级（立卡候选）**：业界接电后可升级为强度×类型二维仲裁（ensemble agreement 阈值口径，AIMS Press NHM 2026 ensemble thresholds 同族），登记接电后挖矿候选，非当前必修。
3. 结论：**对等已有**；T+1/跌停执行面前置项为接电清单。

## 4 缺陷清单

1. **[P2] 风控来源子串匹配脆弱（假强冲突→跳过观察期）**——证据 ：197-198/:359-363；影响：接电后非风控来源含 RISK 字样→卖出跳过 1-tick 观察（保守向误伤，非资金损失向）；建议：以 metadata risk_force 为唯一通道，子串匹配降级为告警或删除；验证法：§2 A 首行构造。
2. **[P3] NO_CONFLICT 直通卖不进事件流**（:288-290）——事件消费方需旁路消费返回值；建议：全部发布+conflict_level 区分；验证法：无冲突构造。
3. **[P3] 买方处置语义缺口**（:336-346）——契约文档补"本模块不裁买方"；验证法：读结果字段。
4. **[P3] tick 定义无锚**（:200-201）——文档补锚或引执行面常量；验证法：grep。
5. **[P3] 空输入三态并存**（vs E01 raise/E02 []）——族级一致性清单；验证法：三函数对照。
6. **[P3] T+1/跌停执行面前置**——接电清单登记；验证法：执行规划器对照。
7. **[P1-族级] 结构性孤儿**——并入 E01 族级发现。

## 5 挂起疑问

1. 弱冲突 1 tick 延迟期间若买入成交、卖出随后执行——净持仓先增后减的过山车是否 Owner 接受？需要在接电设计里定"延迟期买入冻结"与否。
2. strong_conflict_types 集合的维护权（默认主力出货+突破失败）——新增强类型走什么评审？

## 6 完备性自评

- 六轴全查：是（全量逐行）。长尾：①SellSignal.metadata 结构（collector 对象）；②urgency scorer 消费细节（族内兄弟）；③blueprint 冲突分级全文反查（挂起态冻结）。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
