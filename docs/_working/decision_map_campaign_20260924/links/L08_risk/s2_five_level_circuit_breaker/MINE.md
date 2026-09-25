---
ttl: task_bound
title: RSK-2 MINE
---

# RSK-2 交易五级熔断 + 磁盘影子 — 深挖簿

> 车道 L08 风控 · 子块 2 · 班次 st-qmine-20260925 · 只读挖掘（**未触发/未复位任何熔断，未跑测试**）。
> 起点真源=`../SKEL.md` §1/§2 RSK-2 与 §7 演练手册。本簿的核心产出=**对骨架"已接电"判定的三处实测修正 + HALT 演练前置缺口（TRD-A12/L08-C02 能否通过的真答案）**。

## ① 职责一句话

把交易资金安全侧的五级熔断（POSITION_LIMIT / DAILY_LOSS / CIRCUIT_BREAKER / SECOND_LEVEL / API_TIMEOUT）做成"判定→置闸→磁盘影子→重启重臂"的可持久化开关，供逐单硬闸与编排器查询。

## ② 现状实测（生产触发面判定：**部分覆盖未接电**——与骨架判定不同，逐条给证据）

**重要更正（骨架/13 号文把三条不同熔断机制混成了"一套五级+逐单闸通"）**：仓内实存**三套并行熔断机制**，本块只拥有其中一套。

| 机制 | 真源码位 | 生产触发面 | 生产消费面（谁因它而拒单/清算） |
|---|---|---|---|
| 甲：**五级模块**（本块主体，MOD-INF-016） | `trading/trading_contracts/risk/trading_kill_switch.py:71-112`（五级常量）、`:130-145`（trigger/reset+落盘钩子）、`:148-149` active_switches、`:152-165` evaluate 自动判定 | **判定腿未接电**：`evaluate()` 在 `src/` 与 `scripts/` **零调用方**（本班全仓 grep `trading_kill_switch` 命中仅 config 登记/测试/编排器适配器）；`trigger()/reset()` 生产侧唯一可达入口=编排器适配器 `kill_switch_orchestrator.py:169-186`，其上游是人工/AI 行为域 route（非行情判定） | **零**：`active_switches()` 在 src 内仅被编排器 `is_tripped` 查询消费（`:187-191`）——**逐单闸门读的并非本模块**（见乙） |
| 乙：**DefaultRiskValidator 单布尔熔断**（真正卡单的那把闸） | `risk/implementations/default_risk_validator.py:135-172`（含自带持久化记录 `record["active"]`、fresh boot 取默认值）、`:335`（置位）、`:399`（复位）、`:447-448` property；`:71` `GHOST_KILL_SWITCH_ACTIVE="kill_switch_active_but_position_remains"`（幽灵检测） | **已接电（实码+生产装配实证）**：`ex_core/trading_session.py:494-507 _detect_kill_switch_probe`（探针真源=`self._risk_validator.kill_switch_active`，取不到真源→None→闸门记 DEBUG 静默放行）→ `:527-533` 装配进 `PreExecutionChecker(kill_switch_probe=probe)` → `pre_execution_checker.py:234-252` 闸门 1；显式装配实证=`scripts/start_paper_session.py:565`（`kill_switch_probe=lambda: validator.kill_switch_active`） | 逐单拒单（在产）+ `risk_manager_orchestrator.py:373`→`position/core/position_limit_enforcer.py:271-285`（激活即强裁仓位）+ `risk/core/alert_generator.py:235-253`（激活即 RED 告警）+ `strategy_pipeline/promotion_advisory.py:670-672`（激活即暂停策略转正）+ `daily_decision_orchestrator.py:616`（`D6_kill_switch_active` 降级标记） |
| 丙：**编排层保命仲裁点**（真正清算的那条链） | `ex_core/risk_layer_orchestrator.py:114`（A1 单一仲裁点 `_engage_kill_switch`）、`:76-85` check_bankruptcy_floor、`:638,1690-1775`；执行体 `risk/stop_loss.py:98 trigger_kill_switch`、`:282 execute_kill_switch_liquidation`（15 笔/秒+event_id 幂等+LIQUIDATING 锁） | **已接电**：`evaluate_intraday` 由 `trading_session` 每轮调仓驱动（`live_readiness/live_admission_checklist.md:25` R5 绿档；`37_liquidity_crisis_protocol.md:236` 记 LEVEL_3 逃生→`_engage_kill_switch` 2026-08-17 落地） | 状态层 `trigger_kill_switch`→乙 的置位 + 强清发单 |

