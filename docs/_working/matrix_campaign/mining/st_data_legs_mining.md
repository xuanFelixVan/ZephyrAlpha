---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_data_legs —— 数据供给腿（借力挖矿，不占 182/341 口径）

- 性质: **借力挖矿**——数据供给链图（图12，43 节点/62 边）归 chief ENV-01..05 与 fig12 队所有，本册只做骨架交叉引用与断供账转抄，不判其缺口细节（00 §7.8 自查第 8 条）。
- 真源: chief=`docs/_working/chief_fullchain_20261006/01_skeleton_environments.md`/`02_gap_ledger.md`；census 图12 节=`00_panorama_map_census_v1.md` §3。
- 与两主图的关系：TDM L9（st_l9_alt）=决策消费面源线目录；SPM E4 数据件群=考卷后勤；图12=采集入库运维链。三面一域。

## 1. 图12 五段骨架（chief B1 §2 甲段转抄，计数实查于 chief 01 §1 表）

| 段 | 环节 | 节点 | built/partial/pending | chief 作业簿 |
|---|---|---|---|---|
| S1_collect | 采集（23 家源×三通道） | 7 | 3/1/3 | env_01_collect |
| S2_ingest | 集成入库（CH 双级+WAL+判重） | 6 | 4/1/1 | env_02_ingest |
| S3_derive | 衍生（因子/指标原料 DAG） | 10 | 0/5/5 | env_03_derive |
| S4_coldstore | 冷备灾备 | 9 | 5/3/1 | env_04_coldstore |
| S5_recon | 数据对账修复 | 11 | 4/5/2 | env_05_recon |

- 图12 总账（chief 01 §1 表）：43 节点/62 边；gaps_registered=69，unwired_or_hollow=9，verified_semantics=42。
- census §3 图12 补充：tasks.yaml 272 任务/23 源；schedule.yaml 27 cron 槽；机生真源=generate_data_acquisition_flow.py（采集段已机生，扩全链即可）。

## 2. 运行态断供账转抄（chief 02 §2/§3，归属 st-datasop）

- 断供：新闻评分链 news_sentiment_score 断 13 月；台风 F7 复活/reservoir_level 半死/board_index_tick 断档；P1 断供批 17 项（EXEC-1 已消 3）；market_etf_share_snapshot 任务在岗源死（东财 push2 拒连，源恢复自愈）。
- 已修待验：期权 greeks/iv_surface（84bb7f8d83a，EXEC-2a）。
- 消费接线组 20 项（HANDOVER 3-1..3-20，登记待认领）：情绪温度计五成分/attribution_results 接线/knowledge 写口/溢价率三表互救/BOM 叶挂价/style_regime 接宏观/AH 溢价/基本面五岛/convertible_bond_list/futures_term_structure 等。
- 骨架断链组（chief 02 §4）：F16-F20 五条进货车道复活（lane_c 停 14 天，与 st_e1 互链）；D13-20 竞价窗闸恒 skipped；D13-44 日界交接断供；3 个空调度槽。

## 3. 本车道补充挖矿：两主图内的"数据腿"分布（census/chief 均未记载的视角）

1. **SPM E4 数据件群 24 枚**（M-024~M-041、M-051~M-052、M-055~M-058，st_e4 §3）——考卷后勤数据面与图12 职能重叠，层语义混装。
2. **TDM L9 源线 44 枚**（st_l9_alt）中 30 枚 C 类图纸源线=图12 tasks.yaml 未覆盖或未消费的增量需求面（对应关系逐条=not_mined，需图12 任务名对照，留 fig12 队）。
3. **对账链 ENV-15 全链最薄**（chief 01 §3.3：三账核对/当日回测/execution_report 未产表）——与 TDM L4-13 三方对账（D/ND）、E7-M-011 日终对账（built）三点互链：对账骨架分散三图且只有 E7 一点 built。

## 4. 一句话修复建议

对账链（ENV-15）按 chief 建议走施工令级立项；本册不代修，只提请矩阵考试把"三图对账分工"设为必考题。

## 5. 交叉验证

- census §2.3 判"数据管线独立建图不进 TDM/工厂"与本册三面一域观察一致。
- chief ENV-01..05 计数转抄未复算（图12 归他队）——本册所有图12 数字均标 chief 出处，非本车道实查。
- TDM L9-A09 断供（新闻 13 月）与 chief 02 §2 互证；L9-A12 天气与台风 F7 互证。
