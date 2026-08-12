---
ttl: permanent
doc_type: architecture_view
title: VaR/ES 与波动率监控
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.11.0"
date: 2026-08-12
topic: var_es_monitoring
scope: 07_trading_decision_architecture
---

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
| 状态 | ✅ 已定稿 v1.11.0（框架 §2.5.4 + 代码已有实现 + 触发机制裁决 + 4 法回测 MVP 已施工 + 校准/重构/恢复子流程 + 盘中重算 + clean/dirty P&L 区分 + BlackSwanSignal API 对接 + VaR breach 状态机 + FHS/QbSD/Vol-Targeting 施工规约 + 跨文档流程交接链闭合（E1-E3）+ 2026-08 最新研究远期登记 28 节 + §4.21 论文细节补全 + §4.28 Geodesic Execution Slippage + §5.2 演进路径与 §4.x 全量对齐 + **v1.11.0 基础设施盘点与代码实测校正**：§3.20 已施工设施盘点（5 组件+4 测试+注册表+11 项设计态伪代码清单）+ §3.11 daily_auditor v0.2.0→v0.1.0 校正（run_var_backtest 等设计态）+ §3.5 双注解（30号 §2.5.4 相对触发替代裁决 + §2.5.6 监控层定位）+ §3.9 13→15 法框架（补登 #14 Bivariate OP + 新增 #15 Multinomial）+ §3.9.3 监管更新（Fed 2026-03 取消 dual stack → SA as cap）+ §3.16 QbSD 来源（arXiv:2603.02357）+ §6 待裁定 3 项新增 + §6.1 跨文档同步登记 5 项） |

## 2. 背景

### 2.1 项目处境

个人 + 100% AI 开发的 A 股量化交易系统。VaR/ES 监控是风险控制三件套（回撤 Protocol / VaR-ES / 流动性危机）之一，定位为组合级风险度量和触发信号源。

### 2.2 核心问题

1. **VaR_95 怎么算**：参数法假设正态分布（快但尾部低估）vs 历史模拟法（无分布假设但需样本）——如何取？
2. **ES_95 怎么算**：ES 不可独立 elicitable，需要 VaR + 尾部条件期望——如何与 VaR 联动？
3. **入场基准怎么定**：VaR/ES 是时变的，"VaR > 1.2×入场 VaR" 中的 "入场 VaR" 锚定哪个时点？
4. **触发动作怎么执行**：VaR breach → 减仓比例 → 谁执行、怎么执行？
5. **30 日波动率调整怎么算**："每增 10% → 仓位减 20%" 中的 "增 10%" 相对什么基准？
6. **数据窗口多长**：太短不稳定，太长含旧 regime——A 股市场成熟度下的合理窗口？
7. **与回撤 Protocol 怎么协同**：VaR breach 和回撤 breach 是两个独立信号源，如何避免冲突？

### 2.3 约束条件

- **A 股 T+1**：当日买入次日才能卖出，VaR breach 减仓不能立即执行
- **涨跌停**：极端行情下无法交易，VaR breach 减仓可能无法执行
- **个人系统**：算力有限，不能跑蒙特卡洛 GPU 模拟；可解释性优先
- **风险优先原则**：风险相关模块先于策略模块施工至 production

## 3. 决策

### §3.1 VaR_95 计算（参数法 + 历史模拟法，取 max）

**决策**：Phase 1 实现两种方法并发计算，取 `max(parametric, historical)` 作为保守估计（conservative_max）。

**源码**：`src/zephyr/risk/core/var_calculator.py` v0.1.0（production, MOD-RK-05）

**算法**：

```python
# 参数法 (Parametric / Variance-Covariance)
# 假设收益正态分布
VaR_param = (z_α · σ - μ) · V · √T
# z_α = |ppf(1-c)|  如 0.95 → 1.6449
# σ = 样本标准差 (ddof=1)
# μ = 样本均值
# V = 组合价值 (NAV)
# T = 持有期天数 (默认 1)
# 下限 0：(z·σ - μ) 可能为负（高均值低波动）→ VaR 取 0

# 历史模拟法 (Historical Simulation)
# 经验分位数，无分布假设
VaR_hist = -quantile(r, 1-c) · V · √T
# 取收益序列下侧 (1-c) 经验分位数（负数=损失）
# VaR = -该分位数 · V（正数）
# 下限 0

# 保守取 max
VaR_95 = max(VaR_param, VaR_hist)
```

**选型理由**：
1. **取 max 的保守性**：参数法在正态假设下低估厚尾，历史模拟法在小样本下分位数不稳定——取 max 确保两者中更保守的胜出，符合风险优先原则
2. **参数法 <1ms, 历史模拟 ~5ms**：CPU 即可，无需 GPU
3. **每阶段独立可用**：Phase 1 完成即可上线风控（设计真源 §6 VaR 三阶段演进）
4. **Phase 2 远期**：蒙特卡洛法（GPU CuPy/PyTorch）+ MCS forecast combination 替代 max（→ §4.26，≥4 法候选池后 Fissler-Ziegel 联合损失 + SSM 加权组合）
5. **Phase 3 远期**：Basel III 三角验证 + 乘数因子 + 压力 VaR
6. **外部实证佐证**（v1.11.0 补）：Basel 交通灯回测实证中历史模拟 2 超限（GREEN 区）vs 参数法 6 超限（YELLOW 区）——正态假设低估厚尾被独立复现，印证取 max 的保守设计；arXiv:2505.05646 三法对比（HS/GARCH-N/GARCH-FHS）显示 HS 在 regime 突变期失准、FHS 最稳健——印证 §3.16 FHS 作为 Christoffersen 独立性失败首选替代的排序

**配置参数**（C 类可调）：

| 参数 | 默认值 | 说明 |
|---|---|---|
| confidence_level | 0.95 | 置信水平（95% VaR） |
| holding_period_days | 1 | 持有期（日 VaR） |
| method | conservative_max | 取两法 max |
| min_history | 30 | 最少样本数 |
| annualization_factor | 252 | A 股交易日年化因子 |

**最小样本约束**：`min_history=30`，不足时抛 `InsufficientVaRHistoryError`。A 股约 1.5 个月数据。

### §3.2 ES_95 计算（历史模拟 + POT 厚尾拟合）

**决策**：ES_95 双轨计算——历史模拟法为主，POT 模型厚尾拟合为辅（厚尾检测结果）。

**源码**：`src/zephyr/risk/core/tail_risk_monitor.py` v0.1.0（production, MOD-RK-15）

**算法**：

```python
# 方法 1: 历史模拟法 ES（主）
# ES = 尾部条件期望 = 超过 VaR 的损失的平均值
ES_hist = -mean(r[r <= quantile(r, 1-c)])
# 即最差 (1-c) 比例的收益的均值的负数

# 方法 2: POT 模型 (Peaks-Over-Threshold) 厚尾拟合（辅）
# 超过阈值 u 的超额值 X-u ~ GPD(ξ, β)
# ξ (shape): >0=厚尾(Fréchet), =0=指数, <0=有界
# β (scale): 尺度参数
# tail_index = 1/ξ（厚尾程度，越小越厚）

# POT 修正 ES（当 ξ > 0 厚尾时）：
ES_pot = VaR · (1 + (ξ - β/u) · (1-ξ)^(-1))
# POT 拟合步骤：
# 1. 取阈值 u = quantile(r, 0.90)（最差 10%）
# 2. 超额值 x_i = r_i - u (r_i < u, 即损失侧)
# 3. MLE 拟合 GPD(ξ, β)
# 4. 若 ξ > heavy_tail_shape_threshold (0.2) → 厚尾告警

# 最终 ES_95 = ES_hist（主），POT 结果用于厚尾诊断和 FRTB 加价
```

**POT 阈值选择**：默认取 90% 分位数（最差 10% 拟合）。远期演进见 §3.3 EVT 阈值选择。

**ES ≥ VaR 不变式**：ES 是尾部期望 ≥ VaR 分位数，`tail_risk_monitor.py` 强制校验 `es_forecast >= var_forecast`。

**FRTB 尾部风险加价**：当 `shape > critical_shape_threshold (0.5)` 时，`frtb_surcharge = frtb_multiplier (3.0) × shape`，作为资本附加。

**POT 日常计算失败兜底**（v1.4.0 补——原仅 §3.10 校准阶段有 GPD 拟合失败回滚，日常计算路径无兜底）：
- **触发条件**：`tail_risk_monitor.assess()` 日常计算时 GPD 拟合失败（scipy.stats.genpareto.fit 不收敛 / 样本不足 / 分布异常）
- **兜底策略**：回退到纯历史模拟 ES（`ES_95 = ES_hist`），跳过 POT 修正，标记 `pot_fallback_historical=True` 记入日志
- **ES ≥ VaR 不变式仍强制校验**：即使 POT 失败，`es_forecast >= var_forecast` 不变式仍生效（历史模拟 ES 天然满足）
- **连续失败升级**：连续 5 日 POT 拟合失败 → 触发 §3.10 RECALIBRATE 动作 3（重校准 POT 阈值），尝试 `pot_threshold_quantile` 0.90→0.85 或→0.95
- **与 §3.3 Uehara 双门控的关系**：远期 Uehara 双门控拒绝外推时也走此兜底路径（拒绝 GPD 外推 → 回退历史模拟 ES）

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

**决策**：MVP 使用固定 90% 分位数作为 POT 阈值；远期演进 Uehara 双门控拒绝外推机制。

**当前实现**（MVP）：
- 阈值 u = `quantile(returns, pot_threshold_quantile)` 
- GPD 参数估计：scipy.stats.genpareto.fit（MLE）
- 无阈值稳定性检验——固定分位数简化实现

**远期演进：Uehara 2026-05 双门控 EVT 阈值选择**（arXiv:2605.27474）：
1. **参数稳定性门控**：扫描阈值分位数 0.85~0.95，绘制 ξ(u) 稳定性图，选取平台区
2. **GPD 拟合优度门控**：KS 检验 p ≥ 0.05
3. **双门控均通过** → 接受 GPD 外推；**任一不通过** → 拒绝外推，输出空集（A 股样本短时拒绝外推比强行出 GPD 尾更安全）

**远期演进：Belzile & Davison 2026-06 EVT 阈值选择程序系统综述**（arXiv:2606.28540）：
- 40+ 阈值选择程序全景比较
- 当 Uehara 双门控拒绝外推时的替代程序参考

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

> **与 30号 §2.5.4 相对触发的替代裁决**（v1.11.0 补——原 §7 ④ 直接映射未解释差异）：
> 30号 §2.5.4 框架定义**相对触发**（VaR > 1.2×入场 VaR → 减仓 20%；ES > 1.3×入场 ES → 再减仓 20%）。本节落地为**绝对阈值 5 级**（VaR 2%/4%/6% + CVaR 10%），替代理由：
> 1. **锚点稳定性**：多策略并发下各策略入场时点分散，"入场 VaR"锚点随换手漂移，相对阈值基准不稳定；绝对阈值无锚点依赖，口径统一
> 2. **可解释性优先**（§2.3）："VaR 4.5% → ORANGE 级"比"VaR 是 37 天前入场时的 1.23 倍"更易向业主解释与审计
> 3. **与回撤 Protocol 同构**：35号四级回撤也是绝对阈值（8/15/20/25%），绝对阈值体系使两风控轴的裁决逻辑同构，取最严（§3.8）时无量纲混淆
> 4. **相对恶化检测未丢失**：由 35号 §3.16 回撤归因的 `current_var vs entry_var`（ratio > 1.5 → 减仓）保留——相对触发从"实时节流器" relocated 为"归因诊断器"，1.2×/1.3× 阈值升格为 1.5×（更迟钝、防抖动）
>
> **与 30号 §2.5.6 定位裁定的一致性**（v1.11.0 补）：30号 §2.5.6 过度工程审查裁定——**VaR 5 级 + 7 黑天鹅 = 监控层（先全建+全 log，实盘 6-12 月后裁剪未触发项），活跃节流以 35号四级回撤为主节流轴，VaR 5 级为辅助参考**。本节 5 级分级的落地定位据此澄清：计算与告警全量保留（监控仪表盘价值），但作为自动节流触发器时是 35号四级回撤的**辅助轴**而非主轴——`drawdown_controller.evaluate()` 内回撤状态机与 VaR 5 级取最严（§3.8），确保主节流轴失效时 VaR 轴仍可独立兜底。

**源码**：`src/zephyr/position/core/drawdown_controller.py` v0.1.0（production, MOD-POS-008）

#### §3.5.1 5 级系统性风险（VaR/CVaR 驱动）

| 级别 | VaR 阈值 | CVaR 阈值 | 仓位上限 | 动作 |
|---|---|---|---|---|
| GREEN | < 2% | - | 1.0 | 正常 |
| YELLOW | 2%-4% | - | 0.5 | 新开仓减半 |
| ORANGE | 4%-6% | - | 0.7 | 禁止新开 + 减仓 30% |
| RED | > 6% | - | 0.5 | 减仓 50% + 只平不开 |
| BLACK | - | > 10% | 0.0 | 全部清仓 |

> CVaR = ES（Conditional VaR = Expected Shortfall），同一概念不同命名。

**配置参数**（DrawdownControllerConfig）：

| 参数 | 默认值 | 说明 |
|---|---|---|
| var_yellow | 0.02 | 黄级 VaR 阈值 |
| var_orange | 0.04 | 橙级 VaR 阈值 |
| var_red | 0.06 | 红级 VaR 阈值 |
| cvar_black | 0.10 | 黑级 CVaR 阈值 |

#### §3.5.2 BlackSwanSignal API（黑天鹅信号处理）

**源码契约**：`drawdown_controller.py` 定义 `BlackSwanSignal` 数据类和 `BlackSwanMode` 枚举。

```python
# BlackSwanMode 7 模式（drawdown_controller.py §14.3）
class BlackSwanMode(str, Enum):
    BS001_LIQUIDITY = "BS001_LIQUIDITY"       # 流动性蒸发
    BS002_CORRELATION = "BS002_CORRELATION"   # 相关性崩塌
    BS003_VOLATILITY = "BS003_VOLATILITY"     # 波动率爆发
    BS004_MARGIN = "BS004_MARGIN"             # 融资盘踩踏
    BS005_CONTAGION = "BS005_CONTAGION"       # 跨市场传导
    BS006_POLICY = "BS006_POLICY"             # 政策黑天鹅
    BS007_SYSTEMIC = "BS007_SYSTEMIC"         # 系统性风险（多模式同触发）

# BlackSwanSignal 数据类
@dataclass(frozen=True)
class BlackSwanSignal:
    active_modes: frozenset[BlackSwanMode]
    @property
    def has_black_swan(self) -> bool: ...
    @property
    def is_systemic(self) -> bool:
        # BS-007 显式触发 或 ≥2 模式同触发
        return BlackSwanMode.BS007_SYSTEMIC in self.active_modes or len(self.active_modes) >= 2
```

**事件 → BlackSwanMode 映射**（36号负责构造 BlackSwanSignal 传入 drawdown_controller）：

```python
EVENT_TO_BS_MODE = {
    "POLICY":           BlackSwanMode.BS006_POLICY,
    "LIMIT_TIDE":       BlackSwanMode.BS001_LIQUIDITY,
    "VOL_REGIME_SHIFT": BlackSwanMode.BS003_VOLATILITY,
    "CORR_BREAKDOWN":   BlackSwanMode.BS002_CORRELATION,
    "GAP":              BlackSwanMode.BS003_VOLATILITY,
    "TAIL_BREACH":      BlackSwanMode.BS007_SYSTEMIC,
    "CONTAGION":        BlackSwanMode.BS005_CONTAGION,
}

def build_black_swan_signal(events: list[BlackSwanEvent]) -> BlackSwanSignal:
    """从黑天鹅事件列表构造 BlackSwanSignal。"""
    active_modes = set()
    for event in events:
        bs_mode = EVENT_TO_BS_MODE.get(event.type)
        if bs_mode is not None:
            active_modes.add(bs_mode)
    return BlackSwanSignal(active_modes=frozenset(active_modes))
```

**blackswan_active 来源链**：`BlackSwanReport.blackswan_active = len(active_modes) > 0`，供 35号 §3.13 `intraday_risk_loop` 状态机消费。

**BS-007 → Kill Switch 建议**（非直接触发）：`drawdown_controller` 对 BS-007 产出 `kill_switch_advised=True`，委托 `stop_loss` 执行 Kill Switch，本模块不直接触发。

#### §3.5.3 VaR floor 设定警示（2026-08 理论背书）

**arXiv:2608.05623 Li/Lyu/Wei 2026-08-06**：高 VaR floor 诱发 gambling-for-resurrection（赌博回本）行为，低 floor 具防御性。

**对本项目的启示**：
- 本项目 5 级阈值采用**渐进式减仓**（YELLOW 0.5 → ORANGE 0.7 → RED 0.5 → BLACK 0.0），而非硬性单一 floor
- 渐进式设计天然避免"高 floor 诱发赌博"的理论风险
- 与 35号 §4.12 拒绝"回撤进 RiskSignal"的设计决策交叉印证——保守低地板阈值优于激进高地板

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

# 波动率调整系数
# z > 0 → 波动率升高 → 减仓
# 每增 10%（vol_30d / vol_60d_mean - 1 > 0.10）→ 仓位减 20%
vol_ratio = vol_30d / vol_60d_mean if vol_60d_mean > 0 else 1.0
if vol_ratio > 1.10:
    vol_adjustment = max(0.0, 1.0 - 0.20 * ((vol_ratio - 1.0) / 0.10))
else:
    vol_adjustment = 1.0

# 最终仓位上限 = drawdown_controller.position_cap × vol_adjustment
```

**顺周期性风险**：波动率飙升时减仓 → 可能加剧卖压 → 进一步推高波动率。缓解措施：
1. 减仓比例有下限（不低于 BLACK 级 0.0）
2. 与 35号回撤 Protocol 协同，避免双重减仓叠加（取最严而非累乘）
3. 远期演进：Soloviov 2026-07 vol-targeting 受控实证（GARCH vs EWMA 统计不可区分 DM p=0.57，验证当前 30 日滚动 vol 替代 GARCH 的合理性 + vol-targeting 核心价值是 MaxDD 控制非 Sharpe 提升）

### §3.7 数据窗口

**决策**：

| 用途 | 窗口 | 理由 |
|---|---|---|
| VaR 历史模拟 | 60 交易日 | min_history=30（下限）+ 60 日平衡稳定性与时效性 |
| ES 历史模拟 | 60 交易日 | 与 VaR 对齐 |
| POT 拟合 | 60 交易日 | 最差 10% ≈ 6 个样本，GPD 拟合最低要求 |
| 30 日波动率 | 30 交易日 | 框架要求 |
| 60 日均值基准 | 60 交易日 | z-score 分母 |
| 回测验证 | ≥250 交易日 | Basel 交通灯 250 天标准 |

**A 股特殊性**：A 股年交易日 ~244，250 天约 1 年。回测窗口不足 250 天时按比例缩放（var_backtester.py `_traffic_light` 实现）。

### §3.8 与回撤 Protocol 协同

**协同架构**：

```
VaR/ES 监控 (36号)                回撤 Protocol (35号)
┌─────────────────┐               ┌─────────────────────┐
│ VaRCalculator   │──VaR_95──────→│ drawdown_controller  │
│ TailRiskMonitor │──ES_95/CVaR──→│   _evaluate_risk_   │
│                 │               │   level()            │
│ BlackSwanSignal │──BS modes────→│   _evaluate_black_  │
│                 │               │   swan()             │
└─────────────────┘               └─────────────────────┘
                                          │
                                          ▼
                                  DrawdownResponse
                                  (position_cap, reduce_ratio,
                                   kill_switch_advised)
```

**取最严原则**：`drawdown_controller.evaluate()` 对系统性风险级别、黑天鹅仓位上限、Kill Switch 建议三者取 `min(caps)` —— 最严的仓位上限胜出，不累乘。

**正交性**：VaR/ES 是组合风险度量（市场级），回撤是账户级净值回撤（账户级），两者正交。VaR breach 可能在回撤未触发时先行告警（如波动率飙升但净值未跌），回撤 breach 可能在 VaR 未触发时先行告警（如缓慢阴跌）。

**35号跨文档契约**（entry VaR 持久化）：
- 36号 §3.1/§3.2 计算 entry_var/entry_es → 35号 §3.11 持久化
- 35号 §3.16 回撤归因消费 entry_var 判断风险恶化（current_var vs entry_var）

### §3.9 回测验证（15 法框架，MVP 4 法已施工）

**决策**：15 法回测框架，MVP 4 法已施工至 production。

**源码**：`src/zephyr/risk/core/var_backtester.py` v0.1.0（evolving, MOD-RK-05B）

#### §3.9.1 MVP 4 法（已施工）

| # | 方法 | 检验目标 | 统计量 | 分布 | 源码 |
|---|---|---|---|---|---|
| 1 | Kupiec POF | 覆盖率（超限频率对不对） | LR_UC = -2ln[L(α)/L(p̂)] | χ²(1) | `kupiec_pof()` |
| 2 | Christoffersen | 独立性 + 条件覆盖率 | LR_cc = LR_UC + LR_ind | χ²(2) | `christoffersen()` |
| 3 | Acerbi-Szekely Z2 | ES 直接回测（超限日损失幅度） | Z2 = (1/N)Σ R_t/ES_t · 1{breach} | E[Z2]=-1 | `acerbi_szekely_z2()` |
| 4 | E-backtesting | 在线累积（anytime-valid） | e_t = Π(1+λ·b_s) | e > 1/α 拒绝 | `e_backtesting()` |

**Christoffersen LR_ind/LR_cc 区分**：

```python
# christoffersen() 返回 ChristoffersenResult
@dataclass
class ChristoffersenResult:
    lr_uc: float   # 覆盖率分量（= Kupiec LR_UC）
    lr_ind: float  # 独立性分量 χ²(1)
    lr_cc: float   # 条件覆盖率 = LR_UC + LR_ind ~ χ²(2)
    p_value: float # 整体 p 值
    reject: bool
    n_00: int  # 未超限→未超限
    n_01: int  # 未超限→超限
    n_10: int  # 超限→未超限
    n_11: int  # 超限→超限（聚集）

