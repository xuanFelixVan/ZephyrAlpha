---
ttl: task_bound
session: st-ffchief-20261001
lane: lane-f82
parent: ../00_skeleton.md（总包骨架 I-07/F82 行）
scope: order_daemon 建成未接线（P0 断链）六向台账+最小接线施工记录
---

# F82 六向台账 — order_daemon 接线（订单与结算常驻 I-07）

> 挖矿 2026-10-01，施工同批。文件名说明：指令面指定的 `F82.md` 撞 lock_files 命名门
> （N-01/N-13 连续大写违 TRAE-028 snake_case），按宪法 §8 降为 `f82_order_daemon_wiring.md`，
> 内容即 F82 台账，语义零损。Owner 总授权自裁记日志。

## 0. 骨架行回放

I-07(F82) 订单与结算常驻｜上游 F57｜下游 F63｜件：post_settlement_pipeline.py、night_shift_queue.py、
ai_layer/scheduling/order_daemon.py（件在）｜断链=order_daemon 建成未接线（M5 在案 P0）｜盘后→夜班队列/recon。

**勘误先行**：`order_daemon` 实为 **L5 排产段工单生成守护**（胜者证据包→任务书 WO-*，非交易订单下单件）。
其设计真源=order_daemon.py 头注 blueprint（MOD-INF-037）+ `docs/_working/ai_layer_vision/L5_schedule_gate/DESIGN.md`。
"禁实盘/只 sim"红线天然满足：全链零券商接口，工单=任务书文本对象。

## 1. 六向台账

| 向 | 对象 | 实证（2026-10-01 挖矿时点） |
|---|------|---------------------------|
| ① 上游（谁喂） | L4/L2 胜者落库 → emit `evolution_winner_due`（SchedulingJournal，`.runtime/ai_scheduling/pending_events.jsonl`） | **全仓零 emit 方**（grep src+scripts 仅 scheduling 本体/self 引用）=守护恒饿死。L4 落库沿=`comparator.compare_events.archive_and_notify`（亦无生产调用方，L4 考场线未通）；L2 `intake_e2_handoff` 同样无人 emit（属 L2 卡车道） |
| ② 下游（谁吃） | Owner 确认（api `/api/schedulegate-confirm`→confirm_gate→emit `order_confirmed_due`→守护 ConfirmGate.reconcile）；dispatcher（order_dispatch_due 派工段）；L6/L7/L2 回执线（消费体预埋） | api 拍板路由已在（api_server 5389+/confirm_gate 头注"待接线一行"=前置三件未齐，非本车道面）；工单落库面曾缺（见④） |
| ③ 宿主/触发面 | blueprint `[STARTUP] event_driven`+`[INVARIANTS] 零定时器零轮询`（宪法 §9.3）→设计宿主=**DataScheduler task_completed 事件唤醒链**，非 cron/计划任务直挂 | **st-circ-a7（8c5117b600，2026-10-01 02:09）已接**：`pipeline_events.maybe_drain_order_daemon`（journal 非空才起 `OrderDaemon.process_once`，空=零成本跳过，异常 WARN 不反噬），装配点 `wire_data_scheduler`→`DataScheduler.__init__`（src/zephyr/data/scheduler.py:816-821）。骨架"未接线"记载相对 A7 已过时（本台账勘误） |
| ④ 工单落库面 | blueprint：sink"缺省=dry-run 只回执不落库"由宿主挂载；落点=`confirm_gate.OrderFileStore`（orders.jsonl，"已建守护链路快照落点"；PG `ai_scheduling.ai_work_order`=生产真源目标，DDL 在册） | **A7 spawn 未挂 sink=工单蒸发**（断链后半段，本车道治）；OrderFileStore 全仓零调用方（built-not-wired 第二处） |
| ⑤ 启动链三面 | config：`config/schedule_gate_policy.yaml`（policy 真源）+`config/evolution_schedule_seeds.yaml`（种子）+`config/tool_inventory.yaml:282` 能力卡 ai_scheduling_l5——**无 order_daemon 任务注册项=按设计**（事件驱动禁 cron）；Windows 计划任务：`ZephyrAlpha_DataScheduler` **正在运行**（schtasks 实证 2026-10-01）=唤醒宿主活体，无独立 order_daemon 任务=按设计；session_worktree 启动面：DataScheduler 构造即 wire（imported 注册，零线程零轮询） | 三面齐：宿主活+注册按设计+装配点在码 |
| ⑥ 数据字段 | journal 八轻 kind 契约（scheduling_events PAYLOAD_REQUIRED_KEYS）；任务书附录 A schema v0 十三字段（build_task_order 全实现）；criteria_hash 机检；堵点本 bottleneck_ledger.jsonl | 契约全在码，零缺字段 |

