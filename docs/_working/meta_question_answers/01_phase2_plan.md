---
ttl: task_bound
completes_when: A 类回填/B 类载体施工完成后随总包归档
title: Phase 2 计划——96 条 insufficient 三分诊 + 数据/建设需求清单（Owner 令②）
owner: ZephyrAlpha-Owner
session: st-metaq-20260923
date: 2026-09-24
---

# Phase 2 三分诊计划

> 三分诊总况：**A 类缺数据源=28｜B 类载体未建=37｜C 类设计内/立法债=31**（合计 96；含审计改判：PQ-0143 A→C、PQ-0065 fail no_alpha→infra）。判定基于四轮复核后的 results 证据；边界注记 31 条。

## 《数据施工需求清单》（A 类·缺数据源）

| q_id | 数据源 | 历史窗 | 回填量级 | 复考前置 |
|------|--------|--------|----------|----------|
| PQ-0013 | sector_fund_flow（板块资金净流入正源）历史回补 + 板块→个股成分映射带 valid_from 历史回补（sector_constituent_snapshot/concept_board_constituent，现仅存 2026 切点后快照） | 2021-01-04~2025-09-09（闭卷窗；kline_sector_880 切点前 322,995 行/462 板块已在库但 sector_name 100% 空置，须用 sector_code 口径） | sector_fund_flow 板块日频≈53 万行（462 板块×约1150 交易日，现仅 2026-09 起 3529 行）+成分映射历史版本（全量快照≈95,124 行/快照日或月度版本回填） | 两前置齐备后按原口径真算合成强度分位（新高家数占比×板块资金净流入）对板块指数 10 日收益的预测 IC |
| PQ-0016 | c3_fundamental.news_data 存量情绪分回填（sentiment_score/sentiment_label 列已在表）+ c1_market.news_sentiment_window 历史段生成 | 2010-01-02~2025-09-09（切点前存量 7,887,387 条新闻，score≠0 为 0 条） | 789 万条新闻情绪分批量回填 + 按发布时戳生成日度情感窗口历史段（切点后 268,322 条仅 50 条被打分，回填前须先确认打分管线可批处理全量） | 回填后按发布时戳 PIT 重放日度情感分位→次日全A中位数收益 HAC 回归 |
| PQ-0019 | auction_book/auction_snapshot 集合竞价委托队列历史（L2 行情授权供应商回溯渠道）；tick_depth_5 同步回补 | 近一年闭卷窗≈2024-09~2025-09-09（现最早样本 2026-06-01/2026-07-21 均在切点后） | 全A 竞价队列快照回补，亿行量级（≈5400 只×244 交易日×多档委托队列） | 回补后按题面重考 AUC>0.55 且 DeLong p<0.05（tick_data 逐笔成交 34.8 亿行不可替代 |
| PQ-0025 | tushare DS-TUSHARE money_flow（渠道在册已运营；缺口工单 gaps/A06_MONEYFLOW_BACKFILL_workbook.md） | 2021-01-04~2025-09-09 | 全A 主力净流入/超大单/成交额日频≈600 万行（≈5400 只×1150 交易日） | 回补后按本题 exam_plan 原判据（事件研究 t>2）重考 |
| PQ-0026 | tushare DS-TUSHARE money_flow（同 PQ-0025，同一 A06 缺口工单） | 2021-01-04~2025-09-09 | 全A 主力净流入/超大单/成交额日频≈600 万行，回填须保留供应商口径版本标记 | 回补后按本题 exam_plan 原判据重考 Chow 断点检验 |
| PQ-0034 | Hyperliquid 清算流水切点前历史（hl_liquidation_raw 回填；渠道=Hyperliquid 归档 API/第三方清算数据商） | ≥2024-09~2025-09-09（费率侧 hl_funding_history 切点前 2023-05-12~2025-09-08 已有 262.4 万行） | perp 清算流水事件级回填，主要币对百万行量级（现全表仅 5 行心跳，2026-09-18 起） | 回填后按'费率分位×清算量分位'合成公式重考 logit ΔAUC>0.02；若回填不可得则改'费率分位单变量'属换卷须 |
| PQ-0035 | stock_hot_rank（雪球热度）+ alt_stock_comment（千股千评）+ news_sentiment_window（快讯情感）切点前历史回填，或改用切点前可得的替代关注度源 | 12 个月滚动窗→≥2024-09~2025-09-09（三表现有样本均 2026-02/08/09 起） | 关注度日频全A≈130 万行/源 + 快讯情感窗口历史段（PIT 按抓取/发布时戳） | 回填后重算 12 个月滚动 Spearman ρ≥0.6 |
| PQ-0036 | c1_market.money_flow（tushare DS-TUSHARE 回补，同 A06 工单）+ 快讯情绪（存量 news_data 情绪分回填→news_sentiment_window 历史段） | 滚动 250 日互相关→≥2024-09~2025-09-09（资金流建议 2021-01-04 起） | 资金流全A日频≈600 万行 + 789 万条新闻情绪分（同 PQ-0016 回填） | 回填后重算滚动 250 日领先滞后互相关 + block bootstrap 显著性 |
| PQ-0038 | alt_stock_comment 千股千评历史快照（东方财富千股千评页回溯；composite_score/org_participation） | 周频 IC 序列→≥52 周，2024-09~2025-09-09（现仅 2026-09-11 起 12 天） | 全A 日频千股千评快照≈130 万行 | 回填后按全A 周频 IC>0.02 且 t>2（Newey-West）重考；'评级家数'须先确认对应字段（org_par |
| PQ-0040 | tushare DS-TUSHARE money_flow（个股级）+ 板块级 sector_fund_flow 聚合回补 | IC 序列窗≥2024-03~2025-09-09（建议 2021-01-04 起） | 个股资金流≈600 万行 + 板块日频≈53 万行 | 回填后构造板块资金净流入 CR5 集中度因子对板块 5 日收益 IC 序列重考；若仅新窗积累则须以新切点命题 |
| PQ-0042 | QWeather（DS-QWEATHER，exam_plan 已引用）40 城历史逐日观测+气象警报/阈值超限事件回溯落库（weather_data 现仅 2026-08-04 起 10,033 行） | 事件研究窗≥2024-09~2025-09-09（警报事件建议 2012 起对齐 alt 源覆盖） | 40 城逐日观测≈1.5 万行/年 + 警报事件流，合计十万行量级（PIT 对齐警报发布时点，预报/实测分字段） | 回填后按 40 城温度距平/降水超阈事件对公用事业/农业板块重考事件研究；备选降格深圳单城（alt_sz_weather |
| PQ-0043 | 切点前回测重放回填：在产 risk_budget_allocator（MOD-PA-022，inverse_var/risk_parity/sharpe_weight 三模式）+ regime_snapshot_history（切点前 2019-04-01~2025-09-09 共 3132 行状态输入）+ 行情重放生成运行账 | 2019-04-01~2025-09-09（regime 快照覆盖段） | 重放生成 alloc_budget_daily/alloc_shrinkage_daily/decision_daily/sim_trade_log 历史日频账≈1500 交易日×各表（现四表切点前全 0 行，全量仅 2026-09 起 16/8/69/66 行） | 回填或 GPU 新窗积累≥1 年后重算样本外回撤改善与超额；不以切点后 16 行作判据（PIT 纪律） |
| PQ-0045 | tushare DS-TUSHARE money_flow（A06 缺口工单同源；动量腿 kline_sector_880 切点前 322,995 行已在库） | 回测窗≥2019-01-01~2025-09-09（或全史） | 全A 日频资金流 2019 起≈800-900 万行 | 回填后按双信号（板块动量+资金流确认）原口径重考；备选单腿动量降口径属重立项 |
| PQ-0075 | stock_concept（ths_export，单时点 2026-09-14）+ concept_board/concept_board_constituent（akshare，单时点 2026-09-22）月度快照序列（valid_from 版本化字段已具备，缺时间维度样本） | ≥3 个月度快照（前向 2026-10 起每月落一版，或供应商历史月度成分回填） | 两源 750+ 板块×月度≈数千行/月×3+；历史回填 36 个月约十万行内 | 快照序列到位后重测两源重合率月度趋势斜率>0 且显著；另核实 akshare_ths 板块源身份（东财 vs 同花顺） |
| PQ-0080 | 国家统计局 2018 年投入产出表（153 部门，io_official 渠道落库 ig_io_edge year=2018，现 year 非空仅 {2020:16,859}） | 静态横截面表（2018 版全表，与 2020 版 16,859 行同量级） | 官网/统计年鉴获取 2018 版全表落库 + 部门口径映射（2017 国民经济行业分类↔2020 版 138/153 部门差异对齐） | 落库对齐后按 max|a2018-a2020|/|a2020| 或矩阵范数相对差重估外推误差上界 |
| PQ-0083 | alt_stock_comment 千股千评历史（composite_score，回填同 PQ-0038） | 条件频率窗≥2024-09~2025-09-09（现仅 2026-09-11 起） | 全A 日频千股千评快照≈130 万行 | 回填后须命题方指明情绪回落对象序列（建议 emotion_index）及其>90 分位定义，再考条件频率>60% |
| PQ-0084 | money_flow（tushare DS-TUSHARE 回补，A06 工单同源）+ market_fund_flow_daily + news_sentiment_window（存量 news_data 情绪分回填） | 20 日滚动状态月度一致率→≥2024-09~2025-09-09 | 资金流≈600 万行 + 789 万条新闻情绪分（同 PQ-0036） | 回填后重算主力净流入占成交额比与情绪高低状态月度一致率≥70%；备选以新切点重命题 |
| PQ-0085 | 880/申万板块成分带 valid_from 历史映射回补（sector_constituent/industry_class/sector_meta/stock_profile_ths/concept_board_constituent 五表现均仅 2026 快照） | 新高家数占比需≥一年闭卷窗 2024-09~2025-09-09 | 全A-板块映射历史版本化回填：全量快照≈95,124 行/快照日，月度版本 36 个月约数万至十万行 | 回填后按板块聚合新高家数占比重考条件概率>60%；备选命题方改以板块指数自身新高重定义因子属换卷 |
| PQ-0089 | 同 PQ-0043：在产 inverse_var allocator（MOD-PA-022）+ vol_target_allocator（MOD-BT-082）+ regime_snapshot_history 切点前 3132 行重放回填 | 2019-04-01~2025-09-09 | 重放生成 alloc_budget_daily/decision_daily/sim_trade_log 历史日频账≈1500 交易日（现切点前全 0 行） | 回填或 GPU 新窗积累≥1 年后重算样本外年化超额与回撤对比 |
| PQ-0090 | 切点前归因/决策账重放回填（decision_daily/sim_trade_log/sim_attribution_daily/sim_daily_report）+ 资金流腿 tushare money_flow 回补（A06 同源） | 2019-04-01~2025-09-09（regime 覆盖段，须含'超配 5%'决策实例） | 四表重放≈1500 交易日×各表 + 资金流≈600 万行 | 资金流回填与决策账回填两者齐备后重算 IR 贡献>0.1 |
| PQ-0125 | c1_market.money_flow（DS-TUSHARE 渠道 tushare money_flow 接口，渠道在册已运营） | 2021-01-04~2025-09-09（PIT 闭卷窗）全A 日频 | 全A 主力净流入/超大单/成交额日频，约 5000 股×约 1137 交易日（kline_daily 实测）≈560 万行量级（现表仅 2026-06 起 533,575 行可参照）；缺口工单 gaps/A06_MONEYFLOW_BACKFILL_workbook.md | 回补后按本题 exam_plan 原判据（1 日前瞻 IC，Newey-West t）重考 |
| PQ-0126 | c1_market.money_flow（DS-TUSHARE 渠道回补，同 PQ-0125） | 2021-01-04~2025-09-09（PIT 闭卷窗）全A 日频 | 同 PQ-0125：全A 资金流日频约 560 万行量级，工单 gaps/A06_MONEYFLOW_BACKFILL_workbook.md | 回补后按 exam_plan 原判据（5 日前瞻 IC）重考 |
| PQ-0127 | c1_market.money_flow（DS-TUSHARE 渠道回补，同 PQ-0125） | 2021-01-04~2025-09-09（PIT 闭卷窗）全A 日频 | 同 PQ-0125：全A 资金流日频约 560 万行量级，工单 gaps/A06_MONEYFLOW_BACKFILL_workbook.md | 回补后按 exam_plan 原判据（20 日前瞻 IC）重考 |
| PQ-0163 | c1_market.money_flow（DS-TUSHARE 渠道回补，同 PQ-0125） | 2021-01-04~2025-09-09 净流入极端日事件窗 | 同 A06 工单回补（约 560 万行量级全A 资金流日频）；判据三要素（事件定义/超额口径/显著性检验）已齐备可代码化 | 回补后按事件研究原判据重放（同批 U6 先例 PQ-0139/0181 同法） |
| PQ-0167 | alt_stock_comment 日批自积管线（2026-09-11 起在产；ingest_ts 时点字段在、日批落库、无回填写路径） | 前向自积跨切点（预计 2026-09 窗口成熟） | 不可回补——快照时点入库执行记录无历史渠道；非回填缺口，等自积（现状 9 个日批 5196~5199 行/批平稳、未见回填痕迹） | 自积序列跨切点成熟后执行月度 30 条快照时点存证抽样复考（违规=快照时点缺失/序列回填） |
| PQ-0181 | c3_fundamental.news_data 存量（切点前 7,887,387 条，2010~2025-09-09 全文在库）经情绪打分管线回填 → news_sentiment_window 历史段 | 2010~2025-09-09（存量新闻逐条回填情绪分） | 对存量 news_data 全量回填 sentiment_score 并生成 news_sentiment_window 历史段（约 789 万条重算；管线通路已由兄弟问 PQ-0015 密度事件研究实跑验证） | 回填完成 + U6 注册文本补写显式阈值（如 t>2）与评估窗口后重放即可执行 |
| PQ-0197 | weather_data 日更管线（2026-08-04 起在产；forecast_type 区分 forecast 8673 行/now 实况 1360 行，分类型存证机制已建） | 前向自积跨切点（同一 forecast_date 多版预报值序列积累） | 不可回补——时点预报记录无历史渠道；等自积非回填 | 自积跨切点后按月度 30 条抽样，并核同一 (location, forecast_date) 多版预报的版次存证情况后 |
| PQ-0209 | 问答库（answer 500 行 2026-08-25 起）+ 原文快照落 G 盘冷库链路（在产：snapshot_path 非空 500/500=100%，抽检 5 文件全部实存） | 前向自积跨切点（月度批样本） | 不可回补——问答内容与冷库快照为增量新内容；等自积非回填 | 问答自积跨切点后执行月度 30 条抽样，核 snapshot_path 非空率与冷库文件存续率（现状 100%/100% |

