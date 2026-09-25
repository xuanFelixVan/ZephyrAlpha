---
ttl: task_bound
title: L02 大盘情绪 · 子模块清单与封矿状态总勾表
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: 环节 2 子层挖干交付
---

# L02 · 子模块总勾表（父层=SKEL.md，本表=子层入口）

> 编号沿用：E 线 Gx（emotion gap 单）/DU-xx（12 号文）/CNS-xx（14 号文）/L02-Cxx（SKEL 施工项）/LK-01、LK-02（09 号文）；本层新缺口 `L02-<子块>-Gm` 注"册内未见"。D/E 两候选类目因同属"原料通、腿未挂"薄矿，合为一簿（文件内分节，MECE 不重叠）。

| 子簿 | 覆盖 | 态 | 净新增缺口 | 对 SKEL 的改判 |
|---|---|---|---|---|
| `a_builder_kernel` | builder 合成核+DDL+双任务 | 已挖干 | G1 pre_open 无回放 / G2 无成分哨兵 / G3 stage 消费口径未统一 | — |
| `b_history_replay_line` | 回放线 | 已挖干 | G1 live/replay 撞键无机械守卫 | **代码已在主区（`??` 未跟踪）、文档已暂存、source 列已在 HEAD → L02-C01 缩为"两文件提交"** |
| `c1_limitup_temperature` | C1 | 已挖干 | G1 断供即退化 / G2 满窗无触发器 | daban 实测复断（09-23/24 缺，G3 销口需重开） |
| `c2_promotion_rate` | C2 | 已挖干 | G1 炸板率未独立 / G2 晋级率两读面 | **恒 1.0 缺陷取得活体行级证据（obs=16/percentile=1.0）** |
| `c3_breadth` | C3（唯一 KEEP） | 已挖干 | G1 广度双口径无对表 / G2 stub 段诚实标记未落表 | — |
| `c4_volume_energy` | C4 | 已挖干 | G1 成交额未市值归一 | — |
| `c5_leverage_margin` | C5 | 已挖干 | G1 考试回补史未回流 / G2 静默无哨兵 | **DU-03"09-19 起 4 交易日断"实测为周末非断供，末数据 09-23**（交数据班复核销口） |
| `c6_news_sentiment` | C6 | 已挖干 | G1 rule/market 日期错位 3 日 / G2 experimental 分支进生产写库 | **§6 张力 3 收口：llm 仅 3 行、对照期未成立** |
| `d_e_auction_and_rating_candidates` | D 竞价 + E 评级 | 已挖干 | G1 auction 17 行数据孤本 / G2 auction stage 分母残缺 | **§6 张力 1 收口：auction 行确在（17 行 live）但 HEAD 无写手** |
| `f_legacy_emotion_cluster` | 四件存量簇 | 已挖干 | G1 档位计/温度计无口径词表 / G2 intraday 环 production 却不挂任务 | 两件路径纠正 + 成熟度实测 production |
| `g_tomorrow_emotion_forecast` | L0-04 六件族 | 已挖干 | G1 环节级"无概率表"结论需更正 / G2 Brier 链路无机读校验 | **next_day_forecaster 盘后挂点实测在链（pipeline_events:1078-1082）→ D7 收窄为"盘中滚动腿"** |
| `h_consumption_surface` | 消费面 | 已挖干 | G1 偏好表仅盘前侧、覆盖≈0 / G2 无消费方机读登记 | **D13 已落地（mock 分支删除，随 commit d27e0f0df3 进 HEAD）→ L02-C03 销口** |

**合计 12 簿（覆盖 13 个子类目）：已挖干 12 / 在挖 0**。

## 本环节净新增缺口汇总（22 条，三态分布）

施工 14（A-G1/A-G2/A-G3、B-G1、C1-G1/C1-G2、C2-G2、C3-G1/C3-G2、C6-G1、F-G1、G1(文档面)、H-G1 + 文档销口 2 条）；挂起 8（C4-G1 市值归一、C5-G1/G2、C6-G2、C2-G1、D/E-G1 复职批依赖、F-G2、G-G2、H-G2）；封矿 0（本子层无"终局无位置"项——情绪为独立状态变量已裁，凡消灭人工误读者一律给位置）。

## 本环节穷尽性声明

**扫过的源**：①`src/zephyr/alt_data/{emotion_index_builder,emotion_index_replay,alt_regime_signals}.py` 键段行号级 ②`schemas/categories/market/market_emotion_index.py` ③`src/zephyr/data/config/tasks.yaml`（情绪/两融/竞价/新闻相关任务全查，实测情绪仅两任务）④`src/zephyr/intelligence/{nightly_sentiment_window,news_sentiment_analyzer,news_llm_scorer}.py` ⑤存量簇四件（含路径纠正）⑥`plan_engine/` 六件族 ⑦`src/zephyr/strategy_pipeline/pipeline_events.py`（盘后挂点）⑧`sector_state_aggregator.py` 消费侧 ⑨CH 只读探针 7 组（emotion_index 三 stage×source、daban、margin、news scope/data_source、sector_preference、auction_snapshot、research_report）⑩`data/runtime/nightly_sentiment_llm.enabled` 旗标实测 ⑪全网检索 4 轮（涨停/晋级率/炸板率族两源、广度 A/D 两源、竞价教程级判不过质量闸、LLM 对照法单源）。

**封顶判据**：12 簿六向全部有发现或"已查无/受阻+查法"；`emotion_index_builder._build_components` 内六成分**逐一走号归位**到 c1~c6 簿；四件存量簇、六件预测族、两任务、七张原料表全部落册，无未归位资产。噪音轮 6 轮全部记档归因；未以轮数封矿。

**边界**：daban 采集链治理归数据班/L15 车道；两枚举收敛归治理班；盘中节拍归 L09 车道。
