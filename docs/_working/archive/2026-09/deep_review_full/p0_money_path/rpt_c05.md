---
oid: C05
title: 现金台账+划拨账本（cash_manager MOD-POS-006，FundTransferLedger:452）
status: 已审
reviewer: GLM-5.3-Flash/st-deeprev-20260918
baseline: 2fa92002c3
date: 2026-09-18
ttl: task_bound
---

# 深度审查报告：C05 CashManager + FundTransferLedger（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照

- 入口：`src/zephyr/position/core/cash_manager.py:153`（CashManager）、`:452`（FundTransferLedger）、plan_reverse_repo:320。
- 范围：T+1 结算、三储备、可投资上限、逆回购排程、出入金台账与投影，489 行全读。
- 排除项：无。
- 测试覆盖：tests/position/test_cash_manager.py 28 passed（1.26s）——无 pending+投影组合用例、无 NaN/透支用例。
- 生产接线：**零生产调用方**——grep 全仓 CashManager/FundTransferLedger/plan_reverse_repo/projected_available 除本体与测试外零命中。头注 [CONSUMERS] MOD-POS-001(现金约束反馈)/D-EX-CORE 无 import 证据（position_sizing_engine 仅头注列依赖，代码未 import）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **projected_available 不计 pending_settlement 的 T+1 释放**：投影=state.available_cash+Σ台账，而 available=total−pending（:243,317,479-489）；今日卖出次日_projection 系统性少计整笔 pending——本件自declared用途"做 T+N 可用资金规划"（:457）的主用例（明早能买多少）直接错答 | :243,307-318,479-489 | **P1** | 实测：initial=100 万→record_sell(10 万)→projected_available(次日)=100 万（应 110 万）；本报告命令行原样重放 |
| A | **NaN 流水穿透**：`NaN<=0`=False 过校验→total_cash=nan（实测）；NaN 从此污染全状态 | :210-211 | P2 | 实测已复现 nan |
| A | **透支无拦**：WITHDRAWAL/BUY 超余额→total_cash 负值静默（实测 -400），无异常无告警；available 同负，仅 max_investable 被钳 0 | :215-219 | P2 | 实测已复现 -400 |
| A | 数学四问余项：available=total−pending 恒等式、三储备线性扣减、max_investable=max(0,·) 均正确；逆回购利息=amount×rate×days/365 正确但**单一年化利率套全部期限**→"选品预期利息最高"退化为永远最长限，同息取短的流动性 tie-break 死代码 | :362-391 | P3 | 构造默认池+单一利率→GC007 恒胜 |
| A | A 股口径：逆回购最小申报单位 1000 元（10 张）未整手，amount=max_investable×ratio 任意浮点；买卖费用/印花税未建模（SELL amount 语义=净额靠调用方自觉）；T+1 买入日资金可用但份额次日可卖——本件不涉及份额，无违 | :363,415 | P2 | 阅读逆回购无 rounding 逻辑 |
| A.3 | settle() 无日期语义：不校验调用时点，同日两次调用=当日卖出 T+0 释放（:227-229）；事件链若重复触发日结即提前释放 | :227-229 | P2 | record_sell 后立即 settle→available 已含该笔 |
| A.3 | 测试审查：28 用例覆盖台账进出/未来不计/储备钳零——投影用例（:268-282）全无卖出流水前置，pending 释放缺口未固化也未捕获 | tests:268-282 | P2（缺口） | 见 tests 两个投影用例前置条件 |
| B | 输入追源：initial_cash/流水/台账全靠调用方（不存在）；in_holiday_mode 布尔由调用方给——假日判定逻辑（节前2天+节后1天）在别处，本件裸收 | :231-246 | P3 | 代码阅读 |
| C | 下游：零消费方→爆炸半径当前为零；复活后 POS-01 max_investable 是 C04 max_investable 输入真源——C05 错账直通 C04 仓位 | 头注 :5 + C04 :253 | 随 P1 | grep 法 |
| D | 台账健壮性：条目只增不消（无成交核销/取消/幂等），同笔入金重复 schedule 投影双计；无持久化（重启丢） | :460-489 | P3 | schedule 同笔两次→投影双计 |
| D | 兄弟对查：钱包/现金概念在 C01 CashSeat（分配侧钱包内现金）与本件（账户级资金台账）两套口径并存——语义不同但均称"现金"，文档需互指防混 | allocation_orchestrator.py:183-213 | P3 | 两文件对读 |
| E | 静默失败：NaN/透支即静默失败点；settle 过早释放属"假可用资金"时序攻击面（重复触发会出事：双 settle→T+0） | 同上 | 并入上 | 同上 |
| F | （见 §3） | | | |

## 3 SOTA 对照

- T+1 结算/储备金体系：A 股本地市场规则题，无英文 SOTA 对照必要；逆回购整手与计息规则属交易所规则（GC001/R-001 族）——未能取得 2024-2025 规则文本核对（检索 429 **受阻**，如实记），整手结论以"申报单位应为 1000 元整数倍"的常识性标记挂起待核。
- 逆回购利率期限结构：单利率退化问题在实务中需期限化收益率曲线（未检索到直接文献，**受阻**）。

## 4 缺陷清单（按严重级）

1. **[P1] projected_available 漏计 T+1 释放**。现状：实测次日投影=100 万，应 110 万（§2 首行）。影响与爆炸半径：以投影做 T+1 买入规划=系统性少买（决策偏移）；接线后与 C04 max_investable 相通则放大。建议修法：target_date > state 日期时加回 pending_settlement（或按台账逐日结算日历精算）。验证法：本报告 §2 首行命令原样重放。
2. **[P2] NaN 穿透 + 透支静默**：修法=record() 入口 isfinite 硬校验 + 余额不足 raise InvalidCashFlowError。验证法：两条单行复现修复后应 raise。
3. **[P2] settle() 无日期闸**：修法=settle(as_of: date) 只释放 effective_date<as_of 的卖出（需流水带日期结算账本）。验证法：同日双 settle 用例。
4. **[P2] 零生产调用方**（checklist#8）+逆回购整手缺失。验证法：grep 命令见 §1。
5. **[P3]** 逆回购单利率选品退化；台账无核销/幂等/持久化；费用未建模。

## 5 挂起疑问

1. 本件与 C01 钱包额度（CashSeat/alloc 快照）的现金真源关系：sim 链现用 alloc 快照口径，本件是否规划为实盘账户台账——退役或接线需 Owner 裁定。
2. 逆回购 1000 元整手与费率规则文本待核（受阻项）。

## 6 完备性自评

六轴全查。长尾：blueprint.md 未取；CalendarPositionConstraint 假日模式（in_holiday_mode 的上游判定）未深查——其输出正确性影响 holiday_reserve，记长尾。