**A 类归并视图**（同源合并，供排产）：

1. **tushare money_flow 历史回补**（PQ-0025/0026/0125/0126/0127/0163 等 A06 族，工单=WO-011）：DS-TUSHARE 在册，回补 2021-01-04~2025-09-09 全A 日频主力净流入/超大单，量级约 560-600 万行。
2. **国家统计局 IO 表回补**（PQ-0080）：2018 版 153 部门投入产出表落库+口径映射。
3. **前向自积族（等新数据，非回填）**（PQ-0143/0167/0197/0209 等）：管线 2026-07~09 投产，跨切点自然积累后按原判据月度复考，无施工。
4. **可回溯性存疑族**（PQ-0019/0034/0035/0038/0085/0013，ambiguous）：竞价/清算/千股千评/成分归属历史——先做源侧可回溯性取证（S 级探针），可回溯转回填工单，不可回溯转 C。注意口径张力：PQ-0085/0013 立场=『成分历史可回填（申万行业存量史）』vs PQ-0116/0117/0118 立场=『官方成分调整改写历史不可回补』——两立场并陈待 Owner 对成分替代口径统一立法（接受申万替代口径则 0116-0118 翻 A）。

## 《建设需求清单》（B 类·载体未建）

| q_id | 要建载体 | 建设要点 |
|------|----------|----------|
| PQ-0001 | 入库闸审计双轨账（meta_question_audit.jsonl）+ intake_reject 拒绝码留痕机制 + W4 源线谱登记 | ①建 JSONL 双轨落账与 PG audit 表同构双写；②入库闸注册链路写 intake_reject/intake_rate_limited/dedup_hit 事件码及非空 evidence（现 283 条 re |
| PQ-0041 | news→实体→概念映射管线（related_symbol 实体链接）+ 概念指数日线管线 + 互动易历史回填 | ①news_data 回填 related_symbol（现切点前 788.7 万行 related_symbol 100% 空置）或以概念成员公司名做标题/正文匹配归并键（口径与误归并控制须 Owner 认可）；②概念 |
| PQ-0044 | strategy_screen 逐候选判据留痕字段 + 切点前准入账回填 | ①表增 IC>0.02/t>2/扣成本为正三判据逐候选执行结果字段（现仅 is_sharpe/deflated_sharpe 等考尺字段，判据一致率账未逐字段留痕）；②历史积木批次重放回填切点前准入账（现 1340 行全 |
| PQ-0049 | '单因子组合权重上限15%'约束常量落地 + 积木库组合构成与收益账 + 特质波动口径登记 | ①allocation_config.py 落 0.15 因子权重上限常量（现 pf_alloc/position 内 0.15 命中均为异义常量，最接近为 DEFAULT_MAX_SINGLE_SLEEVE=0.25  |
| PQ-0050 | 源线 PIT 风险升级事件账 + 决策假设暂停动作账（现 PG 74 表中无事件发生类载体，domain_events 仅契约定义表） | ①建事件账（event_id/事件时戳/风险等级/受影响假设清单）与暂停动作账（动作时戳/类型/关联假设 ID，现 hypothesis_precheck 58 行无 pause/suspend 语义）；②静态源线谱册（ |
| PQ-0051 | 考试循环机制（meta_question 状态机推进 + meta_question_exam_result 落账） | ①实现考试循环 runner：registered→in_exam→answered 状态流转并写 exam_result（现 283 问全 registered、exam_result 0 行）；②启动后首批问题进入  |
| PQ-0052 | GPU 周五窗口 IBT 修卷任务账与调度机制（现 src/scripts 4753 个 .py 零实现，audit 23 值枚举无任务类事件） | ①实现周五窗口 IBT 修卷任务调度并落任务账（exam_result + audit 任务类事件）；②连续运行≥4 个周五窗口后复考完成率。 |
| PQ-0053 | 滑点模型成交输出管线 + 月度校准账（两者代码全仓零实现；实盘回执侧 tick_data 切点前 34.8 亿行已在库） | ①实现滑点模型并输出模拟成交（对比 tick_data bid/ask 实盘回执），生成切点前（≤2025-09-09）模型成交样本≥20 交易日（现 sim_trade_log 66 行全在 2026-07-17 后、 |
| PQ-0054 | writeback 回填管线与 API（writeback(q_id, exam_result) 唯一合法入口，设计真源 13_exam_backfill_loop_design.md 在而代码未建） | ①按设计真源实现 writeback API 并落 exam_writeback 审计事件；②打通 answered→新鲜窗到期→复考→回填对账链路；一个完整月窗后复考到期复考执行率。 |
| PQ-0055 | 考试循环（产生含 data_window jsonb 的 meta_question_exam_result 记录，表结构已在、记录 0 行） | ①考试循环 runner 按 exam_plan 执行并写 exam_result（含 data_window）；②机检'样本外份额≥1/3 且窗口与生成时戳无重叠'，记录非零后复考通过率。 |
| PQ-0056 | writeback 回填管线（落 exam_writeback 审计事件，含考试完成与回填两时戳；what 枚举已有该值但 849 条事件中 0 条） | ①writeback API 落账首批 exam_writeback 事件（两时戳齐备）；②积累样本后计算落账时延 P99 复考。 |
| PQ-0057 | 复考机制（reexam 状态流转 + exam_result.outcome='reexam' 记录 + exam_arbitrate 仲裁事件，三者现均为 0） | ①复考 runner 产出 reexam 记录与三取二仲裁事件落账；②产生首批 reexam 记录后按季抽样 30 条复考执行率。 |
| PQ-0060 | 状态机拦截器（LEGAL_TRANSITIONS 注册 + 流转事件纳入审计落账，含 illegal_transition 事件类型） | ①注册合法状态边表并实现流转拦截（现拦截代码全仓零实现）；②audit what 枚举扩 illegal_transition 且状态流转事件落账（现 849 条仅 register/update/degraded_ch |
| PQ-0061 | 乐观锁冲突留痕机制（冲突事件类型 + version 字段 + 重放结果关联） | ①audit 表增 VersionConflict/conflict 事件类型与 version 字段（现 meta_question 有 version 列但 audit 无、枚举无冲突类型）；②冲突后重读重写留痕并关 |
| PQ-0063 | IO 部门码↔CH 行情板块（880/申万）显式映射表 + kline_sector_880 sector_name 回填 + 大宗冲击源映射 | ①建 io_sector_code↔board_code 映射表（IO 官方 147/153 部门现与任何行情板块码零映射，880 板块 sector_name 100% 空置）；②接线 kline_futures 主力 |
| PQ-0066 | 假边人工标注集载体 + 消歧桥批量接入管线 | ①建假边标注表（fact_id/is_false_edge/标注人/时戳）抽检标注写入可查表（现库中不存在）；②ig_entity_code_map 批量接入 ig_fact 实体（公司名/产品名→master_id，现 |
| PQ-0076 | news 实体链接管线（related_symbol 回填）或概念成员公司名归并键 | ①news_data 回填 related_symbol（切点前 788.7 万行 related_symbol distinct 仅 1 值=空串）或以成员公司名做标题/正文匹配归并键（口径与误归并控制须 Owner  |
| PQ-0077 | concept_ingest 装载拒绝日志落表（rejected_concept+规则命中原因）+ 同花顺源 TSV 归档 | ①装载器 MARKET_TAG 过滤分支写 rejected 记录落表（现静默 continue 零留痕）；②归档 Owner 提供的源 TSV 入仓；③重放全量过滤生成候选全集，按新日志抽检 500 条评误杀率；④'原 |
| PQ-0079 | ig_company_edge.confidence 列（58,207 行现无该字段，27 列实证） | ①加 confidence 列并按 source 打分回填（top5_customer 销量占比归一 53,236 行/专利协同数归一 1,718/websearch 证据强度 178）；②或 Owner 裁定以 wei |
| PQ-0086 | 互动易历史回填 + news→概念实体热度聚合管线（同 PQ-0041） | ①互动易历史问答回填（irm_interactive_qa 2026-06 起切点前 0 行）；②实体热度管线建成（news_sentiment_window 2026-02 起切点前 0 行）；③命题方给出概念热度合成 |
| PQ-0093 | node_verdict 证伪回传时戳对载体（refuted 实例 + decision 修正引用 ID） | ①node_verdict 增加 refuted 实例与 decision 修正引用 ID + 双时戳（verdict_at 仅记裁决时刻，缺次日生效时戳）；②两账（node_verdict/decision_daily |
| PQ-0094 | pf_alloc 单板块≤30% 约束实现 + 违例注入测试 | ①allocation_orchestrator.py 比照现有 SINGLE_NAME_CAP_LAYERS 层叠 cap 模式（单票硬限 5% 较题面 10% 更严、另有 SYMBOL_AGGREGATE_CAP）增 |
| PQ-0095 | meta_question 模板族标识字段落表（tpl/template_id，现 25 列实证不存在）或 title/provenance 前缀族口径约定登记 | ①meta_question 增加 tpl/template_id 列，或注册 title/provenance 前缀族口径约定；②回填存量 283 问族归属后按族分组比对阈值漂移（exam_plan criterion |
| PQ-0096 | 考试循环 + 考试记录取数/决策双时戳字段 | ①考试循环 runner 落 exam_result 含取数时戳与决策时戳两字段（现 exam_result 0 行无时戳可比对）；②运行后每周抽 20 条抽样比对统计 PIT 违例数（0 记录≠违例=0）。 |
| PQ-0097 | GPU 周五窗口任务账（三件：IBT 修卷/焊成本校准/新鲜窗重考；exam_result 0 行、audit 无任务类事件、调度代码零实现） | ①建周五窗口任务调度与任务账（exam_result + audit 任务类事件）；②连续运行 4 个周五窗口后复考整体完成率；内含 PQ-0052/0053 各自前置。 |
| PQ-0098 | meta_question 治理三载体：exam_plan 结构化功效字段（样本量/效应量）+ 考试循环运行产 exam_result + meta_question_audit CHECK 枚举增补'降阈值'事件值 | ①exam_plan 由 method/criterion/threshold 自由文本扩为含样本量/效应量的结构化对象；②考试循环落地运行使 IC 类考试产生 exam_result 行（现 0 行）；③audit 枚 |
| PQ-0103 | 回写鉴权拦截器（claimed_by==调用会话校验）+ meta_question_audit 枚举增 claim_mismatch 值 + 越权尝试/拒绝结果落账 | ①按 13_exam_backfill_loop_design.md §33 实现回写鉴权拦截代码（全仓 4753 个 .py 现零实现）；②audit 表 CHECK 枚举（23 值）增补 claim_mismatch |
| PQ-0104 | 组合空间预注册载体三件套：space_hash 预注册空间台账 + 批 manifest + N_eff 估计账（PG/CH 新表） | ①按 11_template_generator_design.md 设计稿建 space_hash 台账与批 manifest、N_eff 估计账（PG 现无 %space%/%manifest%/%combin%/% |
| PQ-0105 | E1C 三轨落账载体：hypothesis_precheck/strategy_screen 增 track（gplearn/智能体/MCTS）标识字段，并在统一 space_hash+统一考尺下按批落账 | ①候选/过考记录增三轨标识并将 birth_channel 编码（B/C/C2/D/I）映射规范到三轨口径；②在同一预注册积木库与统一考尺下运行产出账；③积累批次后构造 2×3 产出率列联表与卡方齐性检验复考。 |
| PQ-0106 | 合并闸运行账：逐批相关判定留痕表（逐对相关矩阵/cluster/merge 决策）+ 高相关对占比冗余度账 | ①strategy_correlation_gate.py(MOD-PA-004) 口径对齐题面 |秩相关|>0.7（现代码为 Pearson 0.85/0.90+尾部 0.70，Spearman 未实现）；②合并判定逐 |
| PQ-0107 | E1C 三轨统一考尺配置快照载体：结构化考尺对象（IC>0.02/t>2/扣费多空年化>3%/样本外份额≥1/3）+ 分轨标识，考试前冻结落表/落盘 | ①exam_plan 由自由文本扩为结构化四指标考尺并带分轨字段；②考试前冻结配置快照留痕；③考试运行后即可机械比对一致执行率与口径漂移复考。 |
| PQ-0108 | 新鲜窗重考队列载体：考试循环运行产 answered 状态 + 重考到期/逾期记录落账（月度滚动 20 日窗） | ①落地考试循环使 exam_result 产生记录、问题状态转 answered（现 283 全 registered）；②建重考到期/逾期记录账（现零落账）；③经历一个完整月窗后复考逾期率（现分母为零）。 |
| PQ-0109 | space_hash 台账（登记/扩容/封存流水表，含 seal 封存动作字段——现设计稿亦未含） | ①载体设计补齐封存（seal）动作字段；②建空间台账与扩容/封存流水（PG 无 %space%/%seal%/%expand% 表，registry_event 0 行）；③积累 ≥1 个扩容批次（扩容申请与封存登记一一 |
| PQ-0139 | 模拟成交 vs 实盘回执配对比对载体：execution_report 按单落账积累 + sim_trade_log↔execution_report 配对机制 + 滑点差 bps 显著性判据 | ①实盘成交回执按单落库并覆盖 ≥1 个样本段（现全表仅 1 行 execution_start=2026-09-18）；②建信号→模拟成交→实盘回执→增量比较配对管线（现无配对机制，sim_trade_log 仅 66  |
| PQ-0161 | money_flow 口径版本存证载体：口径版本标记字段或版本表（caliber_version/pub_ts 类）+ 入库链路版本事件落账 | ①money_flow 等口径类表增版本标记字段/版本表（现 DESCRIBE 无 version 字段、全库无版本表）；②入库链路对口径切换落版本事件；③版本切换事件积累后按 U4 抽样审计复考（回补数据不产生历史版本 |
| PQ-0185 | macro_data 增 pub_ts/vintage 存证字段（发布快照入库）+ FRED_ 线入库链路按发布时点写快照 | ①schema（现仅 report_date/indicator_name/indicator_value/unit/frequency/data_source/ingest_ts）补发布时戳与 vintage 字段；② |
| PQ-0191 | macro_data 增发布时戳（pub_ts/release_ts）存证字段 + EIA_ 线按发布时戳 PIT 落账 | ①与 PQ-0185 同一机制缺口宜合并施工：schema 补发布时戳字段；②EIA 周度值按发布时点存证（现切点前 2935 行为回补终值，值冲突组=0 仅证回补幂等不构成发布时戳存证）；③自积后月度 30 条抽样复审 |

