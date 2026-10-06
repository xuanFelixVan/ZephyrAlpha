---
ttl: task_bound
title: M1-SL-A13 预注册卡（规格预填）——股东户数筹码集中度因子
status: draft_pre_freeze   # SOP 铁律二：跑数前冻结，启动后不得改动
family_id: M1-ALT-A13
n_eff: 6   # 变化率/绝对变动/连续期数 × 前瞻(10/20/60) × 桶(2)，冻结后回填
hypothesis: 股东户数下降=筹码集中（散户离场/机构吸筹），对个股未来 10-60 日收益有正向预测力——A 股卖方金工共识假设（东方财富证券《基于高频股东人数变化的选股思路》2019-03；光大证券《股东大类因子，拆解股东数据中的多元信息》；数据参考 https://data.eastmoney.com 股东户数统计）。
data_plane:   # CH 2026-10-06 实测
  - {table: c3_fundamental.shareholder_count, fields: [symbol, announce_date, end_date, holder_count, data_source, quality_flag], range: "1993-01-12..2026-09-30", coverage: "514,395 行 / 5,906 票", pollution_notes: "announce_date 与 end_date 双轴齐备=PIT 干净；披露频率不均（定期报告强制+自愿披露混杂）→ asof 投影是关键实现点"}
proxy_downgrade: 无（户数即真源本体）
mechanism_one_liner: 经济逻辑一句话——股东户数是筹码持有者分散度的直接读数，户数下降=筹码从散户向大资金转移，知情方建仓在先、定价随后。
data_columns_and_formula: |
  数据列名: shareholder_count.symbol/announce_date/end_date/holder_count
  计算式:
    h(t) = holder_count 的 asof 投影值   # 对每个交易日 t 取 announce_date ≤ t-1 的最近披露（PIT 投影）
    f_chg(t) = -[ log h(t) - log h(t_prev_disclose) ]                     # 主因子：对数户数降幅（正=集中）
    f_chg60(t) = -[ log h(t) - log h(t-60 交易日 asof) ]                  # 季度对齐变体
    f_streak(t) = count( 连续披露期户数下降 )                             # 持续集中变体
    全截面 rank 后进 A1 因子面；禁用 end_date 做时点对齐（end_date 是报告期末，非可知日）
exam_method: |
  考法: S2 海选=Spearman 秩 IC，前瞻 10/20/60（低频因子给长前瞻）；分体制主轴=F4_BDI_MOMENTUM_Z20 三桶；
  辅助分桶: 披露密集期（4/8/10 月）vs 稀疏期——信息到达集中度不同。
thresholds:
  - {metric: 海选 |t|, rule: ">3.29 升考弱证据"}
  - {metric: S5 正考, rule: 按 exam_policy；低频因子换手低，成本门预期友好}
exam_windows:
  is: 2010-01..2023-12   # 覆盖创业板/注册制/开放自愿披露各体制段
  oos: 2024-01..2026-09
sample_window_note: 33 年全史可用（1993 起），IS 从 2010 起是为与现代市场结构同构；1993-2009 可作附加稳健段
regime_axis: F4_BDI_MOMENTUM_Z20 主轴 T-1 三桶；预期集中度因子在情绪下行/存量博弈桶更有效——如实报不硬凑
multiplicity:
  total_tests: "3 因子 × 3 前瞻 × 3 桶 = 27 组"
  dsr_note: 27 组计入 DSR；低前瞻重叠性高（10/20/60 相关），N_eff 实际低于名义——封闭族声明按相关调整后报
cost_spec: 成本五项现行口径；半年频更新的因子预期低换手
risks_and_prohibitions:
  - "PIT 铁律: 一切按 announce_date 可知日消费；end_date 只作报告期标识，禁用于时点对齐（前视 10-15 天）"
  - "asof 投影实现须单测边界（同日多披露取最后一条；跨停牌投影）"
  - "户数披露自愿性→样本构成漂移（爱披露的公司有偏），报告披露频率分布"
  - "禁把 hold_count 与 top10_shareholders 混算（后者归 G3 卡，防跨卡重复计票）"
exits: [达标→S6 备料 / 不达标回S0-S3 / 判死归档（带 ≥3 已排除变体）]
---