# 独立性失败分支处理：
# 当 christoffersen_ind_p < 0.05 且 kupiec_p >= 0.05 时
# → 覆盖率正确但超限聚集（独立性失败）
# → action = "RECALIBRATE"，优先选 FHS（Filtered Historical Simulation）
```

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

#### §3.9.2 远期 11 法（未施工）

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
| 14 | Bivariate Orthogonal Polynomials ES 回测 | SSC 2026-06 Lu/Sullivan/Hurlin（§4.11） | duration × severity 联合，model-free Wald test；v1.11.0 补登（§4.11 已承诺入表但遗漏） |
| 15 | Multinomial VaR Backtests | arXiv:1611.04851 Kratz/Lok/McNeil | 多水平 VaR 超限联合检验（N≥4 检验力显著强于二项 Kupiec），ES 隐含回测；Pearson/Nass/LRT 卡方实现简单，适合个人系统；v1.11.0 新增 |

#### §3.9.3 2026-08 监管认知更新（v1.11.0 修订——Fed 2026-03 修订提案推翻 dual stack）

- **CP9/26 PRA IMA（2026-06-19 咨询）**：ES 97.5% IMA 基准不变；go-live 2028-01-01（比 Basel 3.1 整体晚一年）；PLAT 监控期延长至 3 年（过渡期内 PLAT 失败不强制转 ASA）；RFET 阈值放宽（illiquid 风险因子 24→16 可验证报价）；新增 NMRF 中间类别（Type 1 定性通过/定量失败 → 部分留 ES 内）
- **US Basel III Endgame 修订提案（Fed/OCC/FDIC 2026-03-19，v1.11.0 更新）**：**取消 2023 版 "dual stack"（SA 并行 IMA）**，改为 **SA 作为 IMA 资本上限**（SA as cap，非并行计算）——v1.10.0 及之前本节"SA 并行 IMA→双轨映射"表述已过时；PLAT 简化（移除 Spearman 相关，仅留 KS 检验且 3 年过渡期非约束）；NMRF 重定标（100 观测→24 观测/年 liquid、16 观测其他；NMRF 拆 Type A 轻资本 / Type B 原 SES）；交通灯三区国际标尺不变
- **EU**：CRR III 内 FRTB 推迟至 2027-01，另咨询临时乘数（最长 3 年中性化资本影响）——全球三区监管时间表分化（US 2027 / EU 2027 / UK IMA 2028）
- **对本项目的意义**：监管框架适用银行业，个人系统无合规义务；登记价值在于——① Basel 交通灯三区（§3.9.1）仍是国际标尺未变；② PLAT 收敛到 **KS 单一度量**与 §3.3 Uehara 双门控的 GPD 拟合优度 KS 检验（p≥0.05）同族，监管与工程实践交叉印证；③ "SA as cap" 思路（简单法作为复杂法上限）与 §3.1 conservative_max（简单历史模拟作为参数法保守上界）设计哲学同构

### §3.10 校准/重构/恢复子流程

**决策**：三档响应——PASS / RECALIBRATE / REBUILD。

```
回测结果 → 综合定级
├── PASS:        Basel Green + Kupiec p≥0.05 + Christoffersen p≥0.05 + Z2 不拒绝 + E-backtesting green/yellow
├── RECALIBRATE: Basel Yellow + Kupiec reject + Christoffersen 独立性失败 + E-backtesting red
└── REBUILD:     Basel Red + overall_reject + E-backtesting black
```

**RECALIBRATE 动作**（v1.1.0 补 D7——原仅列动作清单无执行者/参数/回滚）：

| # | 动作 | 执行者 | 具体参数 | 回滚机制 |
|---|---|---|---|---|
| 1 | 扩大数据窗口 | RiskOrchestrator → var_calculator.update_config() | `min_history` 30→60，`window` 60→120 交易日 | 次日回测仍 RECALIBRATE → 继续扩大至 250；连续 3 日 REBUILD → 回滚至 60 |
| 2 | 切换 VaR 方法 | RiskOrchestrator → var_calculator.update_config() | `method` conservative_max → historical（参数法不稳定时）；或 → parametric（历史模拟小样本不稳定时） | 切换后次日回测 PASS → 保留；RECALIBRATE → 切回原方法 + 标记方法切换失败 |
| 3 | 重校准 POT 阈值 | RiskOrchestrator → tail_risk_monitor.update_config() | `pot_threshold_quantile` 0.90→0.85（更厚尾）或 →0.95（更保守） | GPD 拟合失败（KS p<0.05）→ 回滚至 0.90 + 跳过 POT 修正 |
| 4 | 切换到 FHS | RiskOrchestrator → fhs_engine.enable() | GARCH(1,1) 拟合 + 残差重采样（§3.16） | FHS 拟合失败（GARCH 不收敛）→ 回退 historical + 标记 FHS 不可用 |

**触发条件 → 动作映射**（v1.1.0 补——原"考虑 FHS"模糊，现明确何时切换）：

| 回测失败信号 | 优先动作 | 理由 |
|---|---|---|
| Kupiec reject（覆盖率失败） | 动作 1（扩窗口）+ 动作 2（切方法） | 覆盖率失败 = 样本不足或分布假设错 |
| Christoffersen LR_ind reject（独立性失败） | 动作 4（切 FHS） | 独立性失败 = 超限聚集 → 需 GARCH 残差重采样破自相关 |
| Z2 reject（ES 幅度失败） | 动作 3（重校准 POT） | ES 幅度失败 = 尾部拟合不准 |
| E-backtesting red（anytime-valid 累积证据） | 动作 1 + 动作 2 + 动作 3（组合） | 累积证据 = 多重校准问题 |

**REBUILD 动作**（v1.1.0 补——原"回退到保守静态映射"未定义具体映射）：

| # | 动作 | 执行者 | 具体参数 |
|---|---|---|---|
| 1 | 标记模型不可用 | RiskOrchestrator → state_store.set_var_model_status("UNAVAILABLE") | 持久化标记，盘前初始化读取 |
| 2 | 回退到保守静态映射 | RiskOrchestrator → drawdown_controller.force_static_mode() | 静态映射：VaR 固定 3%（ORANGE 级），CVaR 固定 5%，position_cap 固定 0.7——不再用 var_calculator 动态计算 |
| 3 | 人工审查 | daily_auditor.log_rebuild_event() + alert(REBUILD) | 通知业主审查模型，需人工解除 UNAVAILABLE 标记 |
| 4 | 考虑 Phase 2 蒙特卡洛 | 远期（不在 REBUILD 自动流程内） | 待 Phase 2 GPU 蒙特卡洛落地后作为 REBUILD 的可选升级路径 |

**REBUILD → 恢复流程**（v1.1.0 补——原无恢复路径）：
1. 业主人工审查模型 + 修复根因
2. 业主解除 UNAVAILABLE 标记（需 ResetConfirmation，对齐 35号 §3.14 人工复位机制）
3. RiskOrchestrator 重新启用 var_calculator 动态计算
4. 次日回测验证 → PASS 才完全恢复；RECALIBRATE/REBUILD 则继续静态映射

> **跨文档契约**（35号 §3.15/§3.18）：REBUILD 动作 2 的 force_static_mode() 产出的静态 position_cap = 0.7，需喂入 35号 §3.10 daily_risk_loop 的 drawdown_controller.evaluate()，作为 C 层 VaR/CVaR 约束的替代。35号 §3.18 盘后持久化需记录 var_model_status，供次日 §3.15 盘前初始化加载。

**RECALIBRATE/REBUILD 审计日志调用时机**（v1.1.0 补 D1——原 log_recalibration 无调用时机说明）：
- **log_recalibration(action="RECALIBRATE", reason=...)**：RiskOrchestrator 执行 RECALIBRATE 动作 1-4 任一后立即调用
- **log_recalibration(action="REBUILD", reason=...)**：RiskOrchestrator 执行 REBUILD 动作 1-2 后立即调用
- **log_recalibration(action="RECOVERED_FROM_REBUILD", reason=...)**：业主解除 UNAVAILABLE 标记后调用

**回测样本不足处理**（v1.4.0 补——原完全未定义冷启动期回测策略）：

| 样本量 n（交易日） | 处理策略 | 综合定级 | 理由 |
|---|---|---|---|
| n < 30 | 跳过回测，不参与综合定级 | 强制 PASS（标记 `INSUFFICIENT_SAMPLE_SKIP`） | min_history=30 下限，VaR 本身已不可靠，回测无统计意义 |
| 30 ≤ n < 60 | 执行回测但标记 `LOW_POWER_WARNING` | 仅 E-backtesting（anytime-valid 小样本友好）参与定级，Kupiec/Christoffersen/Z2 标记 `low_power` 不参与 reject 判定 | 传统 4 法在小样本下检验力不足，假阳性高；E-backtesting 的 anytime-valid 性质对小样本更鲁棒 |
| 60 ≤ n < 250 | 正常执行 4 法回测，Basel 交通灯按比例缩放 | 全 4 法参与定级 | §3.7 数据窗口标准 |
| n ≥ 250 | 正常执行 4 法回测，Basel 交通灯不缩放 | 全 4 法参与定级 | Basel 250 天标准 |

**冷启动期（n < 60）特殊处理**：
- **VaR 计算**：§3.1 min_history=30 下限触发 `InsufficientVaRHistoryError` 时，降级为参数法 only（跳过历史模拟法，因 30 日分位数不稳定），取 `VaR_95 = VaR_param`（不取 max）
- **回测验证**：如上表，跳过传统 4 法，仅用 E-backtesting
- **仓位约束**：冷启动期 position_cap 额外折扣 0.8（与 §3.5 5 级风险乘性叠加），即 `effective_cap = risk_level_cap × 0.8`，对齐 35号 §3.15 nav_history < 30 时保守冷启动模式
- **解除条件**：n ≥ 60 后自动解除冷启动折扣，首次完整回测结果记入 daily_auditor 审计日志

### §3.11 回测验证端到端施工流程（daily_auditor 集成）

**源码**：`src/zephyr/risk/core/daily_auditor.py` v0.1.0（production, MOD-RK-20）+ `src/zephyr/risk/core/var_backtester.py` v0.1.0（evolving, MOD-RK-05B）

> **⚠️ 施工状态（v1.11.0 校正）**：`daily_auditor.py` 实际版本为 **v0.1.0**（PnL 对账 `reconcile_pnl` / 归因偏差 `detect_attribution_bias` / 合规检查 `run_compliance_check` / 日终 checklist / `audit` / `generate_risk_metrics_report`），**不含**本节伪代码的 `run_var_backtest()` / `log_entry_var()` / `log_baseline()` / `log_recalibration()` / `compute_clean_pnl()` / `compute_dirty_pnl()`——全 src 检索零命中，属**设计态待施工**。当前已施工的是 `var_backtester.py full_report()`（4 法 + Basel 交通灯，`overall_reject` 汇总），其 docstring 声明"供 daily_auditor 日终调用"但调用侧未落地。此前版本（v1.0.0-v1.10.0）本节声称 daily_auditor v0.2.0 已含上述方法，与实际代码不符，本次校正。

**端到端流程**（设计态编排伪代码，调用侧待施工）：

```python
# daily_auditor.py DailyAuditor.run_var_backtest()
def run_var_backtest(self, observations: list[BacktestObservation]) -> VarBacktestReport:
    bt = VarBacktester(confidence_level=0.95)
    report = bt.full_report(observations)  # 4 法 + Basel traffic light

    # 综合定级（§3.10）
    basel_zone = report["basel_traffic_light"]["zone"]  # green/yellow/red
    ebt_alert = report["e_backtesting"]["alert_level"]  # green/yellow/red/black

    # v1.4.0 补（一致性修复）：对齐 §3.10 综合定级矩阵——Christoffersen reject（含 LR_ind 独立性失败）也触发 RECALIBRATE。
    # 原伪代码遗漏 christoffersen reject，导致"覆盖率正确但超限聚集（独立性失败）"时误判 PASS。
    if basel_zone == "red" or report["overall_reject"] or ebt_alert == "black":
        action = "REBUILD"
    elif (basel_zone == "yellow" or report["kupiec_pof"]["reject"]
          or report["christoffersen"]["reject"] or ebt_alert in ("yellow", "red")):
        action = "RECALIBRATE"
    else:
        action = "PASS"

    return VarBacktestReport(report=report, action=action, ...)
```

**回撤 Protocol 审计日志集成**（35号 §3.15/§3.17 跨文档契约）：

```python
# daily_auditor.py 三个审计日志方法
def log_entry_var(self, trade_date, entry_var: float) -> EntryVarLog:
    """记录入场 VaR 快照（35号 §3.11 持久化契约）。"""

def log_baseline(self, trade_date, var_95: float, es_95: float) -> BaselineLog:
    """记录当日 VaR/ES 基线（供次日回撤归因对比）。"""

def log_recalibration(self, trade_date, action: str, reason: str) -> RecalibrationLog:
    """记录模型校准/重构事件（RECALIBRATE/REBUILD 审计追溯）。"""
```

**代码差距列表**（v1.11.0 校正——统一迁移至 §3.20「已施工设施盘点」维护，此处保留摘要）：

| 组件 | 状态 | 说明 |
|---|---|---|
| var_calculator.py | ✅ production v0.1.0 | 参数法 + 历史模拟 + conservative_max |
| tail_risk_monitor.py | ✅ production v0.1.0 | ES + POT GPD + 跳跃检测 + FRTB |
| var_backtester.py | ✅ evolving v0.1.0 | MVP 4 法 + Basel traffic light + full_report |
| daily_auditor.py | ⚠️ production v0.1.0（部分） | PnL 对账/归因/合规/audit 已施工；`run_var_backtest` + 3 审计日志方法 + clean/dirty P&L **设计态待施工** |
| drawdown_controller.py | ⚠️ production v0.1.0（部分） | 5 级 + 7 黑天鹅 + BlackSwanSignal API 已施工；`var_breach_state` 参数 + `force_static_mode()` **设计态待施工** |
| backtest_store | ⚠️ 待施工 | 回测结果持久化层 |
| clean P&L 双轨记录 | ⚠️ 待施工 | clean/dirty P&L 区分 |

> 完整盘点（含设计态伪代码清单、注册表登记状态、测试配套）见 §3.20。

### §3.12 盘中重算触发

**决策**：7 条触发条件，盘中重算 VaR/ES 并**反馈给 35号 §3.13 盘中循环重新裁决**（v1.1.0 补 D2——原仅说"反馈回测"但未说如何反馈给 drawdown_controller 重新裁决）。

**触发条件**：

```python
def intraday_var_recalc_trigger(
    trade_date: date,
    market_open: datetime,
    market_close: datetime,
    current_nav: float,
    current_dd: float,
    current_exposure: float,
    universe_size: int,
) -> IntradayRecalcTrigger | None:
    """盘中 VaR/ES 重算触发判定。

    7 条触发条件（任一满足即重算）：
    1. 当前亏损 > 日内 VaR 的 50%（预警线）
    2. 当前回撤 > 8%（回撤 Protocol 一级阈值，与 35号 §3.1 协同）
    3. 涨跌停潮（与 G18 §3.5 涨跌停检测协同）
    4. 波动率 regime shift（30 分钟波动率 > 60 日均值 3σ）
    5. 相关性崩塌（BS-002 前兆）
    6. 跨市场传导（BS-005 前兆）
    7. 政策事件（BS-006）
    """
```

**盘中重算执行 + 结果反馈链**（v1.1.0 补 D2——原触发后无执行/反馈闭环）：

```python
def intraday_var_recalc(trade_date, current_nav, current_returns, trigger: IntradayRecalcTrigger):
    """盘中 VaR/ES 重算执行 + 结果反馈给 35号 §3.13 盘中循环。

    调用方：35号 §3.13 intraday_risk_loop 检测到触发条件后调用本函数。
    返回：IntradayVarResult(var_cvar, breach_state, significant_change)，供 35号 §3.13
          用新 var_cvar 重新调用 drawdown_controller.evaluate() 产出新 DrawdownResponse。

    跨文档契约（35号 §3.13 v1.30.6）：
    - 35号 §3.13 intraday_risk_loop 检测到"日内突破盘前 VaR"等 7 条触发条件
    - 调用本函数重算 VaR/ES
    - 本函数返回 IntradayVarResult
    - 35号 §3.13 用 IntradayVarResult.var_cvar 调用 drawdown_controller.evaluate() 重新裁决
    - 新 DrawdownResponse 覆盖盘前 response（取最严：position_cap 取 min，对齐 35号 §3.8 取最严原则）
    - v1.4.0 补（取最严维度澄清）："取最严" = position_cap 取 min（盘前 cap vs 盘中重算 cap），
      非 level 取 max——因 position_cap 是实际仓位约束，level 仅是分级标签。
      例：盘前 RED（cap=0.5）盘中重算后 YELLOW（cap=0.7）→ 取 min(0.5, 0.7)=0.5（盘前 RED 胜出）。
    """
    # 1. 重算 VaR/ES（用盘中最新收益序列）
    var_result = var_calculator.calculate(current_returns, portfolio_value=current_nav)
    tail = tail_risk_monitor.assess(current_returns, var_result.var)
    new_var_cvar = VarCvarMetrics(var_95=var_result.var, cvar_95=tail.es)

    # 2. 与盘前基线对比，判断是否显著变化
    premarket_baseline = state_store.load_premarket_baseline(trade_date)  # §3.18 盘后持久化
    significant_change = False
    if premarket_baseline is not None and premarket_baseline.var_95 > 0:
        var_change_ratio = abs(new_var_cvar.var_95 - premarket_baseline.var_95) / premarket_baseline.var_95
        if var_change_ratio > 0.20:  # 差异 > 20% → 显著变化
            significant_change = True
            daily_auditor.log_intraday_recalc_significant(
                trade_date, premarket_var=premarket_baseline.var_95,
                intraday_var=new_var_cvar.var_95, change_ratio=var_change_ratio,
            )

    # 3. 更新 VaR breach 状态机（§3.15）
    breach_state = var_breach_state_machine.transition(current_var=new_var_cvar.var_95)

    # 4. 记录盘中重算日志（供日终审计 + 回测分析）
    state_store.append_intraday_recalc_log(trade_date, IntradayRecalcEntry(
        timestamp=now, trigger=trigger.reason, var_95=new_var_cvar.var_95,
        cvar_95=new_var_cvar.cvar_95, significant=significant_change,
    ))

    return IntradayVarResult(
        var_cvar=new_var_cvar,
        breach_state=breach_state,
        significant_change=significant_change,
        # 35号 §3.13 用此返回值重新裁决：
        # new_response = drawdown_controller.evaluate(
        #     drawdown_info=dd_info, var_cvar=result.var_cvar,
        #     black_swan=..., strategy_pnls=...,
        #     var_breach_state=result.breach_state,  # §3.15 BREACHED 状态额外折扣
        # )
        # position_sizing_engine.apply_intraday_recalc(new_response)  # 取最严覆盖盘前
    )
```

**A 股收盘集合竞价特殊处理**（v1.1.0 补——原与 35号 §3.13 重复，现明确职责边界）：
- **本节职责**（36号 §3.12）：检测 14:55 后是否触发盘中重算 → 若触发，重算 VaR/ES → 返回 IntradayVarResult
- **35号 §3.13 职责**：接收 IntradayVarResult → 14:57 收盘集合竞价提交减仓单（基于新 DrawdownResponse 的 position_cap）
- 36号 §3.12 不直接提交减仓单（减仓是 35号 drawdown_controller 的职责），只产出重算结果

**多触发条件去重与防抖**（v1.4.0 补——原未定义多触发同时满足的优先级/去重/冷却期）：

1. **去重机制**：7 条触发条件任一满足即返回 trigger，`intraday_var_recalc_trigger()` 返回首个命中的 trigger（按优先级排序：政策事件 > 涨跌停潮 > 跨市场传导 > 相关性崩塌 > 波动率 regime shift > 回撤 > 亏损）。多个条件同时满足时**只重算一次**，trigger.reason 记录所有命中条件（逗号分隔）。
2. **冷却期（cooldown）**：重算后 5 分钟内不再重算（即使触发条件持续满足）。冷却期内触发的条件记入 `intraday_recalc_log` 的 `suppressed_triggers` 字段供审计。5 分钟后若触发条件仍满足，允许再次重算。
3. **频率上限**：单日最多重算 6 次（约每 40 分钟一次，覆盖 4 小时交易时段）。达到上限后当日不再重算，仅记录 `intraday_recalc_freq_cap_hit` 告警。
4. **触发条件 1 "当前亏损"口径澄清**（v1.4.0 补）：`current_loss = (opening_nav - current_nav) / opening_nav`，基于 clean NAV（不含未实现 MtM），与 §3.13 clean/dirty P&L 区分对齐——用 clean NAV 避免盘中 MtM 噪声导致频繁误触发。

**盘中重算结果反馈回测**（v1.1.0 补——原仅记录日志，现明确回测消费链）：
- 盘中重算的 VaR/ES 结果记录为 `intraday_recalc_log`（持久化到 state_store，§3.18 盘后持久化）
- 日终审计时 daily_auditor 对比盘前基线与盘中重算，若差异 > 20% → 标记 `intraday_recalc_significant`
- 回测验证（§3.9）消费 `intraday_recalc_log`：若盘中重算显著且次日回测 RECALIBRATE → 说明盘前 VaR 模型对盘中波动率 regime shift 响应不足 → 触发 §3.10 RECALIBRATE 动作 4（切 FHS）

### §3.13 clean/dirty P&L 区分

**决策**：双轨记录 clean P&L 和 dirty P&L，回测验证使用 clean P&L。

| 类型 | 定义 | 用途 |
|---|---|---|
| clean P&L | 已实现 + 未实现 P&L，**不含**交易成本、融资成本、分红 | 回测验证（模型纯度检验） |
| dirty P&L | 已实现 + 未实现 P&L，**含**交易成本、融资成本、分红 | 实际盈亏报告 |

**理由**：回测验证的是 VaR/ES 模型对市场风险的预测能力，交易成本等非市场因素会污染检验。clean P&L 剥离非市场因素，使回测结果反映模型纯度。

**产消链**（v1.1.0 补 D5——原无产出方/消费方/持久化说明）：

| 环节 | 责任方 | 具体实现 |
|---|---|---|
| **产出 clean P&L** | daily_auditor.compute_clean_pnl() | 从 broker 获取已实现 PnL + 收盘 Mark-to-Market 未实现 PnL → **减去**交易成本/融资成本/分红 → clean_pnl |
| **产出 dirty P&L** | daily_auditor.compute_dirty_pnl() | 从 broker 获取已实现 PnL + 收盘 Mark-to-Market 未实现 PnL → **包含**交易成本/融资成本/分红 → dirty_pnl |
| **持久化** | state_store.save_pnl_dual(trade_date, clean_pnl, dirty_pnl) | 双轨持久化，供回测 + 报告分别消费 |
| **消费 clean P&L** | var_backtester.full_report(observations) | BacktestObservation.pnl 字段须用 clean_pnl——v1.1.0 补：BacktestObservation 增加 `pnl_type: Literal["clean", "dirty"]` 字段，回测验证强制 `pnl_type="clean"` |
| **消费 dirty P&L** | daily_auditor.report() + 业主报告 | 实际盈亏报告用 dirty_pnl |

**BacktestObservation 契约**（v1.1.0 补——原 var_backtester 接收 BacktestObservation 但未约束 pnl 字段类型）：

```python
@dataclass
class BacktestObservation:
    """VaR 回测的单日观测点。

    pnl 字段必须是 clean P&L（不含交易成本/融资成本/分红），
    否则回测结果会被非市场因素污染（§3.13）。
    """
    trade_date: date
    var_forecast: float   # 当日盘前 VaR_95 预测值
    es_forecast: float    # 当日盘前 ES_95 预测值
    pnl: float            # 当日实际 P&L（须为 clean P&L）
    pnl_type: Literal["clean", "dirty"] = "clean"  # v1.1.0 补：默认 clean，回测验证强制 clean

    def __post_init__(self):
        if self.pnl_type != "clean":
            raise ValueError("VaR 回测必须使用 clean P&L（§3.13），"
                           "dirty P&L 会污染模型纯度检验")
