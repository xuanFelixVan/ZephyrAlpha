---
ttl: task_bound
title: L04-S5 子模块挖矿簿 · 可交易性硬过滤层（市值流动性门槛 ⊕ ST/涨跌停/停牌/次新排除）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L04
status: MINE 完成（六向封口；W4+W5 合并成册，理由见 §①；本册含 4 处对父簿基线的实测改判）
---

# L04 · S5 可交易性硬过滤层（W4 ⊕ W5）

覆盖父簿 SKEL.md 的 **W4（市值流动性过滤）** 与 **W5（ST/涨跌停/停牌过滤）**。
**合并理由（MECE 交代）**：两块的判据同属"能不能买"这一层（W4=买进去有没有意义，W5=买不买得到），且共用同一批表（daily_valuation/stock_daily_basic/stk_limit/limit_up_down）与同一个消费出口（漏斗 L3-01 + 预检 L3-10）；拆开会让⑥数据字段向重复三遍。

**① 职责一句话**：在打分之前先把"不可成交/成交了也无意义"的标的绝对排除并留下排除原因，让候选池成员天生可执行。

**② 现状实测**（CH 只读 `ch_reader.query`，本册实测量标"实测"）

| 项 | 实测值 | 出处 |
|---|---|---|
| 分级过滤器码件 | `src/zephyr/signal_ashare/screening/tiered_screening_filter.py`（MOD-SIG-046）：**三参数已实装为配置默认值**——`min_avg_daily_amount: float = 5_000_000.0`（:138）、`new_stock_min_list_days: int = 30`（:137）、`dealer_abandon_prob_max: float = 0.95`（:139），且逐条参与判定（:190-202 attrgetter 绑定）；`limit_pct_for(board, is_st)`（:72-102）主板±10/科创创业±20/北交±30 齐备，:80 注记"主板 ST 现与主板同幅度 ±10%，参数保留以便演化" | 本册 grep/Read |
| 父簿基线改判① | SKEL W5② 记"BM-SEL-16 **三参数全 proposed 待实现**" → 实测**参数已在代码里落地**，proposed/implemented 之别是 battle_map 侧状态标注，非代码缺件 → L04-C04 的工作量从"实现"降为"状态回填 + 淘汰率实测报告" | 本册实测 |
| fail-open 默认值（新发现） | 同一 dataclass 的**输入侧**默认值是"永不触发排除"的中性值：`avg_daily_amount: float = 1e12`（:154）、`dealer_abandon_prob: float = 0.0`（:155）、`is_st: bool = False`（:152）→ 上游不喂数即**静默放行**（与 S4 linker fail-open 同族病灶） | 本册 grep |
| 过滤器消费面 | 自身头注 :5 自述：`coarse_screening_funnel`（"经 2026-09-05 AI-08 审计实证未接线——接线待排期"）+ `screening_funnel_report`（消费实证）；全仓 grep `tiered_screening_filter` 命中仅 screening 包内两件 + `selection_funnel_skeleton.py` 注记 → **生产消费面=报告器，无日循环** | 本册 grep |
| 可交易性预检码件 | `src/zephyr/signal_ashare/tradability_preflight.py`（MOD-SIG-151）五查函数齐：`_check_suspended`（:120，读 `snap.suspended`）、`_check_limit_up`（:126，含"意图价触板"与 `DATA_MISSING` 分支）、`_check_permission`（:147）、`_check_lot_cash`（:163）、`_cage_suggestion`（:185，CLAMPED 时给夹边建议价）；总入口 `preflight_tradability`（:208）symbol 非法 fail-closed | 本册 Read |
| 预检消费面复核 | 全仓 grep `preflight`（排除同名他件）→ **`preflight_tradability` 调用方仍=0**（命中的是 `ai_layer/comparator/executor.run_preflight`、`backtest/core/preflight_checker.run_backtest_preflight`、`scheduler ddl_preflight` 三件不同名同词，非本件）→ SKEL W5④"调用方=0"复核成立（本册二次确认） | 本册 grep |
| 预检输入落点 | 快照 `InstrumentSnapshot` 的口径锚=`instrument_master`（SKEL W5②，MOD-DATA-069；其 DDL 注释含 `is_suspended UInt8`/`in_delisting_period`/`delist_date`/ST 标志及变更日期/上市日期，:24/:52/:55/:56）；**实测：CH `system.tables` 内无 instrument/master 命名表**（查询仅返回一个名为 `instrumentation` 的 0 行对象）→ 五查的静态快照在 CH 侧无载体，其取数路径本册未追到（长尾 T1） | 本册 CH + grep |
| 涨跌停真源 | `c1_market.stk_limit` **实测 9,209,835 行 / 2015-01-05..2026-09-24**，列含 `pre_close/limit_up/limit_down/limit_pct/st_flag/board` + SCD(valid_from/valid_to) → **深史齐备，ST 标记可历史回溯**；近 6 日 ST 行数 787 / 22,213（≈3.5%） | 本册 CH 实测 |
| 涨跌停榜单 | `c1_market.limit_up_down` **实测 4,942 行 / 2026-07-20..2026-09-24**（≈45 交易日）→ DU-14 浅史基线成立（本册更新行数口径：FINAL 后 4,942） | 本册 CH 实测 |
| 市值/流动性原料 | `stock_daily_basic` **实测 7,079,611 行 / 2021-01-04..2026-09-24**，列 `turnover_rate/float_share/circ_mv/total_mv`；近 3 日覆盖 **5,554/5,556/5,557 只/日、`circ_mv` 为 0/NaN 者 0 行** → **D21 的"流通股本"腿在 stock_daily_basic 里实测有值且无 NaN**（与 SKEL W2⑥"D21 缺口挂起"并列事实：至少 `float_share/circ_mv` 不缺，缺的是获利盘/单峰密集度）；`stock_indicator` 11,685,777 行（2015 起）**同时含 `total_mv/circ_mv`** → 市值双真源并存（新缺口 G3） | 本册 CH 实测 |
| **DU-11 恶化实测** | `daily_valuation` 全表 208,288 行 / 2026-08-03..2026-09-24（**起点与 limit_up_down 同日**）；逐日：**09-15 5,562 / 09-16 5,569 / 09-17 5,570 / 09-18 5,570 / 09-21 5,002 / 09-22 5,003 / 09-23 2,504 / 09-24 1,500** → 部分写入病**仍在逐日恶化**（非仅两日事故），且父簿记"09-24=1,000 行"本册实测 1,500（其间补过一次） | 本册 CH 实测（改判②：严重度升级）；**旁证**：本册独立实测的逐日数与邻卷 `../du11_daily_valuation_partial_write_root_cause.md`（LANE-BUILD 2026-09-25 案卷，写侧根因=截断式部分写入 + 同日重跑重叠，单标的 ≈12 秒 ⇒ 5,560 只需 18.5 小时 > 任务日窗口）**逐日完全吻合**，两车道双测互证；病根归该卷，本册只登记"消费面受害=日成交>2 亿门槛" |
| 停牌腿 | `c1_market.suspend` **实测 0 行**（列结构齐：`suspend_date/resume_date/reason` + SCD），但 `tasks.yaml` 侧**已登记三个写入任务**：`suspend_status_premarket`（:1546）、`suspend_status_postclose`（:1602）、`suspend_status_derive_weekend`（:1671，capability 均 `suspend_status`）→ **改判③：SKEL W5①"suspend 表 0 行=akshare 无批量源"不完整——任务在册、产出为零**，病性从"缺源"转"缺产出/静默失败" | 本册 CH + tasks.yaml 实测 |
| 次新腿 | `c1_market.ipo_schedule` **实测 0 行**（列 `ipo_date/listing_date/issue_price/...`）→ **改判④：CNS-10"次新过滤接线 ipo_schedule"接的是空表**；可用替代实测在库：`stock_basic`（9,036,265 行，2015-01-05..2026-09-23）含 `list_date`，`instrument_master` 注记亦有上市日期口径 | 本册 CH 实测 |

