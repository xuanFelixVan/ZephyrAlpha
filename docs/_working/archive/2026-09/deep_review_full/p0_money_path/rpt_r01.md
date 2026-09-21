---
ttl: task_bound
title: 深度审查报告——风控分层编排器(盘中对账)（R01）
owner: st-deeprev-20260918
created: 2026-09-18
reviewer: GLM-5.3-Flash/st-deeprev-20260918
baseline_commit: 2fa92002c3
---

# 深度审查报告：风控分层编排器(盘中对账)（R01）

- 状态: **已审**
- 级别: P0｜类型: 管线
- 基线 commit: 2fa92002c3（9 个目标文件零漂移，`git diff --stat 2fa92002c3 -- <targets>` 为空）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/ex_core/risk_layer_orchestrator.py:453(start_reconcile_loop:1781)`
- 生产调用方: trading_session:404（start）/ 419（stop）/ 778（is_symbol_frozen 下单硬拦）；装配点 scripts/start_paper_session.py:457
- 测试文件: tests/ex_core/test_risk_layer_orchestrator.py（39 passed，运行实录 2026-09-18）

## 1 对象快照

- **范围**：RiskLayerOrchestrator 的盘中对账编排（start_reconcile_loop:1781 / stop_reconcile_loop:1791 / run_reconcile_once:1800 / is_symbol_frozen:1807 / _schedule_reconcile:1811 / _reconcile_tick:1822）及与 PositionReconciler 的接缝。其余风控编排（回撤/VaR/清算/系统性降级）不在本簿，另簿覆盖。
- **裁定#317 核对（必做项）**：ruling_registry.yaml:3928-3938 在册内容="自续期 Timer（宪法红线唯一在案违规）改挂 ExecutionReport/持仓变更事件+30min staleness 兜底一次；影子并行一周零差异后启用"。**文件现状=Timer 仍在**（`threading.Timer` risk_layer_orchestrator.py:1815-1820），全文件 grep 无 ExecutionReport 挂点、无 staleness 兜底代码。结论：**裁定在册 active、施工未落地**（改造期对象，与本簿备注一致）。
- **测试覆盖概况**：TestIntradayReconcile 两用例覆盖"drift→冻结→调仓硬拦"与"循环启停"；未覆盖连续失败、reconciler=None、interval 漂移路径。
- **材料包缺项声明**：运行时证据包（近 N 天 error 日志/reconcile 记录）未取——无生产日志访问通道，静默失败类发现以代码路径+验证法替代。
- **变更热力**：近 3 月 14 commits（本批 9 文件中并列最高，与 position/position_reconciler.py 并列）=高危区。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | Timer 自续期环仍在（裁定#317 违规现状未改） | risk_layer_orchestrator.py:1811-1827 | P1 | grep `threading.Timer` 该文件仅此一处；对照裁定册 3928 |
| A | _reconcile_tick 异常全吞、仅 log，无失败计数/升级 | risk_layer_orchestrator.py:1822-1827 | P1 | 注入 always-raise reconciler 跑 2 轮，观察仅 `盘中定时对账失败` log 无告警 |
| A | run_reconcile_once fail-open：reconciler=None 返回 True（"一致"） | risk_layer_orchestrator.py:1802-1803 | P2 | 构造无 reconciler 编排器调 run_reconcile_once 断言 True |
| A | tick 完成后才重排 → 实际间隔=interval+耗时漂移；无交易时段门控（夜间/周末照跑） | risk_layer_orchestrator.py:1815-1827 | P3 | 对比 reconcile 结果 timestamp 差值 |
| B | 双源 symbol 键格式隐式契约：QMT 侧 `pos.stock_code` 原样透传未归一化，与 tracker "600000.SH" 格式不一致时全标的假 drift | miniqmt_broker.py:561 vs ex_core/position_reconciler.py:156-163 | P2 | mock broker 返回无后缀代码，观察全量冻结 |
| B | broker.get_positions 抛错 → tick 吞掉下轮重试，无连续失败熔断 | risk_layer_orchestrator.py:1822-1826 | P1（同上吞没条合并） | 同上注入法 |
| C | 下单硬拦消费方存在且 fail-closed（冻结标的订单进 _blocked_orders） | trading_session.py:778 + 测试 test_frozen_symbol_blocked_in_rebalance:471-503 | （正面） | 跑该用例 |
| D | 同文件族双标：调仓 Timer 已按 trae_060 §3 删除（trading_session.py:381-383），对账 Timer 保留=裁定#317 认定的"唯一在案违规" | trading_session.py:381-383 vs risk_layer_orchestrator.py:1815 | P1（即裁定条） | 读两处注释对比 |
| D | 平行实现 zephyr/position/position_reconciler.py 自称"事件触发"与本件 Timer 调度语义相反 | position/position_reconciler.py:8,22-26 | P2 | 详 R02 簿 |
| E | 对账环死掉没人知道：stop 后无心跳；_reconcile_running=False 后无人发现对账已停 | risk_layer_orchestrator.py:1791-1798 | P2 | start 后 stop，无任何告警产生 |
| E | 在途挂单不计入对账（open_orders_provider 未喂 reconciler）→ 已报未成交造成账实差会误冻结 | risk_layer_orchestrator.py:466 + ex_core/position_reconciler.py:151-170 | P2 | 挂单未成交期间跑 reconcile 观察冻结 |
| E | reconcile 幂等（纯读+冻结集全量重算），重放安全 | ex_core/position_reconciler.py:8,169-171 | （正面） | 连跑两次结果一致 |

## 3 SOTA 对照

- **事件触发+批量兜底混合制=2025 业界收敛方向**：Oceanobe《Event-Driven Reconciliation》（oceanobe.com，页面未标注年份，检索 2026-09-18）列举 batch 对账三类失效模式；Juspay《Payment Reconciliation Across Multiple PSPs》（juspay.io/blog，2025）三向对账（账本↔结算↔资金）+事件驱动实时抓差。**结论：裁定#317 方向（事件触发+staleness 兜底）与 SOTA 混合制对等**——但本项目目前是"纯 Timer batch"且改造未施工，落在 SOTA 下风。立卡已裁（在册），本簿只报施工缺口。

## 4 缺陷清单

1. **P1 对账环静默死亡（吞没+无心跳）**
   现状→_reconcile_tick `except Exception: log + 下轮重试`（risk_layer_orchestrator.py:1822-1827），且无失败计数、无连续失败告警、无对账时间戳外露监控点；stop_reconcile_loop 亦无对外痕迹（1791-1798）。
   证据→锚点如上；测试无连续失败用例。
   影响与爆炸半径→对账是盘中 drift 唯一探测通道：对账死 N 小时=冻结/解冻全部停摆=风控盲飞，且一切日志正常（"下轮重试"永不发生也无感知）。全账户级。
   建议修法→随裁定#317 改造一并对齐：连续失败阈值告警+暴露 last_reconcile_at/staleness 给监控（30min 兜底扫描顺带覆盖）。
   验证法→注入 raise reconciler，断言 3 次失败后告警通道收到事件。
2. **P1 裁定#317 施工未落地**
   现状→Timer 仍在（1815-1820），无事件挂点/无 30min staleness 兜底。
   证据→裁定册 ruling_registry.yaml:3928-3938 vs 文件 grep。
   影响与爆炸半径→宪法红线违规持续在案；Timer 线程与调仓事件线程并发写 tracker 视图。
   建议修法→按裁定施工+影子并行一周。
   验证法→grep 文件无 `threading.Timer` 且有事件订阅+staleness 判定。
3. **P2 run_reconcile_once/is_symbol_frozen fail-open 缺省**
   现状→reconciler=None 时 run_reconcile_once 返回 True（"一致"）、is_symbol_frozen 返回 False（"不拦"）（1802-1803/1807-1809），装配漏注入时全链绿灯。
   证据→对照本类破产底线未武装时的"大声告警"先例（risk_layer_orchestrator.py:543-547），对账器缺装却静默。
   影响与爆炸半径→装配回归（漏一行）=盘中对账无声消失，唯一痕迹是 start_reconcile_loop 的静默 return（1783-1784）。
   建议修法→构造期 reconciler=None 且 config.reconcile_interval_seconds>0 时告警（对齐破产底线先例）。
   验证法→构造无 reconciler 实例，断言 warning 日志。
4. **P2 在途挂单未计入对账**
   现状→orchestrator 持有 open_orders_provider（524）但 reconcile 链不消费；tracker 已记成交、broker 未回报的窗口=假 drift→冻结+on_drift 噪音。
   证据→risk_layer_orchestrator.py:466,524 + ex_core/position_reconciler.py:143-170。
   影响与爆炸半径→高频下单窗口内标的被反复冻结/解冻，阻塞调仓（trading_session.py:778 硬拦）。
   建议修法→对账比对前按在途单做"期望在途量"调整，或对冻结新增设单笔确认延迟。
   验证法→mock：下单未成交期间跑 reconcile，观察误冻结。
5. **P3 interval 漂移+无交易时段门控**
   现状→tick 执行后再 _schedule_reconcile（1827）；夜间/周末照跑。
   证据→1815-1827。
   影响与爆炸半径→轻微；夜间券商查询可能超时产生噪音日志。
   建议修法→随事件化改造自然消失（staleness 兜底自带时段语义可后补）。
   验证法→日志时间戳间隔统计。

## 5 挂起疑问

- 疑问①：裁定#317 施工排期在哪本 tracker？本簿只确认"未落地"，是否已有施工项登记请收口方核对（若未登记，裁定在册无施工项=悬空）。
- 疑问②：QMT stock_code 实际返回格式是否恒带 .SH/.SZ 后缀（xtquant 版本差异）——需实单 smoke（checklist #13 同款），代码层无法证实。

## 6 完备性自评

- 六轴全查：A/B/C/D/E/F 均有结论（F=SOTA 对等+施工缺口）。正面项 2 条（下单硬拦 fail-closed、reconcile 幂等）。
- 长尾清单：①运行时证据包未取（无生产日志通道）——"对账静默死亡"是否已实际发生无法从代码判定；②与 reconcile 相关的 RiskLayerConfig.reconcile_interval_seconds 生产装配值未核（start_paper_session.py 用默认 300s，未逐行核对其余装配点）；③系统性风险/清算编排不属本簿范围。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P1 对账环异常吞没+run_reconcile_once fail-open: 挂起登记(裁定#317改造区,防合并冲突,#317落地后随车道修)。
