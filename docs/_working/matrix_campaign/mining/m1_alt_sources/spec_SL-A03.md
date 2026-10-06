---
ttl: task_bound
title: M1-SL-A03 预注册卡（规格预填）——板块/概念指数动量与两层选股
status: draft_pre_freeze   # SOP 铁律二：跑数前冻结，启动后不得改动
family_id: M1-ALT-A03
n_eff: 6   # mom5/10/20/60 × 板块Top-K(10/20) × 行业中性 on/off，封闭族以冻结清单为准
hypothesis: 板块指数动量有 1-3 个月持续期（行业动量=Jegadeesh & Titman 1993 的板块版；A股板块资金聚集-扩散机制），板块层动量 Top-K 再进板块内个股排序可领先全截面选股——同时是 T3 缺口 M3（TDM-E-L2 板块主干最简版）的原料验证。
data_plane:   # CH 2026-10-06 实测，非抄声称值
  - {table: c1_market.kline_sector_880, fields: [trade_date, sector_code, sector_name, close, volume, amount], range: "2020-03-17..2026-09-30", coverage: "729 板块/763,260 行", pollution_notes: "880 同花顺体系，成分变动不可回溯；无复权问题（板块指数）"}
  - {table: c1_market.concept_board / concept_board_constituent, fields: [board_code, board_name, symbol, valid_from, valid_to], range: "board 750 个；成员 valid_from 2026-08-10..2026-09-30", coverage: "成员映射仅 2 个月版本史", pollution_notes: "成员 SCD2 无历史=概念成员面 IS 期不可用，本卡只用板块指数价量面"}
  - {table: c1_market.kline_daily, fields: [trade_date, symbol, close], range: "考卷引擎现行载荷", coverage: "全 A", pollution_notes: "复权口径按 exam_policy 复权降级条款"}
proxy_downgrade: 无（板块指数即真源本体）；成分映射缺口见上
mechanism_one_liner: 经济逻辑一句话——板块指数动量=资金聚集度的即期计量，聚集-扩散有惯性，板块层信号先于个股基本面落地。
data_columns_and_formula: |
  数据列名: kline_sector_880.trade_date/sector_code/close/amount；kline_daily.close（个股层）
  计算式:
    sec_mom_k(s,t) = close_sec(s, t-1) / close_sec(s, t-1-k) - 1   # T-1 PIT，禁用当日
    板块层: 板块截面 rank(sec_mom_20) 取 Top-K 板块
    个股层: 个股因子 = 1{symbol ∈ Top-K 板块} × rank(个股 20 日残差动量)（残差=对板块收益回归取残差）
    考卷接线形态: 作为 A1 输入的单因子/合成因子档进现行九维网格（T3 缺口 M3 的最简实现=板块动量 Top-K × 板块内两层排序）
exam_method: |
  考法: S2 海选=横截面 Spearman 秩 IC（板块因子在板块截面；个股因子在全 A 截面），前瞻 5/10/20 交易日；
  分体制: 主轴=F4_BDI_MOMENTUM_Z20（T-1，在产 1989→2026）或 regime_state_anchored 六态桶（一次考试一个主轴，SOP §2.1），
  桶边界 IS 期钉死，最小桶样本 60 交易日（F 先例）。
thresholds:
  - {metric: 海选 |t|, rule: ">3.29 仅作'值得升考试'弱证据（SOP §3.5），不判有效"}
  - {metric: S5 正考, rule: 按 exam_policy 准入/成本双口径/DSR（喂全部试验次数），本卡不预判数值门柱}
exam_windows:
  is: 2020-04..2024-12   # 数据 2020-03 起，留首月做 mom 窗
  oos: 2025-01..2026-09
sample_window_note: 880 板块 2020-03 起有价量；概念成员映射 2026-08 起才可靠（见 pollution_notes）
regime_axis: F4_BDI_MOMENTUM_Z20 主轴，状态取 T-1；三桶（上/平/下按 IS 分位 1/3 切）；最小桶 60 日
multiplicity:
  total_tests: "6 因子形态 × 3 前瞻 × 3 桶 ≈ 54 组（冻结清单定稿后回填精确值）"
  dsr_note: N_eff=54 时 DSR>0.5 所需 SR 显著高于无条件档；桶×前瞻乘积是假阳性放大器（SOP §2.7）
cost_spec: 成本口径=引擎现行五项（exam_policy §4 双口径），不另设
risks_and_prohibitions:
  - "PIT: 板块指数快照落定不修订（TDM pit_proof）；一切因子用 t-1 及以前收盘"
  - "禁用 concept_board_constituent 做历史成员回溯（valid_from 仅 2026-08）——成员面历史=缺口，只许 2026-08 后验证段试探"
  - "880 板块代码清单冻结后不得中途增删（防选择性报告）"
  - "板块因子换手天然高于个股因子，成本门不放松"
exits: [达标→S6 备料 / 不达标回S0-S3 / 判死归档（带 ≥3 已排除候选）]
---
