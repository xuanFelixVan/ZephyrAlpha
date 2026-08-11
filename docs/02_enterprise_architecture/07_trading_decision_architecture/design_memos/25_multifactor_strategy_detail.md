---
ttl: permanent
doc_type: architecture_view
title: 多因子策略细节
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.13.1"
date: 2026-08-12
topic: multifactor_strategy_detail
scope: 07_trading_decision_architecture
---

# 多因子策略细节

> **性质**：已定型（active）。由 [00_index_trading_decision](00_index_trading_decision.md) G09 主题组派生，6 项讨论要点已逐项对齐落入 §3 决策。
> **施工图纪律**：本文档定型后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。因子工坊 BM-SEL-02 及 D_FACTOR 域 65 个 production 模块已建，本文档是"已建代码的 why 定型"，非"待施工设计"。
> **v1.12.4 补**：第三轮深度审查——§3.3 Hyperbolic 衰减模型补完整实证结果（arXiv:2512.11913 R²=0.65+拥挤预测崩溃1.7-1.8x）+ §3.1 补 A 股 XGBoost+TreeSHAP 实证（arXiv:2606.12843 行为因子58.2%vs估值10.7%）+ Phase 4.6 EFS 补完整实证（arXiv:2507.17211 US/HK/China 三市场验证）+ 新增 Phase 4.14 Regime-Weighted Conformal Calibration（arXiv:2602.03903 扩展 Conformal Kelly）+ Phase 4.15 Risk-Sensitive RL+Fractional Kelly（arXiv:2606.20903 统一 Phase 4.11+4.13）+ 2026-08-08/09/10 arXiv 最新研究整合。
> **v1.12.5 补**：第四轮施工算法深度审查——§3.7 新增 4 项施工算法缺失补全（合成降级链决策+7约束链冲突仲裁+因子衰减→动作全生命周期+MVP因子归因），对齐 24 号 §3.13/§3.14 施工算法形式化深度 + Phase 4.1 Mask-First 补 arXiv:2507.07107 完整消融实证（mask 合约是单一最大贡献者 +0.44 Sharpe，超任何模型/损失选择；上游污染致 IC 虚高 18%+实现 Sharpe -0.44）+ 新增 sign-aware Adjusted-MSE 损失候选（错号预测惩罚 11×）+ A 股 2026-07-06 交易新规监管语境补（ST 涨跌幅 5%→10%+盘后固定价格交易扩容全 A 股/ETF）。
> **v1.12.6 补**：第五轮施工算法+最新研究——§3.7 新增 2 项施工算法缺失补全（#5 因子拥挤实时监控 CrowdingRealTimeMonitor MVP必做 + #6 换仓触发决策 RebalanceTrigger MVP即做）+ §3.3 补 A 股高频因子 2026 实证（国泰海通 2026-08-10 行为因子多空 12-16%+多粒度 28%）+ §3.3 补 A 股因子拥挤崩盘 2026 实证（中国基金报 2026-08 57只量化基金踩雷）+ Phase 4.11 补 Dynamic-β reward 实证（PLoS One Sharpe 1.04→1.27）+ Phase 4.17 新增 Certified Wasserstein Robust Portfolio（arXiv:2608.07032 2026-08-10 最新）。
> **v1.12.7 补**：第六轮施工算法完整性审查——§3.7 新增 2 项施工算法缺失补全（#7 多因子 PIT 安全回测框架——与 24 号 DabanPITBacktestFramework 对称，5 层 PIT：因子值/IC权重/合成权重/协方差/行业分类；#8 持仓偏差监控——因子暴露+行业偏离实时监控，与 RebalanceTrigger 联动）。8 项施工算法完整覆盖"因子→合成→优化→换仓→衰减→拥挤→归因→回测→偏差监控"九环节闭环。
> **v1.12.8 补**：第七轮最新研究整合——Phase 4.11 RL 组合管理补 CVaR RaQL 自适应训练（arXiv:2608.04305 6 机制训练控制器，CVaR Bellman 残差降低 85%，CVaR 目标天然适合 A 股尾部风险，与 VD-MEAC 互补：前者管训练稳定性，后者管策略架构）。8 项施工算法仍完整，本轮无新施工算法缺口。
> **v1.12.9 补**：第八轮字段填充断裂点审查——§3.7#3 DecayActionLifecycle 补 NEW（新因子冷启动：低权重30%试运行+IC样本积累≥20日转ACTIVE）和 RETIRED（永久退役：DORMANT持续120日无恢复→从factor_registry注销+释放池配额）两边界状态。原4态状态机（ACTIVE→OBSERVE→DORMANT→RECOVERY）补全为6态（+NEW+RETIRED），填补新因子入池和永久退役的流程断裂点。
> **v1.12.10 补**：第九轮最新研究整合——Phase 4 新增 MFCCA 多尺度组合配置（arXiv:2608.04987 多重分形互相关分析+符号保留，突破"等权/IC/ICIR三种加权接近"瓶颈，同向与反向因子以相反符号贡献风险，非简单加权）+ 平稳模糊性训练原则（arXiv:2608.04832 防止训练中模糊性衰减导致 regime-shift 过拟合，从模拟器设计源头延缓因子衰减，比事后IC监控退役更上游）。8项施工算法仍完整，本轮无新施工算法缺口。
> **v1.12.11 补**：第十轮施工算法断裂点修复+最新研究——§3.7#6 RebalanceTrigger 补 Inaction Cost 成本感知门控（cost_aware 参数 v1.12.6 声明但未实现→补 Perold 1988 Implementation Shortfall 框架：漂移/信号触发命中后额外检查 Inaction Cost > Action Cost，A 股 0.4% 往返成本 break-even 8 天，convergence_window_max=5 < 8 提供安全垫，避免窗口末尾多余换仓）+ Phase 4.20 QUBO 换仓调度优化（arXiv:2603.16904 换仓时序 QUBO 组合优化，S&P 500 实证 8 次 vs 24 次成本降 44.5%，经典求解器可替代量子，作为 RebalanceTrigger 的远期全局优化升级路径）。8项施工算法仍完整（本轮修复#6内部断裂点非新增算法），无新施工算法缺口。
> **v1.13.0 补**：第十一轮名实相符审查（AI-15，通用规则 #11 基础设施盘点）——① 新增 §2.4 已施工设施盘点（D_FACTOR 域 65 production 模块逐个对号 + §3.7 八项施工算法落码状态 grep 实证全部为 ❌ 未落码）；② 名实不符修正 4 处：§3.3 衰减监控误写 `factor_decay_monitor.py` MOD-L02-013/ANA-11（实为 `decay_monitor.py` MOD-L02-009/ANA-08，且**CUSUM 层+自动淘汰层代码不存在**，仅半衰期 min_half_life=10）/ §2.3+§5.1 池容量误写活跃≤30 休眠≤8（实为 60/4，ADR-FAC-006+_config.yaml）/ §3.2+§3.5 组合优化器误写 MOD-L02-012（实为 MOD-PF-002+约束求解 MOD-PF-006，D_PF_CORE 域）/ §3.5 7 约束链 C1-C7 标注与代码实际约束（行业±10%/MDD5%/相关性0.7 等）不一致的注记；③ §3.6 错链修正（G07 相关性验证真源是 23 号非 28 号）+ §7 补 23 号引用 + 46_d_factor 断链修复；④ §6 待裁定新增 4 行（CUSUM+自动淘汰落码 / C1-C7↔MOD-PF-006 对齐 / 运行时 6 态↔registry 5 态映射 / 15 号骨架依赖倒挂）。决策内容零变更，全部为事实性校正与缺口登记。
> **v1.13.1 补**：第十二轮缺失环节+最新研究整合（AI-15）——① §4.3 补 Barra 风格中性化替代方案行（选型谱系补齐：简单行业减均值 vs Barra vs 组合约束层）；② §3.3 补信号衰减双时标框架（Alphanume 2026-06：intra-signal horizon decay vs secular alpha decay）实证半衰期监控与拥挤监控的正交分工 + gs-quant 2026-07 行业标准确认；③ 并发会话覆盖修复（§3.3/§3.5 两处 v1.13.0 修正被并发 session 回退后重补）；④ 全网搜索（2026-08-12）确认因子加权/因子挖掘方向无新决策缺口（中信建投 2026-06 三加权接近+GRU 最优=Phase 4.9 已登记；AlphaMemo arXiv:2606.20625=Phase 4.6 同类）。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G09 多因子策略细节 |
| 所属 | 作战地图 05（BM-SEL-02 因子计算/注册表/IC-IR/衰减/合成/治理） |
| 依赖 | G04（[20_first_batch_strategies](20_first_batch_strategies.md) §2.3 多因子 sleeve）、G05（信号工坊）、G01（[15_data_feature_layer_spec](15_data_feature_layer_spec.md) 因子工程总纲，status: draft） |
| 对标 | WorldQuant Alpha 工厂 / Numerai 多因子 / 华泰金工多因子 / BigQuant ICIR 加权合成（2026-07） |
| 正交 | ✅ 与 regime 正交（[28 §3.4]）：多因子不读情绪周期，不读 regime，纯横截面选股 |
| 优先级 | P2（承载主力资金的低频基石） |
| 状态 | active 1.13.1（6 项讨论要点已对齐 + §3.7 施工算法 8 项补全：合成降级链+约束冲突仲裁+衰减动作生命周期(6态状态机含NEW冷启动+RETIRED退役)+MVP归因+**拥挤实时监控MVP必做**+**换仓触发MVP即做+Inaction Cost成本门控**+**PIT回测框架**+**持仓偏差监控** + Mask-First 可交易性掩码（Phase 4.1 arXiv:2507.07107 mask 单一最大贡献者+0.44）+ §3.3 A股高频因子2026实证（国泰海通8/10行为因子多空12-16%）+ §3.3 A股拥挤崩盘实证（57只量化基金7月踩雷）+ Phase 4.1-4.20 远期候选栈 20 子项含 Dynamic-β reward+Wasserstein鲁棒组合+CVaR RaQL自适应训练+MFCCA多尺度组合配置+平稳模糊性训练+Conformal Kelly完整实证+QUBO换仓调度优化 + 2026-08 arXiv 最新研究整合 + **v1.13.x 名实相符修正：§2.4 已施工设施盘点+4处误写校正（decay_monitor MOD-L02-009/池容量60+4/MOD-PF-002/约束链注记）+23号错链修正**） |

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