**③ 六向台账**

| 向 | 发现（内部反查 ＋ 全网搜索） |
|---|---|
| ①上游该喂什么 | 内部：该喂的三类原料实测**两类在、两类空**——在=stk_limit（920 万行深史，含 st_flag/board）、stock_daily_basic（circ_mv/float_share 满覆盖）；空=suspend（0 行，三任务在册）、ipo_schedule（0 行）；另缺"账户上下文"（`AccountContext` 权限/一手资金查的输入，属执行层回灌，本环节无源）。外部：涨跌停约束下**可交易信息本身是信号**——《Do Daily Price Limits Stabilize Stock Markets?》CUHK 中国研究中心（2019-07-18 https://cbk.bschool.cuhk.edu.hk/do-daily-price-limits-stabilize-the-markets/ ）与《An A-Share Board Chasing Strategy Based on the JoinQuant Platform》（2025-01-21 https://www.researchgate.net/publication/388163925 ）两独立来源支持"封板状态须进池而非仅进拦截"→ 现设计把"涨停封死"只作**排除**，未把"一字/秒板/封单厚度"作**分层输入**（归 L3-07-1 打板 sleeve，本册只登记事实）。**A 股适配闸**：两源均以 A 股涨跌停制度为本体（非美股迁移），适配无障碍 |
| ②下游该喂谁 | 内部：输出（可交易布尔 + 排除原因分类）设计喂三处=L3-01 Universe 剔除、L3-10 预检（喂 L4 执行兜底）、`stock_candidate_pool` 池成员；**实测三处均未吃到**（预检调用方 0；池快照 `tier_slot`/过滤结论无列——S3 实测 DDL 16 列里没有"被哪条硬过滤拦下"的留痕列）→ 新缺口 G1：**硬过滤的淘汰原因不落库，漏斗不可归因**。外部：已查无（查法：排除原因的下游呈现无外部方法论分歧，业界=日志/reject reason code，与本仓 `BlockedReason` 枚举同构） |
| ③算法/机制业界学界 | 内部：现役三件套=绝对额门槛（500 万日均成交额）、次新 30 天、弃庄概率 0.95 + 涨跌停幅度表（board/ST 感知）+ 封死判定从 close/prev_close 推导（:27，"从原始 close/prev_close 推导涨跌停封死状态，经骨架"）而非直用 stk_limit。外部（换手/成交额约束建模，两独立源）：《Deep Learning Enhanced Multi-Day Turnover Quantitative Trading Strategy》arXiv（2025-06-02 https://arxiv.org/html/2506.06356v1 ）以成交额/换手为组合可容纳规模的显式约束；CUHK 价格限制研究（上一行）指出价格限制引发流动性迁移（magnet 效应）→ 二者合读支持本册判语：**门槛应相对化（ADV 分位/占全市场成交比）而非绝对元值**；现役 2 亿/500 万两把绝对尺随市场扩容与通胀单调漂移，2020 年的 2 亿≠2026 年的 2 亿（该推论为**本仓内生推理 + 外部两源支撑其前提**，未冒充"业界定论"） |
| ④后端代码缺什么 | 内部缺五件——(a) 预检零接线（LK-04 家族）；(b) **涨跌停幅度表三处并存无对表**：`tiered_screening_filter.limit_pct_for`（:72）、`tradability_preflight._limit_ratio`（:109）、`AkshareIngestProvider._limit_pct_of`（被 :90 注记为对齐对象）→ 任一改动即口径漂移，属 RULE-SSOT 违例候选（新缺口 G2）；(c) fail-open 默认值无告警（1e12/0.0 静默放行，G4）；(d) 停牌/次新两腿无数据即"永不排除"，与 BM-SEL-16"绝对排除"设计相反，**当前实现事实上无法执行停牌排除**（G5）；(e) 淘汰原因无落库位（G1）。外部：已查无（查法：可交易性规则的可复用件已在 SKEL §4 登记 rqalpha/vectorbt，本册判其"撮合层内置"与本仓"独立纯函数核"架构不同位，不换轨，只作对表参照） |
| ⑤前端怎么呈现（只登记） | 内部：`screening/screening_funnel_report.py` 即"人工看漏斗淘汰率"的面（它现在就是 tiered filter 的唯一消费者）→ 报告器是**人工审阅件**，终局要机查：淘汰率异常应由哨兵判，不靠人读报告（登记为 G6 的人工环节）；预检结果无任何展示位。外部：已查无（查法：拒绝原因呈现=标准 reason-code 列表，无外部争议） |
| ⑥数据字段有没有 | 内部逐字段：`limit_up/limit_down/limit_pct/st_flag/board` ✓（stk_limit 深史 2015 起）；`circ_mv/float_share/turnover_rate` ✓（2021 起，近 3 日 0 缺失）；`amount`（成交额）✓在 daily_valuation 但**该表行数 09-24 只剩 1,500/5,557=27% → "日成交>2 亿"这第三关正在日毁**；`suspend_date/resume_date` ✗（0 行）；`list_date` ✓在 stock_basic（但 CNS-10 指定的 ipo_schedule ✗0 行）；`reason`（停牌原因）✗。**质量画像（闸 4）**：字段在但断供的三项=suspend/ipo_schedule/daily_valuation 覆盖；字段在且可用的两项=stk_limit/stock_daily_basic——**结论：本层不是"没数据"，是"数据在错的表/对的表没产出"三类混合，处置动作完全不同**（对应 G5/CNS-10 改判/L04-C03） |

