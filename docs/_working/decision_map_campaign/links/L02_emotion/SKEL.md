---
ttl: task_bound
title: L02 大盘情绪链路挖干作业簿（子块全树+六向台账+自审闸+施工项+标准件）
created: 2026-09-25
sid: L02-emotion-mining
lane: decision_map_campaign/links
status: MINING（6 SEALED / 3 MINING / 0 BLOCKED；MINING 余量清单见 §3）
doc_version: v1.0
骨架真源: ../09_link_skeletons.md 环节 2 节
doc_type: log
---

# L02 大盘情绪——挖干作业簿

> 挖矿源已全读：`docs/_working/emotion_line/` 全 7 件（骨架 v0.2/盘点册 v1.1/缺口单 v1.1/考试卡 frozen v1.0/考试报告 v1.0+§重考/外部文册 v1.1/红蓝三轮记录）；`src/zephyr/alt_data/emotion_index_builder.py` 全文；`schemas/categories/market/market_emotion_index.py`；`docs/03_modules/MOD-ALT-EMOTION-INDEX-BUILDER.md`；12 号文 §1.2+DU-03/05/06 卡+勘误行；14 号文消费普查族④+§四/§五；`docs/_working/oddjobs_final/LEDGER.md` emoreplay 段（EVAP-03 三受害者）；**emoreplay 死会话残骸实勘** `.aidrafts/st-emoreplay-20260923/`（回放报告+GPU 条件矩阵三件+私有 worktree tasks.yaml）；`07_pending_work_master_list.md` C2 节（处方①已批）；TDM yaml L0-04 节；消费代码 5 件实读。
> 相对环节 2 总表的三处**状态更新**（挖干新得，环节 2 表沿用旧口径）：
> ① "仅 143 交易日"已勘误——emotion_index 表 FINAL 8,647 行、close_final **全史 8,614 个交易日**（1991-06-10→09-24 当日到），8,596 行为 source='replay' 回放面（12 号文 :72 与 :247 勘误行；emoreplay 报告 §2）。
> ② D28（D2 卡双轴真值窗）**实质已解锁并重考出档**：emoreplay 把 W_map 从 16 日推到 **1,585 日**，D2 双轴重考主判 **NO_MAP**（偏好映射对次日板块结构无解释力；emoreplay 报告 §6①）——环节 2 表⑤"D28 预登记 INSUFFICIENT"已过时。
> ③ C6 的 LLM 分支旗标 `data/runtime/nightly_sentiment_llm.enabled` **已存在**（mtime 09-23 05:16）——S5 交付时"出厂不存在"，现旗标已立，对照期落库质量未核（§3 D 块 MINING 项）。

## §1 子块全树

```
L02 大盘情绪
├─ A 指数 builder 主链（在产）………………… builder+DDL+provider 路由+双任务
├─ B 全史回放线（emoreplay 残骸）………… DB 面已落、代码面滞 .aidrafts
├─ C 成分族 C1-C6 …………………………………… C1/C2 daban 链｜C3 KEEP｜C4/C5/C6 观察
├─ D 新闻情绪窗 …………………………………… market 腿在产｜symbol 腿 DU-06｜score 腿 DU-05｜LLM 旗标 ON
├─ E 两融温度 ……………………………………… C5 原料：S4 回补 442 日 + DU-03 断 4 日
├─ F 竞价情绪 ……………………………………… 原料通、stage 预留、post_auction 槽蒸发
├─ G 评级情绪候选 ………………………………… research_report S20/DU-12
├─ H 存量同域簇与内收 …………………………… sentiment_cycle 三枚举+F23+裁定#400
└─ I 消费面 …………………………………………… 偏好第二轴(D13 mock/D2 NO_MAP)/T0 条件矩阵/L0-04/回测 condition_package
```

## §2 六向台账（逐子块）

### A · 指数 builder 主链

