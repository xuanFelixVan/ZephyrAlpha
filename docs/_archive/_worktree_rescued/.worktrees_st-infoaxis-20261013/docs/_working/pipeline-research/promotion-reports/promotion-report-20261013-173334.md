# 转正建议书（组合门打分）

- 生成: 2026-10-13 17:33:34.477110+00:00（机生禁手改）
- 阈值出处: config/standards.yaml#STD-SIM-ACCESS-002（v2 frozen 2026-09-18，裁定#337）（预注册冻结，修标走标准库重考历史）
- v1 尺注记: STD-SIM-ACCESS-001=suspect（裁定#306：累计 N 口径 DSR>0 需 SR≥2.68 与 OOS≥1.5 数学互斥）——本报告按 v2 frozen 尺打分，历史 v1 对照见 config/standards.yaml
- 扫描候选: 1

| 候选 | OOS Sharpe | 最大回撤 | 成交笔数 | DSR | ρ̄ | 年化换手 | 裁定 |
|------|-----------|---------|---------|-----|---|---------|------|
| STR-VREV-025 | 缺证 | 缺证 | 缺证 | 缺证 | 缺证 | 缺证 | **borderline** |

## STR-VREV-025 — borderline
- [GAP] oos_sharpe: value=None threshold=1.5 (source=strategy_screen/advisory)
- [GAP] max_drawdown: value=None threshold=0.15 (source=sim_pocket_daily)
- [GAP] capacity_trades: value=None threshold=30 (source=sim_trade_log)
- [GAP] dsr: value=None threshold=≥ 0.5（v2：族 N_eff 口径） (source=strategy_screen)
- [GAP] combo_corr: value=None threshold=≤ 0.7（v2 新增腿①） (source=advisory/联赛（F73 未建常缺证）)
- [GAP] ann_turnover: value=None threshold=≤ 12.0（v2 新增腿③） (source=strategy_screen.turnover/advisory)
- 证据缺口: oos_sharpe,max_drawdown,capacity_trades,dsr,combo_corr,ann_turnover（borderline=继续观察，不冤枉不放水）
- **建议：继续模拟观察，补齐证据缺口后重跑**
