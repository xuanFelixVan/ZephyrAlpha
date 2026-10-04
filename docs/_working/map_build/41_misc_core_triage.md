---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：小簇合并册 misc_core（14 簇 118 台）
owner: st-orphtriage-20261004
---

# 41 号·小簇合并册：misc_core（14 簇 118 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml；处置=建议非终裁。
>
> 合并初判汇总：dispute=29，mount=89

### 簇 scripts.backtest（1 台；初判 mount=1）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/backtest/lane_e_enhanced.py` | 车道 E 分布预测完整化——三种模型 IS+OOS 对比实验。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |

### 簇 src.zephyr.backtest（11 台；初判 dispute=4，mount=7）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/backtest/_extensions/__init__.py` | backtest/_extensions | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/backtest/api/__init__.py` | backtest/api | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/backtest/infrastructure/__init__.py` | backtest/infrastructure | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/backtest/models/__init__.py` | backtest/models | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/backtest/regime_validation/c2_extreme_event_protection.py` | D_BACKTEST — C2 极端事件回撤保护分析（11 号 memo §4.3 C2）。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/backtest/regime_validation/c3_throttle_attribution.py` | D_BACKTEST — C3 节流归因分析（11 号 memo §4.3 C3）。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/backtest/regime_validation/c4_deflated_sharpe_runner.py` | D_BACKTEST — C4 Deflated Sharpe 跑批封装入口（11 号 memo §0.6.3 / §4.3 C4）。 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/backtest/regime_validation/e2_stationary_bootstrap.py` | D_BACKTEST — E2 Stationary Bootstrap 重采样引擎（11 号 memo §0.6.3 缺口 3）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/backtest/regime_validation/e3_param_sensitivity.py` | D_BACKTEST — E3 参数敏感性 ±20% 网格分析（11 号 memo §4.5 E3 / §4.4）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/backtest/regime_validation/e4_cost_sensitivity.py` | D_BACKTEST — E4 交易成本敏感性 0-50bps 分析（11 号 memo §4.5 E4）。 | 2026-09-22（12天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/backtest/regime_validation/exam_cost_gate.py` | E4 考尺成本门（批C 成本焊进考尺，Max 整改方案 §2-C；MOD-BT-IBT-COSTGATE）。 | 2026-09-30（4天） | in=7/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |

### 簇 src.zephyr.cross_asset（7 台；初判 mount=7）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/cross_asset/__init__.py` | [DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）（活线在身未挂线） |
| `src/zephyr/cross_asset/_extensions/__init__.py` | [DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）（活线在身未挂线） |
| `src/zephyr/cross_asset/api/__init__.py` | [DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）（活线在身未挂线） |
| `src/zephyr/cross_asset/core/__init__.py` | [DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）（活线在身未挂线） |
| `src/zephyr/cross_asset/infrastructure/__init__.py` | [DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）（活线在身未挂线） |
| `src/zephyr/cross_asset/models/__init__.py` | [DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）（活线在身未挂线） |
| `src/zephyr/cross_asset/services/__init__.py` | [DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）（活线在身未挂线） |

### 簇 src.zephyr.execution_simulation（8 台；初判 mount=8）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/execution_simulation/__init__.py` | zephyr.execution_simulation — 执行仿真域包门面（D_EXEC_SIM）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→TDM（交易执行段）（活线在身未挂线） |
| `src/zephyr/execution_simulation/_extensions/__init__.py` | exec_sim/_extensions | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→TDM（交易执行段）（活线在身未挂线） |
| `src/zephyr/execution_simulation/almgren_chriss_impact_model.py` | AlmgrenChrissImpactModel — Almgren-Chriss 冲击成本模型（MOD-EXSIM-001）。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→TDM（交易执行段）（活线在身未挂线） |
| `src/zephyr/execution_simulation/api/__init__.py` | exec_sim/api | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→TDM（交易执行段）（活线在身未挂线） |
| `src/zephyr/execution_simulation/core/__init__.py` | exec_sim/core | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→TDM（交易执行段）（活线在身未挂线） |
| `src/zephyr/execution_simulation/infrastructure/__init__.py` | exec_sim/infrastructure | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→TDM（交易执行段）（活线在身未挂线） |
| `src/zephyr/execution_simulation/models/__init__.py` | exec_sim/models | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→TDM（交易执行段）（活线在身未挂线） |
| `src/zephyr/execution_simulation/services/__init__.py` | exec_sim/services | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→TDM（交易执行段）（活线在身未挂线） |

### 簇 src.zephyr.pf_alloc（8 台；初判 dispute=5，mount=3）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/pf_alloc/_extensions/__init__.py` | pf_alloc/_extensions | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/pf_alloc/api/__init__.py` | pf_alloc/api | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/pf_alloc/infrastructure/__init__.py` | pf_alloc/infrastructure | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/pf_alloc/models/__init__.py` | pf_alloc/models | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/pf_alloc/services/__init__.py` | pf_alloc/services | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/pf_alloc/allocation_config.py` | allocation_config——组合分配链的配置真源（车道 D 实盘接线，2026-09-16）。 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/pf_alloc/core/forward_stop_loss.py` | 前瞻概率止损模块（TDM 升级蓝图 UP-2）——用分布预测 P(跌) 替代固定百分比止损。 | 2026-09-14（20天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/pf_alloc/core/tail_hedge_signal.py` | 尾部对冲信号生成器（TDM 升级蓝图 UP-5）——预测 CVaR 破阈值时生成对冲建议。 | 2026-09-14（20天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |

### 簇 src.zephyr.pf_core（8 台；初判 dispute=4，mount=4）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/pf_core/_extensions/__init__.py` | pf_core/_extensions | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/pf_core/api/__init__.py` | pf_core/api | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/pf_core/infrastructure/__init__.py` | pf_core/infrastructure | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/pf_core/services/__init__.py` | pf_core/services | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/pf_core/__init__.py` | D_PORTFOLIO_CORE Portfolio Construction — Package root | 2026-09-18（16天） | in=0/out=0·wired_dynamic | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/pf_core/default_equity_strategy.py` | D_PORTFOLIO_CORE — Default Equity Long-Only Strategy | 2026-09-16（18天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/pf_core/strategy_correlation_pipeline.py` | G07 策略间相关性验证管线骨架（23 号 memo §3.1⑤ 七部分报告模板）。 | 2026-09-17（17天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/pf_core/topn_momentum_strategy.py` | D_PORTFOLIO_CORE — TopN 动量等权策略 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |

### 簇 src.zephyr.plan_engine（4 台；初判 mount=4）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/plan_engine/brier_calibration.py` | BrierCalibration — 预案概率校准计算器 (MOD-PLAN-010) | 2026-09-02（32天） | in=3/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/plan_engine/evidence_chain_decision.py` | EvidenceChain — 证据链决策数据结构（GAP-F-42）。 | 2026-08-24（41天） | in=1/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/plan_engine/scenario_attribution_stats.py` | ScenarioAttributionStats — 预案三维归因统计器 (MOD-PLAN-009) | 2026-09-02（32天） | in=2/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/plan_engine/sit_out_list.py` | SitOutList — 禁做清单生成器 (MOD-PLAN-014) | 2026-09-02（32天） | in=2/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |

### 簇 src.zephyr.position（12 台；初判 dispute=4，mount=8）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/position/_extensions/__init__.py` | position/_extensions | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→TDM（交易日夜循环） ②retire→Owner 门位） |
| `src/zephyr/position/api/__init__.py` | position/api | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→TDM（交易日夜循环） ②retire→Owner 门位） |
| `src/zephyr/position/infrastructure/__init__.py` | position/infrastructure | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→TDM（交易日夜循环） ②retire→Owner 门位） |
| `src/zephyr/position/models/__init__.py` | position/models | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→TDM（交易日夜循环） ②retire→Owner 门位） |
| `src/zephyr/position/core/calendar_position_constraint.py` | Calendar Position Constraint — 日历仓位约束 (MOD-POS-017) | 2026-09-16（18天） | in=2/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/position/core/capital_curve_manager.py` | Capital Curve Manager — 资金曲线管理器 (MOD-POS-007) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/position/core/cash_manager.py` | Cash Manager — 资金管理器 (MOD-POS-006) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/position/core/drawdown_controller.py` | Drawdown Controller — 回撤控制器 (MOD-POS-008) | 2026-09-16（18天） | in=5/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/position/core/position_recipe_compiler.py` | D_POSITION — 仓位配方编译器（F-06 组合层穷尽网格 · 编译器雏形） | 2026-09-21（13天） | in=5/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/position/core/sell_position_link.py` | Sell-Position Bidirectional Link — 卖出-仓位双向链接 (MOD-POS-016) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/position/core/single_name_cap_caliber.py` | 单票上限三层口径映射 + 校验（31号 §2.4.1 / §5，32号 §6 同名行）。 | 2026-09-17（17天） | in=1/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/position/live_nav_recorder.py` | MOD-POS-023 — 实盘净值曲线序列（GAP-F-29，总览页净值图后端）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |

### 簇 src.zephyr.regime（14 台；初判 mount=14）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/regime/cross_sectional_features.py` | 横截面结构特征（MOD-REGIME-007，ALG-01）——regime 特征集的横截面维度补强。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/regime/institutional_regime_scorer.py` | MOD-REGIME-015 InstitutionalRegimeScorer — 三维机构级 regime 评分器。 | 2026-09-18（16天） | in=1/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/regime/validation/__init__.py` | regime 验证层 —— Phase 1 C1 (Shrinkage 节流) + Phase 2 (模型质量). | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/regime/validation/a3_transition_coverage.py` | D_REGIME — A3 状态转移路径覆盖正式统计（11 号 memo §0.5.7 A3 / §4.1 A3）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/regime/validation/a4_feature_importance.py` | D_REGIME — A4 特征重要性 Permutation 主轨（11 号 memo §4.1 A4）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/regime/validation/b2_crps.py` | D_REGIME — B2 CRPS 概率预测技能（11 号 memo §4.2 B2）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/regime/validation/b3_confidence_distribution.py` | D_REGIME — B3 置信度合理性分析（11 号 memo §4.2 B3）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/regime/validation/d1_confidence_grid.py` | D_REGIME — D1 ConfidenceSignal 四档阈值 ±20% 敏感性网格（11 号 memo §0.5.7 D1）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/regime/validation/d3_aggregation_perturbation.py` | D_REGIME — D3 聚合公式参数扰动分析（11 号 memo §0.5.7 D3）。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/regime/validation/e1_walkforward_cv.py` | D_REGIME — E1 Walk-Forward 稳定性正式统计（11 号 memo §0.5.7 E1）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/regime/validation/overfitting_guard.py` | 防过拟合方法论栈 MVP（14_regime_s2_diagnosis §4.5，N=3 小样本专用）。 | 2026-09-17（17天） | in=3/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/regime/validation/phase2/b1_probability_calibration.py` | B1 概率校准度验证器（12_regime_phase2_validation §2.4）。 | 2026-09-15（19天） | in=5/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/regime/validation/phase2/b4_transition_accuracy.py` | B4 转换触发准确性验证器（12_regime_phase2_validation §2.2，Phase 2 第一批 MVP）. | 2026-09-15（19天） | in=3/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/regime/validation/phase2/confidence_calibrator.py` | 两阶段概率校准器（13_regime_phase3_engineering_plan §2.2 P0-E2）。 | 2026-09-15（19天） | in=1/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |

### 簇 src.zephyr.research（8 台；初判 mount=8）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/research/__init__.py` | MOD-L09-001 Research Innovation Core — 研究创新核心包。 | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/research/auto_feature_discoverer.py` | AutoFeatureDiscoverer — AI 自动特征发现器（MOD-FAC-001）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/research/factor_mining_pipeline.py` | LLM 因子挖掘流水线（GAP-F-43，research 域骨架）。 | 2026-09-02（32天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/research/factor_model_co_evaluator.py` | FactorModelCoEvaluator — 因子模型联合评估器（MOD-FAC-005）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/research/factor_vote_mining.py` | FactorVoteMiner — FactorMAD 多智能体投票因子挖掘（MOD-FAC-004）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/research/gp_strategy_discovery.py` | GpStrategyDiscovery — 遗传规划策略发现器（MOD-FAC-003）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/research/llm_evolutionary_search.py` | LlmEvolutionarySearch — LLM 进化式策略搜索（MOD-FAC-006）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/research/sell_news_event_study.py` | SellNewsEventStudy — 高位利好落地事件研究（利好出尽实证，MOD-RES-001）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |

### 簇 src.zephyr.sell_decision（9 台；初判 mount=9）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/sell_decision/__init__.py` | （无文档头，按文件名语义：__init__） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/sell_decision/_extensions/__init__.py` | sell_decision/_extensions | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/sell_decision/api/__init__.py` | sell_decision/api | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/sell_decision/core/scaling_out_architect.py` | Scaling Out Architect — 分批卖出架构师 (MOD-SELL-017) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/sell_decision/core/sell_strategy_ab_tester.py` | Sell Strategy AB Tester — 卖出策略 AB 测试 (MOD-SELL-011) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/sell_decision/core/strategy_specific_stop_framework.py` | Strategy Specific Stop Framework — 策略特异止损框架 (MOD-SELL-014) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/sell_decision/infrastructure/__init__.py` | sell_decision/infrastructure | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/sell_decision/models/__init__.py` | sell_decision/models | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/sell_decision/services/__init__.py` | sell_decision/services | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |

### 簇 src.zephyr.signal_quality（8 台；初判 dispute=6，mount=2）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/signal_quality/_extensions/__init__.py` | signal_quality/_extensions | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端） ②retire→Owner 门位） |
| `src/zephyr/signal_quality/api/__init__.py` | signal_quality/api | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端） ②retire→Owner 门位） |
| `src/zephyr/signal_quality/core/__init__.py` | signal_quality/core | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端） ②retire→Owner 门位） |
| `src/zephyr/signal_quality/infrastructure/__init__.py` | signal_quality/infrastructure | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端） ②retire→Owner 门位） |
| `src/zephyr/signal_quality/models/__init__.py` | signal_quality/models | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端） ②retire→Owner 门位） |
| `src/zephyr/signal_quality/services/__init__.py` | signal_quality/services | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（原料端） ②retire→Owner 门位） |
| `src/zephyr/signal_quality/signal_dedup.py` | SignalDedup — 信号去重器（MOD-SIGQC-003）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）（活线在身未挂线） |
| `src/zephyr/signal_quality/signal_explainability_guarantor.py` | SignalExplainabilityGuarantor — 信号可解释性强制保障器（MOD-SIGQC-006）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（原料端）（活线在身未挂线） |

### 簇 src.zephyr.simulation（13 台；初判 dispute=6，mount=7）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/simulation/_extensions/__init__.py` | simulation/_extensions | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（模拟段） ②retire→Owner 门位） |
| `src/zephyr/simulation/api/__init__.py` | simulation/api | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（模拟段） ②retire→Owner 门位） |
| `src/zephyr/simulation/core/__init__.py` | simulation/core | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（模拟段） ②retire→Owner 门位） |
| `src/zephyr/simulation/infrastructure/__init__.py` | simulation/infrastructure | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（模拟段） ②retire→Owner 门位） |
| `src/zephyr/simulation/models/__init__.py` | simulation/models | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（模拟段） ②retire→Owner 门位） |
| `src/zephyr/simulation/services/__init__.py` | simulation/services | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→FACTORY（模拟段） ②retire→Owner 门位） |
| `src/zephyr/simulation/divergence_attributor.py` | 回测-实盘偏差四因子归因模块(BM-BT-05-H) | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→FACTORY（模拟段）（活线在身未挂线） |
| `src/zephyr/simulation/implementations/__init__.py` | （无文档头，按文件名语义：__init__） | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→FACTORY（模拟段）（活线在身未挂线） |
| `src/zephyr/simulation/implementations/default_experiment_pipeline.py` | 实验 — Default Experiment Pipeline | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（模拟段）（活线在身未挂线） |
| `src/zephyr/simulation/limit_board_queue.py` | Paper Matching 涨跌停排队引擎(BM-SIM-08) | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→FACTORY（模拟段）（活线在身未挂线） |
| `src/zephyr/simulation/pipeline_base.py` | 实验 — Experimentation Pipeline Layer | 2026-09-16（18天） | in=1/out=0·wired | **mount**→FACTORY（模拟段）（活线在身未挂线） |
| `src/zephyr/simulation/risk_simulator.py` | D_SIMULATION — Risk Simulator (风控仿真器) | 2026-09-16（18天） | in=1/out=0·wired | **mount**→FACTORY（模拟段）（活线在身未挂线） |
| `src/zephyr/simulation/volume_aware_impact.py` | citrusquant volume-aware sqrt impact 形式模块(53号 §3.2 v2.0 候选) | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→FACTORY（模拟段）（活线在身未挂线） |

### 簇 src.zephyr.strategy_factory（7 台；初判 mount=7）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/strategy_factory/__init__.py` | 策略工厂策略卡模块包（S-OWNER 系列卡转译实现）。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/strategy_factory/owner_band_t/intraday_t.py` | 日内做T 臂——纯决策函数（编排见 engine）。 | 2026-09-17（17天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/strategy_factory/owner_band_t/regime_gate.py` | regime 门——读 c1_backtest.regime_snapshot_history（现役判定器 walk-forward 印教材）。 | 2026-09-17（17天） | in=2/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/strategy_factory/owner_band_t/signals.py` | 波段信号面（信号=000300 指数日线）——布林上轨/前高/涨幅分位/波动率分位。 | 2026-09-17（17天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/strategy_factory/owner_band_t/td_sequence.py` | TD 序列（DeMark TD Sequential）自实现——Buy Setup / Buy Countdown / TD 极值。 | 2026-09-17（17天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/strategy_factory/owner_regime_switcher/packages.py` | 代理包信号面（冻结 §3；两包均为简化代理，非可毕业策略）。 | 2026-09-18（16天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/strategy_factory/owner_regime_switcher/switcher.py` | 切换器核心——regime 状态 → (启用包集合, 各包仓位上限系数) 逐日调度表。 | 2026-09-18（16天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