| 向 | 内容 |
|---|---|
| ①上游输入 | tasks.yaml 双任务 deps：`daban_board_event_derive`/`kline_daily_incremental`/`kline_index_incremental`/`margin_trading_incremental`（src/zephyr/data/config/tasks.yaml:3452-3464）；盘前任务 deps=[]（as-of 语义自洽，tasks.yaml:3473） |
| ②数据原料 | 五表经 TableRegistry 唯一真源（builder :81-85）：daban_board_event/kline_daily/kline_index(000300)/margin_trading/news_sentiment_window(scope='market')；禁 fear_greed 异轴顶替（builder 头注+t0 判例） |
| ③状态输出 | c1_market.emotion_index（DDL 真源 schemas/categories/market/market_emotion_index.py，ReplacingMergeTree (trade_date,stage) 幂等）；契约五字段 emotion_index∈[0,1]+components JSON 六成分明细+version v0.1.0；行数 FINAL 8,647（12 号文 :72） |
| ④下游消费 | data/sector_state_pipeline.py:59,109-158（偏好重映射，消费 close_final@T）；signal_ashare/sector/sector_state_aggregator.py:495-508；backtest/regime_validation/condition_package.py:52-183（T0 灰度五档，公式冻结）；internal_compute_provider.py:597-598,1305-1345（capability 路由） |
| ⑤自动化挂点 | emotion_index_close_final（schedule=daily_kline 盘后 15:10）+emotion_index_pre_open（schedule=pre_market 09:15）——**在产**（tasks.yaml:3452,3466；12 号文 :72"当日到"） |
| ⑥缺口债 | D-1 C2_promotion 恒 1.0（CH join_use_nulls=0 使 LEFT JOIN 未命中 countIf 恒真；daban 史满 120 观测后会把指数常数项拉高——emoreplay 报告 §5 D-1，已入 07 号文 D 节"2027-03 前"）；D-2 子项 obs 取 min 拉低整成分（2005-01-05→07-06 全史只剩 C4）；1991-2018 段为 ~237 只 stub 宇宙分位（跨 2019 断崖不可比，输入包带 universe_honest_ok 列——emoreplay §1） |

### B · 全史回放线（emoreplay 残骸）

| 向 | 内容 |
|---|---|
| ①上游输入 | 冻结公式零复制：回放器 import builder 逐日调原函数+切片缓存 reader 注入（emoreplay 报告 §2） |
| ②数据原料 | 同 A 五表全史；70/70 形状字节等价+10/10 活值逐位对拍自证（§3）；JOIN 形状白名单外直通真查询（窗界伪影防） |
| ③状态输出 | **DB 面已落**：8,596 行 source='replay'（1991-06-10→08-31）+表新增 source 列（ALTER 已执行，P-1 已批面）；**代码面未落主区**（见⑥） |
| ④下游消费 | GPU 情绪条件矩阵输入包 8,613 行×24 列（band5/band3/六成分分位/ok_set/closed_book_ok≤2025-09-09 等）；D2 双轴重考（NO_MAP）；t0 E4 复跑（仍 INSUFFICIENT_SAMPLES）；condition_package 冻结公式消费 |
| ⑤自动化挂点 | 无（回放=一次性批，复跑走 tmp 脚本；报告 §7 复核命令） |
| ⑥缺口债 | **EVAP-03 三受害者之代码侧**：emotion_index_replay.py、test_emotion_index_replay.py、schema source 列 DDL-as-code 更新、GPU 矩阵三件（gpu_emotion_condition_matrix_v1.{csv,meta.yaml}+cells.csv）、history_replay_report_v1.md 全部滞 `.aidrafts/st-emoreplay-20260923/` 死会话 worktree（主区 src/zephyr/alt_data/ 无 replay 件、market_emotion_index.py 无 source 列、docs/_working/emotion_line/ 无该五件）；另 tasks.yaml 14 行情绪竞价槽 WIP 被灭（oddjobs LEDGER.md:31-33，处方①"骨架维持在途"Owner 已批，07 号文 C2#7）；主区悬空引用已实勘：docs/02_enterprise_architecture/02_domain_architecture_docs/34_d_backtest.md:3043 与 config/data/strategy_intake/grid_t0_conditional_v1/t0_condition_matrix_v1.meta.yaml:138 均引"gpu_emotion_condition_matrix_v1/emoreplay 报告"而主区无此件 |

