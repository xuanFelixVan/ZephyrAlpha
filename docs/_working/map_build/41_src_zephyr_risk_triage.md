---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.risk（27 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.risk（27 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=5，wired=14，wired_by_header=7，wired_dynamic=1；初判汇总：dispute=5，mount=22

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/risk/_extensions/__init__.py` | risk/_extensions | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→TDM（交易日夜循环） ②retire→Owner 门位） |
| `src/zephyr/risk/api/__init__.py` | risk/api | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→TDM（交易日夜循环） ②retire→Owner 门位） |
| `src/zephyr/risk/cross_asset/__init__.py` | cross_asset 包初始化。 | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→TDM（交易日夜循环） ②retire→Owner 门位） |
| `src/zephyr/risk/infrastructure/__init__.py` | risk/infrastructure | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→TDM（交易日夜循环） ②retire→Owner 门位） |
| `src/zephyr/risk/services/__init__.py` | risk/services | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→TDM（交易日夜循环） ②retire→Owner 门位） |
| `src/zephyr/risk/atr_stop_engine.py` | ATR Stop Engine — ATR 动态止损与 Bayesian 参数优化 (MOD-RK-35, CAND-RSK-038) | 2026-09-15（19天） | in=1/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/core/backtest_store.py` | Backtest Store — VaR 回测/基线/双轨 P&L/entry_var 持久化门面 (36号 §3.4/§3.13/§3.18) | 2026-09-18（16天） | in=2/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/core/crowding_response_engine.py` | Crowding Response Engine — C-045 拥挤度响应引擎 (MOD-RK-32, MVP) | 2026-09-17（17天） | in=1/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/core/deviation_attribution.py` | D_RISK — 实盘 vs 回测偏离归因分解 H-A~D 四因子（55 号 §6 暂缓项施工）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/core/drawdown_attribution.py` | D_RISK — 回撤类型诊断 + 归因自动化（35 号 memo §6.7/§6.13 施工，§3.12/§3.16 落地）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/core/drawdown_bankruptcy_floor.py` | D_RISK — Static 模式破产底线 Kill Switch 触发源（35 号 memo §6.15 施工，§4.10 部分采纳）。 | 2026-09-17（17天） | in=2/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/core/drawdown_broker_side_stop.py` | D_RISK — L2 平台层 broker 端硬止损（35 号 memo §6.11 施工，§3.5.1 四层架构 L2 落地）。 | 2026-09-17（17天） | in=1/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/core/drawdown_consecutive_loss.py` | D_RISK — 连续亏损降仓触发器（35 号 memo §6.2 施工，§3.5 触发条件表第 3 行）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/core/drawdown_forced_rest.py` | D_RISK — Level 4 强制休息 5 天自动计时器（35 号 memo §6.1 施工，§3.4 落地）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/core/drawdown_session_persistence.py` | D_RISK — 盘前初始化 + 盘后持久化配对编排（35 号 memo §3.15/§3.18/§6.12 施工）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/core/drawdown_tracker.py` | Drawdown Real-Time Tracker — 回撤实时追踪器 (MOD-RK-011) | 2026-08-18（47天） | in=2/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/core/emergency_stop_confirmation.py` | Emergency Stop Confirmation — 紧急停止安全确认 (MOD-RK-36, CAND-RSK-039 / D-RISK-115) | 2026-10-02（2天） | in=1/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/core/fhs_engine.py` | FHS Engine — Filtered Historical Simulation 引擎 (MOD-RK-26, MVP) | 2026-09-15（19天） | in=2/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/core/leverage_risk_model.py` | D_RISK — 杠杆风控模型（CAND-CRYPTO-008，94 号 memo §4.4 杠杆与资金费率）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/core/risk_data_pipeline.py` | Risk Data Pipeline — 风控数据底座 (MOD-RK-25) | 2026-09-17（17天） | in=5/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/core/risk_veto_engine.py` | Risk Veto Engine — 风险否决引擎 (MOD-RK-24) | 2026-09-15（19天） | in=2/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/core/stress_test_engine.py` | Stress Test Engine — 压力测试引擎 (MOD-RK-12) | 2026-09-15（19天） | in=4/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/core/systemic_risk_alert_state_machine.py` | Systemic Risk Alert State Machine — 系统性风险分级预警 5 级状态机 (MOD-RK-34, CAND-RSK-037) | 2026-09-15（19天） | in=1/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/core/var_backtester.py` | VaR/ES Backtester — VaR/ES 模型回测验证器 (MOD-RK-05B, 36号 §3.9 施工) | 2026-09-15（19天） | in=1/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/cross_asset/cross_market_data_adapter/__init__.py` | _cross_layer: Cross-layer integration pipelines for domain blueprints. | 2026-09-18（16天） | in=0/out=0·wired_dynamic | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/cross_asset/cross_market_data_adapter/ml_experiment_pipeline.py` | Re-export from shared SSoT — zephyr.shared._cross_layer.ml_experiment_pipeline | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
| `src/zephyr/risk/hedge_execution_skill.py` | HedgeExecutionSkill — 对冲执行技能（MOD-RK-042）。 | 2026-09-15（19天） | in=1/out=0·wired | **mount**→TDM（交易日夜循环）（活线在身未挂线） |
