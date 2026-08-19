---
ttl: task_bound
---

# AI-NIGHT-001 阶段2 — 端到端红蓝对抗测试报告（数据→信号→组合→执行→风控）

日期：2026-08-19 ｜ 执行：红蓝对抗（非 mock）｜ 基线：阶段1 八项回测正确性修复已落 dev HEAD

---

## 0. 总结论

三层验证**全部通过**，红队三向量**全部 PASS**。过程中新发现 **3 个 P0 正确性 bug**（阶段1 八项修复之外的增量发现），已全部修复并配回归测试；相关 6 个测试套件 **2230 passed / 1 skipped / 23 xfailed / 2 xpassed**，无回归。

| 层 | 结论 | 关键证据 |
|---|---|---|
| Layer 1 已知答案（toy 逐分对账） | PASS（28 用例） | 成交价/量/佣金/现金/avg_cost/realized_pnl/NAV 全部 Decimal 精确等值，错一分钱即 fail 的口径下零偏差 |
| Layer 2 全链连通（真实 CH） | PASS | CH 9,659,286 行实证在库 → load_history → momentum_20d → synthesize → topn-momentum → DefaultBacktestEngine → ConstraintSolver → RiskLayerOrchestrator.evaluate_intraday，各层内部逻辑零 mock |
| Layer 3 区间烟感（真实数据近 6 个月） | PASS（不离谱） | 见 §3；全部指标在经验区间内，与等权买入持有偏差 3.1pp |
| Layer 4 红队向量 ×3 | 全部 PASS | ①除权不再产生虚假 −50%（#197 验证）②满仓零成交 warning 显化（#210 验证）③Σ=1 极端输入保持（#205/#206/#207 验证） |

---

## 1. Layer 1 — toy 逐分对账精度实证

文件：`tests/backtest/test_toy_reconciliation_night001.py`（28 用例，全绿）。

对账口径独立手算（来自模块公开规则：滑点 1bp、佣金万三最低 5 元、印花税千一、100 股整手、price 已含滑点不得双计），与真实引擎输出做 **Decimal 精确等值断言**（非 approx）：

| 场景 | 对账点 | 实证值（手算 = 引擎） |
|---|---|---|
| ① 普通买入 | 50,000股@10.00 → 价 10.001 / 佣 150.015 / 总成本 500,200.015 / 最低佣金 5 元触板用例 | 精确一致 |
| ① 普通卖出 | 26,200股@11.00 → 价 10.9989 / 佣+税 374.622534 / 回款 287,796.557466 / avg_cost 10.0040003 | 精确一致 |
| ② 涨跌停板块推断 | 主板 10.99 成/11.00 拒；科创 68x +15% 成/+20% 拒；创业 30x 同；北交 8/92x +29.9% 成/+30% 拒；引擎日频路径 prev_close 逐日传递涨停日零成交 | 9 参数化用例全过 |
| ③ T+1 | 当日买当日卖 → PortfolioError("T+1")，持仓零污染；次日可卖；allow_t_plus_1 做T通道放行 | 3 用例全过 |
| ④ 卖出回款（#210 回归） | 全往返现金恒等式 final = initial − buy_cost + sell_proceeds = 1,049,030.31483 精确；realized_pnl = 49,030.31483 = final − initial；显式 slippage_cost≠0 用例拦截双计回退（差 55 元即 fail） | 精确一致 |
| ⑤ 引擎级 5 日全链 | 信号→撮合→记账→NAV 逐日手算：d1 双买（66,600 股 A + 300 股高价 B）→ d4 涨停价清仓 A + 补仓 B 700 股 → 终现金 64,908.005258、B avg_cost 1000.40003、A realized 65,308.035258、逐日 NAV 五点全对、BacktestResult.total_return 与手算 rel<1e-9 | 精确一致 |

---

## 2. Layer 2 — 全链连通实证（真实 CH，非 mock）

文件：`tests/cross/test_e2e_redblue_night001.py`（21 用例，全绿；CH 不可达时整文件 skip）。

- **数据层**：`load_history` 真实查询 c1_market.kline_daily，10 只沪深300成分（600519/000858/601318/600036/000333/600900/601899/600030/002594/000651）× 131 交易日（2026-02-02..2026-08-19 实证在库）。
- **信号层**：momentum_20d 真实因子 → synthesize 截面合成 → pit_shift=1 平移 → topn-momentum 产权重面板。PIT 验证：首个非零权重出现在第 ≥20 行（warmup 期内出信号即前视，断言拦截）。
- **组合层**：ConstraintSolver 消费真实权重面板（RiskLimits max_single=0.10 严于策略 0.20）→ C7 裁剪违规如实记录、Σw≤1.0、单标的≤0.10、converged=True。
- **执行层**：DefaultBacktestEngine 跑出 BacktestResult 全字段；轮动 SELL 真实发生（见 §4 P0-2，修复前实数据一笔 SELL 都没有）。
- **风控层**：RiskLayerOrchestrator（DrawdownController/DrawdownTracker/VaRCalculator/TailRiskMonitor 全真实实例，仅 broker 外部边界为测试替身——对齐 tests/ex_core 既定模式）逐日消费 130 点真实 NAV 序列，position_cap∈(0,1]、样本充足后 VaR/尾部链不降级。