### C · 成分族 C1-C6（考试真源=docs/_working/emotion_line/exam_report_v1.md 卡B+§重考）

| 向 | 内容 |
|---|---|
| ①上游输入 | C1/C2=daban_board_event（09-01→09-22 复通 1,454 行；09-23/24 两日未见=DU-14 附注观察，12 号文 :79）；C3=kline_daily+kline_index；C4=kline_daily(amount/turnover)；C5=margin_trading；C6=news_sentiment_window |
| ②数据原料 | 分位=滚动 250 观测秩分位，<120 观测 insufficient 权重重分配禁硬凑（builder :75-77,199）；替代源：limit_up_down（→09-24 通，4,942 行）可替 C1 的 0.4 家数子项，连板/炸板/晋级率无替代（盘点册 §8.4） |
| ③状态输出 | components JSON 逐成分 name/raw_value/percentile/weight/status/obs/asof/source/note（builder :196-231） |
| ④下游消费 | 考试判档：**C3 KEEP**（RankIC -0.176/t -2.10/n 143 唯一达标）｜C4 NO_SIGNAL（-0.030，降权候选）｜C6 NO_SIGNAL（-0.022，归因 rule 法）｜C5 重考 NO_SIGNAL（-0.031，S4 回补 442 日后 obs 25→142）｜C1/C2 INSUFFICIENT（史 16 日，非退役，预承诺等史重考）；冗余 C1×C3 ρ=0.824 REDUNDANT-warn；卡A W_core 反向观察档（RankIC -0.144、Q1−Q5 +0.59%/日、NW t 1.90，尾部反向支持"节流"消费不支持方向择时） |
| ⑤自动化挂点 | 随 A 双任务在产；重考触发器缺位（daban 史≥120 无自动跑卡机制→施工项 C08） |
| ⑥缺口债 | C1/C2 等史自然生长约 2027-03 满窗；daban 断供复发风险（DU-14 附注 09-23/24 未见）；C4 量能口径二评未排期（14 号文 CNS-07）；G5 深史（2024-09 前）需新外部 API 通道（07 号文 D 节） |

### D · 新闻情绪窗

| 向 | 内容 |
|---|---|
| ①上游输入 | c3_fundamental.news_data 8.25M 行当日到（12 号文 :75，四源+MD5 去重）；写入器 src/zephyr/intelligence/nightly_sentiment_window.py（夜间窗=前日 18:00→当日 08:00，NewsSentimentAnalyzer 规则法默认） |
| ②数据原料 | 三腿：market 腿 185 日在产（2026-02-24→09-23）｜symbol 腿止 2026-08-20（120 日，DU-06）｜news_sentiment_score 打分链停摆 1 年+（止 2025-09-09，7.73M 行，DU-05——"下游加工断、上游活着"） |
| ③状态输出 | c1_market.news_sentiment_window（ReplacingMergeTree scope,symbol,window_type,window_ts 幂等；sentiment_index∈[-1,1]+正/负/中性计数+top_events_json） |
| ④下游消费 | emotion_index C6（builder :123-127 只取 scope='market'）；MOD-PLAN-004 overnight_boundary_reviser 预留 plan004_input 对接字段**未接线**（nightly_sentiment_window.py:5 头注）；个股情绪因子（等 DU-06 修） |
| ⑤自动化挂点 | market 腿在产：12 号文 :73 记"nightly cron 20:08"，模块头记"schedule nightly_sentiment 08:20 日频 scheduler._run_special_schedule 分派"（nightly_sentiment_window.py:5）——两口径并存待核（§3）；09-10 接线治本 known_data_gaps news_sentiment_window_no_scheduler_wiring |
| ⑥缺口债 | DU-05（未登记→已立卡，12 号文补采优先级 #6"修接线即回"）；DU-06（symbol 腿，疑夜间批只算 market 粒度或个股窗零数据静默跳过）；LLM 分支：news_llm_scorer.py 适配器已交付（nlp_inference×OllamaChat，LSG 内置，3 测绿），旗标 data/runtime/nightly_sentiment_llm.enabled 已立（09-23 05:16）——**启闭=Owner 门位，llm 行落库质量与 rule/llm 对照期未核** |

