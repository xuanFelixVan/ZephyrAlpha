---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-02
segment: fig13-A 盘前
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-02 数据断供哨兵（含托管质量变异巡检）

## 1. 定义

每日 06:50（全周）特殊槽 `data_supply_sentinel` 驱动断供哨兵三判据腿（业务新鲜度/行数地板/关键列填充率）+ 盲点出声 + 托管 quality_sentinel 变异巡检（7 天节奏闸）。只检测不修复（INVARIANTS 自陈），修复腿让渡 D13-01（档期）与 D13-35（行数）。决策问题：06:50 这一巡检出几条红？红有没有落成可操作产物？谁的手去修？

地图在册态：wiring=wired、build=partial、downstream_action=alert_only、alert_folding=true。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | 哨兵配置条目（覆盖表集合以机生 scanned 为准）+ 托管变异巡检表册 + CH 表读数 | `src/zephyr/data/config/data_supply_sentinel.yaml`；`config/quality_sentinel_tables.yaml`；`src/zephyr/data/supply_sentinel.py` |
| 输出面 | failures 案卷文件 + quality_sentinel 产物 + 哨兵日志行；同 task_id 300 秒冷却去重致多红折叠一痕（11 红只剩 1 痕） | `data/failures/`；`data/quality_sentinel/`；地图 evidence：今晨 06:51 checked/breached/blind_spots 三计数在案、连续 6 日 ERROR 落盘 |
| SSOT 真源 | 图13 节点契约（行 224-305）+ 数据接入 SOP 哨兵段 | `config/trading_day_cycle_map.yaml#D13-02`；`docs/01_policies_and_standards/sop/data_ops_sop/data_source_onboarding_sop.md:138` |
| 代码模块 | supply_sentinel 执行体 + 调度器特殊槽分支 + quality_sentinel 托管件 | `src/zephyr/data/supply_sentinel.py:11`；`src/zephyr/data/scheduler.py:343-356`（实核分支在位，地图锚 238 漂移）；`src/zephyr/data/quality_sentinel.py` |
| 门禁约束 | 服务总闸语义（`data/runtime/quality_sentinel.disabled` 存在=停用，机生扫=不存在在跑）；RULE-DATA-OPS（只检测不修复=无破坏性操作面）；总闸 data 断供不阻断（alert_only） | `src/zephyr/data/scheduler.py` 服务总闸 flag 惯例；`config/trading_day_cycle_map.yaml#D13-02` INVARIANTS 注 |
| 自动化触发 | mechanism=A_apscheduler，每日 06:50 全周（周末断供周一才报=重演两月盲区的已知取舍）；30 日任务级 count=0（冷却折叠+无独立任务计数面）；special_branch_exists=true | `config/trading_day_cycle_map.yaml#D13-02` trigger_facts/machine_facts 块 |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 双配置册实存，覆盖面以机生层为准 |
| 输出面 | warn | 检出条目有落盘案卷，但 alert_folding 使多红折叠成一痕，红计数失真 |
| SSOT 真源 | pass | 节点契约完整且机生对齐（service_flags 实扫） |
| 代码模块 | pass | 三件实存实核；分支在位 |
| 门禁约束 | warn | 修复腿让渡对象 D13-01 当前断裂（补跑圈 0 完成），alert→repair 链路半瘫 |
| 自动化触发 | pass | 每日 1 拍 firing 在案，日志面连续 6 日留痕 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：无；本格是三路兜底边（feedback_loops 断供→回补 D13-02→D13-01）的起点。
- gap_refs 在册：benchmark:C1（alert 腿与 rerun 腿分工真源至今是散文注释，三路兜底边已在本图落地）。
- 建议：①冷却去重改按 (task_id, breach_kind) 复合键，保红条数可数；②研报表（D13-18 断供腿）补进哨兵配置名单（簿 09 配置面事实：当前不含）；③周末盲区两月重演问题给 Owner 级取舍留痕。
