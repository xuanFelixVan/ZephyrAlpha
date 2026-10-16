---
ttl: task_bound
---
# SDSC-19 破损 part 自愈探测器（CHECKSUM 隔离环，进程内常驻）

> 挖矿工程：全链路图12 数据供给链 S5 对账修复段 7/8｜真源=config/data_supply_chain_map.yaml#DSC-19｜挖矿时点=2026-10-15
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：破损 part 自愈探测器（CHECKSUM 隔离环，进程内常驻），node_type=stage，build_status=partial，verified_scope=structure。
- 职责一句话：调度器进程内常驻守护线程，每 5min 扫 system.text_log 的 CHECKSUM_DOESNT_MATCH→STOP MERGES→DETACH PART→审计 jsonl；全仓唯一具备 DETACH 隔离能力的环节；既是入库段自愈腿也是对账修复段反馈环；不产数故永不 ✅。
- 决策问句（图原文）：部件级损坏被谁抓住？抓住之后是谁动手、动了有没有留痕？

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | 输入=system.text_log 的 CHECKSUM_DOESNT_MATCH 事件流（事件型稀疏输入）；检测口径只覆盖 CHECKSUM（0 字节 parts 族不可见=在册盲区） | src/zephyr/data/ch_parts_monitor.py（check_and_alert）；src/zephyr/data/scheduler.py:54（import 本批实读） |
| 输出面 | data/local_fallback/corrupted_parts_audit.jsonl 隔离审计件（append；本批复核仍不存在=零触发无审计行）+告警（alerter）；两条反馈边回 DSC-06（保读/判口径可用）与 DSC-16（DETACH=修复兜底） | config/data_supply_chain_map.yaml edges DSC-19→06/DSC-19→16；data/local_fallback/corrupted_parts_audit.jsonl（本批 ls 不存在） |
| SSOT 真源 | 探测器行为真源=ch_parts_monitor.py+scheduler 守护线程（300s 周期：定义 ：1067/启动实调 :2373 在案）；语义层=图12 DSC-19 | src/zephyr/data/ch_parts_monitor.py；src/zephyr/data/scheduler.py（图 trigger_facts 行号锚）；config/data_supply_chain_map.yaml#DSC-19 |
| 代码模块 | module_id=MOD-L00-004，module_ref=src/zephyr/data/scheduler.py（宿主）；执行体 ch_parts_monitor.py 实存（骨架指针与本批 ls 双证；总纲骨架 2.5 表该行指针即 ch_parts_monitor） | src/zephyr/data/ch_parts_monitor.py；src/zephyr/data/scheduler.py:54/:812（import+调用点本批 grep 实读） |
| 门禁约束 | 检测口径盲区在册（CHECKSUM 之外的 0 字节 parts 族不可见，09-25 macro 事故即漏网实例）；零触发≠零风险；invalidation 条款在册（扩口径落地并首次留痕→判词重估） | config/data_supply_chain_map.yaml#DSC-19 fallback/gaps+invalidation 字段 |
| 自动化触发 | wired_stream：进程内 300s 常驻（零档期）；CHECKSUM 事件零触发自 2026-07-16=探测腿零命中非机制死亡；审计腿 jsonl 应建未建（E-7 呈批在案） | config/data_supply_chain_map.yaml#DSC-19 trigger_facts（as_of 2026-10-04，alive）；本批 scheduler.py:812 调用点 grep |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | pass | 事件流通道在码（ch_parts_monitor+text_log 扫描），宿主调度器进程在跑（今日 task_runs 233,587 行旁证） |
| 输出面 | warn | 反馈双边在册；审计 jsonl 应建未建（零触发=无行可写，但"应建"的落地件仍缺——E-7 呈批未批） |
| SSOT 真源 | pass | 图锚/行号/本批复读三方一致（:54 import、:812 调用） |
| 代码模块 | pass | 双件实存 |
| 门禁约束 | warn | 0 字节 parts 盲区未扩（处方 IN1-34c：ch_parts_monitor 扩 0 字节 parts 探针，归数据班在案）——09-25 事故类型的同类事件今天仍不可见 |
| 自动化触发 | pass | 300s 常驻在岗（宿主活+调用点实读）；零触发自 07-16 属事件稀疏非机制死亡（期望=事件级，计数缺席禁判死纪律适用） |

## 4. 缺口与建议

1. 【warn 处方在案待落地】扩口径（0 字节部件族+装载期错误码）：IN1-34c 处方在案归数据班；落地后按 invalidation 条款重估本格判词——这是 09-25 macro 事故（打死全枚举面）的唯一治本探测件。
2. 【warn 审计腿】corrupted_parts_audit.jsonl 应建未建：建议首次 DETACH（或测试性干跑）时即建文件写首行，把"全仓唯一 DETACH 能力"的留痕面从计划变实物。
3. 【正向证据】退役资格季度审的判据（零触发但有消费面=不退役，消费=40 表读路径可用性前提）在册且本批复核维持——内收判据与保命职能的正确平衡样例。