**A 股 XGBoost+TreeSHAP 实证背书（v1.12.4 补）**：[arXiv:2606.12843](https://arxiv.org/abs/2606.12843)（Han et al. 2026-06）在 3,632 只 A 股（2009-2019）上用 XGBoost+TreeSHAP 做可解释因子分解——rank IC=0.119、ICIR=1.12（t=8.26）、top quintile 56.4% 超越截面中位数、+2.38%/月 long-short spread（Newey-West t=5.94，年化 Sharpe 2.23）、Carhart 四因子 alpha +2.31%/月（t=7.48）。**关键发现**：行为因子（换手率+动量）贡献 58.2% 预测归因 vs 估值因子仅 10.7%，50 行业组一致。**对 25 号的启示**：① 验证 IC 加权合成方法在 A 股有效（rank IC=0.119 远超 0.05 有效阈值）② 行为因子>估值因子的发现支持当前因子池以技术/动量因子为主的设计 ③ SHAP 可解释分解为 Phase 4.5 KTD-Fin Barra 归因提供 A 股实证基础。

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

**信号衰减双时标框架（v1.13.1 补，Alphanume 2026-06）**：信号衰减应区分两个时标——① **intra-signal horizon decay**（单次观测的预测力随时间消散，决定半衰期与换仓频率错配是最常见的实施错误）② **secular alpha decay**（信号被市场学习/拥挤后的长期 alpha 侵蚀，McLean-Pontiff：发表后衰减 58%）。该框架实证了本文档的正交分工：§3.3 半衰期监控管时标①（信号还能用多久→convergence_window 3-5 天的依据），§3.7#5 拥挤监控管时标②（因子是否太挤→崩盘尾部风险）。另：gs-quant 2026-07 半衰期工程实践确认指数拟合 + 滚动窗口交叉检验为行业标准做法（与 `ic_decay.py` 实现同构）。

**Hyperbolic 衰减完整实证结果（v1.12.4 补）**：[arXiv:2512.11913](https://arxiv.org/abs/2512.11913)（Lee 2025-12 KAIST）用 8 个 Fama-French 因子（1963-2024）完整验证 Hyperbolic 衰减模型——① **动量因子 hyperbolic 衰减 R²=0.65**，优于线性（0.51）和指数（0.61），验证博弈论基础；② **并非所有因子同等拥挤**：机械因子（动量/反转）符合模型，判断因子（价值/质量）不符合——与 Hua & Sun "进入壁垒"分类一致；③ **2015 后拥挤加速**：样本外模型高估剩余 alpha（0.30 vs 0.15），与因子 ETF 增长负相关（ρ=-0.63）；④ **平均收益已被有效定价**：基于拥挤的因子选择无法产生 alpha（Sharpe 0.22 vs 因子动量基准 0.39）；⑤ **拥挤预测尾部风险**：样本外（2001-2024），拥挤的反转因子崩溃概率高 1.7-1.8 倍，拥挤的动量因子崩溃风险低（0.38 倍，p=0.006）。**对 25 号的启示**：① Hyperbolic 衰减拟合应优先用于机械因子（动量/反转），判断因子（价值/质量）用指数衰减即可 ② 拥挤预测崩溃而非均值——CUSUM 衰减监控应联动尾部风险预警 ③ 因子 ETF 增长是拥挤加速的代理变量，Phase 4.7 Alpha-R1 动态门控可将 ETF 持仓变化作为输入。

**A 股高频因子 2026 实证（v1.12.6 补，国泰海通 2026-08-10 周报）**：国泰海通证券高频选股因子周报（2026-08-10）披露 A 股高频因子 2026 年多空收益实证——**行为/微结构因子全面领先**：开盘后买入意愿强度因子 16.29% / 日内下行波动占比因子 14.94% / 日内高频偏度因子 14.53% / 尾盘成交占比因子 13.58% / 开盘后买入意愿占比因子 12.60% / 日内收益因子 7.75%。**多粒度模型**（5 日标签）2026 年多空收益 28.18%、多头超额 8.43%；多粒度模型（10 日标签）2026 年多空 25.52%、多头超额 6.67%。**对 25 号的启示**：① 验证 §3.1 行为因子>估值因子结论（arXiv:2606.12843 58.2% vs 10.7%）——A 股高频行为因子 2026 年多空 12-16%，远超传统估值因子 ② 多粒度模型 28% 多空收益验证 Phase 4.4 STAR CrossAttention 混频融合方向的 A 股有效性 ③ 日内微结构因子（开盘后买入意愿/尾盘成交占比）可与打板 sleeve §3.9 竞价三维体系跨 sleeve 复用。

**A 股因子拥挤崩盘 2026 实证（v1.12.6 补，中国基金报 2026-08）**：2026 年 7 月 A 股科技板块骤跌，**57 只主动量化基金单月净值跌幅超 20%**，15 只超 30%——根因是上半年超配科技成长（动量/景气因子拥挤），7 月风格极致切换时拥挤因子迅速失效，量化模型基于历史数据训练的信号存在天然滞后性，无法在风格骤反时及时降仓。8 月初 5 日修复反弹超 10%。工银量化策略逆市上涨 8.46%（侧重质量价值风格，均衡配置）。**对 25 号的启示**：① 这正是 §3.3 Hyperbolic 衰减"拥挤预测崩溃 1.7-1.8x"的 A 股实时验证——57 只基金踩雷=拥挤因子崩盘 ② **因子拥挤实时监控是 MVP 必做项**（非远期候选）——§3.7#5 补 `CrowdingRealTimeMonitor` 施工算法 ③ 均衡配置（工银案例）验证 §3.5 7 约束链 C2 行业暴露约束的价值——单行业拥挤是崩盘放大器。

### 3.4 讨论要点④：多因子换手率与容量

**裁定**：convergence_window = 3-5 天，低换手，大容量。

| 维度 | 参数 | 依据 |
|---|---|---|
| convergence_window | 3-5 天 | [30 §6.4] Tier 1+2 给时间达 |
| sleeve 容量 | 500 万-2000 万（待实盘校准） | 横截面选股流动性远好于打板 |
| 持仓数 | 30-80 只 | 分散度 + 单票 ≤2% NAV（C12） |
| 换手率 | 日均 15-25% | convergence_window 3-5 天决定 |

**与打板 sleeve 差异化**：打板 sleeve 高换手（convergence 1-2 天）、小容量（50-200 万）、持仓 1-3 天；多因子 sleeve 低换手（convergence 3-5 天）、大容量（500-2000 万）、持仓 5-20 天。两者相关性低，构成差异化 sleeve 组合。

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

> 2026-08-10 第四轮施工算法深度审查——对齐 24 号 §3.13/§3.14 的施工算法形式化深度。25 号因子工坊 65 个 production 模块已建，但"因子→合成→优化→仓位→风控→归因"六环节间的**编排决策算法**未形式化。本节补全 8 项真实缺口（4 高+4 中），填补 production 模块间的决策断裂点。不新增模块，仅形式化编排逻辑。v1.12.6 补#5/#6——拥挤实时监控（2026-07 A 股 57 只量化基金踩雷实证驱动）+换仓触发决策（convergence_window 执行断裂点）。v1.12.7 补#7/#8——多因子 PIT 安全回测框架（与 24 号 DabanPITBacktestFramework 对称，5 层 PIT）+持仓偏差监控（因子暴露+行业偏离实时监控，与 RebalanceTrigger 联动）。

#### 缺失#1：合成降级链决策算法（高优先级，合成方法编排断裂点）

**问题**：§3.1 有 3 种合成方法（IC 加权/等权/回归）已在 `multifactor_synthesis.py` 全部 production，但"何时从 IC 加权降级到等权""何时从回归降级到等权"的**触发条件与降级路径**未形式化。当前 production 代码各方法独立调用，缺统一降级编排。

```python
@dataclass
class SynthesisDegradationChain:
    """合成降级链决策（v1.12.5 补，3 方法统一降级编排）

    编排 multifactor_synthesis.py 的 3 个 production 方法。
    降级链：回归优化 → IC 加权 → 等权（兜底）。
    与 §3.3 factor_decay_monitor 联动——IC 衰减触发降级。
    """
    # IC 加权降级触发条件
    ic_min_samples: int = 20              # IC 样本<20→IC 加权不可靠→降级等权
    ic_weight_concentration: float = 0.70 # 单因子 IC 权重>70%→过度集中→降级等权
    ic_abs_floor: float = 0.02            # 全池 |IC|<0.02→信号衰竭→降级等权
    # 回归优化降级触发条件
    regression_min_obs: int = 120         # 前瞻收益观测<120→回归过拟合→降级 IC 加权
    condition_number_max: float = 50.0    # 因子矩阵条件数>50→共线性→降级 IC 加权

    def decide(self, factor_panel, ic_history: list, forward_returns=None) -> dict:
        """降级链决策（v1.12.5 补）"""
        # ① 回归优化可行性检查（最高优先级，IR 最大）
        if forward_returns is not None and len(forward_returns) >= self.regression_min_obs:
            cond = self._condition_number(factor_panel)
            if cond < self.condition_number_max:
                return {'method': 'synthesize_regression', 'reason': f'观测{len(forward_returns)}≥120+条件数{cond:.1f}<50→回归优化'}
            return {'method': 'synthesize_ic_weighted',
                    'reason': f'条件数{cond:.1f}≥50 共线性→降级 IC 加权'}
        # ② IC 加权可行性检查（默认方法）
        if len(ic_history) >= self.ic_min_samples:
            mean_ic = np.mean([abs(x) for x in ic_history])
            if mean_ic < self.ic_abs_floor:
                return {'method': 'synthesize_equal_weight',
                        'reason': f'全池|IC|均值{mean_ic:.3f}<0.02 信号衰竭→降级等权'}
            weights = self._ic_weights(ic_history)
            concentration = max(weights) / sum(abs(w) for w in weights)
            if concentration > self.ic_weight_concentration:
                return {'method': 'synthesize_equal_weight',
                        'reason': f'单因子权重集中度{concentration:.0%}>70%→降级等权'}
            return {'method': 'synthesize_ic_weighted', 'reason': 'IC 样本≥20+分布合理→IC 加权'}
        # ③ 等权兜底
        return {'method': 'synthesize_equal_weight',
                'reason': f'IC 样本{len(ic_history)}<{self.ic_min_samples}→等权兜底'}
```

> **施工建议**：在 `multifactor_synthesis.py` 增加统一入口 `synthesize_with_degradation()`，内部调用 `SynthesisDegradationChain.decide()` 后分派到 3 个 production 方法。纯增量 ~30 行，不替换现有方法。

#### 缺失#2：7 约束链冲突仲裁算法（高优先级，组合优化器约束编排断裂点）

**问题**：§3.5 有 7 约束链（C1-C7）在 `portfolio_optimizer.py` production，但约束间的**硬/软分级与冲突仲裁**未形式化。当 C1 单票≤2% 与 C7 最小 20 只冲突（universe<50 时难以同时满足），或 C3 波动率与 C6 因子暴露冲突时，cvxpy 求解器可能返回不可行解或静默放宽某约束。需明确仲裁优先级。

```python
@dataclass
class ConstraintArbitration:
    """7 约束链冲突仲裁（v1.12.5 补，硬/软分级+不可行回退）

    编排 portfolio_optimizer.py 的 7 约束链。
    硬约束违反=不可行→缩减 universe 重解；软约束违反=次优→记录但接受。
    """
    # 硬约束（违反=不可行，必须满足）
    HARD = {'C1': '单票≤2% NAV', 'C5': '单票≤日成交5%', 'C7': '≥20只'}
    # 软约束（违反=次优，记录但接受，cvxpy 加松弛变量）
    SOFT = {'C2': '行业≤±5%', 'C3': '波动率≤25%', 'C4': '换手≤30%', 'C6': '因子暴露≤±10%'}
    soft_penalty_weight: float = 100.0   # 软约束松弛惩罚权重
    max_universe_shrink: int = 5         # 硬约束不可行时最多剔 5 只标的重解

    def arbitrate(self, optimizer_result: dict, universe_size: int) -> dict:
        """约束冲突仲裁（v1.12.5 补）"""
        violations = optimizer_result.get('constraint_violations', {})
        hard_violations = {k: v for k, v in violations.items() if k in self.HARD}
        soft_violations = {k: v for k, v in violations.items() if k in self.SOFT}
        # ① 硬约束全部满足→接受
        if not hard_violations and not soft_violations:
            return {'status': 'FEASIBLE', 'action': 'ACCEPT', 'result': optimizer_result}
        # ② 仅有软约束违反→加松弛变量重解（接受次优）
        if not hard_violations:
            return {'status': 'SOFT_VIOLATION', 'action': 'ACCEPT_WITH_PENALTY',
                    'violations': soft_violations,
                    'reason': f'软约束违反{list(soft_violations)}→加松弛接受'}
        # ③ 硬约束违反→检查 universe 是否可缩减
        if universe_size - self.max_universe_shrink >= 20:  # C7 下限
            return {'status': 'HARD_INFEASIBLE', 'action': 'SHRINK_UNIVERSE',
                    'drop_count': self.max_universe_shrink,
                    'reason': f'硬约束{list(hard_violations)}违反→剔{self.max_universe_shrink}只重解'}
        # ④ 硬约束违反且 universe 不可缩→降仓位比例
        return {'status': 'HARD_INFEASIBLE', 'action': 'REDUCE_GROSS',
                'gross_ratio': 0.8,
                'reason': f'硬约束违反+universe不可缩→总仓位降至80%保硬约束'}
```

> **施工建议**：在 `portfolio_optimizer.py` 求解后增加 `ConstraintArbitration.arbitrate()` 后处理层，硬约束不可行时触发 universe 缩减或 gross 降仓。纯增量 ~40 行。

#### 缺失#3：因子衰减→动作全生命周期算法（中优先级，衰减监控→池管理编排断裂点）

**问题**：§3.3 三层衰减监控（半衰期/CUSUM/淘汰）在 `factor_decay_monitor.py` production，池管理在 `factor_pool_manager.py` production，但两者间的**动作状态机**未形式化——检测到衰减后是降权、观察、淘汰还是复激活？当前两模块各自独立，缺统一生命周期编排。

```python
@dataclass
class DecayActionLifecycle:
    """因子衰减→动作全生命周期（v1.12.5 补，4 态状态机）

    编排 factor_decay_monitor.py（检测）→ factor_pool_manager.py（池管理）。
    4 态：ACTIVE（正常参与合成）→ OBSERVE（降权50%观察）→ DORMANT（休眠池）
          → RECOVERY（复激活观察）→ ACTIVE / DORMANT。
    与 §3.3 三层监控联动，与缺失#1 SynthesisDegradationChain 联动。
    """
    # 状态转移阈值
    halflife_observe: int = 20            # 半衰期<20→OBSERVE
    cusum_alert_to_dormant: int = 40      # CUSUM 预警后 40 交易日无恢复→DORMANT
    ic_floor_dormant: int = 40            # 连续 40 日 |IC|<0.02→DORMANT
    recovery_ic_threshold: float = 0.03   # DORMANT 后连续 10 日 |IC|>0.03→RECOVERY
    recovery_observe_days: int = 10
    ic_dormant_floor: float = 0.02        # |IC|<0.02 持续→DORMANT
    dormant_skip_synthesis: bool = True   # DORMANT 因子不参与合成

    def transition(self, current_state: str, decay_metrics: dict,
                   days_in_state: int) -> dict:
        """衰减动作状态转移（v1.12.5 补）"""
        halflife = decay_metrics.get('halflife', 999)
        cusum = decay_metrics.get('cusum_alert', False)
        mean_ic = decay_metrics.get('mean_abs_ic_40d', 0.05)
        # ACTIVE → OBSERVE
        if current_state == 'ACTIVE':
            if halflife < self.halflife_observe:
                return {'state': 'OBSERVE', 'weight_mult': 0.5,
                        'reason': f'半衰期{halflife}<{self.halflife_observe}→降权50%观察'}
            return {'state': 'ACTIVE', 'weight_mult': 1.0, 'reason': '衰减正常'}
        # OBSERVE → DORMANT / ACTIVE
        if current_state == 'OBSERVE':
            if mean_ic < self.ic_dormant_floor and days_in_state >= self.cusum_alert_to_dormant:
                return {'state': 'DORMANT', 'weight_mult': 0.0,
                        'reason': f'观察{days_in_state}日+|IC|{mean_ic:.3f}<{self.ic_dormant_floor}→休眠'}
            if halflife >= self.halflife_observe and not cusum:
                return {'state': 'ACTIVE', 'weight_mult': 1.0,
                        'reason': '半衰期恢复+CUSUM 未预警→复激活'}
            return {'state': 'OBSERVE', 'weight_mult': 0.5, 'reason': '观察中'}
        # DORMANT → RECOVERY
        if current_state == 'DORMANT':
            if mean_ic >= self.recovery_ic_threshold and days_in_state >= self.recovery_observe_days:
                return {'state': 'RECOVERY', 'weight_mult': 0.3,
                        'reason': f'|IC|{mean_ic:.3f}≥0.03 持续10日→复激活观察(30%权重)'}
            return {'state': 'DORMANT', 'weight_mult': 0.0, 'reason': '休眠中'}
        # RECOVERY → ACTIVE / DORMANT
        if current_state == 'RECOVERY':
            if halflife >= self.halflife_observe:
                return {'state': 'ACTIVE', 'weight_mult': 1.0, 'reason': '恢复确认→全权重'}
            if mean_ic < 0.02:
                return {'state': 'DORMANT', 'weight_mult': 0.0, 'reason': '恢复失败→重返休眠'}
            return {'state': 'RECOVERY', 'weight_mult': 0.3, 'reason': '复激活观察中'}
        return {'state': current_state, 'weight_mult': 1.0, 'reason': '未知状态'}

    # === v1.12.9 补：状态机边界处理（NEW 冷启动 + RETIRED 永久退役）===

    # 新因子冷启动参数
    new_factor_warmup_days: int = 20          # 新因子冷启动期（IC 样本积累）
    new_factor_weight_mult: float = 0.3       # 冷启动期权重乘子（低权重试运行）
    # 永久退役参数
    dormant_max_days: int = 120               # DORMANT 持续 120 日无恢复→永久退役
    retired_skip_all: bool = True             # RETIRED 因子完全退出（不参与合成+不占池配额）

    def init_new_factor(self, factor_name: str) -> dict:
        """新因子冷启动初始化（v1.12.9 补，填补 NEW 状态缺失）

        新因子加入活跃池时不能直接 ACTIVE——IC 样本不足时 SynthesisDegradationChain
        会降级为等权，但 DecayActionLifecycle 此前无 NEW 状态处理。
        冷启动期：低权重(30%)试运行，IC 样本积累≥20 日后转 ACTIVE。
        与 §3.7#1 SynthesisDegradationChain 联动——冷启动期 IC<20 触发等权降级。
        """
        return {'state': 'NEW', 'weight_mult': self.new_factor_weight_mult,
                'days_in_state': 0,
                'reason': f'新因子{factor_name}冷启动→{self.new_factor_weight_mult:.0%}权重试运行'}

    def transition_with_boundaries(self, current_state: str, decay_metrics: dict,
                                    days_in_state: int) -> dict:
        """含边界的完整状态转移（v1.12.9 补，6 态状态机：NEW+ACTIVE+OBSERVE+DORMANT+RECOVERY+RETIRED）

        在 transition() 基础上补 NEW 和 RETIRED 两边界状态：
        NEW → ACTIVE（冷启动期结束+IC 达标）
        DORMANT → RETIRED（持续 dormant_max_days 无恢复→永久退役）
        """
        # NEW → ACTIVE / OBSERVE
        if current_state == 'NEW':
            if days_in_state >= self.new_factor_warmup_days:
                mean_ic = decay_metrics.get('mean_abs_ic_40d', 0)
                if mean_ic >= 0.02:
                    return {'state': 'ACTIVE', 'weight_mult': 1.0,
                            'reason': f'冷启动{days_in_state}日+|IC|{mean_ic:.3f}≥0.02→转ACTIVE'}
                return {'state': 'OBSERVE', 'weight_mult': 0.5,
                        'reason': f'冷启动结束但|IC|{mean_ic:.3f}<0.02→转OBSERVE观察'}
            return {'state': 'NEW', 'weight_mult': self.new_factor_weight_mult,
                    'reason': f'冷启动期{days_in_state}/{self.new_factor_warmup_days}日→低权重试运行'}
        # DORMANT → RETIRED（永久退役检查）
        if current_state == 'DORMANT' and days_in_state >= self.dormant_max_days:
            return {'state': 'RETIRED', 'weight_mult': 0.0,
                    'reason': f'DORMANT 持续{days_in_state}日≥{self.dormant_max_days}→永久退役'}
        # 其他状态走原 transition() 逻辑
        return self.transition(current_state, decay_metrics, days_in_state)

    def check_retirement(self, factor_name: str, state: str, days_dormant: int) -> dict:
        """永久退役检查（v1.12.9 补，DORMANT→RETIRED 流程）

        DORMANT 持续 dormant_max_days 无恢复→永久退役：
        ① 从 factor_pool_manager 活跃/休眠池移除
        ② 在 factor_registry 标记 status=retired
        ③ 释放池配额（活跃池≤30/休眠池≤8）
        与 §3.7#3 DecayActionLifecycle.transition_with_boundaries 联动。
        """
        if state == 'RETIRED' or (state == 'DORMANT' and days_dormant >= self.dormant_max_days):
            return {'action': 'RETIRE', 'factor': factor_name,
                    'reason': f'DORMANT {days_dormant}日≥{self.dormant_max_days}→永久退役',
                    'cleanup': ['remove_from_active_pool', 'remove_from_dormant_pool',
                                'mark_registry_retired', 'release_pool_quota']}
        return {'action': 'KEEP', 'factor': factor_name, 'reason': '未达退役条件'}
```

> **施工建议**：在 `factor_pool_manager.py` 增加因子状态字段 `decay_state`，每日调用 `DecayActionLifecycle.transition_with_boundaries()` 更新状态+权重乘子。新因子入池调用 `init_new_factor()` 初始化为 NEW 状态。DORMANT 因子每日调用 `check_retirement()` 检查是否永久退役。纯增量 ~50 行，与 `factor_decay_monitor.py` 输出对接。v1.12.9 补 NEW+RETIRED 边界处理 ~30 行。

#### 缺失#4：MVP 因子归因算法（中优先级，归因断裂点——Phase 4.5 Barra 前的过渡方案）

**问题**：§4.1 将 Barra 归因列为 Phase 4.5 远期候选（需 Barra 基础设施），但 MVP 阶段即需因子归因来验证 §3.3 衰减监控的因子贡献、验证 §3.1 合成方法的因子有效性。无归因则无法判断哪些因子真正贡献 alpha。需 Phase 4.5 前的轻量过渡方案。

```python
@dataclass
class SimpleFactorAttribution:
    """MVP 因子归因（v1.12.5 补，Brinson 式因子 PnL 分解，Phase 4.5 Barra 前过渡方案）

    不依赖 Barra 风险模型基础设施，用因子暴露×因子收益的 Brinson 式分解。
    归因 PnL_i = Σ_t (w_{i,t} - w_{benchmark,t}) × r_{i,t}
    其中 w_{i,t}=t 日因子 i 的组合暴露，r_{i,t}=t 日因子 i 的截面收益。
    与 §3.3 衰减监控联动——归因贡献持续低的因子触发衰减复检。
    """
    benchmark: str = 'csi300'   # 基准（沪深300）

    def attribute(self, portfolio_returns: list, factor_exposures: list,
                  factor_returns: list, benchmark_exposures: list = None) -> dict:
        """因子 PnL 归因（v1.12.5 补）"""
        n_factors = len(factor_returns[0]) if factor_returns else 0
        attribution = {}
        total_pnl = sum(portfolio_returns)
        # 各因子归因贡献 = Σ_t (主动暴露 × 因子收益)
        for i in range(n_factors):
            active_exposures = [(factor_exposures[t][i] - (benchmark_exposures[t][i]
                                if benchmark_exposures else 0))
                               for t in range(len(portfolio_returns))]
            factor_pnl = sum(active_exposures[t] * factor_returns[t][i]
                            for t in range(len(portfolio_returns)))
            attribution[f'factor_{i}'] = {
                'pnl': factor_pnl,
                'contribution_ratio': factor_pnl / total_pnl if total_pnl != 0 else 0,
                'avg_active_exposure': np.mean(active_exposures),
            }
        # 残差 = 总 PnL - 因子归因和
        explained = sum(v['pnl'] for v in attribution.values())
        attribution['residual'] = {
            'pnl': total_pnl - explained,
            'contribution_ratio': (total_pnl - explained) / total_pnl if total_pnl != 0 else 0,
        }
        # 排序+标记低贡献因子（联动衰减复检）
        ranked = sorted(attribution.items(), key=lambda x: x[1]['pnl'], reverse=True)
        return {'attribution': attribution, 'ranked': ranked,
                'total_pnl': total_pnl, 'explained_ratio': explained / total_pnl if total_pnl != 0 else 0}
```

> **施工建议**：新增 `simple_factor_attribution.py`（MOD-L02-014，D-FACTOR-ANA-12），Phase 4.5 Barra 就绪前作为过渡归因方案。纯增量 ~45 行，输入来自 `factor_decay_monitor.py` 的因子收益+`portfolio_optimizer.py` 的因子暴露。

#### 缺失#5：因子拥挤实时监控算法（高优先级，v1.12.6 新增——拥挤崩盘断裂点修复）

**问题**：§3.3 三层衰减监控检测 IC 衰减（信号变弱），但**因子拥挤**（太多人用同一因子）是不同的风险——拥挤因子在风格切换时崩溃概率高 1.7-1.8x（arXiv:2512.11913），2026-07 A 股 57 只量化基金踩雷即实时验证（中国基金报 2026-08）。当前 `factor_decay_monitor.py` 只管"信号衰减"不管"拥挤崩盘"，两者正交——衰减是均值回归，拥挤是尾部风险。§3.3 L96 已指出"因子 ETF 增长是拥挤加速的代理变量"但未形式化为监控器。

```python
@dataclass
class CrowdingRealTimeMonitor:
    """因子拥挤实时监控（v1.12.6 补，与 §3.3 衰减监控正交——衰减管均值，拥挤管尾部）

    理论背书：
    - arXiv:2512.11913：拥挤反转因子崩溃概率高 1.7-1.8x，与因子 ETF 增长负相关 ρ=-0.63
    - 中国基金报 2026-08：57 只量化基金 7 月踩雷=拥挤科技因子崩盘
    - §3.7#3 DecayActionLifecycle 检测 IC 衰减→降权；本类检测拥挤→尾部风险预警
    与 §3.7#3 的区别：DecayActionLifecycle 管"因子是否还有效"（IC 衰减），
    本类管"因子是否太拥挤"（崩盘风险）。两者可同时触发——IC 未衰减但拥挤度高=崩盘前兆。
    """
    # 拥挤度代理指标（arXiv:2512.11913 验证 ETF 持仓 ρ=-0.63）
    etf_holding_window: int = 60           # ETF 持仓变化滚动窗口
    etf_holding_alert: float = 0.20        # ETF 持仓增长>20%→拥挤加速
    # 因子相关性拥挤（因子间相关性升高=共识形成=拥挤）
    factor_corr_window: int = 40           # 因子收益相关性滚动窗口
    factor_corr_alert: float = 0.70        # 因子间平均相关性>0.70→拥挤
    # 龙虎榜/资金流拥挤（A 股特色代理）
    quant_seat_ratio_alert: float = 0.35   # 量化席位占比>35%（2026 量化占比）→拥挤
    # 崩盘风险阈值
    crash_risk_high: float = 0.70          # 拥挤综合分>0.70→高崩盘风险→降仓

    def assess(self, factor_name: str, etf_holding_data: list,
               factor_corr_matrix, quant_seat_ratio: float = 0) -> dict:
        """拥挤度综合评估（v1.12.6 补）"""
        scores = {}
        # ① ETF 持仓变化（主要代理变量）
        if len(etf_holding_data) >= self.etf_holding_window:
            recent = etf_holding_data[-20:]
            baseline = etf_holding_data[-self.etf_holding_window:-20]
            growth = (sum(recent) / max(sum(baseline), 1)) - 1
            scores['etf_growth'] = min(growth / self.etf_holding_alert, 1.0)
        # ② 因子间相关性（共识=拥挤）
        if factor_corr_matrix is not None:
            avg_corr = np.mean(factor_corr_matrix[np.triu_indices_from(factor_corr_matrix, k=1)])
            scores['factor_corr'] = min(avg_corr / self.factor_corr_alert, 1.0)
        # ③ 量化席位占比（A 股特色）
        scores['quant_seat'] = min(quant_seat_ratio / self.quant_seat_ratio_alert, 1.0)
        # 综合拥挤分（0-1，越高越拥挤）
        crowding_score = np.mean(list(scores.values())) if scores else 0
        # 分级响应
        if crowding_score > self.crash_risk_high:
            return {'factor': factor_name, 'crowding': crowding_score,
                    'action': 'REDUCE_WEIGHT_50', 'reason': f'拥挤分{crowding_score:.2f}>0.70→降权50%+尾部风险预警'}
        if crowding_score > 0.50:
            return {'factor': factor_name, 'crowding': crowding_score,
                    'action': 'ALERT', 'reason': f'拥挤分{crowding_score:.2f}>0.50→监控+CUSUM联动'}
        return {'factor': factor_name, 'crowding': crowding_score,
                'action': 'MONITOR', 'reason': f'拥挤分{crowding_score:.2f}正常'}
```

> **施工建议**：在 `factor_decay_monitor.py` 增加拥挤度检测通道，与现有 CUSUM 并列。纯增量 ~40 行。**MVP 必做**（非远期候选）——2026-07 A 股 57 只量化基金踩雷证明拥挤监控是生存级需求。输入：ETF 持仓数据（公开）+ 因子收益相关性（已有）+ 龙虎榜量化席位占比（§3.11 detect_quant_seat_warning 复用）。

#### 缺失#6：换仓触发决策算法（中优先级，v1.12.6 新增——convergence_window 执行断裂点）

**问题**：§3.4 裁定 convergence_window = 3-5 天，但"何时在 3-5 天窗口内触发换仓"未形式化——是固定每 3 天换仓？还是组合漂移超阈值时换仓？还是因子信号变化显著时换仓？当前无统一触发决策，依赖人工判断或固定时间触发，可能过早换仓（增加成本）或过晚换仓（alpha 流失）。

```python
@dataclass
class RebalanceTrigger:
    """换仓触发决策（v1.12.6 补，v1.12.11 补 Inaction Cost 成本感知门控）

    三触发器任一满足→触发换仓：
    ① 时间触发（保底）：距上次换仓≥convergence_window_max 天
    ② 漂移触发（主）：组合权重漂移>drift_threshold
    ③ 信号触发（增强）：因子排名变化>rank_change_threshold
    v1.12.11 补：cost_aware 此前声明但未实现——补 Inaction Cost 门控。
    理论背书：Perold (1988) Implementation Shortfall——不换仓的机会成本可量化，
    IS = (P_close - P_0) × Q_unexecuted（未换仓份额因价格漂移的 alpha 流失）。
    门控逻辑：漂移/信号触发器命中后，若 cost_aware=True，额外检查
    Inaction Cost > Action Cost 才真正换仓；时间触发器（保底）不受成本门控。
    与 §3.5 portfolio_optimizer.py 联动——触发后调用 7 约束链重优化。
    与 §3.7#2 ConstraintArbitration 联动——换仓后约束冲突仲裁。
    """
    convergence_window_max: int = 5        # 保底换仓周期
    convergence_window_min: int = 3        # 最短换仓间隔（防过度换仓）
    drift_threshold: float = 0.15          # 组合权重漂移>15%→触发
    rank_change_threshold: int = 10        # top-30 因子排名变化>10 位→触发
    cost_aware: bool = True                # 换仓成本感知（A 股 0.4% 往返）
    # v1.12.11 补：Inaction Cost 参数（Perold IS 框架）
    transaction_cost_rate: float = 0.004   # A 股往返交易成本 0.4%（印花税+佣金+滑点）
    daily_alpha_estimate: float = 0.0005   # 日均因子 alpha 估计 0.05%（IC~0.03 保守估计）

    def should_rebalance(self, days_since_last: int, current_weights: dict,
                         target_weights: dict, current_ranking: list,
                         previous_ranking: list) -> dict:
        """换仓触发决策（v1.12.6 补，v1.12.11 补成本门控）"""
        # ① 最短间隔保护（防过度换仓）
        if days_since_last < self.convergence_window_min:
            return {'trigger': None, 'action': 'WAIT',
                    'reason': f'距上次换仓{days_since_last}天<{self.convergence_window_min}→等待'}
        # ② 时间触发（保底，不受成本门控——保底换仓必须执行）
        if days_since_last >= self.convergence_window_max:
            return {'trigger': 'TIME', 'action': 'REBALANCE',
                    'reason': f'距上次换仓{days_since_last}天≥{self.convergence_window_max}→保底换仓'}
        # ③ 漂移触发（主）
        common = set(current_weights) & set(target_weights)
        drift = sum(abs(current_weights.get(s, 0) - target_weights.get(s, 0)) for s in common) / 2
        if drift > self.drift_threshold:
            # v1.12.11 补：成本门控——Inaction Cost > Action Cost 才换仓
            if self.cost_aware and not self._is_rebalance_worthwhile(drift, days_since_last):
                return {'trigger': None, 'action': 'HOLD',
                        'reason': f'漂移{drift:.1%}超阈值但成本未回本→等待'}
            return {'trigger': 'DRIFT', 'action': 'REBALANCE',
                    'reason': f'组合漂移{drift:.1%}>{self.drift_threshold:.0%}→漂移触发'}
        # ④ 信号触发（增强）
        rank_changes = 0
        prev_ranks = {s: i for i, s in enumerate(previous_ranking[:30])}
        for i, s in enumerate(current_ranking[:30]):
            if s in prev_ranks:
                rank_changes += abs(i - prev_ranks[s])
        if rank_changes > self.rank_change_threshold * 30:  # 归一化
            if self.cost_aware and not self._is_rebalance_worthwhile(drift, days_since_last):
                return {'trigger': None, 'action': 'HOLD',
                        'reason': f'信号变化{rank_changes}但成本未回本→等待'}
            return {'trigger': 'SIGNAL', 'action': 'REBALANCE',
                    'reason': f'因子排名变化{rank_changes}→信号触发'}
        return {'trigger': None, 'action': 'HOLD',
                'reason': f'漂移{drift:.1%}+排名变化{rank_changes}均未达阈值→持有'}

    def _is_rebalance_worthwhile(self, drift: float, days_since_last: int) -> bool:
        """换仓是否值得（v1.12.11 补，Perold IS 成本-收益门控）

        Inaction Cost = drift × daily_alpha × expected_days_to_next_trigger
        Action Cost = transaction_cost_rate × drift（turnover ≈ drift）
        触发条件：Inaction Cost > Action Cost
        化简：daily_alpha × expected_days > transaction_cost_rate
        A 股默认：0.05% × days > 0.4% → break-even 8 天
        convergence_window_max=5 < 8 → 保底换仓在 break-even 前触发（安全垫）
        即：窗口内（3-5天）漂移/信号触发时，若距保底仅剩 1-2 天，
        inaction cost 尚不足以覆盖 action cost → 等保底触发（省交易成本）。
        """
        expected_days = self.convergence_window_max - days_since_last
        inaction_cost = drift * self.daily_alpha_estimate * expected_days
        action_cost = self.transaction_cost_rate * drift
        return inaction_cost > action_cost
```

> **施工建议**：在 `portfolio_optimizer.py` 调度层增加 `RebalanceTrigger.should_rebalance()` 前置门控，触发后才调用 7 约束链重优化。纯增量 ~35 行（v1.12.6）+ ~15 行 Inaction Cost（v1.12.11）。**MVP 即做**——解决 convergence_window 3-5 天"何时换"的执行断裂点，换仓成本感知（A 股 0.4% 往返）防止过度换仓。v1.12.11 补 Perold IS 成本-收益门控：漂移/信号触发命中后额外检查 Inaction Cost > Action Cost，避免窗口末尾"差 1 天就保底"时多余换仓。

#### 缺失#7：多因子 PIT 安全回测框架算法（高优先级，回测验证基础设施——与 24 号对称）

**问题**：§3.7#1-#6 补全了因子合成→组合优化→换仓→衰减→拥挤→归因六环节的编排算法，但**回测验证基础设施**缺失——24 号有 `DabanPITBacktestFramework`（§3.14 缺失#10），25 号无对称框架。多因子 PIT 安全比打板更复杂——涉及 5 层 PIT：① 因子值 AS OF JOIN（t 日决策只用 t 日及之前因子值）② IC 权重 PIT（IC 权重来自 t-1 日及之前历史 IC，不能用 t 日 IC 算 t 日权重=未来函数）③ 合成权重 PIT（合成因子分用 t 日因子值+t-1 日 IC 权重）④ 协方差矩阵 PIT（波动率/相关性用 t-1 日及之前数据）⑤ 行业分类 PIT（股票行业可能变更，AS OF JOIN）。§2.3 PIT 铁律仅声明原则，未形式化回测框架。PIT 违规=回测虚高+实盘失效。

```python
class MultifactorPITBacktestFramework:
    """多因子 PIT 安全回测框架（v1.12.7 补，与 24 号 DabanPITBacktestFramework 对称）

    多因子 PIT 安全比打板更复杂——涉及 5 层 PIT：
    ① 因子值 AS OF JOIN（t 日决策只用 t 日及之前因子值）
    ② IC 权重 PIT（IC 权重来自 t-1 日及之前历史 IC，不能用 t 日 IC）
    ③ 合成权重 PIT（合成因子分用 t 日因子值 + t-1 日 IC 权重）
    ④ 协方差矩阵 PIT（波动率/相关性用 t-1 日及之前数据）
    ⑤ 行业分类 PIT（股票行业可能变更，AS OF JOIN）

    与 §3.7#1 SynthesisDegradationChain 联动——回测中降级链决策必须 PIT 安全。
    与 §3.7#6 RebalanceTrigger 联动——回测中换仓触发必须 PIT 安全。
    与 §3.7#8 HoldingDriftMonitor 联动——回测中偏差监控必须 PIT 安全。
    """
    PIT_LAYERS = {
        'factor_value': {'rule': 'AS OF JOIN', 'desc': 't日决策只用t日及之前因子值'},
        'ic_weight': {'rule': 'ROLLING t-1', 'desc': 'IC权重来自t-1日及之前历史IC'},
        'synthesis_weight': {'rule': 't因子+t-1权重', 'desc': '合成=t日因子值+t-1日IC权重'},
        'covariance': {'rule': 'ROLLING t-1', 'desc': '协方差矩阵用t-1日及之前数据'},
        'industry_class': {'rule': 'AS OF JOIN', 'desc': '行业分类AS OF JOIN（股票行业可能变更）'},
    }
    ic_window: int = 60                # IC 滚动窗口（默认 60 交易日）
    cov_window: int = 60               # 协方差矩阵滚动窗口

    @staticmethod
    def assert_factor_pit(factor_date, decision_date, factor_name: str) -> None:
        """因子值 PIT 断言（v1.12.7 补）"""
        assert factor_date <= decision_date, \
            f"PIT VIOLATION: factor {factor_name} date={factor_date} > decision={decision_date}"

    @staticmethod
    def assert_ic_weight_pit(ic_window_end, decision_date) -> None:
        """IC 权重 PIT 断言（v1.12.7 补）——IC 窗口截止日必须 < 决策日"""
        assert ic_window_end < decision_date, \
            f"PIT VIOLATION: IC window end={ic_window_end} >= decision={decision_date}"

    @staticmethod
    def assert_covariance_pit(cov_end, decision_date) -> None:
        """协方差矩阵 PIT 断言（v1.12.7 补）"""
        assert cov_end < decision_date, \
            f"PIT VIOLATION: covariance end={cov_end} >= decision={decision_date}"

    def run_backtest(self, strategy_config: dict, start, end) -> dict:
        """PIT 安全回测主循环（v1.12.7 补）"""
        results = []
        prev_ranking = None
        prev_weights = None
        last_rebalance_date = None
        for decision_date in self._trading_days(start, end):
            # ① 因子值加载 + PIT 断言（AS OF JOIN）
            factor_panel = self._load_factors_asof(decision_date)
            for f in factor_panel:
                self.assert_factor_pit(f['date'], decision_date, f['name'])
            # ② IC 权重加载 + PIT 断言（IC 窗口截止 t-1）
            ic_history = self._load_ic_history(decision_date, window=self.ic_window)
            # IC 窗口截止日 = decision_date - 1（不含 t 日，防未来函数）
            ic_window_end = self._prev_trading_day(decision_date)
            self.assert_ic_weight_pit(ic_window_end, decision_date)
            # ③ 合成降级链决策（§3.7#1，PIT 安全——forward_returns 回测中传 None 避免前瞻）
            degradation = SynthesisDegradationChain().decide(
                factor_panel, ic_history, forward_returns=None)
            # ④ 合成因子分（t 日因子值 + t-1 日 IC 权重）
            composite = self._synthesize(factor_panel, degradation['method'], ic_history)
            current_ranking = sorted(composite, key=lambda x: x['score'], reverse=True)
            # ⑤ 协方差矩阵加载 + PIT 断言（t-1 日及之前）
            cov_matrix = self._load_covariance_asof(decision_date, window=self.cov_window)
            self.assert_covariance_pit(cov_matrix['end_date'], decision_date)
            # ⑥ 组合优化（7 约束链，§3.5）+ 约束仲裁（§3.7#2）
            target_weights = self._optimize(composite, cov_matrix, decision_date)
            arbitration = ConstraintArbitration().arbitrate(target_weights, len(composite))
            # ⑦ 换仓触发（§3.7#6，PIT 安全）
            days_since = self._trading_days_between(last_rebalance_date, decision_date) \
                if last_rebalance_date else 999
            if days_since == 999:
                trigger = {'trigger': 'INIT', 'action': 'REBALANCE', 'reason': '首次建仓'}
            else:
                trigger = RebalanceTrigger().should_rebalance(
                    days_since_last=days_since,
                    current_weights=prev_weights or {},
                    target_weights=target_weights.get('weights', {}),
                    current_ranking=[x['symbol'] for x in current_ranking],
                    previous_ranking=prev_ranking or [])
            # ⑧ 持仓偏差监控（§3.7#8，非换仓日检查偏差）
            drift_alert = None
            if trigger['action'] != 'REBALANCE' and prev_weights:
                drift_alert = HoldingDriftMonitor().monitor(
                    current_weights=self._current_weights(decision_date),
                    target_weights=prev_weights,
                    factor_exposures=self._current_factor_exposures(decision_date),
                    target_factor_exposures=target_weights.get('factor_exposures', {}),
                    industry_exposures=self._current_industry_exposures(decision_date),
                    target_industry_exposures=target_weights.get('industry_exposures', {}))
                if drift_alert['should_trigger_rebalance']:
                    trigger = {'trigger': 'DRIFT_CRITICAL', 'action': 'REBALANCE',
                               'reason': f'偏差临界({drift_alert["critical_count"]}项)→强制换仓'}
            # ⑨ 记录结果
            if trigger['action'] == 'REBALANCE':
                last_rebalance_date = decision_date
                prev_weights = target_weights.get('weights', {})
                prev_ranking = [x['symbol'] for x in current_ranking]
            results.append({
                'date': decision_date,
                'method': degradation['method'],
                'trigger': trigger['trigger'],
                'drift_alerts': drift_alert['critical_count'] if drift_alert else 0,
            })
        return self._summarize(results)
```

> **施工建议**：新增 `multifactor_pit_backtest.py`（MOD-L02-015，D-FACTOR-ANA-13），作为多因子策略回测的标准框架。纯增量 ~80 行，输入来自 `factor_decay_monitor.py`（IC 历史）+ `portfolio_optimizer.py`（协方差+优化）+ `multifactor_synthesis.py`（合成）。**首批回测前必做**——5 层 PIT 断言防止回测虚高，与 24 号 DabanPITBacktestFramework 对称。

#### 缺失#8：持仓偏差监控算法（中优先级，持仓期间因子暴露+行业偏离实时监控）

**问题**：§3.5 7 约束链（C2 行业暴露±5%/C6 因子暴露±10%）在 `portfolio_optimizer.py` 求解时生效，但**持仓后实际暴露偏差监控缺失**——持仓期间因价格变化，实际因子暴露和行业暴露会偏离优化器输出的目标值。§3.7#6 RebalanceTrigger 的漂移触发（drift_threshold=15%）只监控权重漂移，不监控因子暴露偏差和行业偏离。需补充持仓偏差监控，与 RebalanceTrigger 联动——偏差超阈值时作为漂移触发的增强输入。

```python
@dataclass
class HoldingDriftMonitor:
    """持仓偏差监控（v1.12.7 补，因子暴露+行业偏离实时监控）

    组合优化器输出目标持仓后，持仓期间因价格变化，实际因子暴露和行业暴露会偏离目标。
    与 §3.7#6 RebalanceTrigger 联动——偏差超阈值时作为漂移触发的增强输入。
    与 §3.5 7 约束链 C2(行业≤±5%)/C6(因子暴露≤±10%) 联动——监控优化器约束的持续满足。
    与 §3.7#2 ConstraintArbitration 联动——偏差超阈值触发重优化时仲裁约束冲突。
    """
    # 因子暴露偏差阈值（相对目标，C6 约束 ±10%）
    factor_drift_alert: float = 0.05        # 因子暴露偏差>5%→预警
    factor_drift_critical: float = 0.10     # 偏差>10%→触发换仓（C6 约束边界）
    # 行业暴露偏差阈值（相对目标，C2 约束 ±5%）
    industry_drift_alert: float = 0.03      # 行业偏离>3%→预警
    industry_drift_critical: float = 0.05   # 偏差>5%→触发换仓（C2 约束边界）
    # 权重漂移（与 RebalanceTrigger.drift_threshold=15% 联动）
    weight_drift_alert: float = 0.10        # 权重漂移>10%→预警（RebalanceTrigger 阈值 15%）

    def monitor(self, current_weights: dict, target_weights: dict,
                factor_exposures: dict, target_factor_exposures: dict,
                industry_exposures: dict, target_industry_exposures: dict) -> dict:
        """持仓偏差综合监控（v1.12.7 补）"""
        alerts = []
        # ① 因子暴露偏差（C6 约束持续满足监控）
        for factor, target_exp in target_factor_exposures.items():
            curr_exp = factor_exposures.get(factor, 0)
            drift = abs(curr_exp - target_exp)
            if drift > self.factor_drift_critical:
                alerts.append({'type': 'FACTOR_CRITICAL', 'factor': factor,
                               'drift': drift, 'action': 'TRIGGER_REBALANCE',
                               'reason': f'因子{factor}暴露偏差{drift:.1%}>10%→触发换仓(C6边界)'})
            elif drift > self.factor_drift_alert:
                alerts.append({'type': 'FACTOR_ALERT', 'factor': factor,
                               'drift': drift, 'action': 'MONITOR',
                               'reason': f'因子{factor}暴露偏差{drift:.1%}>5%→预警'})
        # ② 行业暴露偏差（C2 约束持续满足监控）
        for industry, target_exp in target_industry_exposures.items():
            curr_exp = industry_exposures.get(industry, 0)
            drift = abs(curr_exp - target_exp)
            if drift > self.industry_drift_critical:
                alerts.append({'type': 'INDUSTRY_CRITICAL', 'industry': industry,
                               'drift': drift, 'action': 'TRIGGER_REBALANCE',
                               'reason': f'行业{industry}偏离{drift:.1%}>5%→触发换仓(C2边界)'})
            elif drift > self.industry_drift_alert:
                alerts.append({'type': 'INDUSTRY_ALERT', 'industry': industry,
                               'drift': drift, 'action': 'MONITOR',
                               'reason': f'行业{industry}偏离{drift:.1%}>3%→预警'})
        # ③ 权重漂移（与 RebalanceTrigger 联动）
        common = set(current_weights) & set(target_weights)
        weight_drift = sum(abs(current_weights.get(s, 0) - target_weights.get(s, 0))
                           for s in common) / 2
        if weight_drift > self.weight_drift_alert:
            alerts.append({'type': 'WEIGHT_DRIFT', 'drift': weight_drift,
                           'action': 'FEED_REBALANCE_TRIGGER',
                           'reason': f'权重漂移{weight_drift:.1%}>10%→输入RebalanceTrigger(15%阈值)'})
        critical_count = sum(1 for a in alerts if 'CRITICAL' in a['type'])
        return {
            'alerts': alerts,
            'critical_count': critical_count,
            'should_trigger_rebalance': critical_count > 0,
            'weight_drift': weight_drift,
            'summary': f'{len(alerts)} alerts({critical_count} critical)',
        }
```

> **施工建议**：在 `portfolio_optimizer.py` 增加 `HoldingDriftMonitor.monitor()` 每日盘后调用，输出偏差报告。偏差 critical 时触发 RebalanceTrigger 强制换仓（覆盖时间/漂移/信号三触发器）。纯增量 ~45 行。**MVP 即做**——与 RebalanceTrigger 配合解决"换仓后到下次换仓期间偏差谁来管"的监控断裂点。

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
  - **Phase 4.1 Mask-First 可交易性掩码（v1.12.5 补完整消融实证）**：解决 A 股因子 IC 计算的"上游污染"——停牌/涨跌停/流动性不足的标的在因子 IC 计算时未被排除，导致 IC 虚高。构造可交易性掩码（`tradability_mask`），仅在可交易标的池中计算 IC。**MVP 即做**（纯增量逻辑 ~40 行），因子工坊 IC 计算前置门控。**v1.12.5 消融实证补**：[arXiv:2507.07107](https://arxiv.org/abs/2507.07107)（Du 2026-05-09 USTC）完整工程研究——在 3000 股合成面板+真实 A 股数据（2022-2024）上验证 mask-first 设计，mask 合约是**单一最大贡献者**（+0.44 Sharpe），超任何模型/损失选择；忽略上游污染使表观 IC 虚高 18% 但实现 Sharpe -0.44（模型学会预测不可交易的收益）。系统含 GPU 向量化 213 因子引擎（51× over pandas）+ Adjusted-MSE 损失（错号预测惩罚 11×）+ block-bootstrap GBM 增强 + Markowitz-Ledoit-Wolf 优化+cvxpy warm-start。合成面板 Sharpe 2.05 / 真实 A 股 Sharpe 1.63。**对 25 号的启示**：① mask-first 应是 MVP **最高优先级**（贡献超任何 ML 模型）；② Adjusted-MSE 错号惩罚损失可作 Phase 4.2 LambdaRankIC 的互补候选（前者惩罚方向错误，后者优化排序）；③ Ledoit-Wolf 收缩可与 §3.5 7 约束链 C6 因子暴露约束联动。MIT 开源实现 [github.com/initial-d/ml-quant-trading](https://github.com/initial-d/ml-quant-trading)。
  - **Phase 4.2 LambdaRankIC 训练目标**：直接优化 Rank IC 而非 MSE——在 LambdaRank 框架内推导 lambda 梯度的闭式解，使模型训练目标与因子评估目标（Rank IC）对齐。远期候选（需 ML 训练基础设施），MVP 不做。
  - **Phase 4.3 RankGLU 预测头架构**：残差门控评分形成——线性评分路径 + 有界乘性 GLU 分支，解决预测头瓶颈。远期候选，MVP 不做。
  - **Phase 4.4 STAR CrossAttention 混频融合**：Cross-Attention 多频因子融合——日频量价因子与月频基本面因子通过 Cross-Attention 融合，捕捉跨频交互效应。远期候选，MVP 不做。
  - **Phase 4.5 KTD-Fin Barra 归因**：A 股 Barra 风险模型归因——基于 CNE5 风格因子模型做多因子/单因子 IC 双检验。远期候选（需 Barra 基础设施），MVP 不做。
  - **Phase 4.6 EFS/Agentic/CAE 远期候选（v1.12.4 补完整实证）**：EFS（进化因子搜索）/Agentic（LLM 驱动因子发现）/CAE（压缩自编码器因子降维）三方向远期候选，MVP 不做。**v1.12.4 实证补**：[arXiv:2507.17211](https://arxiv.org/abs/2507.17211)（Chen et al. 2026-08-07 CityU+SUFE）完整验证 EFS——LLM+进化算法自动生成 alpha 因子做稀疏组合优化，RMT 去噪因子相关矩阵+正则化 QP 分配权重。在 4 个 Fama-French 基准（FF25/FF32/FF49/FF100）+ 3 个真实市场（美国/香港/中国大陆）上超越统计和优化基线。消融研究验证 prompt 组成/因子多样性/LLM 选择的重要性。**A 股适用性高**——直接在中国大陆市场验证，与现有因子工坊 BM-SEL-02 天然衔接。远期候选（需 LLM 推理基础设施），Phase 4 升级时优先评估。
  - **Phase 4.7 Alpha-R1 LLM+RL 动态门控抗衰减**：LLM+RL 基于因子经济逻辑与实时新闻的语义对齐做动态因子门控，对抗因子衰减。远期候选（需 LLM+RL 基础设施），MVP 不做。
  - **Phase 4.8 AlphaPROBE DAG+贝叶斯过拟合先验**：DAG 因子图 + 贝叶斯过拟合先验做因子选择，控制过拟合。远期候选，MVP 不做。
  - **Phase 4.9 中信建投 GRU 非线性合成 A 股实证**：GRU 非线性因子合成，中信建投 2026-07 A 股实证背书。远期候选，MVP 不做。
  - **Phase 4.10 行业嵌入 LSTM 跨截面异质性（v1.12.0 补）**：可学习行业嵌入 LSTM 捕捉跨截面异质性（[arXiv:2608.05755](https://arxiv.org/abs/2608.05755) 2026-08-07 Döbelt：31 页 16 图 7 表，行业嵌入 LSTM 比标准 LSTM 在金融时间序列预测上持续优于无行业嵌入版本，跨截面异质性建模是关键）。远期候选，MVP 不做。
  - **Phase 4.11 RL 组合管理三候选（v1.12.0 补，v1.12.6 补 Dynamic-β reward 实证）**：VD-MEAC（值分布最大熵 Actor-Critic，critic 学习未来收益完整分布）/ HRT（分层 RL，上层选股+下层执行）/ SAMP-HDRL（安全 RL，内置回撤/波动率/VaR 安全约束）。三者均需 RL 训练基础设施，Phase 4 远期候选非 MVP。与 Phase 4.12 MINGLE/OMD 正交——RL 管"权重怎么动态调整"，MINGLE/OMD 管"组合结构怎么构建"。**v1.12.6 补 Dynamic-β reward 实证**：[PLoS One 2025](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0332779)（Jung & Oh aSSIST）在 PPO/SAC/TD3 上比较 5 种 reward（Sharpe/Sortino/Static-β/Dynamic-β/Momentum-β），Dynamic-β（滚动回归估计 momentum/volatility/MA/volume 因子 β 敏感度）在股权上将年化从 ~20%（Sharpe baseline）提升至 23-24%、Sharpe 从 1.04 提升至 ~1.27，经 HAC/Wilcoxon/jackknife/bootstrap/FDR 多重稳健性检验。**对 25 号的启示**：VD-MEAC 的 reward 设计可参考 Dynamic-β——用因子暴露 β 作为 reward 而非裸收益率，使 RL 策略因子敏感而非纯追逐收益。远期 Phase 4.11 升级时评估。**v1.12.8 补 CVaR RaQL 自适应训练**：[arXiv:2608.04305](https://arxiv.org/abs/2608.04305)（Wu et al. 2026-08-06 ICAIF'26）针对 CVaR 风险感知 Q 学习（RaQL）有限预算下训练脆弱问题，设计 6 机制自适应训练控制器（步长自适应+学习率衰减同步+VaR 早期短修正+覆盖率优先样本分配+渐进后缀聚合+数据驱动尺度校准），不改变 CVaR 估计器和 Bellman 不动点，仅重设计训练过程。20 个随机种子 CVaR Bellman 残差降低约 85%（MeanBEQ: 1.22→0.19），日级交易样本外 Sharpe 0.93/最大回撤 6.46%。**与 VD-MEAC 的关系**：VD-MEAC 管"策略架构"（critic 学习收益分布），CVaR RaQL 管"训练稳定性"（6 机制控制器）——两者互补可叠加。**A 股适用性高**——CVaR 目标天然适合 A 股尾部风险（涨停砸板/闪崩/风格骤反），6 个机制都是训练流程改造无需改目标函数，可直接套用现有 RL 框架。远期 Phase 4.11 升级时与 VD-MEAC 一起评估。
  - **Phase 4.12 组合优化/多样化新范式两候选：MINGLE + OMD（v1.12.2 补）**：MINGLE（[arXiv:2608.06618](https://arxiv.org/abs/2608.06618)，ADMM 联合学习潜因子表示+图拓扑，因子暴露相似性建图替代相关性建图）/ OMD（[arXiv:2607.27461](https://arxiv.org/abs/2607.27461)，三矩阵 rank-based 无需矩阵求逆，volatility rank 可一步预测）。两者均属 Phase 4 远期候选非 MVP。与 Phase 4.11 RL 组合管理正交。
  - **Phase 4.13 仓位 sizing 与风控新范式三候选（v1.12.3 补，v1.12.10 补 Conformal Kelly 完整实证）**：Conformal Kelly（[arXiv:2608.01494](https://arxiv.org/abs/2608.01494) Ryan 2026-08，保形预测区间作为分数 Kelly 仓位的 scale，A 股适用性高——保形预测对非正态分布鲁棒，与现有 Kelly 仓位框架天然衔接）。**v1.12.10 补完整实证**：① **"简单优于复杂"负面结果**——每个使区间更快适应市场状态/regime 的调整反而年化增长降低 0.7-5.3 个百分点，最优是最简单的慢速无加权 per-asset 滚动保形分位数（原因：区间用于 sizing 而非预测时，宽度稳定性比局部锐度更重要）；② **区间失误风控**——当保形区间向下失误率远超历史基准时视为模型崩溃信号→削减杠杆，开发期最大回撤从 27.7% 降至 20.3% 同时提升 Sharpe，时序胜过全部 40 个安慰剂版本（rank-based p=1/41≈0.024）；③ **样本外校准保持但增长未保持**——覆盖率 0.745 vs 目标 0.750（校准好），但 2022 后年化 8.5%/7.0% 低于被动基准（增长衰减）。**与 Phase 4.14 RWC 的张力**：Conformal Kelly 证明"简单无加权最优"，Phase 4.14 RWC 主张"regime 加权在压力期更优"——两者矛盾需 A 股实证裁定，可能结论是"校准用简单版+风控用 regime 加权版"。/ Path Portfolio Optimization（[arXiv:2608.02355](https://arxiv.org/abs/2608.02355)，路径视角组合优化，显式建模路径累积成本）/ Drawdown Risk Beyond Brownian Motion（[arXiv:2608.00127](https://arxiv.org/abs/2608.00127)，非高斯扩展+长记忆回撤建模，与回撤 Protocol 阈值校准直接相关）。三者均属 Phase 4 远期候选非 MVP。登记 §6 待裁定。
  - **Phase 4.14 Regime-Weighted Conformal Calibration（v1.12.4 补，扩展 Phase 4.13 Conformal Kelly）**：[arXiv:2602.03903](https://arxiv.org/abs/2602.03903)（Schmitt 2026-08-03 Oxford）——Regime-Weighted Conformal calibration（RWC），用指数时间衰减+regime 相似性权重从历史预测误差构建安全缓冲，包裹任意条件分位数预测器。在 CRSP 指数+16 个美国组合上 Basel 99%/97.5% 水平验证，TWC（时间加权）在漂移下是强默认，RWC 在压力期为慢适应预测器改善校准。**A 股适用性高**——A 股 regime 结构化（牛熊聚类），RWC 的 regime 相似性权重可直接复用 [10_regime_detector_spec](10_regime_detector_spec.md) 12 态输出。**与 Phase 4.13 Conformal Kelly 的关系**：Conformal Kelly 用保形预测区间做 Kelly scale，RWC 扩展为 regime 加权的保形校准——前者管"仓位多大"，后者管"区间多宽更稳健"。远期候选（需保形预测+regime 联动基础设施），Phase 4 升级时与 Conformal Kelly 一起评估。
  - **Phase 4.15 Risk-Sensitive RL+Fractional Kelly（v1.12.4 补，统一 Phase 4.11+4.13）**：[arXiv:2606.20903](https://arxiv.org/abs/2606.20903)（Lleo & Runggaldier 2026-06-18 NEOMA+Padova）——连续时间风险敏感基准化资产配置的 RL 方法，用自由能-熵对偶将问题重表述为 LQG 随机微分博弈，得到有限/无限期鞍点解。连续时间 q-learning actor-critic：二次价值函数驱动 critic，仿射鞍点控制驱动确定性 actor（组合分配+对抗控制）。**学到的分配可分解为分数 Kelly**——提供 RL（Phase 4.11 VD-MEAC）与 Conformal Kelly（Phase 4.13）的理论统一框架。在美国股权数据上 proof-of-concept 实现显示 actor 高精度学到最优策略，组合 actor 比对抗 actor 收到更干净的学习信号。**A 股适用性中**——连续时间假设与 A 股离散交易+T+1 有差距，但分数 Kelly 分解+风险敏感目标函数可借鉴。远期候选（需连续时间 RL 基础设施），Phase 4+ 升级时作为 Phase 4.11+4.13 的理论统一候选评估。
  - **Phase 4.16 Sign-Aware Adjusted-MSE 损失（v1.12.5 补，Phase 4.2 LambdaRankIC 互补候选）**：源自 [arXiv:2507.07107](https://arxiv.org/abs/2507.07107)（Du 2026-05-09 USTC）——Adjusted-MSE 损失对错号预测（预测涨实际跌）惩罚 11× 于幅度误差，迫使模型优先保证方向正确而非拟合幅度。在 A 股真实数据上消融验证贡献显著（mask + Adjusted-MSE 联合优于任一单独）。**与 Phase 4.2 LambdaRankIC 的关系**：LambdaRankIC 优化排序（rank IC），Adjusted-MSE 优化方向（sign accuracy），两者互补——前者管"谁排前谁排后"，后者管"涨跌方向不犯错"。**A 股适用性高**——A 股因子预测方向错误代价远大于幅度误差（T+1 + 涨跌停使方向错=完全踏空）。远期候选（需 ML 训练基础设施），Phase 4 升级时与 LambdaRankIC 一起评估，可叠加使用。
  - **Phase 4.17 Certified Wasserstein Robust Portfolio（v1.12.6 补，2026-08-10 arXiv 最新）**：[arXiv:2608.07032](https://arxiv.org/abs/2608.07032)（Hsieh & Gan 2026-08-10）——认证高维 Wasserstein 鲁棒组合优化，用 Wasserstein 距离度量经验分布与真实分布的偏差，在分布不确定性下提供**可认证**的最坏情况保证。高维场景下避免传统鲁棒优化的过度保守问题。**与 Phase 4.12 MINGLE/OMD 的关系**：MINGLE/OMD 管"组合结构怎么构建"（图/秩），Wasserstein 管"分布不确定下怎么保底"——三者正交可叠加。**与 §3.7#5 CrowdingRealTimeMonitor 的关系**：拥挤监控检测"因子是否太挤"（实证代理），Wasserstein 鲁棒优化提供"分布偏移下数学保证"（理论兜底）——前者是预警，后者是防御。**A 股适用性高**——A 股分布偏移剧烈（regime 切换+政策冲击），Wasserstein 鲁棒可替代 §3.5 7 约束链中 C3 波动率约束的静态阈值，升级为分布鲁棒。远期候选（需凸优化基础设施 cvxpy 已有），Phase 4+ 升级时评估。
  - **Phase 4.18 MFCCA 多尺度组合配置（v1.12.10 补，突破 IC 加权瓶颈）**：[arXiv:2608.04987](https://arxiv.org/abs/2608.04987)（Kakinaka & Umeno 2026-08-05）——多重分形互相关分析（MFCCA）的带符号涨落函数作为风险泛函，由尺度 s 和涨落阶数 q 双索引。**关键创新**：保留局部去趋势协方差的符号——同向运动与反向运动以相反符号贡献风险，而非简单加权。q=2 时退化为均值-方差准则的尺度依赖极限。**核心发现**：符号保留对尾部风险降低的贡献，大于跨涨落阶数聚合的贡献。在多资产上实证：相对均值-方差基准，在每个目标收益下均降低回撤、VaR、期望损失，且不损失已实现收益（样本内外一致）。**A 股适用性中高**——中信建投 2026-06 研报确认"等权/IC/ICIR 三种加权接近"的瓶颈，说明单尺度线性加权已到极限。A 股因子的同向/反向关系在不同尺度上差异显著（日线动量 vs 周线反转），符号保留机制天然适配。**与 §3.1 IC 加权的关系**：IC 加权是单尺度线性合成，MFCCA 是多尺度非线性合成——前者管"因子权重多大"，后者管"不同尺度+方向上因子怎么协同/对冲"。远期候选（需多重分形分析基础设施），Phase 4+ 升级时作为 §3.1 合成方法的非线性多尺度替代评估。
  - **Phase 4.19 Stationary Ambiguity 平稳模糊性训练（v1.12.10 补，ML 模型 regime-shift 防护）**：[arXiv:2608.04832](https://arxiv.org/abs/2608.04832)（Mueller et al. 2026-08-05）——指出标准鲁棒训练的致命缺陷：策略在训练中逐步推断出潜在参数 x 后，模糊性（ambiguity）系统性衰减，策略逐渐特化到估计值，丧失对 regime shift 的鲁棒性。提出**平稳模糊性**原则：构建模拟器使模糊性随系统状态变化但不随时间系统性衰减，使滤波过程保持平稳。在对冲问题上验证：平稳模糊性训练的策略能长期保持对潜在因子的鲁棒性。**A 股适用性高**——A 股是典型的"政策市+情绪市"，regime 频繁切换，现有量化 ML 模型普遍存在"训练期好、实盘后 regime 一变就衰减"——正是模糊性衰减导致过拟合。**与 §3.7#3 DecayActionLifecycle 的关系**：DecayActionLifecycle 管"因子衰减后怎么退役"（事后补丁），平稳模糊性管"训练时怎么防止衰减"（事前预防）——两者互补，前者是下游治理，后者是上游防护。**与 Phase 4.10/4.11 ML 模型的关系**：Cross-Sectional LSTM/VD-MEAC 等所有 ML 模型均可受益于平稳模糊性训练原则。远期候选（需模拟器设计改造），Phase 4+ 升级时作为所有 ML 模型的训练基础设施改进评估。
  - **Phase 4.20 QUBO 换仓调度优化（v1.12.11 补，§3.7#6 RebalanceTrigger 的远期升级路径）**：[arXiv:2603.16904](https://arxiv.org/abs/2603.16904)（Weinberg 2026-03）——将换仓时序调度建模为二次无约束二值优化（QUBO）问题：目标函数 = 边际 Sharpe 增益 - 交易成本惩罚 - 过频惩罚（指数衰减交互项）。Walk-forward QAOA 求解消除 lookahead bias。S&P 500 实证：8 次换仓 vs 日历基准 24 次（成本降 44.5%），Sharpe 0.588 vs 0.575，风险调整后更优。**关键创新**：换仓时序不再是"阈值触发→执行"的反应式逻辑，而是"未来 N 天换仓计划"的组合优化——同时考虑多个潜在换仓时点的交互（过频惩罚的指数衰减交互项建模此效应）。**A 股适用性中**——A 股 0.4% 往返成本比美股高 4x，过频惩罚更关键，QUBO 的成本-过频联合优化更有价值。**量子计算非必须**：QAOA 可用经典 QUBO 求解器（模拟退火/分支定界）替代，n=5 天窗口规模经典可秒解。**与 §3.7#6 RebalanceTrigger 的关系**：RebalanceTrigger 是反应式三触发器（时间/漂移/信号），QUBO 是前瞻式组合优化——前者管"今天换不换"，后者管"未来 5 天怎么排"。远期候选（需 QUBO 求解器基础设施），Phase 4+ 升级时作为 RebalanceTrigger+Inaction Cost 的全局优化替代评估。
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
| ✅Hyperbolic 衰减完整实证 | arXiv:2512.11913 R²=0.65+拥挤预测崩溃1.7-1.8x | §3.3 v1.12.4 补 |
| ✅A 股 XGBoost+TreeSHAP 实证 | arXiv:2606.12843 rank IC=0.119 行为因子58.2% | §3.1 v1.12.4 补 |
| ✅EFS US/HK/China 三市场实证 | arXiv:2507.17211 Phase 4.6 完整验证 | Phase 4.6 v1.12.4 补 |
| Regime-Weighted Conformal Calibration | RWC 扩展 Conformal Kelly（arXiv:2602.03903） | Phase 4.14 远期候选 |
| Risk-Sensitive RL+Fractional Kelly | 统一 Phase 4.11+4.13（arXiv:2606.20903） | Phase 4.15 远期候选 |
| ✅Mask-First 完整消融实证 | arXiv:2507.07107 mask 单一最大贡献者+0.44 Sharpe | Phase 4.1 v1.12.5 补 |
| Sign-Aware Adjusted-MSE 损失 | 错号预测惩罚 11×，Phase 4.2 互补（arXiv:2507.07107） | Phase 4.16 远期候选 |
| ✅合成降级链决策 | §3.7 缺失#1 SynthesisDegradationChain | §3.7 v1.12.5 补 |
| ✅7 约束链冲突仲裁 | §3.7 缺失#2 ConstraintArbitration 硬/软分级 | §3.7 v1.12.5 补 |
| ✅因子衰减→动作全生命周期 | §3.7 缺失#3 DecayActionLifecycle 4 态状态机 | §3.7 v1.12.5 补 |
| ✅MVP 因子归因 | §3.7 缺失#4 SimpleFactorAttribution Brinson 式 | §3.7 v1.12.5 补 |
| ✅因子拥挤实时监控 | §3.7 缺失#5 CrowdingRealTimeMonitor MVP必做 | §3.7 v1.12.6 补 |
| ✅换仓触发决策 | §3.7 缺失#6 RebalanceTrigger MVP即做 | §3.7 v1.12.6 补 |
| ✅多因子 PIT 安全回测框架 | §3.7 缺失#7 MultifactorPITBacktestFramework 5层PIT | §3.7 v1.12.7 补 |
| ✅持仓偏差监控 | §3.7 缺失#8 HoldingDriftMonitor 因子暴露+行业偏离 | §3.7 v1.12.7 补 |
| ✅DecayActionLifecycle 边界状态 | §3.7#3 补 NEW冷启动+RETIRED退役 6态状态机 | §3.7 v1.12.9 补 |
| ✅A 股高频因子 2026 实证 | 国泰海通 2026-08-10 行为因子多空 12-16% | §3.3 v1.12.6 补 |
| ✅A 股拥挤崩盘 2026 实证 | 中国基金报 2026-08 57只量化基金踩雷 | §3.3 v1.12.6 补 |
| Dynamic-β reward 实证 | PLoS One 2025 Sharpe 1.04→1.27 | Phase 4.11 v1.12.6 补 |
| ✅CVaR RaQL 自适应训练 | arXiv:2608.04305 6机制训练控制器 Bellman残差-85% | Phase 4.11 v1.12.8 补 |
| Certified Wasserstein Robust Portfolio | arXiv:2608.07032 2026-08-10 分布鲁棒 | Phase 4.17 远期候选 |
| MFCCA 多尺度组合配置 | arXiv:2608.04987 符号保留+多尺度非线性合成 | Phase 4.18 远期候选 |
| Stationary Ambiguity 平稳模糊性训练 | arXiv:2608.04832 防模糊性衰减→regime-shift 过拟合 | Phase 4.19 远期候选 |
| ✅换仓触发 Inaction Cost 门控 | §3.7#6 RebalanceTrigger cost_aware 补 Perold IS 成本-收益门控 | §3.7 v1.12.11 补 |
| QUBO 换仓调度优化 | arXiv:2603.16904 换仓时序 QUBO 组合优化 成本降 44.5% | Phase 4.20 远期候选 |
| A 股 2026-07-06 交易新规 | ST 涨跌幅 5%→10%+盘后固定价格交易扩容 | G22 执行层施工时同步 |
| 衰减监控 CUSUM 层 + 自动淘汰层落码 | 代码仅半衰期监控（decay_monitor.py min_half_life=10），CUSUM/40 日\|IC\|<0.02 休眠为本文档决策（§3.3 代码现状注记） | 随 §3.7#3 DecayActionLifecycle 一并落码 |
| C1-C7 策略级约束链 ↔ MOD-PF-006 代码约束链对齐 | 代码约束参数（行业 ±10%/MDD 5%/相关性 0.7 等）与 §3.5 决策参数不一致（§3.5 代码现状注记） | 多因子 sleeve 上线前经 CTR-003 RiskLimits 注入对齐 |
| DecayActionLifecycle 6 态 ↔ factor_registry status 5 态映射 | 运行时 6 态（NEW/ACTIVE/OBSERVE/DORMANT/RECOVERY/RETIRED）vs registry 治理 5 态（candidate/experimental/active/deprecated/retired）双轨，DORMANT/OBSERVE 在 registry 应标什么未定义 | §3.7#3 落码时定义映射规则并回写 62 号 |
| G01 因子工程总纲（15 号）仍为 draft 骨架 | 本文档因子治理参数无上游 why 层背书；因子 10 类真源实际在 62 号 §6.1.1 + factor_registry.yaml | 15 号定稿后回填对齐（由 AI-20 负责 15 号） |
| 00_index 版本显示同步 | 00_index §0 目录/L215/L600 仍显示 v1.12.11，本文档已 1.13.1 | 由 AI-12 负责 00_index 同步（不越界改） |

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