### E · 两融温度（C5 原料）

| 向 | 内容 |
|---|---|
| ①上游输入 | tasks.yaml margin_trading_incremental（akshare stock_margin_detail_sse/szse，交易所 T+1 节奏） |
| ②数据原料 | margin_trading 2,065,857 行 2024-09-02→**09-18**（4,930 标的/日）；S4 深史回补 442 交易日（2024-09→2026-07-17，与 ifind 重叠日逐位一致——exam_report §重考） |
| ③状态输出 | 无独立产出——经 builder C5（20 日变化率分位，as-of 对齐）进 emotion_index |
| ④下游消费 | emotion_index C5；S2 板块杠杆资金/S12 两融温度/cohort_ledger_daily（DU-03 下游行，12 号文 :190） |
| ⑤自动化挂点 | 任务在跑但 0 新日：**09-19 起 4 个交易日断更=DU-03（P1，未登记→已立卡）**；断因未查（疑东财/接口静默 0 行，同 daily_valuation 0 行静默同型病） |
| ⑥缺口债 | DU-03 查因+补跑（12 号文补采优先级 #2"任务在跑只需查断因"）；0 新日静默无告警=哨兵缺口；2024-09 前深史需新外部 API 通道（07 号文 D 节） |

### F · 竞价情绪

| 向 | 内容 |
|---|---|
| ①上游输入 | c1_market.auction_snapshot 272,117 行（2026-06-01→09-24 当日到）+auction_book 3,475,798 行（07-21→09-24）；06-01 前竞价过程数据永久结构性缺口（12 号文 :86-87） |
| ②数据原料 | 10 秒级/3 秒高频层双表皆**通**（盘点册 §8.1 推翻骨架稿"原料未聚合"错判=F6 修复） |
| ③状态输出 | **无**——emotion_index stage='auction' 仅 DDL 预留（market_emotion_index.py:36 注释"v0.2 预留 auction/intraday_vN"）；12 号文 :72 记表中"盘中 pre_open/auction 自 09-01"与 HEAD 仅两任务存在口径张力，待核（§3） |
| ④下游消费 | 候选：竞价强度因子 BM-SEL-23-A-5（14 号文 CNS-11"auction_book 266k/303 万行在库待接线"）；骨架稿 §4 auction stage（T 日 09:25 竞价快照成分） |
| ⑤自动化挂点 | **缺位**——post_auction 调度槽 14 行 WIP 被灭（EVAP-03，oddjobs LEDGER.md:31-33），scheduler 零 post_auction 分支；处方①已批=骨架维持在途、随情绪线复职批正门重立 |
| ⑥缺口债 | G12（v0.2 挂载位）；stage=auction 成分定义未冻结（竞价成交/缺口口径待 v0.2 设计） |

### G · 评级情绪候选