**磁盘影子实测**：
- 写路径（`kill_switch_state_store.py:60-90`，原子 tmp→os.replace）实码在盘；`data/runtime/trading_kill_switch_state.json` 现存 326B，`saved_at=2026-09-25T03:49:18Z`，五级全 `false`。
- **但写路径的实证生产者不是生产事件链**：`tests/autonomy/test_kill_switch_orchestrator.py:292-311` 直接 import 真模块并 `reset(level)`，而 `reset()→_persist_state()→save_state()` **无路径注入参数**（`:119-127`）→ 写死到生产默认路径（`DEFAULT_STATE_RELATIVE`，`:50`）。同类：`.runtime/audit/kill_switch_orchestrator.jsonl` 现存 **14 行全为 trip、零 reset 行**，reason 字段=`redteam-probe`(2)/`rb-cross-process`(12)，时间 2026-09-18/19 → **编排器对 trading 域的真实拉闸记录全部来自红队/弹性演练脚本，且演练后未走编排器复位通道留痕**。
- 结论：运维红线 6（测试禁写生产路径）在本块**已被违反**（新缺口 L08-C17）；骨架 §2 RSK-2③"13 号文实测文件存在=真实写路径已走过"的推证**强度不足**（写者可能是测试），生产写侧事件链仍**无实证**。
- 读路径 `rebuild_from_disk()`（`:93-143`）**已于 2026-09-25 接线**：`ex_core/trading_session.py:401` 在 `start()` 序列内调 `_rearm_kill_switches_from_disk()`（定义 `:434-459`，config 注入位 `:288 kill_switch_state_path`，`:448` 透传）。骨架 §2 RSK-2④"零调用方=断"已过期（该状态在 09-24 的 `fullflow_mining/m7_live_execution/02_kill_switch.md:28,42` 同记）。

## ②-bis **rebuild_from_disk 在 kill -9 恢复面上的代码洞（本班主产出，只读推演，未真跑）**

| # | 洞 | 证据 | 后果（对 HALT 演练/生产） |
|---|---|---|---|
| H1 | **重臂对象 ≠ 卡单对象**（决定性） | `rebuild_from_disk` 只 `trigger()` 甲模块（`:140`）；闸门 1 探针真源是乙（`trading_session.py:502`） | **SKEL §7 演练步骤 6"重启后提交新单→闸门 1 熔断探针拒单"必然失败**——重启失忆窗口的"拒单语义"并未因 L08-C02 接线而关闭，只是甲模块自己记住了。TRD-A12 现状=**代码已接、闭环未成** |
| H2 | `evaluate()` 旁路持久化 | `trading_kill_switch.py:160-162` 直接 `ks.active = True`，**不经 `trigger()`→不落盘** | 唯一"自动判定"腿（若将来接线）产生的熔断态**永不进影子**；kill -9 即蒸发。SKEL §7 步骤 1 备选触发法（"经 evaluate 注入"）踩此洞 |
| H3 | 影子无 per-switch 时刻/无交易日归属 | 载荷仅 `{level:{"active":bool}}` + 全局 `saved_at`（`:70-76`）；rebuild 冷却按 `now - saved_at` 算（`:132-133`） | ①任一其他级别的 trigger/reset 刷新 `saved_at` → 连带改写 auto_reenable 级的冷却计时；②rebuild 内 `trigger()` 又回写影子（H4）→ 冷却钟被重启刷回零，**重启风暴=自恢复级永久锁死**；③影子无 `trading_date` 字段 → 崩溃日遗留的 active=true 会在**次日**开盘重臂（DAILY_LOSS `auto_reenable=False`，无自解路径），缺"日切清影"代码 |
| H4 | rebuild 副作用重写影子 | `:140` 在循环内调 `trigger()` → `_persist_state()` → `save_state()`（N 次全量快照，`saved_at=now`） | 恢复过程改变被恢复对象的时间语义（与 H3 复合）；同时使"影子=崩溃瞬间原貌"这一取证前提失效 |
| H5 | 影子损坏/缺失 fail-open | `:113-121` 返回 `[]` + CRITICAL；`trading_session.py:443-451` 钩子异常仅 CRITICAL 后 `return`（不阻断启动） | 全 false 的"干净影子"与"损坏影子"在生产观感相同（都放行）；主保护（闸门 1）读的又是乙（H1）→ **甲侧不存在任何 fail-closed 兜底**。合成测试设计（不跑生产）：给损坏 JSON 断言"启动不阻断"现在会通过，缺的是**断言"必须有降级告警事件"** |
| H6 | 枚举字符串键查表 | `:128 KILL_SWITCHES.get(level_name)` 以 str 查 `dict[KillSwitchLevel, ...]`，依赖 `KillSwitchLevel(str, Enum)` 的 str-mixin 哈希巧合（现由 `tests/trading/test_kill_switch_state_store.py:54-91` 绿灯间接锁住） | 若枚举去 str 基类/改名→`continue` **静默零重臂**（无 warning 分支）；低成本加固=命中失败计数 + 未识别级别 WARNING |
| H7 | 影子路径为仓库级单文件 | `DEFAULT_STATE_RELATIVE` 单一路径；`save_state` 无 session/broker/env 维度键 | 多会话（sim+paper、多策略）共享一把闸：A 会话 DAILY_LOSS 会把 B 会话一起重臂。当前 `十余车道在跑` 语境下是真实耦合面 |

