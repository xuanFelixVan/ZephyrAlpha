---
ttl: permanent
doc_type: architecture_view
title: 多因子策略细节
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.13.5"
date: 2026-08-15
last_updated: 2026-08-15
topic: multifactor_strategy_detail
scope: 07_trading_decision_architecture
---

> ## 结案报告（AI-NIGHT-001 复核 2026-08-19）
>
> **实际开发**：因子工坊 65 production 模块实证——multifactor_synthesis.py（等权/IC 加权/回归三方法+统一入口）/ ic_ir_calc / ic_ir_evaluator / correlation_dedup / layered_backtest / three_level_judgment / decay_monitor（半衰期层）/ factor_attribution / factor_optimization / factor_dag + 双执行器；治理链 factor_pool_manager（n_max=64/active=60/dormant=4）/ lifecycle_state_machine（8 态）/ abs001_gate / grayscale_rollout / six_step_flow；组合优化 portfolio_optimizer + constraint_solver（MOD-PF-002/006）；factor_registry.yaml 111 条目。
>
> **最终成果**：多因子策略细节定稿（active v1.13.5）——6 项讨论要点 + §3.7 八项编排算法形式化 + Phase 4.1-4.20 远期候选栈；"已建代码的 why 定型"闭环。
>
> **未做事项及原因**：① §3.7 八项编排算法全部未落码（grep 实证零命中）——SynthesisDegradationChain / ConstraintArbitration / DecayActionLifecycle（6 态）/ SimpleFactorAttribution / CrowdingRealTimeMonitor / RebalanceTrigger（含 Inaction Cost）/ MultifactorPITBacktestFramework / HoldingDriftMonitor，文档标"MVP 即做/首批回测前必做"未排期；② Mask-First tradability mask 未施工（~40 行，MVP 即做项）；③ CUSUM 预警层 + "连续 40 日 |IC|<0.02→休眠"自动淘汰层未施工（decay_monitor 现仅半衰期，§3.3 代码现状注记确认）；④ C1-C7 策略级约束链 ↔ MOD-PF-006 代码约束链对齐未施工（CTR-003 RiskLimits 注入，上线前项）；⑤ 6 态↔registry 5 态映射规则未定义（随 ③ 落码时回写 62 号）；⑥ Phase 4.1-4.20 ML 合成/组合/风控栈、BM-SEL-02-E LLM 语义去重、BM-SEL-02-M 因果验证、BM-RC-06-D 三深度增强均为远期登记。

> ## 结案报告回填（2026-08-28 代码实证复核）
> 原"§3.7 八项编排算法未落码/缺口①②④"已过时，八项全部落码：factor/analysis/ 下 multifactor_degradation_chain.py（#1）、multifactor_decay_lifecycle.py（#3 DecayActionLifecycle 6 态）、simple_factor_attribution.py（#4）、multifactor_crowding_monitor.py（#5）、multifactor_pit_backtest.py（#7）、multifactor_tradability_mask.py（Mask-First）；pf_core/core/ 下 multifactor_constraint_arbitration.py（#2，C1-C7↔CTR-003 对齐）、multifactor_rebalance_trigger.py（#6）、multifactor_holding_drift_monitor.py（#8）。
> **仍真实未完工**：CUSUM 独立预警层未见（部分并入 decay_lifecycle）；Phase 4.1-4.20 ML 栈远期登记。

# 多因子策略细节

> **性质**：已定型（active）。由 [00_index_trading_decision](00_index_trading_decision.md) G09 主题组派生，6 项讨论要点已逐项对齐落入 §3 决策。
> **施工图纪律**：本文档定型后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。因子工坊 BM-SEL-02 及 D_FACTOR 域 65 个 production 模块已建，本文档是"已建代码的 why 定型"，非"待施工设计"。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G09 多因子策略细节 |
| 所属 | 作战地图 05（BM-SEL-02 因子计算/注册表/IC-IR/衰减/合成/治理） |
| 依赖 | G04（[20_first_batch_strategies](20_first_batch_strategies.md) §2.3 多因子 sleeve）、G05（信号工坊）、G01（[15_data_feature_layer_spec](15_data_feature_layer_spec.md) 因子工程总纲，status: draft） |
| 对标 | WorldQuant Alpha 工厂 / Numerai 多因子 / 华泰金工多因子 / BigQuant ICIR 加权合成（2026-07） |
| 正交 | ✅ 与 regime 正交（[28 §3.4]）：多因子不读情绪周期，不读 regime，纯横截面选股 |
| 优先级 | P2（承载主力资金的低频基石） |
| 状态 | active 1.13.5（6 项讨论要点已对齐 §3.1-§3.6 + §3.7 施工算法 8 项补全（合成降级链/约束冲突仲裁/衰减动作生命周期 6 态/MVP 归因/拥挤实时监控/换仓触发+Inaction Cost/PIT 回测框架/持仓偏差监控）+ §2.4 设施盘点 + Phase 4.1-4.20 远期候选栈 20 子项——逐项明细见 §8 修订记录） |

## 2. 背景

### 2.1 项目处境

ZephyrAlpha 是个人 + 100% AI 开发的 A 股量化交易系统。首手 3 策略（打板/多因子/事件驱动）已在 [20 §2.2-2.4] 定义为差异化 sleeve。多因子 sleeve 定位为"低换手、大容量、横截面选股的压舱石 sleeve"，承载主力资金。

因子工坊 BM-SEL-02（因子计算/注册表/IC-IR 评估/衰减监控/多因子合成/治理生命周期）及 D_FACTOR 域 65 个 production 模块（[46_d_factor.md]）均已 production，但缺乏"多因子策略如何组合这些能力"的 why 文档。本文档补齐这一缺口，并将 6 项开放讨论要点落定。

### 2.2 核心问题

1. **因子如何组合**——单因子 IC 各异、相关性不同，需选择合成方式（等权/IC 加权/正交化/回归优化）以最大化合成因子 IR。
2. **行业中性化在哪一层做**——因子层中性化会损失信号，组合约束层中性化保留因子信号但控制暴露，需选择。
3. **因子衰减如何监控**——A 股因子衰减速度快于美股（laoyulaoyu 2026-06 实证），需半衰期监控 + CUSUM 预警 + 自动淘汰。
4. **多因子换手率与容量**——低换手（3-5 天 convergence）、大容量（承载主力资金），与打板 sleeve 形成差异化。

### 2.3 约束条件

- **因子池容量**：N_max ≤ 64（运行上限），活跃池 ≤ 60，休眠池 ≤ 4（`factor_pool_manager.py` ADR-FAC-006 + `governance/_config.yaml`，v1.13.0 源码校正——此前误写活跃 ≤30/休眠 ≤8）；[30 §5] 待裁定：个人系统实际活跃 8-15 个因子足够，多了是过拟合温床（池容量是运行上限，非目标持仓因子数）
- **PIT 铁律**：INV-004——合成仅使用同期因子值，IC 加权权重来自历史 IC（不引入未来函数）；因子回测必须 AS OF JOIN，禁止 lookahead bias
- **T+1 结算**：同打板，但多因子换手低，T+1 影响小
- **低换手**：convergence_window = 3-5 天（[30 §6.4]），Tier 1+2 给时间达，Tier 3 兜底防死扛（[30 §2.4]）
- **不读 regime/情绪周期**：纯横截面选股；市场状态适配"由 PerformanceScore 后验捕获（[20 §2.3]）"

### 2.4 已施工设施盘点（v1.13.0 新增，通用规则 #11）

> 盘点多因子策略相关的全部已建设施（截至 2026-08-12 源码 + [46_d_factor](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/02_domain_architecture_docs/46_d_factor.md) 实证：D_FACTOR 域 66 模块 = 65 production + 1 design），明确"有什么"→"改什么"→"退役什么"。

**因子计算与评估（src/zephyr/factor/）**：