| 向 | 内容 |
|---|---|
| ①上游输入 | c3_fundamental.research_report 146,769 行（2017-01-02→09-18，滞后 4 交易日；akshare 日更） |
| ②数据原料 | rating 列在（买入/增持/中性/减持/卖出，schemas/categories/fundamental/fundamental_research_report.py:60）；**rating_change 空列**（:61，DU-12） |
| ③状态输出 | 无——候选成分未入 emotion_index v0.1.0（骨架 §1 明确零新采集边界） |
| ④下游消费 | 无代码消费；候选用途=机构情绪代理（评级上调/下调净流，缺口单 G13 P3） |
| ⑤自动化挂点 | 数据腿在产（工作日夜批，半通）；成分腿缺位 |
| ⑥缺口债 | DU-12（滞后 4 日+rating_change 空列）前置；S20/G13 候选评估未排期 |

### H · 存量同域簇与内收

| 向 | 内容 |
|---|---|
| ①上游输入 | sentiment_cycle：涨停/连板/晋级率等同源输入（与 C1/C2 同族） |
| ②数据原料 | 四件并存：signal_ashare/sentiment/sentiment_cycle.py（五阶段+compute_sentiment_temperature，8 标准函数）、market_sentiment_analyzer.SentimentPhase（4+1）、youzi_relay_emotion_engine.EmotionPhase、F23_LIMITUP_EMOTION（src/zephyr/alt_data/alt_regime_signals.py，阈值 v1 provisional）；另 F15/F25 连续量两件；盘中环 data/intraday_sentiment_loop.py（MOD-DATA-063 单拍，消费 market_breadth_snapshot） |
| ③状态输出 | 各自为政：三枚举中文值一致（冰点/反核/主升/疯狂/退潮）勿混 import（sentiment_cycle.py 头注自曝）；F23 输出分类阶段 vs emotion_index 连续灰度="档位计 vs 温度计" |
| ④下游消费 | sentiment_cycle 消费面=（待 G07 验证/G08 打板 sleeve/BM-SEL-03-B 软影响接线，其头注 CONSUMERS 行）；F15/F23/F25 经 regime_data_loader 已接线（盘点册 §8.1 #22） |
| ⑤自动化挂点 | F 族随 regime 产线；sentiment_cycle 三消费点未接线 |
| ⑥缺口债 | **LK-02**：裁定#400"并存分层+内核单源化"两硬约束已入册，但两枚举收敛移交治理班未落（缺口单 §6 G9/G10 行）；G9 能力反查索引漏报（capability_lookup 查 sentiment 未命中四件）同案移交 |

### I · 消费面

| 向 | 内容 |
|---|---|
| ①上游输入 | emotion_index 全史（A/B 两块产出，replay 8,596+live） |
| ②数据原料 | close_final 定格态为消费口径（t0_condition_matrix_v1.meta.yaml:29"emotion_thermometer: c1_market.emotion_index（stage=close_final；同键多版取 argMax(ingest_ts)）"） |
| ③状态输出 | sector_preference 第二轴（三档偏好）；T0 条件矩阵 emotion 列（band5 四档有数/冰点 0 日）；闭卷输入包 closed_book_ok 列 |
| ④下游消费 | **D13 缺口在码**：sector_state_aggregator.py:499-508 emotion_index=None→mock 0.5 温和档（14 号文 §四#4 实证）；pipeline 真值消费已接（sector_state_pipeline.py:109）；condition_package.py 灰度五档边界冻结 (0.2,0.4,0.6,0.8]；TDM L0-04 明日情绪预测（config/trading_decision_map.yaml:232-265，8 态先验+相似日+Brier 三零件，组合器 intraday_tomorrow_forecast.py 纯函数核）三消费点未接线=D7；L9-V2 状态变量快照 |
| ⑤自动化挂点 | sector_preference/pipeline 日批在产；L0-04 盘中四时点（10:00/11:00/13:30/14:30）挂点缺位（audit"覆盖未接电"） |
| ⑥缺口债 | D13（mock→实值）；D2 主判 **NO_MAP**（W_map 1,585 日出档：偏好映射对次日板块结构无解释力、指向组次日跑输——情绪轴对板块偏好消费口径无效，emoreplay §6①）；D7（L0-04 未接电）；t0 双门被六段词表轴卡住（emotion_index 连续分位不在 TDM 六段词表内，emoreplay §6②案卷） |

