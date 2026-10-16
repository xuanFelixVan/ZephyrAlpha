---
ttl: task_bound
---
# SDSC-17 一致预期管线双向互验（自建聚合 vs 同花顺快照）

> 挖矿工程：全链路图12 数据供给链 S5 对账修复段 5/8｜真源=config/data_supply_chain_map.yaml#DSC-17｜挖矿时点=2026-10-15（含当日只读复跑）
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：一致预期管线双向互验（自建聚合 vs 同花顺快照），node_type=stage，build_status=built，verified_scope=production（行级 ✅；骨架 ⬜ 已被实测改判）。
- 职责一句话：检查族=秩相关/新鲜度/结构断言/PIT 零修正率四族；23:30 交易日档期由特殊槽分派；本图唯一能用产出表新鲜度当执行见证的检核器（表在位、非空、末写与 cron 精确吻合）。
- 决策问句（图原文）：两个独立真源互相打不打脸？用哪一列判它新鲜？

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | DSC-13→DSC-17 control 边（只检测族协同）；两腿输入=自建 consensus_daily（DSC-08 产物）vs 同花顺快照（外部源） | config/data_supply_chain_map.yaml edges DSC-13→17；src/zephyr/data/consensus_crosscheck.py |
| 输出面 | c1_market.cross_validation_log（互验台账，key=check_date+metric+symbol）+data/failures 案卷（consensus_crosscheck 族）；DSC-08 交叉旁证；本批复跑：33,904 行 max(check_date)=2026-10-15=今日夜档已产（远超在案读数 1,601/1,588 行量级——积累四倍于 09-25 时点） | 本批 CH 直查 cross_validation_log；config/data_supply_chain_map.yaml#DSC-17 store_refs |
| SSOT 真源 | 槽位真源=schedule.yaml consensus_crosscheck 槽（特殊分派 task_count=0）；新鲜度口径纪律=钉在 check_date（check_time 自 09-21 恒 epoch=P-7 在册陷阱） | src/zephyr/data/config/schedule.yaml；config/data_supply_chain_map.yaml#DSC-17 freshness_evidence probe_err |
| 代码模块 | module_id=MOD-L00-004，module_ref=src/zephyr/data/consensus_crosscheck.py 实存 | src/zephyr/data/consensus_crosscheck.py（本批 ls） |
| 门禁约束 | 检测≠修复（detect_only）；服务总闸 data/runtime/consensus_crosscheck.disabled（关闸即整环停，无独立健康度指标 residual；本批复核 flag 不存在=在岗） | config/data_supply_chain_map.yaml#DSC-17 fallback；data/runtime/consensus_crosscheck.disabled（本批 ls 不存在） |
| 自动化触发 | wired_special_branch：23:30 交易日档特殊分派（dispatched_slots 在册）；trigger_facts alive（23:30 cron 夜发+末写与 cron 精确吻合） | config/data_supply_chain_map.yaml#DSC-17 machine.slots/trigger_facts（as_of 2026-10-04） |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | pass | 自建腿今日鲜（consensus max=10-15，SDSC-08 交叉证）；同花顺腿按档期供给 |
| 输出面 | pass | 互验台账今日仍在产（max=10-15，33,904 行）——本图唯一"产出表新鲜度=执行见证"的检核器名实相符 |
| SSOT 真源 | pass | 槽位+口径纪律（check_date 钉死）+图节点一致 |
| 代码模块 | pass | 执行体实存，总闸未关 |
| 门禁约束 | warn | coverage 收缩疑点在册（按日行量 ~27 项→4 项，有意收窄 vs 配置漂移不可判，与 DSC-08 交叉为本图最有价值待查线索）；check_time epoch 陷阱靠纪律绕行未修 |
| 自动化触发 | pass | 23:30 特殊分派在机，今日 10-15 夜档产物即证（本批复跑时点 21:33 读到的是 10-15 日档=max=10-15 系当日凌晨档或昨晚——按 check_date 语义成立） |

## 4. 缺口与建议

1. 【warn 待查】互验覆盖收缩（27→4 项）：建议一次性 diff consensus_crosscheck.py 的检查项配置（或其读数的 symbol 集合）09-22 前后版本，判"有意收窄"还是"配置漂移"——与 research_report_detail 慢性超时（SDSC-08 建议一）同批派工。
2. 【warn 小修】check_time 恒 epoch（09-21 起）：该列已废但仍在表里，建议要么修写入要么 DDL 摘列，消灭"用错列判新鲜"的永久陷阱（P-7）。
3. 【正向证据】本环节是图级 terminal_provable 四实锚之一（cross_validation_log 作留痕型终点），今日继续成立。
