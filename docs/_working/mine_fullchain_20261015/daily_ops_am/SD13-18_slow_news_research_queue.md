---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-18
segment: fig13-B 盘中
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-18 慢新闻/研报独立队列（限流分池）

## 1. 定义

7×24 每小时 17 分与 47 分两拍 DAG 槽 `news_slow`（2 个有效任务）：个股新闻（stock_em）/研报（research_report）独立队列不堵 event_driven 快新闻。分池理由=单例限流额度共享致并行总时间与串行相同（槽注释自证）。决策问题：共享额度下的分池节拍成立吗？研报腿断供几个交易日？

地图在册态：wiring=partial、build=partial、red_reason=broken_supply；簿 04：研报腿实测断供 4 交易日，且断供哨兵配置不含该表（配置面事实，簿 09）。tdm_refs=TDM-E-L9-A09。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | 个股新闻源+研报源（限流额度共享） | `src/zephyr/data/config/schedule.yaml:66-68`（槽声明+分池理由注） |
| 输出面 | 慢新闻/研报表族；研报腿断供 4 交易日（在册定性） | `docs/_working/map_build/fig13_daycycle/04_盘中采集层群.md`（环节段） |
| SSOT 真源 | 图13 节点契约（行 1457-1534）+ 簿 04/簿 09 | `config/trading_day_cycle_map.yaml#D13-18`；`docs/_working/map_build/fig13_daycycle/04_盘中采集层群.md` |
| 代码模块 | 采集腿+DAG 槽（2 任务） | `src/zephyr/data/scheduler.py`；`src/zephyr/data/config/schedule.yaml:66`；alt_data 侧消费（骨架指针） |
| 门禁约束 | **断供哨兵配置不含研报表**（D13-02 名单面事实）=研报腿无哨；expected_emits_per_trading_day=1 已落格但缺产告警无主体（A4） | `src/zephyr/data/config/data_supply_sentinel.yaml`（名单不含，簿 09）；`config/trading_day_cycle_map.yaml#D13-18` expected_emits_per_trading_day/gap_refs |
| 自动化触发 | mechanism=A_apscheduler，每小时 2 拍（7×24）；30d count=280（×2）；in_catchup_universe=true 但 fallback 注记=无（不在补跑宇宙，两注冲突以 machine_facts 为准） | `config/trading_day_cycle_map.yaml#D13-18` trigger_facts/machine_facts（in_catchup_universe.news_slow=true） |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | warn | 个股新闻腿在产（280 拍/30d），研报腿断供 4 交易日 |
| 输出面 | fail | 研报表 4 交易日零产出 |
| SSOT 真源 | pass | 节点契约+簿 09 配置面事实在册 |
| 代码模块 | pass | 槽与两腿执行体实存（断供属源/通道层非代码缺失） |
| 门禁约束 | fail | 哨兵名单不含研报表=断供不可检出；A4 应产断言已落格但告警无主体 |
| 自动化触发 | warn | 节拍在案但 fallback 字段自相矛盾（fallback「无」vs machine_facts in_catchup_universe=true） |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：**D13-G04 的姊妹格**（同族新闻产物，edges D13-18→D13-G04）；A2/A4/C4 三 benchmark 缺口汇聚格。
- gap_refs 在册：benchmark:A2（freshness 分级未接线）、benchmark:A4（expected_emits 应产断言未接线——本格先落应产数，缺产告警仍无主体）、benchmark:C4（分级归属留裁）。
- 建议：①研报腿修复归数据链 S1 车道，修复前先把研报表补进 D13-02 哨兵名单（半小时级小改，立即消灭不可检出状态）；②A4 告警主体与 C4 分级归属一并用裁定收口；③fallback 字段矛盾提交图13 机生层复扫。