## §3 自审闸三态

| 子块 | 三态 | 余量/放行条件 |
|---|---|---|
| A builder 主链 | **SEALED** | 全文已读+算法对外部标准对表完成（rank 分位合成=外部文册 §2 推荐目标方案，等权起步=CNN 恐贪同款工业实践） |
| B emoreplay 残骸 | **SEALED** | 残骸五件全部实勘定位（.aidrafts worktree 内在案），去向已批（处方①），施工项 C01 可直接执行 |
| C 成分族 | **SEALED** | 六成分全部有 frozen 卡判档+S4 重考实证；处置路径全部预承诺在案 |
| D 新闻情绪窗 | **MINING** | 清单：①`data_source='llm'` 行落库质量与 rule/llm 对照期数据未核（旗标已立）；②夜间 cron 20:08（12 号文 :73）vs 08:20（模块头 :5）两口径未辨析 |
| E 两融温度 | **SEALED** | 六向全填；断因查证属施工（C03）非挖矿 |
| F 竞价情绪 | **MINING** | 清单：①emotion_index 表内 auction stage 行的有无与来历未核（12 号文 :72"pre_open/auction 自 09-01" vs HEAD 双任务+处方①"post_auction 零实现"并存） |
| G 评级情绪候选 | **SEALED** | 候选登记+前置缺口（DU-12）齐 |
| H 存量同域簇 | **MINING** | 清单：①ruling_registry 裁定#400 原文未亲读；②market_sentiment_analyzer/youzi_relay_emotion_engine 两枚举代码体未读（仅经 sentiment_cycle 头注与盘点册转述）；③F23 阈值 v1 provisional 的 OOS 考试状态未核 |
| I 消费面 | **SEALED** | 14 号文族④+代码双证（pipeline 真值/aggregator mock/condition_package 冻结三态全实证） |

**总判：MINING（6 SEALED / 3 MINING / 0 BLOCKED）**。MINING 余量共 6 条（D 块 2+F 块 1+H 块 3），均不阻塞 C01-C03 施工项开工（README"挖干即开工"条款）。

## §4 施工项（L02-C01 起，内收声明随项）

