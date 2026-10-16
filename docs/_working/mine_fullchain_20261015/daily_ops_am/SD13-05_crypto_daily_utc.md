---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-05
segment: fig13-A 盘前
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-05 币圈日线（UTC 日界→北京晨间时点）

## 1. 定义

每日 08:41（全周）常规 DAG 槽 `daily_crypto`（6 个有效任务）拉币圈日线族：K 线增量/影子闸/资金费率史/强平捕获/OI 快照等，UTC 日界数据在北京晨间时点落地。决策问题：08:41 的币圈日线跑了吗？水位是自动推进还是全靠手动？

地图在册态：wiring=unwired_slot_hollow（我段 4 个空心槽之一）、build=partial、red_reason=broken_supply、paused_zh=Owner 令 2026-10-04 币圈暂停开发保留现状。槽注释自证：原 light 执行器不存在致上线后从未自动跑成（2026-09-16 治标改挂 default 池）。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | crypto 外部源族（HL/交易所 K 线、资金费率、强平、OI） | `src/zephyr/data.connectors`（crypto 源连接器族）；`src/zephyr/data/config/schedule.yaml:75-77`（槽声明+executor 治理注） |
| 输出面 | crypto K 线/衍生表水位；observed=水位全靠手动（上线后从未自动跑成的事故留痕+治标改池） | `src/zephyr/data/config/schedule.yaml:77`（槽注释自证）；地图 evidence 引骨架 §2 D13-05 行 |
| SSOT 真源 | 图13 节点契约（行 465-546）+ paused_zh Owner 暂停令 | `config/trading_day_cycle_map.yaml#D13-05`；`docs/_working/map_build/fig13_daycycle/02_盘前元数据与竞价.md` |
| 代码模块 | 调度器 DAG 槽机制（常规槽非特殊分支，special_branch_exists=false） | `src/zephyr/data/scheduler.py`（executor 字典 default/heavy/realtime/intraday_minute/intraday_sector；light 不存在事故注在 schedule.yaml:77） |
| 门禁约束 | Owner 暂停令（2026-10-04）：本格保留格位与标签（t03），不列任何开发项——Owner 门位经正式通道生效（宪法 §5/§9.11）；槽不在补跑宇宙（in_catchup_universe=false）错过无人补 | `config/trading_day_cycle_map.yaml#D13-05` paused_zh/gap_refs；`AGENTS.md` §5 |
| 自动化触发 | mechanism=A_apscheduler，每日 08:41 全周；trigger_facts 30d count=110（6 任务求和）——firing 在但产物水位手动；calendar_guarded=false | `config/trading_day_cycle_map.yaml#D13-05` trigger_facts/machine_facts |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | warn | 源连接器族在册，但全链押停（暂停令），输入活性冻结 |
| 输出面 | fail | 水位全靠手动+全体任务在补跑宇宙外（错过无人补），自动产出面零在位 |
| SSOT 真源 | pass | 节点契约完整，暂停令与 miss:slot 台账在册 |
| 代码模块 | warn | 槽机制在位；light 执行器事故已治标（改 default），治本（executor 注册校验）未见 |
| 门禁约束 | pass | Owner 暂停令经正式通道（paused_zh 在册），本挖矿不列开发项合规 |
| 自动化触发 | warn | 每日 firing 30d=110 拍但从未跑成过自动水位（历史事故谱），触发≠产出 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：**unwired_slot_hollow 五分之一在本格**（miss:slot:daily_crypto）。
- gap_refs 在册：`miss:slot:daily_crypto` 全体有效任务在补跑宇宙外 + 6 个 task: 台账项（crypto_kline_daily_incremental / crypto_shadow_gate_daily / hl_funding_history_incremental / hl_liquidation_capture / hl_oi_snapshot_daily_refresh / hl_perp_snapshot_daily_refresh）。
- 建议：①暂停令在位期间不做任何开发动作（合 Owner 门位）；②解禁时先补三件：任务挂载有效性校验（APScheduler 注册不校验 executor 的根因）、补跑宇宙纳入、水位自动推进断言；③跨机制漏拍（资源册 window_expr 未抽到该槽）属资源画像盲区，归排班族工具链。