```

**T+1 约束对 clean/dirty P&L 的影响**（v1.4.0 补——原未处理 A 股 T+1 制度对 P&L 双轨记录的影响）：

A 股 T+1 制度下，当日买入的头寸不可当日平仓，其 unrealized P&L 全部归入 dirty P&L（含未实现 MtM），clean P&L 仅包含可平仓头寸的已实现盈亏 + 可平仓头寸的未实现 MtM。

| P&L 组成 | T+1 可平仓头寸 | T+1 不可平仓头寸（当日新建） | 处理 |
|---|---|---|---|
| 已实现 P&L | ✅ 含 | ❌ 不含（不可平仓无已实现） | clean + dirty 均含可平仓已实现 |
| 未实现 MtM（可平仓） | ✅ 含 | — | clean + dirty 均含 |
| 未实现 MtM（不可平仓） | — | ⚠️ 仅 dirty 含 | clean **不含**，dirty 含 |
| 交易成本/融资成本/分红 | ❌ 不含（clean 定义） | ❌ 不含（clean 定义） | 仅 dirty 含 |

```python
def compute_clean_pnl_t1(positions, broker, trade_date):
    """T+1 约束下的 clean P&L 计算。

    clean P&L = 可平仓头寸的已实现 P&L + 可平仓头寸的未实现 MtM
    不含：当日新建头寸的未实现 MtM（T+1 不可平仓）+ 交易成本/融资成本/分红
    """
    realized = broker.get_realized_pnl(trade_date)  # 仅可平仓头寸的已实现
    # 仅计算 T-1 及之前建仓头寸的 MtM（T+1 可平仓）
    t1_tradeable_positions = [p for p in positions if p.entry_date < trade_date]
    unrealized_mtM_t1 = sum(broker.get_unrealized_mtM(p, trade_date)
                            for p in t1_tradeable_positions)
    clean_pnl = realized + unrealized_mtM_t1
    return clean_pnl

def compute_dirty_pnl_t1(positions, broker, trade_date):
    """T+1 约束下的 dirty P&L 计算。

    dirty P&L = 全部头寸的已实现 P&L + 全部头寸的未实现 MtM + 交易成本/融资成本/分红
    含：当日新建头寸的未实现 MtM（虽不可平仓但有 MtM 波动）
    """
    realized = broker.get_realized_pnl(trade_date)
    unrealized_mtM_all = sum(broker.get_unrealized_mtM(p, trade_date) for p in positions)
    costs = broker.get_total_costs(trade_date)  # 交易成本+融资成本+分红
    dirty_pnl = realized + unrealized_mtM_all + costs
    return dirty_pnl
```

**T+1 约束对回测验证的影响**：
- **clean P&L 仅含可平仓头寸**：回测验证（§3.9）用 clean P&L，检验的是 VaR/ES 模型对**可平仓风险**的预测能力——T+1 不可平仓头寸的 MtM 波动是"锁仓风险"而非"可交易风险"，不应纳入 VaR 回测
- **dirty P&L 含全部头寸**：实际盈亏报告用 dirty P&L，反映账户真实损益（含锁仓 MtM）
- **冷启动期特殊处理**：首次建仓日全部头寸为 T+1 不可平仓 → clean P&L = 0（无可平仓已实现+无可平仓 MtM）→ 当日不参与回测验证（§3.10 样本不足处理 n<30 强制 PASS）

### §3.14 黑天鹅信号处理（BlackSwanSignal API）

**决策**：36号负责从黑天鹅事件构造 `BlackSwanSignal`，传入 `drawdown_controller.evaluate()`。

**模块归属**（v1.1.0 补 D6——原 black_swan_detector 标注 D-RISK/D-SIGNAL 但项目模块清单无此模块）：

| 阶段 | black_swan_detector 实现 | 说明 |
|---|---|---|
| **MVP（当前）** | 36号 §3.5.2 EVENT_TO_BS_MODE 映射 + 37号流动性危机检测 + 55号系统监控 事件聚合 | 无独立 black_swan_detector 模块，由 RiskOrchestrator 聚合多源事件：①37号流动性危机（BS001_LIQUIDITY）②36号波动率 regime shift（BS003_VOLATILITY）③55号系统监控异常（BS004_MARGIN/BS007_SYSTEMIC）④外部政策事件输入（BS006_POLICY） |
| **远期（Phase 2）** | 独立 black_swan_detector 模块（D-RISK/D-SIGNAL） | 待 55号系统监控 + 37号流动性危机均 production 后，提取为独立模块 |

**MVP 事件源映射**（v1.1.0 补——原无具体事件源）：

| BlackSwanMode | MVP 事件源 | 检测方法 |
|---|---|---|
| BS001_LIQUIDITY | 37号 §3.5 涨跌停潮检测 + 成交量萎缩 | 涨跌停比例 > 阈值 OR 成交量 < 60 日均值 50% |
| BS002_CORRELATION | 36号 §3.12 盘中重算 触发条件 5 | 相关性矩阵均值骤降（30 分钟窗口 vs 60 日窗口） |
| BS003_VOLATILITY | 36号 §3.12 盘中重算 触发条件 4 | 30 分钟波动率 > 60 日均值 3σ |
| BS004_MARGIN | 55号系统监控 融资余额检测 | 融资余额骤降 > 5%（外部数据源） |
| BS005_CONTAGION | 36号 §3.12 盘中重算 触发条件 6 | 跨市场相关性突变（A股 vs 港股/美股隔夜） |
| BS006_POLICY | 外部政策事件输入（人工/新闻 API） | 业主手动标记 OR 新闻 API 关键词触发 |
| BS007_SYSTEMIC | ≥2 模式同触发 OR 显式标记 | BlackSwanSignal.is_systemic 自动判定 |

**数据流**：

```
MVP: RiskOrchestrator 聚合多源事件
    │ ①37号流动性危机 → BS001_LIQUIDITY
    │ ②36号波动率 regime shift → BS003_VOLATILITY
    │ ③55号系统监控异常 → BS004_MARGIN/BS007_SYSTEMIC
    │ ④外部政策事件 → BS006_POLICY
    ▼
events: list[BlackSwanEvent]  ← 7 类事件检测
    │
    ▼
build_black_swan_signal(events)  ← 36号 §3.5.2 映射
    │
    ▼
BlackSwanSignal(active_modes: frozenset[BlackSwanMode])
    │
    ▼
drawdown_controller.evaluate(drawdown_info, var_cvar, black_swan, strategy_pnls)
    │
    ▼
DrawdownResponse(kill_switch_advised=bool, position_cap=float, ...)
```

**BlackSwanReport 产出**：

```python
@dataclass
class BlackSwanReport:
    events: list[BlackSwanEvent]
    triggered_count: int
    blackswan_active: bool  # = len(active_modes) > 0，供 35号 §3.13 状态机消费
```

**blackswan_active 来源链**：
1. RiskOrchestrator 聚合多源事件（MVP）或 black_swan_detector 检测 7 类事件（远期）
2. 36号 `build_black_swan_signal()` 构造 `BlackSwanSignal`
3. `BlackSwanReport.blackswan_active = len(active_modes) > 0`
4. 35号 §3.13 `intraday_risk_loop` 状态机消费 `blackswan_active` 参数

### §3.15 VaR breach 恢复/复位状态机

**决策**：VaR breach 后的恢复采用 `consecutive_days_below_recovery` 条件判断。

```python
@dataclass
class VarBreachStateMachine:
    """VaR breach 状态机。

    状态：NORMAL → BREACHED → RECOVERY → NORMAL
    """
    state: str  # "NORMAL" / "BREACHED" / "RECOVERY"
    breach_date: date | None
    consecutive_days_below_recovery: int  # 连续低于恢复阈值的天数

    def transition(self, current_var: float, recovery_threshold: float) -> str:
        """
        recovery_threshold: 恢复阈值（如 breach 时 VaR 的 0.8 倍）

        NORMAL → BREACHED: VaR > breach_threshold
        BREACHED → RECOVERY: VaR < recovery_threshold（连续 N 日）
        RECOVERY → NORMAL: consecutive_days_below_recovery >= N（默认 3 日）
        RECOVERY → BREACHED: VaR 再次 > breach_threshold（复燃）
        """
        if self.state == "NORMAL":
            if current_var > self.breach_threshold:
                self.state = "BREACHED"
                self.breach_date = today
                self.consecutive_days_below_recovery = 0
        elif self.state == "BREACHED":
            if current_var < recovery_threshold:
                self.consecutive_days_below_recovery += 1
                if self.consecutive_days_below_recovery >= 3:
                    self.state = "RECOVERY"
            else:
                self.consecutive_days_below_recovery = 0  # 重置
        elif self.state == "RECOVERY":
            if current_var < recovery_threshold:
                self.consecutive_days_below_recovery += 1
                if self.consecutive_days_below_recovery >= 5:  # 恢复期更长
                    self.state = "NORMAL"
                    self.breach_date = None
            else:
                self.state = "BREACHED"  # 复燃
                self.consecutive_days_below_recovery = 0
        return self.state
```

**参数**：

| 参数 | 默认值 | 说明 |
|---|---|---|
| breach_threshold | var_yellow (0.02) | 进入 BREACHED 状态的 VaR 阈值 |
| recovery_threshold | breach_threshold × 0.8 | 进入 RECOVERY 状态的 VaR 阈值 |
| consecutive_days_below_recovery (BREACHED→RECOVERY) | 3 | 连续低于恢复阈值天数 |
| consecutive_days_below_recovery (RECOVERY→NORMAL) | 5 | 恢复期更长，避免反复 |

**跨重启持久化**（v1.1.0 补 D3——原状态机无持久化，重启后 state/breach_date/consecutive_days 丢失）：

```python
@dataclass
class VarBreachStateSnapshot:
    """VaR breach 状态机持久化快照（§3.18 盘后持久化 → §3.19 盘前加载）。"""
    state: str                              # "NORMAL" / "BREACHED" / "RECOVERY"
    breach_date: date | None                # 最近一次 breach 日期
    consecutive_days_below_recovery: int    # 连续低于恢复阈值天数
    last_transition: datetime               # 最近一次状态转换时间

# §3.18 盘后持久化（对齐 35号 §3.18）
def persist_var_breach_state(trade_date, state_machine: VarBreachStateMachine):
    snapshot = VarBreachStateSnapshot(
        state=state_machine.state,
        breach_date=state_machine.breach_date,
        consecutive_days_below_recovery=state_machine.consecutive_days_below_recovery,
        last_transition=state_machine.last_transition,
    )
    state_store.save_var_breach_state(trade_date, snapshot)

# §3.19 盘前加载（对齐 35号 §3.15）
def load_var_breach_state(trade_date) -> VarBreachStateMachine:
    snapshot = state_store.load_var_breach_state(trade_date)
    if snapshot is None:
        # 冷启动 → 默认 NORMAL（保守：不假设上次在 BREACHED）
        return VarBreachStateMachine(state="NORMAL", breach_date=None,
                                     consecutive_days_below_recovery=0)
    return VarBreachStateMachine(
        state=snapshot.state,
        breach_date=snapshot.breach_date,
        consecutive_days_below_recovery=snapshot.consecutive_days_below_recovery,
    )
```

**与 35号回撤状态机协同**（v1.1.0 补 D4——原两状态机无交互说明）：

36号 VarBreachStateMachine（NORMAL/BREACHED/RECOVERY）与 35号 DrawdownStateMachine（NORMAL/WARN/DANGER/CRISIS/KILL/RECOVERY）是**两个正交状态机**，通过 drawdown_controller.evaluate() 的 `var_breach_state` context 参数协同：

| VaR breach 状态 | 对 drawdown_controller 的影响 | 协同理由 |
|---|---|---|
| NORMAL | 无额外影响 | VaR 未 breach，回撤状态机独立运行 |
| BREACHED | position_cap 额外 ×0.8 折扣（如回撤状态机 WARN 80% → VaR BREACHED 后 80%×80%=64%） | VaR breach = 组合风险恶化，即便回撤未触发也需额外保守 |
| RECOVERY | position_cap 额外 ×0.9 折扣（轻量折扣，恢复期但仍需谨慎） | VaR RECOVERY = 风险缓解但未完全恢复，轻量折扣 |

```python
# drawdown_controller.evaluate() 增强（v1.1.0 补 D4——新增 var_breach_state 参数）
def evaluate(self, drawdown_info, var_cvar, strategy_pnls, black_swan,
             var_breach_state: str = "NORMAL"):  # 新增参数
    """综合裁决：回撤状态机 × VaR breach 状态机 取最严。

    var_breach_state 来自 36号 §3.15 VarBreachStateMachine.state，
    通过 position_cap 乘性折扣与回撤状态机的 position_cap 叠加。
    """
    # 1. 回撤状态机产出 base_position_cap（如 WARN → 0.8）
    base_cap = self._evaluate_risk_level(var_cvar, drawdown_info)
    # 2. VaR breach 状态机产出额外折扣
    var_breach_multiplier = {
        "NORMAL": 1.0,
        "BREACHED": 0.8,   # VaR breach → 额外 20% 折扣
        "RECOVERY": 0.9,   # VaR RECOVERY → 轻量 10% 折扣
    }.get(var_breach_state, 1.0)
    # 3. 取最严（乘性叠加，对齐 35号 §3.8 取最严原则）
    effective_cap = base_cap * var_breach_multiplier
    # v1.1.1 补（E3 澄清——双 RECOVERY 叠加场景）：
    #   当 35号 DrawdownStateMachine 处于 RECOVERY（base_cap = 0.25/0.5/0.75 阶梯）
    #   且 36号 VarBreachStateMachine 也处于 RECOVERY（multiplier = 0.9）时，
    #   effective_cap = base_cap × 0.9（如 0.25 × 0.9 = 0.225）——"双恢复期叠加折扣"。
    #   裁决：此叠加是 intended（风险优先原则——两状态机同时处于恢复期意味着账户回撤 +
    #   组合风险同时未恢复，双重保守合理）。但加入下限保护：effective_cap 不得低于
    #   Kill Switch 级（0.0）和 BLACK 级（0.0）——即 effective_cap = max(effective_cap, 0.0)。
    #   注：35号 RECOVERY 阶梯的 base_cap 已是硬上限（0.25/0.5/0.75/1.0），36号 var_breach_multiplier
    #   是额外折扣。两者乘性叠加后，RECOVERY 期实际仓位上限 = 阶梯值 × 0.9（如 step 0 = 22.5%）。
    #   这比"取最严 = min(阶梯值, 阶梯值×0.9) = 阶梯值×0.9"更严，符合风险优先原则。
    effective_cap = max(effective_cap, 0.0)  # 下限保护：不低于 Kill Switch 级
    # 4. 黑天鹅仓位上限（如有）取 min
    if black_swan.has_black_swan:
        bs_cap = self._evaluate_black_swan(black_swan)
        effective_cap = min(effective_cap, bs_cap)
    return DrawdownResponse(position_cap=effective_cap, ...)
```

> **两状态机正交性说明**：回撤状态机是**账户级净值回撤**驱动（已发生事实），VaR breach 状态机是**组合级风险度量**驱动（前瞻性风险）。两者可独立触发——VaR breach 可能在回撤未触发时先行告警（波动率飙升但净值未跌），回撤 breach 可能在 VaR 未触发时先行告警（缓慢阴跌）。乘性叠加确保两者任一触发即整体保守。
>
> **双 RECOVERY 叠加场景**（v1.1.1 补 E3 澄清）：35号 DrawdownStateMachine RECOVERY（净值回撤恢复期，阶梯 25%→50%→75%→100%）与 36号 VarBreachStateMachine RECOVERY（VaR breach 恢复期，连续 5 日低于恢复阈值）可能同时发生——账户回撤 + 组合风险同时未恢复。此时 effective_cap = 阶梯值 × 0.9（如 0.25 × 0.9 = 0.225），双重保守。裁决：此叠加合理（风险优先原则），但需监控"恢复期过长"——若两状态机同时处于 RECOVERY 超 20 交易日，daily_auditor 标记 `DUAL_RECOVERY_PROLONGED` 告警，提示人工审查策略是否需暂停（而非仅靠仓位折扣控制）。

**VaR BREACHED 状态作为 35号 §3.16 回撤归因维度**（v1.1.0 补——跨文档契约）：

35号 §3.16 回撤归因流程新增维度：若 36号 VarBreachStateMachine.state == "BREACHED"，则归因为 "RISK_DETERIORATION_VAR_BREACHED"——VaR 模型本身失效或波动率 regime shift 导致组合风险恶化。这与 35号 §3.16 现有的 entry_var vs current_var 风险恶化检测互补：
- entry_var vs current_var：**单次** VaR 恶化比例（ratio > 1.5 → 减仓）
- VarBreachStateMachine BREACHED：**持续** VaR 超阈值（连续 breach → 状态机升级 → 额外折扣）

两者乘性叠加：单次恶化触发减仓 + 持续 breach 触发额外折扣，双重保护。

### §3.16 FHS/QbSD/Vol-Targeting 施工规约

**Filtered Historical Simulation (FHS)**（远期 Phase 2）：
- GARCH(1,1) 拟合收益序列 → 标准化残差 → 重采样 → 乘以条件波动率预测
- 用途：Christoffersen 独立性失败时优先选 FHS
- 依赖：arch 库（GARCH 拟合）

**FHS 切换触发条件**（v1.1.0 补 D12——原"Christoffersen 独立性失败时优先选"无具体触发机制）：

```python
def should_switch_to_fhs(backtest_report: VarBacktestReport) -> bool:
    """判断是否应切换到 FHS（§3.10 RECALIBRATE 动作 4 的触发条件）。

    触发条件（任一满足即切换）：
    1. Christoffersen LR_ind reject（独立性失败，p < 0.05）——超限聚集，需 GARCH 残差重采样破自相关
    2. 连续 2 次回测 E-backtesting red（累积证据表明波动率有时变结构）
    3. 盘中重算显著（§3.12 intraday_recalc_significant）连续 3 日触发——盘前 VaR 对盘中 vol regime shift 响应不足
    """
    christoffersen_ind_fail = (
        backtest_report.report["christoffersen"]["lr_ind_p"] < 0.05
        and backtest_report.report["kupiec_pof"]["p_value"] >= 0.05  # 覆盖率正确但独立性失败
    )
    ebt_red_streak = (
        state_store.load_ebacktesting_alert_history(window=2) == ["red", "red"]
    )
    intraday_significant_streak = (
        state_store.load_intraday_recalc_significant_history(window=3) == [True, True, True]
    )
    return christoffersen_ind_fail or ebt_red_streak or intraday_significant_streak
```

**FHS 切换流程**（v1.1.0 补——对齐 §3.10 RECALIBRATE 动作 4）：
1. should_switch_to_fhs() 返回 True → RiskOrchestrator 调用 fhs_engine.enable()
2. fhs_engine 用 GARCH(1,1) 拟合过去 60 日收益序列 → 若不收敛（迭代超限/方差非正）→ 回退 historical + 标记 FHS 不可用
3. 收敛 → 标准化残差重采样 → 乘以条件波动率预测 → 产出 FHS VaR
4. 次日回测验证 FHS VaR → PASS 则保留；RECALIBRATE/REBUILD 则切回 historical + 标记 FHS 切换失败

**FHS 切换失败冷却期**（v1.4.0 补——原 FHS 切换失败后无冷却期，可能次日再次触发 should_switch_to_fhs() 反复抖动）：

```python
# FHS 切换失败后 10 交易日内不再尝试切换（冷却期）
FHS_COOLDOWN_DAYS = 10  # 冷却期：约 2 周，覆盖一个完整波动率周期

def should_switch_to_fhs(backtest_report, state_store) -> bool:
    # v1.4.0 补：冷却期检查——FHS 切换失败后 10 日内不再尝试
    last_fhs_failure = state_store.load_last_fhs_failure_date()
    if last_fhs_failure is not None:
        days_since_failure = (trade_date - last_fhs_failure).days
        if days_since_failure < FHS_COOLDOWN_DAYS:
            daily_auditor.log_fhs_cooldown_active(
                trade_date, days_since_failure, FHS_COOLDOWN_DAYS
            )
            return False  # 冷却期内不切换
    # ... 原有触发条件检查 ...
```

- **冷却期机制**：FHS 切换失败（步骤 2 GARCH 不收敛 OR 步骤 4 次日回测 RECALIBRATE/REBUILD）→ 记录 `last_fhs_failure_date` 到 state_store → 10 交易日内 should_switch_to_fhs() 直接返回 False
- **冷却期解除**：10 交易日后自动解除，允许再次尝试（若触发条件仍满足）
- **连续失败升级**：冷却期内累计 3 次 FHS 切换失败 → 标记 `FHS_PERMANENTLY_DISABLED`，不再尝试切换，仅用 historical 方法 + §3.10 RECALIBRATE 动作 1（扩窗口）/动作 2（切方法）替代
- **与 §3.10 的关系**：FHS 冷却期是 §3.10 RECALIBRATE 动作 4 的防抖机制，防止 Christoffersen 独立性失败反复触发 FHS 切换→失败→再触发的死循环

**Quantile-based Scale Dynamics (QbSD)**（远期 Phase 3）：

**来源**（v1.11.0 补）：arXiv:2603.02357 Liu & Luger 2026-03 "Quantile-based modeling of scale dynamics in financial returns for VaR and ES forecasting"——restricted quantile regression 建模条件尺度（两分位数差），分布自由、捕捉偏度/厚尾/杠杆效应，多国股指含 COVID 期间实证优于 GARCH 与联合 VaR-ES 条件分位数基准。

**算法概要**：分位数回归（quantile regression）捕捉不同置信水平下尾部的动态尺度变化——与 §3.1 参数法（假设正态分布，单一 σ 描述整个分布）不同，QbSD 对多个分位数（如 95%/99%/99.5%）分别建模，允许不同尾部有不同动态尺度。

**触发条件**（何时从 MVP 升级到 QbSD）：
1. §3.2 POT 拟合的 GPD shape 参数 ξ 在不同置信水平（90%/95%/99% 分位数阈值）下显著不一致（|ξ_90 - ξ_99| > 0.15）——说明尾部厚度非均匀，单一 σ 或单一 ξ 不足以描述
2. §3.9 回测第 3 法 Acerbi-Szekely Z2 在 95% 和 99% 置信水平下表现分化（一个 PASS 一个 reject）——说明不同尾部校准不一致
3. A 股极端行情（如涨跌停潮）下 99% VaR 回测连续 reject 但 95% VaR PASS——说明深尾部需要独立建模

**算法概要**：
```python
# QbSD 多分位数回归（远期 Phase 3）
# 对每个目标分位数 α ∈ {0.95, 0.99, 0.995} 独立拟合分位数回归模型
# VaR_α = quantile_regression(X_t, α)  # X_t = 特征向量（滞后收益/波动率/成交量等）
# ES_α = mean(returns[returns <= VaR_α])  # 尾部条件期望（与 §3.2 ES_hist 同理）

