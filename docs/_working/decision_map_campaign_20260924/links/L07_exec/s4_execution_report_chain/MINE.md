---
ttl: task_bound
doc_type: log
title: L07-EXE4 子块挖矿簿 · 成交回报链（ExecutionReport 生产端）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L07
status: MINE 完成（六向封口）；含 P0 新证两条（零量行哨兵毒值 / 全表仅 1 行）
---

# L07 · EXE-4 成交回报链（ExecutionReport 生产端）

**① 职责一句话**：把一笔订单的**终态事实**（意图 vs 实际、佣金、时段）凝成一行 CTR-P1-007 聚合记录写进 `c1_market.execution_report`，是"执行质量"这个概念在系统里唯一的物理载体。

**② 现状实测**

| 项 | 实测值 | 出处 |
|---|---|---|
| 生产端件 | `src/zephyr/ex_core/execution_report_producer.py` 455 行，MOD-L06-001-ERP，**MATURITY=evolving**（SKEL 未记此态，其余执行件多标 production），STARTUP=imported | 头注 :6/:8 |
| 产出逻辑件 | `src/zephyr/ex_core/execution_report.py` 129 行（`build_execution_report` + `_signed_slippage_bps` :54-62），MATURITY=evolving，[CONSUMERS] 列 `D_REPORTING(TCA/归因上游, BM-REC-02-B)` | 头注 :5-8 |
| 契约 | `shared/contracts/execution_report.py`（64 行，真源，**[CONSUMERS] 空**）+ 两条 re-export 垫片 `shared/contracts/execution/`（32 行）/`trading/trading_contracts/execution/`（31 行，自注"改为 re-export shared 层真源，消除多真源"，[CONSUMERS]=pf_core） | 本册实读 |
| 表列（18 列，INSERT 15 列） | `order_id, symbol, direction, intended_quantity, actual_quantity, intended_price, vwap_price, slippage_bps, commission, execution_start, execution_end, broker_id, algo_type, idempotency_key, schema_version` + DEFAULT `ingest_ts` + MATERIALIZED `exchange/symbol_canonical` | `schemas/categories/intraday/market_execution_report.py:118-123` + `system.columns` 实查一致 |
| **表内实际数据（本班 CH 实查）** | **FINAL 后全表 = 1 行**：`order_id=f216058c… / 510300.SH / BUY / intended=100 / actual=0 / intended_price=4.07 / vwap_price=0 / **slippage_bps=-10000.0** / commission=0 / start=2026-09-18 10:26:15Z / end=10:27:49Z / broker_id=qmt_sim / algo_type=NONE / schema_version=1.0` | `ch_reader.query`（TCP 失败走通、FINAL 版被 `trade_date` 缺列 404 打回后改写重查，非"空串=无数据"误判） |
| 断链时点 | 09-23 实弹三合同（1573/1800/4820，SKEL EXE-3④ 称 sysid 回填验证过）**在表内零行** → 表内唯一行停在 09-18，说明 09-18 之后生产端再无成功落行（与 L07-C01 载体断同期），SKEL"断点 E4 闭合于 09-23 批"仅指**代码接线闭合**，非**数据闭合** | 本册 CH 实查 vs SKEL §2 EXE-3④/EXE-4⑤ |
| 消费面 | 全仓 `execution_report` 引用 20 文件（本册 grep），**读表者仍为零**：SKEL 结论复核成立，但需精确化——`api_server.py:1480` 有 `"execution_report": "执行回报"` 前端翻译词条（=数据集名可展示，非查询）；`position/position_reconciler.py:123 handle_execution_report(dict)` 是**契约级消费者且 [CONSUMERS] 自注"无生产消费方（BRK-016 在册断点）"** | 实测 |

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：双路取数（fill 回调累积成交面 + `observe()` 轮询订单面），原因实证=OM 只在 SUBMITTED/CANCELLED/EXPIRED 发事件，FILLED 走内部 `_transition_status`、REJECTED 由 broker 侧直接改写 `Order.status` 不经 OM（头注 :36-42）。**上游即 EXE-3 的断链出口**：G1（ack offset 失配）/G3（Deal.csv 短行吞）任一发生 → 本件"终态"永远等不到，**且本件无"应到未到"告警**（它只观察已到的）。外部：待办。 |
| ②下游 | 内部：零读者（表侧）；契约侧 `analytics_base.py:50`/`default_tca_engine.py:46` 都 import 契约但**自建内存对象**（消费 Order/Fill 契约，不读表）→ 同一数据形状两套来源（表 vs 内存），字段真源在 schemas DDL，内存真源在契约 dataclass，**两者无一致性校验**。`BM-REC-02-B` 消费方在 `execution_report.py` [CONSUMERS] 自注但全仓未见对应实码（MINING 债：battle_map 侧未读）。外部：待办。 |
| ③算法/机制 | 内部：滑点口径=40 号 §2.4 DECISION 决策价基准（[INVARIANTS] :8），`intended_price = run_record.target_price`（:100），符号约定"买入正滑点=不利"。**机制缺陷：零成交行的 `avg_fill_price=0` 未被排除**，`_signed_slippage_bps(BUY, 4.07, 0)` → `(0-4.07)/4.07*10000 = -10000.0` → "白拿"型最大有利滑点，实测唯一行正是此值。INVARIANT 只挡"有量无佣金"（"有成交量而佣金不可得时拒绝落行"），**未挡"零量行"**，与同段"禁污染 TCA 消费面"的自誓直接冲突；且 `emitted_unfilled` 分开计数（producer :264-267）证明作者**意识到**filled/unfilled 异质，却仍把 unfilled 的滑点当真值落库。外部：待办。 |
| ④后端 | 内部：写路径 `ch_writer.write_tsv_outcome`（:34）；`[ERROR_CONTRACT] 不向外抛——产出/校验/写入失败一律计数+error 日志`（:12）——旁路不打断主链=对的，但**计数只活在内存 stats()**，进程重启即归零，无一处把 `abandoned` 计数外化→"落了多少行/丢了多少行"在生产上不可查（本册只能靠数表行反推）。`ReplacingMergeTree` + order_id 幂等 + 已发集合跳过=双幂等，健康。外部：待办。 |
| ⑤前端 | 内部：无专窗；仅 api_server 数据集翻译词条。终局全貌要求"每笔意图↔每笔实际"可点开，现=0。外部：待办。 |
| ⑥数据字段 | 内部：**表结构本身缺字段**（与"字段在但数据没供"是反向缺口）：无 `decision_price/arrival_price/vwap_price 之外的基准族`，无 `side_liquidity/ADV 参与率`，无 `venue_reject_reason`，无 **T+1 可卖约束位**（EXE-9 的卖单可行性），无 `parent_order_id`（切片算法单落地即无处表达父子关系，与 `algo_type 恒 NONE` 同因）。`slippage_bps` 是**单一口径标量**，与 EXE-5 的多基准（到达价/VWAP/TWAP/前收/决策价）不兼容→ LK-12 逐笔 TCA 若按现表做，必然退化成"只有决策价基准"。外部：待办。 |