## 2. 断链裁定（挖矿结论）

A7 治了"谁唤它"（触发沿），F82 剩余断点两处：
1. **落库面**：spawn 缺省 dry-run→工单只进回执即蒸发→Owner 永远无单可确认（下游全空转）；
   且 `handle_winner` 硬编码 `order_seq=1`，同日多胜者 upsert 互踩同号=丢单。
2. **生产面**：`evolution_winner_due` 全仓零 emit 方→journal 恒空→触发沿永远 `journal_empty`。

## 3. 本车道落地（最小接线面，2026-10-01 st-ffchief-20261001）

| 件 | 变更 | 设计锚点 |
|----|------|---------|
| pipeline_events.py | `_order_store_sink(journal)`：spawn 挂 `OrderFileStore.upsert` sink+当日序号分配（仓内当日单数+1，单例锁内串化=幂等可停；sink 失败上抛→journal 事务语义保留事件） | blueprint sink 宿主挂载义务；upsert 按 order_id 原地替换=幂等 |
| comparator/compare_events.py | `maybe_emit_evolution_winner`（win/win_starred 转投 L5 journal）+`archive_and_notify` 归档沿同投（`winner_journal` 注入缝供测试） | DESIGN §1①"库外=verdict='win' 直达"；分层契约=journal 闸管键在场、语义完整度由守护必填机检 held_incomplete+堵点本（A7 实弹探针同款分层） |
| comparator/experiment_store.py | 快照补 `domain_id` 字段+from_row 映射（DB 列本就在，SELECT * 已取，此前漏映射=生产边拿不到必填三元之一） | ai_comparison_experiment DDL domain_id 列 |
| 测试 | test_pipeline_events.TestOrderDaemonSpawn：FakeDaemon 补 sink 形参+断言 sink 必挂；新增落库冒烟 2 件（胜者→orders.jsonl 落行；同日第二单序号 002）。test_compare_events：archive 三件补 winner_journal 注入+新增生产边 4 件（win/win_starred/draw/缺 domain_id 空串转运） | 全 tmp 注入零生产路径零券商 |

**幂等可停论证**（交易红线加码面）：消费=drain 成功才出队+offset 断点续读（重放零副作用）；落库=upsert 按 order_id 幂等；序号=锁内仓计数确定推导；停=KillSwitch 探针（drain 内建 fail-closed）+单例锁让位+零定时器零常驻。**全链无券商接口无实盘路径**。

## 4. 测试证据

`pytest tests/ai_layer/comparator/ tests/ai_layer/scheduling/ tests/strategy_pipeline/test_pipeline_events.py
--basetemp=.runtime/tmp/lane-f82` → **329 passed, 1 skipped**（skip=既有 sleeve_provenance 通道）。
ruff check/format：本批 5 件全绿（compare_events/experiment_store/test_compare_events 三件既有 format 漂移
一并治净防撞门，A7 同款）。模拟边界：工单=任务书文本对象，tmp_path 注入，零生产 .runtime 写、零下单。

## 5. 遗留缺口（如实登记，非本车道面）

1. **PG sink**：生产真源目标 `ai_scheduling.ai_work_order`（C2 DDL 在册）未接，快照文件仓为现行落点；
   文件快照 vs PG 谁为长期真源**未裁**（confirm_gate 头注在册+wiring_C_confirm_hardening 判据）。
2. **L2 库内路**：`intake_e2_handoff`（payload 带 labor_killed/card_id）全仓零 emit——L2 intake 卡车道面。
3. **archive_and_notify 生产调用方**：L4 考场线（executor/venue→archive）未通，本边随其点亮；
   `league_judge` promote 属策略席位轮换（非模块进化工单），语义不合不做直达桥（自裁记日志）。
4. **api 投影**：schedulegate 页列队投影读 seeds（骨架提案面），orders.jsonl 工单投影与 confirm
   硬化（鉴权真源/归档语义）待 confirm 接线三件齐。
5. **骨架总册**：00_skeleton.md F82"断链"记载相对 A7+本笔已过时，勘误见 §1③（总册归总包Owner 面，本车道不代改）。

## 6. 同件在途披露（连坐面）

pipeline_events.py 与 test_pipeline_events.py 含同会话兄弟车道 **lane-datapipe P2a**（journal 字节锁
`_byte_lock`+JOURNAL_LOCK_SUFFIX，2026-10-01 staged 完整态、claim 已过期回收）完整在途内容——本笔按
A7 [GW:overlap] 先例同件同袋披露随车，未改动其语义面。