**B 类归并视图**（载体簇合并排产）：

1. **考试循环机制簇**（PQ-0051/0054/0055/0056/0057/0096/0098/0103 等）：writeback API+新鲜窗复考调度+三取二仲裁+功效估计器——真源设计=infra_mining/13_exam_backfill_loop_design.md，代码零实现，本班已用『Owner 任务令 SQL 直写』临时通道完成首轮回填（exam_result 285 行）。
2. **E1C 组合空间簇**（PQ-0104~0109）：space_hash 预注册台账+批 manifest+N_eff 估计账，PG 零命中表，建表后积累 ≥1 批次复考。
3. **宏数发布快照簇**（PQ-0185/0191 等）：macro_data 补 pub_ts/vintage 字段+入库链改快照存证，跨切点自积。
4. **入库闸留痕簇**（PQ-0001 等）：JSONL 双轨账+intake_reject 拒绝码留痕（与 PQ-0062/0102 fail 工单 WO-002 同一载体）。

## C 类案由登记（设计内/立法债）

| q_id | 案由 | Owner 门位 |
|------|------|------------|
| PQ-0143 | 成分快照存证管线 2026-09-14 投产（全表仅 09-14/15 两日 95,124 行/日）历史不可回补（同 PQ-0014 管线案由，审计改判 A→C） | 无（前向自积即达复考条件） |