**④ 缺口清单**（沿用 L04-Cxx／DU-xx／CNS-xx；新缺口续编并注"册内未见"）

| 编号 | 内容 | 状态 |
|---|---|---|
| L04-C03（既有 DU-11） | daily_valuation 部分写入重跑 | 沿用；**本册升级**：实测逐日阶梯衰减（5,570→5,002→2,504→1,500），已非"两日事故"，排期紧迫度应重评 |
| L04-C04（既有） | BM-SEL-16 三参数收口 | 沿用；本册改判工作量（参数已实装，欠的是 battle_map 状态回填 + 7000→1200 淘汰率实测 + fail-open 治理） |
| CNS-10（既有） | 次新过滤接 ipo_schedule | **本册改判**：ipo_schedule 实测 0 行 → 接它=接空；改接 `stock_basic.list_date`（实测有值）或先补采 ipo_schedule 并说明"展示面也在吃空表" |
| DU-14（既有） | limit_up_down 浅史（实测 2026-07-20 起） | 沿用 |
| DU-01/02（既有） | 板块成分验收线 | 归 S2 册（不重复） |
| **L04-S5-G1** | 硬过滤淘汰原因零落库（池快照无 reject 腿）→ 漏斗不可归因、参数无法自动校准——**册内未见** | 新登 |
| **L04-S5-G2** | 涨跌停幅度表三处实现并存无对表单测（MOD-SIG-046 / MOD-SIG-151 / AkshareIngestProvider）——**册内未见** | 新登 |
| **L04-S5-G3** | 市值双真源（`stock_daily_basic.circ_mv` 与 `stock_indicator.circ_mv` 同字段异表，且 daily_valuation 亦含估值列）→ 选哪张为准无 RULE-SSOT 判定痕——**册内未见** | 新登 |
| **L04-S5-G4** | 过滤器输入侧 fail-open 默认值（1e12/0.0/False）无缺数留痕、无告警——**册内未见**（与 S4-G3 同族，两处独立成因） | 新登 |
| **L04-S5-G5** | 停牌批量真源零产出（三任务在册 / 表 0 行）→ BM-SEL-16"绝对排除停牌"与预检第一查**当前不可执行**——**册内未见（本册改判性质，非新事）** | 新登（移交数据线判读失败史） |
| **L04-S5-G6** | 绝对额门槛未随市场漂移相对化（2 亿/500 万为 2025 年前后定值，无分位口径）——**册内未见** | 新登 |

