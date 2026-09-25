---
ttl: task_bound
doc_type: log
title: L02-C6 子类目挖矿簿 · 新闻情绪成分（C6_news，含 LLM 分支落库实测）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（SKEL §6 三条未决张力中的两条以实测收口）
---

**① 一句话**：市场级新闻情绪 5 日均值的秩分位，度量舆论温度（当前纯 rule 法）。

**② 实测**：`emotion_index_builder.py:315-324`（`_SQL_NEWS_MEAN` :123-127 只取 `scope='market'`；`_NEWS_MEAN_DAYS=5` :78）；考试 **NO_SIGNAL**（RankIC −0.022，归因 rule 法）。写入侧 `src/zephyr/intelligence/nightly_sentiment_window.py`（MATURITY=testing，头注 :5 记"schedule nightly_sentiment 08:20 日频、scheduler._run_special_schedule 分派、2026-09-10 治本接线"；LLM 分支 :236-240 经 `make_llm_scorer()`，旗标 `data/runtime/nightly_sentiment_llm.enabled` 实测存在，mtime 09-23 05:16）；适配器 `src/zephyr/intelligence/news_llm_scorer.py` 96 行 **MATURITY=experimental**（本册实测，SKEL 未记其成熟度）。**表实测（本册 CH 只读探针）**：`news_sentiment_window` scope=market **186 行 2026-02-24→09-24**、scope=symbol **19,635 行 止 2026-08-20（DU-06 复证）**；**data_source=rule 19,818 行（max 09-21）／llm 仅 3 行（max 09-24）** → SKEL §6 张力 3（"LLM 已翻转但对照期未核"）**收口**：翻转确已发生但只产出 3 行，对照期实质未成立；同时 rule 腿 max=09-21 与 market 腿 max=09-24 存在 **3 日口径错位**（本册净新增）。

**③ 六向**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：`c3_fundamental.news_data`（8.25M 行级，12 号文在册）→ 夜间窗聚合。外部：LLM 大规模打分件题录沿用仓册（FinBERT/GPT 对照族），本册新增核验=**外部亦以"规则法 vs LLM 法"并行对照为常规**→ 单源，标待验证不入图 |
| ②下游 | 内部：C6→情绪；MOD-PLAN-004 `overnight_boundary_reviser` 预留 plan004_input **未接线**（头注自注）。外部：已查无 |
| ③算法 | 内部：5 日均值→分位（抗单日噪声）。外部：已查无 |
| ④后端 | 内部：**双时点口径未辨**（头注 08:20 vs 12 号文 20:08，SKEL 张力 2 → 本册仍未证，如实挂"受阻"）；news_sentiment_score 打分链停摆（DU-05）在册 |
| ⑤前端 | 内部：情绪页新闻卡。外部：已查无 |
| ⑥数据字段 | 内部：sentiment_index/total_count/top_events_json/data_source 在；质量画像=**llm 3 行 = 不可用级**、symbol 腿断 1 个月+ |

**④ 缺口**：G6（rule 单法）/DU-05/DU-06（在册）；**L02-C6-G1 rule 腿与 market 腿日期错位 3 日（同一 scope 下 data_source 分布不一致的根因待查）**；**L02-C6-G2 LLM 分支 experimental 却经旗标进入生产写库路径（成熟度与门位不对齐）**。

**⑤ 三态裁定**：G6/DU-05/DU-06=施工（L02-C04/C05 在册）；G1=**施工 P1 查证项**（一次只读探针即可定性，属"消灭人工猜"）；G2=**挂起排期**（启闭=Owner 门位，AI 不自翻旗标；解锁=Owner 对照期判据签发）。

**⑥ 日志**：R1 内部：news 表两维探针→signal（张力 3 收口 + 新错位发现）；R2 内部：llm scorer 成熟度→signal；R3 外部：LLM 情绪对照法→noise（单源，归因=收费墙/未全文核）；R4 内部：调度时点两口径→受阻（未能在只读面证伪，如实记不判查无）。

**封矿判据**：六向封口（1 条如实标"受阻"）→ **子类目封矿**。
