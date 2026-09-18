---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——买入时序
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：买入时序（P47）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/plan_engine/closing_session_decision.py`
- TDM 节点: TDM-E-L4-02（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）；MOD-PLAN-003/BM-PLAN-03（41 号 §3.10.4）
- 生产调用方: **0（`plan_engine/__init__.py:19` 显式"ORPHAN-MODULE: 引用登记"=治理在册的自declared 孤儿；邻件头注消费声明均为宣告非接线）**
- 测试文件: `tests/plan_engine/test_plan_engine.py`（共享文件 17 用例全绿，其中 TestClosingSessionDecision 覆盖三动作分支；本班次实跑 17/17 绿）

## 1 对象快照

164 行尾盘决策器：高开概率>70%→ADD（边界内上限，缺省硬编码 0.30）/低开概率>60%→REDUCE/否则 HOLD。44 号修正边界消费接口（boundary 可选注入，None=既有口径零破坏）。ERROR_CONTRACT 声明 ClosingDecisionError（ZA-PLAN-0003）为调用方捕获锚点。依赖 similar_day_inference（高/低开概率产源，同为待接线件）——**决策器与概率产源全链未装配**。测试覆盖：三动作主分支。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 逻辑①：两阈值比较逻辑与 41 号裁定值一致（>70%/>60% :61-62）；REDUCE max_weight=当前权重（:153 语义=可减至 0 上限为现仓）正确 | closing_session_decision.py:61-62,148-155 | 通过 | 对照 docstring |
| A 深度 | **文档-代码漂移②实锤：INVARIANTS"14:45-15:00 决策窗口"+"尾盘决策未就绪→不操作"（:8）与 ERROR_CONTRACT ClosingDecisionError"决策未就绪=不操作"（:13,:67-74）在代码零实现——窗口常量 DECISION_WINDOW_START/END（:63-64）定义后全文件无消费，decide() 无就绪态检查、无窗口校验、从不 raise ClosingDecisionError**；窗口执法责任默推调用方但调用方也是未接线件——不变量目前纯文档态 | :8,13,63-64,67-74 | P2 | grep `DECISION_WINDOW_START` 本文件引用（仅定义行）+grep `ClosingDecisionError(` 全仓（仅类定义） |
| A 深度 | 边界③：NaN 概率→两比较全 False→HOLD（fail-safe 正确方向）；**概率未校验 [0,1]（1.5 也触发 ADD）；intraday_inference 缺 box_upper/box_lower 键→price_bound=(0.0,0.0) 退化区间静默下发**（下游若按区间限价=0 元废单风险）；action 词表 EXIT（:88）无产出路径=死词条 | :128-129,139-145 | P3 | 缺键调用观察 price_bound=(0,0) |
| B 上游 | checklist #6 断供：概率产源 similar_day_inference 自declared"数据期前无，候选消费方：尾盘决策"（similar_day_inference.py:5）——**产消两端均未接线，概率缺省 0.0 时 decide 恒 HOLD**（安全向默认）；持仓权重缺省 0.0 无缺失区分 | similar_day_inference.py:5；:109-110 | P3 | 不传概率观察 HOLD |
| C 下游 | **孤儿裁定：生产零调用方**（ORPHAN-MODULE 治理登记在册——本批对象中登记纪律最佳实践）；下游=BM-BUY-02/BM-SELL-02 融合（未接线）；爆炸半径=尾盘加减仓指令（真金路径上游），接线时 ADD/REDUCE 直连资金动作须 Owner 门位 | `__init__.py:19` | P1(接线期) | `grep -rn "ClosingSessionDecision(" src/ scripts/ --include=*.py` |
| D 旁系 | checklist #4 双承载：阈值 0.70/0.60 在本件常量与 41 号文档双承载（常量与文档对码一致，已核）；与 §3.4 建仓窗口分工声明清晰（:32-35）；与 boundary_revision_engine 的修正边界消费接口（44 号 §3 M2）为正确依赖方向（消费修正后边界非自算） | :26-35,56,121-123 | 通过 | 对照 41 号 §3.10.4 |
| E 对抗 | 五问：①静默失败=概率缺省 0.0 恒 HOLD（缺数据=不动，符合"宁可不操作"宪章语义✓）②假阳性=窗口不校验（任意时刻调用都出 ADD/REDUCE——若调用方漏窗口判断，盘中早段即触发尾盘决策语义）③断供=缺数据 HOLD 安全④重触发幂等（纯函数）⑤时序=窗口/时序全外包（上述 P2） | :133-155 | P2(同漂移案) | — |
| F 新鲜度 | 尾盘博弈明日高/低开为 A 股 T+1 制度特色策略（隔夜跳空溢价捕获，英文市场隔夜 gap 文献方向一致但制度动因不同——T+1 无当日回转使尾盘买入独享次日卖出权）；高开>70% 阈值为设计文档裁定值无实证标定记录；**对等已有（本土制度语境）** | 制度语境结论（声明式）；隔夜收益文献为通用谱系（对照检索预算已投 P45/P44 族） | 通过（声明式） | — |

## 3 SOTA 对照

- 对等已有：尾盘决策+隔夜 gap 博弈为 A 股 T+1 制度化策略，实现与设计文档一致；无立卡/驳回新增。

## 4 缺陷清单

1. P2：**"未就绪→不操作"不变量+决策窗口 14:45-15:00 纯文档态零实现**（窗口常量死代码、ClosingDecisionError 零 raise 点）——接线时窗口执法必须落在本件或调用方其一并留测试锚；验证法=§2 A 轴两条 grep。
2. P1（接线期）：生产零调用方孤儿（ORPHAN-MODULE 登记在册、概率产源同链未接线——接线须三件套齐装：similar_day_inference→本件→BUY/SELL 融合）；验证法=§2 C 轴 grep。
3. P3：box 缺键→(0,0) 退化价格区间静默下发；概率无 [0,1] 校验；EXIT 死词条。

## 5 挂起疑问

- add_cap 缺省 0.30（boundary=None 时）与 premarket_constraint_loader 的 ConstraintState 上限是否同源（两处承载疑似，接线对账项）。

## 6 完备性自评

六轴全查（F 声明式）。长尾：①position_state 契约字段集未定义（只消费 weight 键）②共享测试文件 17 例中本件仅 3-4 例，边界（NaN/缺键/超阈概率）零覆盖③boundary 注入路径有测试但 None 与注入两态的 max_weight 语义差未文档化为契约表。

## 7 收口裁定（收口方填）
