---
ttl: task_bound
title: L04-S2 子模块挖矿簿 · 成分映射层（板块↔个股归属：sector_constituent / 快照 / 指数腿）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L04
status: MINE 完成（六向封口，CH 实测量已入表；长尾 3 条见 §6 尾）
---

# L04 · S2 成分映射层（板块↔个股归属）

覆盖父簿 SKEL.md 的 **W1** 子块（sector_constituent + index_constituent 指数腿）。

**① 职责一句话**：回答"这只股票在某一天属哪个板块"——个股层一切分数、门槛、榜单的归属底座，也是板块结论下沉到个股的唯一合法 join 键。

**② 现状实测**（CH 只读经 `zephyr.data.ch_reader.query`，FINAL 自动注入；本册实测量标"实测"，其余标"文档基线"）

| 项 | 实测值 | 出处 |
|---|---|---|
| DDL 真源 | `schemas/categories/market/market_sector_constituent.py`（MOD-L04-001，MATURITY=production，AI_AUTONOMY=**human_only**，MODIFY-GUARD=schema-change）；列=`sector_code/sector_name/stock_code/update_date/data_source/fetched_at/valid_from/valid_to/updated_at/ingest_ts`，ENGINE=ReplacingMergeTree(fetched_at)，PARTITION BY toYYYYMM(update_date)，ORDER BY (sector_code, stock_code)，DateTime64(3,'UTC') 合规 | 文件 :1-58 本册 Read |
| 列名口径 | 个股列名是 **`stock_code`**（非 `symbol`）；快照表同 | DDL :37-39 |
| 成分表规模 | **实测**：有效版本（`valid_to IS NULL`）95,124 行 / 595 板块 / 6,179 只个股 / `update_date` 2026-07-22..2026-09-03 | 本册 CH 查询 |
| SCD-2 史深 | **实测**：全表 `uniqExact(valid_from)=4`（2026-07-23..2026-09-03）→ 所谓"时点成分"只有 **4 个快照日**，2026-07 之前的历史成员归属**不可取** | 本册 CH 查询 |
| 板块族分布 | **实测**（valid_to IS NULL，按 code 前 4 位）：8800=11 板块/**仅 17 只个股**、8802=32/5,567、8805=89/5,101、8806=98/5,266、8807=90/5,078、8808=82/5,345、8809=65/4,417 → 880 族 467 只；8810-8814 合计 **128 个 881 行业板**（个股 799-1,754/族） | 本册 CH 查询 |
| 8803/8804 | **实测 0 行**——但 `tasks.yaml:2430` 注记：该族"不在 sector_constituent；名单 SSoT=`sector_code_bridge.TDX_INDUSTRY_BOARDS`"（132 条行业板，2026-08-26 T6 §七-7 只接了分钟 K 线腿） | 本册 CH + tasks.yaml 实测 |
| 板块层总盘子对照 | **实测**：`sector_state` 426,985 行 / **729 板块** / 2022-09-01..2026-09-24；`sector_code_name_map` 729 行/729 码；`sector_list` 5,217 行 | 本册 CH 查询 |
| 成分快照表 | `sector_constituent_snapshot`（列=`snapshot_date/sector_code/sector_name/stock_code/data_source/ingest_ts`，**无 SCD 列、无 update_date**）：**实测** 475,620 行 / 595 板块 / 6,179 只 / `snapshot_date` 2026-09-14..2026-09-25 但 **uniqExact(snapshot_date)=5**（10 天窗口仅 5 个日→断日） | 本册 CH 查询 + `system.columns` |
| 采集触发面（在产） | `sector_constituent_refresh`：source=tqcenter，`schedule: monthly_static`，`incremental: false`（全量重建，描述"约 84,450 条映射"），实现 `tqcenter_provider._fetch_sector_constituent`（:511，`get_sector_list`+`get_stock_list_in_sector`） | `src/zephyr/data/config/tasks.yaml:2388-2399`；provider :511/:565/:578 |
| 派生依赖面 | `kline_sector_intraday`/`kline_sector_880` 轮询池、`sector_snapshot_incremental`、`sector_ranking_engine`、`sector_intraday_aggregator` 均以 sector_constituent 反查板块宇宙（`tdx_provider:296,311,320,336,353`、`tqcenter_provider:412,431`、`sector_ranking_engine:51`） | 本册 grep |
| 指数腿 | `index_constituent` 列=`trade_date/index_code/symbol/symbol_canonical/weight/action/exchange/data_source/valid_from/valid_to/...`；**实测** 5 个指数：000300.SH 83,098 行/949 码/2005-04-29..09-23、000852.SH 162,000/2,839/2014-10-31..、000905.SH 127,500/1,800/2007-01-31..、000906.SH 199,198/2,013/2007-01-31..、**000985.SH 仅自 2026-08-14**（102,436 行/5,126 码）；**000010.SH（上证180）零行 = 实测确认**（GROUP BY 结果内不存在该码） | 本册 CH 查询 |
| 指数腿触发面（在产） | 三任务并行写同一表：`index_constituent_refresh`（baostock，monthly_static，**仅沪深300**，akshare fallback）、`index_member_premarket`（akshare，pre_market，DS-084：300/500/1000/中证全指+权重，日快照）、`index_member_postclose`（akshare，daily_capital） | tasks.yaml:1101-1114,1560-1568,1616-1624 |
| 消费面（个股层） | `data/sector_state_pipeline.py:55`、`signal_ashare/mainline_candidates.py:105`、`sector/sector_breadth.py`、`sector_divergence.py`、`plan_engine/llm_premarket_analysis.py:970`（文档基线，本册另实测新增 `data/sector_report_builder.py:4,23,30,39,42` 与 `data/sector_intraday_aggregator.py:26`、`data/sector_ranking_engine.py:51` 三个消费件） | 本册 grep 实测 |

**③ 六向台账**

| 向 | 发现（内部反查 ＋ 全网搜索） |
|---|---|
| ①上游该喂什么 | 内部：上游只有"板块名单×成分名单"两列，缺 **归属生效区间的双侧对账**——`update_date`（分区/更新日）与 `valid_from`（SCD 生效日）语义并存且月度全量重建会把二者一起刷新，历史回放取不到"当日真成分"；`sector_name` 在 880 族"全为代码回显/空"（`sector_code_bridge.py:29,32` 排雷注记），即板块名不可作 join 兜底。外部：成分归属业界标准做法是**按日/按调仓事件维护成员区间**（含 weight/action 与退市标记），A 股公开口径普遍强调不可"拿今天的成分股回测过去"——东方财富财富号《做指数增强回测……"拿今天的成分股回测过去"》（2026-09-07 https://emcreative.eastmoney.com/app_fortune/article/index.html?artCode=20260907095051527961090 ）与同花顺量化《用今天的沪深300成分股回测十年前，为什么可能高估结果》（2026-06-09 https://quant.10jqka.com.cn/view/article/JVUR6XTVOW1580260HRHWZEJ09 ）两独立来源互证 → 现役"4 个 valid_from 版本"=该坑的本仓实例 |
| ②下游该喂谁 | 内部：除 SKEL 已列 4 件，实测另 3 件（`sector_report_builder`、`sector_intraday_aggregator`、`sector_ranking_engine`）；**下游最深的一腿是反向的**：`tdx_provider._resolve_sector_symbols`（:296-:353）与 `tqcenter_provider:412` 用本表**当板块宇宙源**（"取全量板块代码 880+881 全族 594 只"）→ 成分表同时是"板块清单真源"，与 `sector_code_bridge.TDX_INDUSTRY_BOARDS` 常量、`sector_state`（729 码）三处并存=**板块宇宙三真源**（新缺口 G3）；一旦本表停更，采集侧板块宇宙同步塌缩。外部：已查无（查法：以"constituent table used as board universe registry"检索，未见于业界表述——业界把清单与成员分表，本仓属实现耦合，无外部方法论可引） |
| ③算法/机制 | 内部：映射层无算法（纯 SCD-2 + 月度全量），复杂度全在"何时该重建"；`incremental: false` 的注释先例（:2386 附近"增量 5 天回看窗内一次漏跑=永久缺口，2025 全年 312 日断档即漏跑永久化实证，故提到 30 天窗"）说明团队已用"宽窗幂等"治漏跑，但成分表选的是"月度全量"，无漏跑自愈声明。外部：成员区间建模=SCD-2/双时态为通用范式；A 股指数成分变更由 `index_member_premarket/postclose` 的 `action` 列已捕获（实测列在）→ 可派生"调入调出事件表"（本仓 `tasks.yaml:2189-2195` 已有 `index_rebalance_event` 类派生任务，源=index_constituent 月度快照差分）——**该派生事件的下游消费=零**（见 §④） |
| ④后端代码缺什么 | 内部：(a) 无"当日成分"读取函数（PIT 视图缺失）——消费侧各自写 SQL（`sector_report_builder` 自述"SCD 版本取 argMax(trade_date) 最新"），即每个消费者自己发明 PIT 取法；(b) 132 条 8803/8804 行业板**完全没有成分腿数据**（个股→该族归属不可得），分钟 K 线接了、归属没接；(c) 881 族在成分表 128 vs 板块层 729 → 727/728 验收线若按"板块层"口径已过，若按"成分可 join"口径**差 134 板块**，验收文档未区分两口径（DU-01/02 口径歧义）；(d) 上证180 指数腿零行未立"改靶 or 回补"裁定。外部：已查无（查法：以"open source A-share sector constituent SCD python"检索未见维护活跃可复用件；zvt 已在 SKEL §4 入图，沿用） |
| ⑤前端怎么呈现（只登记） | 内部：`sector_report_builder` 生成的板块盘后报告器与 Dashboard 板块榜依赖本表（其 DEPENDENCIES 头注 :4 自列 `sector_constituent（只读）`）；成分表本身无人工审阅界面，**没有任何"归属覆盖率/断更"看板**→人工只能靠跑脚本发现（终局要自动化，见 §⑤裁定）。外部：已查无（查法：映射层呈现无外部惯例争议） |
| ⑥数据字段有没有 | 内部逐个核对：`sector_code/stock_code/valid_from/valid_to` ✓在；`weight`（指数腿有 Decimal(8,4)，实测在）✓但**板块腿无权重列**（等权聚合是 `sector_state_pipeline` 现状口径，无流通市值加权可选）✗；`action`（调入调出）✓仅指数腿；板块名 880 族不可用 ✗；快照表 5/10 日断日 ✗。质量画像（闸 4"字段在≠数据可得"）：成分主表**止 2026-09-03 且月度全量**（本册查询日 09-26 已 23 日未刷新）、SCD 版本仅 4 个、8800 族 11 板块仅 17 只个股（退化/占位嫌疑）。外部：板块权重口径业界=流通市值加权为主（自由流通市值调整），本仓板块腿无该字段 |

**④ 缺口清单**（沿用 L04-Cxx／LK-xx／Dxx／DU-xx／IBT-xx；新缺口续编并注"册内未见"）

| 编号 | 内容 | 状态 |
|---|---|---|
| IBT-A02（既有） | 000010.SH 零行——本册实测确认，且实测显示三个写入任务的 symbols 口径均不含上证180（baostock 腿只 300，akshare 腿只 300/500/1000/全指）→ **不是漏采，是靶单未含** | 沿用（改判性质：从"回补"转"改靶裁定"） |
| DU-01/02（既有） | 881 行业族补采 v5（469→≥727） | 本册补证：**板块层已达 729，成分腿仅 595（881 族仅 128）**→ 验收线须二选一明写口径，否则同名不同物 |
| known_data_gaps `sector_constituent_8803_8804_missing`（既有，open） | 8803/8804 零行 | 本册补证：tasks.yaml:2430 明示"该族不在 sector_constituent"→ 该 gap 条目**方向错位**（既成事实的设计而非事故），应改登为"行业板归属腿未建" |
| **L04-S2-G1** | PIT 成分读函数缺失：无"取 T 日成分"的库级门面，各消费者自写 argMax/latest 取法（≥3 处口径）——**册内未见** | 新登 |
| **L04-S2-G2** | SCD-2 史深仅 4 个 `valid_from` 版本（2026-07 起），2020-03..2026-06 的板块归属在库内不可取 → 个股层任何跨期回测都用"今日成分回测过去"（幸存者/归属漂移偏差双中）——**册内未见** | 新登 |
| **L04-S2-G3** | 板块宇宙三真源并存（`sector_constituent` 反查 / `sector_code_bridge.TDX_INDUSTRY_BOARDS` 常量 / `sector_state`+`sector_code_name_map` 729）——**册内未见** | 新登 |
| **L04-S2-G4** | `sector_constituent_snapshot` 断日（10 天窗口仅 5 日有数）+ 与主表新鲜度劈叉（09-03 vs 09-25）——SKEL W1⑥ 已记"劈叉未立卡"，本册补**实测数字**并把"断日"从推测升为实测 | 加厚既有 |
| **L04-S2-G5** | 板块腿无权重字段（指数腿有 `weight`），板块收益/资金聚合只能等权 → 与业界流通市值加权口径不符——**册内未见** | 新登 |

**⑤ 自审闸三态裁定**

| 项 | 裁定 | 理由（量尺=终局全貌） |
|---|---|---|
| L04-S2-G1 PIT 门面 | **施工（本环节最高优先）** | 一处门面消灭"每个消费者自己发明 PIT 取法"的人工口径核对；与 L04-C01 载体接线同批（载体回放任一历史日需该门面）；成本低、无新表 |
| L04-S2-G2 归属史深 | **挂起排期** | 解锁条件=上游采集面确立"每次全量重建先落 valid_to 闭区间"的写入纪律（属数据线 DU 判读，L04 只登记义务），且历史成分有公开可回溯源；终局必须要（无人盘回测必靠 PIT 归属），禁以"现状只有 4 版"判不值得 |
| L04-S2-G3 三真源 | **施工（内收申报）** | 真源方向明确=板块清单唯一真源归板块层表（sector_state/name_map，729），成分表只承担归属；bridge 常量降级为"该族无成分板的白名单"；净零=不改行为、只定引用方向 |
| L04-S2-G4 断日 | **移交数据线（挂起）** | 本环节是消费方，DU 判读归 12 号文班；本册交付实测量与断日证据即尽责 |
| L04-S2-G5 权重 | **挂起排期** | 解锁条件=成分源本身提供板块权重（当前 tqcenter 接口不提供）；先问终局要不要（要，板块层市值加权是标配）再问现在建不建；禁以"等权也能跑"封矿 |
| IBT-A02 | **挂起排期** | 解锁条件=Owner 裁定"补采上证180"或"靶单改 000985 中证全指"（后者实测已有 5,126 码史，覆盖更宽）；属 high 门位的数据靶单变更，不自行拍 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | signal/noise 与归因 |
|---|---|---|---|
| R1 | 内部：DDL 列/引擎 + 消费面 grep + tasks.yaml 采集任务 | signal | 列名 `stock_code` 非 `symbol`；月度全量；反查为板块宇宙源 |
| R2 | 内部：CH 实测（成分表规模/族分布/8803-8804/快照/指数腿） | signal（最富一轮） | 595 vs 729、4 个 valid_from 版本、快照仅 5 日、000010.SH 零行确认、000985 浅史 |
| R3 | 内部：CH 实测 `kline_sector` / `kline_sector_880` / `sector_constituent_sw_history` | **受阻**（查询空串/异常，未换第二 reader 复核即中止，按闸 4 不记"无数据"） | 归因=预算限制 + 大表扫描慢；`sector_constituent_sw_history` 表名存在但列/行未测→转长尾 T1（该表若为申万历史成分，可直接解 G2 的一半） |
| R4 | 外部：成分 PIT/幸存者偏差（1 轮） | signal | 两独立来源（东方财富 2026-09-07 / 同花顺量化 2026-06-09）；noise 归因=cofool 理财客多页为同一文案的 SEO 转载，按闸 2 不计独立源，已剔 |
| R5 | 外部：开源成分件替代 | 已查无（查法见 §③④行） | 记档 |

**长尾（本册调研未尽，明确列出）**
- T1 `c1_market.sector_constituent_sw_history` 列结构与起止（需 DESCRIBE 成功 + 行数），这是 G2 的现成候选解。
- T2 `kline_sector_881` 表不存在（实测 TCP 报 Unknown table，提示"Maybe you meant kline_sector_880"）→ 881 族 K 线落在哪张表待查（疑在 `kline_sector`），影响"板块收益合成腿"判读。
- T3 881 族 128 vs 260（17 号文"行业族 260 全量"）差额 132 是否与 8803/8804 的 132 条同一集合——两个"132"并存，需板块线核对，禁本册臆断。

**本册封矿判据自评**：六向已填（含两处"已查无+查法"、一处"受阻"），T1-T3 未清空 → **状态=MINING（长尾在册）**。
