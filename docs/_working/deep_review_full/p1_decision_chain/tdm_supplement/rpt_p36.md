---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——环境开关
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：环境开关（P36）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/core/environment_switch.py`
- TDM 节点: TDM-E-L3-06（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）；MOD-SIG-138，Owner 2026-09-11 夜班立项
- 生产调用方: **半接线：词表常量 `SIX_STATES` 被 `pf_core/strategy_engine/framework_composer.py:205`（lazy import，六段 activation 词表真源 T1A-3）真实消费；但开关查表主函数 `evaluate_environment_switches` 生产零调用（头注自declared L3-06/L3-07/C13 均待接线）**
- 测试文件: `tests/signal_ashare/test_environment_switch.py`（14 用例，本班次实跑 14/14 绿）

## 1 对象快照

140 行纯查表核（MOD-SIG-138）：六段封闭状态集（capitulation..distribution）×四开关（首板筛选器/短线链/波段链/反向收紧）封闭表 + 三条硬规则叠加（成交<8000 亿→首板停；冰点→只留波段；euphoria→tighten）。ERROR_CONTRACT：未知状态/负值/非有限成交额→EnvironmentSwitchInputError（fail-closed）。阈值与开关表=proposed 待实盘标定（头注:8 声明诚实）。测试覆盖：封闭表全态/边界/非法输入。排除项：framework_composer 深审不在本批（其 activation 语义仅消费词表不消费动作表）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 数学①：纯查表无统计量；封闭表 6 态×4 开关全覆盖（:82-89）与 docstring 逐条对码（冰点/退潮收短线留波段、euphoria tighten）一致；地量规则 `<8000` 严格小于与节点语义"成交<8000 亿=停"一致（8000 整点不清算） | environment_switch.py:82-89,119-124 | 通过 | 逐态对照 TDM algo_note |
| A 深度 | 边界②：NaN/inf/负成交额全 raise（:113-115 `math.isfinite` 正确防御——与 P33/P35 NaN 洞形成对照的正例）；state 非字符串/不在封闭集 raise（:109-112）；8000 亿恰界不清算（on 侧）语义正确 | :109-115,119 | 通过 | 传 NaN 观察 EnvironmentSwitchInputError |
| B 上游 | checklist #6 断供：输入=调用方注入的状态+成交额两标量；五阶段→六段归并映射由调用方负责（:22-24 声明）——**sentiment_cycle（P22 域）五阶段与六段封闭集的映射唯一位点在调用方，本件不认五阶段词**=隐式契约已文档化但映射本身无唯一承载（framework_composer 有一份 REGIME_STATE_TO_ACTIVATION_PHASE——regime 四态→六段另一映射，两套映射并存） | :22-24；framework_composer.py:8 | P3 | grep `REGIME_STATE_TO_ACTIVATION_PHASE` 与 sentiment_cycle 阶段集对照 |
| C 下游 | **半孤儿裁定：词表已接线（framework_composer.py:205 lazy import SIX_STATES 作 activation 词表真源）、开关动作表零接线**——查表核（本件存在意义）尚无生产消费方；接线后下游=打板链首板筛选器启停/短线波段链启停/C13 情绪档协同（:5 头注全标"待接线"诚实）；爆炸半径=策略链启停（全链级开关，错值=整链停/开） | framework_composer.py:205,250,381 | P1(接线期) | `grep -rn "evaluate_environment_switches" src/ --include=*.py`（零命中） |
| D 旁系 | checklist #4 双承载：晨审定性"STRATEGY_DEPLOYMENT_MATRIX（3 策略×5 阶段）仅部分承载，环境开关查无专件→立 C 类候选"（:26-28）——本件即该缺口补件，双承载嫌疑裁定=无（补缺非复制）；8000 亿阈值单点承载已查无第二处；五阶段（sentiment_cycle）vs 六段（本件）vs 四态（regime_detector）三套状态词表并存=**状态词表族级漂移风险（映射责任分散在两处调用方）** | :26-28 | P3 | grep 三词表常量对照 |
| E 对抗 | 五问：①静默失败=无（全 raise）②假阳性=状态拼写错误 raise fail-closed（framework_composer:381 同纪律互认）③断供=成交额缺失非本件职责（调用方），传 0 会触发地量停链（保守向）④重触发幂等⑤时序=N/A（单日快照） | :109-115 | 通过 | — |
| F 新鲜度 | 情绪周期分段×策略启停为 A 股游资/情绪周期交易语境的工程化（中文卖方金工情绪周期框架同构），无英文文献独立对照面；8000 亿地量阈值为项目实证断言（节点真源）——**底层实证产物锚未在仓内检索到（地量首板次日溢价为负的回测 artifact）**，按 checklist #15 记挂起 | 检索结论：情绪周期框架属 A 股本土语境（中文研报矿脉，英文 SOTA 不适用）；实证锚缺失挂起 | 通过（本土对等）+挂起 | grep `次日溢价\|地量` docs/ 找底层产物 |

## 3 SOTA 对照

- 对等已有（本土）：情绪六段×策略开关查表为 A 股情绪周期交易常规工程化，与中文卖方金工情绪周期框架同构。
- 立卡候选：8000 亿阈值实证 artifact 落仓（回测证据链补锚）——接线校准时顺路。
- 驳回：无。

## 4 缺陷清单

1. P1（接线期）：开关查表主函数生产零调用（半孤儿：词表承载已接线、动作表未接线）；全链级开关接线时属高风险面（错值=整链停开）建议 Owner 门位；验证法=§2 C 轴 grep。
2. P3：状态词表三套并存（六段/五阶段/regime 四态）+两处映射位点——建议映射收拢单一真源模块；验证法=§2 D 轴 grep。
3. P3：8000 亿实证断言无仓内 artifact 锚（checklist #15 关键数字无底层产物）——补回测证据或降级"经验值"；验证法=§2 F 轴 grep。

## 5 挂起疑问

- tighten_risk=True 的执行语义（"压仓位上限/提门槛"）在消费方如何落地无承载件——开关信号有了，动作执行器缺位，接线裁定时需一并立项。

## 6 完备性自评

六轴全查（F 本土语境对等+实证锚挂起）。长尾：①sentiment_cycle/regime_detector 两上游映射精度未审（各自域对象）②开关表 proposed 状态无实盘标定记录③14 测试覆盖全态但无 framework_composer 消费面集成测试。

## 7 收口裁定（收口方填）
