---
ttl: task_bound
---
# SDSC-10B 滚动归档事件触发器（backup-success hook，五重安全阀）

> 挖矿工程：全链路图12 数据供给链 S4 冷备段 2/4｜真源=config/data_supply_chain_map.yaml#DSC-10B｜挖矿时点=2026-10-15（含当日只读复跑）
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：滚动归档事件触发器（backup-success hook，五重安全阀），node_type=stage，build_status=built，verified_scope=production（行级 ✅）。D12-10 拆行后的 b 腿：backup.ps1 STAGE 4b 成功事件钩子链调 rolling_archive_reconciler --mode full_auto（件头明文 Event-triggered only - NO new scheduled task）；骨架原判词"触发靠人工"已被实测推翻。
- 决策问句（图原文）：备份成功之后自动归档这一环今天真的动了吗？动了几格？为什么没动？
- 图级地位：boundary.terminal_provable 四实锚之一（归档清单=可证留痕型终点）。

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | 两条入边：DSC-HB（超线分区准入）+DSC-11→DSC-10B trigger 边（备份成功事件→五重安全阀）；契约限量 batch_max_partitions=3/circuit_breaker_failures=3 | config/data_supply_chain_map.yaml edges DSC-HB→10B+DSC-11→10B；scripts/backup/backup.ps1 STAGE 4b（1352-1360 行区段本批实读） |
| 输出面 | 冷库归档件+archive_manifest.jsonl（append-only 永久）；本批复读末条 archived_at=2026-10-15T04:30Z=今日在产（kline_etf_30min 分区连续落）；rolling_archive_state.json 现值 consecutive_failures=1/kill_switch=false/circuit_open=false | F:/zephyr_cold/50_archive/by_project/zephyralpha/archive_manifest.jsonl+data/databases/rolling_archive_state.json（本批实读） |
| SSOT 真源 | 契约真源=data_retention_contract.yaml §rolling_archive（决策输入节点=DSC-12）；语义层=图12 DSC-10B | docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml；config/data_supply_chain_map.yaml#DSC-12 control 边 |
| 代码模块 | module_id=MOD-INF-043，module_ref=scripts/ch/archiver.py；执行体 rolling_archive_reconciler.py+backup.ps1 实存 | scripts/ch/rolling_archive_reconciler.py；scripts/backup/backup.ps1（本批 ls+grep） |
| 门禁约束 | 五重安全阀（契约 enabled/批限量 3/熔断失败数 3/kill switch/契约参数缺失拒启）；冷库禁反向更新 CH（防双真源）；skip 原因零留痕（🌑-6）在册 | config/data_supply_chain_map.yaml#DSC-10B fallback；AGENTS.md laws 引用块（冷库禁反向更新） |
| 自动化触发 | wired_event：backup.ps1 STAGE 4b 成功事件钩子（backup_log 日发 06:47 北京+post-commit reconciler 多跑）；backup_log max=2026-09-24T22:47Z 判 fresh 在案，今日 working_vault 10-15 在滚 | config/data_supply_chain_map.yaml#DSC-10B freshness_evidence/trigger_facts（alive）；G:/backup/working_vault（本批 ls 20261013/14/15） |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | pass | 备份成功事件今日在发（SDSC-11 pass 交叉证），钩子链在岗 |
| 输出面 | pass | manifest 今日 04:30Z 仍在 append（图在案读数 max=09-24 时判 lagging，现已回正为日发节奏）——可证留痕终点实锚成立 |
| SSOT 真源 | pass | 契约真源+限量参数+状态机文件三层一致；DSC-12 决策→执行关系在图显性化 |
| 代码模块 | pass | 两执行体实存（backup.ps1 4b 钩子段本批 grep 实读） |
| 门禁约束 | warn | 🌑-6 skip 原因零留痕未修（4b stdout 仅 Write-Host 不落档，本批 grep 复核 1360 行仍是 Select-Object -Last 5 | Write-Host）；state mtime 与 manifest 自洽性问题（consecutive_failures=1 谁在动 drop）未判 |
| 自动化触发 | pass | 事件钩子实跑：manifest 今日末条+working_vault 连日+backup_log 日发三证合一 |

## 4. 缺口与建议

1. 【warn 施工项在册】给 4b 加独立 jsonl 留痕（图 gaps 原处方）：每批 skip/落格一行（reason+partitions+result），消掉🌑-6——"今天没备"与"备了没成功"才能一分就知。
2. 【warn 观察】rolling_archive_state.json 覆盖写无历史：consecutive_failures=1 的上下文（哪天失败、哪个分区）不可追溯；建议状态机改 append 日志+派生现值，或至少把 last_failure_at/last_failure_table 两字段落进去。
3. 【正向证据】本环节作为图级可证终点实锚（terminal_provable 四锚之一）今日继续成立：归档清单逐条含 parquet_path+size+archived_at+compress_ratio，翻账面完整。