# 与 §3.1 参数法的关系：
# 参数法：VaR_95 = (z_0.95 · σ - μ) · V —— 正态假设，单一 σ
# QbSD：VaR_95 = QR(X_t, 0.95), VaR_99 = QR(X_t, 0.99) —— 无分布假设，各分位数独立
# QbSD 天然捕捉偏度/厚尾（不同分位数有不同动态），参数法因正态假设无法捕捉
```

**与 MVP 的关系**：
- **MVP（当前）**：§3.1 参数法 + 历史模拟取 max，假设正态分布（参数法）或经验分布（历史模拟），单一分布描述整个收益序列
- **远期 QbSD**：多分位数独立建模，允许不同尾部有不同动态尺度——精化非正态/非对称分布下的 VaR
- **关系**：QbSD 落地后作为 §3.1 的**增强层**（非替代）——当 QbSD 触发条件满足时，用 QbSD 多分位数 VaR 替代参数法 VaR 参与取 max；触发条件不满足时仍用 §3.1 参数法
- **依赖**：scikit-learn QuantileRegressor 或 statsmodels quantile_regression（CPU 即可，无需 GPU）
- **Phase 3 远期**：需特征工程（滞后收益/波动率/成交量等 X_t 构造）+ 回测验证 QbSD 优于参数法的 A 股实证

**Vol-Targeting**（远期 Phase 2）：
- BlackRock 比例控制 vol-targeting（31号已登记）
- 用途：连续闭环替代离散分档
- 2026-07 Soloviov 实证：GARCH vs EWMA 统计不可区分（DM p=0.57），验证当前 30 日滚动 vol 替代 GARCH 的合理性

**Vol-Targeting 与 §3.6 30 日波动率调整的关系**（v1.1.0 补——原未说明是替代还是叠加）：
- **MVP（当前）**：§3.6 30 日波动率 z-score 法是**离散分档**（每增 10% → 仓位减 20%），已施工
- **远期 Vol-Targeting**：是**连续闭环**替代——用 GARCH 预测目标波动率，连续调整仓位使实际波动率逼近目标
- **关系**：Vol-Targeting 落地后**替代** §3.6 离散分档（不叠加），但 §3.6 的 z-score 法作为 Vol-Targeting 失效时的回退方案保留
- **Soloviov 2026-07 实证支持**：GARCH vs EWMA 统计不可区分（DM p=0.57），说明 §3.6 的 30 日滚动 vol 已是 Vol-Targeting 的合理近似，远期升级收益有限——Vol-Targeting 优先级降为 P3

### §3.17 施工流程总览（5 流程闭环）

> **v1.1.0 新增 D8**：对齐 35号 §3.17 的 6 流程闭环总览，本节是 36号文档的施工流程时序图。

**5 流程闭环时序**（一个交易日的 VaR/ES 监控生命周期）：

```
┌─────────────────────────────────────────────────────────────────────┐
│  T-1 收盘后                                                          │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────────┐      │
│  │ §3.11 回测   │ →  │ §3.10 校准/   │ →  │ §3.18 盘后状态      │      │
│  │ 验证（4 法 + │    │ 重构/恢复     │    │ 持久化              │      │
│  │ Basel 交通灯）│    │ PASS/RECAL/  │    │ VarBreachState→     │      │
│  │              │    │ REBUILD      │    │ intraday_recalc_log→│      │
│  └─────────────┘    │ → 次日配置    │    │ clean/dirty P&L→    │      │
│                     └──────────────┘    │ var_model_status    │      │
│                                         └─────────┬──────────┘      │
│                                                   ↓ 持久化状态        │
└──────────────────────────────────────────────────┼──────────────────┘
                                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│  T 盘前                                                              │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ §3.19 盘前初始化                                              │   │
│  │ 加载 VarBreachStateMachine → 加载 entry_var → 加载             │   │
│  │ var_model_status（REBUILD 后是否 UNAVAILABLE）→ 基线校准       │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
│                             ↓                                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ §3.1/§3.2 盘前 VaR/ES 计算                                    │   │
│  │ var_calculator.calculate() → tail_risk_monitor.assess()       │   │
│  │ → VarBreachStateMachine.transition() → 产出 var_cvar +        │   │
│  │   breach_state → 喂入 35号 §3.10 drawdown_controller          │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
└─────────────────────────────┼────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│  T 盘中（9:30-15:00）                                                │
│  ┌─────────────────────────┐    ┌────────────────────────────┐      │
│  │ §3.12 盘中 VaR/ES 重算   │ ←→ │ 35号 §3.13 盘中实时风控循环  │      │
│  │ 7 条触发条件 → 重算 →     │    │ 30 秒轮询：检测触发条件 →    │      │
│  │ IntradayVarResult →      │    │ 调用 §3.12 重算 → 用新       │      │
│  │ 反馈给 35号 §3.13 重新裁决 │    │ var_cvar 重新调用            │      │
│  └─────────────────────────┘    │ drawdown_controller.evaluate │      │
│                                 └────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
```

**衔接规则**：
1. **§3.19 → §3.1/§3.2**：盘前初始化成功（加载 VarBreachStateMachine + entry_var + var_model_status）才进入盘前 VaR/ES 计算；var_model_status == UNAVAILABLE → 跳过动态计算，用 §3.10 REBUILD 静态映射
2. **§3.1/§3.2 → 35号 §3.10**：盘前 VaR/ES 产出 var_cvar + breach_state → 喂入 35号 §3.10 drawdown_controller.evaluate(var_breach_state=breach_state)
3. **§3.12 ↔ 35号 §3.13**：盘中循环检测到 7 条触发条件 → 调用 §3.12 重算 → IntradayVarResult → 35号 §3.13 用新 var_cvar 重新裁决（取最严覆盖盘前）
4. **§3.11 → §3.10**：日终回测验证产出 VarBacktestReport.action → RiskOrchestrator 消费 → PASS 无动作 / RECALIBRATE 执行动作 1-4 / REBUILD 执行动作 1-2
5. **§3.10 → §3.18**：校准/重构动作执行完成后 → 触发 §3.18 盘后持久化（VarBreachState + intraday_recalc_log + clean/dirty P&L + var_model_status）
6. **§3.18 → §3.19**：盘后持久化标记可加载 → 次日 §3.19 据此恢复而非冷启动

> **与 35号文档的关系**：本备忘的 5 流程闭环与 [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md) 的 6 流程闭环共享 `RiskOrchestrator`（设计态角色，代码未施工，见 §6 待裁定表 + §3.20.4）。VaR/ES 是 35号 §3.10 日度循环盘前段 + 35号 §3.13 盘中循环的**子步骤**（喂入 drawdown_controller），不是独立流程。§3.18 盘后持久化与 35号 §3.18 共享 `state_store` 持久化层。

### §3.18 盘后状态持久化流程

> **v1.1.0 新增 D9**：对齐 35号 §3.18 的盘后持久化伪代码，本节是 36号文档的盘后保存流程。

**盘后持久化伪代码**（对照 §3.19 加载顺序的逆序）：

```python
def postmarket_persist_var(trade_date, var_breach_state_machine, var_cvar,
                           intraday_recalc_log, clean_pnl, dirty_pnl,
                           var_model_status="AVAILABLE", backtest_report=None):
    """盘后状态持久化：VarBreachState → intraday_recalc_log → clean/dirty P&L →
    var_model_status → 标记可加载。

    顺序与 §3.19 加载逆序：先保存依赖项，再保存依赖者。
    原子性：全部写入成功才标记 trade_date 可加载，部分失败则次日 §3.19 冷启动默认 NORMAL。

    Args:
        var_breach_state_machine: §3.15 VarBreachStateMachine（当日盘前 + 盘中重算后的终态）
        var_cvar: 当日盘前 VarCvarMetrics(var_95, cvar_95)（§3.1/§3.2 产出）
        intraday_recalc_log: §3.12 盘中重算日志列表（可能为空，无触发则空）
        clean_pnl: §3.13 clean P&L（daily_auditor.compute_clean_pnl 产出）
        dirty_pnl: §3.13 dirty P&L（daily_auditor.compute_dirty_pnl 产出）
        var_model_status: "AVAILABLE" / "UNAVAILABLE"（§3.10 REBUILD 动作 1 标记）
        backtest_report: §3.11 VarBacktestReport（回测验证产出，None=当日未回测）
    """
    # ── 阶段 0：审计门控（对齐 35号 §3.18 阶段 0，v1.1.1 补 E1 修复）──
    # v1.1.1 补（E1 修复——盘后持久化顺序）：本函数（36号 §3.18）在 35号 §3.18 之后执行。
    #   RiskOrchestrator 编排顺序：daily_auditor.audit() → 35号 §3.18 postmarket_persist() →
    #   36号 §3.18 postmarket_persist_var()。若 35号 §3.18 阶段 0 审计失败（audit.passed=False）
    #   → 35号 §3.18 return（不持久化）→ 本函数不执行（由 RiskOrchestrator 跳过）。
    #   本函数假设 35号审计已通过 + 35号 §3.18 已完成（DRAWDOWN_COMPLETE 标记已写入）。
    # v1.1.1 补（E2 修复——状态值配对）：本函数标记 "VAR_COMPLETE"，
    #   与 35号 §3.18 "DRAWDOWN_COMPLETE" 配对——§3.19 盘前初始化检查两阶段都 COMPLETE。
    if var_cvar.var_95 < 0 or var_cvar.cvar_95 < var_cvar.var_95:
        daily_auditor.log_persist_skipped(trade_date, reason="var_cvar_invariant_violation")
        state_store.mark_persistable(trade_date, status="VAR_INVARIANT_VIOLATION_SKIP")
        return  # ES ≥ VaR 不变式违反，不持久化

    # ── 阶段 1：VarBreachStateMachine 状态（§3.15）──
    snapshot = VarBreachStateSnapshot(
        state=var_breach_state_machine.state,
        breach_date=var_breach_state_machine.breach_date,
        consecutive_days_below_recovery=var_breach_state_machine.consecutive_days_below_recovery,
        last_transition=var_breach_state_machine.last_transition,
    )
    state_store.save_var_breach_state(trade_date, snapshot)

    # ── 阶段 2：盘前 VaR/ES 基线（供次日 §3.12 盘中重算对比 + §3.16 回撤归因）──
    state_store.save_premarket_baseline(trade_date, VarCvarBaseline(
        var_95=var_cvar.var_95, cvar_95=var_cvar.cvar_95,
    ))
    # 注：entry_var 的持久化由 35号 §3.18 阶段 4b 承载（35号是 entry_var 的消费方）

    # ── 阶段 3：盘中重算日志（§3.12）──
    if intraday_recalc_log:
        state_store.save_intraday_recalc_log(trade_date, intraday_recalc_log)
        # 统计显著重算次数，供回测分析
        significant_count = sum(1 for e in intraday_recalc_log if e.significant)
        daily_auditor.log_intraday_recalc_summary(
            trade_date, total=len(intraday_recalc_log), significant=significant_count,
        )

    # ── 阶段 4：clean/dirty P&L 双轨持久化（§3.13）──
    state_store.save_pnl_dual(trade_date, clean_pnl=clean_pnl, dirty_pnl=dirty_pnl)

    # ── 阶段 5：var_model_status（§3.10 REBUILD 标记）──
    state_store.set_var_model_status(trade_date, var_model_status)
    if var_model_status == "UNAVAILABLE":
        daily_auditor.log_var_model_unavailable(trade_date, reason="REBUILD_triggered")

    # ── 阶段 6：回测报告（§3.11，若有）──
    if backtest_report is not None:
        state_store.save_backtest_report(trade_date, backtest_report)

    # ── 阶段 7：标记可加载（原子性提交点）──
    state_store.mark_persistable(trade_date, status="VAR_COMPLETE")
    daily_auditor.log_var_persist(trade_date, breach_state=snapshot.state,
                                  var_95=var_cvar.var_95, model_status=var_model_status)
```

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

> **v1.1.0 新增 D10**：对齐 35号 §3.15 的盘前初始化伪代码，本节是 36号文档的盘前加载流程。

**盘前初始化伪代码**（对照 §3.18 保存顺序）：

```python
def premarket_initialization_var(trade_date):
    """盘前初始化：加载 VarBreachStateMachine → 加载 premarket_baseline →
    加载 var_model_status → 基线校准。

    顺序不可调换：先加载状态机（防基于错误状态的计算），再加载基线（供盘中对比），
    最后检查 var_model_status（决定是否用动态计算）。

    Returns:
        VarInitializationResult(var_breach_state_machine, premarket_baseline,
                                var_model_status, entry_var)
        或 RefuseStart（若 var_model_status == UNAVAILABLE 且业主未解除）
    """
    # ── 阶段 1：加载 VarBreachStateMachine 持久化状态（§3.15）──
    snapshot = state_store.load_var_breach_state(trade_date)
    if snapshot is None:
        # 冷启动 → 默认 NORMAL（保守：不假设上次在 BREACHED）
        var_breach_sm = VarBreachStateMachine(
            state="NORMAL", breach_date=None, consecutive_days_below_recovery=0,
        )
        daily_auditor.log_var_state_recovery("cold_start_default_NORMAL")
    else:
        var_breach_sm = VarBreachStateMachine(
            state=snapshot.state,
            breach_date=snapshot.breach_date,
            consecutive_days_below_recovery=snapshot.consecutive_days_below_recovery,
        )
        daily_auditor.log_var_state_recovery(f"restored_{snapshot.state}")

    # ── 阶段 2：加载前日盘前基线（供 §3.12 盘中重算对比）──
    premarket_baseline = state_store.load_premarket_baseline(trade_date - 1)
    # None=首次启动/前日未持久化 → §3.12 盘中重算的 var_change_ratio 跳过（无基线对比）

    # ── 阶段 3：加载 var_model_status（§3.10 REBUILD 标记）──
    var_model_status = state_store.load_var_model_status(trade_date - 1)
    if var_model_status is None:
        var_model_status = "AVAILABLE"  # 默认可用

    if var_model_status == "UNAVAILABLE":
        # 检查业主是否已解除 UNAVAILABLE 标记（需 ResetConfirmation，对齐 35号 §3.14）
        if not state_store.is_unavailable_reset_confirmed(trade_date):
            alert("VaR 模型 UNAVAILABLE，业主未解除，使用静态映射", WARNING)
            # 不拒绝启动——用 §3.10 REBUILD 静态映射继续运行（VaR 固定 3%, CVaR 固定 5%）
            # 但标记 var_dynamic_calculation = False，§3.1/§3.2 跳过动态计算
            return VarInitializationResult(
                var_breach_state_machine=var_breach_sm,
                premarket_baseline=premarket_baseline,
                var_model_status="UNAVAILABLE",
                var_dynamic_calculation=False,  # 静态映射模式
                entry_var=None,
            )
        else:
            # 业主已解除 → 恢复动态计算
            var_model_status = "AVAILABLE"
            daily_auditor.log_var_model_recovered(trade_date)

    # ── 阶段 4：加载 entry_var（35号 §3.18 阶段 4b 持久化，跨文档契约）──
    # entry_var = 前日盘前 VaR_95 快照，供 §3.16 回撤归因 current_var vs entry_var 判断风险恶化
    # 注：entry_var 的持久化由 35号 §3.18 承载，本节仅加载供 35号 §3.16 消费
    entry_var = state_store.load_entry_var()  # None=首次启动/前日未持久化

    return VarInitializationResult(
        var_breach_state_machine=var_breach_sm,
        premarket_baseline=premarket_baseline,
        var_model_status=var_model_status,
        var_dynamic_calculation=True,  # 动态计算模式
        entry_var=entry_var,
    )
