---
ttl: task_bound
---
# SDSC-02 盘中实时/竞价采集（Tick/L2/Greeks/分钟K/880板块/集合竞价）

> 挖矿工程：全链路图12 数据供给链 S1 采集段 2/3｜真源=config/data_supply_chain_map.yaml#DSC-02｜挖矿时点=2026-10-15（含当日只读复跑）
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：盘中实时/竞价采集（Tick/L2/Greeks/分钟K/880板块/集合竞价），node_type=stage，build_status=built，verified_scope=production（行级 ✅）。
- 职责一句话：盘中五槽（pre_market/intraday_realtime/intraday_minute/intraday_sector/auction_highfreq）+秒级竞价窗（6 段 cron+max_instances=1+coalesce 节流）产盘中行情流；产数走 WAL 通道（DSC-05），与盘后批共用写手但不同入口。
- 决策问句（图原文）：盘中这条流今天还在产数吗？哪些子腿已经静默空转？

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | DSC-SRC→本环节（盘中/竞价流）；miniqmt/tqcenter/tdx/tickflow 四源盘中族；QMT 无接口标的以 *_placeholder 任务占位（fallback 在册） | config/data_supply_chain_map.yaml edges DSC-SRC→DSC-02+machine.slots（auction_highfreq 2/intraday_minute 16/intraday_realtime 16/intraday_sector 5/pre_market 9）；src/zephyr/data/config/tasks.yaml |
| 输出面 | c1_market.tick_data/realtime_snapshot/kline_1min/l2_tick/suspend 等→DSC-04 批量写+DSC-05 WAL；消费=TDM 6 表 15 点+backtest ch_tick_replay/cost_model_calibration | config/data_supply_chain_map.yaml#DSC-02 data_refs+consumers；本批复跑 tick_data max=2026-10-15、39.6 亿行（lag 0）；kline_sector_intraday max=2026-10-15 15:00（09-11~09-22 断供案已复活） |
| SSOT 真源 | 槽位真源=schedule.yaml（auction_highfreq 秒级窗 6 段 cron）；语义层=图12 DSC-02；hollow 槽如实登记（post_auction 槽在 0 任务） | src/zephyr/data/config/schedule.yaml；config/data_supply_chain_map.yaml machine.scheduler_dispatch.slots_hollow=[nightly_news_score, post_auction] |
| 代码模块 | module_id=MOD-L00-001，module_ref=src/zephyr/data/tick_subscriber.py；执行体 tick_subscriber.py+implementations/ch_tick_kline.py（tick→分钟K CH 内自拼）实存 | src/zephyr/data/tick_subscriber.py；src/zephyr/data/implementations/ch_tick_kline.py（本批 ls 核实） |
| 门禁约束 | 静默失败即假绿（法条）——占位任务与真断供在档期面同形，须按 task_id 后缀区分；新鲜度主口径=max(date)+近窗计数 | config/data_supply_chain_map.yaml laws+DSC-02 fallback/notes；AGENTS.md §9.4（检测≠修复） |
| 自动化触发 | wired_cron：五槽在机（本批复读 task_runs 7 日窗 879 笔 alive）；post_auction=hollow_slots 成员（到点进常规 DAG、0 任务、静默返回成功=R-021 假通道形态，图如实登记） | config/data_supply_chain_map.yaml#DSC-02 machine.slots/hollow_slots+trigger_facts（as_of 2026-10-04，observed_runs=879） |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | warn | 四源任务面在册在跑；但 L2 行情权限缺失（💰-4 花钱可解）致 l2_tick 腿源侧无供、原降级腿 09-09 被清=静默空转（DSC-GAP-L2TICK 挂本环节） |
| 输出面 | warn | tick_data/分钟K 主腿今日新鲜（max=10-15，3.96B 行）；但 l2_tick=0 行（复跑仍 0）、suspend=36 行停在 09-23（产过一次即停）、realtime_snapshot 供数形态疑点（E8 期望未定）未销 |
| SSOT 真源 | pass | schedule.yaml 槽位与图 machine 层一致；hollow 槽如实显性化（禁散文掩盖） |
| 代码模块 | pass | 两执行体实存（本批 ls） |
| 门禁约束 | pass | 静默失败即假绿法条+占位任务判读纪律在册；0 行表判读按"表在任务在 0 行=断供"口径执行（本批复跑即按此判） |
| 自动化触发 | fail | post_auction 槽=hollow_slots 实锤：槽在、0 任务、无独立产出、静默成功=R-021 假通道未收口；五槽主腿计数 alive 但 post_auction 名下永无产物 |

## 4. 缺口与建议

1. 【fail 收口项】post_auction 空转槽：二选一收口——挂真任务或摘槽；保留空槽=每图复查都要重判一次"假通道吗"（建议随图13 D13-13 竞价聚合消费面一起裁）。
2. 【warn 持续，💰-4】l2_tick/suspend 双 0 行（DSC-GAP-L2TICK）：L2 权限=花钱可解、Owner 门位；suspend 本批复跑 36 行 max=09-23=产过一次后停摆，建议先查 09-23 后三任务为何全静默（源权限 vs 任务 disabled），再议采购。
3. 【warn 待裁】realtime_snapshot max(snapshot_time)=1970 哨兵+盘中段零供给（11 卷实测）：E8 期望未定前不武断标红（N4 纪律），建议列入消费端需求反查卷的下一批改判。
4. 【正向证据】kline_sector_intraday 已复活（09-22 停更→今日 max=10-15 15:00），CASEBOOK-001#outage 段建议补一条复活闭合记录。