| # | 优先 | 内容 | 内收声明（替代/合并对象） | 依赖 |
|---|---|---|---|---|
| **L02-C01** | **P0** | **emoreplay 残骸复职批**：把 `.aidrafts/st-emoreplay-20260923/` 五类交付走提交正门 re-land——src/zephyr/alt_data/emotion_index_replay.py+tests/alt_data/test_emotion_index_replay.py+market_emotion_index.py 补 source 列 DDL-as-code+GPU 条件矩阵三件与 history_replay_report_v1.md 入 docs/_working/emotion_line/（消除 34_d_backtest.md:3043 与 t0_condition_matrix_v1.meta.yaml:138 两处主区悬空引用）；随批呈 Owner 呈批项 P-2（1991-2018 stub 段去留）/P-5（D-3 接缝是否重算活区间） | 替代任何"重写回放器/重做 GPU 包"新案——残骸即正身，公式冻结 v0.1.0 零改动；不复活蒸发 WIP（处方①已批） | 无 |
| **L02-C02** | **P0** | **DU-03 margin_trading 断供查因+补跑**：09-19 起 4 交易日 0 新日，查 fetch_perf+akshare 接口实弹后增量补跑即回（12 号文补采优先级 #2）；同批登记"0 新日静默"哨兵告警缺口 | 合并 DU-03 卡与 S12/S2/cohort 三处下游降级为一次修复 | 无 |
| **L02-C03** | **P1** | **D13 接线**：sector_state_aggregator.py:499-508 情绪轴改实值（消费 emotion_index close_final），删除 mock 0.5 分支 | 替代对象=该 mock 分支代码本体（净删除） | C01（主区先有 replay 面） |
| **L02-C04** | **P1** | **DU-05+DU-06 新闻双腿重启**：news_sentiment_score 打分链复活（停 1 年+）+夜间批扩 symbol 腿（止 08-20） | 复用 nightly_sentiment_window 单一写入面，禁另起写入器；合并 DU-05/DU-06 两卡为一工单 | 无 |
| **L02-C05** | **P1** | **C6 LLM 对照期核验+切轨判定**：核 data_source='llm' 行落库质量，按外部文册 §1.3 版本冻结纪律定对照期与切换判据；启闭呈 Owner 门位 | 复用 S5 已交付 news_llm_scorer.py 适配器，零新组件 | 无（核验先行） |
| **L02-C06** | **P2** | **竞价情绪成分 v0.2 挂载**：auction_snapshot/auction_book→stage='auction' 成分定义冻结+post_auction 调度槽正门重立（scheduler 补分支+运行验证） | 挂骨架稿 §4 auction 预留位；替代 st-emoreplay 蒸发的 14 行 post_auction WIP（处方①"随复职批"）；消费侧联动 CNS-11 | C01 |
| **L02-C07** | **P2** | **C1/C2 等史自动重考触发器**：daban 史≥120 观测自动跑卡A W_full+卡B C1/C2 重考（预承诺时点约 2027-03）；C4 降权二评同窗 | 承接 14 号文 CNS-07 情绪部分，不另立新账 | daban 持续在产 |
| **L02-C08** | **P2** | **D-1 C2_promotion 恒 1.0 修复立项**：join_use_nulls 语义修 SQL（builder :95-105）=成分口径变更→version v0.1.0→v0.2.0→考试族重开（Owner 门位，07 号文 D 节期限 2027-03 前） | 与 C07 合并为同一次重考事件，禁两次开族 | Owner 立项批 |
| **L02-C09** | **P2** | **LK-02 两枚举收敛跟办+G9 反查索引**：三枚举（sentiment_cycle/market_sentiment_analyzer/youzi_relay）按裁定#400 分层边界收敛+capability_lookup sentiment 族索引重建 | 按裁定#400"并存分层+内核单源化"，移交治理班执行、本班跟办 | 治理班排期 |
| **L02-C10** | **P3** | **评级情绪候选评估**：rating 上调/下调净流成分 v0.2 评估 | 前置 DU-12（rating_change 空列+滞后 4 日）；候选只入评估不动 v0.1.0 契约 | DU-12 修复 |
| **L02-C11** | **P3** | **t0 双门情绪轴新卡**：情绪门数据源改 emotion_index 分位+六段↔分位映射裁定（emoreplay §6② 路径 b，取数面已备） | 替代"六段标签历史持久化工单"与"等材料积累"两路线，三选一交 Owner 定 | Owner 择路 |

**净零声明**：11 项中 4 项为纯修复/接线（C02/C03/C04/C05）、4 项为残骸复职或复用挂载（C01/C06/C08/C11）、2 项承接既有账本（C07←CNS-07、C09←LK-02/G9）、1 项为候选评估（C10）；零全新组件立项。

## §5 标准件（全网搜+仓内已收编）

> 仓内已有 16 条带验证状态的锚点总表=docs/_working/emotion_line/external_methodology_review.md §5+§7（5/5 抽验属实，含 Baker-Wurgler JEP 2007、CNN 七成分等权、AAII、CBOE PCR/VIX、集思录温度计、浦银国际 14 成分、QuantsPlaybook、Huang-Jiang-Tu-Zhou PLS RFS 2015）。本轮全网搜新增/复核如下：