```

**与 35号 §3.15 的协同**（v1.1.0 补——跨文档契约）：
- 35号 §3.15 盘前初始化加载 DrawdownStateMachine + peak NAV + nav_history + entry_var
- 36号 §3.19 盘前初始化加载 VarBreachStateMachine + premarket_baseline + var_model_status
- **entry_var 由 35号 §3.15 加载**（35号是 entry_var 的主要消费方，用于 §3.16 回撤归因）
- **premarket_baseline 由 36号 §3.19 加载**（36号是 premarket_baseline 的主要消费方，用于 §3.12 盘中重算对比）
- 两者共享 `state_store` 持久化层，但加载各自负责的状态

**代码差距**（待施工）：
1. **无 `state_store.save/load_var_breach_state` 接口**——VarBreachStateMachine 当前内存态
2. **无 `state_store.save/load_premarket_baseline` 接口**——盘前基线未持久化
3. **无 `state_store.set/load_var_model_status` 接口**——REBUILD 标记未持久化
4. **无 `state_store.save/load_pnl_dual` 接口**——clean/dirty P&L 双轨未持久化
5. **无 `state_store.save_intraday_recalc_log` 接口**——盘中重算日志未持久化

> **裁决**：盘前初始化 + 盘后持久化暂缓为 §6 待裁定施工项，与 35号 §3.15/§3.18 同步落地（共享 state_store 基础设施）。最小补丁：① VarBreachStateMachine 持久化到 DB（复用 daily_auditor 已有持久化）；② var_model_status 持久化（REBUILD 标记需跨日）；③ clean/dirty P&L 双轨持久化（回测验证依赖 clean P&L 历史）。

### §3.20 已施工设施盘点（2026-08-12 全量扫描）

> 通用规则 #11 要求：全面扫描项目代码/配置/注册表/测试/文档引用，统一盘点与本文档主题相关的已建设施与配套。本节为 VaR/ES 监控主题的**单一真源盘点**。

#### §3.20.1 已施工代码组件（5 个，src 实测）

| 组件 | 模块 ID | 版本 | 本文档章节 | 实测核对（2026-08-12） |
|---|---|---|---|---|
| `var_calculator.py` | MOD-RK-05 | v0.1.0 production | §3.1 | ✅ 一致 |
| `tail_risk_monitor.py` | MOD-RK-15 | v0.1.0 production | §3.2 | ✅ 一致 |
| `var_backtester.py` | MOD-RK-05B | v0.1.0 evolving | §3.9 | ✅ 一致（full_report 已施工） |
| `daily_auditor.py` | MOD-RK-20 | v0.1.0 production | §3.11 | ⚠️ 部分：run_var_backtest 等设计态 |
| `drawdown_controller.py` | MOD-POS-008 | v0.1.0 production | §3.5 | ⚠️ 部分：var_breach_state/force_static_mode 设计态 |

#### §3.20.2 测试配套（4 个）

| 测试文件 | 对应组件 | 状态 |
|---|---|---|
| `tests/risk/test_var_calculator.py` | MOD-RK-05 | ✅ |
| `tests/risk/test_tail_risk_monitor.py` | MOD-RK-15 | ✅ |
| `tests/risk/test_var_backtester.py` | MOD-RK-05B | ✅ |
| `tests/risk/test_daily_auditor.py` | MOD-RK-20 | ✅ |

#### §3.20.3 注册表登记状态

| 模块 ID | blueprint_registry | module_translation_registry | path_ownership_map | 结论 |
|---|---|---|---|---|
| MOD-RK-05/15/20/POS-008 | ✅ | ✅ | ✅ | 已登记 |
| MOD-RK-05B | ❌ | ❌ | ❌ | **未登记** → §6.1 #1 |

#### §3.20.4 设计态伪代码清单（11 项，src 零命中）

VarBreachStateMachine / intraday_var_recalc / build_black_swan_signal / postmarket_persist_var / premarket_initialization_var / state_store 5 接口 / RiskOrchestrator / force_static_mode / daily_auditor.run_var_backtest+3 审计日志+clean/dirty P&L / backtest_store / FHS 引擎

#### §3.20.5 文档/治理配套

| 配套 | 状态 |
|---|---|
| 30号 §2.5.4/§2.5.6/§2.5.7 | ✅ 已对齐（§3.5 双注解） |
| 35号跨文档契约（v1.31.0） | ✅ 引用有效 |
| 00_index G17 登记 v1.8.0 | ⚠️ 漂移 → §6.1 #2 |
| 31号 §2.3.3 单标的 VaR/CVaR | ✅ 正交（§3.20.6） |
| 32号引用"§4.13 MFCCA" | ⚠️ 错误（应为 §4.6）→ §6.1 #3 |

#### §3.20.6 层级边界声明

- **31号（单标的级）vs 本号（组合级）**：31号前瞻 VaR/CVaR 是单标的仓位约束（MOD-POS-001 C4/C5）；本号是组合 NAV 级风险度量。独立计算、互不消费。
- **32号 FirmRiskAggregator**：30号 §2.5.7 裁定 EVT 输出 → 32号监控信号。消费契约待 32号落地时显式化。

## 4. 考虑过的替代方案

### §4.1 Conformal Risk Control (CRC)（远期增强）

**方案**：用 conformal prediction 框架提供有限样本覆盖保证的 VaR/ES 区间。

**核心算法**：
- CRC（Conformal Risk Control）：λ 校准 + 交换性假设下的覆盖保证
- RWC（Regime-Weighted Conformal）：Schmitt 2026-08 v3，regime 加权
- TWC（Time-Weighted Conformal）：时间衰减加权

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

**ResCP A 股 ESN reservoir 参数验证计划**：
- ResCP 论文"60% 宽度缩减"是相对 NexCP 结论，未相对本项目 EWMA-Normalized 基线验证
- 须 A 股 head-to-head 决择避免"论文好看但 A 股不适配"
- 四要素：①CSI300+CSI500 walk-forward 2019-2023 训练/2024 OOS；②reservoir 参数扫描 192 组合；③四项验收指标；④决择门 ResCP 须同时优于 EWMA-Normalized 才采纳

**ERCIM 145 GREM 默认**（已施工）：
- ERCIM News 145 2026-07 Ruodu Wang
- 第 4 法 E-backtesting 工程化默认规约
- GREM 推荐 betting process + 四级多区制告警替代二元拒绝
- 已在 `var_backtester.py e_backtesting()` 实现

### §4.2 CAESar 联合动态估计（远期）

**方案**：CAESar（Conditional Autoencoder for Expected Shortfall）联合动态估计 VaR 和 ES。

**拒绝理由**：
1. 需要神经网络（autoencoder），与个人系统可解释性优先原则冲突
2. 训练数据需求大，A 股单标的样本不足
3. MVP 历史模拟 + POT 已满足需求

### §4.3 EVaR Expectile 框架（远期）

**方案**：EVaR（Entropy VaR）基于相对熵的 VaR，Expectile 作为 EVaR 的对偶。

**拒绝理由**：
1. 概念复杂度高，可解释性差
2. 与现有 VaR/ES 框架的增量收益不明确
3. 远期研究登记

### §4.4 OCE Risk Minimization（远期，2026-08-07 新增）

**方案**：arXiv:2608.07113 Gupte/Bhat/Prashanth (IIT Madras) 2026-08-07 Optimized Certainty Equivalent (OCE) 风险的样本优化算法。OCE 涵盖 entropic risk、mean-variance risk、CVaR 的平滑变体。给出 OCE 与 UBSR 的特征化联系，构造基于 UBSR 样本平均近似的 OCE 估计器，建立 MSE 界；进一步给出 OCE 梯度估计器与非渐近 MSE 界，嵌入随机梯度算法。

**远期登记理由**：
1. OCE 是包含 CVaR/ES 的统一风险度量族，此论文提供的样本优化算法和收敛速率保证对实现动态 VaR/ES 监控的数值计算底层有指导价值
2. 尤其适合需要平滑 CVaR 变体（避免分位数不连续）的工程实现
3. Phase 2+ 远期

### §4.5 Bayesian EVT Hawkes-AR-Gumbel 联合 CVaR 估计（远期）

**方案**：Ballesteros 2026-05 arXiv:2605.23353 联合模型：
- GPD 严重度 + Hawkes 频率聚类 + AR regime 持续性 + Gumbel 尾部依赖 + HMC 贝叶斯后验

**拒绝理由**：
1. 模型复杂度极高（5 组件联合）
2. HMC 采样计算成本高
3. 独立 LDA 99.995% CVaR 低估 40% 的结论需 A 股验证
4. Phase 4+ 远期

### §4.6 MFCCA 多重分形交叉相关分析（远期）

**方案**：Kakinaka 2026-08 arXiv:2608.04987 MFCCA（Multifractal Cross-Correlation Analysis）：
- 符号保留 + 多重分形 + 无分形误检修复
- 协方差矩阵 regime 转变非参数检测

**拒绝理由**：
1. 用途为 regime 检测（与 36号 VaR/ES 计算正交）
2. 登记 35号 §4.5 远期演进参考

### §4.7 Lambda-quantiles 推广框架（远期，2026-08-10 新增）

**方案**：arXiv:2608.07122 Bellini & Liebrich 2026-08-10 Lambda-quantiles——将经典分位数的常数概率水平 λ 替换为函数参数 Λ: R→[0,1] 的推广。给出有界变分情形下的混合表示定理。

**远期登记理由**：
1. Lambda-quantiles 是 VaR/ES 族风险度量的推广框架
2. 对构建自定义尾部风险监控指标（如对损失幅度敏感的分位数变体）有理论指导
3. 理论性偏强，落地需要进一步工程化
4. Phase 3+ 远期

### §4.8 Preference-Robust Distortion Risk Measures（远期，2026-08-05 新增）

**方案**：arXiv:2608.02854 Bernard & Pesenti 2026-08-05 偏好稳健的失真风险度量，在决策者偏好不确定时给出稳健的风险度量构造。涉及 VaR/ES 类失真度量的稳健化。

**远期登记理由**：
1. 对在 VaR/ES 监控中加入偏好稳健性（应对风险厌恶参数不确定性）有理论价值
2. 落地需要进一步工程化
3. Phase 3+ 远期

### §4.9 CPPI（组合配置层远期候选）

**方案**：CPPI（Constant Proportion Portfolio Insurance）+ RB 两阶段法。

**东方证券 2026-04 A 股实证反证**：
- CPPI+RB 两阶段法 2006-2026 年化 13.41%/Sharpe 1.53 优于等权/RP
- 三层架构兜底 gap risk 反证拒绝理由 #2

**仍不采纳理由**（35号 §4.1）：
1. 定位正交：CPPI 是组合配置层，36号是风险监控层
2. 无保本承诺：个人系统无保本义务
3. 架构耦合：CPPI 引入 floor/gap risk 管理复杂度
4. 可解释性优先：CPPI 的乘数机制比 5 级阈值更难解释

### §4.10 Zhuang 期权隐含 ES bounds（远期参考）

**方案**：Zhuang 2026-07-28 期权隐含 model-free ES bounds。

**A 股可行性**：A 股有 50ETF/300ETF/中证 1000 ETF 期权 + 股指期权，组合层 put 对冲可行（35号 §4.8）。

**远期参考**：期权隐含 ES 提供市场前瞻性尾部风险估计，与历史模拟 ES（回顾性）互补。

### §4.11 Bivariate Orthogonal Polynomials ES 回测（远期，2026-08-10 新增）

**方案**：Yang Lu & Sullivan & Hurlin（Concordia/Aix-Marseille/Orléans）SSC 2026-06 Annual Meeting "Backtesting Expected Shortfall: Accounting for both Duration and Severity with Bivariate Orthogonal Polynomials"——双维度 ES 回测框架：

- **duration 维度**：VaR 违规之间的时间间隔序列（inter-violation durations）
- **severity 维度**：违规时的损失幅度序列（severities in case of violation）
- 用 **bivariate orthogonal polynomials**（双变量正交多项式）推导两个序列满足的正交矩条件
- 提出 **model-free Wald test**，涵盖 VaR 和 ES 的无条件/条件覆盖率回测
- 突破 PIT-based ES 回测不能分离 frequency 和 severity 的限制

**远期登记理由**：
1. 当前 §3.9 MVP 4 法中 Christoffersen 只检测 VaR 违规的独立性（duration），Acerbi-Szekely Z2 只检测 ES 幅度（severity）——两者分离。Bivariate OP 框架**联合** duration + severity，提供更全面的 ES 回测
2. model-free Wald test 工程实现简单（无需 GARCH 拟合），适合个人系统
3. 应登记为 §3.9 远期第 14 法（Bivariate OP Wald test）
4. Phase 2+ 远期

**与现有 4 法的关系**：
- Kupiec POF：覆盖率（frequency）——Bivariate OP 的 duration 维度子集
- Christoffersen：独立性（duration 聚集）——Bivariate OP 的 duration 维度子集
- Acerbi-Szekely Z2：ES 幅度（severity）——Bivariate OP 的 severity 维度子集
- E-backtesting：anytime-valid 累积——与 Bivariate OP 正交，可叠加
- **Bivariate OP**：duration × severity **联合**——补充上述 4 法的分离检测

### §4.12 ERCIM 145 e-values Post-hoc 风险审计（远期，2026-08-10 新增）

**方案**：ERCIM News 145 (2026-07) Special theme "E-values: Statistical Testing for the 21st Century"——Etienne Gauthier (Inria/ENS/PSL) "Rethinking Conformal Prediction for Constrained Environments"：

- e-values 支持 **post-hoc control of uncertainty**——在观测数据后调整统计保证
- 不像 p-values 在观测后修改参数会失去统计有效性，e-values 允许**回顾性审计和调整**
- 可在飞行中导出自适应覆盖水平，无需额外数据或复杂数据分割

**远期登记理由**：
1. 当前 §3.9 第 4 法 E-backtesting 已用 e-values 做 anytime-valid 累积检验，但仅用于**前向**监测。Gauthier 的 post-hoc 框架扩展了 e-values 的**回顾性审计**用途
2. 对本项目的启示：VaR breach 后可用 e-values **回顾性审计**模型校准——"过去 N 天的 VaR 预测在事后看是否校准良好"，不需预设 α 水平
3. 与 §3.10 RECALIBRATE/REBUILD 决策互补：前向 E-backtesting 触发 RECALIBRATE，回顾性 e-values 审计确认 RECALIBRATE 是否有效
4. Phase 2+ 远期（需 E-backtesting 工程化稳定后扩展）

### §4.13 Fuzzy Conformal Prediction Sets（远期，2026-08-10 新增）

**方案**：arXiv:2509.13130 Koning & van Meer (Erasmus University Rotterdam) "Optimal Conformal Prediction, E-values, Fuzzy Prediction Sets and Subsequent Decisions"：

- **fuzzy conformal confidence sets**：将传统二元 inclusion/exclusion 推广为 [0,1] 区间的"排除程度"
- 连接 fuzzy confidence sets 与 e-values——排除程度等价于在不同置信水平下的排除
- fuzzy confidence set 是一种 predictive distribution，有更合适的误差保证
- 推导最优 conformal confidence sets（minimax 最优测试问题）
- 推广到非交换性 conformal 设置之外的任意模型预测置信集

**远期登记理由**：
1. 当前 §3.1 VaR 是单点估计（95% 分位数），fuzzy conformal 可提供**区间 + 程度**的尾部风险估计——"损失超过 X 的排除程度是 0.7"比"VaR=X"信息更丰富
2. 对 drawdown_controller 的启示：position_cap 可基于 fuzzy 排除程度连续调整，而非基于硬阈值的离散分级
3. 与 §4.1 Conformal Risk Control 互补：CRC 提供 coverage 保证，Fuzzy CP 提供 degree 表达
4. Phase 3+ 远期（需 conformal 预测层就绪）

### §4.14 E-backtesting v6 GRO/GREE/GREL 最优构造（远期，2026-08-10 新增）

**方案**：arXiv:2209.00991v6 Qiuqi Wang/Ruodu Wang/Johanna Ziegel (Georgia State/Waterloo/ETH) 2026-04-15 E-backtesting v6——e-process 最优构造方法系统化：

- **GRO（Growth-Rate Optimal）**：最大化 e-process 的期望对数增长率，对单一假设最优
- **GREE（Growth-Rate for Expected Exceedance）**：针对 ES 的 e-process 构造
- **GREL（Growth-Rate for Expected Loss）**：针对期望损失的 e-process 构造
- **GREM（Growth-Rate for Expected Mixture）**：混合 e-process，已在 var_backtester.py 实现
- v6 关键贡献：**characterization of backtest e-statistics**——用 identification functions 刻画 VaR/ES 的 backtest e-statistics 唯一形式

**远期登记理由**：
1. 当前 §3.9 第 4 法 E-backtesting 用 GREM 默认（ERCIM 145 推荐），v6 的 GRO/GREE/GREL 提供**针对特定风险度量的最优 e-process**——GREE 专为 ES 设计，可能比 GREM 通用方法对 ES 检验更敏感
2. v6 的 characterization 结果说明 backtest e-statistics 的唯一性，为 §3.9 远期第 7 法 Fissler-Ziegel 联合回测提供理论基础
3. 对本项目的启示：当前 GREM 是"通用混合"，远期可针对 ES 切换到 GREE 提高检验效率
4. Phase 2+ 远期（需 var_backtester.py 扩展支持多 e-process 构造方法选择）

**与 §3.9 MVP 4 法的关系**：
- 当前第 4 法用 GREM（混合）——通用但非最优
- 远期可配置 `e_process_method = "GRO" | "GREE" | "GREL" | "GREM"`，按检验目标选择
- GREE 专为 ES → Acerbi-Szekely Z2 失败时优先切换 GREE
- GREL 专为期望损失 → Kupiec POF 失败时优先切换 GREL

### §4.15 Ye et al. 2026-08-06 Finite-Sample Conformal Risk Bounds for Joint VaR/ES（远期，2026-08-10 新增）

**方案**：[MDPI Mathematics 14(15):2847](https://www.mdpi.com/2227-7390/14/15/2847) Ye/Qiu/Zhu/Ladikas (Central South University of Forestry/CAS/KIT) 2026-08-06 "Finite-Sample Conformal Risk Bounds for Joint Value-at-Risk and Expected-Shortfall Forecasting Under Non-Exchangeable Financial Time Series"：

- **核心问题**：金融尾部风险观测是**非可交换的**（serial dependence + regime shifts 使联合分布依赖时间排序），且 ES 不可独立 elicitable——标准 conformal 保证的 exchangeability 假设失效
- **方法**：tune a single inflation parameter by conformal risk control on a bounded monotone loss that **couples VaR breach frequency with breach magnitude normalized by VaR-ES gap**——保证是对 tail-gap-normalized exceedance-severity surrogate 的风险控制
- **理论保证**：
  - 交换性下：有限样本期望风险控制
  - 非可交换下：non-exchangeable swap-distance bound + regime-drift bound（含 explicit cumulative β-mixing cost）+ high-probability realised-path statement + heavy-tail rate D(p−1)/p
- **实证**：8 exchange rates + Bitcoin + GIFT-Eval finance domain，用前一月 FRED-MD vintages 因果构建 regime（避免 look-ahead bias），weighted controller violation rate 2.51%，Fissler-Ziegel score 0.431（vs 最强 conformal baselines 0.441/0.439）——incremental gain，concentrates in turbulent regimes

**远期登记理由**：
1. **解决 A 股非可交换性**：A 股收益序列有强时序依赖（波动率聚集）+ regime shift（牛熊转换），标准 conformal 的 exchangeability 假设失效——Ye et al. 的 non-exchangeable swap-distance bound + regime-drift bound 直接针对此问题
2. **Joint VaR/ES 校准**：ES 不可独立 elicitable 是 §3.9 回测的核心难题（第 3 法 Acerbi-Szekely Z2 是间接检验），Ye et al. 的 bounded monotone loss couples VaR breach frequency with ES breach magnitude——提供 joint 校准的有限样本保证
3. **与 §4.1 CRC + §4.14 Schmitt RWC 的关系**：CRC（§4.1）是标准 conformal risk control，RWC（§4.7/35号 §4.17）是 regime-weighted conformal calibration，Ye et al. 是 **joint VaR/ES + non-exchangeable** 的 conformal risk bounds——三者互补：CRC 是基础，RWC 是 regime 加权，Ye et al. 是 joint + non-exchangeable 理论保证
4. **对 §3.9 回测的增强**：当前 §3.9 第 4 法 E-backtesting 提供 anytime-valid 检验，Ye et al. 的 conformal risk control 提供 **calibration 阶段**的有限样本保证——两者正交（一个管回测检验，一个管校准调整）
5. Phase 3+ 远期（需 conformal 预测层 + regime 特征工程就绪，与 §4.1 CRC / §4.14 RWC 同批次）

### §4.16 TailRisk-Trans Transformer-based 动态 VaR/ES（远期，2026-08-10 新增）

**方案**：[Frontiers in Business and Finance Volume 3 Issue 1](https://sprcopen.com/index.php/FBF/article/download/742/641/1991) Wang & Bai (HKU/Columbia) 2026 "TailRisk-Trans: A Transformer-Based Dynamic Tail-Risk Prediction Model with Extreme-Event–Aware Attention for Financial Markets"：

- **架构**：4 组件——金融数据预处理层（微结构+衍生品隐含+宏观因子）+ Market Transformer Encoder（长程时间依赖）+ Tail-Risk Prediction Head（联合预测 VaR/ES/CVaR）+ Extreme-Event-Aware Attention（自适应增强对波动率尖峰的敏感度）
- **可微分分位数回归层**：`q_α = h·W₄ + b₄`，quantile loss `L_q = Σ ρ_α(yᵢ − q_α,ᵢ)`
- **实证**：99% VaR violation rate 从 4.12% 降至 3.47%（15.8% 改进），quantile loss 2.684，ES score 3.892（vs 最强 baseline Transformer-TS）

**远期登记理由**：
1. **过度工程风险**：Transformer 训练需大量数据（A 股单标的日度数据 <10 年）+ GPU 算力（个人系统 CPU only），与 §2.3 约束"算力有限，不能跑蒙特卡洛 GPU 模拟"冲突
2. **可解释性不足**：Transformer attention 权重难向业主解释"为什么这个点减仓"，与 35号 §3.19 过度工程红线 3"可解释性优先"冲突
3. **登记价值**：作为 §3.1 VaR 计算的远期演进方向登记——当前参数法+历史模拟取 max 是 Phase 1，TailRisk-Trans 是 Phase 3+ 的深度学习远期候选（待 GPU 算力 + 可解释 AI 技术成熟后评估）
4. **与 §4.15 Ye et al. 的关系**：Ye et al. 是 conformal calibration（wrap 任意 forecaster），TailRisk-Trans 是 forecaster 本身——远期可组合：TailRisk-Trans 作 base forecaster + Ye et al. conformal calibration 作 wrapper

### §4.17 ReSGA 检索增强自分组自编码器尾部风险大模型（远期，2026-08-10 新增）

**方案**：[arXiv:2606.04576](https://arxiv.org/abs/2606.04576) Zhang, Zhu & Zhu 2026-06 "ReSGA: A Large Tail Risk Model for Learning Value-at-Risk and Expected Shortfall"（港大+厦门大学）：

- **架构**：百万参数级检索增强自分组自编码器——编码器将特征映射到潜在表示，检索器按特征相似性将资产分组，解码器在组内联合预测 VaR 和 ES
- **实证**：1926-2023 美股月度回报 + 153 个公司特征，VaR-ES 联合预测改进主要由**数据复杂度而非模型复杂度**驱动，展示组重要性可解释性和跨市场迁移学习能力

**远期登记理由**：
1. **过度工程风险**：百万参数级模型与个人系统算力约束冲突（§2.3"算力有限，不能跑蒙特卡洛 GPU 模拟"），训练+推理成本远超 Phase 1 参数法+历史模拟
2. **轻量化提取价值**：ReSGA 的核心洞察可脱离大模型独立实现——①**按特征相似性分组后组内联合估计 VaR/ES**（检索器思路，用 k-NN/层次聚类替代深度检索器，<50 行代码无需 GPU）；②**"数据复杂度比模型复杂度更重要"**结论意味着个人系统应投资于特征工程而非堆参数——印证 §3.1 参数法+历史模拟取 max 在特征充分时已足够
3. **与 §4.16 TailRisk-Trans 的关系**：TailRisk-Trans 是单标的时序深度学习（temporal），ReSGA 是横截面分组深度学习（cross-sectional）——两者正交，远期可组合：ReSGA 组内联合估计 + TailRisk-Trans 时序动态 + Ye et al. conformal calibration
4. **与 §3.1 当前实现的关系**：当前参数法+历史模拟是单标的独立计算（无分组信息共享），ReSGA 的"组内联合估计"思路可在 Phase 2 作为轻量增强——按行业/因子暴露聚类分组后，组内共享 VaR/ES 估计的样本池（类似 panel data 思路），提高小样本稳定性
5. Phase 3+ 远期（需 GPU 算力 + 153 维特征库就绪，与 §4.16 TailRisk-Trans 同批次评估）

### §4.18 D'Innocenzo et al. 2026 JBES 单整合尾形参数动态 VaR/ES（远期，2026-08-10 新增）

**方案**：[JBES DOI:10.1080/07350015.2026.2619541](https://www.tandfonline.com/doi/abs/10.1080/07350015.2026.2619541) D'Innocenzo/Lucas/Schwaab/Zhang（Bologna/VU Amsterdam/ECB/Sveriges Riksbank）2026 "Joint Extreme Value-at-Risk and Expected Shortfall Dynamics with a Single Integrated Tail Shape Parameter"：

- **核心创新**：基于 EVT 的条件 GPD-POT 动态框架，两个关键设计——① **unit root-like integrated autoregressive dynamics** for GPD tail shape（单整自回归尾形参数，捕捉尾部厚度的持续性）；② **re-scale POTs by their thresholds**（将超额值按阈值重标），获得仅一个时变参数描述整个尾部的更简约模型
- **理论保证**：建立 integrated time-varying parameter model 及其 filter 的平稳性/遍历性/可逆性参数区域 + MLE 一致性与渐近正态性条件
- **实证**：两种加密货币汇率，single-parameter 模型在捕捉 VaR/ES 动态（尤其极端尾部）上具竞争力
- **ECB Working Paper 版本**：[ECB WP 3166](https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp3166~4e485ab256.pt.pdf)

**远期登记理由**：
1. **直接增强 §3.2 POT 厚尾拟合**：当前 §3.2 POT 用固定 90% 分位数阈值 + 静态 GPD(ξ, β) 拟合，D'Innocenzo 的 integrated tail shape 让 ξ 随时间动态演化（unit root-like 持续性），更适配 A 股牛熊转换的尾部厚度变化
2. **单参数简约性适合个人系统**：仅一个时变参数（re-scaled tail shape），比双参数（ξ, β）时变模型更易估计 + 更稳健——A 股短样本下双参数时变 GPD 拟合易过拟合，单参数降低估计风险
3. **与 §3.3 Uehara 双门控互补**：Uehara 解决"阈值选择"（u 选哪），D'Innocenzo 解决"尾形动态"（ξ 如何随时间变）——两者正交可组合
4. **与 §4.16 TailRisk-Trans 的关系**：TailRisk-Trans 是深度学习 forecaster（黑箱），D'Innocenzo 是半参数 score-driven 模型（可解释 + 渐近理论保证）——D'Innocenzo 更适合个人系统可解释性优先原则
5. Phase 2+ 远期（需 score-driven 滤波器工程化，与 §3.16 FHS 同批次评估，FHS 是 GARCH 残差重采样，D'Innocenzo 是 GPD 尾形动态——两者尾部建模思路不同可择优）

### §4.19 Jia & Han 2026 自适应 conformal 组合选择（远期，2026-08-10 新增）

**方案**：[DMO-FinTech Workshop Paper](https://academicworkshops.github.io/DMO-FinTech/docs/2026_Paper_portfolio_selection_with_adaptive_conformal_prediction.pdf) Jia & Han（HKUST Guangzhou, Thrust of Financial Technology）2026 "Portfolio selection with adaptive conformal prediction"：

- **核心方法**：model-free 组合选择框架，用 conformal prediction 估计投资风险（VaR 从 prediction set 下界导出）+ projected gradient descent 优化组合权重（受投资者约束）+ adaptive conformal inference（梯度下降调 prediction set 宽度，适应 distribution shift）+ 历史候选步长 re-weighting（解决步长敏感性问题）
- **covariate 变量**：从"virtual portfolios"（用组合收益而非个股收益）导出——降低维度，避免高维个股特征
- **实证**：美股市场，conformalized 策略（含 short-selling 约束）consistently outperform equal-weighted portfolio 和 non-conformal counterparts across multiple performance metrics

**远期登记理由**：
1. **组合层 conformal 保证**：当前 §4.1 CRC/RWC 是单资产层面 VaR 校准，Jia & Han 扩展到组合选择层面——给定候选资产池，用 conformal 框架自适应选择覆盖率有保证的组合
2. **model-free 适配个人系统**：框架不依赖特定预测模型假设（AR/GARCH/RF/NN 均可嵌入），与本项目 §3.1 参数法+历史模拟（无分布假设）理念一致——可 wrap 现有 VaR 预测器
3. **与 §4.15 Ye et al. 的关系**：Ye et al. 是 joint VaR/ES conformal risk bounds（单资产非可交换），Jia & Han 是组合选择 conformal（多资产自适应）——两者正交
4. **与 Kato arXiv:2410.16333 Conformal Predictive Portfolio Selection 的关系**：Kato 用 conformal interval 从有限菜单选组合（不涉及 position sizing），Jia & Han 用 adaptive conformal + gradient descent 优化连续权重——Jia & Han 更接近本项目的连续仓位调整需求
5. **A 股适配性**：A 股板块轮动显著，adaptive conformal 可自动适应风格切换（distribution shift），比静态组合更鲁棒；short-selling 约束天然适配 A 股不能做空约束
6. Phase 3+ 远期（需 conformal 预测层 + 组合优化层就绪，与 §4.1 CRC / §4.15 Ye et al. 同批次）

### §4.20 Fu 2026-01 动态因子半参数 VaR/ES（realized measures）（远期，2026-08-10 新增）

**方案**：[arXiv:2601.01142](https://arxiv.org/abs/2601.01142) Fu（Jinan University）2026-01 "A dynamic factor semiparametric model for VaR and expected shortfall driven by realized measures"：

- **架构**：CAViaR 分位数递归 + 动态 ES-VaR gap（捕捉时变尾部严重度）+ 测量方程（多 realized measures 转高频风险新息）+ 动态因子模型（提取公共高频尾部风险因子）
- **双通道分离**：分位数水平（risk level）与尾部厚度（tail thickness intensification）通过不同风险通道影响——明确分离"风险水平变化"与"尾部风险加剧"
- **实证**：consistently outperforms quantile regression / EVT-based / GARCH-type benchmarks across multiple loss functions，highlighting 重要性 of embedding high-frequency information directly into tail risk generation layer

**远期登记理由**：
1. **高频信息融入尾部风险生成层**：当前 §3.1 VaR 用日度收益序列（低频），Fu 用 realized measures（5 分钟 RV/BV/RK 等高频波动率度量）驱动 VaR/ES——高频信息对尾部预测有显著增量价值（论文实证优于低频基准）
2. **A 股高频数据可得性**：A 股 Level-1 行情（5 分钟 K 线）已由 §3.7 技术指标体系覆盖 9 个周期（含 5min/15min），realized measures 计算基础设施已就绪——Fu 框架可复用现有高频数据管道
3. **双通道分离设计的解释性**：risk level（分位数位置）与 tail thickness（尾部厚度）分离，与 §3.1 参数法（μ, σ 决定分位数）+ §3.2 POT（ξ 决定尾部厚度）的二分架构同构——Fu 是两者的动态联合版本
4. **与 §4.18 D'Innocenzo 的关系**：D'Innocenzo 是 EVT-GPD 尾形动态（时变 ξ），Fu 是半参数 CAViaR + realized measures（时变分位数 + gap）——两者尾部建模路径不同（EVT vs CAViaR），可择优或组合
5. Phase 2+ 远期（需高频 realized measures 数据管道 + CAViaR 递归工程化，与 §3.16 FHS 同批次评估）

### §4.21 CVaR 风险感知 Q-Learning 自适应有限预算训练（远期，2026-08-10 新增）

**方案**：[arXiv:2608.04305v1](https://arxiv.org/abs/2608.04305) [cs.LG; q-fin.RM] 2026-08-05 "Adaptive Finite-Budget Training for CVaR Risk-Aware Q-Learning"，Yifan Wu / Junjie Lei / Wenjie Huang，ICAIF '26（International Conference on AI in Finance, Milan）。**v1.10.0 补全论文细节**（v1.2.0 浅登记同一 arXiv ID，本次补全 6 协同机制+实证+伪代码）：

- **CVaR Risk-Aware Q-Learning（RaQL）**：model-free 双时间尺度估计器用于动态风险目标。核心创新是用 CVaR（Conditional Value at Risk = ES）替代期望 Q 值作为**内在目标函数**（risk-aware RL，非外层 constrained RL）。但原始 RaQL 在**有限预算**下行为脆弱：固定内循环超参产生不稳定值估计、持续 Bellman 残差、低效样本复用
- **关键设计原则**：本文**保留原 CVaR 估计器和 Bellman 不动点不变**，仅重设计训练过程——提出自适应训练控制器，含 **6 个协同机制**：
  1. **per-cell inner-step sizing**：按状态单元（cell）自适应调整内循环步数，不稳定 cell 多投入
  2. **outer-rate-matched decay synchronization**：内循环学习率衰减与外循环速率匹配同步
  3. **short early correction for VaR-like inner variable**：对类 VaR 内变量施加短期早期校正
  4. **coverage-first-then-greedy sample allocation rule**：先覆盖（exploration）后贪婪（exploitation）的样本分配
  5. **progressive suffix aggregation of mature inner estimates**：对成熟内估计做渐进后缀聚合
  6. **data-driven calibration of key scales**：从在线可观测量数据驱动标定关键尺度
- **理论保证**：有限样本收敛性证明 + CVaR 估计的 PAC bound（保留原 RaQL 理论，仅训练过程改变）

**实证结果**（20 random seeds，856,000 内循环转换样本）：
- **Bellman 残差降 85%**：MeanBEQ 1.2202→0.1854；MeanBEV 1.1624→0.0535
- 跨 CVaR level / discount / budget 稳定（鲁棒性跨超参）
- **OOS 测试**：Sharpe 0.9281，maxDD 6.46%（含交易成本）；buy-and-hold 收益更高但波动率 47.93% vs RaQL 9.57%——风险调整后表现显著优于 buy-and-hold
- **关键洞见**：仅修改训练过程不动风险目标即可显著提升可靠性和风险调整后表现

**与本项目的关系**：
1. **与 §3.5 触发动作的关系**：§3.5 当前是**规则驱动**的 5 级系统性风险分级（GREEN/YELLOW/ORANGE/RED/BLACK）→ position_cap 映射。CVaR Q-Learning 是**RL 驱动**的风险感知仓位调整——两者是"规则 vs 学习"的替代关系
2. **与 §3.1 VaR 计算的关系**：§3.1 用参数法+历史模拟取 max 估计 VaR，CVaR Q-Learning 用 RL 内嵌 CVaR 估计——前者是**离线估计**（独立模块），后者是**在线学习**（嵌入决策循环）
3. **与 31号 Conformal Kelly 的关系**：Conformal Kelly 是**仓位 sizing**（用共形区间宽度调仓位），CVaR Q-Learning 是**仓位+动作 learning**（用 CVaR 目标学最优仓位+动作）——前者是静态映射，后者是动态学习
4. **与 §4.27 Information-Geometric Bayesian 的关系**（v1.10.0 补）：§4.27 是**分布形状漂移检测**（监控层——后验分布在 Fisher 流形上移动触发校准），本节是 **CVaR 估计训练稳定性**（训练层——有限预算下 RaQL 内循环估计器的训练过程自适应控制）。二者正交：§4.27 管"分布变了没"（输入端漂移），§4.21 管"CvaR 估计学得稳不稳"（训练端稳定性）。36 号当前 CVaR/ES 估计是**静态/批量**的（§3.1 参数法+历史模拟离线取 max），本节提供**有限预算在线训练稳定性**机制——若远期引入 RL 风险感知决策，6 机制控制器是 RaQL 落地的前置稳定性保障

**远期登记理由**：
1. **过度工程风险**：RL 需训练数据+环境模拟器+奖励函数设计，与个人系统"算力有限+可解释性优先"约束冲突——§3.5 规则驱动的 5 级分级已通过 Phase 1 验证且可解释，RL 增量价值需实盘数据验证
2. **与 40号执行 RL 的关系**：40号已登记 TT-DAC-PS（Phase 2 执行 RL 候选）+ Cheridoto-Weiss logistic-normal RL（Phase 2）+ Garg regime-RL 三部曲（验证 flat RL 无法学习 regime 条件执行）。CVaR Q-Learning 是**风险层 RL**（不同于执行层 RL），但 Garg Paper I 的负面结果（hand-coded rule > flat RL）同样适用——Phase 3+ 评估时优先用 hand-coded CVaR 约束（§3.5 规则）而非 RL
3. **轻量化提取价值**：CVaR Q-Learning 的核心洞察"用 CVaR 替代期望 Q 值"可脱离 RL 独立实现——当前 §3.5 的 5 级分级已隐含 CVaR 约束（BLACK 级 CVaR > 10% → 全清仓），Phase 2 可评估是否需要更细粒度的 CVaR 驱动仓位调整（如 CVaR 每增 1% → 仓位减 X%），而非上 RL
4. Phase 4 鲁棒性阶段远期（需 RL 训练环境+足够实盘数据积累+与 40号执行 RL 同批次评估；v1.10.0 对齐：原 Phase 3+ 上调至 Phase 4 鲁棒性阶段）

**不过度工程审查**：CVaR Q-Learning 需 RL 训练基础设施（环境/奖励/ replay buffer）+ CVaR 估计的样本效率问题 + 收敛性调参——远超个人系统 Phase 1-2 预算。**Phase 4 鲁棒性阶段**评估（v1.10.0 对齐）——若 40号执行 RL 已落地且验证有效，再评估风险层 CVaR RL。

**伪代码**（6 机制中 #1 per-cell sizing / #2 outer-rate-matched decay / #4 coverage-first-then-greedy / #5 suffix aggregation 四机制简化版，<50 行；保留原 CVaR 估计器与 Bellman 不动点，仅重设计训练过程）：

```python
def adaptive_raql_train(env, cvar_levels, budget, outer_steps=100, base_inner=10, base_lr=0.1):
    Q = init_q_table(env)                  # 外循环 Q（Bellman 不动点目标）
    inner_var = init_inner_var()           # 类 VaR 内变量（#3 短期早期校正可施加）
    cells = env.discretize_cells()
    cell_instability = {c: 1.0 for c in cells}   # #1 per-cell 不稳定性
    sample_count = {c: 0 for c in cells}          # #4 覆盖计数
    coverage_threshold = budget * 0.4             # #4 前 40% 预算覆盖
    mature_estimates = []                         # #5 成熟内估计池
    for outer in range(outer_steps):
        lr_inner = base_lr * decay(outer, outer_steps)   # #2 outer-rate-matched decay
        for cell in cells:
            n_inner = int(base_inner * cell_instability[cell])   # #1 不稳定 cell 多投入
            estimates = []
            for _ in range(n_inner):
                if sum(sample_count.values()) < coverage_threshold:  # #4 coverage-first
                    s = env.sample_uniform(cell)
                else:                                                 # #4 then greedy
                    s = env.sample_greedy(cell, Q)
                sample_count[cell] += 1
                est = cvar_estimator.update(s, inner_var[cell])      # 原 CVaR 估计器不动
                estimates.append(est)
            mature = suffix_aggregate(estimates, maturity_frac=0.5)  # #5 成熟后缀聚合
            mature_estimates.extend(mature)
            # Bellman 残差越大 → cell 越不稳定 → 下轮多投入（#6 data-driven 反馈）
            cell_instability[cell] = 1.0 + bellman_residual(Q, cell, mature)
        Q = bellman_update(Q, mature_estimates, cvar_levels)   # 外循环不动点更新
    return Q
