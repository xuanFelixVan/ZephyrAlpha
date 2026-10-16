---
ttl: task_bound
---
# SDSC-05 实时 WAL 落盘排空（tick 先段落盘→异步 drain）

> 挖矿工程：全链路图12 数据供给链 S2 入库段 2/3｜真源=config/data_supply_chain_map.yaml#DSC-05｜挖矿时点=2026-10-15
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：实时 WAL 落盘排空（tick 先段落盘→异步 drain），node_type=stage，build_status=built，verified_scope=production（行级 ✅）。
- 职责一句话：tick/tick_depth_5 两路先写 WAL 段（data/local_fallback/ 与 DSC-04 同袋）再异步 drain 入 CH；90% 容量（2 GiB）是硬阻断（add() 直接拒收）不是软减速；攒批写（buffered_writer 32 任务）与 WAL 同形不同物。
- 决策问句（图原文）：tick 流落盘的段什么时候被排空？容量告急时是减速还是拒收？

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | DSC-02→DSC-05 data_flow 边（tick 段落 WAL）；tick/tick_depth_5 两路 | config/data_supply_chain_map.yaml edges DSC-02→DSC-05；src/zephyr/data/wal_writer.py |
| 输出面 | WAL 段 drain→CH c1_market.tick_data/tick_depth_5；本批复跑 tick_data max=2026-10-15、3,960,210,772 行（lag 0）=WAL 排空主腿新鲜实证；段文件 drain 成功即删 | config/data_supply_chain_map.yaml#DSC-05 data_refs/store_refs；本批 CH 只读直查 |
| SSOT 真源 | WAL 行为真源=wal_writer.py 模块契约（90% 拒收/容量 2 GiB）；图 DSC-05 节点块；与 DSC-04 共用 local_fallback 目录+manifest+回灌器（WB12-26 并置裁定） | src/zephyr/data/wal_writer.py；config/data_supply_chain_map.yaml#DSC-FB |
| 代码模块 | module_id=MOD-L00-004，module_ref=src/zephyr/data/wal_writer.py；执行体 wal_writer.py+buffered_writer.py 实存（裁定 #ARCH-CH-003 攒批写手） | src/zephyr/data/wal_writer.py；src/zephyr/data/buffered_writer.py（本批 ls） |
| 门禁约束 | 静默失败即假绿；背压指标两义性在册（zephyr_wal_backlog_files 分不清背压积压还是链路故障积压，🌑-5）；检测≠修复法条 | config/data_supply_chain_map.yaml laws+DSC-05 fallback |
| 自动化触发 | wired_stream（事件驱动无档期）；drain 复用 DSC-04 回灌守护线程（scheduler.py:1128-1165）；task_runs 台账另有 32 笔带 buffer 任务（机生） | src/zephyr/data/scheduler.py:1128-1165；config/data_supply_chain_map.yaml#DSC-05 trigger_facts（as_of 2026-10-04 alive） |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | pass | DSC-02 盘中主腿今日在产（tick_data 当日行数在涨），WAL 入流成立 |
| 输出面 | pass | tick_data 39.6 亿行 max=今日=排空产出直证；top 层无未排空段积压 |
| SSOT 真源 | pass | 模块契约+图节点+FB 并置裁定一致；"不是两套积压"已在图显性化 |
| 代码模块 | pass | 两执行体实存 |
| 门禁约束 | warn | 🌑-5 背压指标两义性未修：单指标无法区分"背压积压"与"链路故障积压" |
| 自动化触发 | warn | drain 守护线程在岗；但 warning/critical 档历史上是否真触发过无 metrics 落盘可证（🌑-5 判定欠项）——触发面带不可证限定 |

## 4. 缺口与建议

1. 【warn 持续】背压指标两义性（🌑-5）：建议拆 zephyr_wal_backlog_files 为 backlog_by_reason（backpressure/link_fault 两标签），一次小改消掉两处判定欠项（DSC-05 触发面+DSC-04 门禁面共用）。
2. 【warn 持续】90% 硬拒收无预演证据：warning/critical 阈值历史触发不可证；建议在 drain 周期里顺带写一行水位采样（ts+bytes+pct）进日志，让"从未逼近过"也可证。
3. 【正向证据】共用袋设计（DSC-FB 汇聚）经本批复跑自洽：顶层面无 TSV 残留、quarantine 有序——两入口一出口的结构在现网成立。