| # | 标准件 | 对本线的用途 | 出处 |
|---|---|---|---|
| 1 | **浦银国际 A 股情绪指数（14 成分）** | 成分集对标：成交量/换手率/RSI/两融余额/陆股通/IPO 募资/再融资/限售解禁/产业资本等——本线 C 系缺口成分（两融占比/解禁/产业资本）的外部先例 | spdbi.com 研报（2024-01-11）；知乎转载全文（zhuanlan.zhihu.com，搜索确认） |
| 2 | **中信建投投资者情绪量化（2025-09）** | 20+ 指标（涨停家数/换手/两融/基金发行/估值）**等权+PLS 双轨并用**、极端情绪预示反转——支撑本线"等权起步+二期 PLS/IC 加权"路线 | finance.sina.com.cn 转载（王程畅，2025-09，搜索确认；仓册 [12] 复核一致） |
| 3 | **BigQuant 情绪指标构建** | 涨跌停因子（price_limit_status）→日度涨停/跌停家数计数的工程化先例，对 C1/C2 与 limit_up_down 替代源 | bigquant.com《情绪指标的构建和使用》（搜索确认） |
| 4 | **东方财富 A 股市场情绪指标梳理** | 价格/量能/估值比对三分类框架，成分族盘点外部对照 | pdf.dfcfw.com（2019，搜索确认） |
| 5 | **LLM 情绪打分大规模对比** | OPT/BERT/FINBERT 三模型 965,375 条金融新闻情绪→交易策略实证：C6 LLM 分支（C05）的模型选型与预期收益基准 | arxiv.org（2024-12，abs/2412.xxxx 族，搜索确认） |
| 6 | **GPT-4o+prompt engineering vs FinBERT** | GPT-4o 经 prompt 工程领先 FinBERT 约 10%（分行业）——C05 对照期应含 prompt 冻结纪律（与仓册 §1.3 告诫互证） | MDPI（Kang et al. 2025，搜索确认） |
| 7 | **混合打分架构** | FinBERT 批量低延迟打分+GPT 类模型疑难句深判+LLM-as-annotator 蒸馏——DU-05 score 链重启（C04）的推荐形态 | LSEG sentiment 白皮书+GitHub 端到端样例（搜索确认，仓库未直读） |
| 8 | **PLS 合成开源实现** | Huang-Jiang-Tu-Zhou RFS 2015 对齐情绪的复用件：netneurolab/pypyls（GitHub，Python PLS；许可证未直读核验）、R pls 包（Mevik & Wehrens，JSS）——二期加权方案备选 | github.com/netneurolab/pypyls；cran.r-project.org pls（搜索确认） |
| 9 | **多源情绪聚合综述** | Liu et al. 2024（Scientific Reports）投资者情绪聚合方法首篇系统综述+Fu et al. 2024（MDPI）新闻+评论多源价格预测——v0.2 多源扩展方法论索引 | nature.com/scientificreports；mdpi.com（2024，搜索确认） |

**标准件结论**（对表）：本线现行算法（rank 分位合成+可用成分等权+250 观测窗+<120 降档）与外部主流实践（CNN 等权、中信建投等权轨、外部文册 §2"rank 分位=推荐目标方案"）一致，**无需返工**；二期备选序=IC 加权（骨架 §3 已登记）→PLS（本轮补强，件 8）→PCA（≥1 年史后再评），维持"考试通过后才启用"前置。

## §6 未决张力登记（如实并列，不下断言）

1. emotion_index 表内 auction 行口径：12 号文 :72 "盘中 pre_open/auction 自 09-01" vs HEAD tasks.yaml 仅双任务（:3452/:3466）+ oddjobs 实勘"post_auction 零实现"——三源并存待 DB 探针核实（§3 F 块 MINING 项）。
2. 夜间批时点：20:08（12 号文 :73）vs 08:20（nightly_sentiment_window.py:5 头注）——或为两调度点并存，待核。
3. LLM 旗标已立（09-23 05:16）vs S5 交付记录"出厂不存在、启闭=Owner 门位"（缺口单 §6 S5 行）——翻转动作发生在何会话无案，核 data_source='llm' 落库行即真相（C05 前置）。