```

### §4.22 Standard and Comparative E-backtests for General Risk Measures（远期，2026-08-10 新增）

**方案**：[arXiv:2511.05840](https://arxiv.org/abs/2511.05840) Jiao, Wang & Zhao 2025-11 "Standard and comparative e-backtests for general risk measures"：

- **标准 e-backtest 扩展**：将 Wang et al. 2026（§4.14 E-backtesting v6 GRO/GREE/GREL）的 e-value 框架从 (VaR, ES) 二元扩展到**任意可识别风险度量**（identifiable risk measures）——mean / variance / VaR / ES / expectile 均可 model-free backtest。基于 identification function 构造 test supermartingales，Casgrain et al. 2022 的静态理论动态化
- **比较 e-backtest（comparative backtest）**：标准 backtest 只回答"模型准不准"，比较 backtest 回答"内部模型 vs 监管标准模型谁更准"——H₀⁻: 内部模型至少与标准模型一样准 / H₀⁺: 内部模型至多与标准模型一样准。基于 e-processes 构造双向检验，complement 标准 backtest 的"通过 ≠ 正确"盲区（Fissler et al. 2016 指出标准 backtest alternative 过宽）
- **expectile 回测**：expectile 是唯一 elicitable 的谱风险度量（Newey & Powell 1987），本论文首次提供 expectile 的 model-free e-backtest——为 §4.3 EVaR Expectile 框架提供回测验证路径

**与本项目的关系**：
1. **与 §3.9 回测验证的关系**：§3.9 MVP 4 法（Kupiec/Christoffersen/Z2/E-backtesting）是**标准 backtest**（评估单一模型准确性）。Jiao 比较 backtest 提供**模型间比较**能力——Phase 2 可用于比较 conservative_max（§3.1）vs FHS（§3.16）vs 历史模拟法的预测质量，当前仅靠 Basel 交通灯 + E-backtesting GREM 告警定性判断，缺定量 head-to-head 检验
2. **与 §4.14 E-backtesting v6 的关系**：§4.14 是 (VaR, ES) 专用 e-backtest 的最优构造（GRO/GREE/GREL），§4.22 是**通用化扩展**（任意 identifiable risk measure + comparative dimension）。两者递进：§4.14 是 §4.22 的特例（risk measure = (VaR, ES)），§4.22 是 §4.14 的泛化
3. **与 §4.3 EVaR Expectile 的关系**：§4.3 登记 EVaR/Expectile 框架但无回测路径，§4.22 首次提供 expectile 的 model-free e-backtest——填补 §4.3 的回测验证缺口
4. **与 §3.10 校准/重构的关系**：比较 backtest 的 H₀⁻/H₀⁺ 双向检验可嵌入 §3.10 RECALIBRATE 决策——若 internal model（conservative_max）vs standard model（纯历史模拟）比较 backtest 拒绝 H₀⁻（internal 不如 standard），触发 RECALIBRATE 重新评估 method 选择

**远期登记理由**：
1. **MVP 回测已足够**：§3.9 4 法回测（Kupiec/Christoffersen/Z2/E-backtesting）已覆盖 Basel 监管要求 + ES 直接回测 + anytime-valid 在线检验，Phase 1 生存底线已满足
2. **比较 backtest 需多模型并行**：当前 §3.1 conservative_max 取 max 后是单一输出，比较 backtest 需保守并行运行多个 VaR 模型（parametric / historical / FHS）分别 e-backtest 再比较——Phase 2 FHS 落地后才有比较对象
3. **expectile 回测需先落地 expectile 计算**：§4.3 EVaR/Expectile 是远期，expectile e-backtest 随其后
4. Phase 2+ 远期（FHS 落地后，多模型并行回测时评估比较 backtest 价值）

**轻量化提取价值**：比较 backtest 的核心洞察"通过标准 backtest ≠ 模型正确（alternative 过宽）"可立即应用于 §3.11 回测验证解读——当前 §3.11 action 映射 PASS/RECALIBRATE/REBUILD 仅基于标准 backtest 结果，Phase 1 可在审计日志中标注"PASS ≠ 模型正确，仅 = 未检测到显著偏差"，避免过度自信。无需代码改动，仅审计解读增强。

**不过度工程审查**：比较 backtest 需 e-process 双向构造 + identification function 推导 + 多模型并行回测管道——远超 Phase 1 预算。Phase 2+ FHS 落地后评估。

### §4.23 Discrete Moment Matching（DMM）VaR Bracketing——稳健尾部替代（远期，2026-08-10 新增）

**方案**：[arXiv:2601.09927](https://arxiv.org/abs/2601.09927) Aditri 2026-01 "Efficiency versus Robustness under Tail Misspecification: Importance Sampling and Moment-Based VaR Bracketing"：

- **核心问题**：VaR 在高置信度（99%+）是稀有事件估计，对尾部模型选择极敏感。重要性采样（IS）在名义模型下高效但**系统性低估**厚尾真实 VaR；离散矩匹配（DMM）通过有限矩约束构造**保守 VaR 区间**（bracketing），在尾部误设下保持稳健
- **DMM 算法**：给定有限矩约束（均值/方差/偏度/峰度等），在离散化网格上构造满足矩约束的分布集合，VaR 区间 = 该集合上 VaR 的 [min, max]。矩越多区间越紧但数值可行性下降
- **IS vs DMM 权衡**：IS 追求**效率**（低方差，但模型误设下偏差大）；DMM 追求**稳健**（显式建模分布模糊性，但区间宽、效率低）。方差缩减单独不足以在模型不确定性显著时保证尾部风险估计可靠

**与本项目的关系**：
1. **与 §3.2 POT 的关系**：POT 用 GPD 拟合尾部（参数化），DMM 用矩约束构造 VaR 区间（非参数化半稳健）。POT 在 GPD 拟合失败时（§3.2 兜底已补）回退历史模拟，DMM 可作为**第三条路径**——当 GPD 拟合失败且历史模拟样本不足时，DMM 矩约束区间比纯历史模拟点估计更稳健
2. **与 §3.3 Uehara 双门控的关系**：Uehara 双门控拒绝 GPD 外推时回退历史模拟 ES（§3.2 兜底）。DMM 提供替代——拒绝 GPD 外推时可用 DMM 矩约束构造 ES 区间，比纯历史模拟更保守
3. **与 §3.1 conservative_max 的关系**：当前 §3.1 取 max(parametric, historical) 是"两法取最保守"，DMM 区间上界可作为**第三法**纳入 max——DMM 上界在厚尾场景下可能比历史模拟更高，进一步强化保守性
4. **A 股适配**：A 股收益分布厚尾+偏斜，矩约束（4 阶矩：均值/方差/偏度/峰度）可捕捉这些特征。DMM 不需 GPD 假设，在 A 股短样本下比 POT 更稳健

**远期登记理由**：
1. **MVP POT 已足够**：§3.2 POT + 历史模拟双轨已覆盖 MVP 需求，GPD 拟合失败有兜底
2. **DMM 区间宽**：矩约束少则区间太宽（保守但无用），多则数值不可行——需校准矩数量与网格精度，工程化成本高于 POT
3. **Phase 2+ 评估**：当 POT 频繁拟合失败（A 股短样本+极端行情）或 Uehara 双门控频繁拒绝外推时，DMM 作为稳健替代评估

**轻量化提取价值**：DMM 的核心洞察"方差缩减 ≠ 尾部准确（模型误设下 IS 系统性低估）"可立即应用于 §3.1 参数法的解读——参数法（正态假设）在厚尾下系统性低估 VaR，取 max(parametric, historical) 的 conservative_max 设计正是对此的缓解。Phase 1 可在审计日志中标注"参数法低估厚尾风险是已知局限，conservative_max 是缓解而非消除"。

**不过度工程审查**：DMM 需矩约束优化+离散化网格+区间构造算法，远超 Phase 1 预算。Phase 2+ POT 频繁失败时评估。

### §4.24 Lévy-stable VaR/ES Horizon Correction——封闭形式厚尾传播（远期，2026-08-10 新增）

**方案**：[arXiv:2511.07834](https://arxiv.org/abs/2511.07834) Vlasiuk 2025-11 "Lévy-stable scaling of risk and performance functionals"（Columbia University）：

- **核心模型**：在数据驱动的 Lévy 窗口 `[τ_UV, τ_IR]` 内，收益服从 α-稳定分布（α ∈ (1,2)），尺度 τ^{1/α}；窗口外聚合为有限方差 √τ 体制。窗口边界和 α 从对数斜率+两段拟合识别
- **封闭形式公式**：以锚定 horizon τ₀ 为基准，VaR/ES/Sharpe/Kelly-under-VaR/drawdown 的 Lévy 传播与高斯传播的差异为显式偏差项 `(τ/τ₀)^{1/α} - (τ/τ₀)^{1/2}`——高斯假设的偏差可量化
- **实证验证**：Lévy 传播在窗口内跨 horizon 产生平坦的超限率（VaR/ES 覆盖率一致），高斯传播则随 horizon 偏离
- **非参数化**：仅需 α 和固定尾部分位数，无完整分布假设

**与本项目的关系**：
1. **与 §3.1 参数法的关系**：§3.1 参数法假设正态分布（α=2），Vlasiuk 提供厚尾（α<2）的封闭形式修正——`VaR_Lévy = VaR_Gaussian × (τ/τ₀)^{1/α - 1/2}`。当 A 股收益 α 估计 <2 时，参数法低估 VaR 的程度可量化
2. **与 §3.7 数据窗口的关系**：§3.7 使用 60 交易日历史模拟窗口。Vlasiuk 的 Lévy 窗口 `[τ_UV, τ_IR]` 提供窗口选择的**理论依据**——窗口应在 Lévy 稳定区间内，超出 τ_IR 后 √τ 聚合使历史模拟分位数偏向高斯
3. **与 §3.6 30 日波动率的关系**：§3.6 年化用 √252（高斯传播）。Vlasiuk 修正为 252^{1/α}——α<2 时年化因子更大，波动率低估程度可量化
4. **跨文档**：35号 §4.24 登记 Lévy-stable drawdown scaling（同一论文的 drawdown 公式），本节登记 VaR/ES 公式，两者同源

**远期登记理由**：
1. **α 估计需长样本**：α 从对数斜率识别需足够数据点覆盖多个 horizon，A 股短样本下 α 估计不稳定
2. **Lévy 窗口识别复杂**：需两段拟合 + 超越/红外截止点定位，工程化成本高
3. **Phase 2+ 评估**：当 §3.1 参数法频繁低估（回测超限率 >5%）且 A 股 α 估计稳定时，引入 Lévy 修正作为参数法增强

**轻量化提取价值**：Vlasiuk 的核心洞察"高斯传播 vs Lévy 传播的偏差 = `(τ/τ₀)^{1/α} - (τ/τ₀)^{1/2}`"可立即用于理解 §3.1 参数法在多日持有期下的低估趋势——持有期越长（T 越大），高斯假设的 √T 传播 vs Lévy 的 T^{1/α} 传播偏差越大。Phase 1 holding_period_days=1（日 VaR）时偏差最小，远期多日 VaR 需关注。

**不过度工程审查**：α 估计 + Lévy 窗口识别 + horizon 修正公式，需统计建模基础设施。Phase 2+ 参数法低估验证后评估。

### §4.25 Set-Preserving P2E Calibrator——p-value 到 e-value 桥接（远期，2026-08-10 新增）

**方案**：ICML 2026 [Alami, Zakharia, Ben Taieb "Set-Preserving Calibration from Conformal P-Values to E-Values"](https://icml.cc/virtual/2026/poster/62147)：

- **核心问题**：标准 conformal prediction 用 p-value，但 p-value 难以跨模型/数据分割合并依赖证据。e-value 公式化更适合组合，但 p→e 直接转换会改变预测集（set-altering），导致过度保守
- **P2E Calibrator**：提出新的 p-to-e 校准器，将 conformal p-value 转为 e-value **而不改变原始 p-value 诱导的预测集**（set-preserving）——保持 CP 的实际效率同时获得 e-value 理论的丰富性
- **应用**：cross-conformal prediction（CCP，变体仅提供近似 1-2α 覆盖）和 conformal aggregation（CA）——e-value 方法在两者中均满足 1-α 覆盖保证且提升效率

**与本项目的关系**：
1. **与 §3.9 回测验证的关系**：§3.9 MVP 4 法中 Kupiec/Christoffersen 是 p-value 检验，E-backtesting 是 e-value 检验。P2E Calibrator 提供**统一框架**——将 Kupiec/Christoffersen 的 p-value 转为 e-value 后可与 E-backtesting 的 e-process 统一合并，形成单一累积证据指标
2. **与 §4.14 E-backtesting v6 的关系**：§4.14 是 (VaR, ES) 专用的 e-backtest 最优构造。P2E Calibrator 可将传统 p-value 回测（Kupiec/Christoffersen）的输出"翻译"为 e-value，与 §4.14 的 e-process 对齐——实现"p-value 回测 + e-value 回测"的证据合并
3. **与 §4.22 Comparative E-backtests 的关系**：§4.22 的 comparative backtest 需多模型并行 e-backtest。P2E Calibrator 可将现有 p-value 回测结果转为 e-value 后纳入比较框架，降低比较 backtest 的工程化门槛（无需重写所有回测为 e-value 原生）
4. **多回测证据合并**：当前 §3.11 action 映射对 4 法回测结果分别判读（Kupiec reject / Christoffersen reject / Z2 / E-backtesting alert），P2E Calibrator 可将 4 法 p-value 统一转为 e-value 后合并——单一合并 e-process > 1/α 即拒绝，比"任一法 reject 即 RECALIBRATE"更精确（避免多检验多重比较问题）

**远期登记理由**：
1. **MVP 4 法分立判读已足够**：§3.11 action 映射对 4 法分别判读 + 取最严，Phase 1 生存底线已满足
2. **P2E 需 conformal prediction 基础设施**：本项目当前无 conformal prediction 管道（§4.14/§4.17 RWC 均远期），P2E 的前提条件未满足
3. **Phase 2+ 评估**：当 §4.14 E-backtesting v6 和 §4.17 RWC conformal 落地后，P2E Calibrator 作为"统一 p-value/e-value 回测框架"评估

**轻量化提取价值**：P2E 的核心洞察"多检验 p-value 直接合并会导致多重比较问题，e-value 合并提供更严格的证据累积"可立即用于 §3.11 回测解读——当前 4 法分别判读时，若 4 法中 2 法 p-value 略高于 0.05（边缘 PASS），不应视为"模型正确"（多重比较下联合证据可能已足够拒绝）。Phase 1 可在审计日志中标注边缘 PASS 的多重比较风险。

**不过度工程审查**：P2E 需 conformal prediction 管道 + e-value 合并算法，远超 Phase 1 预算。Phase 2+ conformal 落地后评估。

### §4.26 VaR/ES Forecast Combination via Model Confidence Set（MCS）——模型不确定性下的预报组合（远期，2026-08-10 新增）

**方案**：[arXiv:2406.06235v2](https://arxiv.org/abs/2406.06235) Amendola/Candila/Naimoli/Storti 2026 "Combining Value-at-Risk and Expected Shortfall forecasts via the Model Confidence Set"（International Journal of Forecasting, 2026）+ [arXiv:2508.16919v2](https://arxiv.org/abs/2508.16919) Taylor & Wang 2026-05 "Combining a Large Pool of Forecasts of Value-at-Risk and Expected Shortfall"（Oxford Saïd + Sydney）：

- **核心问题**：当前 §3.1 用 `max(parametric, historical)` 作 conservative_max——这是**最粗粒度的组合策略**（永远选更保守者，不管模型质量）。但 VaR/ES 预报受多重不确定性影响（模型误设/数据限制/估计程序/采样频率/regime 变化），**无单一模型在所有条件下一致最优**。取 max 忽略了模型间的互补性：参数法在平稳期准、历史模拟在厚尾期准，max 在平稳期过保守（浪费仓位）、在厚尾期恰好够（但不是因为选对了而是因为另一端更保守）

- **MCS 方法**（Amendola et al.）：
  1. **严格一致联合 VaR-ES 损失函数**（Fissler-Ziegel）：用同时评估 VaR 和 ES 的 strictly consistent loss 对候选模型打分
  2. **Model Confidence Set（MCS）**：对多模型做等价性检验（Hansen et al. 2003/2011），识别统计上不可区分的 **Set of Superior Models（SSM）**——SSM 内模型预测质量无显著差异
  3. **SSM 加权组合**：对 SSM 内模型的 VaR/ES 预报做加权组合（等权/性能加权/正则化加权），组合预报比任何单一模型更稳健
  4. **实证**：9 个股票指数 2.5%/1% 水平，组合预报通过标准回测且一致进入 MCS 的 SSM

- **大池组合方法**（Taylor & Wang）：
  1. **90 种预报方法池**：涵盖 GARCH/CAViaR/CARE/简单法（mean/median/mode）等
  2. **非性能组合**：trimmed mean（去极值后均值）、mixtures（推断概率分布后混合）
  3. **性能加权组合**：基于 Fissler-Ziegel 联合 score 的性能权重 + 正则化防过拟合
  4. **关键发现**：**仅 6 种多样性方法的小池 + 性能加权 > 90 种大池任意组合**——多样性比数量重要，6 种方法（覆盖不同方法论族）+ performance-based weighting 产生最优整体表现；trimmed mean 和 mixtures 方法也有强劲结果

**与本项目的关系**：

1. **与 §3.1 conservative_max 的关系**：`max(parametric, HS)` 是 MCS 组合的**退化特例**——当池中只有 2 个模型且权重为 {0,1}（赢者通吃）时等价于 max。MCS 组合是**有原则的推广**：用 Fissler-Ziegel 联合损失评估模型质量 → SSM 筛选 → 性能加权组合，替代 max 的"无脑选保守者"
2. **与 §3.9 回测验证的关系**：MCS 程序本身依赖回测损失函数（Fissler-Ziegel score），与 §3.9 的 4 法回测基础设施天然衔接——§3.11 var_backtester 已计算 Z2（Acerbi-Szekely）和 E-backtesting，Fissler-Ziegel score 是同族 strictly consistent loss，工程化复用度高
3. **与 §4.16 TailRisk-Trans / §4.17 ReSGA 的关系**：MCS 是**模型选择/组合层**，TailRisk-Trans/ReSGA 是**单一模型层**。远期若引入深度学习 VaR/ES 模型，MCS 提供将其与传统模型组合的框架——避免"全押新模型"风险
4. **与 §4.22 Comparative E-backtests 的关系**：§4.22 做模型间比较（内部 vs 监管标准），MCS 做模型间等价性检验+组合——两者互补：comparative backtest 判"谁更好"，MCS 判"谁不可区分"并组合不可区分者

**远期登记理由**：

1. **MVP 仅 2 法（参数法+历史模拟）**：MCS 需 ≥3-4 个候选模型才有意义（2 个模型 SSM 退化为一对一比较）。Phase 2 引入 FHS + 蒙特卡洛后（4 法），MCS 才有足够候选池
2. **Taylor & Wang 实证启示**：6 种多样性方法 + 性能加权最优——本项目 Phase 2 有 4 法（参数法/HS/FHS/MC），Phase 3 可引入 CAESar/QbSD 达 6 法，此时 MCS 组合效益最大化
3. **工程化成本**：Fissler-Ziegel 联合损失计算 + MCS p-value 检验程序 + 滚动窗口性能加权——约 200-300 行 Python，依赖 scipy.stats（已有），无第三方库
4. **与 §3.1 max 的兼容性**：MCS 组合是 max 的严格推广——MCS 落地后 `method` 配置从 `conservative_max` 扩展为 `conservative_max | mcs_combination | performance_weighted`，`conservative_max` 作为 fallback 保留

**轻量化提取价值**（Phase 1 可立即用的洞察）：

- **max 的认知偏差修正**：当前 §3.1 选型理由#1 说"取 max 确保两者中更保守的胜出"——MCS 研究表明这**不总是最优**：在平稳期 max 过保守（参数法在正态下准但 max 选了 HS 的更保守值→浪费仓位），在厚尾期 max 恰好够但是因为 HS 更保守而非 HS 更准。Phase 1 可在审计日志中记录两法分叉度 `divergence = |VaR_param - VaR_hist| / VaR_95`，分叉度持续 >20% 时标记 MODEL_DIVERGENCE_HIGH 供 Phase 2 MCS 评估
- **Taylor & Wang 多样性原则**：6 法多样性 > 90 法数量——指导 Phase 2/3 模型引入策略：优先引入**方法论多样性**（参数法→半参数法→非参数法→深度学习）而非同类方法堆砌

**不过度工程审查**：MCS 需 ≥4 候选模型（Phase 2 后满足）+ Fissler-Ziegel 损失 + MCS 检验程序 ~300 行，在 Phase 2 预算内。Phase 1 不改动 conservative_max。

### §4.27 Information-Geometric Bayesian 风险监控（远期，2026-08-10 新增）

**方案**：[arXiv:2608.01294v1](https://arxiv.org/abs/2608.01294) Quirini 2026-08-04 "An Information-Geometric Framework for Bayesian Credit Risk Monitoring"（q-fin.RM）——用信息几何（Fisher 度量 / KL 散度 / 统计流形上的测地线）构建贝叶斯风险监控框架。将违约率后验分布视作统计流形上的点，用测地距离衡量 regime 变化、用曲率识别风险集中区，提供在线更新和异常报警机制。

- **核心方法**：
  1. **后验分布→流形映射**：将策略 PnL（或违约率）的贝叶斯后验分布参数化（如 Beta/Normal-Inverse-Gamma），映射到统计流形上的一个点
  2. **Fisher 信息度量**：用 Fisher 信息矩阵定义流形上的 Riemannian 度量，衡量参数空间各方向的"信息量"
  3. **测地距离 regime 检测**：两个后验分布（校准期 vs 当前期）的测地距离 > 阈值 → regime 切换信号。测地距离优于 KL 散度——KL 非对称且不满足三角不等式，测地距离是对称度量
  4. **曲率→风险集中**：流形曲率高的区域 = 后验不确定性集中 = 风险集中区，曲率突变预警尾部风险聚集
  5. **在线更新**：每新观测一笔 PnL，贝叶斯更新后验 → 重新映射流形点 → 计算测地漂移 → 滚动监控

- **与本项目的关系**：
  1. **与 §3.11 VaR 校准触发的关系**：当前 VaR 校准是**周期性**的（§3.11 按日/周固定 schedule）+ **违规驱动**的（Christoffersen/Kupiec 失败触发 RECALIBRATE）。信息几何提供**第三种触发**：测地距离漂移触发——后验分布在流形上"移动"超阈值即触发校准，比周期性更及时（regime 切换当天即触发）比违规驱动更早（违规是事后，测地漂移是事前分布变化）
  2. **与 §3.6 漂移检测的关系**：§3.6 用 PSI/KS/MMD/CUSUM 检测输入漂移——这些是**欧氏空间**统计量。信息几何是**流形空间**度量，对分布形状变化（不仅是均值/方差漂移）更敏感——高阶矩变化（偏度/峰度漂移）在欧氏统计量中可能不显著但在测地距离上显著
  3. **与 §4.17 ReSGA 的关系**：ReSGA 按特征相似性分组+组内联合预测（横截面分组），信息几何按后验分布测地距离监控（时序分布漂移）——二者正交，远期可组合
  4. **与 10 号 regime 检测的关系**：10 号 regime 检测是显式状态识别（HMM/HSMM 标签），信息几何是隐式分布漂移监控（无显式状态标签，只报"分布变了"）——信息几何更轻量（无状态数选择/无 EM 收敛问题），但解释性差（不告诉"变成了什么 regime"只告诉"变了"）

- **A 股适用性评估**：中低。论文以信用风险（违约率 Beta 分布）为载体，迁移到 A 股 PnL 监控需：① PnL 分布参数化（Normal-Inverse-Gamma 或 Student-t 族）② Fisher 度量解析推导（需分布族的 Fisher 矩阵闭式解，非所有分布族可得）③ 测地线数值计算（流形上测地线通常无解析解，需数值 ODE 求解）。A 股 PnL 厚尾+时变波动率+ regime 切换频繁，后验分布族选择是关键难点

- **轻量化提取价值**（Phase 1-2 可立即用的洞察，无需完整信息几何框架）：
  - **KL 散度漂移监测**：测地距离的**一阶近似**是 KL 散度（Jeffreys 散度 = (KL(P‖Q)+KL(Q‖P))/2 对称化）。Phase 2 可用对称 KL 散度作 PnL 分布漂移监测的轻量替代——无需 Fisher 矩阵/测地线 ODE，仅用 scipy.stats.entropy 计算滚动窗口 PnL 分布 vs 校准期分布的对称 KL，超阈值触发 VaR 校准审查。这是信息几何框架的"平民版"实现
  - **分布形状变化>均值变化的认知**：信息几何的核心洞察是"分布形状变化（偏度/峰度/尾部）比均值变化更值得关注"——Phase 1 可在 §3.6 漂移检测中增加偏度/峰度漂移监控（滚动窗口偏度/峰度 vs 校准期，超 2σ 触发 SHAPE_DRIFT 标志），作为 PSI/KS 的形状维度补充

- **过度工程审查**：**Phase 4+ 远期登记，远超个人系统 Phase 1-3 预算**。完整信息几何框架需：①微分几何背景知识（Fisher 度量/测地线/Riemannian 流形）②数值测地线计算（scipy ODE solver 或 pymanopt 优化库）③分布族 Fisher 矩阵解析推导（研究密集型）④参数化选择敏感性分析。与项目记忆"Mamba/SSM 被评估为过度工程远期不采纳"同类——学术优雅但工程成本远超收益。**Phase 4 鲁棒性阶段**若 §3.6 漂移检测 + §3.11 校准触发 + §4.14 e-backtesting 三层仍无法捕捉某些 regime 切换（分布形状突变），才评估完整信息几何框架。Phase 1-2 仅采纳上述"轻量化提取价值"（对称 KL 散度 + 偏度/峰度漂移监控），<30 行代码无第三方库

- **定位**：Phase 4+ 远期候选（完整框架），Phase 2 轻量提取（对称 KL 散度漂移 + 形状漂移监控）

### §4.28 Geodesic Execution Slippage——Fisher 流形测地滑点预测与早期告警（远期，2026-08-10 新增）

**方案**：Entropy 2026, 28(6), 705；[DOI:10.3390/e28060705](https://doi.org/10.3390/e28060705)（preprint [arXiv:2605.0757](https://arxiv.org/abs/2605.0757), 2026-05-12）"Geodesic Execution Slippage: A Statistical Physics Framework for Cryptocurrency Liquidity Risk"，Ntebogang Dinah Moroke / Lebotsa Daniel Metsileng。

- **核心方法**：用**统计物理框架**替换 flat-fee 执行成本模型——执行滑点 = **Markov-switching GARCH 最大熵模型 Fisher 信息流形上的测地弧长**（geodesic arc length）。同一参数向量派生**联合曲率-拓扑碎片化告警**（curvature + TDA 拓扑数据分析）：
  1. **Fisher 信息流形**：将 MS-GARCH 最大熵模型的参数空间视作 Riemannian 流形，Fisher 信息矩阵定义度量
  2. **测地弧长 = 执行滑点**：参数轨迹在流形上的测地弧长度量执行成本——比 flat-fee / 线性冲击模型更准确捕捉流动性状态的非线性变化
  3. **联合曲率-拓扑碎片化告警**：流形曲率突变 + TDA 持续同调拓扑特征变化 → 联合触发流动性危机早期告警
- **消融实验**：移除 geodesic 项 MSE +2.9%；移除 TDA +2.1%；移除曲率 +1.5%；无子集匹配完整框架——三组件协同不可拆
- **实证**：5 加密市场（BTC/ETH/XRP/LTC/BCH）+ 2,253 日观测——全部 5 资产最低预测误差；10% 显著性下 **Model Confidence Set（MCS）唯一保留模型**（对比 Amihud / Kyle λ / Almgren-Chriss 等 6 基线）
- **关键洞见**：联合曲率-拓扑告警在 4 次危机（含 Terra 2022-05 / FTX 2022-11）中**中位数提前 2 天**触发，早于价格型 circuit breaker 阈值——直接服务于 35 号回撤 Protocol 的早期预警
- **不需额外数据或自由参数**（除上游 MS-GARCH 估计管线）

**与本项目的关系**：
1. **与 36 号 + 35 号的关系**：本节是"执行成本预测 + 危机早期告警"层——连接 **36 号风险监控 → 35 号回撤 Protocol 触发**。36 号 VaR/ES 监控管"组合风险多少"（事后度量），本节管"流动性危机将临"（事前告警），告警信号可喂入 35 号回撤 Protocol 作为 circuit breaker 之外的早期触发源
2. **与 §4.27 Information-Geometric Bayesian 的关系**：§4.27 用 Fisher 度量做**风险监控**（后验分布漂移），本节用 Fisher 度量做**执行成本预测**（参数轨迹测地弧长）——同一数学工具（Fisher 信息流形）的不同应用：§4.27 监控分布形状漂移，§4.28 度量流动性状态距离
3. **与 §3.5 / §3.14 触发的关系**：当前 §3.5 5 级分级 + §3.14 BlackSwanSignal 是价格/事件驱动；本节提供流形拓扑驱动的第三类触发源（提前 2 天级）

**A 股适用性评估**：中。论文在加密市场验证（24h 交易），A 股无 24h 交易但 **Markov-switching GARCH 通用**（regime 切换模型与交易时段无关）。迁移需：① A 股 PnL/成交滑点序列的 MS-GARCH 估计 ② Fisher 矩阵数值计算 ③ TDA 持续同调（需 gudhi/ripser 等拓扑库）。盘中集合竞价跳空 + 涨跌停限制可能影响滑点结构，需 A 股特化校准

**伪代码**（Fisher 度量计算 + 测地弧长 + 曲率-拓扑告警简化版，<50 行；需上游 MS-GARCH 估计管线）：

```python
import numpy as np
# Geodesic Execution Slippage 简化框架（需上游 MS-GARCH 估计）