## ③ 六向台账

| 向 | 台账 |
|---|---|
| 上游 | 判定注入 `evaluate(condition, evaluator)`（调用方给 evaluator，`:152-165`，**生产零调用方**）；人工/编排 `trip("domain","trading[:LEVEL]")`（`kill_switch_orchestrator.py:581-602`，空目标=五级全拉 `:174-176`）；系统级传播（`:556-567`，RSK-1 L08-C12）；`config/governance_operations_map.yaml:91,265-266`（运维地图登记） |
| 下游 | 编排器状态查询 `is_tripped`（唯一 src 消费）；`pre_execution_checker` 闸门 1（**经乙 而非甲**）；甲自身无清算动作（发单唯一真源=丙 `_engage_kill_switch`→`stop_loss.execute_kill_switch_liquidation`）；`ai_layer/redline/sev_router.py:18` 把 `trading_kill_switch` 列为 SEV 信号源（测试 `test_sev_router.py:108` 反而断言 redline **不得** import 本模块——红线域刻意解耦） |
| 算法/机制 | 五级阈值常量：DAILY_LOSS=`daily_pnl < -0.03*aum` 且当日不自恢复、CIRCUIT_BREAKER=连续拒单≥5 或价差>5%、SECOND_LEVEL=延迟>1000ms 或成交率<50%、API_TIMEOUT=超时>10s 或心跳失联≥3（`:71-112`）；`cooldown_seconds + auto_reenable` 双参数自恢复；影子版本 `_STATE_VERSION=1`；重臂"纯加闸不加放"不变量（`:10`） |
| 后端 | 进程内模块级全局 `KILL_SWITCHES`（可变 dataclass/模型，无锁）；`_persist_state` fail-open 钩子；`os.replace` 原子写；`default_state_path()` 经 `zephyr.shared.io.paths.REPO_ROOT`；启动侧装配=`TradingSession.start()` |
| 前端 | 未查得面板消费实证；`risk/core/alert_generator.py:235-253` 把乙的激活态映射为 RED 告警（甲无对应告警语义）；`echo-guard.yml:134` 把 `trigger\|\|reset` 登记为 stable_key（改动需过回声闸=治理面而非 UI 面） |
| 数据字段 | 影子：`version`/`saved_at`(ISO, UTC)/`switches.{LEVEL}.active`；**缺字段**：per-switch `triggered_at`、`trading_date`、`reason`、`actor/approver`、`session_id`（H3/H5/H7 的共同根因）；编排器侧另有 jsonl 的 `reason/approver` 字段但**不落进影子**→拉闸理由与熔断态两张皮 |

## ④ 缺口清单（本层新增；SKEL §4 已立项引用不重复）