**⑤ 自审闸三态裁定**

| 项 | 裁定 | 理由（量尺=终局全貌） |
|---|---|---|
| G1 淘汰原因落库 | **施工（建议编 L04-C10）** | 这是"漏斗参数自动校准"的前置：没有 reject 流，任何阈值调整都只能人工试；且落库位应扩到既有 `stock_candidate_pool`（加 `reject_stage`/`reject_reason`）或池变更流表（S3-G5），二者同批设计以免二次改表——净零声明：不新建第三条池表 |
| G2 三处幅度表 | **施工（P0，安全向）** | 同一制度参数三写=终局必炸（ST 幅度 2025 年制度变动过一次即需三处同改）；收口=单一函数 + 两处 import + 一条对表单测，成本极低、消灭的是"人肉记住三处都改" |
| G3 市值双真源 | **挂起排期（等 SSOT 判定）** | 真源方向属 RULE-SSOT 判定，需 Owner/治理侧一句话（规则数据 vs 架构数据不改，但"哪张表是流通市值真源"要钉）；解锁条件=判定入 `trae_062_ssot_classification`；终局要单一真源，禁以"两处都一样"为由维持并存 |
| G4 fail-open 治理 | **施工（随 L04-C04）** | 缺数即放行=静默错误，与宪法"fail-visible"精神相悖；改法=输入缺省时填 `None` + 判定分支显式记"未评"（复用候选池 `score_components` 的"逐成分 status"口径），不新增字段语义 |
| G5 停牌零产出 | **移交数据线（挂起）** | 本环节交付"任务在册×表空"的矛盾实证；解锁条件=数据线查三任务失败史（是否 capability 无实现/源站改版）；禁在 L04 侧自造停牌判定（如用 limit_up_down 缺失反推停牌=近似假信号） |
| G6 门槛相对化 | **挂起排期** | 终局要（自动校准阈值必须相对化），但**改判据=高门位动作**（宪法 §5：策略阈值变更属 Owner），且需 G1 的 reject 流先落地才能回测新口径；两条件任一不满足即禁自行改数 |
| 预检接线（L04-C02 一部分） | **沿用他车道** | 接线施工已在 LANE-BUILD 范围（`tradability_preflight` 调用方 0→≥1 是其验收口径之一），本册只登记复核结论，不重立 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | signal/noise 与归因 |
|---|---|---|---|
| R1 | 内部：八表列结构与起止实测（valuation/daily_basic/indicator/suspend/limit_up_down/stk_limit/stock_basic/ipo_schedule） | signal（改判 4 处） | suspend 0 行但三任务在册；ipo_schedule 0 行；circ_mv 无 NaN；DU-11 阶梯恶化逐日数 |
| R2 | 内部：过滤器参数实装状态 + 消费面 grep | signal | 参数已落地（proposed 标注失真）；唯一消费者=报告器；输入侧 fail-open |
| R3 | 内部：预检五查函数体 + 调用方 + instrument_master 载体 | signal（部分） | 调用方仍 0；CH 无 instrument/master 表 → 快照取数路径未追到（长尾 T1） |
| R4 | 外部：涨跌停制度与可交易性、换手约束（1 轮） | signal 3 / noise 4 | noise 归因=①百度百科词条（百科非方法论，闸 1 剔）②BOCHK 基金页（营销，无方法论）③docin/聚合站论文转载（不可溯）④"enterprise digital transformation→liquidity"（主题漂移）；有效=CIFER/CUHK 价格限制（2019）、arXiv 2506.06356（2025）、ResearchGate JoinQuant 打板（2025）；Gank Interview 私募面经（2026-01）为工程博客单源，标**待验证**未入图 |
| R5 | 外部：开源可交易性规则件 | 已查无（查法见 §④行；SKEL §4 的 rqalpha 已登记，沿用不重开） | 记档 |

**长尾（本册调研未尽，明确列出）**
- T1 `instrument_master.py`（MOD-DATA-069）实际存储载体与 `is_suspended` 的写入方——预检输入的唯一口径锚，本册未落到表级。
- T2 `battle_map_05_stock_selection.md:1394-1436` BM-SEL-16 六件套原文与本册实测参数逐条对表（"7000→1200 只"的淘汰率是否已可实测）。
- T3 微盘/风格漂移风险面：17 号文市值五分位验收轴与现役 30 亿下限是否互相抵消（未做分位实测，属考试卡级动作）。

**本册封矿判据自评**：六向已填（含两处"已查无+查法"），T1-T3 未清空 → **状态=MINING（长尾在册）**。
