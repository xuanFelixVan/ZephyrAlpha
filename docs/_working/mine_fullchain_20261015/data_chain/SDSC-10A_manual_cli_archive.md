---
ttl: task_bound
---
# SDSC-10A 手动 CLI 归档（archiver 五子命令 export→verify→drop）

> 挖矿工程：全链路图12 数据供给链 S4 冷备段 1/4｜真源=config/data_supply_chain_map.yaml#DSC-10A｜挖矿时点=2026-10-15（含当日只读复跑）
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：手动 CLI 归档（archiver 五子命令 export→verify→drop），node_type=stage，build_status=built，verified_scope=structure。D12-10 批次4 拆行后的 a 腿：生产者=人工 CLI，验证口径=dry-run+人工判断，无档期。与 b 腿共享同一执行体（同码），拆行理由=生产者与验证口径同时变（三问已过）。
- 决策问句（图原文）：人工批归档今天该不该跑、跑完有没有对到位次？
- 语境：全项目唯一含不可逆删除（drop）的日常面，受不可逆动作三步验证+Owner 门位约束。

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | DSC-HB→DSC-10A data_flow 边（人工批量归档入口）；准入=超保留线分区（契约分层线）+当日备份成功回执 | config/data_supply_chain_map.yaml edges DSC-HB→10A；docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml（retention_lines_months/§rolling_archive） |
| 输出面 | 冷库归档件 F:/zephyr_cold/50_archive/by_project/zephyralpha/<table>/<partition>.parquet+archive_manifest.jsonl（append-only 永久）；本批复读 manifest 末条 archived_at=2026-10-15T04:30Z（kline_etf_30min 201110/201111 分区，当日仍在产——注意该读数主要来自 b 腿事件触发，a 腿人工批未区分留痕） | F:/zephyr_cold/50_archive/by_project/zephyralpha/archive_manifest.jsonl（本批 tail 实读）；config/data_supply_chain_map.yaml#DSC-10A store_refs |
| SSOT 真源 | 归档判据真源=data_retention_contract.yaml（契约驱动）；压缩比顺带产出=manifest 字段 compress_ratio；语义层=图12 DSC-10A | docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml；config/data_supply_chain_map.yaml#DSC-12（压缩比度量同源注记） |
| 代码模块 | module_id=MOD-INF-043，module_ref=scripts/ch/archiver.py（三阶段原子操作 export→verify→drop）实存 | scripts/ch/archiver.py（本批 ls） |
| 门禁约束 | verify False→unlink 不可信 Parquet 且不 drop（安全侧失败）；顺序控制非事务控制（drop 成功而 manifest 写失败=盘已删清单无记）；行数容差四条放行口（>1M 差 1 行/>10M 跳抽样/抽样 0 行放行）；不可逆升 Owner 门位（AGENTS §5 物理不可逆删除） | config/data_supply_chain_map.yaml#DSC-10A fallback；AGENTS.md §5 Owner 保留面 |
| 自动化触发 | wired_manual（无节拍=by design）；trigger_facts 期望≤1 且计数缺席=insufficient_window 禁判死（SOP v1.1.0 补丁1） | config/data_supply_chain_map.yaml#DSC-10A wiring_status/trigger_facts |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | pass | 契约准入两件套（分层线+备份回执）在册且备份腿今日健康（SDSC-11 交叉证） |
| 输出面 | warn | manifest append-only 在产（今日末条）；但 a 腿人工批与 b 腿事件批共用 manifest 无 producer 字段=人工归档几次了不可分 |
| SSOT 真源 | pass | 契约真源+图节点一致 |
| 代码模块 | pass | archiver.py 实存 |
| 门禁约束 | warn | 顺序控制非事务+四条抽样放行口 residual 在册：超大分区无逐位保证、盘删清单无记的窗口存在 |
| 自动化触发 | warn | manual 无节拍是设计态；但零周期抽检+端到端 restore 覆盖缺口（DSC-GAP-ARCHIVE-AUDIT）仍开放——restore 演练任务 10-13 首跑（schtasks LastRun=10-13 23:33 Result=1）但 logs/dr_drill_*.json 最新仍停 09-15=跑了没留成产物 |

## 4. 缺口与建议

1. 【warn 建议】manifest 行加 producer 字段（manual_cli vs rolling_event）：一行 schema 变更让 a/b 两腿各算各的账，拆行的意义才算落地。
2. 【warn 持续→与 GAP-ARCHIVE-AUDIT 合并收口】冷档案零周期抽检：restore_drill 任务 10-13 已首跑但 Result=1 且无新 JSON 案卷——建议先修演练脚本产物落盘，再谈抽检常态化（节点退役条件=抽检常态化+端到端 restore 通过）。
3. 【warn 观察】verify 抽样放行口：对 >10M 行分区建议至少保留逐分区行数+checksum 双核（现跳抽样），或在契约明文接受该风险（Owner 门位签认）。