**④ 缺口清单**（本册新立；SKEL §4 的 L07-C04=接读者、T6b=撤单语义 不重复）

| 编号 | 内容 | 级别 |
|---|---|---|
| **L07-S4-G1** | **零成交行的 `slippage_bps` 哨兵毒值落库**：全表唯一实测行即 `-10000.0`（未成交 BUY）。任何 `avg(slippage_bps)` 型 TCA 报表一旦被接上（正是 L07-C04 要做的事），第一天就会被这一行拉到 -10000bp；且随"未成交率上升"毒行占比上升——**接读者之前必须先修语义，否则 L07-C04 落地即引爆**。修=零量行 slippage 落 NULL（或表改 Nullable），并在 producer 侧加"零量不填滑点"的 INVARIANT。 | **P0**（与 L07-C04 同批前置） |
| **L07-S4-G2** | **数据闭合与代码闭合被混记**：SKEL EXE-4⑤"断点 E4 闭合于 09-23 批"证伪为"接线闭合"——表内 09-18 后零行，09-23 三合同未落表。需把 E4 从"闭"改判"半闭（生产端在、数据未回补）"，并查 09-23 当日 `producer.stats()`/日志判定是"未装配"还是"写了没落"。 | **P0（事实纠偏）** |
| L07-S4-G3 | **无"应到未到"探针**：本件是回报链终点，其上游（EXE-3 五条通道）任一条断都表现为"这里没有新行"，而"没有新行"与"今天确实没单"不可分。终局全貌=必须有 `submitted_today vs terminal_today vs rows_today` 三计数日终对平（`run_eod_quality_check.ps1` 已是同类件，可挂同处）。 | P1 |
| L07-S4-G4 | **生产端计数器不外化**：`emitted_*/abandoned/validation_failed` 仅内存 `stats()`；进程重启归零。 | P1 |
| L07-S4-G5 | **表/契约双形状零一致性校验**：DDL 15 列 vs 契约 dataclass 字段无自动对平件（本册人肉对平一次，结论=一致）；缺 gate。 | P2（gate 型） |
| L07-S4-G6 | **表缺切片/归因必需列**：`parent_order_id`、多基准价族、拒单原因、T+1 可卖位——EXE-6/EXE-9 落真单前的 schema 欠账（属 CTR-P1-007 frozen 契约，Owner 窗口）。 | P1（Owner 门位） |
| L07-S4-G7 | **契约消费边断头**：`position_reconciler.handle_execution_report` 是现成消费者却自注 BRK-016 未接（=持仓对账链的另一条回报断链），与 L07-C04 是两条不同的边，SKEL 未记。 | P1 |

