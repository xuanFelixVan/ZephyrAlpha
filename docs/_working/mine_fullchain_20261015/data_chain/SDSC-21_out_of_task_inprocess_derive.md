---
ttl: task_bound
---
# SDSC-21 任务表外进程内派生生产（工厂/回测/组合域直写 CH）

> 挖矿工程：全链路图12 数据供给链 S3 衍生段 4/4｜真源=config/data_supply_chain_map.yaml#DSC-21｜挖矿时点=2026-10-15（含当日只读复跑）
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：任务表外进程内派生生产（工厂/回测/组合域直写 CH），node_type=stage，build_status=partial，verified_scope=structure（🔨 为该格状态天花板：不走任务表⇒任务在策与档期留痕两腿结构性缺位）。
- 职责一句话：生产者在工厂/回测/组合/计划域进程内，不走 tasks.yaml/schedule.yaml——只能以表新鲜+写器代码在位证在产。D12-21 专款防腐：新表入本格必过三问，应挂任务表面未挂者不得入格、一律走 gap 红项。
- 决策问句（图原文）：消费端在用的这批表是谁产的？没有 task_id 与档期的产线怎么被检核？

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | 上游=E3 构造/回测/组合域进程内产物（非图内节点边，域间输入）；原料=库内成品表+进程内计算 | config/data_supply_chain_map.yaml#DSC-21 note_zh/source_anchors（五写手锚） |
| 输出面 | c1_backtest.regime_snapshot_history/strategy_screen（+C 态 4 表）→DSC-HA 出图被消费（11 卷 174 点分母的组成部分）；本批复跑：regime_snapshot_history 3,638 行 max=2026-10-14（鲜）、factor_feature_value/factor_signal 两表已建但 0 行（产数未启动） | config/data_supply_chain_map.yaml#DSC-21 data_refs；本批 CH 直查（strategy_screen 无 trade_date 列=另一日期口径，列名待查） |
| SSOT 真源 | 三问准入纪律=图12 专款（12 簿 §1.4 裁定+反方理由）；process_in_product_tables 机械尺（六表在 tasks.yaml 命中数全 0 ⇒ 生产者不在任务表面） | config/data_supply_chain_map.yaml#DSC-07 machine.internal_task_ids/process_in_product_tables（锚点合并 &id002）；docs/_archive/_working_cleared/map_build/fig12_datachain/12_扩行提案与封顶重宣.md §1.4 |
| 代码模块 | module_id=MOD-PA-031，module_ref=src/zephyr/pf_alloc/allocation_inputs.py；五写手（allocation_inputs/allocation_orchestrator/daily_loop_master_switch/n_trial_ledger/strategy_screener_3d/live_nav_recorder）实存 | src/zephyr/pf_alloc/allocation_inputs.py；src/zephyr/plan_engine/daily_loop_master_switch.py；src/zephyr/backtest/core/n_trial_ledger.py；src/zephyr/pf_alloc/core/strategy_screener_3d.py；src/zephyr/position/live_nav_recorder.py（本批 ls） |
| 门禁约束 | D12-21 三问防腐（应挂任务表面未挂者走 gap 红项）；新表入格回写骨架 §1；CREATE-GUARD/登记义务不豁免进程内写手 | config/data_supply_chain_map.yaml#DSC-21 note_zh；tasks.yaml 车道F 注记（disabled 登记留位=合规通道先例） |
| 自动化触发 | wired_import（进程内随宿主进程，无档期无打卡=两腿结构性缺位）；唯一节拍证据=产物表新鲜度 | config/data_supply_chain_map.yaml#DSC-21 wiring_status/trigger_facts（insufficient_window） |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | pass | 五写手宿主域（工厂/回测/组合）代码在位，域间输入关系在册 |
| 输出面 | warn | regime_snapshot 今日鲜（max=10-14）；但 C 态 4 表中 FFVAL/FFSIG 已建 0 行（产数未启动）、NAV 已复活（9 行 max=10-15，GAP-F-29 经 run_post_settlement 接线）、execution_report 仍 1 行（实盘链未接）——产出面四态并存 |
| SSOT 真源 | pass | 三问纪律+机械尺（命中数全 0）在册且本批未发现违反（新登记的 factor 两任务走 disabled 留位=按规矩来） |
| 代码模块 | pass | 六写手全部实存（live_nav_recorder 新增生产调用方 scripts/run_post_settlement.py 实读） |
| 门禁约束 | warn | 三问防腐靠人工自觉+图复查，无门禁硬拦"进程内新写手未过三问" |
| 自动化触发 | fail | 无 task_id 无档期无打卡=触发面结构性缺位（该格天花板即 🔨）：产物新鲜度是唯一可观测腿，宿主进程不跑则全格静默归零且无告警 |

## 4. 缺口与建议

1. 【fail 结构项】触发面缺位是该格本质风险：建议最低成本补法=给六个进程内写手加"产物日期自检"（写后读回 max(date) 写一行 progress），让 DSC-20 的应跑集合外多一张"应产清单"。
2. 【warn 收口中】C 态 4 表分化：NAV 已接线复活（GAP-F-29 净值腿，今日 9 行鲜）、execution_report 实盘链仍 0 供给（E4 断点在册）、FFVAL/FFSIG 表建产数未启动（车道F disabled 留位+恢复条件已写明）——建议按"一表一票"推进消账，图侧 waiting_table_gaps 三态分化应逐格更新。
3. 【正向证据】live_nav_recorder 已从"全仓零调用方"变为有生产调用链（scripts/run_post_settlement.py:445-454 延迟 import+record_daily_nav 落库），DSC-GAP-NAV 的 red_reason=unwired 事实基础已消失。
