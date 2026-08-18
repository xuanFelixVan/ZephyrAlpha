---
ttl: permanent
doc_type: architecture_view
title: VaR/ES 与波动率监控
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.11.2"
date: 2026-08-16
topic: var_es_monitoring
scope: 07_trading_decision_architecture
---

> ## 结案报告（2026-08-16 补记）
>
> **实际开发**：2026-08-13 第二批施工（会话 AI-VAR-001，2 笔提交合并回 dev），VaR/ES 监控模块落码，零遗留完工；风控限额注册表同步补登 var 5 条/es 3 条。
>
> **最终成果**：VaR_95/ES_95 计算、入场基准、触发减仓动作与 30 日波动率调整体系按本档契约落地，测试全绿。
>
> **未做事项及原因**：
> - FHS/QbSD/Vol-Targeting 三增强未做——裁定远期项，本期不落码。
> - 2026-08-16 双轮审查发现 F1 ES 插值口径、F2+F4 NaN/Inf 过滤等算法缺陷——已派单算法修复批 AI-RFIX-001，在途未合并，属正常迭代而非烂尾。

# VaR/ES 与波动率监控

> 本备忘记录 VaR/ES 与波动率监控从 §2.5.4 框架到代码落地的选型推理、触发机制裁决与上限定义。
> 性质：永久态设计记录，可随项目演进而修订，不是不可推翻的裁定。
> 管理规范见 [01_design_memo_management_spec](01_design_memo_management_spec.md)。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G17 VaR/ES 与波动率监控 |
| 所属 | 作战地图 09 + [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5.4 |
| 依赖 | G16（[35_drawdown_protocol_impl](35_drawdown_protocol_impl.md)，VaR/ES 喂入 drawdown_controller）+ G18（[37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md)，流动性危机放大 VaR breach 严重度） |
| 对标 | 赢牛资管 VaR-ES / Sina 量化风控 / MetricGate VaR/ES / Pomegra VaR vs CVaR / Man Numeric CVaR / Nystrup-Boyd HMM+MPC |
| 正交性 | ✅ 与 regime 正交（VaR 是组合风险度量，regime 是市场状态） |
| 优先级 | P3（风险相关模块先于策略模块施工至 production，符合风险优先原则） |
| 状态 | ✅ 已定稿 v1.11.0（框架 §2.5.4 + 代码已有实现 + 触发机制裁决 + 4 法回测 MVP 已施工 + 校准/重构/恢复子流程 + 盘中重算 + clean/dirty P&L 区分 + BlackSwanSignal API 对接 + VaR breach 状态机 + FHS/QbSD/Vol-Targeting 施工规约 + 跨文档流程交接链闭合（E1-E3）+ 2026-08 研究远期登记 28 节 + §3.20 BM-RC-04-C + §3.1 BM-RC-07-A 口径对齐 + v1.10.4 第二轮循环压缩（AI-DC2-05）+ **v1.11.0 双轮审查算法修复批（AI-RFIX-001）**：ES 插值口径 method='lower' 裁定 / VaR 非有限值 Fail-Closed / POT 小样本降级落码 / 5 级仓位上限单调性修正 / FHS 漂移语气修正转 CAND-AUTONOMYCORE-002 / D1-D9 漂移逐条对账） |

## 2. 背景

### 2.1 项目处境

个人 + 100% AI 开发的 A 股量化交易系统。VaR/ES 监控是风险控制三件套（回撤 Protocol / VaR-ES / 流动性危机）之一，定位为组合级风险度量和触发信号源。

### 2.2 核心问题

1. **VaR_95 怎么算**：参数法（快但尾部低估）vs 历史模拟法（无分布假设但需样本）——如何取？
2. **ES_95 怎么算**：ES 不可独立 elicitable，需要 VaR + 尾部条件期望——如何与 VaR 联动？
3. **入场基准怎么定**："VaR > 1.2×入场 VaR" 中的 "入场 VaR" 锚定哪个时点？
4. **触发动作怎么执行**：VaR breach → 减仓比例 → 谁执行、怎么执行？
5. **30 日波动率调整怎么算**："每增 10% → 仓位减 20%" 中的 "增 10%" 相对什么基准？
6. **数据窗口多长**：太短不稳定，太长含旧 regime——A 股市场成熟度下的合理窗口？
7. **与回撤 Protocol 怎么协同**：两个独立信号源如何避免冲突？

### 2.3 约束条件

- **A 股 T+1**：当日买入次日才能卖出，VaR breach 减仓不能立即执行
- **涨跌停**：极端行情下无法交易，VaR breach 减仓可能无法执行
- **个人系统**：算力有限，不能跑蒙特卡洛 GPU 模拟；可解释性优先
- **风险优先原则**：风险相关模块先于策略模块施工至 production

## 3. 决策

### §3.1 VaR_95 计算（参数法 + 历史模拟法，取 max）

**决策**：Phase 1 两种方法并发计算，取 `max(parametric, historical)` 作为保守估计（conservative_max）。

✅ 已施工（var_calculator，2 轮 27 测试全绿）：`src/zephyr/risk/core/var_calculator.py` v0.1.0（production, MOD-RK-05）。接口级摘要：`calculate(returns, portfolio_value)` → VaR_95；样本不足 min_history 抛 `InsufficientVaRHistoryError`。

**算法**：

```python
# 参数法 (Parametric / Variance-Covariance)，假设收益正态分布
VaR_param = (z_α · σ - μ) · V · √T
# z_α = |ppf(1-c)|  如 0.95 → 1.6449
# σ = 样本标准差 (ddof=1)；μ = 样本均值；V = 组合价值 (NAV)；T = 持有期天数 (默认 1)
# 下限 0：(z·σ - μ) 可能为负（高均值低波动）→ VaR 取 0

# 历史模拟法 (Historical Simulation)，经验分位数，无分布假设
VaR_hist = -quantile(r, 1-c, method='lower') · V · √T
# 取收益序列下侧 (1-c) 经验分位数（负数=损失），VaR = -该分位数 · V（正数），下限 0
# 分位数口径统一 method='lower'（v1.11.2，AI-R5 审查批）：与 ES 同口径——v1.11.0 F1 裁定只统一了
# ES 侧，VaR 侧遗留线性插值造成同模块双口径（es_var_ratio 分子分母不同口径、5 级分级对插值虚拟值敏感）

# 保守取 max
VaR_95 = max(VaR_param, VaR_hist)
```

**选型理由**：
1. **取 max 的保守性**：参数法正态假设低估厚尾，历史模拟小样本分位数不稳——取 max 确保更保守者胜出（风险优先原则）
2. **参数法 <1ms, 历史模拟 ~5ms**：CPU 即可，无需 GPU
3. **每阶段独立可用**：Phase 1 完成即可上线风控（设计真源 §6 VaR 三阶段演进）
4. **Phase 2 远期**：蒙特卡洛法（GPU CuPy/PyTorch）+ MCS forecast combination 替代 max（→ §4.26，≥4 法候选池后 Fissler-Ziegel 联合损失 + SSM 加权组合）
5. **Phase 3 远期**：Basel III 三角验证 + 乘数因子 + 压力 VaR

**配置参数**（C 类可调）：

| 参数 | 默认值 | 说明 |
|---|---|---|
| confidence_level | 0.95 | 置信水平（95% VaR） |
| holding_period_days | 1 | 持有期（日 VaR） |
| method | conservative_max | 取两法 max |
| min_history | 30 | 最少样本数 |
| annualization_factor | 252 | A 股交易日年化因子 |
| max_nonfinite_ratio | 0.05 | 非有限值（NaN/±Inf）占比上限（v1.11.0 新增，双轮审查 F2+F4）：过滤数入 `VaRResult.nan_dropped` 计数 + warning；占比 >5% 抛 `ExcessiveNonFiniteDataError`（Fail-Closed——数据缺口期多为停牌/极端行情高波动日，静默过滤会系统性低估风险且无信号） |

**最小样本约束**：`min_history=30`，不足时抛 `InsufficientVaRHistoryError`。A 股约 1.5 个月数据。

> **BM-RC-07-A 口径对齐（v1.10.1，作战地图全覆盖补丁）**：作战地图 BM-RC-07-A"VaR 三阶段演进"（L4，production，MOD-RK-05）定义为"Phase1 参数法+历史模拟 → Phase2 蒙特卡洛（GPU） → Phase3 Basel III 三角验证"，与本备忘 §5.2 演进路径（Phase 1 参数法+历史模拟+POT → Phase 2 FHS/蒙特卡洛/Conformal(RWC) → Phase 3 QbSD/CAESar/Basel III 三角）口径不一致——BM 三阶段缺 FHS/QbSD/CRC 中间层。**裁定：VaR 演进口径以本备忘路线为准**——本文是 VaR/ES 主题备忘（G17 权威真源），FHS/QbSD/CRC 是参数法→蒙特卡洛之间已评估登记的中间形态（§3.16 施工规约 + §4.1 CRC），跳级到 GPU 蒙特卡洛不符合风险优先原则的渐进演进；BM"三阶段演进"定义留作战地图维护批次同步修订，登记 §6 待裁定（开放问题，本备忘不越界改 BM 真源）。

### §3.2 ES_95 计算（历史模拟 + POT 厚尾拟合）

**决策**：ES_95 双轨计算——历史模拟法为主，POT 模型厚尾拟合为辅（厚尾检测结果）。

✅ 已施工（tail_risk_monitor，2 轮 27 测试全绿）：`src/zephyr/risk/core/tail_risk_monitor.py` v0.1.0（production, MOD-RK-15）。接口级摘要（v1.11.0 勘正）：`assess(returns, portfolio_value=1.0, now=None)` → TailRiskSnapshot（VaR/ES/POT 厚尾诊断/跳跃/告警/FRTB 加价）——实际签名无 `var_forecast` 参数；ES ≥ VaR 不变式由 `method='lower'` 口径构造性成立（尾部均值 ≤ 分位点），非运行时强制校验（v1.11.0 前本节声称的 `assess(returns, var_forecast)` + "强制校验 es_forecast >= var_forecast" 为文档-代码漂移，双轮审查 D3 对账修正）。

**算法**：

```python
# 方法 1: 历史模拟法 ES（主）——尾部条件期望 = 超过 VaR 的损失的平均值
# 插值口径裁定（v1.11.0，双轮审查 F1）：分位数取 method='lower'（实有样本点，不线性插值）——
# 线性插值产出样本中不存在的虚拟值，小样本下尾部样本口径不稳定；'lower' 下分位点 = sorted[floor((n-1)(1-c))]
ES_hist = -mean(r[r <= quantile(r, 1-c, method='lower')])   # 尾部（≤ 实有分位点）收益均值的负数

# 方法 2: POT 模型 (Peaks-Over-Threshold) 厚尾拟合（辅）
# 超过阈值 u 的超额值 X-u ~ GPD(ξ, β)
# ξ (shape): >0=厚尾(Fréchet), =0=指数, <0=有界；β (scale): 尺度参数；tail_index = 1/ξ
# POT 修正 ES（当 ξ > 0 厚尾时）：ES_pot = VaR · (1 + (ξ - β/u) · (1-ξ)^(-1))
# POT 拟合步骤：① 阈值 u = quantile(r, 0.90)（最差 10%）② 超额值 x_i = r_i - u（损失侧）
#              ③ MLE 拟合 GPD(ξ, β) ④ ξ > heavy_tail_shape_threshold (0.2) → 厚尾告警
# 最终 ES_95 = ES_hist（主），POT 结果用于厚尾诊断和 FRTB 加价
```

**POT 阈值选择**：默认取 90% 分位数（最差 10% 拟合）。远期演进见 §3.3 EVT 阈值选择。

**ES ≥ VaR 不变式**：ES 是尾部期望 ≥ VaR 分位数——`method='lower'` 口径下由构造成立（尾部均值 ≤ 分位点），代码无独立运行时校验（v1.11.0 勘正，原"强制校验"表述删除）。

**FRTB 尾部风险加价**：当 `shape > critical_shape_threshold (0.5)` 时，`frtb_surcharge = frtb_multiplier (3.0) × shape`，作为资本附加。

**POT 日常计算失败兜底**（v1.4.0 提出，v1.11.0 落码勘正）：
- **触发条件**：`tail_risk_monitor.fit_pot()` 日常计算 GPD 拟合失败（scipy genpareto.fit 不收敛/样本不足/分布异常）
- **兜底策略**：回退纯历史模拟 ES（`ES_95 = ES_hist`），跳过 POT 修正；✅ **已落码（v1.11.0，双轮审查深挖③裁定）**：`fit_pot` 三条降级路径（样本 <min_samples / 负收益 <10 / exceedances <5）均 warning 日志留痕，`TailRiskSnapshot.pot_fallback_historical=True` 标记并入 to_dict——60 日窗口 + 常态负日占比（40-60%）下 exceedances 常 <5，小样本 GPD 拟合是噪声发生器，降级而非硬拟合；ES ≥ VaR 不变式仍构造性成立（历史模拟 ES 天然满足）
- **连续失败升级**：⚠️ 未施工——"连续 5 日 POT 拟合失败 → §3.10 RECALIBRATE 动作 3（`pot_threshold_quantile` 0.90→0.85 或→0.95）"需跨日失败计数器（状态持久化），随 state_store 持久化批（§3.19 代码差距）一并落地；当前 `pot_threshold_quantile` 为 frozen 配置常量
- **与 §3.3 Uehara 双门控的关系**：远期 Uehara 拒绝外推时同走此兜底路径

**配置参数**（C 类可调）：

| 参数 | 默认值 | 说明 |
|---|---|---|
| confidence | 0.95 | VaR/ES 置信度 |
| pot_threshold_quantile | 0.90 | POT 阈值分位数 |
| heavy_tail_shape_threshold | 0.2 | 厚尾判定 shape 阈值 |
| critical_shape_threshold | 0.5 | 严重尾部 shape 阈值 |
| es_warning_ratio | 1.5 | ES/VaR 比值告警阈值 |
| frtb_multiplier | 3.0 | FRTB 加价乘数 |

### §3.3 EVT 阈值选择（GPD 校准形式化）

**决策**：MVP 使用固定 90% 分位数作为 POT 阈值（`scipy.stats.genpareto.fit` MLE，无阈值稳定性检验）；远期演进 Uehara 双门控拒绝外推机制。

**远期演进：Uehara 2026-05 双门控 EVT 阈值选择**（arXiv:2605.27474）：
1. **参数稳定性门控**：扫描阈值分位数 0.85~0.95，绘制 ξ(u) 稳定性图，选取平台区
2. **GPD 拟合优度门控**：KS 检验 p ≥ 0.05
3. **双门控均通过** → 接受 GPD 外推；**任一不通过** → 拒绝外推，输出空集（A 股样本短时拒绝外推比强行出 GPD 尾更安全）

**远期演进：Belzile & Davison 2026-06 EVT 阈值选择程序系统综述**（arXiv:2606.28540）：40+ 阈值选择程序全景比较，Uehara 双门控拒绝外推时的替代程序参考。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-RC-06-B | 尾部风险监控 | §3.2 ES_95 计算（历史模拟+POT）/ §3.3 EVT 阈值选择 | production 已建 |
| BM-RC-07 | 风险预算与VaR | §3.1 VaR_95 计算 / §3.2 ES_95 计算 | production 已建 |

### §3.4 入场 VaR/ES 基准

**决策**：入场 VaR/ES = 策略开仓日的盘前 VaR_95/ES_95 快照，持久化到 `state_store`。

**跨文档契约**（35号 §3.11 v1.0.0）：
- 35号 §3.11 盘前计算 VaR_95 快照 → 持久化为 `entry_var` 到 state_store
- 35号 §3.16 回撤归因加载 `entry_var` 供 `current_var vs entry_var` 判断风险恶化

**配对约束表**：

| 产出方（36号） | 消费方（35号） | 字段 | 说明 |
|---|---|---|---|
| §3.1 VaRCalculator | 35号 §3.11 | entry_var | 入场时盘前 VaR_95 快照 |
| §3.2 TailRiskMonitor | 35号 §3.11 | entry_es | 入场时盘前 ES_95 快照 |

**冷启动守卫**：首次启动无历史 entry_var 时，`entry_var = None`，消费方需 None 守卫。

### §3.5 触发动作（5 级系统性风险 + BlackSwanSignal API）

**决策**：VaR/ES breach 不直接触发减仓，而是通过 `drawdown_controller` 的 5 级系统性风险分级 + 黑天鹅模式信号产出分级响应指令。

✅ 已施工（drawdown_controller，2 轮 27 测试全绿）：`src/zephyr/position/core/drawdown_controller.py` v0.1.0（production, MOD-POS-008）。接口级摘要（v1.11.0 勘正）：`evaluate(drawdown_info, var_cvar, black_swan=None, strategy_pnls=None)` → `DrawdownResponse(position_cap, reduce_ratio, kill_switch_advised)`——实际签名无 `var_breach_state` 参数（VarBreachStateMachine 乘性折扣协同为 §3.15 待施工项，双轮审查 D4 对账修正）。

#### §3.5.1 5 级系统性风险（VaR/CVaR 驱动）

| 级别 | VaR 阈值 | CVaR 阈值 | 仓位上限 | 动作 |
|---|---|---|---|---|
| GREEN | < 2% | - | 1.0 | 正常 |
| YELLOW | 2%-4% | - | 0.5 | 新开仓减半 |
| ORANGE | 4%-6% | - | 0.5 | 禁止新开 + 减仓（v1.11.0 修正：原 0.7 非单调倒挂，双轮审查 P1-4 裁定降为 0.5） |
| RED | > 6% | - | 0.5 | 减仓 50% + 只平不开 |
| BLACK | - | > 10% | 0.0 | 全部清仓 |

> CVaR = ES（Conditional VaR = Expected Shortfall），同一概念不同命名。
> **仓位上限单调性裁定（v1.11.0，双轮审查 P1-4）**：仓位上限序列必须按严重度单调非增（1.0→0.5→0.5→0.5→0.0）——原 ORANGE 0.7 致 YELLOW(0.5)→ORANGE(0.7) 风险升级后仓位上限反而放宽，与"渐进减仓"语义矛盾。级别严格度由动作语义区分（YELLOW 新开减半 / ORANGE 禁新开 / RED 只平不开 / BLACK 清仓），不由 cap 数值区分。

**配置参数**（DrawdownControllerConfig）：

| 参数 | 默认值 | 说明 |
|---|---|---|
| var_yellow | 0.02 | 黄级 VaR 阈值 |
| var_orange | 0.04 | 橙级 VaR 阈值 |
| var_red | 0.06 | 红级 VaR 阈值 |
| cvar_black | 0.10 | 黑级 CVaR 阈值 |

#### §3.5.2 BlackSwanSignal API（黑天鹅信号处理）

**源码契约**：`drawdown_controller.py` §14.3 定义 `BlackSwanSignal` 数据类和 `BlackSwanMode` 枚举。

**BlackSwanMode 7 模式**：BS001_LIQUIDITY（流动性蒸发）/ BS002_CORRELATION（相关性崩塌）/ BS003_VOLATILITY（波动率爆发）/ BS004_MARGIN（融资盘踩踏）/ BS005_CONTAGION（跨市场传导）/ BS006_POLICY（政策黑天鹅）/ BS007_SYSTEMIC（系统性风险，多模式同触发）。

**BlackSwanSignal**：`active_modes: frozenset[BlackSwanMode]`；`has_black_swan = len(active_modes) > 0`；`is_systemic = (BS007_SYSTEMIC ∈ active_modes) 或 (len(active_modes) ≥ 2)`。

**事件 → BlackSwanMode 映射**（36号 `build_black_swan_signal(events)` 构造 BlackSwanSignal 传入 drawdown_controller）：

| 事件 | BlackSwanMode |
|---|---|
| POLICY | BS006_POLICY |
| LIMIT_TIDE | BS001_LIQUIDITY |
| VOL_REGIME_SHIFT / GAP | BS003_VOLATILITY |
| CORR_BREAKDOWN | BS002_CORRELATION |
| TAIL_BREACH | BS007_SYSTEMIC |
| CONTAGION | BS005_CONTAGION |

**blackswan_active 来源链**：`BlackSwanReport.blackswan_active = len(active_modes) > 0`，供 35号 §3.13 `intraday_risk_loop` 状态机消费。

**BS-007 → Kill Switch 建议**（非直接触发）：`drawdown_controller` 对 BS-007 产出 `kill_switch_advised=True`，委托 `stop_loss` 执行 Kill Switch，本模块不直接触发。

#### §3.5.3 VaR floor 设定警示（2026-08 理论背书）

**arXiv:2608.05623 Li/Lyu/Wei 2026-08-06**：高 VaR floor 诱发 gambling-for-resurrection（赌博回本）行为，低 floor 具防御性。本项目 5 级阈值采用分级响应（GREEN 1.0 → YELLOW 0.5 → ORANGE 0.5 → RED 0.5 → BLACK 0.0，仓位上限单调非增 + 动作语义递严：新开减半→禁新开→只平不开→清仓）而非硬性单一 floor，天然避免该理论风险；与 35号 §4.12 拒绝"回撤进 RiskSignal"交叉印证——保守低地板阈值优于激进高地板。（v1.11.0 勘正：原文"渐进式减仓 YELLOW 0.5 → ORANGE 0.7"的 0.7 为非单调倒挂数值错误，已按双轮审查 P1-4 裁定修正为 0.5，"渐进"语义改由动作递严承载——双轮审查 D8 对账）

### §3.6 30 日波动率调整（z-score 法）

**决策**：30 日滚动波动率 z-score 法，相对 60 日均值基准。

**框架要求**（30号 §2.5.4）："每增 10% → 仓位减 20%（LedgerMind 2026-05）"

**算法**：

```python
# 30 日滚动年化波动率
vol_30d = std(returns[-30:], ddof=1) * sqrt(252)
# 60 日均值基准（z-score 分母）
vol_60d_mean = mean([vol_30d(t) for t in range(t-60, t)])
# z-score
vol_z = (vol_30d - vol_60d_mean) / std([vol_30d(t) for t in range(t-60, t)])
# 波动率调整系数：每增 10%（vol_30d / vol_60d_mean - 1 > 0.10）→ 仓位减 20%
vol_ratio = vol_30d / vol_60d_mean if vol_60d_mean > 0 else 1.0
if vol_ratio > 1.10:
    vol_adjustment = max(0.0, 1.0 - 0.20 * ((vol_ratio - 1.0) / 0.10))
else:
    vol_adjustment = 1.0
# 最终仓位上限 = drawdown_controller.position_cap × vol_adjustment
```

**顺周期性风险**：波动率飙升时减仓 → 加剧卖压 → 进一步推高波动率。缓解措施：
1. 减仓比例有下限（不低于 BLACK 级 0.0）
2. 与 35号回撤 Protocol 协同，避免双重减仓叠加（取最严而非累乘）
3. 远期演进：Soloviov 2026-07 vol-targeting 受控实证（GARCH vs EWMA 统计不可区分 DM p=0.57，验证 30 日滚动 vol 替代 GARCH 的合理性 + vol-targeting 核心价值是 MaxDD 控制非 Sharpe 提升）

### §3.7 数据窗口

**决策**：

| 用途 | 窗口 | 理由 |
|---|---|---|
| VaR 历史模拟 | 60 交易日 | min_history=30（下限）+ 60 日平衡稳定性与时效性 |
| ES 历史模拟 | 60 交易日 | 与 VaR 对齐 |
| POT 拟合 | 60 交易日 | v1.11.0 勘正（双轮审查 D6/深挖③）：原"最差 10% ≈ 6 个样本"隐含全负日假设——60 日窗口负日占比 50% 常态下 exceedances 仅约 3 个 < 代码 ≥5 门槛，GPD 小样本拟合为噪声；裁定为样本不足时跳过 POT 仅历史 ES（`pot_fallback_historical` 标记 + warning 告警，已落码），窗口扩至 252 日列为远期备选 |
| 30 日波动率 | 30 交易日 | 框架要求 |
| 60 日均值基准 | 60 交易日 | z-score 分母 |
| 回测验证 | ≥250 交易日 | Basel 交通灯 250 天标准 |

**A 股特殊性**：A 股年交易日 ~244，250 天约 1 年。回测窗口不足 250 天时按比例缩放（var_backtester.py `_traffic_light` 实现）。

### §3.8 与回撤 Protocol 协同

**协同架构**：VaRCalculator/TailRiskMonitor（36号）产出 VaR_95/ES_95(CVaR)/BlackSwanSignal → `drawdown_controller._evaluate_risk_level()` / `_evaluate_black_swan()`（35号）→ `DrawdownResponse(position_cap, reduce_ratio, kill_switch_advised)`。

**取最严原则**：`drawdown_controller.evaluate()` 对系统性风险级别、黑天鹅仓位上限、Kill Switch 建议三者取 `min(caps)`——最严的仓位上限胜出，不累乘。

**正交性**：VaR/ES 是组合风险度量（市场级），回撤是账户级净值回撤（账户级），两者正交。VaR breach 可能在回撤未触发时先行告警（波动率飙升但净值未跌），回撤 breach 可能在 VaR 未触发时先行告警（缓慢阴跌）。

**35号跨文档契约**（entry VaR 持久化）：
- 36号 §3.1/§3.2 计算 entry_var/entry_es → 35号 §3.11 持久化
- 35号 §3.16 回撤归因消费 entry_var 判断风险恶化（current_var vs entry_var）

### §3.9 回测验证（13 法框架，MVP 4 法已施工）

**决策**：13 法回测框架，MVP 4 法已施工至 production。

✅ 已施工（var_backtester，2 轮 27 测试全绿）：`src/zephyr/risk/core/var_backtester.py` v0.1.0（evolving, MOD-RK-05B）。接口级摘要：`full_report(observations)` → 4 法 + Basel traffic light + overall_reject。

#### §3.9.1 MVP 4 法（已施工）

| # | 方法 | 检验目标 | 统计量 | 分布 | 源码 |
|---|---|---|---|---|---|
| 1 | Kupiec POF | 覆盖率（超限频率对不对） | LR_UC = -2ln[L(α)/L(p̂)] | χ²(1) | `kupiec_pof()` |
| 2 | Christoffersen | 独立性 + 条件覆盖率 | LR_cc = LR_UC + LR_ind | χ²(2) | `christoffersen()` |
| 3 | Acerbi-Szekely Z2 | ES 直接回测（超限日损失幅度） | Z2 = (1/N)Σ R_t/ES_t · 1{breach} | E[Z2]=-1 | `acerbi_szekely_z2()` |
| 4 | E-backtesting | 在线累积（anytime-valid） | e_t = Π(1+λ·b_s) | e > 1/α 拒绝 | `e_backtesting()` |

**Christoffersen LR_ind/LR_cc 区分**：`christoffersen()` 返回 `ChristoffersenResult(lr_uc, lr_ind, lr_cc, p_value, reject, n_00, n_01, n_10, n_11)`（n_00/n_01/n_10/n_11 = 未超限→未超限 / 未超限→超限 / 超限→未超限 / 超限→超限聚集）。**独立性失败分支**：当 christoffersen_ind_p < 0.05 且 kupiec_p ≥ 0.05 时 → 覆盖率正确但超限聚集（独立性失败）→ action = "RECALIBRATE"——⚠️ v1.11.0 勘正（双轮审查 D1）：FHS 未施工（src 零匹配），原"优先选 FHS（§3.16）"指向不存在代码；当前实际首选动作为 §3.10 动作 1（扩窗口）+ 动作 2（切方法），FHS 晋升走 CAND-AUTONOMYCORE-002 trigger。

**E-backtesting GREM 四级告警**（ERCIM 145 接口）：

| 级别 | 条件（对数刻度） | 动作 |
|---|---|---|
| green | log(e) < 0.5·log(1/α) | 无动作 |
| yellow | 0.5·log(1/α) ≤ log(e) < log(1/α) | 早期预警 |
| red | log(1/α) ≤ log(e) < 2·log(1/α) | 实质证据，审查校准 |
| black | log(e) ≥ 2·log(1/α) | 决定性证据，拒绝模型 |

**Basel 交通灯**（辅助报告）：
- 95% VaR 250 天：Green ≤16, Yellow 17-20, Red ≥21（期望 12.5）
- 样本不足 250 天时按比例缩放

#### §3.9.2 远期 9 法（未施工）

| # | 方法 | 来源 | 说明 |
|---|---|---|---|
| 5 | FHS | Filtered Historical Simulation | GARCH 残差重采样，独立性失败时优先选 |
| 6 | 多项式 VaR 回测 | - | Phase 2 |
| 7 | Fissler-Ziegel 联合回测 | - | Phase 2 |
| 8 | Ridge 回测 | - | Phase 2 |
| 9 | DSR/CSCV 过拟合检测 | - | Phase 2 |
| 10 | Comparative e-backtests | arXiv:2511.05840 | 两模型序贯比较，改进三区制 |
| 11 | ES 精度极限诊断 | Pele 2026-06 | (nα)^{-1/2} 信息极限防伪精度 |
| 12 | Feature-Aware Auditing | arXiv:2607.11653 | 特征级误校准归因 |
| 13 | Latent-Regime Bias Auditing | - | Phase 3 |

#### §3.9.3 2026-08 监管认知更新

- **CP9/26 PRA IMA**：ES 97.5% IMA 基准
- **US Basel III Endgame NPR**：traffic light 三区国际标尺
- **"SA 并行 IMA"→双轨映射**：标准化法 + 内部模型法并行

### §3.10 校准/重构/恢复子流程

**决策**：三档响应——PASS / RECALIBRATE / REBUILD。

> **执行者状态标注（v1.11.1 命名对账，AI-GOVB-001 #106）**：本节动作表的执行者 `RiskOrchestrator` 为设计契约名——编排层已建成，落地名 `RiskLayerOrchestrator`（MOD-L06-001，`src/zephyr/ex_core/risk_layer_orchestrator.py`，AI-RWIRE-001 #ARCH-100）；盘中风控编排（evaluate_intraday/Kill Switch/对账冻结）已接线，但各 `update_config()/enable()/force_static_mode()` 校准动作调用点未接入编排层——本节动作仍由人工/daily_auditor 告警驱动执行，禁止按可执行语气直读。
>
> **ES 插值口径裁定（v1.11.0，双轮审查 F1）**：`compute_expected_shortfall` 尾部筛选分位数采用 `method='lower'`（实有样本点 sorted[floor((n-1)(1-c))]，不线性插值）——线性插值产出样本中不存在的虚拟分位值，小样本下尾部口径不稳定；'lower' 口径下 ES ≥ VaR 由构造成立。VaR 历史模拟分位数（`compute_var` / `var_calculator._historical`）保留线性插值（单点连续取值无尾部切片抖动问题）；离散收益（大量 0 值日）下 VaR 可分位报 0 为已知口径特征，由 min_samples 下限 + POT 降级链兜底，回测验证（§3.9）负责捕获系统性低估。

- **PASS**：Basel Green + Kupiec p≥0.05 + Christoffersen p≥0.05 + Z2 不拒绝 + E-backtesting green/yellow
- **RECALIBRATE**：Basel Yellow + Kupiec reject + Christoffersen 独立性失败 + E-backtesting red
- **REBUILD**：Basel Red + overall_reject + E-backtesting black

**RECALIBRATE 动作**（v1.1.0 D7）：

| # | 动作 | 执行者 | 具体参数 | 回滚机制 |
|---|---|---|---|---|
| 1 | 扩大数据窗口 | RiskOrchestrator → var_calculator.update_config() | `min_history` 30→60，`window` 60→120 交易日 | 次日回测仍 RECALIBRATE → 继续扩大至 250；连续 3 日 REBUILD → 回滚至 60 |
| 2 | 切换 VaR 方法 | RiskOrchestrator → var_calculator.update_config() | `method` conservative_max → historical（参数法不稳定时）；或 → parametric（历史模拟小样本不稳定时） | 切换后次日回测 PASS → 保留；RECALIBRATE → 切回原方法 + 标记方法切换失败 |
| 3 | 重校准 POT 阈值 | RiskOrchestrator → tail_risk_monitor.update_config() | `pot_threshold_quantile` 0.90→0.85（更厚尾）或 →0.95（更保守） | GPD 拟合失败（KS p<0.05）→ 回滚至 0.90 + 跳过 POT 修正 |
| 4 | 切换到 FHS | ⚠️ 未施工（远期候选 CAND-AUTONOMYCORE-002）——RiskOrchestrator → fhs_engine.enable() 为设计契约，src 零匹配 | GARCH(1,1) 拟合 + 残差重采样（§3.16） | FHS 拟合失败（GARCH 不收敛）→ 回退 historical + 标记 FHS 不可用 |

**触发条件 → 动作映射**（v1.1.0）：

| 回测失败信号 | 优先动作 | 理由 |
|---|---|---|
| Kupiec reject（覆盖率失败） | 动作 1（扩窗口）+ 动作 2（切方法） | 覆盖率失败 = 样本不足或分布假设错 |
| Christoffersen LR_ind reject（独立性失败） | 动作 1 + 动作 2（v1.11.0 勘正：动作 4 切 FHS 未施工，src 零匹配——远期晋升走 CAND-AUTONOMYCORE-002） | 独立性失败 = 超限聚集 → 远期用 GARCH 残差重采样破自相关，当前以扩窗口/切方法应对 |
| Z2 reject（ES 幅度失败） | 动作 3（重校准 POT） | ES 幅度失败 = 尾部拟合不准 |
| E-backtesting red（anytime-valid 累积证据） | 动作 1 + 动作 2 + 动作 3（组合） | 累积证据 = 多重校准问题 |

**REBUILD 动作**（v1.1.0）：

| # | 动作 | 执行者 | 具体参数 |
|---|---|---|---|
| 1 | 标记模型不可用 | RiskOrchestrator → state_store.set_var_model_status("UNAVAILABLE") | 持久化标记，盘前初始化读取 |
| 2 | 回退到保守静态映射 | RiskOrchestrator → drawdown_controller.force_static_mode() | 静态映射：VaR 固定 3%（ORANGE 级），CVaR 固定 5%，position_cap 固定 0.7——不再用 var_calculator 动态计算 |
| 3 | 人工审查 | daily_auditor.log_rebuild_event() + alert(REBUILD) | 通知业主审查模型，需人工解除 UNAVAILABLE 标记 |
| 4 | 考虑 Phase 2 蒙特卡洛 | 远期（不在 REBUILD 自动流程内） | 待 Phase 2 GPU 蒙特卡洛落地后作为 REBUILD 的可选升级路径 |

**REBUILD → 恢复流程**（v1.1.0）：
1. 业主人工审查模型 + 修复根因
2. 业主解除 UNAVAILABLE 标记（需 ResetConfirmation，对齐 35号 §3.14 人工复位机制）
3. RiskOrchestrator 重新启用 var_calculator 动态计算
4. 次日回测验证 → PASS 才完全恢复；RECALIBRATE/REBUILD 则继续静态映射

> **跨文档契约**（35号 §3.15/§3.18）：REBUILD 动作 2 的 force_static_mode() 产出的静态 position_cap = 0.7，需喂入 35号 §3.10 daily_risk_loop 的 drawdown_controller.evaluate()，作为 C 层 VaR/CVaR 约束的替代。35号 §3.18 盘后持久化需记录 var_model_status，供次日 §3.15 盘前初始化加载。

**RECALIBRATE/REBUILD 审计日志调用时机**（v1.1.0 D1）：
- `log_recalibration(action="RECALIBRATE", reason=...)`：执行 RECALIBRATE 动作 1-4 任一后立即调用
- `log_recalibration(action="REBUILD", reason=...)`：执行 REBUILD 动作 1-2 后立即调用
- `log_recalibration(action="RECOVERED_FROM_REBUILD", reason=...)`：业主解除 UNAVAILABLE 标记后调用

**回测样本不足处理**（v1.4.0）：

| 样本量 n（交易日） | 处理策略 | 综合定级 | 理由 |
|---|---|---|---|
| n < 30 | 跳过回测，不参与综合定级 | 强制 PASS（标记 `INSUFFICIENT_SAMPLE_SKIP`） | min_history=30 下限，VaR 本身已不可靠，回测无统计意义 |
| 30 ≤ n < 60 | 执行回测但标记 `LOW_POWER_WARNING` | 仅 E-backtesting（anytime-valid 小样本友好）参与定级，Kupiec/Christoffersen/Z2 标记 `low_power` 不参与 reject 判定 | 传统 4 法小样本检验力不足假阳性高；E-backtesting anytime-valid 对小样本更鲁棒 |
| 60 ≤ n < 250 | 正常执行 4 法回测，Basel 交通灯按比例缩放 | 全 4 法参与定级 | §3.7 数据窗口标准 |
| n ≥ 250 | 正常执行 4 法回测，Basel 交通灯不缩放 | 全 4 法参与定级 | Basel 250 天标准 |

**冷启动期（n < 60）特殊处理**：
- **VaR 计算**：§3.1 min_history=30 触发 `InsufficientVaRHistoryError` 时，降级为参数法 only（30 日分位数不稳定），取 `VaR_95 = VaR_param`（不取 max）
- **回测验证**：如上表，跳过传统 4 法，仅用 E-backtesting
- **仓位约束**：冷启动期 position_cap 额外折扣 0.8（与 §3.5 5 级风险乘性叠加），`effective_cap = risk_level_cap × 0.8`，对齐 35号 §3.15 nav_history < 30 保守冷启动模式
- **解除条件**：n ≥ 60 后自动解除冷启动折扣，首次完整回测结果记入 daily_auditor 审计日志

### §3.11 回测验证端到端施工流程（daily_auditor 集成）

✅ 已施工（daily_auditor，2 轮 27 测试全绿）：`src/zephyr/risk/core/daily_auditor.py` v0.2.0（production, MOD-RK-20）。接口级摘要：`run_var_backtest(observations)` → `VarBacktestReport(report, action)`；`log_entry_var / log_baseline / log_recalibration` 三审计方法。

**综合定级**（`DailyAuditor.run_var_backtest()`，对齐 §3.10 矩阵，v1.4.0 一致性修复后含 Christoffersen reject）：
- `basel_zone == "red"` 或 `overall_reject` 或 `ebt_alert == "black"` → action = REBUILD
- `basel_zone == "yellow"` 或 `kupiec_pof.reject` 或 `christoffersen.reject` 或 `ebt_alert ∈ (yellow, red)` → action = RECALIBRATE
- 否则 → action = PASS

**回撤 Protocol 审计日志集成**（35号 §3.15/§3.17 跨文档契约）：
- `log_entry_var(trade_date, entry_var)`：记录入场 VaR 快照（35号 §3.11 持久化契约）
- `log_baseline(trade_date, var_95, es_95)`：记录当日 VaR/ES 基线（供次日回撤归因对比）
- `log_recalibration(trade_date, action, reason)`：记录校准/重构事件（RECALIBRATE/REBUILD 审计追溯）

**组件状态**：

> **"production" 口径澄清（v1.11.0，双轮审查 D7 对账）**：下表 ✅ production = **模块成熟度**（模块已建 + 单测全绿 + 接口冻结承诺），≠ 生产交易链已接线生效。风控链路（VaR/ES/回撤/KillSwitch/流动性危机/对账）的生产接线由接线批承载（AI-RWIRE-001，#ARCH-100）——RWIRE-001 已建成编排层（`RiskLayerOrchestrator`，MOD-L06-001）+ `trading_session` 注入缝，组合根实例化前，本节组件在盘中仅经 daily_auditor 盘后回测链路消费。

| 组件 | 状态 | 说明 |
|---|---|---|
| var_calculator.py | ✅ production v0.1.0 | 参数法 + 历史模拟 + conservative_max（v1.11.0 +非有限值 Fail-Closed：nan_dropped 计数 + 超阈值 raise） |
| tail_risk_monitor.py | ✅ production v0.1.0 | ES（method='lower' 口径）+ POT GPD（小样本降级 pot_fallback_historical）+ 跳跃检测 + FRTB |
| var_backtester.py | ✅ evolving v0.1.0 | MVP 4 法 + Basel traffic light |
| daily_auditor.py | ✅ production v0.2.0 | run_var_backtest + 3 审计日志方法 |
| drawdown_controller.py | ✅ production v0.1.0 | 5 级（v1.11.0 仓位上限单调性修正：ORANGE 0.7→0.5）+ 7 黑天鹅 + BlackSwanSignal API |
| RiskOrchestrator（落地名 `RiskLayerOrchestrator`，MOD-L06-001） | ✅ 已建（AI-RWIRE-001，#ARCH-100） | 盘中风控编排（evaluate_intraday/Kill Switch/对账冻结）已接线；§3.10/§3.15/§3.17 动作表校准执行者语义仍=设计契约，未接入编排层 |
| backtest_store | ⚠️ 待施工 | 回测结果持久化层 |
| clean P&L 双轨记录 | ⚠️ 待施工 | clean/dirty P&L 区分 |

### §3.12 盘中重算触发

**决策**：7 条触发条件，盘中重算 VaR/ES 并**反馈给 35号 §3.13 盘中循环重新裁决**（v1.1.0 D2）。

**7 条触发条件**（`intraday_var_recalc_trigger()`，任一满足即重算）：
1. 当前亏损 > 日内 VaR 的 50%（预警线）
2. 当前回撤 > 8%（回撤 Protocol 一级阈值，与 35号 §3.1 协同）
3. 涨跌停潮（与 G18 §3.5 涨跌停检测协同）
4. 波动率 regime shift（30 分钟波动率 > 60 日均值 3σ）
5. 相关性崩塌（BS-002 前兆）
6. 跨市场传导（BS-005 前兆）
7. 政策事件（BS-006）

**盘中重算执行 + 结果反馈链**（v1.1.0 D2）：
- 调用方：35号 §3.13 `intraday_risk_loop` 检测触发后调用 `intraday_var_recalc()`
- 执行：① `var_calculator.calculate(current_returns, current_nav)` + `tail_risk_monitor.assess()` 重算 → `VarCvarMetrics(var_95, cvar_95)`；② 与盘前基线（state_store.load_premarket_baseline，§3.18 持久化）对比，`var_change_ratio > 0.20` → `significant_change=True` + `daily_auditor.log_intraday_recalc_significant()`；③ 更新 §3.15 VaR breach 状态机；④ `state_store.append_intraday_recalc_log()` 记录
- 返回 `IntradayVarResult(var_cvar, breach_state, significant_change)` → 35号 §3.13 用新 var_cvar 重新调用 `drawdown_controller.evaluate()` 产出新 DrawdownResponse，覆盖盘前 response
- **取最严维度澄清**（v1.4.0）："取最严" = position_cap 取 min（盘前 cap vs 盘中重算 cap），非 level 取 max——position_cap 是实际仓位约束，level 仅是分级标签。例：盘前 RED（cap=0.5）盘中重算 YELLOW（cap=0.7）→ 取 min(0.5, 0.7)=0.5（盘前 RED 胜出）

**A 股收盘集合竞价特殊处理**（v1.1.0，职责边界）：
- 36号 §3.12：检测 14:55 后是否触发盘中重算 → 重算 → 返回 IntradayVarResult（不直接提交减仓单）
- 35号 §3.13：接收 IntradayVarResult → 14:57 收盘集合竞价提交减仓单（基于新 DrawdownResponse 的 position_cap）

**多触发条件去重与防抖**（v1.4.0）：
1. **去重**：返回首个命中 trigger（优先级：政策事件 > 涨跌停潮 > 跨市场传导 > 相关性崩塌 > 波动率 regime shift > 回撤 > 亏损）；多条件同时满足只重算一次，trigger.reason 记录所有命中条件（逗号分隔）
2. **冷却期**：重算后 5 分钟内不再重算；冷却期内触发记入 `suppressed_triggers` 供审计；5 分钟后条件仍满足允许再次重算
3. **频率上限**：单日最多重算 6 次（约每 40 分钟一次覆盖 4 小时交易时段）；达上限仅记录 `intraday_recalc_freq_cap_hit` 告警
4. **触发条件 1 口径**（v1.4.0）：`current_loss = (opening_nav - current_nav) / opening_nav`，基于 clean NAV（不含未实现 MtM），与 §3.13 clean/dirty 对齐——避免盘中 MtM 噪声误触发

**盘中重算结果反馈回测**（v1.1.0）：
- 重算结果持久化 `intraday_recalc_log`（§3.18）；日终审计对比盘前基线，差异 > 20% → 标记 `intraday_recalc_significant`
- §3.9 回测消费：盘中重算显著且次日回测 RECALIBRATE → 盘前 VaR 模型对盘中波动率 regime shift 响应不足 → 触发 §3.10 RECALIBRATE 动作 4（切 FHS）

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-RC-04-A | VaR实时计算 | §3.1 VaR_95 计算 / §3.12 盘中重算触发 | production 已建 |

### §3.13 clean/dirty P&L 区分

**决策**：双轨记录 clean P&L 和 dirty P&L，回测验证使用 clean P&L。

| 类型 | 定义 | 用途 |
|---|---|---|
| clean P&L | 已实现 + 未实现 P&L，**不含**交易成本、融资成本、分红 | 回测验证（模型纯度检验） |
| dirty P&L | 已实现 + 未实现 P&L，**含**交易成本、融资成本、分红 | 实际盈亏报告 |

**理由**：回测验证的是 VaR/ES 模型对市场风险的预测能力，交易成本等非市场因素会污染检验；clean P&L 剥离非市场因素反映模型纯度。

**产消链**（v1.1.0 D5）：

| 环节 | 责任方 | 具体实现 |
|---|---|---|
| 产出 clean P&L | daily_auditor.compute_clean_pnl() | broker 已实现 PnL + 收盘 MtM 未实现 PnL − 交易成本/融资成本/分红 |
| 产出 dirty P&L | daily_auditor.compute_dirty_pnl() | broker 已实现 PnL + 收盘 MtM 未实现 PnL + 交易成本/融资成本/分红 |
| 持久化 | state_store.save_pnl_dual(trade_date, clean_pnl, dirty_pnl) | 双轨持久化，供回测 + 报告分别消费 |
| 消费 clean P&L | var_backtester.full_report(observations) | BacktestObservation.pnl 须为 clean_pnl |
| 消费 dirty P&L | daily_auditor.report() + 业主报告 | 实际盈亏报告用 dirty_pnl |

**BacktestObservation 契约**（v1.1.0）：`trade_date / var_forecast / es_forecast / pnl / pnl_type: Literal["clean","dirty"] = "clean"`；`__post_init__` 强制 `pnl_type == "clean"`，否则 ValueError——dirty P&L 会污染模型纯度检验。

**T+1 约束对 clean/dirty P&L 的影响**（v1.4.0）：A 股 T+1 下当日买入不可当日平仓，其未实现 MtM 全部归入 dirty P&L；clean P&L 仅含可平仓头寸（T-1 及之前建仓，`p.entry_date < trade_date`）的已实现盈亏 + 未实现 MtM。

| P&L 组成 | T+1 可平仓头寸 | T+1 不可平仓头寸（当日新建） | 处理 |
|---|---|---|---|
| 已实现 P&L | ✅ 含 | ❌ 不含（不可平仓无已实现） | clean + dirty 均含可平仓已实现 |
| 未实现 MtM（可平仓） | ✅ 含 | — | clean + dirty 均含 |
| 未实现 MtM（不可平仓） | — | ⚠️ 仅 dirty 含 | clean **不含**，dirty 含 |
| 交易成本/融资成本/分红 | ❌ 不含 | ❌ 不含 | 仅 dirty 含 |

**T+1 对回测验证的影响**：
- clean P&L 仅含可平仓头寸——回测检验 VaR/ES 模型对**可平仓风险**的预测能力；T+1 不可平仓头寸 MtM 是"锁仓风险"而非"可交易风险"，不纳入 VaR 回测
- dirty P&L 含全部头寸——实际盈亏报告反映账户真实损益（含锁仓 MtM）
- 冷启动期：首次建仓日全部头寸 T+1 不可平仓 → clean P&L = 0 → 当日不参与回测验证（§3.10 n<30 强制 PASS）

### §3.14 黑天鹅信号处理（BlackSwanSignal API）

**决策**：36号负责从黑天鹅事件构造 `BlackSwanSignal`，传入 `drawdown_controller.evaluate()`。

**模块归属**（v1.1.0 D6）：

| 阶段 | black_swan_detector 实现 | 说明 |
|---|---|---|
| MVP（当前） | 36号 §3.5.2 EVENT_TO_BS_MODE 映射 + 37号流动性危机检测 + 55号系统监控事件聚合 | 无独立 black_swan_detector 模块，RiskOrchestrator 聚合多源事件 |
| 远期（Phase 2） | 独立 black_swan_detector 模块（D-RISK/D-SIGNAL） | 待 55号 + 37号均 production 后提取为独立模块 |

**MVP 事件源映射**（v1.1.0）：

| BlackSwanMode | MVP 事件源 | 检测方法 |
|---|---|---|
| BS001_LIQUIDITY | 37号 §3.5 涨跌停潮检测 + 成交量萎缩 | 涨跌停比例 > 阈值 OR 成交量 < 60 日均值 50% |
| BS002_CORRELATION | 36号 §3.12 盘中重算 触发条件 5 | 相关性矩阵均值骤降（30 分钟窗口 vs 60 日窗口） |
| BS003_VOLATILITY | 36号 §3.12 盘中重算 触发条件 4 | 30 分钟波动率 > 60 日均值 3σ |
| BS004_MARGIN | 55号系统监控 融资余额检测 | 融资余额骤降 > 5%（外部数据源） |
| BS005_CONTAGION | 36号 §3.12 盘中重算 触发条件 6 | 跨市场相关性突变（A股 vs 港股/美股隔夜） |
| BS006_POLICY | 外部政策事件输入（人工/新闻 API） | 业主手动标记 OR 新闻 API 关键词触发 |
| BS007_SYSTEMIC | ≥2 模式同触发 OR 显式标记 | BlackSwanSignal.is_systemic 自动判定 |

**数据流**：RiskOrchestrator 聚合多源事件（①37号流动性危机 ②36号波动率 regime shift ③55号系统监控异常 ④外部政策事件）→ `events: list[BlackSwanEvent]` → `build_black_swan_signal(events)`（§3.5.2 映射）→ `BlackSwanSignal` → `drawdown_controller.evaluate(...)` → `DrawdownResponse(kill_switch_advised, position_cap, ...)`。

**BlackSwanReport 产出 + blackswan_active 来源链**：`events / triggered_count / blackswan_active = len(active_modes) > 0`；来源链 = RiskOrchestrator 聚合（MVP）或 black_swan_detector 检测（远期）→ 36号 `build_black_swan_signal()` → `BlackSwanReport.blackswan_active` → 35号 §3.13 `intraday_risk_loop` 状态机消费（定义点 §3.5.2）。

### §3.15 VaR breach 恢复/复位状态机

> **⚠️ 施工状态（v1.11.0，双轮审查 D4 对账）**：本节为**设计契约，未落码**——`VarBreachStateMachine` 类、`drawdown_controller.evaluate(var_breach_state=...)` 参数、×0.8/×0.9 乘性折扣、§3.18/§3.19 持久化 7 阶段在 src 均零匹配；当前 `evaluate()` 实际签名无 `var_breach_state`（见 §3.5 接口摘要勘正）。落地随 state_store 持久化批（§3.19 代码差距）+ 风控接线批（AI-RWIRE-001）一并施工。以下内容为设计规约，禁止按已实现语气直读。

**决策**：VaR breach 后的恢复采用 `consecutive_days_below_recovery` 条件判断，状态 NORMAL → BREACHED → RECOVERY → NORMAL。

**转换规则**（`transition(current_var, recovery_threshold)`）：
- NORMAL → BREACHED：`current_var > breach_threshold`，记录 breach_date，计数清零
- BREACHED → RECOVERY：`current_var < recovery_threshold` 连续 ≥3 日（期间反弹则计数重置）
- RECOVERY → NORMAL：`current_var < recovery_threshold` 连续 ≥5 日（恢复期更长）；RECOVERY 中 VaR 再超 breach_threshold → 回 BREACHED（复燃，计数清零）

**参数**：

| 参数 | 默认值 | 说明 |
|---|---|---|
| breach_threshold | var_yellow (0.02) | 进入 BREACHED 状态的 VaR 阈值 |
| recovery_threshold | breach_threshold × 0.8 | 进入 RECOVERY 状态的 VaR 阈值 |
| consecutive_days_below_recovery (BREACHED→RECOVERY) | 3 | 连续低于恢复阈值天数 |
| consecutive_days_below_recovery (RECOVERY→NORMAL) | 5 | 恢复期更长，避免反复 |

**跨重启持久化**（v1.1.0 D3）：`VarBreachStateSnapshot(state, breach_date, consecutive_days_below_recovery, last_transition)`；§3.18 盘后 `state_store.save_var_breach_state()` 保存，§3.19 盘前 `load_var_breach_state()` 加载；快照缺失 → 冷启动默认 NORMAL（保守：不假设上次在 BREACHED）。

**与 35号回撤状态机协同**（v1.1.0 D4）：36号 VarBreachStateMachine（NORMAL/BREACHED/RECOVERY）与 35号 DrawdownStateMachine（NORMAL/WARN/DANGER/CRISIS/KILL/RECOVERY）是**两个正交状态机**，通过 `drawdown_controller.evaluate(var_breach_state=...)` context 参数乘性折扣协同：

| VaR breach 状态 | position_cap 乘数 | 协同理由 |
|---|---|---|
| NORMAL | ×1.0 | VaR 未 breach，回撤状态机独立运行 |
| BREACHED | ×0.8 | VaR breach = 组合风险恶化，即便回撤未触发也需额外保守（如回撤 WARN 80% → 80%×80%=64%） |
| RECOVERY | ×0.9 | 风险缓解但未完全恢复，轻量折扣 |

**取最严链**（v1.1.0 D4 + v1.1.1 E3）：`base_cap = _evaluate_risk_level(var_cvar, drawdown_info)`（回撤状态机产出，如 WARN → 0.8）→ `effective_cap = max(base_cap × var_breach_multiplier, 0.0)`（下限保护：不低于 Kill Switch 级）→ 若 `black_swan.has_black_swan` 则 `effective_cap = min(effective_cap, _evaluate_black_swan(black_swan))`（黑天鹅 cap 取 min）。

> **两状态机正交性**：回撤状态机是账户级净值回撤驱动（已发生事实），VaR breach 状态机是组合级风险度量驱动（前瞻性风险），可独立触发；乘性叠加确保任一触发即整体保守。
>
> **双 RECOVERY 叠加**（v1.1.1 E3）：35号 DrawdownStateMachine RECOVERY（阶梯 25%→50%→75%→100%）与 36号 VarBreachStateMachine RECOVERY（×0.9）同时发生时，`effective_cap = 阶梯值 × 0.9`（如 0.25 × 0.9 = 0.225），双重保守——裁决为 intended（风险优先原则，账户回撤 + 组合风险同时未恢复）；下限保护 `max(effective_cap, 0.0)`。若两状态机同时 RECOVERY 超 20 交易日，daily_auditor 标记 `DUAL_RECOVERY_PROLONGED` 告警，提示人工审查策略是否需暂停（而非仅靠仓位折扣控制）。

**VaR BREACHED 状态作为 35号 §3.16 回撤归因维度**（v1.1.0 跨文档契约）：若 36号 VarBreachStateMachine.state == "BREACHED"，归因为 "RISK_DETERIORATION_VAR_BREACHED"（VaR 模型失效或波动率 regime shift 导致组合风险恶化），与 35号 §3.16 现有检测互补：
- entry_var vs current_var：**单次** VaR 恶化比例（ratio > 1.5 → 减仓）
- VarBreachStateMachine BREACHED：**持续** VaR 超阈值（连续 breach → 状态机升级 → 额外折扣）

两者乘性叠加：单次恶化触发减仓 + 持续 breach 触发额外折扣，双重保护。

### §3.16 FHS/QbSD/Vol-Targeting 施工规约

**Filtered Historical Simulation (FHS)**（远期 Phase 2）：
- GARCH(1,1) 拟合收益序列 → 标准化残差 → 重采样 → 乘以条件波动率预测
- 用途：Christoffersen 独立性失败时优先选 FHS
- 依赖：arch 库（GARCH 拟合）

**FHS 切换触发条件**（v1.1.0 D12，`should_switch_to_fhs()`，任一满足即切换）：
1. Christoffersen LR_ind reject（独立性失败，`lr_ind_p < 0.05` 且 `kupiec_pof.p_value >= 0.05`——覆盖率正确但超限聚集，需 GARCH 残差重采样破自相关）
2. 连续 2 次回测 E-backtesting red（累积证据表明波动率有时变结构）
3. 盘中重算显著（§3.12 `intraday_recalc_significant`）连续 3 日触发（盘前 VaR 对盘中 vol regime shift 响应不足）

**FHS 切换流程**（v1.1.0，对齐 §3.10 RECALIBRATE 动作 4）：
1. should_switch_to_fhs() 返回 True → RiskOrchestrator 调用 fhs_engine.enable()
2. fhs_engine 用 GARCH(1,1) 拟合过去 60 日收益序列 → 若不收敛（迭代超限/方差非正）→ 回退 historical + 标记 FHS 不可用
3. 收敛 → 标准化残差重采样 → 乘以条件波动率预测 → 产出 FHS VaR
4. 次日回测验证 FHS VaR → PASS 则保留；RECALIBRATE/REBUILD 则切回 historical + 标记 FHS 切换失败

**FHS 切换失败冷却期**（v1.4.0）：
- **冷却期机制**：`FHS_COOLDOWN_DAYS = 10`（约 2 周覆盖一个完整波动率周期）——FHS 切换失败（步骤 2 GARCH 不收敛 OR 步骤 4 次日回测 RECALIBRATE/REBUILD）→ 记录 `last_fhs_failure_date` → 10 交易日内 `should_switch_to_fhs()` 直接返回 False + `log_fhs_cooldown_active()`
- **冷却期解除**：10 交易日后自动解除，允许再次尝试（若触发条件仍满足）
- **连续失败升级**：冷却期内累计 3 次 FHS 切换失败 → 标记 `FHS_PERMANENTLY_DISABLED`，不再尝试切换，仅用 historical + §3.10 RECALIBRATE 动作 1（扩窗口）/动作 2（切方法）替代
- **与 §3.10 的关系**：冷却期是动作 4 的防抖机制，防止独立性失败反复触发 切换→失败→再触发 死循环

**Quantile-based Scale Dynamics (QbSD)**（远期 Phase 3）：

**算法概要**：分位数回归捕捉不同置信水平下尾部的动态尺度变化——与 §3.1 参数法（正态假设单一 σ）不同，QbSD 对多个分位数分别建模，允许不同尾部有不同动态尺度。

```python
# QbSD 多分位数回归（远期 Phase 3）
# 对每个目标分位数 α ∈ {0.95, 0.99, 0.995} 独立拟合分位数回归模型
# VaR_α = quantile_regression(X_t, α)  # X_t = 特征向量（滞后收益/波动率/成交量等）
# ES_α = mean(returns[returns <= VaR_α])  # 尾部条件期望（与 §3.2 ES_hist 同理）
# 参数法：VaR_95 = (z_0.95 · σ - μ) · V —— 正态假设，单一 σ
# QbSD：无分布假设，各分位数独立，天然捕捉偏度/厚尾
```

**触发条件**（何时从 MVP 升级到 QbSD）：
1. §3.2 POT 的 GPD shape 参数 ξ 在不同置信水平（90%/95%/99% 分位数阈值）下显著不一致（|ξ_90 - ξ_99| > 0.15）——尾部厚度非均匀，单一 σ 或单一 ξ 不足以描述
2. §3.9 回测第 3 法 Acerbi-Szekely Z2 在 95% 和 99% 置信水平下表现分化（一个 PASS 一个 reject）——不同尾部校准不一致
3. A 股极端行情（如涨跌停潮）下 99% VaR 回测连续 reject 但 95% VaR PASS——深尾部需要独立建模

**与 MVP 的关系**：
- MVP（当前）：§3.1 参数法 + 历史模拟取 max，单一分布描述整个收益序列
- 远期 QbSD：多分位数独立建模，精化非正态/非对称分布下的 VaR
- 关系：QbSD 落地后作为 §3.1 的**增强层**（非替代）——触发条件满足时用 QbSD 多分位数 VaR 替代参数法 VaR 参与取 max；不满足时仍用 §3.1 参数法
- 依赖：scikit-learn QuantileRegressor 或 statsmodels quantile_regression（CPU 即可，无需 GPU）
- Phase 3 远期：需特征工程（X_t 构造）+ 回测验证 QbSD 优于参数法的 A 股实证

**Vol-Targeting**（远期 Phase 2）：
- BlackRock 比例控制 vol-targeting（31号已登记）
- 用途：连续闭环替代离散分档
- 2026-07 Soloviov 实证：GARCH vs EWMA 统计不可区分（DM p=0.57），验证当前 30 日滚动 vol 替代 GARCH 的合理性

**Vol-Targeting 与 §3.6 30 日波动率调整的关系**（v1.1.0）：
- MVP（当前）：§3.6 30 日波动率 z-score 法是**离散分档**（每增 10% → 仓位减 20%），已施工
- 远期 Vol-Targeting：**连续闭环**替代——用 GARCH 预测目标波动率，连续调整仓位使实际波动率逼近目标
- 关系：Vol-Targeting 落地后**替代** §3.6 离散分档（不叠加），§3.6 z-score 法作为 Vol-Targeting 失效时的回退方案保留
- Soloviov 2026-07 实证支持：GARCH vs EWMA 统计不可区分（DM p=0.57），§3.6 的 30 日滚动 vol 已是 Vol-Targeting 的合理近似，远期升级收益有限——Vol-Targeting 优先级降为 P3

### §3.17 施工流程总览（5 流程闭环）

**5 流程闭环**（v1.1.0 D8，对齐 35号 §3.17 的 6 流程闭环总览；一个交易日的 VaR/ES 监控生命周期）：
1. **T-1 收盘后**：§3.11 回测验证（4 法 + Basel 交通灯）→ §3.10 校准/重构/恢复（PASS/RECALIBRATE/REBUILD → 次日配置）→ §3.18 盘后持久化（VarBreachState → intraday_recalc_log → clean/dirty P&L → var_model_status）
2. **T 盘前**：§3.19 盘前初始化（加载 VarBreachStateMachine + entry_var + var_model_status）→ §3.1/§3.2 盘前 VaR/ES 计算（calculate → assess → breach 状态机 transition）→ 产出 var_cvar + breach_state 喂入 35号 §3.10 drawdown_controller
3. **T 盘中（9:30-15:00）**：§3.12 盘中重算（7 条触发 → IntradayVarResult）↔ 35号 §3.13 盘中实时风控循环（30 秒轮询检测 → 调用重算 → 用新 var_cvar 重新 evaluate）

**衔接规则**：
1. **§3.19 → §3.1/§3.2**：盘前初始化成功（加载 VarBreachStateMachine + entry_var + var_model_status）才进入盘前计算；var_model_status == UNAVAILABLE → 跳过动态计算，用 §3.10 REBUILD 静态映射
2. **§3.1/§3.2 → 35号 §3.10**：盘前 var_cvar + breach_state → `drawdown_controller.evaluate(var_breach_state=breach_state)`
3. **§3.12 ↔ 35号 §3.13**：盘中循环检测 7 条触发 → 调用 §3.12 重算 → IntradayVarResult → 35号 §3.13 重新裁决（取最严覆盖盘前）
4. **§3.11 → §3.10**：日终 VarBacktestReport.action → RiskOrchestrator：PASS 无动作 / RECALIBRATE 动作 1-4 / REBUILD 动作 1-2
5. **§3.10 → §3.18**：校准/重构动作完成 → 触发 §3.18 盘后持久化
6. **§3.18 → §3.19**：盘后标记可加载 → 次日 §3.19 据此恢复而非冷启动

> **与 35号文档的关系**：本备忘 5 流程闭环与 [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md) 的 6 流程闭环共享 `RiskOrchestrator`（§6.5 待裁定）。VaR/ES 是 35号 §3.10 日度循环盘前段 + 35号 §3.13 盘中循环的**子步骤**（喂入 drawdown_controller），不是独立流程。§3.18 盘后持久化与 35号 §3.18 共享 `state_store` 持久化层。

### §3.18 盘后状态持久化流程

**盘后持久化顺序**（v1.1.0 D9，对齐 35号 §3.18 的盘后持久化）（`postmarket_persist_var()`，与 §3.19 加载逆序配对；原子性：全部写入成功才标记可加载，部分失败则次日 §3.19 冷启动默认 NORMAL）：

- **阶段 0：审计门控**（v1.1.1 E1）：本函数在 35号 §3.18 之后执行（RiskOrchestrator 编排：daily_auditor.audit() → 35号 §3.18 → 36号 §3.18）；35号审计失败（audit.passed=False）则本函数不执行。ES ≥ VaR 不变式校验：`var_95 < 0 或 cvar_95 < var_95` → `log_persist_skipped(reason="var_cvar_invariant_violation")` + 标记 `VAR_INVARIANT_VIOLATION_SKIP`，不持久化
- **阶段 1**：VarBreachStateSnapshot（§3.15 当日终态）→ `save_var_breach_state`
- **阶段 2**：盘前 VaR/ES 基线 `VarCvarBaseline(var_95, cvar_95)` → `save_premarket_baseline`（供次日 §3.12 盘中对比 + §3.16 回撤归因；entry_var 持久化由 35号 §3.18 阶段 4b 承载）
- **阶段 3**：intraday_recalc_log（§3.12，可空）→ `save_intraday_recalc_log` + `log_intraday_recalc_summary(total, significant)`
- **阶段 4**：clean/dirty P&L 双轨（§3.13）→ `save_pnl_dual`
- **阶段 5**：var_model_status（AVAILABLE/UNAVAILABLE，§3.10 REBUILD 动作 1）→ `set_var_model_status`；UNAVAILABLE → `log_var_model_unavailable(reason="REBUILD_triggered")`
- **阶段 6**：backtest_report（§3.11，若有）→ `save_backtest_report`
- **阶段 7**：标记 `VAR_COMPLETE`（原子提交点）→ `mark_persistable` + `log_var_persist`

> **E2 状态值配对**（v1.1.1）：36号 "VAR_COMPLETE" 与 35号 §3.18 "DRAWDOWN_COMPLETE" 配对——§3.19 盘前初始化检查两阶段都 COMPLETE。

**与 §3.19 的配对约束**：

| §3.19 加载顺序 | §3.18 保存顺序 | 配对约束 |
|---|---|---|
| 阶段 1 加载 VarBreachStateMachine | 阶段 1 保存 VarBreachStateSnapshot | state + breach_date + consecutive_days 必须一致（§3.15 转换守卫依赖） |
| 阶段 2 加载 premarket_baseline | 阶段 2 保存 premarket_baseline | 供 §3.12 盘中重算对比（var_change_ratio > 20% → 显著） |
| —（intraday_recalc_log 当日产生当日消费，不跨日加载） | 阶段 3 保存 intraday_recalc_log | 供回测分析 + §3.10 RECALIBRATE 触发 |
| —（clean/dirty P&L 当日产生，回测时历史加载） | 阶段 4 保存 clean/dirty P&L | 回测验证（§3.9）加载历史 clean P&L 构造 BacktestObservation |
| 阶段 3 加载 var_model_status | 阶段 5 保存 var_model_status | UNAVAILABLE → 跳过动态计算用静态映射（§3.10 REBUILD） |
| —（backtest_report 当日产生当日消费） | 阶段 6 保存 backtest_report | 供 §3.10 校准/重构决策 + §3.16 回撤归因参考 |
| —（首次启动无前置） | 阶段 7 标记可加载 | 原子提交点：§3.19 据此判断"恢复"vs"冷启动 NORMAL" |

### §3.19 盘前初始化流程

> **v1.1.0 D10**：对齐 35号 §3.15，本节是 36号文档的盘前加载流程。

**盘前初始化**（`premarket_initialization_var()`，顺序不可调换：先状态机防错误状态计算，再基线供盘中对比，最后 var_model_status 决定是否动态计算）：

- **阶段 1**：`load_var_breach_state` → 无快照则冷启动默认 NORMAL（保守）+ `log_var_state_recovery("cold_start_default_NORMAL")`；有快照则恢复 + `log_var_state_recovery(f"restored_{state}")`
- **阶段 2**：`load_premarket_baseline(T-1)` → None=首次启动/前日未持久化，§3.12 盘中重算 var_change_ratio 跳过（无基线对比）
- **阶段 3**：`load_var_model_status(T-1)` → None 默认 AVAILABLE；UNAVAILABLE 时检查业主是否已 ResetConfirmation 解除（对齐 35号 §3.14）：未解除 → alert(WARNING) + 不拒绝启动，用 §3.10 REBUILD 静态映射（VaR 固定 3%, CVaR 固定 5%），`var_dynamic_calculation=False`；已解除 → 恢复 AVAILABLE + `log_var_model_recovered`
- **阶段 4**：`load_entry_var`（35号 §3.18 阶段 4b 持久化，供 35号 §3.16 回撤归因消费；None=首次启动/前日未持久化）

**与 35号 §3.15 的协同**（跨文档契约）：
- 35号 §3.15 加载 DrawdownStateMachine + peak NAV + nav_history + entry_var（35号是 entry_var 主消费方，§3.16 回撤归因）
- 36号 §3.19 加载 VarBreachStateMachine + premarket_baseline + var_model_status（36号是 premarket_baseline 主消费方，§3.12 盘中对比）
- 两者共享 `state_store` 持久化层，各加载各自负责的状态

**代码差距**（待施工）：
1. 无 `state_store.save/load_var_breach_state` 接口——VarBreachStateMachine 当前内存态
2. 无 `state_store.save/load_premarket_baseline` 接口——盘前基线未持久化
3. 无 `state_store.set/load_var_model_status` 接口——REBUILD 标记未持久化
4. 无 `state_store.save/load_pnl_dual` 接口——clean/dirty P&L 双轨未持久化
5. 无 `state_store.save_intraday_recalc_log` 接口——盘中重算日志未持久化

> **裁决**：盘前初始化 + 盘后持久化暂缓为 §6 待裁定施工项，与 35号 §3.15/§3.18 同步落地（共享 state_store 基础设施）。最小补丁：① VarBreachStateMachine 持久化到 DB（复用 daily_auditor 已有持久化）；② var_model_status 持久化（REBUILD 标记需跨日）；③ clean/dirty P&L 双轨持久化（回测验证依赖 clean P&L 历史）。

### §3.20 盘中因子暴露与相关性矩阵（作战地图 BM-RC-04-C 闭合，production 补强）

**定位**（v1.10.1 作战地图全覆盖补丁——BM-RC-04-C，因子暴露与相关性矩阵，L4 风控域，production，MOD-RK-16 `core/risk_decomposition.py`）：BM-RC-04 盘中持仓风控监控的子环节——VaR（§3.1/§3.2）与回撤（35 号）之外的风险维度：firm 层**因子暴露矩阵 + 相关性矩阵**的盘中定时计算，输出暴露矩阵（CTR-P1-008 契约）→ BM-RC-04-D 告警生成（E-RK-01/E-RK-03）→ BM-RC-03 Kill Switch 判定。

**裁定**：盘中因子暴露监控**以 firm 层定时计算形态补强，不新建独立模块**——复用 MOD-RK-16（risk_decomposition.py）计算内核，盘中定时驱动，超限额走既有告警链。理由：① 因子暴露是 VaR 的结构性补充——VaR 答"组合风险多少"，因子暴露答"风险集中在哪些因子上"，CTR-P1-008 暴露矩阵是前端 RiskDashboardSnapshot 与告警链的共同契约；② 盘中**定时**（非每 Tick）即可——因子载荷日频更新（D-FACTOR 供给），盘中变化来自持仓与价格，计算频率对齐 §3.12 盘中重算节奏（事件驱动联动 + 定时全量兜底）；③ production 补强非新设计——MOD-RK-16 已建，本节补"盘中实时计算"的设计契约落点。**重评条件**：① D-FACTOR 因子载荷盘中更新频率升级（日频→盘中多次）时，暴露矩阵计算频率同步升级；② 因子数据缺失降级（跳过检查）实盘频发时，评估独立风险数据管道重建（BM-RC-11 已 deprecated 的替代方案）。

**契约/参数/接口**：

| 项 | 裁决值 | 来源 |
|---|---|---|
| 触发 | 盘中定时（兜底全量）+ §3.12 七条重算触发联动（事件驱动） | BM-RC-04-C trigger"盘中定时" |
| 阈值 | FACTOR_EXPOSURE 限额（单因子暴露上限，配置注入不硬编码） | BM-RC-04-C threshold |
| 输入 | 因子暴露（D-FACTOR）+ 持仓（D-EX-CORE 持仓快照） | BM-RC-04-C consumes |
| 输出 | 暴露矩阵（CTR-P1-008）→ BM-RC-04-D 告警判定 | BM-RC-04-C data_flow |
| 计算内容 | firm 层因子暴露矩阵（组合权重 × 因子载荷 → 各因子净暴露）+ 持仓相关性矩阵（组合内标的两两相关，供 corr<0.7 监控口径消费——注意：此为**监控层**相关性矩阵，与 30号 §3.1 拒绝的**决策层**协方差估计不同，监控不进入下单优化链路） | BM-RC-04-C process |
| 降级 | 因子数据缺失 → 跳过因子暴露检查（告警留痕，不阻断交易） | BM-RC-04-C degradation |

**与 25 号 §3.7#8 策略级暴露监控的层级分工**：[25_multifactor_strategy_detail](25_multifactor_strategy_detail.md) §3.7#8 HoldingDriftMonitor 是**策略级**暴露/偏差监控（单策略内部"当前持仓 vs 目标权重"的因子暴露+行业偏离，盘后每日调用，critical 时触发 RebalanceTrigger 强制换仓）；本节是 **firm 层**聚合暴露矩阵（跨策略求和后的组合因子暴露，盘中定时，超限额走 BM-RC-04-D 告警）。层级链：策略级（25 号 #8，盘后，策略内纠偏）⊂ firm 级（本节，盘中，组合级告警）→ 告警（BM-RC-04-D）→ Kill Switch 判定（BM-RC-03）。两层不重复计算：策略级管"策略自己有没有跑偏"，firm 级管"全组合加起来会不会撞因子限额"。

## 4. 考虑过的替代方案

### §4.1 Conformal Risk Control (CRC)（远期增强）

**方案**：用 conformal prediction 框架提供有限样本覆盖保证的 VaR/ES 区间。核心算法：CRC（λ 校准 + 交换性假设覆盖保证）、RWC（Regime-Weighted Conformal，Schmitt 2026-08 v3）、TWC（Time-Weighted Conformal 时间衰减加权）。

**拒绝理由（MVP 不采纳，远期登记）**：
1. 交换性假设在金融时序上不成立（有时变波动率、regime 切换）
2. RWC/TWC 缓解但引入额外超参（regime 识别、时间衰减率）
3. MVP 优先施工已有源码实现的 4 法回测，conformal 作为 Phase 2 增强

**远期演进登记**：

| 方法 | 来源 | 说明 |
|---|---|---|
| CRC | arXiv:2107.07511 | 基础 conformal risk control |
| RWC v3 | Schmitt 2026-08-03 | regime 加权，TWC-first 部署路径 |
| TWC | Schmitt 2026-08-03 | 时间衰减加权 |
| Joint VaR/ES Conformal Bounds | Ye 2026-08-06 Mathematics 14(15):2847 | 联合 VaR/ES conformal，ES 不可独立 elicitable 的 bounded monotone loss |
| ResCP | arXiv:2510.05060 | training-free reservoir conformal，区间宽度减 60% |
| COP | arXiv:2512.07770 ICLR 2026 | distribution-informed online CP |
| BAWS | arXiv:2603.01157 | bootstrap 自适应窗口选择 |
| DASC | arXiv:2606.15953 | drift-aware spectral conformal |
| Tail-Specific Conformal Intervals | Cuonzo & Deliu 2026-06 | 单侧共形区间左尾强制覆盖 |
| Anytime-Valid CRC | Hultberg et al. 2026-02 | anytime-valid conformal |
| Non-exchangeable CRC | - | 非交换性 conformal |
| Ochoa Rivera & Tewari 2026-05 | arXiv:2605.12668 | Online Multi-Quantile Nested Conformal |

**ResCP A 股 ESN reservoir 参数验证计划**：论文"60% 宽度缩减"是相对 NexCP 结论，未相对本项目 EWMA-Normalized 基线验证，须 A 股 head-to-head 决择避免"论文好看但 A 股不适配"。四要素：①CSI300+CSI500 walk-forward 2019-2023 训练/2024 OOS；②reservoir 参数扫描 192 组合；③四项验收指标；④决择门 ResCP 须同时优于 EWMA-Normalized 才采纳。

**ERCIM 145 GREM 默认**（已施工）：ERCIM News 145 2026-07 Ruodu Wang——第 4 法 E-backtesting 工程化默认规约，GREM 推荐 betting process + 四级多区制告警替代二元拒绝，已在 `var_backtester.py e_backtesting()` 实现。

### §4.2 CAESar 联合动态估计（远期）

**方案**：CAESar（Conditional Autoencoder for Expected Shortfall）联合动态估计 VaR 和 ES。

**拒绝理由**：① 需要神经网络（autoencoder），与个人系统可解释性优先原则冲突；② 训练数据需求大，A 股单标的样本不足；③ MVP 历史模拟 + POT 已满足需求。

### §4.3 EVaR Expectile 框架（远期）

**方案**：EVaR（Entropy VaR）基于相对熵的 VaR，Expectile 作为 EVaR 的对偶。

**拒绝理由**：① 概念复杂度高，可解释性差；② 与现有 VaR/ES 框架的增量收益不明确；③ 远期研究登记（回测验证路径见 §4.22 expectile e-backtest）。

### §4.4 OCE Risk Minimization（远期，2026-08-07 新增）

**方案**：arXiv:2608.07113 Gupte/Bhat/Prashanth（IIT Madras）2026-08-07 Optimized Certainty Equivalent（OCE）风险的样本优化算法——OCE 涵盖 entropic risk、mean-variance risk、CVaR 平滑变体；给出 OCE 与 UBSR 的特征化联系，构造基于 UBSR 样本平均近似的 OCE 估计器并建立 MSE 界；进一步给出 OCE 梯度估计器与非渐近 MSE 界，嵌入随机梯度算法。

**远期登记理由**：① OCE 是包含 CVaR/ES 的统一风险度量族，样本优化算法与收敛速率保证对动态 VaR/ES 监控数值计算底层有指导价值；② 尤其适合需要平滑 CVaR 变体（避免分位数不连续）的工程实现；③ Phase 2+ 远期。

### §4.5 Bayesian EVT Hawkes-AR-Gumbel 联合 CVaR 估计（远期）

**方案**：Ballesteros 2026-05 arXiv:2605.23353 联合模型：GPD 严重度 + Hawkes 频率聚类 + AR regime 持续性 + Gumbel 尾部依赖 + HMC 贝叶斯后验。

**拒绝理由**：① 模型复杂度极高（5 组件联合）；② HMC 采样计算成本高；③ 独立 LDA 99.995% CVaR 低估 40% 的结论需 A 股验证；④ Phase 4+ 远期。

### §4.6 MFCCA 多重分形交叉相关分析（远期）

**方案**：Kakinaka 2026-08 arXiv:2608.04987 MFCCA（Multifractal Cross-Correlation Analysis）：符号保留 + 多重分形 + 无分形误检修复，协方差矩阵 regime 转变非参数检测。

**拒绝理由**：① 用途为 regime 检测（与 36号 VaR/ES 计算正交）；② 登记 35号 §4.5 远期演进参考。

### §4.7 Lambda-quantiles 推广框架（远期，2026-08-10 新增）

**方案**：arXiv:2608.07122 Bellini & Liebrich 2026-08-10 Lambda-quantiles——将经典分位数的常数概率水平 λ 替换为函数参数 Λ: R→[0,1] 的推广，给出有界变分情形下的混合表示定理。

**远期登记理由**：① Lambda-quantiles 是 VaR/ES 族风险度量的推广框架；② 对构建自定义尾部风险监控指标（如对损失幅度敏感的分位数变体）有理论指导；③ 理论性偏强，落地需进一步工程化；④ Phase 3+ 远期。

### §4.8 Preference-Robust Distortion Risk Measures（远期，2026-08-05 新增）

**方案**：arXiv:2608.02854 Bernard & Pesenti 2026-08-05 偏好稳健的失真风险度量——决策者偏好不确定时给出稳健的风险度量构造，涉及 VaR/ES 类失真度量的稳健化。

**远期登记理由**：① 对在 VaR/ES 监控中加入偏好稳健性（应对风险厌恶参数不确定性）有理论价值；② 落地需进一步工程化；③ Phase 3+ 远期。

### §4.9 CPPI（组合配置层远期候选）

**方案**：CPPI（Constant Proportion Portfolio Insurance）+ RB 两阶段法。

**东方证券 2026-04 A 股实证反证**：CPPI+RB 两阶段法 2006-2026 年化 13.41%/Sharpe 1.53 优于等权/RP，三层架构兜底 gap risk 反证拒绝理由 #2。

**仍不采纳理由**（35号 §4.1）：① 定位正交：CPPI 是组合配置层，36号是风险监控层；② 无保本承诺：个人系统无保本义务；③ 架构耦合：CPPI 引入 floor/gap risk 管理复杂度；④ 可解释性优先：CPPI 的乘数机制比 5 级阈值更难解释。

### §4.10 Zhuang 期权隐含 ES bounds（远期参考）

**方案**：Zhuang 2026-07-28 期权隐含 model-free ES bounds。

**A 股可行性**：A 股有 50ETF/300ETF/中证 1000 ETF 期权 + 股指期权，组合层 put 对冲可行（35号 §4.8）。

**远期参考**：期权隐含 ES 提供市场前瞻性尾部风险估计，与历史模拟 ES（回顾性）互补。

### §4.11 Bivariate Orthogonal Polynomials ES 回测（远期，2026-08-10 新增）

**方案**：Yang Lu & Sullivan & Hurlin（Concordia/Aix-Marseille/Orléans）SSC 2026-06 "Backtesting Expected Shortfall: Accounting for both Duration and Severity with Bivariate Orthogonal Polynomials"——双维度 ES 回测框架：duration 维度（VaR 违规间隔序列）× severity 维度（违规损失幅度序列），用 bivariate orthogonal polynomials 推导两序列正交矩条件，提出 model-free Wald test 涵盖 VaR/ES 无条件/条件覆盖率回测，突破 PIT-based ES 回测不能分离 frequency 和 severity 的限制。

**远期登记理由**：① §3.9 MVP 4 法中 Christoffersen 只检 duration、Z2 只检 severity——Bivariate OP **联合** duration + severity；② model-free Wald test 工程实现简单（无需 GARCH 拟合），适合个人系统；③ 登记为 §3.9 远期第 14 法（Bivariate OP Wald test）；④ Phase 2+ 远期。

**与现有 4 法的关系**：Kupiec POF/Christoffersen = duration 维度子集；Acerbi-Szekely Z2 = severity 维度子集；E-backtesting 与 Bivariate OP 正交可叠加；Bivariate OP = duration × severity 联合，补充分离检测。

### §4.12 ERCIM 145 e-values Post-hoc 风险审计（远期，2026-08-10 新增）

**方案**：ERCIM News 145 (2026-07) Special theme "E-values: Statistical Testing for the 21st Century"——Etienne Gauthier (Inria/ENS/PSL) "Rethinking Conformal Prediction for Constrained Environments"：e-values 支持 post-hoc control of uncertainty——观测数据后可调整统计保证（p-values 观测后修改参数即失去统计有效性），允许回顾性审计和调整，可在飞行中导出自适应覆盖水平，无需额外数据或复杂数据分割。

**远期登记理由**：① §3.9 第 4 法 E-backtesting 用 e-values 做前向监测，Gauthier 扩展回顾性审计用途——VaR breach 后可审计"过去 N 天的 VaR 预测事后看是否校准良好"，不需预设 α 水平；② 与 §3.10 互补：前向 E-backtesting 触发 RECALIBRATE，回顾性 e-values 审计确认 RECALIBRATE 是否有效；③ Phase 2+ 远期（需 E-backtesting 工程化稳定后扩展）。

### §4.13 Fuzzy Conformal Prediction Sets（远期，2026-08-10 新增）

**方案**：arXiv:2509.13130 Koning & van Meer (Erasmus University Rotterdam) "Optimal Conformal Prediction, E-values, Fuzzy Prediction Sets and Subsequent Decisions"：fuzzy conformal confidence sets 将传统二元 inclusion/exclusion 推广为 [0,1] 区间"排除程度"；连接 fuzzy confidence sets 与 e-values（排除程度等价于不同置信水平下的排除）；fuzzy confidence set 是一种 predictive distribution，有更合适的误差保证；推导最优 conformal confidence sets（minimax 最优测试问题）；推广到非交换性设置之外的任意模型预测置信集。

**远期登记理由**：① §3.1 VaR 是单点估计，fuzzy conformal 可提供区间+程度的尾部风险估计——"损失超过 X 的排除程度是 0.7"比"VaR=X"信息更丰富；② 对 drawdown_controller 的启示：position_cap 可基于 fuzzy 排除程度连续调整，而非硬阈值离散分级；③ 与 §4.1 CRC 互补：CRC 提供 coverage 保证，Fuzzy CP 提供 degree 表达；④ Phase 3+ 远期（需 conformal 预测层就绪）。

### §4.14 E-backtesting v6 GRO/GREE/GREL 最优构造（远期，2026-08-10 新增）

**方案**：arXiv:2209.00991v6 Qiuqi Wang/Ruodu Wang/Johanna Ziegel (Georgia State/Waterloo/ETH) 2026-04-15——e-process 最优构造方法系统化：GRO（Growth-Rate Optimal，最大化期望对数增长率，单一假设最优）/ GREE（Growth-Rate for Expected Exceedance，ES 专用）/ GREL（Growth-Rate for Expected Loss，期望损失专用）/ GREM（混合，已在 var_backtester.py 实现）；v6 关键贡献：用 identification functions 刻画 VaR/ES backtest e-statistics 唯一形式。

**远期登记理由**：① 当前 §3.9 第 4 法用 GREM 通用混合，GREE 专为 ES 设计可能比 GREM 对 ES 检验更敏感；② characterization 结果为 §3.9 远期第 7 法 Fissler-Ziegel 联合回测提供理论基础；③ 远期可配置 `e_process_method = "GRO" | "GREE" | "GREL" | "GREM"` 按检验目标选择：Acerbi-Szekely Z2 失败时优先切换 GREE，Kupiec POF 失败时优先切换 GREL；④ Phase 2+ 远期（需 var_backtester.py 扩展支持多 e-process 构造方法选择）。

### §4.15 Ye et al. 2026-08-06 Finite-Sample Conformal Risk Bounds for Joint VaR/ES（远期，2026-08-10 新增）

**方案**：[MDPI Mathematics 14(15):2847](https://www.mdpi.com/2227-7390/14/15/2847) Ye/Qiu/Zhu/Ladikas 2026-08-06 "Finite-Sample Conformal Risk Bounds for Joint Value-at-Risk and Expected-Shortfall Forecasting Under Non-Exchangeable Financial Time Series"：金融尾部风险观测非可交换（serial dependence + regime shifts），ES 不可独立 elicitable——标准 conformal 的 exchangeability 假设失效；方法：tune 单一 inflation parameter by conformal risk control on bounded monotone loss（couples VaR breach frequency with breach magnitude normalized by VaR-ES gap）。理论保证：交换性下有限样本期望风险控制；非可交换下 swap-distance bound + regime-drift bound（含 explicit cumulative β-mixing cost）+ high-probability realised-path statement + heavy-tail rate D(p−1)/p。实证：8 汇率 + Bitcoin + GIFT-Eval，前一月 FRED-MD vintages 因果构建 regime（避免 look-ahead），weighted controller violation rate 2.51%，Fissler-Ziegel score 0.431（vs 最强 conformal baselines 0.441/0.439），增益集中于 turbulent regimes。

**远期登记理由**：① 直接针对 A 股强时序依赖（波动率聚集）+ regime shift（牛熊转换）的非可交换性；② ES 不可独立 elicitable 是 §3.9 回测核心难题（Z2 仅间接检验），本文提供 joint 校准的有限样本保证；③ 与 §4.1 CRC / RWC 互补：CRC 是基础，RWC 是 regime 加权，本文是 joint + non-exchangeable 理论保证；④ 与 §3.9 E-backtesting 正交：E-backtesting 管回测检验，conformal risk control 管校准调整；⑤ Phase 3+ 远期（需 conformal 预测层 + regime 特征工程，与 §4.1/§4.14 同批次）。

### §4.16 TailRisk-Trans Transformer-based 动态 VaR/ES（远期，2026-08-10 新增）

**方案**：[Frontiers in Business and Finance Volume 3 Issue 1](https://sprcopen.com/index.php/FBF/article/download/742/641/1991) Wang & Bai (HKU/Columbia) 2026 "TailRisk-Trans"：4 组件——金融数据预处理层（微结构+衍生品隐含+宏观因子）+ Market Transformer Encoder + Tail-Risk Prediction Head（联合预测 VaR/ES/CVaR）+ Extreme-Event-Aware Attention；可微分分位数回归层 `q_α = h·W₄ + b₄`，quantile loss `L_q = Σ ρ_α(yᵢ − q_α,ᵢ)`。实证：99% VaR violation rate 4.12%→3.47%（15.8% 改进），quantile loss 2.684，ES score 3.892（vs 最强 baseline Transformer-TS）。

**远期登记理由**：① 过度工程风险：训练需大量数据（A 股单标的日度 <10 年）+ GPU 算力，与 §2.3 算力约束冲突；② 可解释性不足：attention 权重难向业主解释，与 35号 §3.19 过度工程红线 3 冲突；③ 登记为 §3.1 的 Phase 3+ 深度学习远期候选（待 GPU 算力 + 可解释 AI 成熟后评估）；④ 与 §4.15 的关系：TailRisk-Trans 是 forecaster 本身，Ye et al. 是 conformal calibration wrapper——远期可组合。

### §4.17 ReSGA 检索增强自分组自编码器尾部风险大模型（远期，2026-08-10 新增）

**方案**：[arXiv:2606.04576](https://arxiv.org/abs/2606.04576) Zhang, Zhu & Zhu 2026-06 "ReSGA: A Large Tail Risk Model for Learning Value-at-Risk and Expected Shortfall"（港大+厦门大学）：百万参数级检索增强自分组自编码器——编码器映射潜在表示，检索器按特征相似性分组，解码器组内联合预测 VaR/ES。实证：1926-2023 美股月度 + 153 公司特征，改进主要由数据复杂度而非模型复杂度驱动，展示组重要性可解释性与跨市场迁移能力。

**远期登记理由**：① 过度工程风险：百万参数级模型与 §2.3 算力约束冲突；② 轻量化提取价值：按特征相似性分组+组内联合估计可脱离大模型实现（k-NN/层次聚类替代深度检索器，<50 行无 GPU）；"数据复杂度比模型复杂度更重要"印证 §3.1 取 max 在特征充分时已足够；③ 与 §4.16 正交（横截面分组 vs 时序），远期可组合；④ 与 §3.1 的关系：当前单标的独立计算无分组共享，Phase 2 可按行业/因子暴露聚类分组共享样本池（panel data 思路）提高小样本稳定性；⑤ Phase 3+ 远期（需 GPU + 153 维特征库，与 §4.16 同批次）。

### §4.18 D'Innocenzo et al. 2026 JBES 单整合尾形参数动态 VaR/ES（远期，2026-08-10 新增）

**方案**：[JBES DOI:10.1080/07350015.2026.2619541](https://www.tandfonline.com/doi/abs/10.1080/07350015.2026.2619541) D'Innocenzo/Lucas/Schwaab/Zhang（Bologna/VU Amsterdam/ECB/Sveriges Riksbank）2026（[ECB WP 3166](https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp3166~4e485ab256.pt.pdf)）"Joint Extreme Value-at-Risk and Expected Shortfall Dynamics with a Single Integrated Tail Shape Parameter"：EVT 条件 GPD-POT 动态框架——① unit root-like integrated autoregressive dynamics for GPD tail shape（捕捉尾部厚度持续性）；② POTs 按阈值重标，仅一个时变参数描述整个尾部。理论保证：integrated time-varying parameter model 及 filter 的平稳性/遍历性/可逆性参数区域 + MLE 一致性与渐近正态性。实证：两种加密货币汇率，single-parameter 模型捕捉 VaR/ES 动态（尤其极端尾部）具竞争力。

**远期登记理由**：① 直接增强 §3.2 POT：当前固定 90% 阈值 + 静态 GPD(ξ, β)，本文让 ξ 随时间动态演化，适配 A 股牛熊转换的尾部厚度变化；② 单参数简约适合个人系统：A 股短样本下双参数时变 GPD 易过拟合，单参数降低估计风险；③ 与 §3.3 Uehara 双门控正交可组合（Uehara 解决阈值选择，本文解决尾形动态）；④ 比 §4.16 深度学习更适合可解释性优先原则（半参数 score-driven + 渐近理论保证）；⑤ Phase 2+ 远期（与 §3.16 FHS 同批次评估，尾部建模思路不同可择优）。

### §4.19 Jia & Han 2026 自适应 conformal 组合选择（远期，2026-08-10 新增）

**方案**：[DMO-FinTech Workshop Paper](https://academicworkshops.github.io/DMO-FinTech/docs/2026_Paper_portfolio_selection_with_adaptive_conformal_prediction.pdf) Jia & Han（HKUST Guangzhou）2026 "Portfolio selection with adaptive conformal prediction"：model-free 组合选择框架——conformal prediction 估计投资风险（VaR 从 prediction set 下界导出）+ projected gradient descent 优化组合权重（受投资者约束）+ adaptive conformal inference（梯度下降调 prediction set 宽度，适应 distribution shift）+ 历史候选步长 re-weighting；covariate 从 "virtual portfolios" 导出（组合收益而非个股收益，降维）。实证：美股 conformalized 策略（含 short-selling 约束）一致优于等权组合与 non-conformal counterparts。

**远期登记理由**：① 组合层 conformal 保证：§4.1 CRC/RWC 是单资产层面，本文扩展到组合选择层；② model-free 适配个人系统：不依赖特定预测模型假设，可 wrap 现有 VaR 预测器；③ 与 §4.15 正交（单资产非可交换 vs 多资产自适应）；④ 比 Kato arXiv:2410.16333（有限菜单选组合不涉及 position sizing）更接近本项目连续仓位调整需求；⑤ A 股适配：板块轮动下 adaptive conformal 自动适应风格切换，short-selling 约束天然适配 A 股不能做空；⑥ Phase 3+ 远期（需 conformal 预测层 + 组合优化层，与 §4.1/§4.15 同批次）。

### §4.20 Fu 2026-01 动态因子半参数 VaR/ES（realized measures）（远期，2026-08-10 新增）

**方案**：[arXiv:2601.01142](https://arxiv.org/abs/2601.01142) Fu（Jinan University）2026-01 "A dynamic factor semiparametric model for VaR and expected shortfall driven by realized measures"：CAViaR 分位数递归 + 动态 ES-VaR gap（捕捉时变尾部严重度）+ 测量方程（多 realized measures 转高频风险新息）+ 动态因子模型（提取公共高频尾部风险因子）；双通道分离：分位数水平（risk level）与尾部厚度（tail thickness）通过不同风险通道影响。实证：一致优于 quantile regression / EVT-based / GARCH-type 基准。

**远期登记理由**：① 高频信息融入尾部风险生成层：§3.1 用日度收益（低频），本文用 realized measures（5 分钟 RV/BV/RK）驱动 VaR/ES；② A 股高频数据可得性：Level-1 行情 5 分钟 K 线数据管道已就绪可复用；③ 双通道分离与 §3.1 参数法（μ, σ 定分位数）+ §3.2 POT（ξ 定尾部厚度）二分架构同构——本文是两者的动态联合版；④ 与 §4.18 路径不同（EVT-GPD 尾形动态 vs CAViaR + realized measures）可择优或组合；⑤ Phase 2+ 远期（需高频 realized measures 管道 + CAViaR 递归工程化，与 §3.16 FHS 同批次）。

### §4.21 CVaR 风险感知 Q-Learning 自适应有限预算训练（远期，2026-08-10 新增）

**方案**：[arXiv:2608.04305v1](https://arxiv.org/abs/2608.04305) Yifan Wu / Junjie Lei / Wenjie Huang，ICAIF '26（Milan）2026-08-05 "Adaptive Finite-Budget Training for CVaR Risk-Aware Q-Learning"（v1.10.0 补全论文细节）：CVaR Risk-Aware Q-Learning（RaQL）——model-free 双时间尺度估计器，用 CVaR 替代期望 Q 值作为内在目标函数（risk-aware RL 非 constrained RL）；原始 RaQL 有限预算下行为脆弱（固定内循环超参 → 不稳定值估计、持续 Bellman 残差、低效样本复用）。关键设计原则：**保留原 CVaR 估计器和 Bellman 不动点不变**，仅重设计训练过程——6 协同机制：① per-cell inner-step sizing（不稳定 cell 多投入）② outer-rate-matched decay synchronization（内循环学习率衰减与外循环速率匹配）③ 类 VaR 内变量短期早期校正 ④ coverage-first-then-greedy 样本分配（前 40% 预算覆盖后贪婪）⑤ 成熟内估计渐进后缀聚合 ⑥ 关键尺度数据驱动标定。理论保证：有限样本收敛性 + CVaR 估计 PAC bound。

**实证结果**（20 random seeds，856,000 内循环转换样本）：Bellman 残差降 85%（MeanBEQ 1.2202→0.1854；MeanBEV 1.1624→0.0535）；跨 CVaR level/discount/budget 稳定；OOS Sharpe 0.9281，maxDD 6.46%（含交易成本）；buy-and-hold 收益更高但波动率 47.93% vs RaQL 9.57%——风险调整后表现显著优于 buy-and-hold。关键洞见：仅修改训练过程不动风险目标即可显著提升可靠性和风险调整后表现。

**与本项目的关系**：① vs §3.5 触发动作：规则驱动 5 级分级 → position_cap 映射 vs RL 驱动风险感知仓位调整——"规则 vs 学习"替代关系；② vs §3.1 VaR 计算：离线估计（独立模块）vs 在线学习（嵌入决策循环）；③ vs 31号 Conformal Kelly：静态仓位 sizing vs 动态仓位+动作 learning；④ vs §4.27（v1.10.0）：§4.27 管分布形状漂移检测（监控层输入端），本节管 CVaR 估计训练稳定性（训练层），二者正交；36号当前 CVaR/ES 估计是静态/批量的，本节提供有限预算在线训练稳定性机制——若远期引入 RL 风险感知决策，6 机制控制器是 RaQL 落地的前置稳定性保障。

**远期登记理由**：① 过度工程风险：RL 需训练数据+环境模拟器+奖励函数设计，与算力+可解释性约束冲突；§3.5 规则驱动已 Phase 1 验证且可解释；② Garg Paper I 负面结果（hand-coded rule > flat RL）同样适用——Phase 3+ 优先 hand-coded CVaR 约束（§3.5 规则）而非 RL；③ 轻量化提取："用 CVaR 替代期望 Q 值"可脱离 RL 实现——§3.5 的 5 级分级已隐含 CVaR 约束（BLACK 级 CVaR > 10% → 全清仓），Phase 2 可评估更细粒度 CVaR 驱动仓位调整（CVaR 每增 1% → 仓位减 X%）而非上 RL；④ **Phase 4 鲁棒性阶段**（v1.10.0 对齐，原 Phase 3+ 上调）——若 40号执行 RL 已落地且验证有效，再评估风险层 CVaR RL。

### §4.22 Standard and Comparative E-backtests for General Risk Measures（远期，2026-08-10 新增）

**方案**：[arXiv:2511.05840](https://arxiv.org/abs/2511.05840) Jiao, Wang & Zhao 2025-11 "Standard and comparative e-backtests for general risk measures"：① 标准 e-backtest 扩展——e-value 框架从 (VaR, ES) 二元扩展到任意可识别风险度量（mean/variance/VaR/ES/expectile），基于 identification function 构造 test supermartingales，Casgrain et al. 2022 静态理论动态化；② 比较 e-backtest——H₀⁻: 内部模型至少与标准模型一样准 / H₀⁺: 内部模型至多与标准模型一样准，基于 e-processes 双向检验，complement 标准 backtest"通过 ≠ 正确"盲区（Fissler et al. 2016）；③ expectile 回测——expectile 是唯一 elicitable 谱风险度量（Newey & Powell 1987），本文首次提供 expectile model-free e-backtest，为 §4.3 EVaR 提供回测验证路径。

**与本项目的关系**：① §3.9 MVP 4 法是标准 backtest（单一模型准确性），比较 backtest 提供模型间比较能力——Phase 2 可比较 conservative_max vs FHS vs 历史模拟的预测质量（当前仅 Basel 交通灯 + GREM 告警定性判断，缺定量 head-to-head）；② §4.14 是 (VaR,ES) 专用最优构造，§4.22 是通用化泛化——§4.14 是 §4.22 特例；③ 填补 §4.3 回测缺口；④ 可嵌入 §3.10 RECALIBRATE——internal vs standard 比较拒绝 H₀⁻ → 触发重评 method 选择。

**远期登记理由**：① MVP 4 法已覆盖 Basel 要求 + ES 直接回测 + anytime-valid，Phase 1 底线已满足；② 比较 backtest 需多模型并行（Phase 2 FHS 落地后才有比较对象）；③ expectile 回测随 §4.3 之后；④ Phase 2+ 远期。

**轻量化提取价值**：核心洞察"通过标准 backtest ≠ 模型正确（alternative 过宽）"立即应用于 §3.11 解读——审计日志标注"PASS ≠ 模型正确，仅 = 未检测到显著偏差"，避免过度自信；无需代码改动。

### §4.23 Discrete Moment Matching（DMM）VaR Bracketing——稳健尾部替代（远期，2026-08-10 新增）

**方案**：[arXiv:2601.09927](https://arxiv.org/abs/2601.09927) Aditri 2026-01 "Efficiency versus Robustness under Tail Misspecification: Importance Sampling and Moment-Based VaR Bracketing"：VaR 在 99%+ 高置信度是稀有事件估计，对尾部模型选择极敏感——重要性采样（IS）名义模型下高效但系统性低估厚尾真实 VaR；DMM 通过有限矩约束（均值/方差/偏度/峰度）在离散化网格构造分布集合，VaR 区间 = 集合上 [min, max]——矩越多区间越紧但数值可行性下降。IS vs DMM 权衡：IS 追求效率（低方差但模型误设偏差大），DMM 追求稳健（显式建模分布模糊性但区间宽效率低）；方差缩减单独不足以在模型不确定性显著时保证尾部风险估计可靠。

**与本项目的关系**：① vs §3.2 POT：POT 参数化 GPD 拟合，DMM 非参数化半稳健矩约束——GPD 拟合失败且历史模拟样本不足时，DMM 是第三条路径（比纯历史模拟点估计稳健）；② vs §3.3 Uehara：双门控拒绝 GPD 外推时可用 DMM 矩约束构造 ES 区间（比回退历史模拟更保守）；③ vs §3.1 conservative_max：DMM 区间上界可作第三法纳入 max，厚尾场景进一步强化保守性；④ A 股适配：厚尾+偏斜可被 4 阶矩捕捉，短样本下比 POT 稳健（不需 GPD 假设）。

**远期登记理由**：① MVP POT + 历史模拟双轨已覆盖，GPD 失败有兜底；② DMM 区间宽——矩少则太宽（保守但无用）多则数值不可行，需校准矩数量与网格精度，工程化成本高于 POT；③ Phase 2+ 评估：POT 频繁拟合失败或 Uehara 频繁拒绝外推时作为稳健替代。

**轻量化提取价值**：核心洞察"方差缩减 ≠ 尾部准确（模型误设下 IS 系统性低估）"立即应用于 §3.1 参数法解读——参数法正态假设在厚尾下系统性低估 VaR，conservative_max 正是缓解；Phase 1 审计日志标注"参数法低估厚尾是已知局限，conservative_max 是缓解而非消除"。

### §4.24 Lévy-stable VaR/ES Horizon Correction——封闭形式厚尾传播（远期，2026-08-10 新增）

**方案**：[arXiv:2511.07834](https://arxiv.org/abs/2511.07834) Vlasiuk 2025-11 "Lévy-stable scaling of risk and performance functionals"（Columbia University）：数据驱动 Lévy 窗口 [τ_UV, τ_IR] 内收益服从 α-稳定分布（α ∈ (1,2)），尺度 τ^{1/α}；窗口外聚合为有限方差 √τ 体制；窗口边界与 α 从对数斜率+两段拟合识别。封闭形式公式：以锚定 horizon τ₀ 为基准，VaR/ES/Sharpe/Kelly-under-VaR/drawdown 的 Lévy 与高斯传播差异为显式偏差项 `(τ/τ₀)^{1/α} - (τ/τ₀)^{1/2}`。实证：Lévy 传播窗口内跨 horizon 超限率平坦（覆盖率一致），高斯传播随 horizon 偏离。非参数化：仅需 α 和固定尾部分位数。

**与本项目的关系**：① vs §3.1 参数法：正态假设 α=2，本文提供厚尾（α<2）封闭修正 `VaR_Lévy = VaR_Gaussian × (τ/τ₀)^{1/α - 1/2}`——A 股 α 估计 <2 时参数法低估程度可量化；② vs §3.7 数据窗口：Lévy 窗口为 60 日窗口选择提供理论依据——窗口应在 Lévy 稳定区间内，超出 τ_IR 后 √τ 聚合使历史模拟分位数偏向高斯；③ vs §3.6 30 日波动率：年化 √252 修正为 252^{1/α}——α<2 时年化因子更大，波动率低估程度可量化；④ 跨文档：35号 §4.24 登记同文 drawdown 公式，本节登记 VaR/ES 公式，两者同源。

**远期登记理由**：① α 估计需长样本（对数斜率需多 horizon 数据点），A 股短样本下不稳定；② Lévy 窗口识别复杂（两段拟合 + 截止点定位），工程化成本高；③ Phase 2+ 评估：§3.1 参数法频繁低估（回测超限率 >5%）且 A 股 α 估计稳定时引入 Lévy 修正。

**轻量化提取价值**：核心洞察"高斯 vs Lévy 传播偏差 = (τ/τ₀)^{1/α} - (τ/τ₀)^{1/2}"——持有期越长（T 越大）√T vs T^{1/α} 偏差越大；Phase 1 holding_period_days=1（日 VaR）偏差最小，远期多日 VaR 需关注。

### §4.25 Set-Preserving P2E Calibrator——p-value 到 e-value 桥接（远期，2026-08-10 新增）

**方案**：ICML 2026 [Alami, Zakharia, Ben Taieb "Set-Preserving Calibration from Conformal P-Values to E-Values"](https://icml.cc/virtual/2026/poster/62147)：标准 conformal prediction 用 p-value，但 p-value 难跨模型/数据分割合并依赖证据；e-value 更适合组合，但 p→e 直接转换会改变预测集（set-altering）导致过度保守。P2E Calibrator 将 conformal p-value 转为 e-value 而不改变原始预测集（set-preserving）——保持 CP 实际效率同时获得 e-value 理论丰富性。应用：cross-conformal prediction（CCP）与 conformal aggregation（CA），e-value 方法在两者中均满足 1-α 覆盖保证且提升效率。

**与本项目的关系**：① vs §3.9：Kupiec/Christoffersen 是 p-value 检验、E-backtesting 是 e-value 检验——P2E 提供统一框架，p-value 转 e-value 后与 e-process 合并为单一累积证据指标；② vs §4.14：传统 p-value 回测输出可"翻译"为 e-value 与 §4.14 e-process 对齐；③ vs §4.22：现有 p-value 回测结果转 e-value 后纳入比较框架，降低比较 backtest 工程门槛；④ 多回测证据合并：§3.11 对 4 法分别判读，P2E 可统一转 e-value 合并——单一合并 e-process > 1/α 即拒绝，比"任一法 reject 即 RECALIBRATE"更精确（避免多重比较问题）。

**远期登记理由**：① MVP 4 法分立判读 + 取最严已满足 Phase 1；② P2E 需 conformal prediction 基础设施（§4.14/§4.17 均远期），前提未满足；③ Phase 2+ 评估：§4.14 与 conformal 落地后作为统一回测框架评估。

**轻量化提取价值**：核心洞察"多检验 p-value 直接合并会导致多重比较问题，e-value 合并提供更严格证据累积"立即用于 §3.11 解读——4 法中 2 法 p-value 略高 0.05（边缘 PASS）不应视为"模型正确"（多重比较下联合证据可能已足够拒绝）；Phase 1 审计日志标注边缘 PASS 的多重比较风险。

### §4.26 VaR/ES Forecast Combination via Model Confidence Set（MCS）——模型不确定性下的预报组合（远期，2026-08-10 新增）

**方案**：[arXiv:2406.06235v2](https://arxiv.org/abs/2406.06235) Amendola/Candila/Naimoli/Storti 2026 "Combining Value-at-Risk and Expected Shortfall forecasts via the Model Confidence Set"（International Journal of Forecasting, 2026）+ [arXiv:2508.16919v2](https://arxiv.org/abs/2508.16919) Taylor & Wang 2026-05 "Combining a Large Pool of Forecasts of Value-at-Risk and Expected Shortfall"（Oxford Saïd + Sydney）：当前 §3.1 `max(parametric, historical)` 是最粗粒度组合策略（永远选更保守者不管模型质量）——VaR/ES 预报受多重不确定性影响（模型误设/数据限制/估计程序/采样频率/regime 变化），无单一模型在所有条件下一致最优；取 max 忽略模型互补性（参数法平稳期准、历史模拟厚尾期准，max 在平稳期过保守浪费仓位、在厚尾期恰好够但非因选对）。

**MCS 方法**（Amendola et al.）：① 严格一致联合 VaR-ES 损失（Fissler-Ziegel）对候选模型打分；② Model Confidence Set 等价性检验（Hansen et al. 2003/2011）识别统计上不可区分的 Set of Superior Models（SSM）；③ SSM 加权组合（等权/性能加权/正则化）——组合预报比任何单一模型更稳健；④ 实证：9 股票指数 2.5%/1% 水平，组合预报通过标准回测且一致进入 SSM。

**大池组合方法**（Taylor & Wang）：① 90 种预报方法池（GARCH/CAViaR/CARE/简单法）；② 非性能组合：trimmed mean、mixtures；③ 性能加权组合：Fissler-Ziegel score 权重 + 正则化；④ 关键发现：**仅 6 种多样性方法的小池 + 性能加权 > 90 种大池任意组合**——多样性比数量重要。

**与本项目的关系**：① max 是 MCS 组合的退化特例（2 模型权重 {0,1} 赢者通吃），MCS 是有原则的推广（Fissler-Ziegel 评估 → SSM 筛选 → 性能加权组合替代"无脑选保守者"）；② 与 §3.9 回测基础设施天然衔接（Z2/E-backtesting 与 Fissler-Ziegel 同族 strictly consistent loss，工程复用度高）；③ 为 §4.16/§4.17 深度学习模型提供与传统模型的组合框架（避免全押新模型）；④ 与 §4.22 互补（comparative backtest 判"谁更好"，MCS 判"谁不可区分"并组合）。

**远期登记理由**：① MVP 仅 2 法，MCS 需 ≥3-4 候选模型（2 模型 SSM 退化为一对一比较）——Phase 2 引入 FHS + 蒙特卡洛达 4 法后落地，Phase 3 引入 CAESar/QbSD 达 6 法效益最大化；② 工程化成本：Fissler-Ziegel 损失 + MCS p-value 检验 + 滚动性能加权约 200-300 行 Python，仅依赖 scipy；③ 与 §3.1 兼容：method 配置从 `conservative_max` 扩展为 `conservative_max | mcs_combination | performance_weighted`，max 作 fallback 保留。

**轻量化提取价值**（Phase 1 立即可用）：
- **max 的认知偏差修正**：MCS 表明取 max 不总是最优（平稳期过保守、厚尾期恰好够是因 HS 更保守而非更准）——审计日志记录两法分叉度 `divergence = |VaR_param - VaR_hist| / VaR_95`，持续 >20% 标记 MODEL_DIVERGENCE_HIGH 供 Phase 2 MCS 评估
- **Taylor & Wang 多样性原则**：6 法多样性 > 90 法数量——指导 Phase 2/3 优先引入方法论多样性（参数→半参数→非参数→深度学习）而非同类堆砌

**不过度工程审查**：MCS 需 ≥4 候选模型（Phase 2 后满足）+ ~300 行，在 Phase 2 预算内；Phase 1 不改动 conservative_max。

### §4.27 Information-Geometric Bayesian 风险监控（远期，2026-08-10 新增）

**方案**：[arXiv:2608.01294v1](https://arxiv.org/abs/2608.01294) Quirini 2026-08-04 "An Information-Geometric Framework for Bayesian Credit Risk Monitoring"（q-fin.RM）——信息几何（Fisher 度量/KL 散度/统计流形测地线）构建贝叶斯风险监控框架：① 后验分布→流形映射（Beta/Normal-Inverse-Gamma 参数化）；② Fisher 信息矩阵定义 Riemannian 度量；③ 测地距离 regime 检测（校准期 vs 当前期后验分布测地距离 > 阈值 → regime 切换；测地距离优于 KL——KL 非对称且不满足三角不等式）；④ 曲率→风险集中（曲率高 = 后验不确定性集中，曲率突变预警尾部风险聚集）；⑤ 在线更新（每新观测贝叶斯更新 → 重映射 → 测地漂移 → 滚动监控）。

**与本项目的关系**：① vs §3.11 VaR 校准触发：当前是周期性 + 违规驱动，信息几何提供第三种触发（测地漂移比周期性更及时、比违规驱动更早——违规是事后，漂移是事前分布变化）；② vs §3.6 漂移检测：PSI/KS/MMD/CUSUM 是欧氏空间统计量，测地距离是流形空间度量——对分布形状变化（偏度/峰度高阶矩漂移）更敏感；③ vs §4.17 ReSGA：正交（横截面分组 vs 时序分布漂移）远期可组合；④ vs 10号 regime 检测：隐式分布漂移监控（无显式状态标签，只报"变了"）vs 显式状态识别——更轻量（无状态数选择/EM 收敛问题）但解释性差（不告诉"变成什么"）。

**A 股适用性评估**：中低——迁移需 ① PnL 分布参数化（Normal-Inverse-Gamma 或 Student-t 族）② Fisher 度量解析推导（需分布族 Fisher 矩阵闭式解）③ 测地线数值计算（通常无解析解需数值 ODE）；A 股 PnL 厚尾+时变波动率+regime 切换频繁，后验分布族选择是关键难点。

**轻量化提取价值**（Phase 1-2 立即可用，<30 行无第三方库）：
- **对称 KL 散度漂移监测**：测地距离一阶近似是 Jeffreys 散度（(KL(P‖Q)+KL(Q‖P))/2）——Phase 2 用 scipy.stats.entropy 计算滚动窗口 PnL 分布 vs 校准期分布的对称 KL，超阈值触发 VaR 校准审查（信息几何"平民版"）
- **分布形状变化 > 均值变化**：§3.6 漂移检测增偏度/峰度漂移监控（滚动窗口偏度/峰度 vs 校准期超 2σ 触发 SHAPE_DRIFT 标志），作 PSI/KS 的形状维度补充

**过度工程审查**：**Phase 4+ 远期登记，远超个人系统 Phase 1-3 预算**——完整框架需微分几何背景 + 数值测地线 ODE + 分布族 Fisher 矩阵解析推导 + 参数化敏感性分析，与 Mamba/SSM 同类过度工程（学术优雅但工程成本远超收益）。Phase 4 鲁棒性阶段若 §3.6 漂移检测 + §3.11 校准触发 + §4.14 e-backtesting 三层仍无法捕捉分布形状突变，才评估完整框架；Phase 1-2 仅采纳轻量化提取。

**定位**：Phase 4+ 远期候选（完整框架），Phase 2 轻量提取（对称 KL 散度漂移 + 形状漂移监控）。

### §4.28 Geodesic Execution Slippage——Fisher 流形测地滑点预测与早期告警（远期，2026-08-10 新增）

**方案**：Entropy 2026, 28(6), 705；[DOI:10.3390/e28060705](https://doi.org/10.3390/e28060705)（preprint [arXiv:2605.0757](https://arxiv.org/abs/2605.0757), 2026-05-12）"Geodesic Execution Slippage: A Statistical Physics Framework for Cryptocurrency Liquidity Risk"，Moroke & Metsileng——用统计物理框架替换 flat-fee 执行成本模型：执行滑点 = Markov-switching GARCH 最大熵模型 Fisher 信息流形上的测地弧长（geodesic arc length）；同一参数向量派生联合曲率-拓扑碎片化告警（curvature + TDA 持续同调拓扑特征）：① Fisher 信息流形（MS-GARCH 参数空间 Riemannian 流形）；② 测地弧长 = 执行滑点（比 flat-fee/线性冲击模型更准确捕捉流动性状态非线性变化）；③ 流形曲率突变 + TDA 拓扑特征变化 → 联合触发流动性危机早期告警。消融实验：移除 geodesic MSE +2.9%、移除 TDA +2.1%、移除曲率 +1.5%——三组件协同不可拆。实证：5 加密市场（BTC/ETH/XRP/LTC/BCH）+ 2,253 日观测全部最低预测误差；10% 显著性下 MCS 唯一保留模型（vs Amihud/Kyle λ/Almgren-Chriss 等 6 基线）。关键洞见：联合曲率-拓扑告警在 4 次危机（含 Terra 2022-05/FTX 2022-11）中位数提前 2 天触发，早于价格型 circuit breaker 阈值——直接服务于 35 号回撤 Protocol 早期预警；不需额外数据或自由参数（除上游 MS-GARCH 估计管线）。

**与本项目的关系**：① 连接 36号风险监控 → 35号回撤 Protocol：36号管"组合风险多少"（事后度量），本节管"流动性危机将临"（事前告警），告警信号可喂入 35号回撤 Protocol 作 circuit breaker 之外的早期触发源；② vs §4.27：同一数学工具（Fisher 信息流形）的不同应用——§4.27 监控分布形状漂移，本节度量流动性状态距离；③ vs §3.5/§3.14：当前是价格/事件驱动，本节提供流形拓扑驱动的第三类触发源（提前 2 天级）。

**A 股适用性评估**：中——论文在加密市场验证（24h 交易），MS-GARCH 通用（regime 切换模型与交易时段无关）；迁移需 ① A 股 PnL/成交滑点序列 MS-GARCH 估计 ② Fisher 矩阵数值计算 ③ TDA 持续同调（gudhi/ripser 拓扑库）；盘中集合竞价跳空 + 涨跌停限制可能影响滑点结构，需 A 股特化校准。

**过度工程审查**：Phase 5+ 远期登记，远超个人系统 Phase 1-3 预算——完整框架需 MS-GARCH regime 估计管线 + Fisher 矩阵数值计算 + 测地线数值积分 + TDA 持久同调库，与 §4.27 同类过度工程；但提供 circuit breaker 之外"提前 2 天"早期告警能力——若 Phase 4 §3.6 漂移检测 + §3.14 BlackSwanSignal 仍无法足够提前捕捉流动性危机，Phase 5+ 评估本框架；Phase 1-2 不采纳，仅登记诚实账本。

**定位**：Phase 5+ 远期候选（需 Fisher 流形估计基础设施 + TDA 工具栈；与 §4.27 共享微分几何/数值测地线工具栈，额外需 TDA 持续同调库）；加密市场已验证，A 股适用性需评估。

## 5. 上限定义

### 5.1 系统上限

| 维度 | 上限 | 理由 |
|---|---|---|
| VaR 方法 | 参数法 + 历史模拟（取 max） | Phase 1，蒙特卡洛/GARCH 远期 |
| ES 方法 | 历史模拟 + POT | 联合动态估计远期 |
| 回测方法 | 4 法 MVP（13 法框架） | 9 法远期 |
| 黑天鹅模式 | 7 模式 | 框架固定 |
| 系统性风险级别 | 5 级 | 框架固定 |
| 数据窗口 | 60 交易日（回测 250） | A 股平衡稳定性与时效性 |
| 盘中重算频率 | 事件驱动（7 条触发） | 非定时轮询 |

### 5.2 演进路径

> v1.9.0 补：演进路径与 §4.1-§4.27 全量对齐——按"风险度量族 / 回测族 / conformal 族 / 深度学习族 / 半参数族 / 审计族"六类重组，确保每项 §4.x 远期登记可追溯到 Phase。

```
Phase 1 (当前): 参数法 + 历史模拟 + POT + 4 法回测 + 5 级 + 7 黑天鹅
    ↓
Phase 2 (远期):
  ├─ 风险度量族: + FHS + 蒙特卡洛 + Vol-Targeting
  ├─ conformal 族: + Conformal (RWC/TWC) + Fuzzy CP Sets (§4.13) + 自适应 conformal 组合选择 (§4.19)
  ├─ 回测族: + 9 法回测
  ├─ 预报组合: + MCS forecast combination (§4.26，≥4 法候选池后替代 max)
  ├─ p/e 桥接: + P2E Calibrator (§4.25)
  └─ 轻量提取: + 对称 KL 散度漂移 + 形状漂移监控 (§4.27 Information-Geometric 轻量版，<30 行)
    ↓
Phase 3 (远期):
  ├─ 风险度量族: + QbSD + CAESar + Bayesian EVT Hawkes + EVaR/Expectile (§4.3) + OCE (§4.4)
  │              + Lambda-quantiles (§4.7) + Preference-Robust Distortion (§4.8)
  ├─ 尾部修正: + DMM VaR Bracketing (§4.23) + Lévy-stable horizon correction (§4.24)
  ├─ 半参数族: + D'Innocenzo 单整合尾形参数 (§4.18) + Fu 动态因子半参数 (§4.20)
  ├─ 回测族: + Comparative e-backtests (§4.22) + Bivariate Orthogonal Polynomials ES 回测 (§4.11)
  │           + E-backtesting v6 GRO/GREE/GREL (§4.14)
  ├─ 审计族: + ERCIM 145 e-values Post-hoc 风险审计 (§4.12)
  └─ 期权参考: + Zhuang 期权隐含 ES bounds (§4.10，需期权数据管道)
    ↓
Phase 4+ (远期): + TailRisk-Trans Transformer 动态 VaR/ES (§4.16) + ReSGA 检索增强自编码器 (§4.17)
                  + Information-Geometric Bayesian 完整框架 (§4.27，需微分几何 + 测地线 ODE)
```

**不在 VaR/ES 演进路径的 §4.x 项**（定位正交，登记于本号仅作诚实账本）：
- §4.5 Bayesian EVT Hawkes-AR-Gumbel：Phase 4+ 鲁棒性阶段（5 组件联合，复杂度极高）
- §4.6 MFCCA：regime 检测，登记 35号 §4.5 远期演进参考（与 VaR/ES 计算正交）
- §4.9 CPPI：组合配置层远期候选（非 sleeve 级 VaR/ES 方法，同 35号 §6.30）
- §4.15 Ye et al. Finite-Sample Conformal Risk Bounds：理论界证明（非可施工方法，支撑 conformal 族合理性）
- §4.21 CVaR Q-Learning：RL 风险感知训练（属 alpha 层训练，非监控层；v1.10.0 补全 6 协同机制+Bellman 残差 -85% 实证+OOS Sharpe 0.9281+§4.27 关系，Phase 4 鲁棒性阶段）
- §4.28 Geodesic Execution Slippage：执行成本预测+危机早期告警层（Fisher 流形测地弧长+TDA，连接 36号风险监控→35号回撤 Protocol 早期触发；Phase 5+ 远期候选，加密市场验证 A 股待评估）

### 5.3 为何是上限

1. **个人系统算力限制**：Phase 1 CPU 即可（<5ms），Phase 2/3 需 GPU
2. **可解释性优先**：参数法/历史模拟的数学逻辑明确，conformal/CAESar 的保证条件复杂
3. **风险优先原则**：Phase 1 已覆盖生存底线（5 级 + Kill Switch），Phase 2/3 是精度提升
4. **过度工程审查**（30号 §2.5.6）：VaR/ES 5 级 + 7 黑天鹅已从活跃节流精简为计算与监控，保留计算但活跃节流层级精简

## 6. 待裁定

| 项 | 暂缓理由 | 重评条件 |
|---|---|---|
| Conformal Risk Control (CRC) 采纳时机 | 交换性假设不成立，RWC/TWC 引入超参 | A 股 walk-forward 验证 RWC 覆盖率 ∈ [0.94, 0.96] |
| ResCP ESN reservoir A 股适配 | 论文 60% 宽度缩减未相对 EWMA 基线验证 | head-to-head 四要素验证通过 |
| FHS 采纳时机 | Christoffersen 独立性失败未实际发生 | 回测出现独立性失败（LR_ind p < 0.05） |
| 蒙特卡洛法 | 算力限制 | GPU 环境就绪 |
| Bayesian EVT Hawkes | 模型复杂度极高 | Phase 4 鲁棒性阶段 |
| 期权隐含 ES bounds | 期权数据接入待建 | 50ETF/300ETF 期权数据管道就绪 |
| OCE Risk Minimization | 理论框架，落地需工程化 | Phase 2+ 需平滑 CVaR 变体时 |
| BM-RC-07-A"三阶段演进"口径修订（开放问题，v1.10.1 登记） | BM 定义"参数法+历史模拟→蒙特卡洛(GPU)→Basel III 三角"缺 FHS/QbSD/CRC 中间层，与本备忘 §5.2 演进路径口径不一致；裁定 VaR 演进口径以本备忘路线为准（§3.1 口径对齐注），本备忘不越界改 BM 真源 | 作战地图维护批次同步修订 BM-RC-07-A 环节定义 |

## 7. 待定问题（讨论要点）

以下来自 00_index §3 G17 讨论要点，已逐项对齐落入 §3 决策。

- [x] ① VaR_95 计算（历史模拟/参数法）→ §3.1 取 max
- [x] ② ES_95 计算 → §3.2 历史模拟 + POT
- [x] ③ 入场 VaR/ES 基准 → §3.4 开仓日盘前快照
- [x] ④ 触发动作（VaR>1.2×减仓20%/ES>1.3×再减20%）→ §3.5 5 级系统性风险 + BlackSwanSignal API
- [x] ⑤ 30 日波动率调整（每增10%→仓位减20%）→ §3.6 z-score 法
- [x] ⑥ 数据窗口 → §3.7 60 交易日（回测 250）
- [x] ⑦ 与回撤 Protocol 的协同 → §3.8 取最严不累乘

## 8. 引用

### 8.1 框架与源码

- [00_index_trading_decision](00_index_trading_decision.md) §3 G17
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5.4
- [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md)（G16，依赖项，entry VaR 持久化跨文档契约）
- [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md)（G18，涨跌停潮协同）
- `src/zephyr/risk/core/var_calculator.py` v0.1.0（MOD-RK-05）
- `src/zephyr/risk/core/tail_risk_monitor.py` v0.1.0（MOD-RK-15）
- `src/zephyr/risk/core/var_backtester.py` v0.1.0（MOD-RK-05B）
- `src/zephyr/risk/core/daily_auditor.py` v0.2.0（MOD-RK-20）
- `src/zephyr/position/core/drawdown_controller.py` v0.1.0（MOD-POS-008）
- battle_map_09_risk_control（当前状态快照）

### 8.2 学术引用

#### 回测方法

- Kupiec 1995 POF (Proportion-of-Failures) 似然比检验
- Christoffersen 1998 条件覆盖率（独立性 + 覆盖率）
- Acerbi & Szekely 2014/2017 Z2 ES 回测（非参数）
- Wang, Wang & Ziegel arXiv:2209.00991v6 (2026-04) E-backtesting
- ERCIM News 145 (2026-07) Ruodu Wang GREM 默认 betting process + 多区制告警
- arXiv:2511.05840 Jiao/Wang/Zhao 2025-11 Standard and comparative e-backtests for general risk measures（→ §4.22，标准+比较双向 e-backtest，expectile 回测）
- Pele 2026-06 ES 精度极限 (nα)^{-1/2}
- arXiv:2607.11653 Feature-Aware Auditing
- ICML 2026 Alami/Zakharia/Ben Taieb Set-Preserving Calibration from Conformal P-Values to E-Values（→ §4.25，p→e 桥接，多回测证据合并）

#### Conformal Risk Control

- arXiv:2107.07511 CRC (Conformal Risk Control)
- Schmitt 2026-08-03 RWC v3 (Regime-Weighted Conformal)
- arXiv:2510.05060 ResCP (training-free reservoir conformal)
- arXiv:2512.07770 COP (distribution-informed online CP, ICLR 2026)
- arXiv:2603.01157 BAWS (bootstrap 自适应窗口)
- arXiv:2606.15953 DASC (drift-aware spectral conformal)
- Cuonzo & Deliu 2026-06 Tail-Specific Conformal Intervals
- Hultberg et al. 2026-02 Anytime-Valid CRC
- arXiv:2605.12668 Ochoa Rivera & Tewari Online Multi-Quantile Nested Conformal
- Ye 2026-08-06 Mathematics 14(15):2847 Joint VaR/ES Conformal Risk Bounds
- Jia & Han 2026 (HKUST Guangzhou) Portfolio selection with adaptive conformal prediction
- Kato arXiv:2410.16333 Conformal Predictive Portfolio Selection

#### EVT 与尾部风险

- arXiv:2605.27474 Uehara 2026-05 双门控 EVT 阈值选择
- arXiv:2606.28540 Belzile & Davison 2026-06 EVT 阈值选择程序系统综述
- arXiv:2605.23353 Ballesteros 2026-05 Bayesian EVT Hawkes-AR-Gumbel
- Zhuang 2026-07-28 期权隐含 ES bounds
- D'Innocenzo/Lucas/Schwaab/Zhang 2026 JBES DOI:10.1080/07350015.2026.2619541 单整合尾形参数动态 VaR/ES
- arXiv:2601.09927 Aditri 2026-01 DMM VaR Bracketing（→ §4.23，矩约束稳健尾部替代，IS vs DMM 效率-稳健权衡）

#### Lévy-stable 厚尾传播

- arXiv:2511.07834 Vlasiuk 2025-11 Lévy-stable scaling of risk and performance functionals（→ §4.24，封闭形式 VaR/ES/drawdown horizon 修正，偏差项 (τ/τ₀)^{1/α}-(τ/τ₀)^{1/2}，跨文档 35号 §4.24 drawdown 公式同源）
- González Cázares & Mijatović 2022 Finance and Stochastics 26(4) Drawdown simulation in Lévy models via stick-breaking Gaussian approximation（MLMC 估计 Lévy 过程 drawdown/duration，SBG coupling）

#### 深度学习与动态 VaR/ES

- Wang & Bai 2026 TailRisk-Trans Transformer-based 动态 VaR/ES（Extreme-Event-Aware Attention）
- Zhang/Zhu/Zhu arXiv:2606.04576 ReSGA 检索增强自分组自编码器尾部风险大模型
- Fu arXiv:2601.01142 2026-01 动态因子半参数 VaR/ES（realized measures）

#### OCE 与广义风险度量

- arXiv:2608.07113 Gupte/Bhat/Prashanth 2026-08-07 OCE Risk Minimization Using Samples
- arXiv:2608.07122 Bellini & Liebrich 2026-08-10 Lambda-quantiles under the microscope
- arXiv:2608.02854 Bernard & Pesenti 2026-08-05 Preference robust distortion risk measures

#### 波动率与 Vol-Targeting

- Soloviov 2026-07 vol-targeting 受控实证（GARCH vs EWMA DM p=0.57，vol-targeting 核心价值是 MaxDD 控制非 Sharpe 提升）
- Kakinaka 2026-08 arXiv:2608.04987 MFCCA 多重分形交叉相关分析
- Xin 2026-04 DOI:10.12677/sa.2026.154095 两步波动率（EWMA 长期趋势基准 + GARCH 短期预测，沪深300ETF期权实证，连续波动率状态识别信号）

#### VaR floor 理论

- arXiv:2608.05623 Li/Lyu/Wei 2026-08-06 Non-concave VaR 约束下赌博回本行为

#### 预报组合（Forecast Combination）

- arXiv:2406.06235v2 Amendola/Candila/Naimoli/Storti 2026 "Combining VaR and ES forecasts via the MCS"（Int. J. Forecasting, 2026）（→ §4.26，MCS 等价性检验 + SSM 加权组合，Fissler-Ziegel 联合损失，9 指数 2.5%/1% 实证）
- arXiv:2508.16919v2 Taylor & Wang 2026-05 "Combining a Large Pool of Forecasts of VaR and ES"（Oxford Saïd + Sydney）（→ §4.26，90 法大池 trimmed mean/mixtures/performance-weighted，6 法多样性小池+性能加权最优）

#### 监管

- CP9/26 PRA IMA（ES 97.5% IMA 基准）
- US Basel III Endgame NPR
- FSB 2026-06-10 AI 稳健实践咨询报告

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G17 讨论要点占位 |
| 2026-08-10 | 1.0.0 | 骨架→active 重建 | v1.29.x 内容因工作树还原丢失（未提交即被还原，不在任何悬空 blob/不可达 commit/stash 中），从源码实现（var_calculator/tail_risk_monitor/var_backtester/daily_auditor/drawdown_controller）+ 30号 §2.5.4 框架 + 35号跨文档契约重建为 active v1.0.0：核心决策 16 节 + 替代方案 10 节 + 30+ 篇 2026-08 研究远期登记 |
| 2026-08-10 | 1.1.0 | §3.14-§3.19 跨文档协同补全（D3/D4/D6/D9/D10 + E1/E2/E3 修复）——补登 | 与 35号 v1.31.0 跨文档流程交接链修复同步。**D3** §3.15 VarBreachStateMachine 跨重启持久化（VarBreachStateSnapshot + save/load）；**D4** §3.15 与 35号回撤状态机协同（var_breach_state 参数 + 乘性折扣 NORMAL×1.0/BREACHED×0.8/RECOVERY×0.9）；**D6** §3.14 black_swan_detector 模块归属（MVP RiskOrchestrator 聚合 / 远期独立模块）+ 7 类 BlackSwanMode MVP 事件源映射表；**D9** §3.18 盘后状态持久化流程（7 阶段 + §3.19 配对约束表）；**D10** §3.19 盘前初始化流程（加载顺序 + 冷启动守卫）。**E1** §3.18 持久化顺序（audit()→35号§3.18→36号§3.18，35号审计失败则36号不执行）；**E2** 状态值配对（"VAR_COMPLETE" vs "DRAWDOWN_COMPLETE"）；**E3** 双 RECOVERY 叠加澄清（effective_cap = 阶梯值×0.9 + 下限 max(0.0) + DUAL_RECOVERY_PROLONGED >20日告警） |
| 2026-08-10 | 1.2.0 | §4.15 Ye et al. Finite-Sample Conformal Risk Bounds for Joint VaR/ES + §4.16 TailRisk-Trans 远期登记 | 2026-08 最新研究 2 篇：① Ye et al.（Mathematics 14(15):2847）非可交换 + joint VaR/ES conformal risk bounds（swap-distance + regime-drift bound）；② Wang & Bai TailRisk-Trans 4 组件 Transformer（99% VaR violation 4.12%→3.47%）。均 Phase 3+ 远期登记，MVP 不改动 conservative_max + POT 双轨 |
| 2026-08-10 | 1.3.0 | §4.17 ReSGA 检索增强自分组自编码器尾部风险大模型（arXiv:2606.04576）远期登记 | 按特征相似性分组后组内联合预测 VaR/ES，"数据复杂度比模型复杂度更重要"；Phase 3+ 远期，轻量提取：分组+组内联合估计 Phase 2 可作轻量增强（<50 行无 GPU）；与 §4.16 正交（横截面 vs 时序）。同步 00_index v1.2.0→v1.3.0 |
| 2026-08-10 | 1.4.0 | 施工流程算法完整性审查 + 17 项缺失/不一致修复 + §4.18-§4.20 三篇 2026-08 新研究登记 | **HIGH**：①§9 补登 v1.2.0；②回测样本不足处理（§3.10 阈值+降级+冷启动）；③§3.16 QbSD 施工规约补全（触发条件+算法+与 MVP 关系）；④§3.11 action 映射对齐 §3.10（Christoffersen LR_ind reject 纳入 RECALIBRATE）。**MEDIUM**：⑤§3.12 多触发优先级/去重/防抖；⑥§3.12 取最严=position_cap 取 min；⑦§3.13 T+1 对 clean/dirty P&L 影响；⑧§3.14 BS-007→kill_switch_advised 映射；⑨§3.16 FHS 切换失败冷却期；⑩§3.19 静态映射 entry_var=None 边界；⑪§3.19 首次启动无 premarket_baseline 降级；⑫POT 日常计算失败兜底。**新增**：§4.18 D'Innocenzo 单整合尾形参数 + §4.19 Jia & Han 自适应 conformal 组合选择 + §4.20 Fu 动态因子半参数。同步 00_index v1.3.0→v1.4.0 |
| 2026-08-10 | 1.5.0 | §9 补登 v1.1.0 + §4.22 comparative e-backtests 新增 + §8.2 补 Xin 两步波动率 + §1 状态行版本漂移修复 + frontmatter v1.5.0 | 一致性修复 4 项（§9 缺 v1.1.0 条目 / §1 版本漂移 / §8.2 有引用无 §4.x 节 / 缺 A 股波动率实证）；§4.22 Jiao/Wang/Zhao arXiv:2511.05840——标准 e-backtest 通用化 + comparative 双向检验 + expectile 首次 model-free e-backtest。同步 00_index v1.4.0→v1.5.0 |
| 2026-08-10 | 1.6.0 | §4.23 DMM VaR Bracketing + §4.24 Lévy-stable Horizon Correction + §4.25 P2E Calibrator 新增 + §5.2/§8.2 同步 + frontmatter v1.6.0 | 2026-08-10 最新研究 3 篇：①§4.23 arXiv:2601.09927 DMM 矩约束稳健尾部替代（POT 失败第三路径）；②§4.24 arXiv:2511.07834 Lévy-stable 封闭形式 horizon 修正（偏差项 (τ/τ₀)^{1/α}-(τ/τ₀)^{1/2}，跨文档 35号 §4.24 同源）；③§4.25 ICML 2026 P2E Calibrator（p→e 桥接 set-preserving，多回测证据合并）。§5.2 Phase 2 增 P2E、Phase 3 增 DMM+Lévy+Comparative。同步 00_index v1.5.0→v1.6.0 |
| 2026-08-10 | 1.7.0 | §4.26 VaR/ES Forecast Combination via MCS 新增 + §5.2 Phase 2 增 MCS + §8.2 新增"预报组合"分类 + frontmatter v1.7.0 | §3.1 conservative_max 的"选项之外更好算法"：arXiv:2406.06235v2 Amendola et al.（MCS + SSM 加权组合，Fissler-Ziegel 联合损失）+ arXiv:2508.16919v2 Taylor & Wang（90 法大池，6 法多样性小池+性能加权最优）。max 是 MCS 退化特例（2 法 {0,1} 赢者通吃）；Phase 1 轻量提取：分叉度 divergence=\|VaR_param-VaR_hist\|/VaR_95 持续 >20% 标记 MODEL_DIVERGENCE_HIGH；Phase 2 ≥4 法候选池后 MCS 替代 max，method 扩展 conservative_max\|mcs_combination\|performance_weighted。同步 00_index v1.6.0→v1.7.0 |
| 2026-08-10 | 1.8.0 | §4.27 Information-Geometric Bayesian 风险监控新增（arXiv:2608.01294）+ frontmatter v1.8.0 | 全网搜 2026-08 交叉验证 15 篇候选仅本篇未收录：Quirini 信息几何贝叶斯风险监控（Fisher 度量/测地距离 regime 检测/曲率风险集中）。关系：§3.11 校准第三触发 + §3.6 流形空间补充 + 与 10号 regime 检测正交。A 股适用性中低。Phase 4+ 远期（与 Mamba/SSM 同类过度工程）；Phase 1-2 轻量提取：对称 KL 散度漂移 + 偏度/峰度 SHAPE_DRIFT（<30 行）。同步 54号 v1.14.0 §3.14 MCR/CCR 风险分解（与 36号正交：36号管"组合风险多少"54号管"谁贡献了风险"） |
| 2026-08-10 | 1.9.0 | §5.2 演进路径与 §4.1-§4.27 全量对齐——11 项远期登记缺口补全 + 六类族重组 + 5 项正交定位澄清 | §5.2 此前仅列代表性方法，§4.8/§4.11-§4.14/§4.16-§4.20/§4.27 共 11 项未体现；按"风险度量族/回测族/conformal 族/深度学习族/半参数族/审计族"六类重组 Phase 2/3/4+ 路径，每项 §4.x 可追溯到 Phase；新增"不在路径"小节澄清 5 项（§4.5 Phase 4+ / §4.6 regime 检测 / §4.9 组合配置层 / §4.15 理论界证明 / §4.21 RL alpha 层）。文档结构一致性修复非施工算法缺失 |
| 2026-08-10 | 1.10.0 | §4.21 论文细节补全（6 协同机制+Bellman 残差 -85%+OOS Sharpe 0.9281+§4.27 关系+Phase 4 对齐）+ §4.28 Geodesic Execution Slippage 新增 + frontmatter v1.10.0 | ① arXiv:2608.04305v1（ICAIF '26）与既有 §4.21 同一论文，就地补全：RaQL 双时间尺度、保留原 CVaR 估计器与 Bellman 不动点仅重设计训练、6 协同机制、MeanBEQ 1.2202→0.1854/MeanBEV 1.1624→0.0535、OOS Sharpe 0.9281 maxDD 6.46%、Phase 3+→Phase 4 对齐；② Entropy 2026 28(6) 705 / arXiv:2605.0757 全新登记 §4.28：执行滑点=MS-GARCH Fisher 流形测地弧长+曲率-TDA 拓扑告警，5 加密市场 2,253 日 MCS 唯一保留，4 次危机中位提前 2 天告警（服务 35号回撤 Protocol 早期预警），Phase 5+ 远期。§4.1-§4.28 共 28 节远期登记闭合 |
| 2026-08-12 | 1.10.1 | 作战地图全覆盖补丁——BM-RC-04-C / BM-RC-07-A | ① §3.20 新增盘中因子暴露与相关性矩阵（BM-RC-04-C，production 补强）——firm 层暴露矩阵+相关性矩阵（CTR-P1-008）盘中定时+§3.12 事件联动，复用 MOD-RK-16 不新建模块，FACTOR_EXPOSURE 限额→BM-RC-04-D 告警链，降级跳过检查；与 25号 §3.7#8 策略级 HoldingDriftMonitor 层级分工，监控层相关性矩阵与 30号 §3.1 决策层协方差边界显式标注；② §3.1 补 BM-RC-07-A 口径对齐——VaR 演进口径以本文 FHS/QbSD/CRC 路线为准（G17 权威真源），BM"三阶段演进"缺中间层留 BM 维护批次修订，登记 §6 待裁定；frontmatter date 2026-08-10→2026-08-12 |
| 2026-08-12 | 1.10.2 | 作战地图环节映射补强——锚定 BM-RC-04-A、BM-RC-06-B、BM-RC-07 | §3.3/§3.12 末尾补映射块，环节级可追溯 |
| 2026-08-14 | 1.10.3 | 压缩精简：已施工内容折叠，零信息丢失审查通过（AI-DOCS-001） | 已施工内容折叠为"✅ 已施工（2 轮 27 测试全绿）+ 接口级摘要"，删除施工过程/调试记录/重复散文；VaR/ES 公式、配置参数、四级阈值、FHS/QbSD/Vol-Targeting 远期规约、§6 待裁定、§7 待定问题、35号契约、BM 锚点、全部数值参数零丢失 |
| 2026-08-15 | 1.10.4 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-05） | §3.14 blackswan_active 来源链相邻两处重复合并为一处（定义点 §3.5.2）；全篇扫描无其他可压缩点——VaR 2/4/6%+CVaR 10% 五级、POT 0.90/0.2/0.5/3.0、Basel 交通灯 16/17-20/21、REBUILD 静态 3%/5%/0.7、var_breach ×0.8/×0.9、GREM 四级、盘中 7 触发+冷却 5 分钟+日限 6 次、§6 待裁定/BM 锚点/35号契约/链接逐项零丢失 |
| 2026-08-17 | 1.11.1 | RiskOrchestrator 命名对账（AI-GOVB-001 #106）：§3.10 执行者状态标注/组件状态表/「production 口径澄清」三处同步 RWIRE-001 完工现实——编排层已建（落地名 RiskLayerOrchestrator，MOD-L06-001，盘中编排已接线），§3.10 校准动作调用点未接入仍=设计契约 | 仅命名/状态对账，零语义变更；「禁止按可执行语气直读」标注保留 |
| 2026-08-18 | 1.11.2 | §3.1 历史模拟法 VaR 分位数口径统一 `method='lower'`（AI-R5 审查批，F1 裁定延伸） | v1.11.0 F1 裁定只统一 ES 侧，VaR 侧遗留线性插值致同模块双口径（es_var_ratio 分子分母不同口径、5 级分级对插值虚拟值敏感）；统一后 ES≥VaR 不变量同口径下更严格成立；tail_risk_monitor.compute_var 同步落码 |
