---
ttl: task_bound
title: 深度审查作业簿——KillSwitch清仓链
owner: st-deeprev-20260918
created: 2026-09-18
reviewed: 2026-09-18
---

# 深度审查报告：KillSwitch清仓链（K01）

- 状态: **已审**
- 级别: P0｜类型: 闸门
- 基线 commit: 2fa92002c3（已核实 9 个目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/risk/stop_loss.py:98(:282/:545)`；SSoT 委托 `src/zephyr/risk/implementations/default_stop_loss_engine.py`、状态仲裁 `src/zephyr/risk/implementations/default_risk_validator.py:67-125`
- 生产调用方（实测 grep）: 唯一生产触发链=`src/zephyr/ex_core/risk_layer_orchestrator.py:1722-1773`（_engage_kill_switch），生产装配=`scripts/start_paper_session.py:457-475`（传 state_store+kill_switch_owner）
- 测试文件: tests/risk/test_kill_switch_state_persistence.py（15 用例全绿）；tests/risk/test_l04_risk_management.py:483-510；tests/trading/test_stop_loss.py（14 用例）；tests/trading/test_trading_kill_switch.py **实为另一模块**（zephyr.trading.trading_contracts.risk.trading_kill_switch，非本对象）
- 运行结果: `python -m pytest tests/trading/test_stop_loss.py tests/trading/test_trading_kill_switch.py tests/risk/test_kill_switch_state_persistence.py -q` → 54 passed（Python 3.12.8）

## 1 对象快照

- **范围**：stop_loss.py 全文件（触发事件层 trigger/reset + 清算执行 execute_kill_switch_liquidation + 幽灵持仓检测 detect_ghost_positions + 止损兼容层 evaluate_stop_loss）及其直接依赖 default_stop_loss_engine.py、default_risk_validator.py 状态仲裁面、shared/state_store.py 锁语义。
- **排除项**：drawdown_watchdog/drawdown_session_persistence 全文（只审其作为 K01 消费方的接线状态）；RiskLayerOrchestrator 全文归 K01 的调用面证据（该文件不在 9 对象清单，但其 _engage_kill_switch 是本链唯一生产入口，不审则链断）。
- **材料缺项声明**：运行时证据包（近 N 天 CRITICAL 日志）未取；数据画像未取；轴 F WebSearch 见 §3。
- **测试覆盖概况**：持久化/幂等/损坏/活持仓 15 用例质量高（信任）；止损四模式有边界用例但**把"未知 method 静默回退 5%"锁死为正确行为**（test_l04_risk_management.py:503）；跨进程并发零覆盖。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 清算"成功"=订单被受理而非成交：place_order 返回即记 liquidation_orders，无成交确认、无事后持仓复核，all_success=True ≠ 已平仓 | stop_loss.py:477-490,508-521 | **P1** | mock 一个"受理但永不成交"的 broker 调 execute_kill_switch_liquidation→报告 all_success=True |
| A | T+1 未适配：当日买入持仓无法卖出，无 T+1 过滤/无次日重试计划；清算报告只留 liquidation_errors 全文无 t+1/T+1 字样 | stop_loss.py:474-500（全文） | **P1** | 全文 grep "T+1/t+1"=0 命中；构造当日买持仓走清算→券商拒单进 errors 后无人接手 |
| A | 跌停不可成交未适配：MARKET 单跌停封板不成交，同 P1 根因（受理≠成交），无升级路径 | stop_loss.py:481-482 | **P1** | 同上 mock 场景；真实剧本=跌停日触发熔断 |
| A | 600s 陈旧锁租约 < 极端清算时长（15 笔/s+每批 1s，>9000 标的即超租约）→ 接管者与原 owner 并行发单（跨进程/崩溃恢复场景）；长-only 账户由券商拒超额兜底，但超额卖单=合规噪音 | stop_loss.py:210,388-419 vs 454-506 | P2 | 算术：ceil(N/15)+N/15-1 秒 vs 600；N>9000 即破 |
| A | 跨进程无真锁：_LIQUIDATION_LOCK=threading.Lock 仅进程内；JsonStateStore 整记录替换无 CAS/文件锁，双进程可同过 LIQUIDATING 检查→双清算 | stop_loss.py:204,361-425；state_store.py:128-131,147-171 | P2 | 两进程各起一条线程对同一 root_dir 调 execute（不同 event_id）→ 双双发单 |
| A | 幂等重放缓存 completed 封顶 100 条，淘汰后同 event_id 重放会**重新发单** | stop_loss.py:205,531-535 | P3 | 灌 101 次完成记录后重放第 1 条 event_id→再次进入清算 |
| A | trigger_kill_switch 不校验 scope（execute 校验），两入口契约不一致 | stop_loss.py:98-114 vs 338-342 | P3 | 传 scope="foo" 调 trigger→正常返回 triggered |
| A | 未知止损 method 静默回退 5% 固定止损（typo=fail-silent），测试反而锁死该行为 | default_stop_loss_engine.py:173；tests/risk/test_l04_risk_management.py:503 | P2 | 调 evaluate(rules={"method":"fixed_prc"})→按 5% 跑不报错 |
| A | trailing 高水位存模块级单例 `_engine` 内存：重启即清零且 rules 不带 highest_since_entry 时静默弱化 | stop_loss.py:75；default_stop_loss_engine.py:78-80,160-165 | P2 | 重启进程后调 evaluate trailing→highest=current→永不触发 |
| A | naive entry_date 按 UTC 解释（北京时区差 8h，仅跨日边界受影响）；volatility 止损缺 current_volatility 静默用默认 0.02 | default_stop_loss_engine.py:134-139,168-171 | P3 | 传 naive 北京时间 entry_date 看 held_days |
| B | 持仓快照上游：编排器过滤 isfinite 后传入；但 stop_loss 自行兜底路径 `_resolve_live_positions` 的 float(qty) 不查 NaN/inf（NaN qty→发 NaN 单被券商拒） | stop_loss.py:230-279；risk_layer_orchestrator.py:1748-1755 | P3 | broker.get_holdings 返回 {"X": float("nan")}→abs(nan) 传 place_order |
| B | 券商查询失败降级调用方快照（WARNING 留痕），方向正确但降级后"实时持仓"承诺失效——降级本身只有 WARNING 无告警路由 | stop_loss.py:244-279 | P2 | mock get_holdings 抛异常→静默用快照继续清算 |
| C | **Ghost 残仓双检测链全孤儿**：drawdown_watchdog.poll_once 与 drawdown_session_persistence.premarket_initialization 在 src/scripts 零调用方（模块头自认"未接入任何事件通道"）→ 清算失败后的独立复核层不存在 | drawdown_state_machine.py:6（自认头注）；grep poll_once/premarket_initialization 零生产命中 | **P1** | `grep -rn "poll_once\|premarket_initialization" src/ scripts/` 排除定义文件=0 |
| C | 清算异常被编排器吞成内存报告（status=liquidation_error），报告仅存 `self._kill_switch_report` 无任何下游消费 all_success → 失败后无人接手、无自动重试 | risk_layer_orchestrator.py:1765-1773；grep `_kill_switch_report` 消费=仅同文件 | **P1** | mock execute 抛异常→返回占位报告后全链无动作 |
| C | evaluate_stop_loss 兼容层零生产调用（仅 tests/governance/test_e2e_pipeline.py）；DefaultStopLossEngine 在 default_risk_manager_orchestrator 实例化但 `_stop_loss_engine.` 零调用=死接线；per-position 止损生产真源是否为 K06 ashare 引擎→见 rpt_k06 交叉 | grep evaluate_stop_loss 生产=0；grep "_stop_loss_engine\." default_risk_manager_orchestrator.py=0 | P2 | 两条 grep 均零命中 |
| C | 模块级 reset_kill_switch 零生产调用（复位实际走 DefaultRiskValidator.reset_kill_switch）；双复位入口漂移风险 | grep stop_loss.reset_kill_switch 调用=0 | P3 | grep 验证 |
| D | kill switch 状态承载≥4 处：validator 持久化记录（真源）/stop_loss 事件层/trading_kill_switch 5 级内存注册表（KILL_SWITCHES）/DrawdownStateMachine KILL 态（未接线）——缺陷模式 #4 双份承载 | default_risk_validator.py:67；zephyr/trading/trading_contracts/risk/trading_kill_switch.py；drawdown_state_machine.py | P2 | 逐个 grep 状态字段载体并对照写入口 |
| D | detect_ghost_positions 双实现漂移：stop_loss 版（参数 kill_switch_state 默认 "OPEN"）vs validator 版（读 self._kill_switch_active，新增 GHOST_KILL_SWITCH_ACTIVE 类型）——同概念两处算 | stop_loss.py:545-590 vs default_risk_validator.py:401-444 | P2 | 对比两函数签名与情况 2 判定源 |
| E | 假阳性过关（该触发没触发→反向：触发后失守）：persist 失败仅 CRITICAL 日志，返回值无 persist 结果字段，调用方无法区分"已持久化"与"重启即丢"；进程内防护不失效但重启=解除 | stop_loss.py:128-150；default_risk_validator.py:337-352 | P2 | 断开磁盘（mock save 抛 OSError）调 trigger→返回 triggered 无异常 |
| E | 静默失败：owner 状态层触发失败被 `except Exception` 吞（"继续清算"）——若持久化同批失败，kill switch 只剩一行日志 | risk_layer_orchestrator.py:1726-1730 | P2 | mock owner.trigger 抛+store.save 抛→链路继续且无状态残留 |
| E | 时序攻击：engage 取 open_orders 快照→撤单窗口内新提交的订单不在快照中不会被撤（之后新单被 validator probe+pre_execution gate 拦，但已提交在途单可成交→成 ghost，而 ghost 复核链孤儿化见 C 轴） | risk_layer_orchestrator.py:1756-1763；start_paper_session.py:560-562 | P2 | 快照后、cancel 前插入 submit→该单存活 |
| E | 重复触发防重入：进程内闩（_liquidation_started）+event_id 幂等+测试覆盖（test_concurrent_double_trigger_only_one_round/test_same_event_id_replay_no_duplicate_orders）——**进程内闭环扎实**；跨进程漏洞见 A 轴 | risk_layer_orchestrator.py:1707-1719；tests/risk/test_kill_switch_state_persistence.py:146,178 | 已查无（进程内） | 已有测试即验证法 |
| E | 边界：空持仓/空挂单/scope=order 均正确跳过；锁记录损坏 Fail-Closed 拒绝进入；锁释放失败 Fail-Safe 留 CRITICAL+600s 后可接管 | stop_loss.py:429,456-457,365-375,537-542 | 已查无 | 已有测试 test_corrupt_lock_fail_closed 覆盖 |

## 3 SOTA 对照

- **Crash-only 状态外部化**：对标 NautilusTrader crash-only 恢复（代码头注自认，state_store.py:44-45）；业界做法一致（数据库/文件外部化+启动恢复），**对等已有**。
- **Kill switch 监管语境**（程序化交易熔断/kill switch 功能，SEC 15c3-5 market access、MiFID II RTS 6 算法交易 kill 功能、中国程序化交易新规申报速率阈值）：见本战役轴 F 检索记录（rpt_k02 §3 汇总检索，其中"15 笔/秒"与新规高频认定阈值口径问题在 K02 报告复核）；**待收口方对 15 笔/秒的法规出处立卡核实**——代码注释自称"A 股 2026 新规限频"（stop_loss.py:291-294），公开规则文本中高频认定阈值并非 15 笔/秒量级（详见 K02 §3），注释口径存漂移嫌疑。
- 搜索受阻项：无（检索记录见 K02 报告 §3，本报告引用其结论）。

## 4 缺陷清单（按严重级排序）

1. **[P1] 清算完成语义=受理非成交 + 成交复核链孤儿化**（A×3 合并）：现状→place_order 返回即计成功，无 fill 确认/无事后持仓复核；独立复核层（watchdog L3 强平裁决、盘前 ghost 拒启）双双零接线；报告 all_success 无人消费。影响→跌停日/T+1 日触发熔断，系统报"executed/all_success"而残仓裸奔至人工发现；爆炸半径=全账户。建议修法→清算后轮询 broker 持仓直到为 0 或超时（可复用 K09 drawdown_liquidation_guard 的超时保护——注意 K09 本身接线状态见 rpt_k09）；watchdog/premarket 二选一接入生产。验证法→mock 永不成交 broker 断言报告与真实持仓差。
2. **[P1] T+1/跌停无差异化处置**：当日买入仓与跌停封板仓必然失败但被混入普通 errors，无次日自动重清计划（重启只禁新单：start_paper_session.py:543-545 打印熔断态）。建议→liquidation_errors 分型（T+1/跌停/其他）+ 次日开盘自动重清算任务（事件触发，守 §9.3 禁 cron）。验证法→构造当日买持仓剧本看是否有任何后续动作。
3. **[P2] 跨进程双清算窗口**（A4+A5 合并）：threading.Lock+整文件替换无 CAS；600s 租约可短于执行时长。建议→文件锁（msvcrt/portalocker）或 save 前二次 load 校验 owner+时间戳 CAS。验证法→双进程集成测试。
4. **[P2] 触发持久化失败不可观测**：返回值加 persisted: bool 字段+告警路由；当前只有日志。验证法→mock save 失败检查返回 dict。
5. **[P2] 未知止损 method 静默回退**：改为抛 ValueError（fail-closed），同步修 test_l04:503。验证法→传 typo method 断言异常。
6. **[P2] trailing 高水位不持久化**：highest_since_entry 落 state_store（与 kill_switch 同机制），否则重启后 trailing 静默失效。验证法→重启进程模拟。
7. **[P2] 双 ghost 检测实现+双 kill switch 承载漂移**（D×2 合并）：收敛到单一实现/真源，停用副本或改委托。验证法→对拍两函数输出。
8. **[P3] completed 缓存淘汰致幂等失效 / trigger scope 不校验 / naive 时区 UTC 化 / vol 缺省静默 / NaN qty 不设防 / 双复位入口**：低危打包，随下次触碰该文件顺手修。验证法→各自单测。

## 5 挂起疑问

1. "A 股 2026 新规 15 笔/秒限频"的法规真源出处？公开程序化交易规则的量化阈值与此口径不一致（K02 §3 检索），需 Owner 裁定口径真源。
2. per-position 止损的生产真源是否全权归属 K06 ashare_stop_loss_engine？若是，本文件 evaluate 兼容层+DefaultStopLossEngine 是否可申请退役（规范预算净零）？
3. tests/trading/test_trading_kill_switch.py 测的是 trading_kill_switch 注册表（5 级 kill switch），该注册表在 K01/K02 之外是否另有生产接线？（grep KILL_SWITCHES 消费方待查，本报告按排除项处理。）

## 6 完备性自评

- 六轴全查：A/B/C/D/E/F 均有结论；E 轴"进程内重复触发/损坏锁/空输入"三问为"已查无"（有测试背书）。
- 长尾清单：① 运行时证据包（CRITICAL 日志近 N 天采样）未取——静默失败的实际发生率未知；② data/runtime/state 实际部署路径与权限未核实；③ Redis 后端（state_store_redis）与本链组合行为未审（生产用文件后端，start_paper_session 实证）；④ trading_kill_switch 注册表生产接线状态未深挖（挂起疑问 3）。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P1 清算受理≠成交+T+1/跌停无处置+复核双链零接线: 挂起登记(接线裁定)。'15笔/秒=新规'注释被上交所2025细则证伪。
