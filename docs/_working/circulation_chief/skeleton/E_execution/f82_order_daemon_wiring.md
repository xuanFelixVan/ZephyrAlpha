---
ttl: task_bound
session: st-ffchief-20261001
lane: lane-f82
parent: ../00_skeleton.md（总包骨架 I-07/F82 行）
scope: order_daemon 接线六向台账+端到端冒烟验证（W3-3 处方，sim/mock 级）
---

# F82 六向台账 — order_daemon 接线验证与补全（订单与结算常驻 I-07）

> 挖矿+施工 2026-10-01。路径史：指令面原指定 `fullflow_chief_20261001/skeleton/E_execution/F82.md`
> ——①文件名撞 lock_files 命名门（N-01/N-13 连续大写违 TRAE-028）降为 snake_case；②战役目录
> 撞 R5-DIGIT-SUFFIX 门（数字后缀目录禁令，bags q-0013/q-0021 实证死因）→ 总包改名
> `circulation_chief/`，本册随迁新路径。Owner 总授权自裁记日志。
> 任务收窄对齐：总包据 W3-2/W3-3 双路挖矿交叉印证通知"A7 已接线、任务收窄为端到端冒烟+落档，
> 勿重复接线"——本车道冒烟实证：**接线真实性=触发沿 1/3 真**（详见 §3），生产边+落库面两断边
> 为冒烟暴露的剩余断点，本车道最小面补齐（非重复 A7 的接线，A7 触发沿零触碰）。

## 0. 骨架行回放

I-07(F82) 订单与结算常驻｜上游 F57｜下游 F63｜件：post_settlement_pipeline.py、night_shift_queue.py、
ai_layer/scheduling/order_daemon.py（件在）｜断链=order_daemon 建成未接线（M5 在案 P0）｜盘后→夜班队列/recon。

**勘误**：`order_daemon` 实为 **L5 排产段工单生成守护**（胜者证据包→任务书 WO-*，非交易订单下单件）。
设计真源=order_daemon.py 头注 blueprint（MOD-INF-037）+ `docs/_working/ai_layer_vision/L5_schedule_gate/DESIGN.md`。
"禁实盘/只 sim"红线天然满足：全链零券商接口，工单=任务书文本对象。

## 1. 六向台账

| 向 | 对象 | 实证（2026-10-01 挖矿时点） |
|---|------|---------------------------|
| ① 上游（谁喂） | L4/L2 胜者落库 → emit `evolution_winner_due`（SchedulingJournal，`.runtime/ai_scheduling/pending_events.jsonl`） | 挖矿时**全仓零 emit 方**（grep src+scripts 仅 scheduling 本体/self 引用）=守护恒饿死；本车道补 L4 侧边（§3）。L2 `intake_e2_handoff` 仍零 emit（属 L2 卡车道） |
| ② 下游（谁吃） | Owner 确认（api `/api/schedulegate-confirm`→confirm_gate→emit `order_confirmed_due`→守护 ConfirmGate.reconcile）；dispatcher（order_dispatch_due 派工段）；L6/L7/L2 回执线（消费体预埋） | api 拍板路由在码（confirm_gate 头注"待接线一行"=前置三件未齐，非本车道面） |
| ③ 宿主/触发面 | blueprint `[STARTUP] event_driven`+`零定时器零轮询`（宪法 §9.3）→设计宿主=**DataScheduler task_completed 事件唤醒链** | **st-circ-a7（8c5117b600，09-30）已接**（W3-2/W3-3 印证属实）：`maybe_drain_order_daemon`（journal 非空才起 `process_once`）→`wire_data_scheduler`→`DataScheduler.__init__`（scheduler.py:816-821）。骨架"未接线"记载过时——本册即回写 |
| ④ 工单落库面 | blueprint：sink"缺省=dry-run 只回执不落库"由宿主挂载；落点=`confirm_gate.OrderFileStore`（orders.jsonl"已建守护链路快照落点"；PG `ai_scheduling.ai_work_order`=生产真源目标，DDL 在册） | 挖矿时 **A7 spawn 未挂 sink=工单蒸发**（OrderFileStore 全仓零调用方）+`handle_winner` 硬编码 `seq=1`（同日多胜者互踩丢单）；本车道补（§3） |
| ⑤ 启动链三面 | config：`schedule_gate_policy.yaml`（policy 真源）+`evolution_schedule_seeds.yaml`（种子）+`tool_inventory.yaml:282` 能力卡——**无 order_daemon 任务注册项=按设计**（事件驱动禁 cron）；Windows 计划任务：`ZephyrAlpha_DataScheduler` **正在运行**（schtasks 实证）=唤醒宿主活体，无独立 order_daemon 任务=按设计；worktree 启动面：DataScheduler 构造即 wire（imported 注册，零线程零轮询） | 三面齐：宿主活+注册按设计+装配点在码 |
| ⑥ 数据字段 | journal 八轻 kind 契约（PAYLOAD_REQUIRED_KEYS）；任务书附录 A schema v0 十三字段（build_task_order 全实现）；criteria_hash 机检；堵点本 bottleneck_ledger.jsonl | 契约全在码，零缺字段 |

## 2. 断链裁定（挖矿结论，W3-3 收窄的验证基线）

A7 治了"谁唤它"（触发沿）。端到端真实性核验发现剩余两断点：
1. **落库面**：spawn 缺省 dry-run→工单只进回执即蒸发→Owner 永远无单可确认（下游全空转）；
   `handle_winner` 硬编码 `order_seq=1`，同日多胜者 upsert 互踩同号=丢单。
2. **生产面**：`evolution_winner_due` 全仓零 emit 方→生产 journal 恒空→触发沿永远 `journal_empty`
   （A7 实弹探针只能在 tmp 注入侧验证，正是"接线只通一半"的表征）。

## 3. 端到端冒烟（W3-3 处方，sim/mock 级）——结果与补全

**冒烟设计**：胜者事件（tmp journal）→ `maybe_drain_order_daemon`（真 spawn 入口）→ 真 OrderDaemon
（单例锁/断点续读/毒丸内建）→ sink 落 orders.jsonl → 断言行级工单。全 tmp_path 注入=零生产路径
零券商；工单=任务书文本对象（非交易订单），红线天然达标。

| 冒烟项 | 结果 |
|---|---|
| 触发沿（A7 件） | ✅ journal 空→`journal_empty` 零成本；非空→起守护（A7 原测 4 件仍绿） |
| 落库面（本车道补） | ✅ 胜者事件→orders.jsonl 落行 `WO-*-001 state=pending domain_id=governance`（dry-run 下此步必空=断链复现） |
| 同日多胜者 | ✅ 第二单自动 `WO-*-002`（互踩且回归钉死） |
| 生产边（本车道补） | ✅ L4 `archive_and_notify` 归档沿同投：win/win_starred→`evolution_winner_due` 落发；draw→零转投；缺 domain_id→空串如实转运（分层契约=journal 闸管键在场，语义完整度归守护必填机检 held_incomplete+堵点本，A7 实弹探针同款分层） |
| 生产 journal 实探（只读） | `SchedulingJournal().status()`→pending=0（生产面健康零积压，无残留测试物） |

**补全面（自裁记日志：非重复接线，是冒烟暴露的剩余断边）**：
1. `pipeline_events._order_store_sink`：spawn 挂 `OrderFileStore.upsert` sink+当日序号分配
   （锁内仓计数确定推导=幂等；sink 失败上抛→journal 事务语义保留事件=可停可重放）。
2. `compare_events.maybe_emit_evolution_winner`+`archive_and_notify(winner_journal=)`：
   L4 归档沿→L5 journal 生产边（DESIGN §1①"库外=verdict='win' 直达"）。
3. `experiment_store`：快照补 `domain_id`（DB 列本在 SELECT* 已取，此前漏映射=生产边缺必填三元之一）；
   顺带治净本件既有红面防撞门（两处内联 UPDATE 提取 `_SQL_TRANSITION`/`_SQL_VERDICT_APPEND`
   模块常量=§5.160.2 集中化、zip strict、Invalid noqa 补码段、UP037）。

**幂等可停论证**（交易红线加码面）：消费=drain 成功才出队+offset 断点续读（重放零副作用）；
落库=upsert 按 order_id 幂等；停=KillSwitch 探针 fail-closed+单例锁让位+零定时器零常驻。**全链无券商接口无实盘路径**。

## 4. 测试证据

`pytest tests/ai_layer/comparator/ tests/ai_layer/scheduling/ tests/strategy_pipeline/test_pipeline_events.py
--basetemp=.runtime/tmp/lane-f82` → **329 passed, 1 skipped**（skip=既有 sleeve_provenance 通道）。
ruff check/format：本批 5 件全净。落袋史：q-0020 首投死于同袋 P2a 车道 fcntl 悬空 import
（其车道已自愈=POSIX 零锁直通）；q-0021 死于旧路径 R5（目录已迁，袋作废不 requeue，新袋重投）。

## 5. 遗留缺口（如实登记，非本车道面）

1. **PG sink**：生产真源目标 `ai_scheduling.ai_work_order`（C2 DDL 在册）未接，快照文件仓为现行落点；
   文件快照 vs PG 谁为长期真源**未裁**（confirm_gate 头注在册+wiring_C_confirm_hardening 判据）。
2. **L2 库内路**：`intake_e2_handoff`（payload 带 labor_killed/card_id）全仓零 emit——L2 intake 卡车道面。
3. **archive_and_notify 生产调用方**：L4 考场线（executor/venue→archive）未通，本边随其点亮；
   `league_judge` promote 属策略席位轮换（非模块进化工单），语义不合不做直达桥（自裁记日志）。
4. **api 投影**：schedulegate 页列队投影读 seeds（骨架提案面），orders.jsonl 工单投影与 confirm
   硬化（鉴权真源/归档语义）待 confirm 接线三件齐。
5. **骨架总册回写**：00_skeleton.md F82"断链"行应改"已接线（A7 触发沿+本车道生产/落库边）"——
   总册归总包 Owner 面，本车道不代改（本册即回写载体）。