def fisher_metric(params, returns, regimes):
    """MS-GARCH 参数空间 Fisher 信息矩阵（数值近似：I ≈ E[gg^T]）"""
    def loglik(theta):
        return ms_garch_loglik(theta, returns, regimes)
    eps = 1e-5
    g = numerical_grad(loglik, params, eps)   # 得分向量
    return np.outer(g, g)

def geodesic_arc_length(theta_s, theta_t, fisher_fn, n=20):
    """参数轨迹测地弧长 ≈ 执行滑点预测（一阶线性近似数值积分）"""
    path = np.linspace(theta_s, theta_t, n)
    arc = 0.0
    for i in range(n - 1):
        d = path[i+1] - path[i]
        I_mid = fisher_fn(0.5 * (path[i] + path[i+1]))
        arc += np.sqrt(max(d @ I_mid @ d, 0.0))
    return arc

def curvature_topology_alert(win, base_I, base_betti, tda_fn):
    """联合曲率-拓扑碎片化告警（危机早期预警，中位数提前 2 天 vs circuit breaker）"""
    I_now = fisher_metric(current_params, win, current_regimes)
    curvature = np.trace(I_now) / max(np.trace(base_I), 1e-9)  # 曲率相对基线放大
    betti_now = tda_fn(win)                                     # TDA 持续同调 Betti 数
    betti_delta = sum(abs(betti_now[k] - base_betti.get(k, 0))
                      for k in set(betti_now) | set(base_betti))
    alert = (curvature > 2.0) and (betti_delta > 1)            # 联合触发
    return {"alert": alert, "curvature": curvature, "betti_delta": betti_delta,
            "slippage_forecast": geodesic_arc_length(prev_params, current_params, fisher_metric)}
```

**过度工程审查**：Phase 5+ 远期登记，远超个人系统 Phase 1-3 预算。完整框架需：① MS-GARCH regime 估计管线 ② Fisher 矩阵数值计算 ③ 测地线数值积分 ④ TDA 持久同调库（gudhi/ripser）。与 §4.27 同类过度工程（微分几何背景+研究密集型），但提供了 circuit breaker 之外的"提前 2 天"早期告警能力——若 Phase 4 §3.6 漂移检测 + §3.14 BlackSwanSignal 仍无法足够提前捕捉流动性危机，Phase 5+ 评估本框架。Phase 1-2 不采纳，仅登记诚实账本

**定位**：Phase 5+ 远期候选（需 Fisher 流形估计基础设施 + TDA 工具栈；与 §4.27 共享微分几何/数值测地线工具栈，但 §4.28 额外需 TDA 持续同调库）；加密市场已验证，A 股适用性需评估

## 5. 上限定义

### 5.1 系统上限

| 维度 | 上限 | 理由 |
|---|---|---|
| VaR 方法 | 参数法 + 历史模拟（取 max） | Phase 1，蒙特卡洛/GARCH 远期 |
| ES 方法 | 历史模拟 + POT | 联合动态估计远期 |
| 回测方法 | 4 法 MVP（15 法框架） | 11 法远期 |
| 黑天鹅模式 | 7 模式 | 框架固定 |
| 系统性风险级别 | 5 级 | 框架固定 |
| 数据窗口 | 60 交易日（回测 250） | A 股平衡稳定性与时效性 |
| 盘中重算频率 | 事件驱动（7 条触发） | 非定时轮询 |

### 5.2 演进路径

> v1.9.0 补：演进路径与 §4.1-§4.27 全量对齐——此前 §5.2 仅列代表性方法，§4.8/§4.11-§4.14/§4.16-§4.20/§4.27 共 11 项远期登记未在路径中体现。本次按"风险度量族 / 回测族 / conformal 族 / 深度学习族 / 半参数族 / 审计族"六类重组，确保每项 §4.x 远期登记可追溯到 Phase。

```
Phase 1 (当前): 参数法 + 历史模拟 + POT + 4 法回测 + 5 级 + 7 黑天鹅
    ↓
Phase 2 (远期):
  ├─ 风险度量族: + FHS + 蒙特卡洛 + Vol-Targeting
  ├─ conformal 族: + Conformal (RWC/TWC) + Fuzzy CP Sets (§4.13) + 自适应 conformal 组合选择 (§4.19)
  ├─ 回测族: + 11 法回测（v1.11.0 同步：13→15 法框架）
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
- §4.21 CVaR Q-Learning：RL 风险感知训练（属 alpha 层训练，非监控层；v1.10.0 补全 6 协同机制+Bellman 残差 -85% 实证+OOS Sharpe 0.9281+伪代码+§4.27 关系，Phase 4 鲁棒性阶段）
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
| RiskOrchestrator 编排角色施工（v1.11.0 新增） | 设计态角色，src 零命中；35号/36号双侧伪代码均以其为编排者 | 35号 state_store 就绪 + 5 流程闭环联调 |
| 30 日波动率调整斜率校准（v1.11.0 新增） | §3.6 斜率来源单一（LedgerMind 2026-05），未 A 股实证 | G04 首批策略 50+ trades 后校准 |
| 5 级 position_cap 非单调（YELLOW 0.5 < ORANGE 0.7）语义裁定（v1.11.0 新增） | 代码与 §3.5.1 一致但非单调：YELLOW cap 比 ORANGE 更严，疑语义本为"新开仓增量减半"而非"总仓位上限" | 业主裁定后同步代码+文档（越界 §6.1 #4） |

### §6.1 跨文档同步登记（越界事项，不在本号修改）

| # | 事项 | 位置 | 建议处理 |
|---|---|---|---|
| 1 | MOD-RK-05B 注册表缺口 | blueprint/module_translation/path_ownership/capability_canonical 4 个 yaml | 补登记 |
| 2 | 00_index 36号版本漂移 | 00_index L57/L604 登记 v1.8.0 | 更新为 v1.11.0 |
| 3 | 32号两处错误引用 | 32_firm_risk_aggregator.md "36号 §4.13 MFCCA" | 改为 §4.6 |
| 4 | drawdown_controller 5 级 cap 非单调 | src drawdown_controller.py `_RISK_LEVEL_CAP` | 业主裁定后修代码 |
| 5 | 32号消费本号产出契约 | 32_firm_risk_aggregator.md | 32号落地时补契约表 |

