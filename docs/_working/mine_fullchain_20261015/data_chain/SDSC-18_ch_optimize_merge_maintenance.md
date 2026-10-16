---
ttl: task_bound
---
# SDSC-18 CH 存储维护 OPTIMIZE / 合并（周度 OS 任务）

> 挖矿工程：全链路图12 数据供给链 S5 对账修复段 6/8｜真源=config/data_supply_chain_map.yaml#DSC-18｜挖矿时点=2026-10-15（含当日只读复核）
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：CH 存储维护 OPTIMIZE/合并（周度 OS 任务），node_type=stage，build_status=partial，verified_scope=structure，wiring_status=running_unregistered（开工了但没登记）。
- 职责一句话：存在理由=ReplacingMergeTree 去重是异步的，本工具是三防线（读侧 FINAL/归档 FINAL 导出/物理去重）的最后一道；表清单自发现无硬编码；消费 data_retention_contract。判词=已运行 OS 周任务、登记侧滞后、计数不可信。
- 决策问句（图原文）：合并真的发生了吗？失败 0 算不算效果证据？

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | DSC-16→DSC-18 control 边（修复后 OPTIMIZE 逐位验证）；输入=CH 表清单自发现+契约参数 | config/data_supply_chain_map.yaml edges DSC-16→18；scripts/ch/optimize_merge.py |
| 输出面 | logs/ch_optimize_merge_weekly.log（UTF-16LE 追加式日志）；合并效果回判重口径（DSC-18→06 feedback）；物理去重=ReplacingMergeTree 幂等前提的维护腿 | config/data_supply_chain_map.yaml#DSC-18 store_refs/feedback_loops；scripts/ch/optimize_merge.py:13（[ERROR_CONTRACT] 注记本批实读） |
| SSOT 真源 | 触发真源=OS 计划任务 ZephyrAlpha-CH-OptimizeMerge-Weekly（schtasks，slot_source=schtasks）；契约=data_retention_contract.yaml（消费方 grep 实证）；资源登记=config/resource_profile_registry.yaml（登记侧滞后：planned/manual/samples=0） | Get-ScheduledTaskInfo ZephyrAlpha-CH-OptimizeMerge-Weekly（本批实跑：LastRun=2026-10-12 18:26:50/Result=2147946720/Next=10-18）；config/resource_profile_registry.yaml |
| 代码模块 | module_id=MOD-L04-001，module_ref=scripts/ch/optimize_merge.py 实存 | scripts/ch/optimize_merge.py（本批 ls+grep） |
| 门禁约束 | empty_string_as_success residual（ch_reader.query 失败返回空串不抛→记 optimize 完成 0.0s=写/维护侧假成功，比读侧假绿更危险）；outside_resource_gate（OS 任务不进 APScheduler exclusive_group=资源闸盲区）；效果证据唯一可信=合并前后逐位比对或 system.parts 冗余率复测 | config/data_supply_chain_map.yaml#DSC-18 fallback/gaps（:138 false_success 判据在册） |
| 自动化触发 | wired：schtasks 周发（周日 03:30 档族）；09-20 实测 LastRun Result=0 在案；本批复核 10-12 LastRun=18:26:50 但 Result=2147946720（0x800710E0=操作员/管理员拒绝请求=该次未跑成），Next=10-18 | 本批 Get-ScheduledTaskInfo 实跑；config/data_supply_chain_map.yaml#DSC-18 gaps（unregistered_running+登记册滞后） |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | pass | 表清单自发现+契约消费在码在册（grep 实证 data_retention_contract 消费方） |
| 输出面 | warn | 维护日志追加式在盘；但"失败 0 不可信"（效果证据缺逐位比对/冗余率复测）在册未补——效果面无读数 |
| SSOT 真源 | warn | schtasks 真源在机但 resource_profile_registry 登记 planned/manual/samples=0 滞后未刷新（登记侧滞后双证：09-20 在案+本批 10-12 现值） |
| 代码模块 | pass | optimize_merge.py 实存；[ERROR_CONTRACT] exit 1 契约已在件头（13 行注记） |
| 门禁约束 | fail | :150 "optimize 完成 (%.1fs)" 完成日志与 :138 false_success 判据（空串→0.0s 假成功）共存：查询失败被记成功的写侧假绿路径未见修复证据——三防线最后一道的完成信号不可信，判 fail |
| 自动化触发 | warn | 周任务在机但最近一次（10-12）Result=2147946720 未跑成=当前无"最近一次成功"新鲜读数；资源闸对 OS 任务盲区 residual 在册 |

## 4. 缺口与建议

1. 【fail 收口项】假成功路径：建议 optimize_merge 的 OPTIMIZE 执行改走严格通道（query_rows 失败必抛，同 DSC-06② 改法），并把"失败 0"升级为"前后 parts 冗余率对比读数"——否则失败 0 恒不可信（在册原话）。
2. 【warn 触发面】10-12 周任务未跑成（0x800710E0=条件不满足拒绝）：建议查该次任务条件（idle-only/ac 状态）并在 backup/report 面同构留一份 schtasks 结果案卷，让周维护的"该跑没跑"进 DSC-20 视野（OS 任务现游离在任务对账面外）。
3. 【warn 登记侧】resource_profile_registry 把 dynamic_local_replay/ops_ch_optimize_merge_weekly 等 planned/manual 件刷新为实际 cadence——登记册滞后是本环节+DSC-04 共同判定欠项的根。
