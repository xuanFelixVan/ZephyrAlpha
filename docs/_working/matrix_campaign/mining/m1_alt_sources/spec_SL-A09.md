---
ttl: task_bound
title: M1-SL-A09 预注册卡（规格预填）——市场级新闻情绪指数与极端情绪反转
status: draft_pre_freeze   # SOP 铁律二：跑数前冻结，启动后不得改动
family_id: M1-ALT-A09
n_eff: 6   # 市场级情绪因子(水平/变化/极值反转) × 前瞻(1/5/10) × 桶(3)，冻结后回填
hypothesis: 媒体快讯情绪的极端水平伴随注意力过度反应，随后出现反转（Barber & Odean 注意力理论 + A股散户情绪市）；市场级情绪指数的变化率可作择时条件轴，个股级映射因历史缺口本期不立假设（如实记）。
data_plane:   # CH 2026-10-06 实测
  - {table: c3_fundamental.news_data, fields: [news_id, publish_time, source, quality_flag], range: "2010-01-02..2026-10-05", coverage: "8,119,241 行 / 7,927,326 uniq id", pollution_notes: "related_symbols 仅 ~80 行非空 → 个股级历史映射不可建（P3 教训：声称覆盖必须复核，此处如实判缺口）"}
  - {table: c3_fundamental.news_sentiment_score, fields: [news_id, polarity, label, n_pos, n_neg, method, caliber_version, scored_at], range: "7,947,739 行 / 7,937,504 uniq news", coverage: "≈97.8% 已打分", pollution_notes: "caliber_version 变更点须圈污染段（净段证据档候选）"}
  - {table: c1_market.news_sentiment_window, fields: [window_date, symbol, sentiment_index, avg_polarity, positive_count, negative_count, total_count, scope], range: "2026-02-24..2026-10-04", coverage: "19,831 行 / 4,858 票", pollution_notes: "仅 8 个月——个股级面只作管道验证段，禁进 IS"}
proxy_downgrade: 个股级情绪历史不可建 → 本卡只考市场级（指数/择时条件），proxy_downgrade=个股情绪因子降级为"管道就绪、数据未备"
mechanism_one_liner: 经济逻辑一句话——快讯流情绪是散户注意力的实时计量，极端乐观/悲观对应流动性提供者的反向机会窗口。
data_columns_and_formula: |
  数据列名: news_data.news_id/publish_time；news_sentiment_score.news_id/polarity/caliber_version
  计算式（市场级日度聚合模块=M 级补写内容）:
    mkt_sent(t) = mean( polarity | publish_time ∈ (t-1 15:00, t 15:00] )   # 窗口右闭，A 股交易日对齐
    f_level(t)  = mkt_sent(t)                                              # 水平（择时条件）
    f_rev(t)    = -rank( mkt_sent(t) - mean(mkt_sent, 20) )                # 极端情绪反转
    PIT: publish_time 即落定时戳不可回填（TDM pit_proof）；打分得分后追加不改变原始文本，但 polarity 是派生值——
    派生时戳=scored_at，若 scored_at 晚于 t+1 日则该条在 t 日不可知，聚合须按 scored_at 二次过滤（严格版）
exam_method: |
  考法: 市场级=时序条件考法（情绪三分位桶 × 下期指数收益/回撤），非截面 IC；
  辅助: 情绪极端日 vs 常态日的 next-5d 指数收益差，bootstrap CI。
thresholds:
  - {metric: 桶间差, rule: "极值桶与中性桶 5 日收益差 >0（反向）且 90% CI 不含 0 → 升考证据；正考按 exam_policy"}
exam_windows:
  is: 2012-01..2023-12   # sentiment_score 覆盖先实查 2010-2011 密度，不足则顺延起点（冻结前定）
  oos: 2024-01..2026-09
sample_window_note: 16 年跨多轮情绪周期；新闻源结构变化（cls/eastmoney/rss 占比漂移）须按年度报源占比，重大断档圈污染段
regime_axis: 情绪自身即候选轴；为满足"一次一轴"，主轴钉 f_level 三桶，六态桶另批
multiplicity:
  total_tests: "3 因子 × 3 前瞻 × 3 桶 = 27 组"
  dsr_note: 时序样本量小（日度≈3,300 IS 日），桶后每桶≈1,000 日，功效须在卡内声明
cost_spec: 择时条件类不涉及个股换手；若转仓位控制考法按引擎五项成本
risks_and_prohibitions:
  - "PIT 铁律: 聚合窗口右闭且按 publish_time；严格版加 scored_at 二次过滤（打分器上线时间造成的隐形前视是本卡头号风险）"
  - "个股级历史映射缺口如实记：related_symbols≈空 → 禁用 title 正则捞股票名伪装个股因子（映射质量无保证）"
  - "caliber_version 变更=分界点，跨版本混算须净段声明"
  - "news_sentiment_window（8 个月）禁进 IS，只作管道一致性验证"
exits: [达标→S6 备料 / 不达标回S0-S3（含个股级待数据回补重开） / 判死归档]
---