---

## 3. Layer 3 — 区间合理性烟感（真实数据动量回测）

窗口 2026-02-02..2026-08-18，10 只大盘蓝筹，W-FRI 周频调仓，top_n=5 / max_single=0.20，初始资金 100 万：

| 指标 | 实证值 | 经验区间判定 |
|---|---|---|
| total_return | **−8.52%** | ±60% 内 ✓（同期 000858 −32.4%、601318 −21.5%，下跌 tape 合理） |
| annual_return | −15.74% | ±150% 内 ✓ |
| sharpe_ratio | **−1.33** | \|s\|<4 ✓（前视典型征兆为高正夏普+高胜率，未出现） |
| max_drawdown | 12.95% | <40% ✓ |
| win_rate | 34.6% | [20%,80%] ✓ |
| trades_count | 111 | [5,500] ✓（28 周调仓+轮动清仓，量级合理） |
| 对照：等权买入持有 | −5.41% | 偏差 **3.1pp** ≤ 35pp ✓（动量在下跌 tape 追弱+成本磨损，跑输等权 3pp 符合直觉） |
| 因子评估（同窗口） | IC −0.007 / IR −0.019 / OOS正率 35% | 动量因子本窗口近零 IC，与策略小负收益互相印证 |

**判定：不离谱。** 无任何前视/未来函数/成本漏算的典型数值征兆（不离谱≠正确——正确性由 Layer 1 逐分对账背书）。

---

## 4. 红队攻击向量 PASS/FAIL

| 向量 | 结论 | 实证 |
|---|---|---|
| ① 除权日信号收益核算 | **PASS** | 真实 `_adjusted_close_panel`+`_compute_forward_returns` 消费 10送10 toy 序列：跨除权日前向收益 = 0.00%（修复前 raw close 口径 = −50.00%，对照实验同测试内固化）；adj_factor NULL/0/负 → 回退 1.0 防御有效；真实 CH evaluate_factor 跑通，IC 不离谱 |
| ② 满仓信号零成交 warning 显化 | **PASS** | 单标的满仓（Σ=1 归一化）信号：买入成本 1,000,400.03 > 100 万必然拒单 → 零成交，但逐笔 "Fill skipped" + 汇总 "回测完成但 N 笔 fill 被拒绝" warning 全部显化（caplog 断言，#210 修复生效） |
| ③ Σ=1 极端输入 | **PASS** | RegimeMetaAllocator：N=2 全贴 cap（0.8<1）与 N=25 全贴 floor（1.25>1）两不可行场景 Σ=1±1e-9（#206）；极端绩效离散+shrinkage 启用下 effective=alloc×shrinkage 两层一致；ConstraintSolver：软拥挤 ρ=0.85 一次性减半 Σw=0.5 不坍缩（#205）、硬拥挤 ρ=0.95 清零小者、全同号暴露标 infeasible 不缩放（#207）、Σw=10 极端输入裁到 ≤1.0 |

---

## 5. 新发现 bug 及修复（阶段2 增量，3 个 P0 全部已修）

> 与阶段1 八项修复（#196/#197/#198/#202/#203/滑点双计/涨跌停板块推断/组合坍缩三件套/Σ=1）无文件区域交叠；匹配引擎今日改动在 `_infer_limit_pct` 区，本次改动在其下游 `_build_target_orders` 与新增 `_is_limit_up/_is_limit_down`，无冲突。

### P0-1 持仓标的停牌/缺价日 NAV 幻视回撤 — `src/zephyr/backtest/core/portfolio.py`

- **实证**：持有 1,000 股@10，次日 prices 缺该标的 → NAV 从 999,995 幻视跌到 989,995（−10,000），复牌日幻视恢复。多标的错开停牌时 NAV 序列锯齿化，直接污染 Sharpe/MDD/total_return，且 `total_nav` 低估会使撮合目标 sizing 系统性偏小。
- **修复**：新增 `_last_prices` 最后已知价结转——买/卖 fill 与每日有效价（>0）登记；`update_market_value`/`total_market_value` 估值时当日有效价优先、缺失/非正结转最后已知价。
- **回归测试**：场景⑥ 3 用例（停牌日 NAV 不变/复牌正确重估、total_nav 结转、price≤0 视为无效）。