**⑤ 自审闸三态裁定**

| 项 | 裁定 | 理由 |
|---|---|---|
| G1 | **施工 P0，且必须排在 SKEL L07-C04（接读者）之前** | "禁污染 TCA 消费面"是本件自己的 INVARIANT，违宪修复属施工非新增；顺序颠倒=把已知毒值主动接进报表。 |
| G2 | **施工（事实核查型，零代码）**：查 09-23 producer 日志/stats 定性，改判 SKEL 记语 | 不可留"已闭合"假绿（同类假绿在 13 号文已有先例纪律）。 |
| G3/G4 | 施工 P1（观测件，不动语义） | 断链家族的通用止血；与 EXE-3 G8 同族可并一批。 |
| G5 | 挂起排期：解锁条件=新增 gate 需附"全仓扫描 or own-scope"理由（AGENTS §3.3），且属结构校验型分级未定 | 不是不重要，是需先定 gate 分级。 |
| G6 | **挂起排期（Owner 门位）**：解锁条件=CTR-P1-007 契约窗口开启 + EXE-6 算法层收口裁定（L07-C03）确定切片语义后才知需要什么列 | 改 frozen 契约的先置条件是消费语义定下来。 |
| G7 | 施工 P2：随 L07-C04 同批改装配（消费者已存在=纯接线） | 零新增件。 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | 备注 |
|---|---|---|---|
| R1 | producer 头注全文（455 行件，INVARIANTS/ERROR_CONTRACT/断点 E4 史） | signal | — |
| R2 | 全仓 `execution_report` 引用 20 文件逐一消歧（表 vs 契约 vs 前端词条） | signal | 精确化 SKEL"零读取方"，产出 G7 |
| R3 | 三份契约件比对（真源 + 两垫片） | **noise（已否）** | 查法：逐件读 docstring → 两垫片自注 re-export 真源，**非多真源**，不立内收项；仅记"两条垫片路径 + 真源 [CONSUMERS] 空" |
| R4 | schemas DDL INSERT_COLUMNS 实读 + `system.columns` CH 实查对平 | signal | 18 列（15 写 + 3 派生），一致 |
| R5 | CH 数据实查（首次带 `trade_date` 的查询 404 失败 → 改写重查，未采信"空串=无数据"） | signal | **G1/G2 主证**：全表 1 行 + slippage_bps=-10000 |
| R6 | `build_execution_report`/`_signed_slippage_bps` 正文复算毒值 | signal | 手算 (0-4.07)/4.07*10000=-10000 与库值一致，非猜测 |
| R7 | 外部对表（execution report schema/未成交行口径） | **未做** | 推迟到统一外部轮 |

**本册封矿判据**：六向封口；表侧数据事实已达"全表逐行核"级别（1 行）；剩余长尾=`BM-REC-02-B` 消费方实码（battle_map 域）、`execution_engine.py` 的 `ExecutionEngineRunRecord` 产出路径正文（MINING 债，SKEL §3 已列）→ **判 MINING（正文级两条留尾），数据级封口**。
