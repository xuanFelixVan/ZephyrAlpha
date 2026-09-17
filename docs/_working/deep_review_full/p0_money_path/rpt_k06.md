---
ttl: task_bound
title: 深度审查作业簿——A股止损规则引擎
owner: st-deeprev-20260918
created: 2026-09-18
reviewed: 2026-09-18
---

# 深度审查报告：A股止损规则引擎（K06）

- 状态: **已审**
- 级别: P0｜类型: 闸门
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/risk/core/ashare_stop_loss_engine.py:286`（六模式 :320-409；亏损限额 :413-479）
- 生产调用方（实测 grep）: **零**。全仓 src+scripts 非测试对 AshareStopLossRuleEngine/check_position/check_loss_limit/StopLossSignal/LossLimitAlert/forced_halt_days 的引用=0（唯一命中是 post_entry_instant_validator.py:29 的 docstring 提及，非调用）。作业簿预填"position core包/风控validator链"经查不成立
- 测试文件: tests/risk/test_ashare_stop_loss_engine.py（38 用例全绿——测的是信号产出，无法暴露孤儿状态）
- 运行结果: `python -m pytest tests/risk/test_ashare_stop_loss_engine.py -q` → 38 passed（Python 3.12.8）

## 1 对象快照

- **范围**：引擎本体（6 模式+亏损限额三级+强制停盘天数）；接线面延伸核实了 per-position 止损族四件：RK-09（本件）/RK-04（stop_loss.py 评估层，见 rpt_k01）/RK-35（atr_stop_engine）/RK-40（post_entry_instant_validator）。
- **排除项**：atr_stop_engine 本体细审（同族旁证已取：grep 亦无生产调用）；K07 回撤链（组合级，独立存活）。
- **材料缺项声明**：运行时证据包未取；数据画像未取。
- **测试覆盖概况**：38 用例覆盖六模式+限额递进+非法输入+边界（信任）；但全部是"产而不消"链路上的单测。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C | **孤儿闸（零生产调用方）**：信号引擎+亏损限额+停盘天数三件产物无一生产行消费；模块 MATURITY=production/SAFETY=H 与现实不符。设计链 RK-09(信号)→RK-04(执行)两端均孤儿（RK-04 见 rpt_k01 C 轴）——**per-position 止损在生产不存在**，唯一活的风险线=组合级回撤链（K07→EMERGENCY→K01 熔断） | grep 全部公开符号生产命中=0；ashare_stop_loss_engine.py:5-8,37 | **P1**（P0 论证见 §4-1） | `grep -rn "AshareStopLossRuleEngine\|check_loss_limit" src/ scripts/ --include=*.py \| grep -v test` |
| C | forced_halt_days 全仓无执行者：停盘=N 天禁开仓需要日历级禁单机制配合，grep halt_days 生产命中=0——即便将来接线信号面，停盘语义仍无处落地 | grep "halt_days" 非测试非本件=0 | P2 | 同左 |
| D | 止损族四件全产而不消：RK-09（本件）/RK-04 评估层/atr_stop_engine（RK-35）/post_entry_instant_validator（RK-40，MATURITY=design 但头注称"调用方按 T+5/15/30min 逐档调用(运行时装配批)"——grep 消费=仅 re-export）——模式 #8 孤儿死码的家族性案例，建议挖矿节点统一裁定退役或接线 | post_entry_instant_validator.py:5,29；risk/__init__.py:69,94 | **P1**（与 C 轴合并计一次） | 逐件 grep 消费方 |
| A | 数学审查：六模式比例计算正确（loss=(entry-cur)/entry、discount=(exp-act)/exp、break=(ref-cur)/ref、动量阈值）；亏损限额 abs(min(x,0)) 正确忽略盈利侧；递进约束（日<周<月、停盘天数非降）配置期强制 | ashare_stop_loss_engine.py:151-176,436-457 | 已查无 | 手算对拍测试 |
| A | 边界：空 symbol/非正 entry/current → InvalidStopLossInputError（Fail-Closed）；未提供的模式跳过不臆测；auction_actual_price 未做正数校验（actual=0→discount=100% 必触发；负价→>100%） | ashare_stop_loss_engine.py:356-361,553-554 | P3 | check_position(actual_price=0) 观察触发 |
| A | 语义漂移：分时破位 docstring"跌破分时均线**/前低**"（或语义），实现 vwap 存在时 prev_low 被完全忽略（单一参考） | ashare_stop_loss_engine.py:346,389-391 | P3 | 传 vwap+prev_low 看只用 vwap |
| A | EMERGENCY 不可达：头注 INVARIANT"EMERGENCY 级必须触发 RK-04 执行"，但 check_position 六模式最高只产 CRITICAL；EMERGENCY 仅来自月亏限额线路——且该线路同样无人消费（C 轴） | ashare_stop_loss_engine.py:401-408,260-266 | P3 | grep severity=EMERGENCY 赋值点 |
| B | 上游输入全部调用方注入（纯函数无 IO，解耦正确）——但正因无调用方，支撑位/vwap/板块动量/竞价预期的**产源**全仓也不存在（数据画像无从谈起）；support_break 无缓冲带（跌破 0.01% 即 CRITICAL，支撑位本身是估计值） | ashare_stop_loss_engine.py:513-516 | P3 | grep support_level 产源 |
| E | 假阳性过关（该触发没触发）：孤儿状态本身=永久性"该触发不触发"（P1 已计）；规则级 fail-open 仅跳过未提供输入的模式（已文档化，可接受） | ashare_stop_loss_engine.py:338 | （已计） | — |
| E | 静默失败：无吞异常；A股口径——跌停无法成交/流动性枯竭时 suggested_action"立即止损卖出"不可执行，信号面无成交可行性评估（执行面责任，执行面亦孤儿）；集合竞价时段触发行为=AUCTION_DISAPPOINT 模式覆盖（仅开盘语义，无 9:15-9:25 时段窗校验） | ashare_stop_loss_engine.py:499,543-568 | P2（跌停可行性归执行面缺口，随 §4-1 计） | 读码 |
| E | 重复触发/时序：纯函数无状态，逐次调用幂等；同标的重复信号去重归调用方（无调用方=无验证） | 全文 | 已查无 | — |
| A.3 | 测试质量：断言强（类型+数值+级别），无日期漂移；缺 actual_price≤0 边界与 EMERGENCY 不可达断言 | tests/risk/test_ashare_stop_loss_engine.py | P3 | 补用例建议 |

## 3 SOTA 对照（轴 F）

- **A 股交易台止损纪律**（固定比例-7%/支撑破位/竞价不及预期/分时破位/板块退潮+亏损限额三级停盘复盘）：与 A 股游资/交易台常规纪律同构，规则集本身**对等已有**（本战役轴 F 检索预算已用于 K02 监管阈值与 K05 VaR 统计充分性，本对象未做独立 WebSearch，如实记录；中文卖方金工研报为独立矿脉，留待收口方按需补检）。
- 同族 RK-40 头注引 Gao, Han, Li, Zhou (2018, Journal of Finance) 日内动量作为三档验证依据（post_entry_instant_validator.py:56）——该模块同为孤儿，学术对照随件休眠。

## 4 缺陷清单（按严重级排序）

1. **[P1→建议 Owner 按 P0 议处] per-position 止损生产整体缺位**：现状→信号族四件（RK-04/09/35/40）全部零接线，仓位级止损、买入后即时纠错、亏损限额停盘在生产一条都不跑。影响→个股黑天鹅（跌停/暴雷）只能靠组合级回撤 5%/10%/15% 分级兜底，第一道防线缺位；爆炸半径=单标的损失无自动截断。按任务口径"零调用=孤儿闸 P1"计，但鉴于缺失的是整套止损语义且模块以 production/SAFETY=H 示人（假安全感），建议收口方按 P0 插队议处：要么排期接线（信号面→trading_session 调仓循环+停盘天数控ock），要么正式退役改登记（规范预算净零）。验证法→§2 C 轴 grep。
2. **[P2] 停盘天数无执行机制**：接线信号面前需先建 halt_days→禁开仓日历的落地件（可挂 K03 生命周期或 risk_layer allow_new_position）。验证法→grep halt_days 消费。
3. **[P3] 五条打包**：auction_actual_price 无正数校验；分时破位 prev_low 被忽略的语义漂移；support_break 无缓冲带；EMERGENCY 在 check_position 不可达；测试缺上述边界用例。

## 5 挂起疑问

1. 本模块在 blueprint 里的消费规划（RK-03 告警/RK-04 执行）是否曾有时表？零接线是"未排期"还是"接线后被回退"？建议查 tracker 后裁定接线或退役。
2. 组合级亏损限额（日-2%/周-5%/月-10%）与 K07 回撤分级（5%/10%/15%）、K01 EMERGENCY(15%) 的阈值体系无联动文档——三套百分比各管一段还是重复？建议 Owner 出一张阈值总表（避免多套"日亏"口径并存漂移，模式 #1）。

## 6 完备性自评

- 六轴全查：A/B/C/D/E/F 均有结论；数学四问逐模式过；E 轴五问逐条（多数收敛到孤儿主发现）。
- 长尾清单：① atr_stop_engine（RK-35）本体未细审（旁证零调用已取）；② post_entry_instant_validator 的三档规则数学（ATR/量比）未逐条验算（design 级且孤儿）；③ 中文研报止损实践对照未检索（轴 F 如实记录）。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P1 零生产调用+RK-04/35/40同族产而不消(per-position止损整体缺位): 挂起登记(Owner裁定接线或退役)。
