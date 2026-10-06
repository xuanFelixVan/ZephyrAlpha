---
ttl: task_bound
title: M1-SL-A15 预注册卡（规格预填）——Hyperliquid 资金费率跨市场杠杆拥挤条件轴
status: draft_pre_freeze   # SOP 铁律二：跑数前冻结，启动后不得改动
family_id: M1-ALT-A15
n_eff: 6   # 聚合口径(中位数/OI加权/极端占比) × 桶(3) × 对齐(1)，冻结后回填
hypothesis: "永续资金费率是加密杠杆多头拥挤度的直接计量——费率高企=多头拥挤=全球 risk-on 的极端端，历史上先于或同步于 risk-off 转折；作为 A 股组合的风险偏好条件轴（拥挤桶收缩敞口/防守），非选股 alpha。出处：费率=拥挤度而非方向预言（[Funding Rate Crowding Risk in Crypto Perpetuals](https://www.bifu.co/blog/funding-rate-crowding-risk)、[Crypto Funding Rates: Positioning and Squeezes](https://coinunited.io/en/research/crypto/crypto-funding-rates-positioning-squeeze-guide-2026)）；费率机制学术面 [arXiv:2506.08573](https://arxiv.org/html/2506.08573v1)；跨资产直接证据薄（诚实位：属未充分检验假设，这正是预注册的意义）。"
data_plane:   # CH 2026-10-06 实测
  - {table: c1_market.hl_funding_history, fields: [coin, funding_time, funding_rate, premium], range: "2023-05-12..2026-10-05", coverage: "4,750,075 行 / 234 币 / 8h 费率", pollution_notes: "24/7 市场→A 股交易日对齐规则须冻结；新币上市潮造成截面扩张"}
  - {table: c1_market.hl_oi_snapshot_daily, fields: [snapshot_date, coin, open_interest, oi_ntl_usd, funding_rate, premium], range: "2026-09-18..2026-10-05", coverage: "3,744 行——仅 2.5 周，OI 加权口径暂不可考", pollution_notes: "OI 加权变体禁进 IS（样本不足），如实记"}
  - {table: c1_market.crypto_kline_daily, fields: [trade_date, symbol, close], range: "2025-08-08..2026-10-04", coverage: "19,344 行 / 133 币", pollution_notes: "对照项（BTC 动量轴 F14_BTC_MOMENTUM_30D 在产 2025-09→）"}
proxy_downgrade: "proxy：Hyperliquid 单所费率代理全加密杠杆拥挤（币安/OKX 未接）；等权/中位数代理 OI 加权（OI 快照太短）。均披露"
mechanism_one_liner: 经济逻辑一句话——资金费率是永续多头为杠杆付出的持续成本，费率极端=拥挤极致=脆弱性积累，是全球风险偏好温度计的高频读数。
data_columns_and_formula: |
  数据列名: hl_funding_history.coin/funding_time/funding_rate
  计算式（日聚合模块）:
    A 股交易日 t 的费率读数 = funding_rate 按 funding_time ∈ (t-1 15:00, t 15:00] 右闭聚合:
      f_med(t) = median_i( funding_rate_i )                    # 主口径：全市场中位数（3 段/日）
      f_ext(t) = share_i( funding_rate_i > q90(IS 期阈值) )    # 极端拥挤占比
    桶: f_med 三分位（IS 期边界钉死），考 A 股主干组合在拥挤/中性/冷清桶的 Sharpe/MaxDD
exam_method: |
  考法: 条件化（拥挤桶 vs 其余桶的 A 股组合净值/回撤对比 + 桶间差 bootstrap）；辅助: 拥挤极值后 N 日 risk-off 事件命中率（对照随机）。
thresholds:
  - {metric: 条件增益, rule: "拥挤桶 MaxDD 改善 ≥5pp 且收益不劣化 → 升考证据；正考按 exam_policy"}
exam_windows:
  is: 2023-06..2025-12
  oos: 2026-01..2026-09   # OOS 偏短如实声明；结论一律降级"短 OOS 证据档"
sample_window_note: 3.5 年费率史含 2024 牛/2025 段——体制依赖强（几乎全牛市），分桶报告必须含体制占比；F14_BTC_MOMENTUM_30D（2025-09→）作相关性对照防同源计票
regime_axis: f_med 为主轴；与 F14_BTC/F4_BDI 的相关性进沙箱同源预检（S4 第一关）
multiplicity:
  total_tests: "2 口径 × 3 桶 × 1 前瞻 ≈ 6 组"
  dsr_note: 组数少但 OOS 短——DSR 校正照喂全部试验次数
cost_spec: 条件轴类按仓位控制考法计五项成本；不做个股轮换
risks_and_prohibitions:
  - "PIT: funding_time 右闭对齐 A 股 15:00；8h 结算时戳不可回填（TDM pit_proof）"
  - "OI 加权口径在 OI 快照（2.5 周）充足前禁用——禁用短样本伪装长历史因子"
  - "单所 proxy 偏差如实披露；结论禁表述为'全市场拥挤度'"
  - "样本期牛市长，'拥挤桶回撤保护'结论可能只是牛市无回撤的伪象——必须报分桶占比与体制标签"
exits: [达标→S6 备料（条件轴归 regime 族） / 不达标回S0-S3 / 判死归档]
---