| PQ-0014 | 概念成分按日存证管线 2026-07~2026-09 才建成，闭卷窗内存证对象真空且快照历史不可回补（回补即失真）——是存证机制时点性缺席的设计现状，非可回填的数据源缺口 | 无（复考=管线前向积累满考试窗（建议≥12 连续月）后以新窗同口径复考；现状 2026-09-14/15 两日逐日快照已 |
| PQ-0030 | 清算账本捕获管线 2026-09-18 才投产且快照历史不可回补，闭卷窗内永久断档（SL-A15 U4 已登记'断档即永久缺口'）——无源可回填，无解 | 无（复考=以切点后新积累清算样本重立新题（新切点），或等待可回溯的替代清算数据源落库——后者属命题方决策） |
| PQ-0032 | 数据在库充足（stock_indicator 切点前 1029.8 万行），唯一根因是 exam_plan 未固化分位预热口径——最忠实 trailing 250 日窗满实现 t=-0.44/-1.2 | 命题方/Owner 在 exam_plan 固化分位预热口径（trailing 窗满 vs min_periods 宽松 |
| PQ-0116 | 1 日前瞻 IC 需切点前板块→个股 PIT 成分映射：成分归属被官方调整改写历史（U4 已登记），存证管线 2026-07 后才投产，切点前历史不可回补（index_constituent 切点前仅 | 无 |
| PQ-0117 | 同 PQ-0116（5 日前瞻口径）：切点前板块→个股 PIT 成分映射不可回补，闭卷窗信号永无法构造，属设计内缺口 | 无 |
| PQ-0118 | 同 PQ-0116（20 日前瞻口径）：切点前板块→个股 PIT 成分映射不可回补，闭卷窗信号永无法构造，属设计内缺口 | 无 |
| PQ-0169 | 判据口径须立法：'得分变化分组收益差'的分组数/显著性阈值/信号分档口径均未登记（'无领先性'无数值定义），且信号序列需前向自积 ≥120 交易日不可回补——口径立法是硬前置 | Owner 裁定并登记分组数、显著性阈值与信号分档口径（退役判据立法；参考 DS-IFIND deprecated 留痕 |
| PQ-0193 | 判据口径须立法：核心回归子'库存意外项'=实际-预期的预期基线源未登记（calendar_event 无任何 EIA/库存事件 0 行、consensus_daily 系 A 股分析师盈利预测口径与  | Owner 裁定'意外项'口径：登记共识预期源（如 EIA 报告周度预期调查）或裁定统计性意外定义并登记阈值；vinta |
| PQ-0199 | 判据口径须立法+数据不可回补：'天气冲击日'极端阈值、'无异常收益'显著性/估计窗、温度距平所需气候基线序列（PQ-0194）三处登记债；天气信号切点前 0 行（表起点 2026-08-04）不可回补 | Owner 登记极端事件阈值口径、气候基线源与板块收益代理（公用事业/农业指数或成分篮子）及显著性判据 |
| PQ-0211 | 判据口径须立法+数据不可回补：题材关键词清单、事件窗 N、'无事件窗效应'显著性/超额收益基准均未登记；问答事件切点前 0 行（500 行全为 2026-09-18 单批装载）不可回补 | Owner 登记题材关键词清单与 N（事件窗长度）、超额收益基准（市场/行业调整）及显著性口径 |
| PQ-0227 | SL-B01 卫星影像线 U4 PIT 控制执行审计：B 档'外有可采未落库'——管线未建、DS 册无 active 条目、入库链路不存在，审计对象存在性=False 属源线谱§4/§6 施工边界设计 | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |
| PQ-0228 | SL-B01 卫星影像线 U5 消费方挂接核验：消费挂接记录（层宪章/问题表 line_ref/data_sources 入表）系 W6/W7 施工件，B 档未落库未挂线，源线谱/层宪章行级交叉比对对 | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |
| PQ-0233 | SL-B02 美国官方天气/海洋线 U4 PIT 控制执行审计：B 档'外有可采未落库'——管线未建、DS 册无 active 条目、入库链路不存在，审计对象存在性=False 属源线谱§4/§6 施 | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |
| PQ-0234 | SL-B02 美国官方天气/海洋线 U5 消费方挂接核验：消费挂接记录（层宪章/问题表 line_ref/data_sources 入表）系 W6/W7 施工件，B 档未落库未挂线，源线谱/层宪章行级 | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |
| PQ-0239 | SL-B03 招聘 JD 线 U4 PIT 控制执行审计：B 档'外有可采未落库'——管线未建、DS 册无 active 条目、入库链路不存在，审计对象存在性=False 属源线谱§4/§6 施工边界 | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |
| PQ-0240 | SL-B03 招聘 JD 线 U5 消费方挂接核验：消费挂接记录（层宪章/问题表 line_ref/data_sources 入表）系 W6/W7 施工件，B 档未落库未挂线，源线谱/层宪章行级交叉比 | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |
| PQ-0245 | SL-B04 电商价格线 U4 PIT 控制执行审计：B 档'外有可采未落库'——管线未建、DS 册无 active 条目、入库链路不存在，审计对象存在性=False 属源线谱§4/§6 施工边界设计 | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |
| PQ-0246 | SL-B04 电商价格线 U5 消费方挂接核验：消费挂接记录（层宪章/问题表 line_ref/data_sources 入表）系 W6/W7 施工件，B 档未落库未挂线，源线谱/层宪章行级交叉比对对 | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |
| PQ-0251 | SL-B05 招投标线 U4 PIT 控制执行审计：B 档'外有可采未落库'——管线未建、DS 册无 active 条目、入库链路不存在，审计对象存在性=False 属源线谱§4/§6 施工边界设计现 | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |
| PQ-0252 | SL-B05 招投标线 U5 消费方挂接核验：消费挂接记录（层宪章/问题表 line_ref/data_sources 入表）系 W6/W7 施工件，B 档未落库未挂线，源线谱/层宪章行级交叉比对对象 | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |
| PQ-0257 | SL-B06 社媒舆情 X/Reddit 线 U4 PIT 控制执行审计：B 档'外有可采未落库'——管线未建、DS 册无 active 条目、入库链路不存在，审计对象存在性=False 属源线谱§4 | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |
| PQ-0258 | SL-B06 社媒舆情 X/Reddit 线 U5 消费方挂接核验：消费挂接记录（层宪章/问题表 line_ref/data_sources 入表）系 W6/W7 施工件，B 档未落库未挂线，源线谱/ | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |
| PQ-0263 | SL-B07 雪球/股吧散户情绪线 U4 PIT 控制执行审计：B 档'外有可采未落库'——管线未建、DS 册无 active 条目、入库链路不存在，审计对象存在性=False 属源线谱§4/§6 施 | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |
| PQ-0264 | SL-B07 雪球/股吧散户情绪线 U5 消费方挂接核验：消费挂接记录（层宪章/问题表 line_ref/data_sources 入表）系 W6/W7 施工件，B 档未落库未挂线，源线谱/层宪章行级 | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |
| PQ-0269 | SL-B08 APP 榜单线 U4 PIT 控制执行审计：B 档'外有可采未落库'——管线未建、DS 册无 active 条目、入库链路不存在，审计对象存在性=False 属源线谱§4/§6 施工边界 | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |
| PQ-0270 | SL-B08 APP 榜单线 U5 消费方挂接核验：消费挂接记录（层宪章/问题表 line_ref/data_sources 入表）系 W6/W7 施工件，B 档未落库未挂线，源线谱/层宪章行级交叉比 | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |
| PQ-0275 | SL-B09 进出口贸易线 U4 PIT 控制执行审计：B 档'外有可采未落库'——管线未建、DS 册无 active 条目、入库链路不存在，审计对象存在性=False 属源线谱§4/§6 施工边界设 | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |
| PQ-0276 | SL-B09 进出口贸易线 U5 消费方挂接核验：消费挂接记录（层宪章/问题表 line_ref/data_sources 入表）系 W6/W7 施工件，B 档未落库未挂线，源线谱/层宪章行级交叉比对 | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |
| PQ-0281 | SL-B10 信用卡/支付消费线 U4 PIT 控制执行审计：B 档'外有可采未落库'——管线未建、DS 册无 active 条目、入库链路不存在，审计对象存在性=False 属源线谱§4/§6 施工 | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |
| PQ-0282 | SL-B10 信用卡/支付消费线 U5 消费方挂接核验：消费挂接记录（层宪章/问题表 line_ref/data_sources 入表）系 W6/W7 施工件，B 档未落库未挂线，源线谱/层宪章行级交 | 无（B 档接入施工立项属另立战役规划事项，非本题人机门位） |

## fail 侧交叉引用

45 条 fail 闭环台账=[gaps/FAIL_CLOSURE_LEDGER.md](gaps/FAIL_CLOSURE_LEDGER.md)；大缺口工单总册=[gaps/WORKORDER_MASTER.md](gaps/WORKORDER_MASTER.md)。A 类清单与 fail 工单存在同源归并（A06 资金流回补同 WO-011/数据清单#1）。