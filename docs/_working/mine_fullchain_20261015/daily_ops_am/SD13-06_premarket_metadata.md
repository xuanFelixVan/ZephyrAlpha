---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-06
segment: fig13-A 盘前
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-06 L0.5 盘前元数据（universe 与撮合约束前提）

## 1. 定义

交易日晨间 08:34（APScheduler 0-4 口径）常规 DAG 槽 `pre_market`（9 个有效任务）产盘前元数据五子源：universe 成分/停复牌/撮合约束等决策链前提。决策问题：08:34 五子源都到位了吗？有没有「任务 SUCCESS 而水位不动」的子源？

地图在册态：wiring=partial、build=partial、red_reason=broken_supply、subsource_hollow=true（名义在产、一子源零行且不在任何哨兵名单）。簿 02 实测：四子源有行、停复牌子源 0 行且水位停在纪元起点；C2 字面口径假绿的实证源（11,106=2×5,553 行、无当日行）。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | universe 五子源（成分/停复牌/涨跌停价/换牌/撮合参数）；蓝图册 | `src/zephyr/data/config/schedule.yaml:24`（pre_market 槽）；`docs/03_modules/_domain_data/data_source_integrator_blueprint.md`；`docs/01_policies_and_standards/_registry/catalogs/universe_registry.yaml`（universe 资产册实存，骨架指针 `catalogs/` 为缩写路径） |
| 输出面 | universe/撮合约束前提表（当日行）；停复牌子源 0 行=子源断链整槽不得判绿 | `docs/_working/map_build/fig13_daycycle/02_盘前元数据与竞价.md` §D13-06（簿 02 实测） |
| SSOT 真源 | 图13 节点契约（行 547-623）+ universe 资产册 | `config/trading_day_cycle_map.yaml#D13-06`；universe_registry.yaml（路径同上） |
| 代码模块 | 槽任务挂载面（地图锚 scheduler.py:475 为挂载编排区） | `src/zephyr/data/scheduler.py`；`src/zephyr/data/config/schedule.yaml:24` |
| 门禁约束 | 双层哨兵共同盲区：同一子源不在断供哨兵（D13-02 配置）与日历覆盖检查（D13-03 名单）任何名单内——「SUCCESS 而水位不动」型假绿不可被现有哨兵捕获 | `docs/_working/map_build/fig13_daycycle/01_盘前就绪链.md`（簿 01 O-4）；`src/zephyr/data/config/data_supply_sentinel.yaml`（名单面） |
| 自动化触发 | mechanism=A_apscheduler，交易日 08:34；30d count=158（9 任务求和）；in_catchup_universe=true（pre_market 在 intraday 桶，可被 D13-01 补） | `config/trading_day_cycle_map.yaml#D13-06` trigger_facts/machine_facts |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | fail | 停复牌子源 0 行且水位停在纪元起点——子源断链，整槽不得判绿 |
| 输出面 | warn | 四子源有行（局部在产），当日行面靠断链子源补齐才完整 |
| SSOT 真源 | pass | 节点契约+簿 02 逐子源读数在册，subsource_hollow 显式登记 |
| 代码模块 | pass | 槽与 9 任务挂载实存，30d 158 拍 |
| 门禁约束 | fail | 双层哨兵共同盲区：断链子源不可检出（哨兵名单+覆盖名单双缺） |
| 自动化触发 | pass | 交易日每拍 firing 在案且在补跑宇宙内（fallback=D13-01 有效） |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：无 G 节点，但本格是 **D13-09 就绪门 C2 判据被证伪的实证源**（SUCCESS 而水位未动型假绿）——门 C2 定义因此被地图钉死为「水位比对==今日，禁沿用最近运行 SUCCESS 字面口径」。
- gap_refs 空（subsource_hollow 字段承载）。骨架指针 `catalogs/universe_registry.yaml` 实际路径=`docs/01_policies_and_standards/_registry/catalogs/universe_registry.yaml`（登记时勿按缩写路径找）。
- 建议：①停复牌子源断链修复（矿权归数据链 S1/S5，本段只挂需求）；②该子源补进 D13-02/D13-03 双名单；③「SUCCESS 而水位不动」检测器应成为通用判据件（可挂在 task_runs×表行数交叉核对，与 DSC-20 任务级对账同族）。