| 设施 | 路径 | MOD/域 ID | 状态 | 与本策略的关系 |
|---|---|---|---|---|
| 多因子合成 | [multifactor_synthesis.py](file:///d:/ZephyrAlpha/src/zephyr/factor/analysis/multifactor_synthesis.py) | MOD-L02-011 / D-FACTOR-ANA-10 | ✅ production | §3.1 三方法（等权/IC 加权 w/Σ\|w\| 归一化负 IC 自动反向/回归 OLS lstsq）+ `synthesize` 统一入口，各方法失败自动退化等权；默认 ic_weighted（analysis/_config.yaml） |
| IC/IR 批量计算 | `analysis/ic_ir_calc.py` | D-FACTOR-ANA-01 | ✅ production | §3.1 IC 加权权重的数据来源 |
| 多因子评估报告 | `analysis/ic_ir_evaluator.py` | D-FACTOR-ANA-02 | ✅ production | 因子准入评估 |
| 相关性去重 | `analysis/correlation_dedup.py` | D-FACTOR-ANA-05 | ✅ production | §3.1 正交化不实现的前提（因子筛选期已控相关性） |
| 分层回测 | `analysis/layered_backtest.py` | D-FACTOR-ANA-06 | ✅ production | 5 分位单调性验证 |
| 三级判定 | `analysis/three_level_judgment.py` | D-FACTOR-ANA-07 | ✅ production | excellent_ic=0.1 / pass_ic=0.05（_config.yaml） |
| 衰减监控 | `analysis/decay_monitor.py` | MOD-L02-009 / D-FACTOR-ANA-08 | ⚠️ production 但仅半衰期 | §3.3 第一层；**CUSUM 层 + 自动淘汰层未实现**（决策待落码） |
| 因子归因 | `analysis/factor_attribution.py` | D-FACTOR-ANA-09 | ✅ production | 按月时间归因；§3.7#4 的 Brinson 式因子 PnL 分解待落码 |
| 因子优化 | `analysis/factor_optimization.py` | D-FACTOR-ANA-11 | ✅ production | 合成权重优化（max_ir 目标） |
| 因子 DAG | `core/factor_dag/dag.py` + `core/dag_manager/executor.py` | D-FACTOR-04 | ✅ production | 依赖拓扑 + 双模调度（盘前全量/盘中增量） |

**因子治理（src/zephyr/factor/governance/）**：

| 设施 | MOD/域 ID | 状态 | 关键参数（_config.yaml 实证） |
|---|---|---|---|
| 因子池管理 `factor_pool_manager.py` | MOD-L02-018 / D-FACTOR-08 | ✅ production | ADR-FAC-006：n_max=64 / active=60 / dormant=4 / min_ic_to_enter=0.02（入池门槛，非休眠淘汰） |
| 生命周期状态机 `lifecycle_state_machine.py` | D-FACTOR-GOV-01 | ✅ production | 8 态：research→development→backtest→paper→grayscale→production→deprecated→retired |
| ABS001 上线门禁 `abs001_gate.py` | D-FACTOR-GOV-02 | ✅ production | min_ic=0.03 / min_ir=0.5 / min_oos_rate=0.5 |
| 灰度发布 `grayscale_rollout.py` | D-FACTOR-GOV-03 | ✅ production | 阶梯 10%→30%→100% |
| 六步流程 `six_step_flow.py` + 治理引擎 `engine.py` | D-FACTOR-GOV-04/05 | ✅ production | 状态转换编排 |

**组合优化（src/zephyr/pf_core/，D_PF_CORE 域）**：

| 设施 | MOD ID | 状态 | 与本策略的关系 |
|---|---|---|---|
| 组合优化器 `portfolio_optimizer.py` | MOD-PF-002 | ✅ production | 风险预算（MOD-RK-08）+ Kelly 截断（只减不增）+ 约束求解 → TargetPortfolio（CTR-007） |
| 约束求解器 `constraint_solver.py` | MOD-PF-006 | ✅ production | 代码侧 7 约束：行业绝对≤30%/行业相对±10%/市值暴露/MDD≤5%/相关性≤0.7/风格±0.3σ/仓位上限 + 拥挤检测——**与 §3.5 C1-C7 策略级参数不一致**（对齐缺口 §6 待裁定） |

**注册表 / battle_map**：

| 设施 | 路径 | 状态 |
|---|---|---|
| 因子注册表 | [factor_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml)（REG-FCT-001） | ✅ active v1.0.0，111 条目（62 号 §3）；status 枚举 candidate/experimental/active/deprecated/retired（与 §3.7#3 运行时 6 态映射缺口见 §6 待裁定） |
| 因子工坊 | battle_map_05 BM-SEL-02（+ 子环节 A-M，M 因果验证层为设计态） | ✅ production |

**§3.7 八项施工算法落码状态**（全部为本文档形式化伪代码，grep 实证未落码，禁止误判为已建）：#1 SynthesisDegradationChain ❌ / #2 ConstraintArbitration ❌ / #3 DecayActionLifecycle（6 态）❌ / #4 SimpleFactorAttribution ❌ / #5 CrowdingRealTimeMonitor ❌ / #6 RebalanceTrigger（含 Inaction Cost）❌ / #7 MultifactorPITBacktestFramework ❌ / #8 HoldingDriftMonitor ❌。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-SEL-02-A | 因子计算引擎 | §2.4（`core/factor_dag/dag.py` + `dag_manager/executor.py` 依赖拓扑+双执行器，D-FACTOR-04） | production已建 |
| BM-SEL-02-B | 因子注册表与池管理 | §2.4（factor_registry.yaml REG-FCT-001 111 条目 + `factor_pool_manager.py` ADR-FAC-006 n_max=64/active=60/dormant=4） | production已建 |
| BM-SEL-02-C | 因子管线双模调度 | §2.4（因子 DAG 行：双模调度——盘前全量/盘中增量） | production已建 |
| BM-SEL-02-D | 因子评估-IC/IR体系 | §2.4（`ic_ir_calc.py` ANA-01 / `ic_ir_evaluator.py` ANA-02 / `three_level_judgment.py` ANA-07 / `layered_backtest.py` ANA-06） | production已建 |
| BM-SEL-02-I | 因子治理-生命周期与门禁 | §2.4 因子治理表（lifecycle_state_machine 8 态 + abs001_gate 上线门禁 + grayscale_rollout 阶梯 + six_step_flow/engine 编排） | production已建 |

## 3. 决策

### 3.1 讨论要点①：因子组合方式（打分→IC 加权/正交化）

**裁定**：采用 IC 加权（`synthesize_ic_weighted`）为默认合成方法，等权（`synthesize_equal_weight`）为降级兜底，回归优化（`synthesize_regression`）为可选增强。**正交化不实现**（当前规模不需要）。三种合成方法已在 `multifactor_synthesis.py`（MOD-L02-011，D-FACTOR-ANA-10）全部 production。

| 合成方法 | 实现 | 适用场景 | 降级条件 |
|---|---|---|---|
| 等权 `synthesize_equal_weight` | `panel.mean(axis=1)` | 冷启动 IC 数据不足/兜底 | 默认降级目标 |
| IC 加权 `synthesize_ic_weighted` | 按 IC 均值归一化权重 `w/Σ|w|` | **默认方法**，IC 数据≥20 时 | IC 权重不均匀配裸等权兜底 |
| 回归优化 `synthesize_regression` | OLS `np.linalg.lstsq(X, y)` | 因子数多、前瞻收益数据充足 | 数据不足/矩阵奇异→等权兜底 |

**IC 加权细节**：权重来自因子最近 N 期（默认 60 交易日）的截面 Rank IC 均值，按 `w_i = IC_i / Σ|IC_j|` 归一化。负 IC 因子自动反向。IC 衰减至 |IC| < 0.02 时因子进入休眠池（`factor_pool_manager.py`）。

**正交化不实现理由**：当前因子池 ≤30 个，因子间相关性已通过因子筛选阶段控制（D_FACTOR 域因子工程时已做相关性清洗），正交化在当前规模下收益小于实现成本。远期因子池扩张到 50+ 时重新评估。

**A 股 XGBoost+TreeSHAP 实证背书（v1.12.4 补）**：[arXiv:2606.12843](https://arxiv.org/abs/2606.12843)（Han et al. 2026-06，3,632 只 A 股 2009-2019）——rank IC=0.119、ICIR=1.12（t=8.26）、+2.38%/月 long-short（年化 Sharpe 2.23）、Carhart alpha +2.31%/月；**行为因子（换手率+动量）贡献 58.2% vs 估值因子 10.7%**。启示：① 验证 IC 加权在 A 股有效 ② 支持因子池以技术/动量因子为主 ③ 为 Phase 4.5 KTD-Fin Barra 归因提供 A 股实证基础。

> **BM-SEL-02-E LLM 语义去重处置裁定（v1.13.2 补）**：
> - **定位**：BM-SEL-02-E（因子评估-相关性与语义去重，L1）含两支——数值相关性去重（`analysis/correlation_dedup.py`，D-FACTOR-ANA-05，✅ production，数值相关性 >0.85 丢弃）+ LLM 语义去重（作战地图 trigger"逻辑等价→保留 IC 高者"，未建）。
> - **裁定**：LLM 语义去重一支**登记远期候选，当前不施工**。理由：① 数值相关性去重已 production 且当前因子池规模（≤64）下够用；② 与 21 号 §5.4"LLM 不进入在线路径、只做离线研发"边界一致；③ 作战地图已内建降级路径（"LLM 不可用→仅数值去重"）——**现状即降级态运行**，无断裂。
> - **契约（远期候选登记）**：相关矩阵→聚类→LLM 语义等价判断→逻辑等价时保留 IC 高者，输出=去重后因子集+语义冗余标记，下游=BM-SEL-02-F 分层回测。
> - **重评条件**：因子池扩张到 50+（与正交化重评同门槛）且出现"数值低相关但逻辑同构"的伪异质因子实例 ≥2 例时激活。
>
> **BM-SEL-02-M 因果因子验证层（DoWhy/DML）处置裁定（v1.13.2 补）**：
> - **定位**：BM-SEL-02-M（L1，MOD-SIG-054 `causal_factor_validator.py` planned）——新因子入库前+盘前全量评估时做因果验证，区分相关因子 vs 因果因子→因果因子加权提升。
> - **裁定**：**登记远期 Phase 4，当前不施工**。关键消歧——#ARCH-OE-009 裁剪的是 **BM-MT-04 因子发现与因果发现（PC/LiNGAM/时滞因果图）**（模型训练域），**本环节（BM-SEL-02-M，选股域因子入库前 DoWhy/DML 因果验证）未被裁剪**，两者域不同、工具链不同。与 [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) §0.6.10 发现 2（Bloomberg Causal-TS 库评估）呼应——因果工具链登记远期。
> - **契约（远期登记）**：候选因子+L2-D 预计算因果图→DoWhy/DML 因果验证→因果因子加权→因子池；降级=因果图未就绪→仅统计评估（IC/IR）——**现状即降级态**。
> - **重评条件（激活门槛）**：因子库出现**伪相关惨案 ≥1 例**（入库因子被实证实为伪相关/数据挖掘产物并造成实亏）→ 激活施工评估。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-SEL-02-H | 多因子合成与优化 | §3.1（IC 加权默认/等权降级兜底/回归可选三方法 `synthesize` 统一入口 + `factor_optimization.py` max_ir 合成权重优化，ANA-10/ANA-11） | production已建 |

### 3.2 讨论要点②：行业中性化层级

**裁定**：在**组合约束层**做行业中性化（约束 C2），不在因子层做。

**理由**：因子层中性化会损失因子信号（某些因子本就含行业 alpha——如银行 PB 低是行业特征非错误暴露）。组合约束层通过行业暴露约束保留因子信号同时控制行业偏离。

**施工**：`portfolio_optimizer.py`（MOD-PF-002，D_PF_CORE 域，v1.13.0 校正 MOD ID——此前误写 MOD-L02-012）约束链 C2 行业暴露约束——单行业暴露 ≤ ±5%（相对基准），7 约束链的一部分。**代码现状注记**：`constraint_solver.py`（MOD-PF-006）当前实现的行业约束为绝对 ≤30% / 相对 ±10%，与本节裁定 ±5% 不一致——±5% 是多因子 sleeve 的策略级决策，严于基础设施默认，施工对齐缺口见 §6 待裁定。

### 3.3 讨论要点③：因子衰减监控

**裁定**：三层衰减监控——半衰期追踪 + CUSUM 预警 + 自动淘汰。

| 层级 | 机制 | 阈值 | 动作 |
|---|---|---|---|
| 半衰期追踪 | 滚动 60 日 IC 衰减拟合 `IC(t) = IC_0 * exp(-λt)` | 半衰期 < 20 交易日 | 标记"快速衰减"，降低权重 50% |
| CUSUM 预警 | 累积 IC 偏移 `S_t = max(0, S_{t-1} + (IC_t - μ_IC - k))` | S_t > h（k=0.5σ, h=4σ） | 触发衰减预警，进入观察池 |
| 自动淘汰 | 连续 40 交易日 |IC| < 0.02 | 衰减至噪声级 | 移入休眠池，停止参与合成 |

**施工**：`decay_monitor.py`（MOD-L02-009，D-FACTOR-ANA-08，v1.13.0 校正——此前误写 `factor_decay_monitor.py` MOD-L02-013/ANA-11）已 production。**代码现状注记（v1.13.0 源码实证）**：当前仅实现**半衰期监控**（`min_half_life=10`，`analysis/_config.yaml`），**CUSUM 预警层与"连续 40 日 |IC|<0.02→休眠"自动淘汰层在代码中不存在**——二者是本文档决策，随 §3.7#3 DecayActionLifecycle 一并落码；`factor_pool_manager.py` 的 `min_ic_to_enter=0.02` 是入池门槛，非休眠淘汰逻辑。上表三层阈值为决策目标态，非代码现状。

**A 股因子衰减实证**（laoyulaoyu 2026-06）：A 股因子半衰期约 15-25 交易日（美股 30-50），需更激进的监控。Hyperbolic 衰减模型 α(t) = K/(1+λt)（博弈论 Nash 均衡推导）比指数衰减更贴合 A 股因子衰减曲线——远期校准时考虑替换指数衰减拟合。

**信号衰减双时标框架（v1.13.1 补，Alphanume 2026-06）**：① **intra-signal horizon decay**（单次观测预测力随时间消散，半衰期与换仓频率错配是最常见实施错误）② **secular alpha decay**（信号被市场学习/拥挤后的长期 alpha 侵蚀，McLean-Pontiff：发表后衰减 58%）。实证本文档正交分工：§3.3 半衰期监控管时标①（→convergence_window 3-5 天的依据），§3.7#5 拥挤监控管时标②（崩盘尾部风险）。gs-quant 2026-07 确认指数拟合+滚动窗口交叉检验为行业标准（与 `ic_decay.py` 同构）。

**Hyperbolic 衰减完整实证（v1.12.4 补）**：[arXiv:2512.11913](https://arxiv.org/abs/2512.11913)（Lee 2025-12 KAIST，8 个 Fama-French 因子 1963-2024）——① **动量因子 hyperbolic 衰减 R²=0.65**，优于线性（0.51）和指数（0.61）；② **机械因子（动量/反转）符合模型，判断因子（价值/质量）不符合**（与 Hua & Sun"进入壁垒"分类一致）；③ 2015 后拥挤加速，样本外高估剩余 alpha（0.30 vs 0.15），与因子 ETF 增长负相关（ρ=-0.63）；④ 基于拥挤的因子选择无法产生 alpha（Sharpe 0.22 vs 因子动量基准 0.39）；⑤ **拥挤预测尾部风险**：样本外拥挤的反转因子崩溃概率高 1.7-1.8 倍，拥挤的动量因子崩溃风险低（0.38 倍，p=0.006）。启示：① Hyperbolic 拟合优先用于机械因子，判断因子用指数衰减即可 ② CUSUM 衰减监控应联动尾部风险预警 ③ 因子 ETF 增长是拥挤加速代理变量（Phase 4.7 Alpha-R1 可用作输入）。

**A 股高频因子 2026 实证（v1.12.6 补，国泰海通 2026-08-10 周报）**：行为/微结构因子全面领先——开盘后买入意愿强度 16.29% / 日内下行波动占比 14.94% / 日内高频偏度 14.53% / 尾盘成交占比 13.58% / 开盘后买入意愿占比 12.60% / 日内收益 7.75%（2026 年多空收益）。**多粒度模型**（5 日标签）多空 28.18%、多头超额 8.43%；（10 日标签）多空 25.52%、多头超额 6.67%。启示：① 验证 §3.1 行为因子>估值因子结论 ② 多粒度 28% 多空验证 Phase 4.4 STAR CrossAttention 混频融合方向的 A 股有效性 ③ 日内微结构因子可与打板 sleeve §3.9 竞价三维体系跨 sleeve 复用。

**A 股因子拥挤崩盘 2026 实证（v1.12.6 补，中国基金报 2026-08）**：2026-07 A 股科技板块骤跌，**57 只主动量化基金单月净值跌幅超 20%**，15 只超 30%——根因是动量/景气因子拥挤+风格极致切换时模型信号滞后；8 月初 5 日修复反弹超 10%；工银量化策略逆市上涨 8.46%（质量价值均衡配置）。启示：① 即 §3.3"拥挤预测崩溃 1.7-1.8x"的 A 股实时验证 ② **因子拥挤实时监控是 MVP 必做项**（§3.7#5）③ 验证 §3.5 C2 行业暴露约束的价值——单行业拥挤是崩盘放大器。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-SEL-02-G | 因子衰减监控与归因 | §3.3（三层衰减监控：半衰期追踪/CUSUM 预警/自动淘汰，`decay_monitor.py` ANA-08 + `factor_attribution.py` ANA-09 归因；CUSUM 层+自动淘汰层落码缺口登记 §6） | production已建 |

### 3.4 讨论要点④：多因子换手率与容量

**裁定**：convergence_window = 3-5 天，低换手，大容量。

| 维度 | 参数 | 依据 |
|---|---|---|
| convergence_window | 3-5 天 | [30 §6.4] Tier 1+2 给时间达 |
| sleeve 容量 | 500 万-2000 万（待实盘校准） | 横截面选股流动性远好于打板 |
| 持仓数 | 30-80 只 | 分散度 + 单票 ≤2% NAV（C12） |
| 换手率 | 日均 15-25% | convergence_window 3-5 天决定 |

**与打板 sleeve 差异化**：打板高换手（convergence 1-2 天）、小容量（50-200 万）、持仓 1-3 天；多因子低换手（3-5 天）、大容量（500-2000 万）、持仓 5-20 天。两者相关性低，构成差异化 sleeve 组合。

### 3.5 讨论要点⑤：合成后组合优化

**裁定**：合成因子分→组合优化器（7 约束链 C1/C2），输出目标持仓。

**7 约束链**（策略级决策；代码载体 `portfolio_optimizer.py` MOD-PF-002 + `constraint_solver.py` MOD-PF-006，D_PF_CORE 域，production——v1.13.0 校正 MOD ID，此前误写 MOD-L02-012）：

| 约束 | 内容 | 参数 |
|---|---|---|
| C1 单票上限 | 单票 ≤ 2% NAV | position_sizing_engine C12 |
| C2 行业暴露 | 单行业 ≤ ±5% | 申万一级 |
| C3 波动率 | 组合年化波动 ≤ 25% | 滚动 60 日 |
| C4 换手率 | 日均换手 ≤ 30% | convergence 约束 |
| C5 流动性 | 单票≤日成交 5% | C6/C11 容量约束 |
| C6 因子暴露 | 合成因子暴露 ≤ 指数 ±10% | 跟踪误差控制 |
| C7 最小持仓 | ≥ 20 只 | 分散度底线 |

**优化目标**：最大化合成因子分 × 因子暴露（C6 约束下），即 `max Σ(w_i * score_i)` s.t. 7 约束链。

> **代码现状注记（v1.13.0 源码实证）**：`constraint_solver.py`（MOD-PF-006）当前实现的 7 约束为**行业绝对 ≤30% / 行业相对 ±10% / 市值暴露 ≤±0.3σ / MDD≤5% / 相关性 ≤0.7 / 风格暴露 ≤±0.3σ / 仓位上限**（+拥挤检测 ρ>0.8 减半、ρ>0.9 留一），与上表 C1-C7 策略级参数（单票 2%/行业 ±5%/波动 25%/换手 30%/流动性 5%/因子暴露 ±10%/≥20 只）**不一致**——上表是多因子 sleeve 的策略级决策目标态，经 CTR-003 RiskLimits 注入约束求解器，参数对齐施工缺口见 §6 待裁定。

### 3.6 讨论要点⑥：多因子×事件驱动相关性

**裁定**：多因子与事件驱动 sleeve 正交设计（不读情绪/不读 regime），相关性由 PerformanceScore 后验捕获。G07 相关性验证施工前必做（[23_strategy_correlation_validation](23_strategy_correlation_validation.md) §3.1，v1.13.0 校正错链——此前误引 [28 §3.5]），若相关性 >0.6 需重新审视策略组合（战略级阈值；运营级门禁 0.85/0.90 由 MOD-PA-004 执行，见 23 号 §2.3 分层）。

### 3.7 施工算法 8 项缺失补全（v1.12.5+v1.12.6+v1.12.7 新增，第四+五+六轮施工算法深度审查）

> 25 号因子工坊 65 个 production 模块已建，但"因子→合成→优化→仓位→风控→归因"环节间的**编排决策算法**未形式化。本节补全 8 项真实缺口（4 高+4 中），不新增模块，仅形式化编排逻辑，完整覆盖"因子→合成→优化→换仓→衰减→拥挤→归因→回测→偏差监控"九环节闭环。全部 8 项 grep 实证未落码（§2.4 落码状态表）。

#### 缺失#1：合成降级链决策算法（高优先级，合成方法编排断裂点）

**问题**：§3.1 三种合成方法已 production，但"何时降级"的触发条件与降级路径未形式化，缺统一降级编排。

**SynthesisDegradationChain 参数**（降级链：回归优化 → IC 加权 → 等权兜底；与 §3.3 衰减监控联动）：

| 参数 | 值 | 含义 |
|---|---|---|
| ic_min_samples | 20 | IC 样本<20→IC 加权不可靠→降级等权 |
| ic_weight_concentration | 0.70 | 单因子 IC 权重>70%→过度集中→降级等权 |
| ic_abs_floor | 0.02 | 全池 \|IC\|<0.02→信号衰竭→降级等权 |
| regression_min_obs | 120 | 前瞻收益观测<120→回归过拟合→降级 IC 加权 |
| condition_number_max | 50.0 | 因子矩阵条件数>50→共线性→降级 IC 加权 |

**决策逻辑**（`decide(factor_panel, ic_history, forward_returns)`）：① 回归可行性（最高优先级）：`forward_returns≥120` 且条件数 `<50`→`synthesize_regression`；条件数 `≥50`→降级 IC 加权。② IC 加权（默认）：样本 `≥20` 时——全池 |IC| 均值 `<0.02`→等权（信号衰竭）；权重集中度 `>70%`→等权；否则 IC 加权。③ 样本 `<20`→等权兜底。

> **施工建议**：`multifactor_synthesis.py` 增加统一入口 `synthesize_with_degradation()`，内部调用 `decide()` 后分派到 3 个 production 方法。纯增量 ~30 行，不替换现有方法。

#### 缺失#2：7 约束链冲突仲裁算法（高优先级，组合优化器约束编排断裂点）

**问题**：§3.5 的 7 约束链缺**硬/软分级与冲突仲裁**——如 C1 单票≤2% 与 C7 最小 20 只在 universe<50 时难以同时满足，cvxpy 可能返回不可行解或静默放宽。

**ConstraintArbitration 参数**：

| 参数 | 值 | 含义 |
|---|---|---|
| HARD | {C1 单票≤2% NAV, C5 单票≤日成交5%, C7 ≥20只} | 硬约束（违反=不可行，必须满足） |
| SOFT | {C2 行业≤±5%, C3 波动率≤25%, C4 换手≤30%, C6 因子暴露≤±10%} | 软约束（违反=次优，记录但接受，cvxpy 加松弛变量） |
| soft_penalty_weight | 100.0 | 软约束松弛惩罚权重 |
| max_universe_shrink | 5 | 硬约束不可行时最多剔 5 只标的重解 |

**决策逻辑**（`arbitrate(optimizer_result, universe_size)`）：① 无违反→`FEASIBLE/ACCEPT`；② 仅软约束违反→`SOFT_VIOLATION/ACCEPT_WITH_PENALTY`（加松弛接受次优）；③ 硬约束违反且 `universe_size-5≥20`（C7 下限）→`HARD_INFEASIBLE/SHRINK_UNIVERSE` 剔 5 只重解；④ 硬约束违反且 universe 不可缩→`REDUCE_GROSS` 总仓位降至 80% 保硬约束。

> **施工建议**：`portfolio_optimizer.py` 求解后增加 `arbitrate()` 后处理层。纯增量 ~40 行。

#### 缺失#3：因子衰减→动作全生命周期算法（中优先级，衰减监控→池管理编排断裂点）

**问题**：§3.3 三层衰减监控（`decay_monitor.py`）与池管理（`factor_pool_manager.py`）各自独立，缺"检测到衰减后降权/观察/淘汰/复激活"的统一动作状态机。

**DecayActionLifecycle——6 态状态机**（v1.12.5 原 4 态 ACTIVE→OBSERVE→DORMANT→RECOVERY；v1.12.9 补 NEW 冷启动+RETIRED 永久退役两边界态）：

| 参数 | 值 | 含义 |
|---|---|---|
| halflife_observe | 20 | 半衰期<20→OBSERVE |
| cusum_alert_to_dormant | 40 | CUSUM 预警后 40 交易日无恢复→DORMANT |
| ic_floor_dormant | 40 | 连续 40 日 \|IC\|<0.02→DORMANT |
| recovery_ic_threshold | 0.03 | DORMANT 后连续 10 日 \|IC\|>0.03→RECOVERY |
| recovery_observe_days | 10 | 复激活观察期 |
| ic_dormant_floor | 0.02 | \|IC\|<0.02 持续→DORMANT |
| dormant_skip_synthesis | True | DORMANT 因子不参与合成 |
| new_factor_warmup_days | 20 | 新因子冷启动期（IC 样本积累） |
| new_factor_weight_mult | 0.3 | 冷启动期权重乘子（低权重试运行） |
| dormant_max_days | 120 | DORMANT 持续 120 日无恢复→永久退役 |
| retired_skip_all | True | RETIRED 完全退出（不参与合成+不占池配额） |

**状态转移**（`transition_with_boundaries()`）：
- **NEW**（`init_new_factor()` 初始化，0.3 权重试运行）：冷启动满 20 日且 |IC|≥0.02→ACTIVE（1.0）；满 20 日但 |IC|<0.02→OBSERVE（0.5）；未满→保持 NEW。
- **ACTIVE**：半衰期<20→OBSERVE（降权 0.5）；否则保持（1.0）。
- **OBSERVE**：|IC|<0.02 且在态≥40 日→DORMANT（0.0）；半衰期恢复≥20 且 CUSUM 未预警→ACTIVE（1.0）；否则观察中（0.5）。
- **DORMANT**：|IC|≥0.03 持续 10 日→RECOVERY（0.3）；持续≥120 日无恢复→**RETIRED**（`check_retirement()` 执行清理：移出活跃/休眠池、factor_registry 标 status=retired、释放池配额）；否则休眠中（0.0）。
- **RECOVERY**：半衰期≥20→ACTIVE（1.0）；|IC|<0.02→DORMANT（0.0）；否则复激活观察中（0.3）。

> **施工建议**：`factor_pool_manager.py` 增加因子状态字段 `decay_state`，每日调用 `transition_with_boundaries()` 更新状态+权重乘子；新因子入池调 `init_new_factor()`；DORMANT 因子每日调 `check_retirement()`。纯增量 ~50 行（+v1.12.9 边界 ~30 行），与 `decay_monitor.py` 输出对接。

#### 缺失#4：MVP 因子归因算法（中优先级，归因断裂点——Phase 4.5 Barra 前的过渡方案）

**问题**：Barra 归因列为 Phase 4.5 远期候选，但 MVP 阶段即需因子归因验证 §3.3 衰减监控的因子贡献与 §3.1 合成方法的因子有效性。需轻量过渡方案。

**SimpleFactorAttribution**（Brinson 式因子 PnL 分解，不依赖 Barra 基础设施；benchmark='csi300' 沪深300）：

- 归因公式：`PnL_i = Σ_t (w_{i,t} - w_{benchmark,t}) × r_{i,t}`，其中 w=t 日因子 i 的组合暴露，r=t 日因子 i 的截面收益。
- 输出：各因子 `pnl / contribution_ratio / avg_active_exposure` + 残差（总 PnL - 因子归因和）+ `explained_ratio`，按 pnl 排序标记低贡献因子（联动 §3.3 衰减复检）。

> **施工建议**：新增 `simple_factor_attribution.py`（MOD-L02-014，D-FACTOR-ANA-12）。纯增量 ~45 行，输入来自 `decay_monitor.py` 的因子收益 + `portfolio_optimizer.py` 的因子暴露。

#### 缺失#5：因子拥挤实时监控算法（高优先级，v1.12.6 新增——拥挤崩盘断裂点修复）

**问题**：§3.3 衰减监控管"信号变弱"（均值），**因子拥挤**管"太多人用同一因子"（尾部风险）——拥挤因子风格切换时崩溃概率高 1.7-1.8x（arXiv:2512.11913），2026-07 A 股 57 只量化基金踩雷即实时验证。两者正交，可同时触发（IC 未衰减但拥挤度高=崩盘前兆）。

**CrowdingRealTimeMonitor 参数**：

| 参数 | 值 | 含义 |
|---|---|---|
| etf_holding_window | 60 | ETF 持仓变化滚动窗口（arXiv:2512.11913 验证 ETF 持仓 ρ=-0.63） |
| etf_holding_alert | 0.20 | ETF 持仓增长>20%→拥挤加速 |
| factor_corr_window | 40 | 因子收益相关性滚动窗口 |
| factor_corr_alert | 0.70 | 因子间平均相关性>0.70→拥挤（共识形成） |
| quant_seat_ratio_alert | 0.35 | 龙虎榜量化席位占比>35%（2026 量化占比，A 股特色代理）→拥挤 |
| crash_risk_high | 0.70 | 拥挤综合分>0.70→高崩盘风险→降仓 |

**决策逻辑**（`assess()`）：① ETF 持仓增长（近 20 日 vs 前 40 日基线）归一化得分；② 因子间平均相关性归一化得分；③ 量化席位占比归一化得分；综合拥挤分=三者均值（0-1）。分级响应：`>0.70`→`REDUCE_WEIGHT_50`（降权 50%+尾部风险预警）；`>0.50`→`ALERT`（监控+CUSUM 联动）；否则 `MONITOR`。

> **施工建议**：`decay_monitor.py` 增加拥挤度检测通道，与 CUSUM 并列。纯增量 ~40 行。**MVP 必做**（非远期候选）。输入：ETF 持仓数据（公开）+ 因子收益相关性（已有）+ 龙虎榜量化席位占比（§3.11 detect_quant_seat_warning 复用）。

> **BM-RC-06-D 拥挤度检测深度增强扩展（v1.13.2 补）**：
> - **定位**：BM-RC-06-D（拥挤度检测，L4 风控域，design 态）= 因子拥挤 + **策略拥挤**双支预警，输出喂 BM-RC-06-C 三级警报。本小节承接其**因子/策略持仓侧**拥挤代理计算（多因子 sleeve 消费侧）；三级警报与组合级去杠杆裁决属风控域职责，不越界。
> - **裁定**：上述三代理指标为 **MVP 必做基线（不变）**；作战地图要求的三个深度增强项**登记 design 远期**——① **策略逻辑相似度检测**（跨策略信号逻辑同构度，防"不同策略同一拥挤交易"）；② **去杠杆路径预案**（拥挤触发时降杠杆顺序/节奏预登记）；③ **拥挤悖论防护**（"人人躲拥挤=新拥挤"，对拥挤规避动作做二阶监控）。理由：三项均依赖多策略并发实盘数据（当前 sleeve 未上线，无横截面可算），提前施工是无输入的空转组件（charter 约束五）。
> - **契约（远期登记）**：输入=因子暴露+策略持仓（D-FACTOR/D-PF-CORE），输出=拥挤度预警（因子拥挤分+策略相似度分+去杠杆预案触发标记），降级=拥挤度检测未就绪→跳过（现状即降级态）。
> - **重评条件**：首批策略上线产生横截面持仓数据后激活①；首次拥挤触发去杠杆事件后校准②；③随①上线后一并评估。

#### 缺失#6：换仓触发决策算法（中优先级，v1.12.6 新增——convergence_window 执行断裂点）

**问题**：§3.4 裁定 convergence_window = 3-5 天，但"何时在窗口内触发换仓"未形式化——过早换仓增成本，过晚换仓 alpha 流失。

**RebalanceTrigger 参数**（v1.12.6 三触发器 + v1.12.11 Inaction Cost 成本门控）：

| 参数 | 值 | 含义 |
|---|---|---|
| convergence_window_max | 5 | 保底换仓周期 |
| convergence_window_min | 3 | 最短换仓间隔（防过度换仓） |
| drift_threshold | 0.15 | 组合权重漂移>15%→触发 |
| rank_change_threshold | 10 | top-30 因子排名变化>10 位（×30 归一化）→触发 |
| cost_aware | True | 换仓成本感知（A 股 0.4% 往返） |
| transaction_cost_rate | 0.004 | A 股往返交易成本 0.4%（印花税+佣金+滑点） |
| daily_alpha_estimate | 0.0005 | 日均因子 alpha 估计 0.05%（IC~0.03 保守估计） |

**决策逻辑**（`should_rebalance()`）：① `days_since_last<3`→WAIT（最短间隔保护）；② `≥5`→TIME 保底换仓（**不受成本门控**）；③ 漂移 `>15%`→成本门控通过→DRIFT 触发；④ top-30 排名变化 `>10×30`→成本门控通过→SIGNAL 触发；⑤ 均未达→HOLD。
**成本门控**（`_is_rebalance_worthwhile()`，Perold 1988 Implementation Shortfall 框架）：`Inaction Cost = drift × daily_alpha × expected_days`（expected_days=5-days_since_last），`Action Cost = 0.4% × drift`；**Inaction > Action 才换仓**。化简 break-even：0.05%×days > 0.4% → 8 天；convergence_window_max=5 < 8 提供安全垫——窗口内漂移/信号触发时若距保底仅剩 1-2 天，等保底触发省交易成本。触发后调用 §3.5 七约束链重优化 + §3.7#2 仲裁。

> **施工建议**：`portfolio_optimizer.py` 调度层增加 `should_rebalance()` 前置门控。纯增量 ~35 行（v1.12.6）+ ~15 行 Inaction Cost（v1.12.11）。**MVP 即做**。

#### 缺失#7：多因子 PIT 安全回测框架算法（高优先级，回测验证基础设施——与 24 号对称）

**问题**：§3.7#1-#6 补全六环节编排，但**回测验证基础设施**缺失——24 号有 `DabanPITBacktestFramework`（§3.14 缺失#10），25 号无对称框架。多因子 PIT 比打板更复杂——5 层 PIT，§2.3 PIT 铁律仅声明原则未形式化。PIT 违规=回测虚高+实盘失效。

**MultifactorPITBacktestFramework——5 层 PIT**：

| 层 | 规则 | 说明 |
|---|---|---|
| factor_value | AS OF JOIN | t 日决策只用 t 日及之前因子值 |
| ic_weight | ROLLING t-1 | IC 权重来自 t-1 日及之前历史 IC（不能用 t 日 IC 算 t 日权重=未来函数） |
| synthesis_weight | t因子+t-1权重 | 合成因子分用 t 日因子值 + t-1 日 IC 权重 |
| covariance | ROLLING t-1 | 协方差矩阵（波动率/相关性）用 t-1 日及之前数据 |
| industry_class | AS OF JOIN | 行业分类 AS OF JOIN（股票行业可能变更） |

参数：`ic_window=60`（IC 滚动窗口）、`cov_window=60`（协方差滚动窗口）。PIT 断言：`assert_factor_pit`（factor_date ≤ decision_date）/ `assert_ic_weight_pit`（IC 窗口截止日 < 决策日）/ `assert_covariance_pit`（协方差截止 < 决策日）。

**回测主循环**（`run_backtest()`，每决策日）：① 因子值 AS OF JOIN 加载+断言；② IC 历史加载（窗口截止 t-1）+断言；③ 合成降级链决策（§3.7#1，回测中 `forward_returns=None` 避免前瞻）；④ 合成因子分+当前排名；⑤ 协方差加载+断言；⑥ 组合优化（§3.5 七约束链）+约束仲裁（§3.7#2）；⑦ 换仓触发（§3.7#6，首次建仓=INIT）；⑧ 非换仓日跑 §3.7#8 持仓偏差监控，critical→`DRIFT_CRITICAL` 强制换仓；⑨ 记录结果（日期/方法/触发器/偏差警报数）。

> **施工建议**：新增 `multifactor_pit_backtest.py`（MOD-L02-015，D-FACTOR-ANA-13），多因子策略回测标准框架。纯增量 ~80 行，输入来自 `decay_monitor.py`（IC 历史）+ `portfolio_optimizer.py`（协方差+优化）+ `multifactor_synthesis.py`（合成）。**首批回测前必做**——5 层 PIT 断言防止回测虚高，与 24 号 DabanPITBacktestFramework 对称。

#### 缺失#8：持仓偏差监控算法（中优先级，持仓期间因子暴露+行业偏离实时监控）

**问题**：§3.5 约束链在优化器求解时生效，但**持仓后实际暴露偏差监控缺失**——价格变化使实际因子/行业暴露偏离目标。§3.7#6 的漂移触发（15%）只监控权重漂移，不监控因子暴露偏差和行业偏离。

**HoldingDriftMonitor 参数**：

| 参数 | 值 | 含义 |
|---|---|---|
| factor_drift_alert | 0.05 | 因子暴露偏差>5%→预警 |
| factor_drift_critical | 0.10 | 偏差>10%→触发换仓（C6 约束边界） |
| industry_drift_alert | 0.03 | 行业偏离>3%→预警 |
| industry_drift_critical | 0.05 | 偏差>5%→触发换仓（C2 约束边界） |
| weight_drift_alert | 0.10 | 权重漂移>10%→预警（输入 RebalanceTrigger，其阈值 15%） |

**决策逻辑**（`monitor()` 每日盘后）：① 因子暴露偏差——critical→`FACTOR_CRITICAL/TRIGGER_REBALANCE`，alert→`FACTOR_ALERT/MONITOR`；② 行业暴露偏差——同理 `INDUSTRY_CRITICAL/INDUSTRY_ALERT`；③ 权重漂移>10%→`WEIGHT_DRIFT/FEED_REBALANCE_TRIGGER`。输出 `alerts + critical_count + should_trigger_rebalance(critical>0) + weight_drift`；critical 时触发 RebalanceTrigger 强制换仓（覆盖时间/漂移/信号三触发器）。

> **施工建议**：`portfolio_optimizer.py` 增加 `monitor()` 每日盘后调用。纯增量 ~45 行。**MVP 即做**——与 RebalanceTrigger 配合解决"换仓后到下次换仓期间偏差谁来管"的断裂点。

## 4. 考虑过的替代方案

### 4.1 过度工程审查

| 候选 | 评估 | 结论 |
|---|---|---|
| 因子数 >50 | 个人系统 8-15 因子足够，多了是过拟合温床 | 不过度工程，池上限 64 实际活跃 ≤30 |
| 正交化 | 当前规模因子相关性已控制 | 不实现，远期评估 |
| 深度学习因子合成 | 需大量数据+算力，个人系统不适用 | 远期 Phase 4 候选，MVP 不做 |
| Barra 风险模型归因 | 需多因子风险模型基础设施 | 远期 Phase 4 候选 |

### 4.2 替代方案：因子组合方式

| 方案 | 优势 | 劣势 | 结论 |
|---|---|---|---|
| 等权 | 简单、鲁棒 | 忽略因子质量差异 | 降级兜底 |
| **IC 加权** | 因子质量加权、自动化 | 依赖 IC 稳定性 | **默认方法** |
| 回归优化 | 最大 IR | 过拟合风险、需前瞻数据 | 可选增强 |
| 正交化 | 消除因子共线性 | 损失信号、实现复杂 | 不实现 |

### 4.3 替代方案：行业中性化层级

| 方案 | 优势 | 劣势 | 结论 |
|---|---|---|---|
| 因子层中性化 | 因子纯净 | 损失行业 alpha | 不采用 |
| **组合约束层** | 保留因子信号 | 需优化器 | **采用** |
| Barra 风格中性化（因子层，v1.13.1 补） | 机构级纯度（行业+风格联合正交） | 需 Barra 风险模型基础设施 + 同样损失行业 alpha | 不采用（Phase 4.5 KTD-Fin 远期候选，MVP 不需要） |

## 5. 上限定义

### 5.1 系统上限

| 维度 | 上限 | 依据 |
|---|---|---|
| 因子池 | ≤64 活跃≤60 休眠≤4 | `factor_pool_manager.py` ADR-FAC-006 + governance/_config.yaml（v1.13.0 源码校正） |
| 单票仓位 | ≤2% NAV（C12） | 分散度 |
| sleeve 容量 | 500-2000 万（待校准） | 横截面流动性 |
| 持仓周期 | 5-20 天 | convergence 3-5 天 |
| 持仓数 | 30-80 只 | 分散度 + C7 |
| 回撤上限 | 25% 清仓 | [30 §2.5] |

### 5.2 演进路径

- **Phase 1（当前，production）**：IC 加权合成 + 7 约束链组合优化 + 三层衰减监控，全部 production
- **Phase 2（回测微调）**：IC 加权窗口校准 + 衰减监控阈值校准 + 行业暴露约束实测 + **PIT 安全回测框架（§3.7#7，5 层 PIT 断言，首批回测前必做）** + **持仓偏差监控（§3.7#8，C2/C6 约束持续满足，MVP 即做）**
- **Phase 3（容量校准）**：首批实盘后校准 sleeve 容量精确值 + convergence_window 实测 + 拥挤监控阈值校准（§3.7#5，57 只量化基金踩雷实证驱动）
- **Phase 4（ML 合成升级栈）**：
  - **Phase 4.1 Mask-First 可交易性掩码（v1.12.5 补完整消融实证）**：解决 A 股因子 IC 计算的"上游污染"——停牌/涨跌停/流动性不足标的未排除导致 IC 虚高；构造 `tradability_mask` 仅在可交易池中计算 IC。**MVP 即做**（纯增量 ~40 行），因子工坊 IC 计算前置门控。**消融实证**：[arXiv:2507.07107](https://arxiv.org/abs/2507.07107)（Du 2026-05-09 USTC，3000 股合成面板+真实 A 股 2022-2024）——mask 合约是**单一最大贡献者**（+0.44 Sharpe，超任何模型/损失选择）；忽略上游污染使表观 IC 虚高 18% 但实现 Sharpe -0.44；合成面板 Sharpe 2.05 / 真实 A 股 1.63；含 GPU 向量化 213 因子引擎（51× over pandas）+ Adjusted-MSE（错号惩罚 11×）+ Ledoit-Wolf 优化。启示：① mask-first 是 MVP **最高优先级**；② Adjusted-MSE 可作 Phase 4.2 互补候选（前者罚方向，后者优化排序）；③ Ledoit-Wolf 收缩可与 §3.5 C6 联动。MIT 开源 [github.com/initial-d/ml-quant-trading](https://github.com/initial-d/ml-quant-trading)。
  - **Phase 4.2 LambdaRankIC 训练目标**：直接优化 Rank IC 而非 MSE——LambdaRank 框架内推导 lambda 梯度闭式解，训练目标与评估目标对齐。远期候选（需 ML 训练基础设施），MVP 不做。
  - **Phase 4.3 RankGLU 预测头架构**：残差门控评分形成——线性评分路径 + 有界乘性 GLU 分支。远期候选，MVP 不做。
  - **Phase 4.4 STAR CrossAttention 混频融合**：日频量价因子与月频基本面因子 Cross-Attention 融合，捕捉跨频交互。远期候选，MVP 不做。
  - **Phase 4.5 KTD-Fin Barra 归因**：基于 CNE5 风格因子模型做多因子/单因子 IC 双检验。远期候选（需 Barra 基础设施），MVP 不做。
  - **Phase 4.6 EFS/Agentic/CAE 远期候选（v1.12.4 补完整实证）**：EFS（进化因子搜索）/Agentic（LLM 驱动因子发现）/CAE（压缩自编码器降维）三方向。**EFS 实证**：[arXiv:2507.17211](https://arxiv.org/abs/2507.17211)（Chen et al. 2026-08-07 CityU+SUFE）——LLM+进化算法生成 alpha 因子做稀疏组合优化，RMT 去噪+正则化 QP；4 个 Fama-French 基准（FF25/32/49/100）+ 3 个真实市场（美/港/中国大陆）超越基线。**A 股适用性高**——直接在中国大陆验证，与 BM-SEL-02 天然衔接。远期候选（需 LLM 推理基础设施），Phase 4 升级时优先评估。
  - **Phase 4.7 Alpha-R1 LLM+RL 动态门控抗衰减**：基于因子经济逻辑与实时新闻语义对齐做动态因子门控。远期候选（需 LLM+RL 基础设施），MVP 不做。
  - **Phase 4.8 AlphaPROBE DAG+贝叶斯过拟合先验**：DAG 因子图 + 贝叶斯过拟合先验做因子选择。远期候选，MVP 不做。
  - **Phase 4.9 中信建投 GRU 非线性合成 A 股实证**：GRU 非线性因子合成，中信建投 2026-07 A 股实证背书。远期候选，MVP 不做。
  - **Phase 4.10 行业嵌入 LSTM 跨截面异质性（v1.12.0 补）**：[arXiv:2608.05755](https://arxiv.org/abs/2608.05755)（2026-08-07 Döbelt）——行业嵌入 LSTM 持续优于无嵌入版本，跨截面异质性建模是关键。远期候选，MVP 不做。
  - **Phase 4.11 RL 组合管理三候选（v1.12.0 补，v1.12.6+v1.12.8 补实证）**：VD-MEAC（值分布最大熵 Actor-Critic，critic 学习未来收益完整分布）/ HRT（分层 RL，上层选股+下层执行）/ SAMP-HDRL（安全 RL，内置回撤/波动率/VaR 约束）。均需 RL 基础设施，Phase 4 远期候选。与 Phase 4.12 正交——RL 管"权重怎么动态调整"，MINGLE/OMD 管"组合结构怎么构建"。**Dynamic-β reward 实证**：[PLoS One 2025](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0332779)——PPO/SAC/TD3 上 5 种 reward 比较，Dynamic-β（滚动回归估计 momentum/volatility/MA/volume 因子 β 敏感度）年化 ~20%→23-24%、Sharpe 1.04→~1.27（HAC/Wilcoxon/jackknife/bootstrap/FDR 多重检验）；启示：VD-MEAC reward 可参考 Dynamic-β 用因子暴露 β 而非裸收益。**CVaR RaQL 自适应训练**：[arXiv:2608.04305](https://arxiv.org/abs/2608.04305)（Wu et al. 2026-08-06 ICAIF'26）——6 机制自适应训练控制器（步长自适应+学习率衰减同步+VaR 早期短修正+覆盖率优先样本分配+渐进后缀聚合+数据驱动尺度校准），不改 CVaR 估计器仅重设计训练过程，CVaR Bellman 残差降低约 85%（MeanBEQ 1.22→0.19），样本外 Sharpe 0.93/最大回撤 6.46%。与 VD-MEAC 互补（前者管训练稳定性，后者管策略架构），CVaR 目标天然适合 A 股尾部风险。远期 Phase 4.11 升级时一并评估。
  - **Phase 4.12 组合优化/多样化新范式两候选（v1.12.2 补）**：MINGLE（[arXiv:2608.06618](https://arxiv.org/abs/2608.06618)，ADMM 联合学习潜因子表示+图拓扑，因子暴露相似性建图替代相关性建图）/ OMD（[arXiv:2607.27461](https://arxiv.org/abs/2607.27461)，三矩阵 rank-based 无需矩阵求逆，volatility rank 一步预测）。Phase 4 远期候选，与 Phase 4.11 正交。
  - **Phase 4.13 仓位 sizing 与风控新范式三候选（v1.12.3 补，v1.12.10 补 Conformal Kelly 完整实证）**：Conformal Kelly（[arXiv:2608.01494](https://arxiv.org/abs/2608.01494) Ryan 2026-08，保形预测区间作为分数 Kelly 仓位的 scale，A 股适用性高——对非正态分布鲁棒，与现有 Kelly 框架天然衔接）。**完整实证**：① **"简单优于复杂"负面结果**——每个使区间更快适应 regime 的调整反而年化降低 0.7-5.3 个百分点，最优是最简单的慢速无加权 per-asset 滚动保形分位数（区间用于 sizing 时宽度稳定性比局部锐度更重要）；② **区间失误风控**——向下失误率远超历史基准时视为模型崩溃信号→削减杠杆，最大回撤 27.7%→20.3% 同时提升 Sharpe，胜过全部 40 个安慰剂版本（p=1/41≈0.024）；③ 样本外校准保持（覆盖率 0.745 vs 目标 0.750）但增长未保持（2022 后年化 8.5%/7.0% 低于被动基准）。**与 Phase 4.14 的张力**：Conformal Kelly 证"简单无加权最优"，RWC 主张"regime 加权压力期更优"——矛盾需 A 股实证裁定，可能结论"校准用简单版+风控用 regime 加权版"。/ Path Portfolio Optimization（[arXiv:2608.02355](https://arxiv.org/abs/2608.02355)，路径视角组合优化，显式建模路径累积成本）/ Drawdown Risk Beyond Brownian Motion（[arXiv:2608.00127](https://arxiv.org/abs/2608.00127)，非高斯扩展+长记忆回撤建模，与回撤 Protocol 阈值校准直接相关）。三者均属 Phase 4 远期候选。登记 §6 待裁定。
  - **Phase 4.14 Regime-Weighted Conformal Calibration（v1.12.4 补，扩展 Phase 4.13 Conformal Kelly）**：[arXiv:2602.03903](https://arxiv.org/abs/2602.03903)（Schmitt 2026-08-03 Oxford）——RWC 用指数时间衰减+regime 相似性权重从历史预测误差构建安全缓冲，包裹任意条件分位数预测器；CRSP+16 个美国组合 Basel 99%/97.5% 验证，TWC（时间加权）漂移下是强默认，RWC 压力期改善慢适应预测器校准。**A 股适用性高**——regime 相似性权重可复用 [10_regime_detector_spec](10_regime_detector_spec.md) 12 态输出。与 4.13 关系：Conformal Kelly 管"仓位多大"，RWC 管"区间多宽更稳健"。远期候选（需保形预测+regime 联动基础设施），与 Conformal Kelly 一起评估。
  - **Phase 4.15 Risk-Sensitive RL+Fractional Kelly（v1.12.4 补，统一 Phase 4.11+4.13）**：[arXiv:2606.20903](https://arxiv.org/abs/2606.20903)（Lleo & Runggaldier 2026-06-18）——连续时间风险敏感基准化资产配置 RL，自由能-熵对偶重表述为 LQG 随机微分博弈，得鞍点解；**学到的分配可分解为分数 Kelly**——提供 RL（4.11）与 Conformal Kelly（4.13）的理论统一框架。美国股权 proof-of-concept：组合 actor 比对抗 actor 收到更干净学习信号。**A 股适用性中**——连续时间假设与离散交易+T+1 有差距，分数 Kelly 分解+风险敏感目标可借鉴。远期候选，Phase 4+ 评估。
  - **Phase 4.16 Sign-Aware Adjusted-MSE 损失（v1.12.5 补，Phase 4.2 互补候选）**：源自 [arXiv:2507.07107](https://arxiv.org/abs/2507.07107)——错号预测（预测涨实际跌）惩罚 11× 于幅度误差，优先保证方向正确；A 股真实数据消融验证与 mask 联合优于任一单独。与 4.2 关系：LambdaRankIC 优化排序，Adjusted-MSE 优化方向，互补可叠加。**A 股适用性高**——T+1+涨跌停使方向错=完全踏空。远期候选（需 ML 训练基础设施），与 LambdaRankIC 一起评估。
  - **Phase 4.17 Certified Wasserstein Robust Portfolio（v1.12.6 补，2026-08-10 arXiv 最新）**：[arXiv:2608.07032](https://arxiv.org/abs/2608.07032)（Hsieh & Gan）——认证高维 Wasserstein 鲁棒组合优化，分布不确定性下提供**可认证**最坏情况保证，避免传统鲁棒优化过度保守。与 4.12 正交可叠加（MINGLE/OMD 管结构，Wasserstein 管分布保底）；与 §3.7#5 关系：拥挤监控是预警（实证代理），Wasserstein 是防御（数学保证）。**A 股适用性高**——分布偏移剧烈，可替代 §3.5 C3 静态波动率约束升级为分布鲁棒。远期候选（cvxpy 已有），Phase 4+ 评估。
  - **Phase 4.18 MFCCA 多尺度组合配置（v1.12.10 补，突破 IC 加权瓶颈）**：[arXiv:2608.04987](https://arxiv.org/abs/2608.04987)（Kakinaka & Umeno 2026-08-05）——多重分形互相关分析带符号涨落函数作为风险泛函（尺度 s × 阶数 q 双索引）；**关键创新**：保留局部去趋势协方差符号——同向与反向运动以相反符号贡献风险；q=2 退化为均值-方差。核心发现：符号保留对尾部风险降低贡献 > 跨阶聚合；相对均值-方差基准每个目标收益下均降回撤/VaR/期望损失且不损失收益（样本内外一致）。**A 股适用性中高**——中信建投 2026-06 确认"等权/IC/ICIR 三种加权接近"瓶颈，A 股因子同向/反向关系跨尺度差异显著（日线动量 vs 周线反转）。与 §3.1 关系：IC 加权是单尺度线性合成，MFCCA 是多尺度非线性合成。远期候选（需多重分形分析基础设施），Phase 4+ 作为合成方法替代评估。
  - **Phase 4.19 Stationary Ambiguity 平稳模糊性训练（v1.12.10 补，ML 模型 regime-shift 防护）**：[arXiv:2608.04832](https://arxiv.org/abs/2608.04832)（Mueller et al. 2026-08-05）——标准鲁棒训练缺陷：策略推断出潜在参数后模糊性系统性衰减→特化→丧失 regime-shift 鲁棒性；**平稳模糊性原则**：构建模拟器使模糊性随状态变化但不随时间系统性衰减。对冲问题验证长期保持鲁棒。**A 股适用性高**——政策市 regime 频繁切换，"训练期好、实盘 regime 一变就衰减"正是模糊性衰减过拟合。与 §3.7#3 关系：DecayActionLifecycle 管"衰减后怎么退役"（事后），平稳模糊性管"训练时怎么防衰减"（事前），互补。Phase 4.10/4.11 等所有 ML 模型均可受益。远期候选（需模拟器设计改造），Phase 4+ 作为训练基础设施改进评估。
  - **Phase 4.20 QUBO 换仓调度优化（v1.12.11 补，§3.7#6 远期升级路径）**：[arXiv:2603.16904](https://arxiv.org/abs/2603.16904)（Weinberg 2026-03）——换仓时序建模为 QUBO：目标=边际 Sharpe 增益-交易成本惩罚-过频惩罚（指数衰减交互项）；Walk-forward QAOA 消除 lookahead。S&P 500 实证：8 次换仓 vs 日历 24 次（成本降 44.5%），Sharpe 0.588 vs 0.575。**关键创新**：从"阈值触发→执行"反应式升级为"未来 N 天换仓计划"组合优化。**A 股适用性中**——0.4% 往返成本比美股高 4x，过频惩罚更关键。**量子非必须**：经典 QUBO 求解器（模拟退火/分支定界）可替代，n=5 天窗口秒解。与 §3.7#6 关系：RebalanceTrigger 管"今天换不换"，QUBO 管"未来 5 天怎么排"。远期候选（需 QUBO 求解器基础设施），Phase 4+ 评估。
- **Phase 5（最终升级）**：若 Phase 4 候选有验证增益，逐步替换静态 IC 加权/固定 Kelly/布朗回撤假设

### 5.3 为何是上限

因子池上限由个人系统过拟合风险决定（8-15 因子足够，多了是过拟合温床）。sleeve 容量上限由横截面选股流动性决定（30-80 只标的分散持仓，单票≤日成交 5%）。回撤上限取行业基准下限是因为多因子波动小于打板但仍需 25% 清仓底线。

## 6. 待裁定

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| 因子池扩张到 50+ | 当前 8-15 因子足够 | Phase 4 ML 合成验证增益后评估 |
| 正交化实现 | 当前规模因子相关性已控制 | 因子池扩张到 50+ 时重新评估 |
| IC 加权窗口校准 | 当前默认 60 交易日 | 首批策略回测时校准最优窗口 |
| 衰减监控阈值校准 | 当前 k=0.5σ/h=4σ | 首批策略实盘后校准 A 股因子衰减参数 |
| sleeve 容量精确测算 | 当前为估算值 500-2000 万 | 首批策略实盘后校准 |
| Mask-First 可交易性掩码 | A 股因子 IC 计算的"上游污染" | MVP 即做（纯增量 ~40 行） |
| LambdaRankIC 训练目标 | 直接优化 Rank IC | 需 ML 训练基础设施，Phase 4 远期候选 |
| RankGLU 预测头架构 | 残差门控评分形成 | Phase 4 远期候选 |
| STAR CrossAttention 混频融合 | Cross-Attention 日频量价×月频基本面 | Phase 4 远期候选 |
| KTD-Fin Barra 归因 | A 股 Barra 风险模型归因 | 需 Barra 基础设施，Phase 4 远期候选 |
| EFS/Agentic/CAE 远期候选 | 进化因子搜索/LLM 因子发现/CAE 降维 | Phase 4+ 远期候选 |
| Alpha-R1 LLM+RL 动态门控抗衰减 | LLM+RL 语义对齐动态门控 | 需 LLM+RL 基础设施，Phase 4 远期候选 |
| AlphaPROBE DAG+贝叶斯过拟合先验 | DAG 因子图+贝叶斯过拟合先验 | Phase 4 远期候选 |
| 中信建投 GRU 非线性合成 | GRU 非线性因子合成 A 股实证 | Phase 4 远期候选 |
| 行业嵌入 LSTM 跨截面异质性 | 可学习行业嵌入 LSTM（arXiv:2608.05755） | Phase 4.10 远期候选 |
| VD-MEAC 值分布 RL 组合管理 | critic 学习未来收益完整分布+最大熵 actor | Phase 4.11 远期候选 |
| HRT 分层 RL 组合管理 | 上层选股+下层执行分层 RL | Phase 4.11 远期候选 |
| SAMP-HDRL 安全 RL 组合管理 | 多阶段分层深度 RL+内置安全约束 | Phase 4.11 远期候选 |
| MINGLE 因子-图联合组合优化 | ADMM 联合学习潜因子+图拓扑（arXiv:2608.06618） | Phase 4.12 远期候选 |
| OMD 三矩阵 rank-based 组合优化 | 三矩阵 rank-based 无需矩阵求逆（arXiv:2607.27461） | Phase 4.12 远期候选 |
| Conformal Kelly 保形预测仓位 | 保形预测区间作为 Kelly scale（arXiv:2608.01494） | Phase 4.13 远期候选 |
| Path Portfolio Optimization | 路径视角组合优化（arXiv:2608.02355） | Phase 4.13 远期候选 |
| Drawdown Risk Beyond Brownian | 非高斯扩展+长记忆回撤建模（arXiv:2608.00127） | Phase 4.13 远期候选 |
| 多因子×事件驱动相关性实测 | 两者都受情绪周期隐形驱动 | G07 施工前必做 |
| Hyperbolic 衰减模型替换指数衰减 | α(t)=K/(1+λt) 更贴合 A 股 | 首批策略实盘后校准对比 |
| Regime-Weighted Conformal Calibration | RWC 扩展 Conformal Kelly（arXiv:2602.03903） | Phase 4.14 远期候选 |
| Risk-Sensitive RL+Fractional Kelly | 统一 Phase 4.11+4.13（arXiv:2606.20903） | Phase 4.15 远期候选 |
| Sign-Aware Adjusted-MSE 损失 | 错号预测惩罚 11×，Phase 4.2 互补（arXiv:2507.07107） | Phase 4.16 远期候选 |
| Dynamic-β reward 实证 | PLoS One 2025 Sharpe 1.04→1.27 | Phase 4.11 v1.12.6 补 |
| Certified Wasserstein Robust Portfolio | arXiv:2608.07032 2026-08-10 分布鲁棒 | Phase 4.17 远期候选 |
| MFCCA 多尺度组合配置 | arXiv:2608.04987 符号保留+多尺度非线性合成 | Phase 4.18 远期候选 |
| Stationary Ambiguity 平稳模糊性训练 | arXiv:2608.04832 防模糊性衰减→regime-shift 过拟合 | Phase 4.19 远期候选 |
| QUBO 换仓调度优化 | arXiv:2603.16904 换仓时序 QUBO 组合优化 成本降 44.5% | Phase 4.20 远期候选 |
| A 股 2026-07-06 交易新规 | ST 涨跌幅 5%→10%+盘后固定价格交易扩容 | G22 执行层施工时同步 |
| 衰减监控 CUSUM 层 + 自动淘汰层落码 | 代码仅半衰期监控（decay_monitor.py min_half_life=10），CUSUM/40 日\|IC\|<0.02 休眠为本文档决策（§3.3 代码现状注记） | 随 §3.7#3 DecayActionLifecycle 一并落码 |
| C1-C7 策略级约束链 ↔ MOD-PF-006 代码约束链对齐 | 代码约束参数（行业 ±10%/MDD 5%/相关性 0.7 等）与 §3.5 决策参数不一致（§3.5 代码现状注记） | 多因子 sleeve 上线前经 CTR-003 RiskLimits 注入对齐 |
| DecayActionLifecycle 6 态 ↔ factor_registry status 5 态映射 | 运行时 6 态（NEW/ACTIVE/OBSERVE/DORMANT/RECOVERY/RETIRED）vs registry 治理 5 态（candidate/experimental/active/deprecated/retired）双轨，DORMANT/OBSERVE 在 registry 应标什么未定义 | §3.7#3 落码时定义映射规则并回写 62 号 |
| G01 因子工程总纲（15 号）仍为 draft 骨架 | 本文档因子治理参数无上游 why 层背书；因子 10 类真源实际在 62 号 §6.1.1 + factor_registry.yaml | 15 号定稿后回填对齐（由 AI-20 负责 15 号） |
| 00_index 版本显示同步 | 00_index §0 目录/L215/L600 仍显示 v1.12.11，本文档已 1.13.1 | 由 AI-12 负责 00_index 同步（不越界改） |
| BM-RC-06-D 拥挤度深度增强三项 | §3.7#5 v1.13.2 补：策略逻辑相似度检测+去杠杆路径预案+拥挤悖论防护登记 design 远期（依赖多策略并发实盘数据，当前无输入） | 首批策略上线产生横截面策略持仓数据后激活①；首次去杠杆事件后校准②；③随①上线评估 |
| BM-SEL-02-E LLM 语义去重 | §3.1 v1.13.2 补：登记远期候选——数值相关性去重（correlation_dedup.py ANA-05）已 production 够用，现状即作战地图降级态 | 因子池扩张到 50+ 且"数值低相关但逻辑同构"伪异质因子实例 ≥2 例 |
| BM-SEL-02-M 因果因子验证层（DoWhy/DML） | §3.1 v1.13.2 补：登记远期 Phase 4——#ARCH-OE-009 裁的是 BM-MT-04（PC/LiNGAM 因果发现），本环节未被裁剪；与 11 号 §0.6.10 发现 2 Causal-TS 评估呼应 | 因子库伪相关惨案 ≥1 例（入库因子实证为伪相关并造成实亏） |

> 原 17 行 ✅「文档已补」登记行（§3.7 施工算法 8 项、Phase 4.x 实证背书等）非待裁定项且与 §8 修订记录 v1.12.4~v1.12.11 各行重复，第二轮压缩已移除——明细真源见 §8 修订记录与 §3.7/§5.2 正文。

## 7. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G09
- [20_first_batch_strategies](20_first_batch_strategies.md) §2.3 多因子 sleeve 定义
- [23_strategy_correlation_validation](23_strategy_correlation_validation.md) §2.3/§3.1 G07 相关性验证（战略级 >0.6 vs 运营级门禁 0.85/0.90 分层，v1.13.0 补链）
- [28_sentiment_cycle_trading](28_sentiment_cycle_trading.md) §3.4 多因子与 regime 正交边界
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.4/§2.5/§6.4
- [15_data_feature_layer_spec](15_data_feature_layer_spec.md)（G01 因子工程总纲）
- [46_d_factor](../02_domain_architecture_docs/46_d_factor.md) D_FACTOR 域 65 个 production 模块
- battle_map_05_stock_selection（BM-SEL-02）
- **arXiv**：2507.07107 Mask-First 消融实证+Adjusted-MSE（v1.12.5 补）/ 2608.07032 Certified Wasserstein Robust Portfolio（v1.12.6 补 2026-08-10）/ 2608.06618 MINGLE / 2607.27461 OMD / 2608.05755 LSTM Cross-Sectional / 2608.01494 Conformal Kelly / 2608.02355 Path Portfolio / 2608.00127 Drawdown Beyond Brownian / 2608.04987 Multifractal Portfolio（v1.12.10 补，MFCCA 多尺度组合配置）/ 2608.04832 Stationary Ambiguity 平稳模糊性训练（v1.12.10 补，防 regime-shift 过拟合）/ 2603.16904 QUBO 换仓调度优化（v1.12.11 补，S&P 500 成本降 44.5%）/ **2608.04305 CVaR RaQL 自适应训练（v1.12.8 补，6 机制训练控制器 Bellman 残差-85%）**
- **经典理论**：Perold (1988) Implementation Shortfall——不换仓的机会成本 IS=(P_close-P_0)×Q_unexecuted（v1.12.11 补，§3.7#6 RebalanceTrigger Inaction Cost 理论基础）/ Almgren-Chriss (2000) 最优执行前沿（执行成本-方差权衡）
- **学术期刊**：PLoS One 2025 Dynamic-β reward DRL（v1.12.6 补，Sharpe 1.04→1.27）/ ICAIF'26 CVaR RaQL（v1.12.8 补，Wu et al. 2026-08-06）
- **券商研报**：华泰金工多因子（2026-07）/ BigQuant ICIR（2026-07）/ 国信中证1000增强（2026-08-08，超额21.45%）/ 国金量化行业配置（2026-08-08）/ 中信建投 GRU（2026-07）/ laoyulaoyu 因子衰减（2026-06）/ **国泰海通高频选股因子周报（2026-08-10，v1.12.6 补，行为因子多空 12-16%+多粒度 28%）**
- **行业实证**：中国基金报 2026-08 公募量化7月回撤（v1.12.6 补，57只量化基金踩雷=拥挤因子崩盘实证）
- **监管**：沪深北交易所新版交易规则（2026-07-06 落地，v1.12.5 补）——ST 涨跌幅 5%→10%、盘后固定价格交易扩容全 A 股/ETF、创业板做市商

## 8. 修订记录

| 日期 | 版本 | 变更摘要 |
|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 |
| 2026-08-10 | 1.0.0 | 6 项讨论要点全部对齐落定，status→active |
| 2026-08-10 | 1.10.0 | 施工算法深度审查 + 2026-08 最新研究整合：Mask-First + LambdaRankIC + RankGLU + STAR CrossAttention + KTD-Fin Barra + EFS/Agentic/CAE + Alpha-R1 + AlphaPROBE + 中信建投 GRU + 行业嵌入 LSTM Phase 4.10 |
| 2026-08-10 | 1.12.0 | Phase 4.11 RL 组合管理三候选 VD-MEAC/HRT/SAMP-HDRL |
| 2026-08-10 | 1.12.2 | Phase 4.12 MINGLE+OMD 组合优化/多样化新范式 |
| 2026-08-10 | 1.12.3 | Phase 4.13 Conformal Kelly+Path Portfolio+Drawdown Beyond Brownian 仓位sizing与风控新范式（2026-08-10 arXiv 92篇q-fin审查新增3篇）。延续轻量优先+不替换已定决策原则 |
| 2026-08-10 | 1.12.4 | §3.3 Hyperbolic 衰减完整实证（arXiv:2512.11913 R²=0.65）+ §3.1 A 股 XGBoost+TreeSHAP 实证（arXiv:2606.12843 行为因子58.2%）+ Phase 4.6 EFS US/HK/China 三市场实证（arXiv:2507.17211）+ Phase 4.14 Regime-Weighted Conformal Calibration（arXiv:2602.03903）+ Phase 4.15 Risk-Sensitive RL+Fractional Kelly（arXiv:2606.20903 统一 4.11+4.13） |
| 2026-08-10 | 1.12.5 | **第四轮施工算法深度审查——§3.7 新增 4 项施工算法缺失补全**：①SynthesisDegradationChain 合成降级链决策 ②ConstraintArbitration 7约束链冲突仲裁（硬/软分级）③DecayActionLifecycle 因子衰减→动作全生命周期 4 态状态机 ④SimpleFactorAttribution MVP 因子归因（Brinson 式，Phase 4.5 Barra 前过渡）。对齐 24 号 §3.13/§3.14 施工算法形式化深度。Phase 4.1 Mask-First 补 arXiv:2507.07107 完整消融实证（mask 单一最大贡献者 +0.44 Sharpe，超任何模型/损失；上游污染致 IC 虚高 18%+实现 Sharpe -0.44）+ Phase 4.16 新增 Sign-Aware Adjusted-MSE 损失候选（错号预测惩罚 11×，Phase 4.2 互补）+ A 股 2026-07-06 交易新规监管语境补。延续轻量优先+不替换已定决策原则 |
| 2026-08-10 | 1.12.6 | **第五轮施工算法+最新研究——§3.7 新增 2 项施工算法缺失补全**：⑤CrowdingRealTimeMonitor 因子拥挤实时监控（MVP必做——2026-07 A股57只量化基金踩雷实证驱动，与§3.3衰减监控正交：衰减管均值，拥挤管尾部）⑥RebalanceTrigger 换仓触发决策（MVP即做——convergence_window 3-5天"何时换"执行断裂点，三触发器：时间保底+漂移主+信号增强）。§3.3 补 A股高频因子2026实证（国泰海通8/10行为因子多空12-16%+多粒度28%）+ A股拥挤崩盘2026实证（中国基金报8/10 57只量化基金7月踩雷=拥挤因子崩盘实时验证）。Phase 4.11 补 Dynamic-β reward实证（PLoS One Sharpe 1.04→1.27）。Phase 4.17 新增 Certified Wasserstein Robust Portfolio（arXiv:2608.07032 2026-08-10最新，分布鲁棒与拥挤监控正交：预警+防御）。延续轻量优先+不替换已定决策原则 |
| 2026-08-10 | 1.12.7 | **第六轮施工算法完整性审查——§3.7 新增 2 项施工算法缺失补全**：⑦MultifactorPITBacktestFramework 多因子PIT安全回测框架（高优先级——与24号DabanPITBacktestFramework对称，5层PIT断言：因子值AS OF JOIN/IC权重ROLLING t-1/合成权重t因子+t-1权重/协方差ROLLING t-1/行业分类AS OF JOIN，首批回测前必做）⑧HoldingDriftMonitor 持仓偏差监控（中优先级MVP即做——因子暴露偏差+行业偏离实时监控，C2/C6约束持续满足，与RebalanceTrigger联动：偏差critical时强制换仓覆盖三触发器）。8项施工算法完整覆盖"因子→合成→优化→换仓→衰减→拥挤→归因→回测→偏差监控"九环节闭环。延续轻量优先+不替换已定决策原则 |
| 2026-08-10 | 1.12.8 | **第七轮最新研究整合——Phase 4.11 RL组合管理补CVaR RaQL自适应训练**：arXiv:2608.04305（Wu et al. 2026-08-06 ICAIF'26）6机制自适应训练控制器（步长自适应+学习率衰减同步+VaR早期短修正+覆盖率优先样本分配+渐进后缀聚合+数据驱动尺度校准），不改变CVaR估计器和Bellman不动点仅重设计训练过程，20个随机种子CVaR Bellman残差降低约85%（MeanBEQ: 1.22→0.19），日级交易Sharpe 0.93/最大回撤6.46%。与VD-MEAC互补——VD-MEAC管策略架构，CVaR RaQL管训练稳定性，CVaR目标天然适合A股尾部风险（涨停砸板/闪崩/风格骤反）。8项施工算法仍完整，本轮无新施工算法缺口。延续轻量优先+不替换已定决策原则 |
| 2026-08-10 | 1.12.9 | **第八轮字段填充断裂点审查——§3.7#3 DecayActionLifecycle 补 NEW+RETIRED 边界状态**：原4态状态机（ACTIVE→OBSERVE→DORMANT→RECOVERY）假设因子从ACTIVE开始、DORMANT可无限恢复，但新因子入池和永久退役流程未形式化。补全为6态：①NEW（新因子冷启动：低权重30%试运行+IC样本积累≥20日转ACTIVE，与SynthesisDegradationChain联动）②RETIRED（永久退役：DORMANT持续120日无恢复→从factor_registry注销+释放池配额，check_retirement()执行清理）。新增init_new_factor()+transition_with_boundaries()+check_retirement()三方法。延续轻量优先+不替换已定决策原则 |
| 2026-08-10 | 1.12.10 | **第九轮最新研究整合+文档完整性修复——Phase 4 新增 MFCCA 多尺度组合配置（Phase 4.18）+ 平稳模糊性训练原则（Phase 4.19）**：①Phase 4.18 MFCCA（arXiv:2608.04987 Kakinaka&Umeno 2026-08-05）——多重分形互相关分析带符号涨落函数作为风险泛函，保留局部去趋势协方差符号（同向与反向因子以相反符号贡献风险），q=2退化为均值-方差，符号保留对尾部风险降低贡献>跨阶聚合，突破"等权/IC/ICIR三种加权接近"瓶颈（中信建投2026-06研报确认）②Phase 4.19 Stationary Ambiguity（arXiv:2608.04832 Mueller et al. 2026-08-05）——标准鲁棒训练致命缺陷=策略推断潜在参数后模糊性系统性衰减→特化→丧失regime-shift鲁棒性，平稳模糊性原则构建模拟器使模糊性随状态变化但不随时间系统性衰减，从训练源头延缓因子衰减（比事后IC监控退役更上游）③文档完整性修复：§6待裁定补Phase 4.18/4.19条目+§7引用补arXiv:2608.04832。8项施工算法仍完整，本轮无新施工算法缺口。延续轻量优先+不替换已定决策原则 |
| 2026-08-10 | 1.12.11 | **第十轮施工算法断裂点修复+最新研究——§3.7#6 RebalanceTrigger 补 Inaction Cost 成本感知门控 + Phase 4.20 QUBO 换仓调度优化**：①§3.7#6 RebalanceTrigger 的 cost_aware 参数 v1.12.6 声明但未实现——本轮补 Perold (1988) Implementation Shortfall 框架的成本-收益门控：漂移/信号触发器命中后，额外检查 Inaction Cost (drift×daily_alpha×expected_days) > Action Cost (transaction_cost_rate×drift) 才真正换仓，时间触发器（保底）不受成本门控。A 股 0.4% 往返成本 break-even 8 天，convergence_window_max=5 < 8 提供安全垫——窗口内漂移/信号触发时若距保底仅剩 1-2 天，inaction cost 不足以覆盖 action cost → 等保底触发省交易成本。新增 _is_rebalance_worthwhile() 方法+transaction_cost_rate/daily_alpha_estimate 参数。②Phase 4.20 QUBO 换仓调度优化（arXiv:2603.16904 Weinberg 2026-03）——换仓时序建模为 QUBO 组合优化（边际 Sharpe 增益-交易成本惩罚-过频惩罚指数衰减交互项），S&P 500 实证 8 次换仓 vs 日历 24 次（成本降 44.5%），Sharpe 0.588 vs 0.575。QAOA 可用经典 QUBO 求解器替代，n=5 天窗口经典可秒解。作为 RebalanceTrigger+Inaction Cost 的远期全局优化升级路径。8项施工算法仍完整（本轮修复#6内部断裂点非新增算法），无新施工算法缺口。延续轻量优先+不替换已定决策原则 |
| 2026-08-12 | 1.13.0 | **第十一轮名实相符审查（AI-15，通用规则 #11 基础设施盘点）**：① 新增 §2.4 已施工设施盘点——D_FACTOR 域 65 production 模块逐个对号（合成/评估/治理/DAG）+ pf_core 组合优化 + factor_registry（111 条目）+ BM-SEL-02，§3.7 八项施工算法 grep 实证全部未落码（禁止误判为已建）；② 名实不符修正 4 处：§3.3 衰减监控文件名/MOD ID 误写（实 decay_monitor.py MOD-L02-009/ANA-08，CUSUM+自动淘汰层代码不存在）/ §2.3+§5.1 池容量误写 30/8（实 60/4）/ §3.2+§3.5 MOD ID 误写（实 MOD-PF-002/MOD-PF-006）/ §3.5 7 约束链与代码实际约束参数不一致注记；③ §3.6 错链修正（G07 真源 23 号非 28 号）+ §7 补 23 号引用 + 46_d_factor 相对路径断链修复；④ §6 待裁定新增 4 行（CUSUM+自动淘汰落码 / C1-C7↔MOD-PF-006 对齐 / 6 态↔5 态映射 / 15 号骨架依赖倒挂）。决策内容零变更，全部为事实性校正与缺口登记 |
| 2026-08-12 | 1.13.1 | （补录）第十二轮缺失环节+最新研究整合（AI-15）——① §4.3 补 Barra 风格中性化替代方案行（选型谱系补齐：简单行业减均值 vs Barra vs 组合约束层）；② §3.3 补信号衰减双时标框架（Alphanume 2026-06：intra-signal horizon decay vs secular alpha decay）实证半衰期监控与拥挤监控的正交分工 + gs-quant 2026-07 行业标准确认；③ 并发会话覆盖修复（§3.3/§3.5 两处 v1.13.0 修正被并发 session 回退后重补）；④ 全网搜索（2026-08-12）确认因子加权/因子挖掘方向无新决策缺口。本行系 v1.13.2 施工时补录（原 revision 行缺失 drift） |
| 2026-08-12 | 1.13.2 | **作战地图全覆盖补丁——闭合 BM-RC-06-D / BM-SEL-02-E / BM-SEL-02-M（3 环节）**：① §3.7#5 补「BM-RC-06-D 拥挤度检测深度增强扩展」——现有三代理指标（ETF 持仓/因子相关性/量化席位）维持 MVP 必做基线，三个深度增强项（策略逻辑相似度检测/去杠杆路径预案/拥挤悖论防护"人人躲拥挤=新拥挤"二阶监控）登记 design 远期（依赖多策略并发实盘数据）；② §3.1 补「BM-SEL-02-E LLM 语义去重处置裁定」——数值相关性去重（correlation_dedup.py ANA-05）production 够用，LLM 语义去重一支登记远期候选（逻辑等价→保留 IC 高者），现状即作战地图降级态；③ §3.1 补「BM-SEL-02-M 因果因子验证层处置裁定」——显式消歧 #ARCH-OE-009 裁的是 BM-MT-04 因子发现与因果发现（PC/LiNGAM），本环节未被裁剪，登记远期 Phase 4（因子入库前 DoWhy/DML 因果验证），与 11 号 §0.6.10 发现 2 Causal-TS 评估呼应，激活条件=因子库伪相关惨案 ≥1 例；④ §6 待裁定新增 3 行对应登记。三环节均按定位→裁定→契约→重评条件四要素显式映射 |
| 2026-08-12 | 1.13.3 | 作战地图环节映射补强——锚定 BM-SEL-02-A/02-B/02-C/02-D/02-I（§2.4 末映射块）、BM-SEL-02-H（§3.1 末）、BM-SEL-02-G（§3.3 末）：语义已覆盖但正文未显式编号的环节锚定到承载小节，实现环节级可追溯；不改既有正文 |
| 2026-08-14 | 1.13.4 | 压缩精简：噪音去除+施工细节梳理，零信息丢失审查通过（AI-DOCS-001） |
| 2026-08-15 | 1.13.5 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-06）——§1 状态行清单去重（真源=§8 修订记录）；§6 移除 17 行 ✅「文档已补」闭合登记行（与 §8 修订记录 v1.12.4~v1.12.11 重复，表末补指针注记），§6 现仅余真暂缓/待裁定项。IC 加权/7 约束链/衰减三层阈值/8 项施工算法参数/Phase 4.1-4.20 栈/裁定/链接零丢失 |
