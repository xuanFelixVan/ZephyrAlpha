---
ttl: task_bound
---
# SDSC-14 缺口回补三通道（行数缺口 / 档期打卡 / 已知缺口台账）

> 挖矿工程：全链路图12 数据供给链 S5 对账修复段 2/8｜真源=config/data_supply_chain_map.yaml#DSC-14｜挖矿时点=2026-10-15
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：缺口回补三通道（行数缺口/档期打卡/已知缺口台账），node_type=stage，build_status=partial，verified_scope=structure，行级状态=分面（weekend 🔨/daily 🔨/catchup 🔨/auto4 ⬜ 退役留档）。
- 职责一句话：三通道口径互不重叠——weekend_backfill（过去 7 天行数缺口）/daily_backfill（当日全表缺口）/catchup_guard（档期 vs 打卡对账，不看行数）；第 4 通道（事件自动回填 auto_backfiller）单列 DSC-14D 并经 Owner 2026-10-04 批留档退役。catchup_guard 从 DSC-13 去重移归本环节（WB12-27）。
- 决策问句（图原文）：哪一类缺口由哪一条通道捞？通道自己不跑了谁会知道？

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | DSC-20→DSC-14 control 边（漏跑清单=catchup 的基准输入，批次4 移交后唯一路径）；行数缺口自发现 | config/data_supply_chain_map.yaml edges DSC-20→14 |
| 输出面 | 补跑动作经 scheduler.run_task（与被补任务同写手同表）+补跑台账 integrator_progress.db（键=被补任务原 task_id）+缺口台账 known_data_gaps.yaml；反馈边回 DSC-01/02/03（重放采集） | config/data_supply_chain_map.yaml edges DSC-14→01/02/03+feedback_loops；src/zephyr/data/config/known_data_gaps.yaml |
| SSOT 真源 | 三通道槽位真源=schedule.yaml（weekend_backfill/daily_backfill/catchup_guard 三槽全特殊分派）；缺口台账规则真源=known_data_gaps.yaml；语义层=图12 DSC-14 | src/zephyr/data/config/schedule.yaml；src/zephyr/data/config/known_data_gaps.yaml；config/data_supply_chain_map.yaml#DSC-14 machine.slots |
| 代码模块 | module_id=MOD-L00-021，module_ref=src/zephyr/data/catchup_guard.py；执行体 backfill_checker.py+catchup_guard.py 实存；第四通道 auto_backfiller.py 在盘退役留档（wiring_registry CAND-DAT-014 pure_library/exempt） | src/zephyr/data/catchup_guard.py；src/zephyr/data/backfill_checker.py；src/zephyr/data/auto_backfiller.py（本批 ls；退役批复 IN1-E7④ docs/_archive/_working_cleared/vmap12_intake/） |
| 门禁约束 | catchup_bounded（单批限量+trading_day_only 顺延+RUNNING 跳过防撞车）；补跑走 run_task=合并前按行数判据会飘（须 FINAL）；通道自身不留 progress 键（记被补任务名下=健康度不可直接观测） | config/data_supply_chain_map.yaml#DSC-14 fallback |
| 自动化触发 | wired_cron：三槽特殊分派（dispatched_slots 在册）；run 计数腿未接（task_runs 零行=期望 7 计数缺席，禁判死）；catchup 末次打卡 09-25T01:24Z（北京 09:24，PARTIAL rows=15）=非声明的 05:30 档 | config/data_supply_chain_map.yaml#DSC-14 facets/machine/trigger_facts（as_of 2026-10-04 insufficient_window） |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | pass | DSC-20 漏跑清单基准链在册（案卷连日到 10-14，SDSC-20 交叉证） |
| 输出面 | warn | 补跑台账/缺口台账两件在册；但 known_data_gaps 仍有 open/monitoring 未了账（在册），补跑后行数判据须 FINAL 的约束靠人工遵守 |
| SSOT 真源 | pass | 三槽+缺口台账+图节点一致；第四通道退役留档有 Owner 批文+注册表豁免双证 |
| 代码模块 | pass | 三执行体实存；退役件在盘摘挂载合规 |
| 门禁约束 | warn | "通道自身健康度不可直接观测"（no_channel_name residual）+catchup 档期漂移（末次 09:24 非 05:30 档，schedule.yaml 自述过渡补丁）——③ 兜 ① 的前提在册存疑 |
| 自动化触发 | warn | 三槽分派分支在机；但 catchup_guard task_runs=0（本批复读，计数腿未接 by design）+末次打卡停在 09-25=通道节拍无新鲜读数 |

## 4. 缺口与建议

1. 【warn 最直接】catchup_guard 档期漂移：schedule.yaml 自述"该槽被当成周末校准槽的过渡补丁"——建议把 05:30 档正式落 cron 或在图上明示现行为设计态，终结"③ 兜 ① 前提不成立"的悬账。
2. 【warn 观测腿】通道健康度不可直接观测：建议三通道每次执行写一行 channel_runs（channel/被补 task/rows/verdict）进 progress db 新表——与 DSC-20 案卷同目录族，半日工。
3. 【退役正向】第四通道留档退役（文件在盘摘挂载+Owner 批+豁免登记）是内收判据的合规执行样例；SOP 中把它写成常态在岗的矛盾描述（data_source_onboarding_sop.md）建议同步修订，消文档矛盾=事故条款。