| # | 缺口 | 判级 |
|---|---|---|
| L08-C18 | **H1 闭环未成**：重臂对象与卡单探针不同源。三案（只出材料不拍）：①探针取并集 `validator.kill_switch_active or bool(tks.active_switches())`（与仲裁序 v1"保守者胜并集"同构，改 1 处 lambda，零新组件）②rebuild 内追加 `validator.trigger_kill_switch()`（跨模块写态，破坏乙 的唯一真源）③判甲为"登记/演练用 advisory"并按 w5_1 把五级状态收编进乙（内收，动模块身份） | **P0（TRD-A12 的真前置，本班新发现）** |
| L08-C19 | H2 `evaluate()` 旁路持久化：自动判定腿未接电且一旦接电即失守 | P1 |
| L08-C20 | H3/H4 影子载荷缺 `triggered_at`/`trading_date`，重臂回写污染时钟；缺日切清影 | P1 |
| L08-C21 | H5 损坏影子与干净影子不可分辨且无降级告警事件 | P1 |
| L08-C22 | H7 仓库级单影子文件 = 多会话串闸 | P2 |
| L08-C17 | 测试/红队直写生产影子与 jsonl（红线 6 违反）+ 演练 jsonl 有 trip 无 reset（复位留痕不闭环） | P1（纪律面） |
| 引用不重复 | SKEL L08-C02（接线，**代码侧已落地，闭环差 H1**）、L08-C05（reset 权限闸）、L08-C01/TRD-A13（双五级仲裁序）、L08-C06（流转全史物化表）；`p0_money_path/rpt_x05.md:36`（探针 None 时仅 DEBUG 静默放行，已由他班立项，本班附证不重登） | 已在账 |

## ⑤ 自审闸三态裁定

**MINING**。理由：骨架判 SEALED 的两条支柱（"自动触发在产"、"逐单拦截=甲模块"）被本班实测推翻，且新增 H1-H7 七条代码洞，需再钻 33 号/丙侧正文才能封。
未读指针清单（MINING 债）：①`ex_core/risk_layer_orchestrator.py` `_engage_kill_switch` 正文（是否同时置乙/记甲——决定 H1 是否已有半桥）；②`risk/implementations/default_risk_validator.py:120-220` 持久化记录真源（JsonStateStore 键与命名空间，决定甲乙能否同影）；③`tests/trading/test_kill_switch_state_store.py::TestKill9Drill` 三例断言强度（是否只测甲 自环=H1 盲区来源）；④`algo_flow/trading_kill_switch.yaml`、`kill_switch_state_store.yaml`；⑤`docs/03_modules/_cross_layer/shared_core/blueprint.md` MOD-INF-016 身份声明；⑥`scripts/start_paper_session.py` 熔断相关装配全文（生产事件链真装配面）。
**不得以"现状规模小/演练未跑"封矿**（量尺=终局全貌：Owner 一人 + 100% AI 自制，五级熔断必须既有自动判定腿又有可信重臂腿）。

## ⑥ 挖矿日志

1. 读 `../SKEL.md` 全文 → 抓出 §7 演练手册的隐含假设"重臂→闸门 1 拒单"，定为验证目标。
2. Grep 全仓 `rebuild_from_disk|_rearm_kill_switches_from_disk` → 发现接线已于 09-25 落地（骨架状态过期）。
3. Read `kill_switch_state_store.py` 全文（144 行）→ H3/H4/H5/H6。
4. Read `trading_kill_switch.py:108-166` → **H2**（evaluate 旁路 persist）。
5. Grep `trading_kill_switch|active_switches()`（排除 docs）→ **甲模块在 src 零判定调用方、零拒单消费方**。
6. Grep `pre_execution_checker.py` 内 kill_switch → 拿到探针类型 `KillSwitchProbe=Callable[[],bool]` 与"生产接线: DefaultRiskValidator.kill_switch_active"注释。
7. Grep `kill_switch_probe|kill_switch_active` 全仓 → 乙模块及其 5 处真实消费面（拒单/仓位强裁/RED 告警/转正暂停/降级标记）。
8. Grep `trigger_kill_switch|engage_kill_switch|execute_kill_switch_liquidation` → 丙仲裁点链与历史评审（`_archive/2026-08-16-dual-review-adjudication.md` P0 风控接线批）交叉印证。
9. Read `trading_session.py:370-460` 与 `:490-545` → start 序列次序（先 `reset_daily_circuit_breaker` 再重臂）+ 探针自动反查逻辑。
10. Bash 只读：`data/runtime/trading_kill_switch_state.json` 内容/时间戳、`.runtime/audit/kill_switch_orchestrator.jsonl`（14 行，全 trip 无 reset，reason=红队）。
- 纪律：全程只读；**未触发/未复位任何熔断**（含 sim/paper）；未跑测试；未动 `D:\zephyr_t1_backup\`；无 git 写。
- 外部对表：未做（车道纪律，留统一轮）。