## 7. 待定问题（讨论要点）

以下来自 00_index §3 G17 讨论要点，已逐项对齐落入 §3 决策。

- [x] ① VaR_95 计算（历史模拟/参数法）→ §3.1 取 max
- [x] ② ES_95 计算 → §3.2 历史模拟 + POT
- [x] ③ 入场 VaR/ES 基准 → §3.4 开仓日盘前快照
- [x] ④ 触发动作（VaR>1.2×减仓20%/ES>1.3×再减20%）→ §3.5 5 级系统性风险 + BlackSwanSignal API（v1.11.0 注：30号 §2.5.4 相对触发已由绝对 5 级阈值替代，相对恶化检测 relocated 至 35号 §3.16 归因 1.5×，替代裁决见 §3.5 双注解）
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
- `src/zephyr/risk/core/var_backtester.py` v0.1.0（MOD-RK-05B；⚠️ 注册表未登记 → §6.1 #1）
- `src/zephyr/risk/core/daily_auditor.py` v0.1.0（MOD-RK-20；⚠️ v1.11.0 校正：run_var_backtest 等设计态待施工）
- `src/zephyr/position/core/drawdown_controller.py` v0.1.0（MOD-POS-008；⚠️ var_breach_state/force_static_mode 设计态 → §3.20.4）
- [31_position_sizing](31_position_sizing.md) §2.3.3（单标的级前瞻 VaR/CVaR，与本号组合级正交 → §3.20.6）
- [32_firm_risk_aggregator](32_firm_risk_aggregator.md)（firm 层聚合，EVT 监控信号消费契约待显式化 → §6.1 #5）
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
- ICML 2026 Alami/Zakharia/Ben Taieb Set-Preserving Calibration from Conformal P-Values to E-Values（→ §4.25）
- arXiv:1611.04851 Kratz/Lok/McNeil Multinomial VaR Backtests（→ §3.9.2 第 15 法；v1.11.0 新增）
- SSC 2026-06 Lu/Sullivan/Hurlin Bivariate Orthogonal Polynomials ES 回测（→ §3.9.2 第 14 法 + §4.11；v1.11.0 补登入表）

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
- arXiv:2508.16919v2 Taylor & Wang 2026-05 "Combining a Large Pool of Forecasts of VaR and ES"

#### 半参数分位数动态

- arXiv:2603.02357 Liu & Luger 2026-03 Quantile-based modeling of scale dynamics（QbSD）（→ §3.16；v1.11.0 补来源）
- arXiv:2505.05646 Xin 2025-05 VaR 三法对比（HS/GARCH-N/GARCH-FHS）（→ §3.1 佐证 #6；v1.11.0 新增）

#### 监管

- CP9/26 PRA IMA（2026-06-19：go-live 2028-01-01；PLAT 3 年过渡；RFET 24→16；v1.11.0 更新）
- US Basel III Endgame 修订提案（Fed/OCC/FDIC 2026-03-19：取消 dual stack → SA as IMA cap；v1.11.0 更新）
- EU CRR III FRTB 推迟 2027-01 + 临时乘数咨询（v1.11.0 新增）
- FSB 2026-06-10 AI 稳健实践咨询报告

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G17 讨论要点占位 |
| 2026-08-10 | 1.0.0 | 骨架→active 重建 | v1.29.x 内容因工作树还原丢失（未提交即被还原，不在任何悬空 blob/不可达 commit/stash 中），从源码实现（var_calculator/tail_risk_monitor/var_backtester/daily_auditor/drawdown_controller）+ 30号 §2.5.4 框架 + 35号跨文档契约重建为 active v1.0.0。核心决策 16 节 + 替代方案 10 节（含 2026-08-10 全网最新搜索新增 3 篇：arXiv:2608.07113 OCE Risk Minimization、arXiv:2608.07122 Lambda-quantiles、arXiv:2608.02854 Preference-robust distortion）+ 30+ 篇 2026-08 研究远期登记 |
| 2026-08-10 | 1.1.0 | §3.14-§3.19 跨文档协同补全（D3/D4/D6/D9/D10 + E1/E2/E3 修复）——补登 | 与 35号 v1.31.0 跨文档流程交接链修复同步。**D3** §3.15 VarBreachStateMachine 跨重启持久化（VarBreachStateSnapshot + save/load）；**D4** §3.15 与 35号回撤状态机协同（var_breach_state 参数 + 乘性折扣表 NORMAL×1.0/BREACHED×0.8/RECOVERY×0.9）；**D6** §3.14 black_swan_detector 模块归属（MVP RiskOrchestrator 聚合 / 远期独立模块）+ 7 类 BlackSwanMode MVP 事件源映射表；**D9** §3.18 盘后状态持久化流程（7 阶段伪代码 + §3.19 配对约束表）；**D10** §3.19 盘前初始化流程（加载顺序 + 冷启动守卫）。**E1** §3.18 盘后持久化顺序明确（daily_auditor.audit()→35号§3.18→36号§3.18，35号审计失败则36号不执行）；**E2** §3.18 状态值配对（36号 "VAR_COMPLETE" vs 35号 "DRAWDOWN_COMPLETE" 双阶段标记）；**E3** §3.15 双 RECOVERY 叠加逻辑澄清（effective_cap = 阶梯值×0.9 + 下限保护 max(0.0) + DUAL_RECOVERY_PROLONGED >20日告警）|
| 2026-08-10 | 1.2.0 | §4.15 Ye et al. 2026-08-06 Finite-Sample Conformal Risk Bounds for Joint VaR/ES + §4.16 TailRisk-Trans Transformer-based 动态 VaR/ES 远期登记 | 持续改进：用户要求再次审查文档所有内容+选项之外更好算法+全网搜索 2026-08-08 最新研究+持续改进不停。全网搜索发现两篇 2026-08 最新研究——① [MDPI Mathematics 14(15):2847](https://www.mdpi.com/2227-7390/14/15/2847) Ye/Qiu/Zhu/Ladikas 2026-08-06 "Finite-Sample Conformal Risk Bounds for Joint VaR/ES Forecasting Under Non-Exchangeable Financial Time Series"：金融尾部风险观测非可交换（serial dependence + regime shifts），ES 不可独立 elicitable，方法 tune a single inflation parameter by conformal risk control on bounded monotone loss coupling VaR breach frequency with breach magnitude normalized by VaR-ES gap，交换性下有限样本期望风险控制，非可交换下 non-exchangeable swap-distance bound + regime-drift bound；② [Frontiers in Business and Finance Vol 3 Issue 1](https://sprcopen.com/index.php/FBF/article/download/742/641/1991) Wang & Bai 2026 "TailRisk-Trans"：4 组件 Transformer（金融数据预处理+Market Transformer Encoder+Tail-Risk Prediction Head 联合 VaR/ES/CVaR+Extreme-Event-Aware Attention），可微分分位数回归层，99% VaR violation rate 4.12%→3.47%（15.8% 改进）。两篇均远期登记 Phase 3+，MVP 不改动现有 conservative_max + POT 双轨架构 |
| 2026-08-10 | 1.3.0 | §4.17 新增 ReSGA 检索增强自分组自编码器尾部风险大模型（arXiv:2606.04576）远期登记 | 全网搜索 2026-08 最新研究，发现 ReSGA（港大+厦门大学，百万参数级检索增强自分组自编码器）尚未在本号登记。ReSGA 按特征相似性将资产分组后组内联合预测 VaR/ES，关键发现"数据复杂度比模型复杂度更重要"。远期登记 Phase 3+，轻量化提取价值：按特征相似性分组+组内联合估计可在 Phase 2 作为轻量增强（<50 行代码无需 GPU）。与 §4.16 TailRisk-Trans 正交（横截面 vs 时序），远期可组合。同步更新 00_index 36号版本 v1.2.0→v1.3.0 |
| 2026-08-10 | 1.4.0 | 施工流程算法完整性审查 + 17 项缺失/不一致修复 + §4.18-§4.20 三篇 2026-08 新研究登记 | 持续改进：用户要求再次审查文档所有内容+施工环节流程算法缺失+选项之外更好算法+全网搜索 2026-08-08 最新研究+文档结构顺序内容调整+持续改进不停。施工流程算法完整性深度审查发现 17 项缺失/不一致——**HIGH**：①§9 修订记录缺 v1.2.0 条目（§4.15/§4.16 新增未登记，已补登）；②回测样本不足处理完全未定义（已补 §3.10 样本不足阈值+降级策略+冷启动期处理）；③§3.16 QbSD 施工规约严重缺失仅 2 行（已补触发条件+算法概要+与 MVP 关系）；④§3.11 action 映射与 §3.10 定级矩阵不一致（Christoffersen LR_ind reject 未纳入 RECALIBRATE 判定，已修复）。**MEDIUM**：⑤§3.12 多触发条件优先级/去重/防抖未定义（已补）；⑥§3.12 取最严比较维度未定义（已补 position_cap 取 min）；⑦§3.13 T+1 约束对 clean/dirty P&L 影响未处理（已补）；⑧§3.14 BS-007→kill_switch_advised 映射规则未明确（已补）；⑨§3.16 FHS 切换失败无冷却期可能抖动（已补）；⑩§3.19 静态映射 entry_var=None 边界未覆盖（已补）；⑪§3.19 首次启动日无 premarket_baseline 降级策略未定义（已补）；⑫POT 日常计算失败兜底未明确（已补 §3.2 交叉引用）。**新增研究**：§4.18 D'Innocenzo et al. 2026 JBES 单整合尾形参数动态 VaR/ES + §4.19 Jia & Han 2026 自适应 conformal 组合选择 + §4.20 Fu 2026-01 动态因子半参数 VaR/ES（realized measures）。同步更新 00_index 36号版本 v1.3.0→v1.4.0 |
| 2026-08-10 | 1.5.0 | §9 补登 v1.1.0 + §4.22 新增 comparative e-backtests + §8.2 补 Xin 两步波动率 + §1 状态行版本漂移修复 + frontmatter v1.5.0 | 持续改进：用户要求再次审查文档所有内容+施工环节流程算法缺失+选项之外更好算法+全网搜索 2026-08-08 最新研究+文档结构顺序内容调整+持续改进不停。**一致性审查 4 项修复**：①§9 修订记录缺 v1.1.0 条目（§3.14-§3.19 的 D3/D4/D6/D9/D10 + E1/E2/E3 修复均标注 v1.1.0/v1.1.1 但 §9 跳过，已补登）；②§1 状态行版本漂移（frontmatter v1.4.0 但 §1 仍写 v1.0.0，已修复为 v1.5.0）；③§8.2 有 arXiv:2511.05840 引用但无对应 §4.x 替代方案节（结构不一致，已补 §4.22 + 交叉引用）；④§8.2 波动率与 Vol-Targeting 缺 A 股实证参考（已补 Xin 2026-04 沪深300ETF期权两步波动率）。**新增研究**：§4.22 Jiao/Wang/Zhao arXiv:2511.05840 "Standard and comparative e-backtests for general risk measures"——标准 e-backtest 从 (VaR,ES) 扩展到任意 identifiable risk measure + comparative backtest（内部模型 vs 监管标准模型双向检验）+ expectile 首次 model-free e-backtest，填补 §4.3 EVaR 回测缺口 + §4.14 E-backtesting v6 通用化泛化。**全网搜索 2026-08-08~10 结论**：arXiv q-fin.RM 截至 8/6 最新 listing 已全覆盖，36 号 5 流程闭环无缺失独立环节，§4.1-§4.22 共 22 节替代方案远期登记闭合。同步更新 00_index 36号版本 v1.4.0→v1.5.0 |
| 2026-08-10 | 1.6.0 | §4.23 DMM VaR Bracketing + §4.24 Lévy-stable VaR/ES Horizon Correction + §4.25 P2E Calibrator 新增 + §5.2 演进路径更新 + §8.2 学术引用 3 篇新增 + frontmatter v1.6.0 | 持续改进：用户要求再次审查文档所有内容+施工环节流程算法缺失+选项之外更好算法+全网搜索 2026-08 今天最新研究+文档结构顺序内容调整+持续改进不停。全网搜索 2026-08-10 arXiv q-fin.RM/q-fin.PM 最新研究 3 篇新增：①§4.23 [arXiv:2601.09927](https://arxiv.org/abs/2601.09927) Aditri 2026-01 DMM VaR Bracketing——矩约束稳健尾部替代，IS vs DMM 效率-稳健权衡，POT 拟合失败时第三条路径；②§4.24 [arXiv:2511.07834](https://arxiv.org/abs/2511.07834) Vlasiuk 2025-11 Lévy-stable scaling——封闭形式 VaR/ES/drawdown horizon 修正，偏差项 (τ/τ₀)^{1/α}-(τ/τ₀)^{1/2}，参数法正态假设低估可量化，跨文档 35号 §4.24 drawdown 公式同源；③§4.25 ICML 2026 Alami et al. P2E Calibrator——p-value→e-value 桥接（set-preserving），多回测证据合并统一框架，填补 Kupiec/Christoffersen(p-value) 与 E-backtesting(e-value) 的割裂。§5.2 演进路径 Phase 2 增 P2E、Phase 3 增 DMM+Lévy-stable+Comparative e-backtests。§8.2 新增"Lévy-stable 厚尾传播"引用分类。施工算法完整性结论：36号 5 流程闭环无缺失独立环节，§4.1-§4.25 共 25 节替代方案远期登记闭合。同步更新 00_index 36号版本 v1.5.0→v1.6.0 |
| 2026-08-10 | 1.7.0 | §4.26 VaR/ES Forecast Combination via MCS 新增 + §5.2 演进路径 Phase 2 增 MCS + §8.2 新增"预报组合"引用分类 + §1 状态行更新 + frontmatter v1.7.0 | 持续改进：用户要求再次审查文档所有内容+施工环节流程算法缺失+选项之外更好算法+全网搜索 2026-08 今天最新研究+文档结构顺序内容调整+持续改进不停。全网搜索发现 §3.1 conservative_max（取 max）的"选项之外更好算法"——[arXiv:2406.06235v2](https://arxiv.org/abs/2406.06235) Amendola et al. 2026（Int. J. Forecasting）MCS-based VaR/ES forecast combination + [arXiv:2508.16919v2](https://arxiv.org/abs/2508.16919) Taylor & Wang 2026-05（Oxford+Sydney）large pool combination。核心洞察：max 是 MCS 组合的退化特例（2 法权重{0,1}赢者通吃），MCS 用 Fissler-Ziegel 联合损失评估模型质量→SSM 筛选→性能加权组合，替代 max 的"无脑选保守者"；Taylor & Wang 实证"6 法多样性小池+性能加权 > 90 法大池任意组合"。Phase 1 轻量提取：审计日志记录两法分叉度 divergence=\|VaR_param-VaR_hist\|/VaR_95，持续>20% 标记 MODEL_DIVERGENCE_HIGH 供 Phase 2 MCS 评估。Phase 2 远期：≥4 法候选池（参数法/HS/FHS/MC）后 MCS 落地替代 max，method 配置扩展 conservative_max\|mcs_combination\|performance_weighted。§4.1-§4.26 共 26 节替代方案远期登记。施工算法完整性结论：36号 5 流程闭环无缺失独立环节，本次为 §3.1 max 的"选项之外更好算法"远期登记非施工算法缺失 |
| 2026-08-10 | 1.8.0 | §4.27 Information-Geometric Bayesian 风险监控新增（arXiv:2608.01294，全网搜 2026-08 唯一未收录新论文）+ §1 状态行 26→27 节 + frontmatter v1.8.0 | 持续改进：用户要求"再次审查文档所有内容+施工环节流程算法有缺失+选项之外更好的答案算法+全网搜 2026年8月今天最新研究+文档结构顺序内容调整+持续改进不要停下来询问"。后台 agent 全网搜 2026-08 最新量化算法返回 5 领域 15 篇候选论文，交叉验证（grep 全 design_memos 目录）确认 14 篇已收录（DASC/Conditional CTM/Changepoint/MPC/Microstructure/Diffusive/CVaR Tail/Three Matrices/EFS/Alpha Decay/FactorEngine/Unstructured Regime/MS-GARCH/Wasserstein HMM），**仅 arXiv:2608.01294 Information-Geometric Bayesian 未收录**。决策：§4.27 新增 Quirini 2026-08-04 信息几何贝叶斯风险监控框架（Fisher 度量/KL 散度/统计流形测地距离 regime 检测 + 曲率风险集中识别）。与本项目关系：①§3.11 VaR 校准第三种触发（测地距离漂移，比周期性及时比违规驱动早）；②§3.6 漂移检测的流形空间补充（欧氏 PSI/KS vs 流形测地距离，对高阶矩漂移更敏感）；③与 10 号 regime 检测正交（隐式分布漂移 vs 显式状态标签）。A 股适用性中低（需分布族 Fisher 矩阵解析推导+数值测地线 ODE）。过度工程审查：**Phase 4+ 远期登记，与 Mamba/SSM 同类过度工程**（微分几何背景+数值测地线+研究密集型），Phase 1-2 仅采纳轻量化提取（对称 KL 散度漂移监测 scipy.stats.entropy + 偏度/峰度形状漂移 SHAPE_DRIFT 标志，<30 行无第三方库）。§4.1-§4.27 共 27 节替代方案远期登记。施工算法完整性结论：36号 5 流程闭环无缺失独立环节，本次为全网搜唯一新论文远期登记非施工算法缺失。同步 54号 v1.14.0 新增 §3.14 MCR/CCR 风险分解（与 36号 VaR 监控正交：36号管"组合风险多少"54号管"谁贡献了风险"） |
| 2026-08-10 | 1.9.0 | §5.2 演进路径与 §4.1-§4.27 全量对齐——11 项远期登记缺口补全 + 六类族重组 + 5 项正交定位澄清 | 持续改进：用户要求"再次审查文档所有内容+施工环节流程算法有缺失+选项之外更好的答案算法+全网搜 2026年8月今天最新研究+文档结构顺序内容调整+持续改进不要停下来询问"。文档结构一致性审查发现 §5.2 演进路径与 §4.x 替代方案存在同步缺口——此前 §5.2 仅列代表性方法（Phase 2: FHS/MC/Vol-Targeting/Conformal/9法/P2E/MCS；Phase 3: QbSD/CAESar/Bayesian EVT/EVaR/OCE/Lambda/DMM/Lévy/Comparative e-backtests），但 §4.8/§4.11-§4.14/§4.16-§4.20/§4.27 共 11 项远期登记未在路径中体现（§4.8 Preference-Robust Distortion / §4.11 Bivariate Polynomials ES 回测 / §4.12 ERCIM 145 e-values 审计 / §4.13 Fuzzy CP Sets / §4.14 E-backtesting v6 GRO/GREE/GREL / §4.16 TailRisk-Trans / §4.17 ReSGA / §4.18 D'Innocenzo / §4.19 Jia&Han / §4.20 Fu / §4.27 Information-Geometric）。本次按"风险度量族/回测族/conformal 族/深度学习族/半参数族/审计族"六类重组 Phase 2/3/4+ 路径，确保每项 §4.x 远期登记可追溯到 Phase；新增"不在 VaR/ES 演进路径的 §4.x 项"小节澄清 5 项正交定位（§4.5 Phase 4+ 鲁棒性 / §4.6 regime 检测登记 35号 / §4.9 组合配置层 / §4.15 理论界证明 / §4.21 RL alpha 层）。**施工算法完整性结论**：36号 5 流程闭环无缺失独立环节，本次为文档结构一致性修复（§5.2 ↔ §4.x 全量对齐）非施工算法缺失 |
| 2026-08-10 | 1.10.0 | §4.21 论文细节补全（6 协同机制+Bellman 残差 -85% 实证+OOS Sharpe 0.9281+伪代码+§4.27 关系+Phase 4 对齐）+ §4.28 Geodesic Execution Slippage 新增 + §1 状态行 27→28 节 + "不在路径"清单增 §4.28 + frontmatter v1.10.0 | 持续改进：整合两篇 2026-08 风险/执行滑点新研究。**论文1** arXiv:2608.04305v1（Yifan Wu / Junjie Lei / Wenjie Huang，ICAIF '26 Milan）"Adaptive Finite-Budget Training for CVaR Risk-Aware Q-Learning"——经核验与既有 §4.21（v1.2.0 浅登记同一 arXiv ID）为**同一论文**，故**就地补全 §4.21** 而非新建重复章节：补 ICAIF '26 venue+作者、RaQL model-free 双时间尺度估计器、关键设计原则（保留原 CVaR 估计器与 Bellman 不动点仅重设计训练过程）、**6 协同机制**（per-cell sizing / outer-rate-matched decay / early correction / coverage-first-then-greedy / suffix aggregation / data-driven calibration）、Bellman 残差降 85%（MeanBEQ 1.2202→0.1854; MeanBEV 1.1624→0.0535）、OOS Sharpe 0.9281 maxDD 6.46%（含成本）vs buy-hold 波动率 47.93%/9.57%、伪代码（#1/#2/#4/#5 四机制<50 行）、与 §4.27 关系（前者分布形状漂移检测 vs 本节 CVaR 估计训练稳定性）、Phase 3+→Phase 4 鲁棒性阶段定位。**论文2** Entropy 2026 28(6) 705 / arXiv:2605.0757（Moroke & Metsileng）"Geodesic Execution Slippage: A Statistical Physics Framework for Cryptocurrency Liquidity Risk"——全新登记 §4.28：执行滑点=MS-GARCH 最大熵模型 Fisher 信息流形测地弧长+联合曲率-TDA 拓扑碎片化告警；5 加密市场（BTC/ETH/XRP/LTC/BCH）2,253 日观测全部最低预测误差+MCS 10% 显著性唯一保留模型（vs Amihud/Kyle λ/Almgren-Chriss 等 6 基线）；4 次危机（Terra 2022-05/FTX 2022-11）中位数提前 2 天告警（早于价格型 circuit breaker）——直接服务于 35 号回撤 Protocol 早期预警；连接 36 号风险监控→35 号回撤 Protocol 触发；Phase 5+ 远期候选（需 Fisher 流形估计+TDA 工具栈，与 §4.27 共享微分几何工具栈）；伪代码（Fisher 度量+测地弧长+曲率-拓扑告警<50 行）。§4.1-§4.28 共 28 节替代方案远期登记。**施工算法完整性结论**：36号 5 流程闭环无缺失独立环节，本次为既有 §4.21 论文细节补全+§4.28 全新研究远期登记非施工算法缺失 |
| 2026-08-12 | 1.11.0 | §3.20 已施工设施盘点（通用规则#11）+ 代码实测校正 5 项（daily_auditor v0.2.0→v0.1.0 等）+ §3.5 双注解（30号§2.5.4 替代裁决+§2.5.6 监控层定位）+ §3.9 13→15 法框架 + §3.9.3 监管更新（Fed 2026-03 SA as cap）+ §3.16 QbSD 来源 + §6 待裁定 3 项 + §6.1 跨文档同步登记 5 项 + frontmatter v1.11.0 |
