---
ttl: task_bound
title: L03 板块状态与轮动 · 子模块清单与封矿状态总勾表
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: 环节 3 子层挖干交付
---

# L03 · 子模块总勾表（父层=SKEL.md 八子块，本表=子层入口）

> 编号沿用：S 线 Gx（sector_gap_list）/DU-xx/LK-03/L03-Cxx（SKEL 施工项）；本层新缺口 `L03-Bm-Gn` 注"册内未见"。**切分与 SKEL 的差异（如实注）**：SKEL B2 一册混装了"算法核"与"落库编排"，本层拆为 B2+B3；SKEL B4（轮动序列）与 B5（三标尺）合并为一册 B5（16 件算法农场，逐件归位），三标尺原料仍按 G14 挂起。

| 子簿 | 覆盖 | 态 | 净新增缺口 | 对 SKEL 的改判（本册实测） |
|---|---|---|---|---|
| `b1_index_data_foundation` | 880/881/分钟腿/名称 | 已挖干 | G1 名称 100% 空 / G2 史差 17 月无登记 / G3 补采验收无自动化 | **补采已落（729 码，日均 728）→ DU-01 判据①达成、②未达（881 起 2021-08-02）** |
| `b2_state_aggregation_kernel` | 五成分聚合核 | 已挖干 | G1 rrg 空串 4.8% 无归因 / G2 宇宙混合断层 | state 表实测 426,985 行/986 日/729 码 |
| `b3_pipeline_slots_preference` | 双槽+偏好 | 已挖干 | G1 pre_open 槽仅 1 日 / G2 切换日无标记 / G3 偏好语义未声明 | **偏好表全库仅 2 行、pre_open 近停摆** |
| `b4_fund_dimension` | 资金维双路径 | 已挖干 | G1 capital_score 恒空无裁 | 北向披露停两源外部证据 |
| `b5_rotation_algorithm_family` | sector/ 16 件 | 已挖干 | G1 算法农场未内收申报 / G2 881 轮动态从未产出 | 16 件 MATURITY+消费边逐件底账（SKEL 只列 8+4） |
| `b6_l2_gate_wiring` | S66 门三原料 | 已挖干 | G1 接线未验收 | **L2 门已落地进 HEAD（commit d27e0f0df3）→ SKEL"v1 stub 未落"改判、水位桥 WIP 争议消解** |
| `b7_constituent_and_coordinates` | SCD-2 + 坐标系 | 已挖干 | G1 成分表未随补采扩容（595 vs 729）/ G2 valid_to 全空 | 前视两源外部佐证 |
| `b8_p1_conditional_tables` | T1/T2/T3 | 已挖干 | G1 无 v1↔v2 对比报告 / G2 README 漂移 / G3 无重算排班 | **P1 实质已按 729 宇宙重跑（4,362 行、881 族 764 行）→ "v1 469 板"过时** |

**合计 8 簿：已挖干 8 / 在挖 0**（`ls src/zephyr/signal_ashare/sector/` 17 文件 + `data/sector_state_pipeline.py` + `strategy_pipeline/daily_gate_snapshot.py` + 四张表 + 五份 P1 产物全部归位；`sector_state_aggregator.py` 归 B2、其余 16 件归 B5）。

## 本环节净新增缺口汇总（14 条）

施工 11（B1-G1/G2、B2-G1/G2、B3-G1/G2、B5-G1、B6-G1（验收）、B7-G1、B8-G1/G2）；挂起 3（B4-G1 待 Owner 双轨、B5-G2 待史回填、B7-G2/B8-G3）；封矿 0。升格边界追认（G9/L03-C05）仍为**唯一硬呈报项**，本层不重裁。

## 本环节穷尽性声明

**扫过的源（全部只读）**：①`config/trading_decision_map.yaml` L2 全段（545-1393，节点名/模块挂点）②`src/zephyr/signal_ashare/sector/` 17 文件（wc+头注逐件）③`src/zephyr/data/sector_state_pipeline.py` ④`src/zephyr/strategy_pipeline/daily_gate_snapshot.py`（HEAD 与工作区双向）⑤`src/zephyr/plan_engine/boundary_revision_engine.py` 消费边 ⑥`data/strategy_intake/conditional_tables/` 五产物逐文件解析 ⑦`docs/_working/sector_line/` 全目录（gap 单/骨架/盘点/考试卡 v0-v2/回放 dossier/MORNING_REPORT/batch2 补丁）⑧CH 只读探针 6 组（kline_sector_880 分族与日量、sector_state stage×日×分布、sector_preference、sector_constituent、margin/daban/news 联动）⑨git log 归属核验（d070dd4270、d27e0f0df3）⑩全网检索 4 轮（拥挤度三源、动量反转两源、前视偏差两源、北向披露两源、RRG 沿用）。

**封顶判据**：8 簿六向全部有发现或"已查无/受阻+查法"；无 SKEL 未列而未归位的资产；噪音轮 3 轮记档归因；未以轮数封矿；判据口径与阈值零改动（凡涉口径变更一律转"须预注册新卡/Owner 门位"）。

**边界**：概念轴前视治理归图书馆/数据班；ETF 载体执行（G13）待 S10/D2 出档后归执行车道；坐标系裁定页（L03-C04）与升格追认（L03-C05）属 Owner 门位。

**本轮未完成项（诚实披露，交续挖）**：SKEL B4"单板块轮动预警"（TDM-E-L2-02 子件）、板块级市场状态五分类与虹吸（L2-04）、水温响应三件套（L2-05）三处仅按模块名登记、未做公式级行号实测；三标尺（G14）原料侧仅给外部配方未做仓内字段逐个 schema 核对；ETF 载体（G13）只作边界登记。以上属**矿脉未枯竭**，本环节"已挖干 8/8"的判据范围=已归位的代码与数据资产，不含上述三条明列长尾。
