---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_e8_assembly —— E8 组装与资金分配（SPM 35 节点）

- 真源: `config/strategy_production_map.yaml`；行号=SPM:L*。
- 职责: 多策略装配线：预算切分、regime 元分配、约束求解、再平衡，产出权重唯一真源。
- 计数: 35 = 1 stage(partial) + 34 mech（built 33 / pending 1）。

## 1. 族内节点全清单

| node_id | 名称 | 状态 | module_ref | 行 |
|---|---|---|---|---|
| FAC-E8 | 组装与资金分配（stage） | partial | MOD-PA-002..004,MOD-PA-006..007,MOD-PA-013..015,MOD-PA-020..024 | SPM:L389 |
| FAC-E8-M-001 | 多策略资金分配件族（E8 装配线） | **pending** | MOD-PA-002..004,MOD-PA-006..007,MOD-PA-013..015,MOD-PA-020..024 | SPM:L4340 |
| FAC-E8-M-002 | 多策略资金分配器 | built | MOD-PA-003 | SPM:L4351 |
| FAC-E8-M-003 | 策略相关性门禁 | built | MOD-PA-004 | SPM:L4362 |
| FAC-E8-M-004 | Regime元分配器 | built | MOD-PA-007 | SPM:L4373 |
| FAC-E8-M-005 | 最大回撤限制分配器 | built | MOD-PA-013 | SPM:L4384 |
| FAC-E8-M-006 | 策略筛选三维评估器 | built | MOD-PA-014 | SPM:L4395 |
| FAC-E8-M-007 | 体制条件BMA信号权重 | built | MOD-PA-015 | SPM:L4406 |
| FAC-E8-M-008 | 前瞻风险预算分配器 | built | MOD-PA-022 | SPM:L4417 |
| FAC-E8-M-009 | 信号合成器（多策略加权投票） | built | MOD-PA-002 | SPM:L4428 |
| FAC-E8-M-010 | 分批建仓引擎 | built | MOD-PA-006 | SPM:L4439 |
| FAC-E8-M-011 | Regime检测器（12态灰度概率） | built | MOD-REGIME-001 | SPM:L4450 |
| FAC-E8-M-012 | 再平衡调度器（四触发源） | built | MOD-PF-003 | SPM:L4482 |
| FAC-E8-M-013 | 波动率目标化仓位计算器 | built | MOD-BT-082 | SPM:L4497 |
| FAC-E8-M-014 | STR 翻译件面板适配器 | built | MOD-BT-196 | SPM:L4509 |
| FAC-E8-M-015 | Regime 特征管道（E8 元分配输入） | built | MOD-REGIME-002 | SPM:L4524 |
| FAC-E8-M-016 | 筹码分布引擎 | built | MOD-REGIME-005 | SPM:L4537 |
| FAC-E8-M-017 | 大盘指数传感器 | built | MOD-REGIME-016 | SPM:L4550 |
| FAC-E8-M-018 | 波动率体制预警 | built | MOD-REGIME-011 | SPM:L4563 |
| FAC-E8-M-019 | 风格体制模型 | built | dir:_domain_regime/style_regime_model | SPM:L4576 |
| FAC-E8-M-020 | 截面特征 | built | dir:_domain_regime/cross_sectional_features | SPM:L4589 |
| FAC-E8-M-021 | 市场预测融合 | built | dir:_domain_regime/market_forecast_fusion | SPM:L4602 |
| FAC-E8-M-022 | 策略引擎（生命周期状态机+四维决策） | built | MOD-PF-001 | SPM:L4615 |
| FAC-E8-M-023 | 组合优化器（风险预算主+均值方差备选） | built | MOD-PF-002 | SPM:L4626 |
| FAC-E8-M-024 | 约束求解器（7 约束链+拥挤检测） | built | MOD-PF-006 | SPM:L4637 |
| FAC-E8-M-025 | 再平衡成本收益分析 | built | dir:_domain_portfolio_core/rebalance_cost_analyzer | SPM:L4648 |
| FAC-E8-M-026 | 策略容量估计器（资金分配输入） | built | dir:_domain_portfolio_core/strategy_capacity_estimator | SPM:L4660 |
| FAC-E8-M-027 | 漏斗组合裁决器 | built | dir:_domain_portfolio_core/funnel_portfolio_adjudicator | SPM:L4672 |
| FAC-E8-M-028 | 敞口管理 | built | dir:_domain_portfolio_core/exposure_manager | SPM:L4683 |
| FAC-E8-M-029 | 策略装配工厂（portfolio_core 内 strategy_factory） | built | dir:_domain_portfolio_core/strategy_factory | SPM:L4695 |
| FAC-E8-M-030 | 权重唯一真源与写图权柄闸 | built | code:scripts/backtest/weight_ssot.py | SPM:L4706 |
| FAC-E8-M-031 | 前瞻概率止损模块 | built | code:src/zephyr/pf_alloc/core/forward_stop_loss.py | SPM:L4717 |
| FAC-E8-M-032 | 前瞻风险预算分配器（PA-022 真身） | built | code:src/zephyr/pf_alloc/core/risk_budget_allocator.py | SPM:L4728 |
| FAC-E8-M-033 | 板块分布比较选优 | built | code:src/zephyr/pf_alloc/core/sector_distribution_comparator.py | SPM:L4739 |
| FAC-E8-M-034 | 尾部对冲信号生成器 | built | code:src/zephyr/pf_alloc/core/tail_hedge_signal.py | SPM:L4751 |

## 2. 接线现状与缺口判定

- 已接线：装配线实体件（M-002~M-034）33 枚 built，含权柄级件——M-030 权重唯一真源与写图权柄闸（weight_ssot）。
- 缺口：**M-001 是"件族级 pending 占位"**——其 module_ref 与 stage 相同（PA-002..024 整族），即"族清单节点"本身 pending 而族内单件多已 built（M-002~M-008）。判定：占位语义，非实体缺口；真实缺口在族间编排（谁在何时调用全族）=not_mined（需运行时证据）。
- 可考性：E8 对应 H9 TDM C 族/F 维的"多策略组合层引擎"缺口带（H9 L4 级缺口）——工厂侧组装件齐、考卷侧 F 维折叠（strategy_pool=["primary"]，H9 §1.8），**组装力与考试力不对称**是本层最大结构性事实。

## 3. 修复建议（一句话）

M-001 占位件族的编排接线（assembly orchestrator）补齐，并作为 T3c/PP-001 整装组合 V0 的工厂侧对接口。

## 4. 交叉验证

- TDM C 族（st_c_portfolio）：TDM-F-C1 预算切分 mounts=MOD-PA-006/013（TDM:L4114）与 E8-M-010/M-005 同件；TDM-F-C3-03 sleeve权重调权 mounts=MOD-PA-015（TDM:L4450）=E8-M-007——两图在 E8 短路互链，交叉验证一致。
- H9 §1.8/§2 L4：多策略组合层引擎缺口（F 维全开+PP-001 八 sleeve）——E8 是现成蓝图侧（PP-001 在 TDM portfolio_plan，TDM:L6081 区）。
- chief 02 §6：commit_queue_interactive 出厂翻转等 Owner 门位不涉本层；PP-001 sleeves 内容属 Owner 资金门位（H9 S4 同判），本册不代裁。