### P0-2 跌出信号的持仓永不清仓（目标权重语义残缺） — `src/zephyr/backtest/core/matching_engine.py`

- **实证**：信号 {A:0.6,C:0.4}→{B:0.6,C:0.4} 轮动，A 轮出后 **59,900 股永久滞留**（无任何 SELL），轮入的 B 因现金被锁连续 3 天买入被拒——任何轮动策略的回测都系统性失真（持仓只进不出、换手低估、收益退化为"所有曾入选标的的买入持有"）。根因：`_build_target_orders` 只迭代 target_weights，`_normalize_day_signals` 又过滤零值，策略永远无法表达"退出"。
- **修复**：目标权重语义补全——持仓但目标权重缺失/≤0 的标的生成全量清仓 SELL（停牌/跌停无法成交时跳过），与既有差额单一起先卖后买。
- **回归测试**：场景⑦ 3 用例（跌出清仓/停牌不清仓/引擎级轮动端到端）；跨层 `test_rotation_sells_actually_happen` 用真实数据固化（修复前真实数据 28 周一笔 SELL 都没有）。

### P0-3 涨跌停阻断买卖对称（涨停日卖单被误锁） — `src/zephyr/backtest/core/matching_engine.py`

- **实证**：P0-2 修复后的回归测试暴露——A 于轮出日 +10% 涨停，清仓卖单被阻断（`_is_price_limit` 对称判板）。A股微观结构：涨停封板只阻买单（卖方排队买盘即时消化，卖单可成交）；跌停反之。对称阻断会在涨停日锁死一切减仓/清仓。
- **修复**：拆分为 `_is_limit_up`/`_is_limit_down` 方向感知判定——涨停拒买、跌停拒卖；`_is_price_limit` 保留为两者或运算（既有板块推断测试不动）。
- **回归测试**：场景② `test_limit_down_sell_rejected`（跌停拒卖保持）+ 场景⑤ d4 涨停价清仓成交 + 场景⑦ 引擎级轮动。

---

## 6. 登记事项（非本阶段修复对象）

1. **adj_factor 全表=1（#209② 已知 P2 遗留实证固化）**：c1_market.kline_daily 全 965 万行 adj_factor 无一行 ≠1。#197 的复权链路在真实数据下退化为 raw close 口径，真实除息缺口（如茅台年度分红 −1.5%~−2.5% 跳空）仍会被计入策略盈亏与 IC。已写实证断言 `test_real_ch_adj_factor_uniformly_one_registered_limitation`：一旦 adj_factor 接入真实值该断言会 fail，提示升级为真实除权事件验证。另：回测引擎本身不做公司行动处理（除权日股数调整），属更大的功能项，建议连同 #209② 一并立项。
2. **满仓（Σ=1 归一化）信号与成本的结构性摩擦**：vectorized 引擎将信号归一化为满仓，而目标 sizing 不留成本余量 → 单标的满仓信号买入必然差几百元被拒（每日重复 warning）。当前行为"拒单+可见"是安全的，但更友好的做法是 sizing 时预留滑点+佣金余量（建议 P1 优化，不改现状）。
3. **涨跌停价 rounding 口径**：`quantize(0.01)` 默认 ROUND_HALF_EVEN，与交易所实际涨停价舍入（如 10.15×1.1=11.165 → 交易所 11.17，本实现 11.16）在分位边界有 1 分差异，仅影响恰卡边界的极端价，建议随 stk_limit 表接入（#211 遗留）一并校准。
4. **kline_daily 存在 1970-01-01 异常行**（min(trade_date) 探测所见）：数据层清洗遗留，量极小，建议数据治理例行排查。

---

## 7. 文件清单

**新增测试（2 文件，49 用例）**
- `tests/backtest/test_toy_reconciliation_night001.py`（28 用例：Layer 1 四场景 + 引擎级对账 + P0-1/2/3 回归 + 红队向量②）
- `tests/cross/test_e2e_redblue_night001.py`（21 用例：Layer 2 连通 6 + Layer 3 烟感 3 + Layer 4 向量①③ 12）

**src 修复（2 文件）**
- `src/zephyr/backtest/core/portfolio.py`（P0-1：`_last_prices` 结转 + `_remember_prices`/`_resolve_price`）
- `src/zephyr/backtest/core/matching_engine.py`（P0-2：清仓单生成；P0-3：`_is_limit_up`/`_is_limit_down` 方向感知）

**本报告**
- `docs/_working/reviews/2026-08-19-night001-e2e-redblue.md`

**验证执行**：`tests/backtest/ tests/pf_core/ tests/cross/ tests/factor/ tests/pf_alloc/ tests/ex_core/` 合计 **2230 passed, 1 skipped, 23 xfailed, 2 xpassed**（19.01s）。

## 8. 阻塞

无。未 git commit（按统筹统一收口要求）。
