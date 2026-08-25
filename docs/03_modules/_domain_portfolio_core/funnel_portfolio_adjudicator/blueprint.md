---
blueprint_id: MOD-PF-010
module_name: funnel_portfolio_adjudicator
domain: D_PF_CORE
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: H
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_PF_CORE
path: src/zephyr/pf_core/core/funnel_portfolio_adjudicator.py
granularity: file
---

# MOD-PF-010 funnel_portfolio_adjudicator 蓝图（筛选漏斗第六层：组合优化 →N≤10）

> **module_id**: MOD-PF-010 | **域**: D_PF_CORE | **优先级**: P1
> **来源**: B10-01505（AUD-DRAFT-001-DIGEST P1 波 W-P1-21，CAND-PF004-003，A1交易决策架构 §13）
> 代码：`src/zephyr/pf_core/core/funnel_portfolio_adjudicator.py`

## 0. 定位

筛选漏斗**第六层**裁决器：对第五层产出候选（~30）施加组合层规则族，输出
N≤10 目标持仓清单（含权重）。规则族：行业±10%/绝对30% + 市值分散 + 波动率与
MaxDD 风险预算 + 风格暴露 ≤±0.3σ + corr<0.7 过滤 + C-045 拥挤度降权 +
C-036 合力偏空整体降仓。

查重分工（W-P1-21 铁律③）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| portfolio_optimizer | MOD-PF-002 | 通用权重优化（风险预算/均值方差/Kelly+约束→CTR-007） | 优化数学引擎；本件=漏斗层**规则裁决器**（筛选+降权+预算），不重复凸优化 |
| strategy_cpcv_matrix | MOD-BT-028 | 第五层**离线** CPCV 打分（D_BACKTEST） | 上游打分层；本件消费其候选结论（注入） |
| strategy_cross_vote_funnel | MOD-SIG-109 | 第五层**在线**投票（D_ASHARE_SIGNAL） | 信号层；不同数据平面 |
| constraint_solver | MOD-PF-006 | CTR-003 限额投影求解 | 本件规则族为漏斗专用（corr 过滤/拥挤降权/偏空降仓），非通用约束求解 |

## 1. 规则（确定性纯函数，数据全注入）

- **拥挤度降权（C-045）**：crowding ≥ crowding_warn（默认 0.7）→
  adjusted = score × (1 − derate × crowding)（derate 默认 0.5）。
- **排序**：adjusted 降序，同分按 symbol 升序（确定性）。
- **corr 过滤**：与已选任一标的 |corr| ≥ corr_limit（默认 0.7）→ 跳过。
- **行业约束**：行业权重 ≤ industry_abs_cap（默认 0.30）；若注入基准行业权重，
  另 ≤ benchmark + industry_band（默认 ±0.10）。等权目标下按入选进度预判。
- **市值分散**：大/中/小市值三桶（阈值注入），单桶占比 ≤ bucket_cap（默认 0.7）。
- **风险预算**：组合波动率 σ_p = √(w′Σw)（由个股波动率+corr 矩阵合成）≤
  vol_budget；加权 MaxDD ≤ maxdd_budget；超限则确定性淘汰（最低 adjusted 先出）
  重算，直至满足或清仓。
- **风格暴露**：|Σ w×loading| ≤ style_limit（默认 0.3σ）；超限淘汰该因子最大
  贡献者重算。
- **C-036 合力偏空**：bearish=True → 总仓 × bearish_gross（默认 0.5），余为现金。
- **输出**：N≤10 目标持仓清单（权重 Σ≤1）+ 逐标的淘汰原因 + 组合诊断。
- Fail-Closed：空候选/非法阈值/未知 corr 对缺失按 0 计并披露 missing_corr。

## 2. 接口

- `FunnelCandidate`（frozen：symbol/score/industry/market_cap/volatility/
  max_drawdown/style_loadings/crowding_score）
- `FunnelAdjudicatorConfig`（frozen 阈值族）
- `FunnelPick` / `FunnelPortfolioVerdict`（frozen）
- `FunnelPortfolioAdjudicator(config=None)`
  - `adjudicate(candidates, correlations, benchmark_industry_weights=None,
    bearish=False) -> FunnelPortfolioVerdict`

## 3. 不做什么

不做凸优化（MOD-PF-002）、不打分（上游第五层）、不下单（输出候选清单供
MOD-PF-002/CTR-007 装配）、不取数（全部注入）。
