---
ttl: task_bound
title: 深度审查作业簿——订单管理器+执行Saga
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：订单管理器+执行Saga（X02）

- 状态: **已审**
- 级别: P0｜类型: 模块
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/ex_core/order_manager.py:131` + `src/zephyr/ex_core/order_execution_saga.py:320`
- 生产调用方: OrderManager=TradingSession(trading_session.py:102,335)+装配层；**OrderExecutionSaga=全仓零生产调用方（已查无，见 P1-1）**
- 测试文件: tests/ex_core/test_order_execution_saga.py + test_saga_timeout_recovery.py + test_order_manager_compliance_gate.py + test_order_manager_redteam.py（81 passed，实测）
- 备注: 每张单都过这里

## 1 对象快照

- **范围**：order_manager.py 全文 559 行（FSM VALID_TRANSITIONS、C-002 三道合规闸、fill 聚合与幂等去重、拒单分类表）+ order_execution_saga.py 全文 894 行（六步 Saga、_FillCollector、超时补偿/终态恢复、持仓回滚）。
- **排除项**：CancelRateGuard 内部（X01 已核同实例防护）、PositionTracker 内部去重实现、rejection_action_handler 细节（仅审 Saga 侧消费契约）、ExecutionEngine（X03）。
- **测试覆盖概况**：81 passed（4.48s 实测，4 套文件）。Saga 超时恢复有专文件；覆盖超时撤单失败强制查终态、成本不可得门禁。**未覆盖**：部分成交余量路径、多笔 fill 序列、IDEMPOTENT_RETURN 实际语义。
- **材料包缺项声明**：运行时证据包无（生产未常态运行）；数据画像不适用；checklist 15 条已过——**命中 #8 孤儿死码（Saga）、#12 假完成状态邻近（部分成交记 FILLED）**。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | FSM 转移表完备性验证：终态（FILLED/CANCELLED/REJECTED/EXPIRED）出边空集✓；PENDING 不可直达 FILLED✓；PARTIAL 含全部合理去向✓；_transition_status 违规抛 ValueError✓ | order_manager.py:134-148,258-274 | 通过 | 读审+构造非法转移复跑 |
| A | avg_fill_price 增量加权公式正确：新均价=(旧均价×(新总量-本笔)+本笔价×本笔量)/新总量，先更新 filled_quantity 后用差值回推旧量，代数成立 | order_manager.py:521-530 | 通过 | 两笔部分成交数值对拍 |
| A | 超额成交无防御：filled_quantity 累加无上限校验，累计>order.quantity 照常入账转 FILLED、无告警——仅 Saga 路径 _FillCollector 有 qty>order_qty 拒收（:239-246），OrderManager 直连路径裸奔 | order_manager.py:521-533 | P2 | 直接 _on_fill 注入累计超量 fill 观察无拦截 |
| A | 拒单分类表与 xttrader 错误码对齐（50 涨停/51 跌停/53 价格/54 资金/55 持仓/-1 连接/-3 订单号重复），未知码保守 ABANDON✓；但 -3 的 IDEMPOTENT_RETURN"返回已存在id"语义全仓无实现（假闸） | order_manager.py:118-128 | P2 | grep IDEMPOTENT_RETURN 消费方（仅日志） |
| B | 上游 broker.submit_order 返回值无契约校验：返回 None 时赋 broker_order_id=None，后续 cancel_order 走"无 broker_order_id 纯本地撤单"分支——柜台侧真实挂单无法撤、本地却记 CANCELLED | order_manager.py:309-310,398-411 | P2 | mock broker.submit_order 返回 None 后撤单观察 |
| C | 消费方清单：orders/get_open_orders→TradingSession/Saga/对账；fills→_fill_callbacks（session/collector/操纵监测）；order events→manipulation_realtime_monitor；爆炸半径=全账户订单台账；_on_fill 回调异常逐个隔离不阻断主链✓ | order_manager.py:544-548,221-227 | 记录 | grep 已列 |
| D | 旁系双通道：aggregate_root_manager.py:235 与 saga:709 对**同一 fill 双 apply_fill 通道**，仅靠 PositionTracker dedup_store（配置才生效）兜底——双份承载嫌疑（checklist#4 邻近），当前因 Saga 零接线未触发 | aggregate_root_manager.py:216-235 vs saga:709 | P2 | 同 fill 走两链观察入账次数；查 dedup_store 装配点 |
| E | **Saga 零生产接线（孤儿死码，checklist#8）**：grep 全仓 OrderExecutionSaga=仅自身/测试/文档；TradingSession 未 import、ExecutionEngine 零引用。蓝图 [CONSUMERS]/INVARIANTS 声称的补偿/超时/拒单接管保障在生产路径不存在——文档口径 vs 实际接线漂移 | order_execution_saga.py:5,8 + grep 实证 | P1 | `grep -rn "OrderExecutionSaga" src/ scripts/ --include=*.py` 排除自身 |
| E | **部分成交余量失控（接线即触发）**：_FillCollector 只收第一笔 fill（event.is_set 即弃，:233）→ 首笔部分成交即走 step5/6 → step6 直赋 order.status=FILLED（绕过 FSM 封装，:735-737）→ Saga 返回 COMPLETED，余量仍挂交易所无人撤、补偿矩阵无余量条目——余量敞口失控+本地假 FILLED | saga:231-251,731-740,33-38 | P1 | mock broker 首笔回 1/3 量 fill，断言 COMPLETED 且无 cancel |
| E | 重复触发：execute 对终态单拒重复执行✓；对 SUBMITTED 单重放经 FSM SUBMITTED→SUBMITTED ValueError→ORDER_REJECTED✓——OrderManager 层重放防护成立；但 create_order 每次新 uuid idempotency_key，调用方层无业务幂等键（根因已记 X01 P1-1） | saga:414-424; order_manager.py:239-252 | 通过 | 重放 execute 断言 ORDER_REJECTED |
| E | 超时补偿链质量高：超时→撤单；撤单失败或已终态均强制查终态（AI-R3 P1 治本防吞成交）；有成交补走 step5/6、PARTIAL 按已成交量恢复；成本价不可得宁缺账不错账（ATK-6 critical）✓ | saga:464-482,771-838 | 通过 | test_saga_timeout_recovery.py 含此路径（81 passed） |
| E | 静默失败：_step5 失败回滚持仓后仅 INFO 日志——真实订单已成交而本地账被反向冲销，账实漂移无 critical/告警；step1/2 异常吞进 ctx.error 无审计事件 | saga:855-884,572-575 | P2 | 造 tracker.apply_fill 抛异常查日志级别 |
| E | submit 失败状态死角：先转 SUBMITTED 再调 broker，broker 抛异常后停留 SUBMITTED、无人转 REJECTED——"疑似在途"无超时回收（仅日终 expire 兜底）；与 X01 P2-3 同根因 | order_manager.py:294-316 | P2 | mock broker 抛异常断言状态停留 SUBMITTED |
| E | 时序：迟到 fill（EXPIRED/CANCELLED 后到达）入 _fills+触发回调但状态机拒绝转移（warning 跳过）——入账与状态死角靠盘后对账收敛，衔接依赖 eod_reconciliation | order_manager.py:533-542 | P2 | 过期后注入 fill，断言已入账而状态未变 |
| E | 并发：create/_orders 无锁 vs _on_fill 持 _fill_lock——状态转移判定存在窄竞态窗口（GIL 下字典读写原子、转移判定非原子）；当前调用方（session rebalance 持锁）实际串行化 | order_manager.py:170,253-256,493-542 | P3 | 压测并发 create+fill 观察转移异常 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

1. **Saga 编排模式用于订单执行事务**：**受阻**——WebSearch 连续 3 次上游 429 限流（2026-09-18），无法取得 URL+发布方+年份实证，按纪律记受阻不算查无。方向性备注（不作对等断言）：公认参考为 microservices.io（Chris Richardson）Saga pattern 页与 Microsoft Azure Architecture Center "Saga distributed transactions" 指南；业界共识要点（补偿幂等、超时≠失败需查询终态、部分成交不可盲目回滚）与本对象超时补偿链设计方向一致。收口方可补检索。
2. **部分成交处理语义**：立卡候选。业界订单系统对 partial fill 的通行语义是"剩余量保持活跃+按需撤余量+仅以已成交量入账"（FIX 协议 OrdStatus=PartiallyFilled 语义；本次检索受阻，来源待补）。本对象"首笔 partial 即 COMPLETED+强改 FILLED"与该语义相悖——接线前必须先修（P1-2）。

## 4 缺陷清单

**P1-1 OrderExecutionSaga 零生产接线（孤儿死码，checklist#8 命中）**
- 现状：Saga 及其补偿/超时恢复/拒单接管能力全仓无生产调用方；TradingSession 直连 OrderManager 裸路径下单。
- 证据：order_execution_saga.py:5,8（声称消费方与保障）；grep 实证 TradingSession/ExecutionEngine 均零引用。
- 影响：声称的钱路径保障纸面化；蓝图-代码口径漂移；Saga 内部缺陷（P1-2）因未接线未被生产暴露。爆炸半径=全链信任面。
- 建议修法：二选一——(a) 装配层把 TradingSession._validate_and_submit 改走 Saga（先修 P1-2）；(b) 登记 Saga 为模拟域专用并在蓝图标注生产未接线，消除口径漂移。
- 验证法：grep 复核；对照 qmt_trading_session 装配链确认无 Saga 注入点。

**P1-2 部分成交首笔即 COMPLETED，余量失控+状态假 FILLED（接线即触发）**
- 现状：_FillCollector 只捕获第一笔 fill；step6 无条件把非终态订单直赋 FILLED；补偿矩阵无余量撤单条目。
- 证据：saga:233、:735-737、:33-38。
- 影响：若按 P1-1(a) 接线，实盘部分成交余量无人管理（敞口+资金占用失控），本地台账假 FILLED 与券商漂移。爆炸半径=全账户在途单。
- 建议修法：collector 改累计制（持续等待至累计成交≥订单量或超时）；step6 仅在累计成交≥订单量时置 FILLED，否则保持 PARTIAL 并在超时分支撤余量。
- 验证法：单测 mock 两笔 fill（1/3+2/3）断言等满全额；单笔 1/3+超时断言余量被 cancel。

**P2-1 `_pending_orders` 死字段只增不减**（order_manager.py:162,254；grep 全仓无读者；内存慢泄+误导；修法：删除；验证法：grep）。
**P2-2 超额成交无上限防御**（order_manager.py:521-533；修法：filled_quantity>quantity 拒收+告警；验证法：注入超额 fill 单测）。
**P2-3 IDEMPOTENT_RETURN 假闸**（order_manager.py:127；全仓无"返回已存在id"实现；修法：实现或删枚举；验证法：造 error_code=-3 观察行为）。
**P2-4 broker_order_id 契约无校验**（order_manager.py:309-310；返回 None 时撤单链变纯本地撤单、柜台单不可撤；修法：submit 后断言非空否则按失败处理；验证法：mock 返回 None）。
**P2-5 submit 失败停留 SUBMITTED 无回收**（order_manager.py:294-316；与 X01 P2-3 同根因双面记录；修法：except 转 REJECTED 或入"疑似在途"复核队列；验证法：mock broker 异常查状态）。
**P2-6 step5 回滚漂移仅 INFO 级**（saga:855-884；真实成交被本地反向冲销仅 info；修法：升 critical+对账标记；验证法：造 tracker 异常查日志级别）。
**P2-7 fill 双应用通道并存**（aggregate_root_manager.py:235 vs saga:709；仅靠 tracker dedup_store 配置兜底；修法：明确唯一入账链+dedup_store 强制装配；验证法：同 fill 双链注入查持仓增量）。
**P3**：①_step1 target_weight 以 order_value/nav 近似弱化风控口径（saga:528-534）；②orders 属性 setter 可整体替换内部台账（order_manager.py:188-191）；③迟到 fill 状态死角靠盘后对账（order_manager.py:533-542）；④create/_orders 与 _fill_lock 并发窄窗口（order_manager.py:170,253）；⑤Saga 5s 超时硬契约 vs 实盘文件桥延迟适配未验证（saga:202-210，联动 X08）。

## 5 挂起疑问

1. P1-1 需 Owner 裁定方向：接线 Saga（先修 P1-2）还是降级登记为模拟域设施——涉及蓝图 MOD-EX-057 生产语义。
2. PositionTracker dedup_store 在生产装配点是否配置（决定 P2-7 实际风险等级）——装配真源未在本次范围。
3. eod_reconciliation 是否覆盖"迟到 fill 状态死角"的账实收敛——归对账链审查。

## 6 完备性自评

- 六轴全查：A（FSM/均价公式/分类表/超额四问）、B（broker 返回契约）、C（消费方+爆炸半径）、D（双应用通道）、E（五问逐条：静默=P2-6、假阳性=P2-3、断了没人知道=P2-5、重复触发=通过、时序=P3-③⑤）、F（受阻如实记）。
- 长尾：①rejection_action_handler 内部动作实现未逐行（Saga 侧消费契约已核）；②audit_journal 哈希链完整性未验；③PositionTracker dedup 实现细节未深审。

## 7 收口裁定（收口方填）
- 三态逐条：
- 修复 commit:
- 复检结论:
