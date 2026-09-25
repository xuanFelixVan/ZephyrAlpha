---
ttl: task_bound
title: L07-EXE3 子块挖矿簿 · QMT 桥客户端（文件桥 + HTTP 快路径 + 桥执行腿）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L07
status: MINE 完成（六向封口）；本册使命=只挖"同类静默丢失/回报断链的未覆盖路径"，不触碰 LANE-BUILD 在修的两缺陷
---

# L07 · EXE-3 QMT 桥客户端

> **分工声明**：隔夜单静默丢弃 + submit→cancel<5s 竞态（TRD-A10）由车道 LANE-BUILD 在修（HEAD 已见 `_reconcile_phantom_claims`/`_note_client_claims` 在办实码，:926/:940）。本册**不提任何桥实现施工项**，只做"同族其他路径"的增量清单。

**① 职责一句话**：把仓内 `Order` 序列化成柜台哑执行器看得见的指令行（CSV/HTTP），再把柜台三类导出文件（Order/Deal/Position+Account）异步回读成 `Fill`/终态——是全链路唯一跨"自有代码 ↔ 闭源 exe"边界的翻译与回读件。

**② 现状实测**（`src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py`，1,098+ 行正文级实读；MATURITY=draft，MOD-L06-001-QMTFB）

| 面 | 实测值 | 出处 |
|---|---|---|
| API 面 | `CounterStateMirror`（get_orders/positions/account/deals/available_qty/pending_count/sync_all）+ `QmtFileBridgeBroker(BrokerInterface)` + 模块级 `_read_gbk_csv/_scan_instruction_states/_read_new_acks/_apply_acks/check_broker_health` | :134/:361/:1010-1098 |
| 回读通道 | 3 秒轮询 `sync_all`（daemon `_sync_loop` :901）；本地通道 `_sync_local_channel` :915 | — |
| 快路径 | `_http_post_order(line) -> bool` :873，失败 fail-open 降级文件桥（头注 :24-26，中位 32ms） | — |
| 幂等 | 指令 `#SENDING→#DONE` 文件状态机；成交 `deal_id` 去重 | :313 |
| 新鲜度闸 | `order_export_age_ms()` :160 用 `Order.csv` mtime，负值按 0；`counter_export_stale_ms` 超龄→**幽灵单判定暂停**（:960-968，不误杀活单） | — |
| 生产触发面 | **已接电（sim 腿）**：计划任务 `SimBridgeExecute` 09:35/13:05 + 手工 `scripts/bridge_monitor_check.ps1`（只读巡检）；载体已由 LANE-BUILD 于 09-25 恢复（SKEL EXE-3⑥ 销号注记），本班复核 `bridge_execute` 在位（:863 引注） | 计划任务实测见 §⑥ |
| 回读证据 | `.runtime/monitor/bridge_monitor_check.txt`（末次 2026-07-07 11:02）自证：`order_state age_s=1099134`（**12.7 天无更新**）、`quote age_s=6786723`（78 天）、`state rows=17112 with_trade=2246` | 实测读数 |
| 旁证 | `config/quarantine/qmt_trade_csv_quarantine_20260622/` 全套 5 CSV + 只读分析件 `trade_stats.json:4 "price_cage_reject": 0` | 实测 |

**③ 六向台账 —— 本册重心在"同族未覆盖路径"（E 列）**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：`submit_order` :590 前置=`board_lot` 最小申报单位硬拒（:605-607）+ `check_price_cage` 三参直调（→ **恒 UNKNOWN，见 EXE-2 C-GATE-01**）+ `_pretrade_risk_check` :652；柜台 quote（wrapper mtime>900s 拒单）。外部：待办。 |
| ②下游 | 内部：`_dispatch_fill` :998（remark→本地 order_id 反查）→ OM/FillHandler；`_observe_terminal_orders` :530 → `attach_execution_report_producer` :505（EXE-4）；`get_*` 系列供持仓/现金。外部：待办。 |
| ③算法/机制 | 内部：本件无算法（单笔直投），`avg_fill_price = price` 取**最后一笔成交价而非加权均价**（:340）——多笔部分成交时该字段即失真（不是"没算"，是"算错"），下游 EXE-4 的 commission/price 与 EXE-5 的滑点基准全部继承此失真。外部：待办。 |
| ④后端 | 内部：Windows 文件系统语义=共享资源：`_read_new_acks` 的 `except OSError: return [], offset`（:1061-1062）**无日志无计数**，而 QMT 客户端写文件时对 ack/order_state 持独占句柄是常态（`PermissionError` ⊂ `OSError`）→ 一次锁冲突=该轮 ack 全丢且**零痕迹**。外部：待办。 |
| ⑤前端 | 内部：人工面=`bridge_monitor_check.ps1`（只读巡检，含 2026-07-07 BUGFIX 两条：offset 失配→文件缩短时告警+重置 0；#SENDING 无 ack 假 DONE→改判 PENDING_RETRY）+ 仪表盘 `app_panel.py`（未覆，MINING 债）。外部：待办。 |
| ⑥数据字段 | 内部：柜台 CSV **位置式取列**（`row[9]=remark / row[11,12]=证券代码/市场 / row[14]=成交编号 / row[17]=价格 / row[18]=数量 / row[19,20]=日期时间 / row[21]=手续费 / row[23]=买卖`，:308-321），且 `if len(row) < 24: continue`（:308）；表头靠中文哨兵 `remark == "投资备注"` 识别。外部：待办。 |

**④ 缺口清单——"同类静默丢失/回报断链"的未覆盖路径增量**（与 A10 两缺陷不重叠；SKEL §4 与本册 §⑥ 的既有项不重复）

| 编号 | 未覆盖路径 | 证据（文件:行） | 级别 |
|---|---|---|---|
| **L07-S3-G1** | **ack 增量读取的 offset 无缩短保护，且只在巡检脚本侧修过**：`_read_new_acks` 对 ack 文件 `f.seek(offset)` 后不校验 `file_size < offset`；ack 文件被客户端重写/轮转/人工清理 → offset 永超 EOF → **此后所有回执永久静默丢弃**（订单永远停在 SUBMITTED，既非 FAIL 也非 FILLED）。同 bug 的修法早已存在于 `bridge_monitor_check.ps1:72`（"offset 失配（客户端重启重写）→ 文件缩短时告警+重置 0"），**但未回植进程内路径**=监控有防、正码无防的双标家族。 | :1053-1067 | **P0** |
| **L07-S3-G2** | **ack 应用只认 `FAIL` 且 cache 未命中即 `continue`**：`_apply_acks` 对 `order_cache.get(ack.order_id) is None` 的 ack 静默跳过（:1085-1086）；进程重启后缓存由 `_scan_instruction_states` 重建，期间到达/新读的 ack 全部丢；且 `DONE`/`ACCEPTED` 类 ack 不被消费（终态只靠 Deal.csv），任何"柜台只写 ack 不写 deal"的拒单分支无家可归。 | :1082-1096 | P1 |
| **L07-S3-G3** | **Deal.csv 列数/列位硬编码 + 短行零日志吞**：`len(row) < 24 → continue`（:308）无任何计数；柜台版本升级（v14→v16 已实际发生）改列即**整片成交回报无声消失**，且因为 `deal_id` 未进 `_processed_fill_ids`，修复后不会回补——永久缺数据。 | :305-321 | **P0** |
| **L07-S3-G4** | **成交去重集非持久**：`self._processed_fill_ids: set[str] = set()`（:149）纯内存、无 `AppendOnlyDedupSet`/state_store（本文件 grep 零命中）；重启后 Deal.csv 全量重放——`on_fill` 下游有 fill_id 幂等，**但 `cached.filled_quantity += qty` 发生在 broker 自身缓存、早于下游幂等**（:339），故重启+缓存重建路径下的累计量一致性无保护（重建逻辑是否恢复 filled_quantity 未读实，标 MINING 债）。 | :149/:339 | P1 |
| **L07-S3-G5** | **avg_fill_price 非加权**（多笔部分成交失真，见 §③④）→ 直接污染 execution_report 与 TCA/滑点归因。 | :340 | P1 |
| **L07-S3-G6** | **回读停摆的可观测性只有 mtime 一处**：`_reconcile_phantom_claims` 依赖 `Order.csv` mtime；若 QMT 持续 touch 文件但内容不再更新（导出器半死），mirror "看起来新鲜"，`get_orders()` 返回陈旧集合 → 幽灵单判定被 `remark in visible` 误销案，或真回报永久不来。缺"内容哈希/行数增量"第二新鲜度轴（monitor 脚本已用 `rows=17112 with_trade=2246` 这一思路，同样未回植正码）。 | :160-167/:953-958 | P1 |
| **L07-S3-G7** | **客户端活性依赖闭源 exe 的日志行**：`_note_client_claims(remarks, now_ms)` :926 从客户端日志取"声称已发"Remark 作为幽灵单判定的输入源；日志格式变/不写/轮转 → `_unconfirmed_claims` 为空 → :959 `if not self._unconfirmed_claims: return`，**整段兜底不触发**且无"兜底未武装"告警。这是对第三方黑盒产物的单点依赖。 | :926/:959-960 | P1（登记，修法归 LANE-BUILD/Owner） |
| **L07-S3-G8** | **生产实况 vs 代码态的时间尺度差未量化**：order_state.csv 12.7 天 / quote 78 天（monitor 实读）与"每日 09:35/13:05 触发"的口径不符——桥的**回读平面**长期不新鲜而下单平面自认正常，正是"发得出、收不回"的断链温床；SKEL 只记了载体断（已销号），未记回读平面 staleness。 | monitor 读数 | **P0（数据/事实类，非施工）** |

**⑤ 自审闸三态裁定**

| 项 | 裁定 | 理由 |
|---|---|---|
| G1/G2/G3/G4/G5/G6 | **移交不立项施工**：全部登记为 LANE-BILLD 在办的桥治理批的**增量清单**（本册不动桥实现，遵分工）。理由：与在修两缺陷同文件同函数族，分头施工必冲突；但**不得因"有人在修"而不登记**——G1/G3 与 A10 两缺陷机制完全不同（A10 是"指令发出后无收录"，G1/G3 是"回执/成交读回来那条路断"）。 | 终局全貌：跨黑盒边界的每条通道都要有独立断链探针，一条修好不代表族内其他条安全。 |
| G7 | **挂起排期**：解锁条件=与哑执行器版本冻结一次契约核对（客户端日志格式=外部契约），需 Owner 决策是否升级为"仓内不依赖客户端日志"的自证方案。 | 依赖外部不可控件的方法学裁定，不是接线活。 |
| G8 | **施工（事实侧，零代码）**：把"桥回读平面新鲜度双轴（mtime+行数增量）"写成 `.runtime/monitor` 常驻指标并进日报；SKEL 的保守声明"通=仅 sim 语境"据此可量化。 | 不可观测=最便宜的止血，且不侵入桥码。 |
| 载体（L07-C01） | 引用 SKEL 已结案，不重复。 | — |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | 备注 |
|---|---|---|---|
| R1 | API 面全量（def/class 清单 46 项） | signal | 见 §② |
| R2 | `_read_new_acks`/`_apply_acks`/`check_broker_health` 正文（:1053-1110） | signal | G1/G2 主证 |
| R3 | `_reconcile_phantom_claims` + `order_export_age_ms` 正文（:940-1000/:160-167） | signal | G6/G7；同时确认 A10① 已由 LANE-BUILD 在办，本册撤手 |
| R4 | `_sync_deals` 正文（:301-360） | signal | G3/G4/G5 |
| R5 | `_processed_fill_ids` 持久化反查（grep=纯内存 set，无 state_store） | signal | G4 定性 |
| R6 | 生产事实：`.runtime/monitor/bridge_monitor_check.txt` + `config/quarantine/*` | signal | G8，只读旁证 |
| R7 | 外部对表（文件桥 ack/offset 断链业界做法） | **未做** | 推迟；本册缺口全为代码级直读证据，不依赖外部论断 |

**本册封矿判据**：使命（同族未覆盖路径清单）已穷尽至桥件全部读回通道（ack/deal/order/position/account/client-log 五条），剩余长尾=`_scan_instruction_states` 与 `submit_order`/`cancel_order` 正文逐行（LANE-BUILD 领地，本班主动不掘以免产冲突结论）+ `qmt_file_bridge_integration` 全文 + 2026-09-08 迁移台账全文（SKEL §3 已列）→ **判 MINING，跨边界不封**。
