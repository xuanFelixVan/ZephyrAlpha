---
module_id: MOD-REGIME-002
title: "Regime特征管道蓝图 — ClickHouse→RegimeFeatures/OverlaySignals/RiskSignalInputs（C1一票否决验证的数据地基）"
doc_type: blueprint
status: Active
version: "0.1.2"
design_maturity: production
build_status: stable
ttl: permanent
layer: L2_domain
layer_name: regime
functional_domain: regime
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-06"
last_updated: "2026-08-06"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-REGIME-002 RegimeFeatureBuilder — Regime特征管道 蓝图

> **module_id**: MOD-REGIME-002 | **域**: D_REGIME | **层**: L2 业务域
> **优先级**: P0 | **成熟度**: design | **建设标记**: 🟡 待施工
> **SSoT**: depgraph MOD-REGIME-002 | **spec 真源**: [10_regime_detector_spec.md](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/10_regime_detector_spec.md) v1.3.1（13参数§5.3 / S2十二维度§4.12 / 8转换§4）
> **验证真源**: [11_regime_backtest_validation_plan.md](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/11_regime_backtest_validation_plan.md) v1.0.0（C1一票否决§5 / 数据基础§7）
> **消费方**: [RegimeDetector](../regime_detector/blueprint.md) MOD-REGIME-001（detect() 三参输入消费者）

## 0. 本蓝图存在理由（第一性原理）

11_regime_backtest_validation_plan §5 **C1 开/关对比是一票否决**——Shrinkage 节流不改善回撤还伤害 Sharpe，整个 regime 系统不部署。C1 的输入是 regime 特征管道的输出。**特征算错一处、PIT 边界泄漏一天、字段名对不齐一个，C1 验证链全部污染**，最后无法判断 regime 到底有没有用——在不稳定地基上盖楼，盖完发现塌了不知道是楼的问题还是地基的问题。

本蓝图把"OHLCV + 多源数据 → RegimeDetector.detect() 三参输入"的每一步计算逻辑、数据源、PIT 边界、warmup 窗口钉死成机器可读真源，是 100% AI 开发场景下后续续写的硬契约。

## 1. 定位

regime 特征管道——把 ClickHouse 多源数据转换成 `RegimeDetector.detect()` 的三个输入参数。是 regime 链的"数据入口"（ClickHouse → 特征 → 检测器 → Shrinkage → budget）。

属 **B 类核心业务模块**（特征工程 + 阈值标定 + PIT 处理），特征公式/阈值为 C 类可调参数（待 D 类参数校准验证）。

### 1.1 三个输出三明治（严格对齐 detect() 签名）

```python
# RegimeDetector.detect() 签名（MOD-REGIME-001，不可破坏）
def detect(
    self,
    regime_features: dict[str, Any],      # ① HMM 6特征 + X矩阵
    overlay_signals: dict[str, Any],      # ② 8转换维度评分
    risk_signal_inputs: dict[str, Any],   # ③ RiskSignal 13参数
) -> tuple[RegimeProbabilities, ShrinkageResult]:
```

| 输出 | 内容 | detect() 内消费方 | spec 真源 |
|------|------|-------------------|-----------|
| ① regime_features | HMM 6特征 + X矩阵 (T,6) | `_run_hmm()` | 10_regime_detector_spec §3 / blueprint §3 |
| ② overlay_signals | 8转换维度评分 {T_id: {dim: score}} | `_run_overlay()` → `record_transition()` | 10_regime_detector_spec §4 / TRANSITION_CONFIG |
| ③ risk_signal_inputs | 13参数 {params: {1..10,12}, opportunity: {...}} | `_compute_risk_signal()` | 10_regime_detector_spec §5.3 |

### 1.2 不做什么

- **不做 regime 判定**（归 MOD-REGIME-001 RegimeDetector）
- **不做 Shrinkage 计算**（归 MOD-REGIME-001，本模块只产 13 参数原料）
- **不做 budget 分配**（归 MOD-PA-007 RegimeMetaAllocator）
- **不做回测**（归 BM-BT 框架，本模块只供数据）
- **不做账户回撤风控**（10_regime_detector_spec §5.3：回撤是沉没成本，归 StrategyBook drawdown protocol，不进 RiskSignal）

## 2. 输入 / 输出

### 2.1 输入（ClickHouse 多源，经 TableRegistry 取表名）

> 数据基础已确认（11_regime_backtest_validation_plan §7）：13 参数全部有数据（#12 筹码用华泰前沿算法自建，非换手率代理）。
> **2026-08-06 修正**：北向资金 2024-08-19 起日度数据停发（仅季度公布），`hk_connect_flow` 标为死数据（仅历史回测用）；资金承接改用 `money_flow` 超大单逆势承接（湘财证券实证前瞻性最强）。

| category_id | 全限定表名 | 用途 | 就绪 |
|-------------|-----------|------|:----:|
| market_kline_daily | c1_market.kline_daily | 后复权 OHLCV（2000年起），主数据源 | ✅ |
| index_kline_daily | c1_index.kline_daily | 指数K线（沪深300/中证500/创业板），跨市场相关性 | ✅ |
| sector_kline_daily | c1_sector.kline_daily | 880xxx 板块K线（460板块），虹吸态#8 HHI + T3 mainline RRG | ✅ |
| market_snapshot | c1_market.snapshot_daily | 涨跌家数/涨跌停，#7 + S2广度 | ✅ |
| market_sector_snapshot | c1_market.sector_snapshot | 板块涨跌家数/成交额，虹吸#8 上涨家数占比 | ✅ |
| market_realtime_snapshot | c1_market.realtime_snapshot | 个股成交额，虹吸#8 前5%成交集中度 | ✅ |
| **market_money_flow** | **c1_market.money_flow** | **主力资金流（超大单/大单净流入），#8资金集中度 + S2 fund主力逆势承接 + T3 sentiment** | ✅ |
| news_data | c1_news.news_data | 新闻情绪原始数据，#11 + S2 policy/bad_news_flat（经NLP管道处理） | ✅ |
| option_iv_surface | c1_derivative.option_iv | 期权IV曲面，A股VIX构建（S1/S2，§4.9/§4.12） | ✅ |
| daily_valuation | c1_valuation.daily | 估值（破净率/PE分位），S2维度5 | ✅ |
| margin_balance | c1_margin.daily | 融资融券余额，S2 fund资金承接 + T3 sentiment | ✅ |
| ~~hk_connect_flow~~ | ~~c1_flow.hk_connect_daily~~ | ~~北向资金~~ **死数据（2024-08-19停发），仅历史回测用，不进实时特征** | ⚠️ |

**取表名铁律**：禁止硬编码表名字符串，必须 `TableRegistry.table(category_id)`（MOD-L00-004 fail-closed，查不到抛 KeyError）。ClickHouse 连接配置从环境变量读取（`CLICKHOUSE_HOST`/`CLICKHOUSE_PORT` 等），缺省时降级（§8）。

### 2.2 输出（三 dict，字段钉死）

#### ① regime_features（HMM 6特征 + X矩阵）

```python
regime_features: dict[str, Any] = {
    "X": np.ndarray,           # (T, 6) HMM 观测矩阵，T=时间步数，6=特征数
    "feature_names": list[str], # ["realized_vol_pct","hurst_dfa","kalman_slope","cross_asset_corr","ad_ratio","volume_anomaly"]
    "timestamps": list[datetime], # 每行对应的日期（PIT 归因用）
    "as_of_date": datetime,    # 当前 detect 时点（PIT 锚点）
}
```

#### ② overlay_signals（8转换维度评分）

```python
overlay_signals: dict[str, Any] = {
    "transitions": {
        "T1": {"bqs": float, "rcs": float, "frs": float},           # §4.6
        "T2": {"continue_decline": float},                           # §4.7
        "T3": {"volume_price": float, "ma_trend": float, "money_effect": float,
               "sentiment": float, "mainline": float, "leader": float,
               "one_day_mainline": float},                           # §4.10.8
        "T4": {"shrink_flat": float},                                # §4.8
        "T5": {"leader_break": float, "rebound_wrap": float},        # §4.11.8
        "T6": {"sudden_volume": float},                              # §4.7
        "S1": {"vix_panic": float, "correlation": float, "liquidity": float,
               "flash_recover": float},                              # §4.9
        "S2": {"capitulation": float, "wyckoff": float, "vix": float,
               "policy": float, "valuation": float, "fund": float,
               "bad_news_flat": float, "spring": float, "three_yang": float,
               "break_sc_low": float, "vix_new_high": float, "fund_outflow": float},  # §4.12
    },
    "as_of_date": datetime,
}
```

> **维度 key 钉死**：必须与 [regime_detector.py](../../../../src/zephyr/regime/core/regime_detector.py) `TRANSITION_CONFIG` 的 `keys_gte` 完全同名，否则 `record_transition()` 的 `_eval_stage()` 取不到值（缺 key 视为不满足）。

#### ③ risk_signal_inputs（RiskSignal 13参数）

```python
risk_signal_inputs: dict[str, Any] = {
    "params": {
        1: float,   # realized_vol 分位 → {1.0, 0.85, 0.6, 0.3}
        2: float,   # 量能异动(量)
        3: float,   # 价格形态(价)
        4: float,   # 时间酝酿(时)
        5: float,   # 空间位置(空)
        6: float,   # 跨市场相关性
        7: float,   # 涨跌家数极端
        8: float,   # 虹吸态
        9: float,   # 技术指标背离
        10: float,  # 趋势斜率衰竭
        12: float,  # 筹码结构（#11 不在此，归 opportunity）
    },
    "opportunity": {
        "news_ghost": float,      # #11 鬼故事抵消（0.0~0.10）
        "bad_news_flat": float,   # #13 利空不跌抵消（0.0~0.20）
    },                             # 合计上限 0.25（detect 内 clamp）
    "as_of_date": datetime,
}
```

> **#11 双向处理**：spec §5.3.2 定义 #11 双向（鬼故事=机会 / 利好密集=风险 / 天灾=避险）。当前 detect() 代码只消费 opportunity 侧（`news_ghost`）；风险侧（利好密集→0.85 / 天灾→0.6）在本模块计算后**暂存 `params[11]`**，待 MOD-REGIME-001 后续扩展 `risk_param_ids` 时启用（登记为遗留，§11）。

## 3. HMM 6特征详细（regime_features["X"]）

> **2026-08-06 修正**：F2 从"250日均线斜率"升级为 Hurst(DFA) + Kalman 斜率双子特征——均线斜率依赖量纲和图表比例（伪精确），Hurst 指数（DFA 法）衡量趋势持久性是统计信号，Kalman 滤波估计自适应斜率不依赖固定窗口。特征数 5→6，X 矩阵 (T,5)→(T,6)。

| F | 特征名 | 计算公式 | 窗口 | 数据源 | PIT |
|---|--------|---------|------|--------|-----|
| F1 | realized_vol_pct | 20日实现波动率的历史分位（滚动250日分位） | HV:20 / 分位:250 | kline_daily.close 收益率 | t-1 及以前 |
| F2a | hurst_dfa | DFA法计算Hurst指数，表征趋势持久性（>0.5趋势，<0.5均值回归，≈0.5随机游走） | 200 | kline_daily.close | t-1 |
| F2b | kalman_slope | Kalman滤波估计的趋势斜率/价格，归一化[-1,1]（自适应，不依赖固定窗口） | 自适应 | kline_daily.close | t-1 |
| F3 | cross_asset_corr | 沪深300/中证500/创业板指 两两相关系数均值（60日） | 60 | index_kline_daily | t-1 |
| F4 | ad_ratio | 涨跌家数比的对数 log((涨+1)/(跌+1))，归一化[-1,1] | 当日 | market_snapshot | t |
| F5 | volume_anomaly | 成交量 z-score（20日均量标准化） | 20 | kline_daily.volume | t-1 |

**Hurst(DFA) 算法**（2026前沿趋势持久性检测，替代均线斜率）：
```
# DFA (Detrended Fluctuation Analysis) 法计算 Hurst 指数
# 1. 累积和序列: Y(t) = Σ(r_i - mean(r)), i=1..t  （r=对数收益率）
# 2. 分割为等长窗口 w（w ∈ {10,20,...,200}），每窗口做线性去趋势
# 3. 计算均方根波动 F(w) = sqrt(mean(残差²))
# 4. log(F(w)) vs log(w) 线性回归，斜率 = Hurst 指数
# 输出: H ∈ (0, 1)，H>0.5 趋势持久，H<0.5 均值回归，H≈0.5 随机游走
```

**Kalman 斜率算法**（自适应趋势斜率，替代固定窗口均线斜率）：
```
# 状态空间模型：斜率 s(t) = s(t-1) + w(t)，观测 y(t) = s(t) + v(t)
# y(t) = 当日对数收益率，s(t) = 潜在趋势斜率
# Kalman 滤波递推估计 s(t)，归一化: kalman_slope = clamp(s(t) / (10×std(r)), -1, 1)
# 优势：不依赖固定窗口，自适应追踪斜率变化，比"250日均线斜率"更稳健
```

**X 构造规则**：
- 单标的 regime（如全市场等权指数）→ X 形状 **(T, 6)**
- 多标的（如分市场分别建模）→ `lengths` 参数标分段，X 拼接（10_regime_detector_spec §3 多序列可选）
- **warmup**：前 250 日（max 窗口）X 置 NaN，HMM 训练前 `np.nan_to_num(X, nan=0.0)` 或 dropna
- **feature_names** 更新: `["realized_vol_pct","hurst_dfa","kalman_slope","cross_asset_corr","ad_ratio","volume_anomaly"]`

**特征标准化**：HMM 假设 Gaussian，特征量纲差异大时需标准化。**训练时 fit StandardScaler on train only**（防泄漏），推理时 transform。Scaler 随 HMM 一起 walk-forward 重拟合。

## 4. 8转换维度评分详细（overlay_signals["transitions"]）

> 每个维度的 score 是 0~100 分（动态评分制，10_regime_detector_spec §4.1）。本模块负责从原始数据计算各维度分值；阈值判定（trigger/confirm/fail）由 MOD-REGIME-001 `record_transition()` 按 `TRANSITION_CONFIG` 完成。

### 4.1 T1 NORMAL→BREAKOUT→Bull-Medium（§4.6）

| 维度 key | 含义 | 计算 | 数据源 |
|----------|------|------|--------|
| bqs | 突破质量（Breakout Quality Score） | 放量突破前高（量>1.5×+收盘>前高）→ 基础60分 + 量价确认加成 | kline_daily |
| rcs | 回踩确认（Re-test Confirm） | 突破后回踩不破前高+缩量 → 60分 | kline_daily |
| frs | 假突破恢复（False-breakout Recover） | 突破失败回落 → 60分（fail 信号） | kline_daily |

### 4.2 T2 Bear-Low→RECOVERY（§4.7 冰点反核）

| 维度 key | 含义 | 计算 |
|----------|------|------|
| continue_decline | 继续下跌标志 | 1.0=跌破前低（fail 信号），0.0=未跌破 |

### 4.3 T3 RECOVERY→BREAKOUT→Bull-Medium（§4.10.8 主升确立）

| 维度 key | 含义 | 计算 |
|----------|------|------|
| volume_price | 量价配合 | 放量上涨（量>1.3×+涨>1%）→ 60分 |
| ma_trend | 均线趋势 | 多头排列（5>10>20>60）→ 50分 |
| money_effect | 赚钱效应 | 全市场上涨家数>60% → 50分 |
| sentiment | 情绪修复(去北向) | 融资余额5日回升+主力资金(super_large)净流入转正 → 60分（§4.3.1，北向2024-08停发已去除） |
| mainline | 主线明确(正向评分) | RRG象限(Improving/Leading)+多周期涨幅交叉(3/5/10/20日)+主力资金持续流入+龙头连板梯队 → 60分（§4.3.2，虹吸排除走#8否决不混入） |
| leader | 龙头领涨 | 龙头股涨幅>板块均值1.5× → 60分 |
| one_day_mainline | 一日游主线 | 1.0=主线一日游（fail 信号） |

#### §4.3.1 T3 sentiment — 情绪修复（2026-08-06 修正，去除北向死数据）

> **糊弄判定**：原公式"融资余额回升/北向回流"——北向资金2024-08-19起日度数据停发是死数据。修正后用融资余额+主力资金（money_flow.super_large_net_inflow）双源：

```
# 情绪修复 = 融资回升 + 主力资金转正（双源确认）
margin_recover = margin_balance_t > margin_balance_{t-5}   # 融资余额5日回升
main_force_positive = sum(super_large_net_inflow_{t-4..t}) > 0  # 主力资金5日净流入转正
# 双源同时满足 → 60分；单源 → 30分；均不满足 → 0分
```

#### §4.3.2 T3 mainline — 主线明确正向评分（2026-08-06 修正，替换"无虹吸=主线"逻辑错位）

> **糊弄判定**：原公式"主板涨幅差<3%（无虹吸）→60分"把"主线明确"等同于"无虹吸"——这是逻辑错位。主线明确是正向确认（有板块领涨+资金持续+龙头梯队），虹吸排除是否决条件（走#8），不能把"否决条件的反面"当"确认分"。
>
> 2026机构主流（西部金工RRG+扩散指标2018-2026年化20.60%超额13.91%）用RRG相对旋转图+多周期涨幅交叉+资金持续+龙头梯队四维度正向评分：

```
# 主线明确正向评分（四维度加权）
# 维度1 — RRG相对旋转图（权重30%，西部金工实证有效）
rs = sector_close / hs300_close                    # 相对强度
rs_ratio = EMA(rs, 10) / EMA(rs, 26) * 100         # >100 跑赢基准
rs_momentum = EMA(rs_ratio, 10) / EMA(rs_ratio, 26) * 100  # >100 加速
# Leading(+,+) 跑赢+加速 → 主线确认期（满分）
# Improving(-,+) 跑输但加速 → 主线苗头期（左侧信号）
# Weakening/Lagging → 减分

# 维度2 — 多周期涨幅交叉验证（权重30%，雪球红星战将2026-01 A股实盘共识）
# 3/5/10/20日板块涨幅榜交叉
# 主线候选: ≥3周期上榜且2周期前10
# 第一梯队: 4周期均上榜且前10（真主线）
# 轮动题材: 仅1-2周期上榜（一日游，排除）

# 维度3 — 主力资金持续流入（权重25%）
# money_flow连续N日净流入≥30亿
persist_score = 连续天数 × 强度

# 维度4 — 龙头连板梯队（权重15%）
# 连板高度 + 龙二龙三跟风
leader_score = 连板高度 + 跟风度

mainline_score = 0.30*rrg + 0.30*cross + 0.25*persist + 0.15*leader
# ≥60 → T3 mainline维度 = 60分
# 注意: 虹吸排除走 #8 否决条件，不在这里扣分
```

### 4.4 T4 Bull-Medium→Bull-High（§4.8 疯狂期赶顶）

| 维度 key | 含义 | 计算 |
|----------|------|------|
| shrink_flat | 放量滞涨 | 1.0=放量滞涨（量>1.5×+涨<0.5%）（fail 信号） |

### 4.5 T5 Bull-High→Bear-Medium（§4.11.8 逃顶退潮）

| 维度 key | 含义 | 计算 |
|----------|------|------|
| leader_break | 龙头破位 | 龙头股跌破20日均线 → 60分 |
| rebound_wrap | 反弹包裹 | 1.0=反弹被包（fail 信号） |

### 4.6 T6 Bear-Medium→Bear-Low（§4.7 退潮冰点）

| 维度 key | 含义 | 计算 |
|----------|------|------|
| sudden_volume | 突发放量 | 1.0=底部突发放量（fail→转 RECOVERY 信号） |

### 4.7 S1 Any→CRISIS（§4.9 VIX Panic + 相关性 + 流动性）

| 维度 key | 含义 | 计算 | 数据源 |
|----------|------|------|--------|
| vix_panic | VIX恐慌(合成VIX) | 合成VIX(方差互换公式,§4.8.3)>近1年90分位+期限结构倒挂+ATM IV偏斜反转 → 60分 | option_iv_surface |
| correlation | 跨资产相关性 | 平均相关性>0.7 → 60分 | index_kline_daily |
| liquidity | 流动性枯竭 | 涨跌停极端+成交骤降 → 60分 | market_snapshot |
| flash_recover | 闪崩恢复 | 1.0=单日闪崩后迅速拉回（fail 信号） | kline_daily |

### 4.8 S2 CRISIS→RECOVERY（§4.12 八基础维度 + §4.12.10 四机构补强）

> S2 是用户抄底能力的系统化编码（10_regime_detector_spec §4.12）。八基础维度对应 `TRANSITION_CONFIG.S2.stages` 的 keys_gte。

| 维度 key | 含义 | 计算 | 数据源 |
|----------|------|------|--------|
| capitulation | 投降式抛售(ACSI) | ACSI=A股投降指数(§4.8.1)：量能极端(3×均量)+价格跌幅(10日ROC<-10%)+广度崩塌(跌停>5%)+杠杆出清(两融5日缩水≥5%)+流动性枯竭(地量换手)，加权[0,100]，≥60分→60 | kline_daily + market_snapshot + margin |
| wyckoff | Wyckoff吸筹(规则法) | 规则法TR+4触发器(§4.8.2)：TR识别(swing中位数+宽度/漂移/测试次数过滤)→SC/Spring/SOS/LPS事件触发(量价三因子)→5态FSM+失效规则，阶段≥Accum_C→60 | kline_daily（OHLCV+量比+振幅） |
| vix | VIX见顶回落 | 合成VIX(§4.8.3)从>90分位回落+期限结构修复(Backwardation→Contango)+Regime降级 → 40分 | option_iv_surface |
| policy | 政策底传导(NLP) | 三层NLP管道(§4.8.4)：规则白名单强召回(降准/降息/MLF/喊话关键词)+FinBERT sentiment+LLM事件五元组精分类，政策类事件得分→40 | news_data → news_nlp（NLP管道输出） |
| valuation | 估值极端 | 破净率>15%/PE历史分位<10% → 40分 | daily_valuation |
| fund | 资金承接(IC加权) | 三源IC加权(§4.8.5)：超大单逆势承接(权重0.5)+融资余额5日变化率(0.3)+ETF净申购(0.2)，标准化+市值行业中性化+滚动IC重标定，composite分位>60%→50 | money_flow + margin + etf_flow |
| bad_news_flat | 利空钝化(NLP+价格) | 三层NLP识别重大利空+次日价格行为验证(§4.8.6)：低开>1%但收红/平开高开+放量/连续钝化 → 40分 | news_data → news_nlp + kline_daily |
| spring | Wyckoff Spring(规则法) | Spring检测算法(§4.8.2)：pierced(跌破support×0.98)+recovered(次日close>support×1.005)+量比≥1.2+仍在区间内 → 1.0（strong_confirm标志） | kline_daily（需先识别TR） |
| three_yang | 三根阳线确认 | 连续3日放量阳线（量递增+阳线实体>1%）→ 1.0（strong_confirm标志） | kline_daily |
| break_sc_low | 跌破SC低点 | 1.0=跌破抛售高潮低点（fail信号，Spring失效规则） | kline_daily |
| vix_new_high | VIX新高 | 1.0=A股VIX再创新高（fail信号） | option_iv_surface |
| fund_outflow | 资金流出 | 1.0=composite_fund分位从>60%回落至<40%（主力净流出+融资下降） | money_flow + margin |

> **四机构补强维度**（§4.12.10 信用利差/相关性回落/流动性恢复/广度恢复）：当前 `TRANSITION_CONFIG.S2` 的 keys_gte 未消费这4维（用 total_gte 聚合）。本模块**计算并暂存**为 `overlay_signals["s2_institutional"]`（信用/相关/流动/广度4字段），待 MOD-REGIME-001 `TRANSITION_CONFIG.S2` 扩展后启用（遗留，§11）。

#### §4.8.1 S2 capitulation — ACSI A股投降指数（2026-08-06 修正，替换加密货币指标）

> **糊弄判定**：原公式"持仓急降+负资金费率"是加密货币指标（持仓量OI+资金费率funding rate），A股现货市场无对应数据。2026 A股适配用ACSI（A股投降指数），基于A股特有的量能/价格/广度/杠杆/流动性五维度：

```
# ACSI = A股投降指数 (A股Capitulation Severity Index) [0, 100]
# 5维度加权（权重由历史案例标定，2026-08-06初版）：

# 维度1 — 量能极端 (权重25%)
#   3×均量 = 极端放量抛售（margin call+自动平仓+止损簇扫荡）
vol_extreme = (volume > 3 * MA(volume, 20)) ? 100 : (volume / (3*MA20)) * 100

# 维度2 — 价格跌幅 (权重25%)
#   10日ROC < -10% = 急性暴跌
price_crash = min(100, max(0, (-roc_10d - 5) / 10 * 100))   # ROC=-15→100分

# 维度3 — 广度崩塌 (权重20%)
#   跌停家数占比 > 5% = 全市场恐慌
breadth_collapse = min(100, (limit_down_count / total_stocks) / 0.05 * 100)

# 维度4 — 杠杆出清 (权重15%)
#   两融余额5日缩水 ≥ 5% = 被动去杠杆
leverage_unwind = min(100, max(0, (margin_balance_5d_ago - margin_balance_now) / margin_balance_5d_ago / 0.05 * 100))

# 维度5 — 流动性枯竭 (权重15%)
#   地量换手（流动性枯竭，抛售无人接盘）
liquidity_dry = min(100, max(0, (1 - turnover / MA(turnover, 20)) * 200))

ACSI = 0.25*vol_extreme + 0.25*price_crash + 0.20*breadth_collapse
     + 0.15*leverage_unwind + 0.15*liquidity_dry
# ≥60 → S2 capitulation 维度 = 60分（trigger门槛）
```

#### §4.8.2 S2 wyckoff/spring — Wyckoff规则法状态机（2026-08-06 修正，替换名词堆砌）

> **糊弄判定**：原公式"PS/SC/AR/ST/Spring/SOS 结构识别→60分"是名词堆砌型糊弄——没有量化检测规则、缺失TR地基、没有量价确认、没有阶段序列FSM、没有失效规则。2026前沿（YoungCan-Wang/WyckoffTradingAgent + heavenJiang/WyckoffPro + FibAlgo）共识：规则法TR+事件触发器+FSM+失效规则，不上纯ML。

**四层架构**：
```
# L1 — 交易区间识别(TR)（地基，没有TR就没有Spring/SOS）
# swing high/low 中位数法（比固定分位数稳，exclude_last=1防未来函数）
swing_lows = find_swings(low, window=3, exclude_last=1)
swing_highs = find_swings(high, window=3, exclude_last=1)
support = median(last 5 swing_lows)      # 支撑=近5个swing low中位数
resistance = median(last 5 swing_highs)   # 阻力=近5个swing high中位数
width_pct = (resistance - support) / support * 100
# 过滤: 4% < width < 55%（太窄/太宽不是有效TR）
# 漂移: |首尾收盘变化| < 18%（漂移太大不是盘整）
# 测试: support测试≥2 且 resistance测试≥2（3.5%容差）
# quality_score = 0.45*test_score + 0.35*width_score + 0.20*drift_score

# L2 — 4个高价值触发器（量价三因子联合判定）
# SC(抛售高潮): vol_ratio≥2.5 + spread≥2×ATR + 收盘在bar上40%（下影线长）
#   A股常表现为跌停板放量撬板
# Spring(震仓): pierced(min(prev_low,last_low)≤support×0.98)
#            + recovered(次日close>support×1.005，A股T+1用次日确认)
#            + vol_ratio≥1.2 + 仍在区间内(last_close<mid+width×0.25)
# SOS(需求信号): close≥resistance×0.99 + pct_chg≥7%(A股调高) + vol_ratio≥2.0
# LPS(最后支撑点): 近N日低点≤support+width×0.35 + 守住support + 缩量(dry_ratio≤0.6)

# L3 — 5态FSM（阶段转移+反面证据回退）
# Crisis(无TR) --SC+AR--> Stabilizing(TR形成)
# Stabilizing --ST确认--> Accumulating(Phase B)
# Accumulating --Spring--> Washing(Phase C)
# Washing --SOS--> Recovering(Phase D)
# Recovering --close>resistance--> Recovered(Phase E,转S3)
# 反面证据积分≥阈值 → 回退阶段（参考WyckoffPro Counter-Evidence Tracker）

# L4 — 失效规则（必须有）
# Spring后收盘低于Spring低点0.5×ATR → Spring失效
# 无AR出现 → 整个形态stale
# PS/AR/ST不强求单独触发器（主观性强，合并到SC后续验证）

# S2评分:
# wyckoff维度: FSM阶段≥Accum_C(Washing/Recovering) → 60分
# spring维度(strong_confirm): Spring触发器命中 → 1.0
```

> **参考实现**：YoungCan-Wang/WyckoffTradingAgent `core/wyckoff_structure.py`（动态TR+4触发器，A股实战558 stars）；heavenJiang/WyckoffPro（11维FSM+反面证据积分）。不追求全14事件，聚焦Spring+SOS两个高价值信号。

#### §4.8.3 S2 vix + S1 vix_panic — A股合成VIX构建（2026-08-06 修正，替换"期权IV>35"糊弄）

> **糊弄判定**：原公式"期权IV>35"有5个糊弄点：①未定义"哪个IV"（662期权每个都有IV）；②未指定标的（50ETF/300ETF/MO的IV不同）；③未说明聚合方法（需方差互换1/K²加权，非单点）；④期限结构Backwardation未定义取法；⑤阈值35是美股VIX的，A股50ETF IV中位数约20，直接照搬未校准。
>
> iVIX（中国波指000188）2018-02-22停发至今未恢复。2026年机构各自用50ETF/300ETF期权+方差互换公式自算（国泰君安期货/国泰海通/上财SVIX）。项目有662期权+Greeks数据（IV已用Newton-Raphson反解写入option_iv_surface表），完全有能力自算。

**核心算法 — CBOE VIX白皮书方差互换公式**（model-free，不依赖BS假设）：
```
# 单期限方差: σ²(T) = (2/T) × Σ[ΔK_i / K_i² × e^(rT) × Q(K_i)] − (1/T) × (F/K₀ − 1)²
# 30天双期限插值: VIX = 100 × √[T₁σ₁²×(N₂-30)/(N₂-N₁) + T₂σ₂²×(30-N₁)/(N₂-N₁)] × 365/30
#
# A股适配:
#   标的 = 300ETF(510300.SH)（流动性好，代表大盘）
#   r = SHIBOR对应期限插值（1D/7D/14D/1M/3M）
#   展期 = 7自然日（上交所原iVIX规则）
#   Q(K_i) = OTM期权买卖价差中点（K<K₀用put，K>K₀用call，K₀取put/call均值）
#   剔除 bid=0 合约 + 连续零bid截断（A股期权流动性差）
#   行权价稀疏 → SVI参数化曲面校准后插值补虚拟行权价（上财SVIX改进）

def compute_ashare_vix(trade_date, underlying="510300.SH"):
    rows = ch_query(option_iv_surface, trade_date, underlying)
    near_exp, next_exp = select_two_expiries(rows, trade_date, min_days=7)
    sigma2_near = variance_swap_var(rows, near_exp, r=shibor(near_exp))
    sigma2_next = variance_swap_var(rows, next_exp, r=shibor(next_exp))
    vix = 100 * sqrt(interpolate_30d(sigma2_near, sigma2_next, near_exp, next_exp))
    return vix   # 与原iVIX误差±5%（上财SVIX实证）

def compute_term_structure(trade_date, underlying="510300.SH"):
    # ATM IV期限结构（用delta≈0.5选ATM，或方差互换方差σ²(T)更稳健）
    near_iv = atm_iv(trade_date, underlying, near_exp)
    next_iv = atm_iv(trade_date, underlying, next_exp)
    slope = next_iv - near_iv   # >0 Contango(正常) / <0 Backwardation(恐慌)
    return slope
```

**S1 vix_panic 维度评分**（CRISIS触发，§4.9 替换"IV>35"）：
```
# 6子维度合计（满分100+，触发门槛见TRANSITION_CONFIG.S1.keys_gte: vix_panic=60）
# 子维度1 — 合成VIX绝对值: >近1年90分位→+25 / >95分位→+30 / >99分位→+35
#   （用滚动分位而非硬编码35，自动适应A股IV中枢漂移）
# 子维度2 — 合成VIX持续性: 连续>90分位>10日→+25
# 子维度3 — 期限结构倒挂: slope<0(Backwardation)→+25
# 子维度4 — ATM IV偏斜反转: put_atm_iv > call_atm_iv→+30（机构买put对冲痕迹）
# 子维度5 — IV飙升速度: 3日合成VIX翻倍→+20
# 子维度6 — 单日spike噪音: VIX单日spike>30但1-3天回落→-10（非危机，闪崩恢复）
```

**S2 vix 维度评分**（RECOVERY确认，§4.12.3 替换"VIX>35后回落<30"）：
```
# 4子维度合计（满分100，触发门槛见TRANSITION_CONFIG.S2.keys_gte: vix=40）
# 子维度1 — VIX见顶回落: 合成VIX从>90分位回落至<75分位→+25
# 子维度2 — VIX spike→reverse: 持续飙升后快速反转下行→+30
# 子维度3 — VIX Regime降级: Panic(>95分位)→Elevated(75-95分位)→Normal(25-75分位)→+20
# 子维度4 — 期限结构修复: Backwardation恢复Contango(slope由负转正)→+25
```

> **阈值校准**：不硬编码35（美股VIX阈值），改用近1年滚动分位（>90/95/99分位），自动适应A股IV中枢漂移。MVP可先用ATM IV简化版（delta=0.5 call IV近月/远月均值），完整版用方差互换公式。

#### §4.8.4 S2 policy + S2 bad_news_flat + #11 news_ghost — 金融新闻NLP三层管道（2026-08-06 修正，替换定性词）

> **糊弄判定**：原公式"降准降息/MLF/喊话→40分"和"重大利空后低开拉回→40分"全是定性词，没有自动识别逻辑，news_data表无事件类型字段。2026前沿用规则+FinBERT+LLM三层混合架构（解决"鬼故事""重大利空""政策事件"自动识别）：

```
# 三层NLP管道（新增 news_nlp 表存储输出）
# Layer 1 — 规则白/黑名单强召回（高召回率，防漏）
policy_whitelist = ["降准","降息","MLF","逆回购","定向降准","再贷款",
                    "稳定市场","提振信心","国务院","央行","证监会"]
bad_news_blacklist = ["爆雷","退市","立案调查","业绩暴雷","财务造假",
                      "ST","违约","质押强平","鼠仓","操纵市场"]
ghost_keywords = ["鬼故事","恐慌","崩盘","血洗","归零","大萧条"]  # 鬼故事密集=底部信号
# 命中 → 进入Layer 2

# Layer 2 — FinBERT 全量 sentiment 打分（情感方向+强度）
sentiment_score = finbert(news_text)   # ∈ [-1, 1]，负=利空，正=利好
# FinBERT-Finance（yiyanghkust/finbert-tone）A股适配版

# Layer 3 — LLM 事件五元组精分类（主体/粗类/细类/方向/规模）
event = llm_extract(news_text)  # Qwen3/CFGPT
# 五元组: {subject, coarse_type, fine_type, direction, magnitude}
# coarse_type: 政策/利空/鬼故事/利好/中性
# fine_type: 货币政策/监管处罚/业绩雷/宏观风险/...
# direction: +1利好 / -1利空 / 0中性
# magnitude: 1-5 级影响规模

# 输出存入 news_nlp 表:
# {news_id, event_type, sentiment_score, direction, magnitude, coarse_type, fine_type}
```

**S2 policy 维度评分**：
```
policy_events = news_nlp WHERE coarse_type='政策' AND direction=+1 AND timestamp in [t-5, t]
policy_score = sum(event.magnitude for event in policy_events) * 10  # 降准5级→50，喊话2级→20
# ≥40 → S2 policy维度 = 40分
```

**S2 bad_news_flat 维度评分**（利空钝化=重大利空+次日价格行为验证）：
```
bad_news_events = news_nlp WHERE coarse_type='利空' AND magnitude≥3 AND date=t-1
if bad_news_events and kline_daily[t].open < kline_daily[t-1].close * 0.99:  # 低开>1%
    if kline_daily[t].close > kline_daily[t-1].close:  # 收红（低开拉回）
        bad_news_flat = 40  # 利空钝化确认
    elif kline_daily[t].close > kline_daily[t].open and volume > MA(volume,20):  # 平开高开+放量
        bad_news_flat = 40
# 连续钝化: 近5日≥3次利空事件但价格未创新低 → 40
```

**#11 news_ghost 机会抵消**（鬼故事密集=资本拿货，用户盘感映射）：
```
ghost_events = news_nlp WHERE coarse_type='鬼故事' AND date in [t-5, t]
ghost_count = count(ghost_events)
if ghost_count >= 5 and close < MA(close, 250):  # 鬼故事密集+价格低位
    news_ghost = 0.10  # 机会抵消+0.10
```

#### §4.8.5 S2 fund — 资金承接三源IC加权（2026-08-06 修正，替换北向死数据）

> **糊弄判定**：原公式"融资余额回升/北向回流/ETF申购→50分"——三源没权重没融合公式没归一化，全是定性词；北向资金2024-08-19起日度数据停发是死数据；money_flow（超大单主力资金流）这张更关键的表根本没进数据源。2026机构标准用IC/ICIR加权融合（中信建投2026-06实证GRU最优，信息比2.74）：

```
# 三源衍生特征（统一成"净流入率"）
margin_factor = (margin_balance_t - margin_balance_{t-5}) / circulating_mktcap   # 融资5日变化率
main_force_factor = sum(super_large_net_inflow_{t-4..t}) / circulating_mktcap    # 超大单逆势承接（权重最大）
etf_factor = etf_net_subscription_weekly / sector_mktcap                          # ETF净申购

# 预处理: MA5/MA20平滑 → flow_trend = MA5/MA20 - 1
# 中性化: 市值+行业 OLS 取残差（消除size/industry暴露）

# IC加权融合（权重由滚动IC标定，非拍脑袋）
IC_i = spearman_corr(factor_i, forward_return_5d)   # 滚动60日
# 先验权重（北向停发后重标定，湘财证券实证超大单前瞻性最强）:
weights = {main_force: 0.5, margin: 0.3, etf: 0.2}  # 上线后用滚动IC替代
composite_fund = sum(w_i * rank_pct(factor_i_neutral))

# S2 fund 评分
fund_score = 100 * sigmoid_rank_pct(composite_fund)
# 触发承接(≥50分) = composite_fund分位 > 60% 且 指数新低时super_large净流入转正（逆势承接）
```

> **ETF流向是负向因子**（机构高抛低吸，ICIR 0.65），应作为拥挤/风险提示而非承接信号——此处etf_factor权重低且方向需校准。

#### §4.8.6 S2 bad_news_flat 补充 — 利空钝化次日价格行为验证

> 见 §4.8.4 NLP管道的 bad_news_flat 评分部分。核心：NLP识别重大利空事件 → 次日价格行为验证（低开拉回/平开高开+放量/连续钝化）→ 两者联合判定。

## 5. RiskSignal 13参数详细（risk_signal_inputs）

> 11个下调参数四档系数 {1.0, 0.85, 0.6, 0.3}（10_regime_detector_spec §5.3.1）+ 2个机会抵消参数（§5.3.2，合计上限0.25）。本模块从原始数据计算 raw 特征 → 按阈值映射系数。

### 5.1 11个下调参数（params[1..10, 12]）

| # | 参数 | raw特征计算 | 四档阈值（→系数） | 数据源 |
|---|------|------------|-------------------|--------|
| 1 | realized_vol分位 | 20日HV的250日分位 | <80→1.0 / 80-90→0.85 / 90-95→0.6 / >95→0.3 | kline_daily |
| 2 | 量能异动(量) | 量比+涨跌幅 | 正常→1.0 / 放量滞涨(量>1.5×+涨<0.5%)→0.85 / 放量杀跌(>1.5×+跌>1.5%)→0.6 / 放量暴跌(>2×+跌>3%)→0.3 | kline_daily |
| 3 | 价格形态(价) | 均线排列+支撑 | 趋势完好→1.0 / 前高横盘→0.85 / 支撑失守或假突破→0.6 / 高低峰递减→0.3 | kline_daily |
| 4 | 时间酝酿(时) | 盘整周期占比 | 盘整充分→1.0 / 变盘窗口临近(±2日)→0.85 / 盘整不足(<2/3预期)→0.6 / 无极端档 | kline_daily |
| 5 | 空间位置(空) | 价格相对前高/套牢区 | 中低位→1.0 / 近前高(<5%)→0.85 / 套牢盘密集区→0.6 / 盈亏比<1:2→0.3 | kline_daily + chip_distribution（MOD-REGIME-005） |
| 6 | 跨市场相关性 | 60日平均相关性 | <0.5→1.0 / 0.5-0.7→0.85 / 0.7-0.8→0.6 / >0.8→0.3 | index_kline_daily |
| 7 | 涨跌家数极端 | 上涨家数占比 | 40-60%→1.0 / <40%或>70%→0.85 / 下跌>70%→0.6 / 下跌>80%→0.3 | market_snapshot |
| 8 | 虹吸态 | 前5%成交集中度+板块HHI+资金集中度（§5.1.8） | 健康(差<3%且集中度<40%)→1.0 / 弱虹吸(差3-5%或集中度40-60%)→0.85 / 虹吸(差>5%+上涨<40%)→0.6 / 虹吸+极端(集中度>60%或HHI>1800或前5%>45%)→0.3 | realtime_snapshot + sector_kline_daily + money_flow |
| 9 | 技术指标背离 | Pivot-Pair单调配对+多分时共振（§5.1.9） | 无背离→1.0 / 单指标背离→0.85 / 单分时顶背离→0.6 / 多分时共振背离(日+120m+60m)→0.3 | kline_daily (MACD-DIF/KDJ-J/RSI) |
| 10 | 趋势斜率衰竭 | Hurst衰退+ADX峰值回落+价格结构破坏（§5.1.10） | 无衰竭→1.0 / ADX回落(>40→<35)→0.85 / Hurst+ADX双衰(0.65→0.50)→0.6 / 三者共振(含结构破坏)→0.3 | kline_daily (Hurst/ADX/价格结构) |
| 12 | 筹码结构 | 华泰前沿算法：VWAP中心三角分布+筹码龄分层+32相对网格（§5.1.12，MOD-REGIME-005） | 健康(底部单峰+长龄堆积)→1.0 / 触及上方套牢峰→0.85 / 底部未堆积→0.6 / 高位派发(筹码上移)→0.3 | chip_distribution（自建，非换手率代理） |

> **地量特殊处理**（§5.3.1）：量<0.5×均量=抛压枯竭/底部信号，#2 系数=1.0（不计下调），底部意义由 #12 和 S2 承接。
> **#4 无极端档**：时间因素影响"是否该等"非"风险多大"，最高到危险档0.6。

#### §5.1.8 #8 虹吸态详细算法（2026-08-06 修正，替换模糊"主板vs板块涨幅差"）

> **糊弄判定**：原公式"主板vs板块涨幅差+资金集中度"——"主板"未定义是哪个指数，"涨幅差"未定义1日还是N日，"资金集中度"只给阈值>60%没给计算公式（HHI还是top5占比？成交额还是主力净流入？）。申万宏源2026-07-31《虹吸、趋同与分化》三层虹吸框架量化落地：

**三支柱指标**（力的期权工作室2026-06实证，20年回测）：
```
# 指标A — 前5%个股成交集中度（最核心）
top5pct_conc = sum(个股成交额降序前5%) / sum(全市场成交额)
# 阈值: <40%正常 / 40-45%中度抱团 / >45%极致抱团（历史峰值49%→后续崩盘）
# 数据源: realtime_snapshot.amount（或 money_flow 当日聚合）

# 指标B — 板块成交额HHI（赫芬达尔指数）
shares_i = sector_amount_i / sum(all sector_amount)
hhi_sector = sum(shares_i ** 2) * 10000   # ×10000转标准量纲
# 阈值(DOJ/FTC标准): <1000分散 / 1000-1800中度 / >1800高度集中
# 辅助: CR5/CR10(前5/10板块占比), Neff=1/HHI
# 数据源: sector_kline_daily.amount（460板块）

# 指标C — 资金集中度（钱诚2026-06两融指数体系）
mainline_inflow = sum(主线板块个股 main_net_inflow)
fund_conc = mainline_inflow / sum(全市场 main_net_inflow)
# 阈值: <40%健康分散 / >60%虹吸
# 数据源: money_flow.main_net_inflow 聚合到板块

# 指标D — 涨幅背离度（5日累计）
divergence = max(sector_5d_return) - hs300_5d_return   # >5%虹吸
# 指标E — 上涨家数占比
up_ratio = up_stocks / (up_stocks + down_stocks)       # <40%虹吸
```

**四档系数映射**：
- 健康（差<3% 且 上涨>60% 且 集中度<40%）→ **1.0**
- 弱虹吸（差3-5% 或 集中度40-60%）→ **0.85**
- 虹吸（差>5% 且 上涨<40%）→ **0.6**
- 虹吸+极端（集中度>60% 或 HHI>1800 或 前5%>45%）→ **0.3**

#### §5.1.9 #9 技术指标背离详细算法（2026-08-06 修正，替换"KDJ>90+价未超前高"模糊定义）

> **糊弄判定**：原公式"KDJ>90+价未超前高"非数学化定义，无pivot配对逻辑，KDJ超买≠背离。2026前沿用Pivot-Pair单调配对算法（scipy.find_peaks）：

```
# Pivot-Pair 单调配对算法（顶背离为例）
# 1. 用 scipy.signal.find_peaks 检测价格和指标的极值点
price_peaks = find_peaks(kline_daily.high, distance=5)    # 价格高点
indicator_peaks = find_peaks(macd_dif, distance=5)         # 指标(MACD-DIF/KDJ-J/RSI)高点

# 2. 单调配对：相邻的价格峰和指标峰配对（时间上对齐）
pairs = match_pivots(price_peaks, indicator_peaks, max_lag=3)

# 3. 背离判定
for (p1, i1), (p2, i2) in consecutive_pairs(pairs):
    if price[p2] > price[p1] and indicator[p2] < indicator[i1]:
        # 价格HH + 指标LH = 顶背离
    elif price[p2] < price[p1] and indicator[p2] > indicator[p1]:
        # 价格LL + 指标HL = 底背离

# 4. 多分时共振（增强信号）
# 在日线、120分钟线、60分钟线三个周期上分别检测背离
# 共振 = 2个及以上周期同时出现背离
```

**四档系数**：无背离→1.0 / 单指标背离→0.85 / 单分时顶背离→0.6 / 多分时共振(日+120m+60m)→0.3
**指标选择**：MACD-DIF（趋势背离）+ KDJ-J（动量背离）+ RSI（强度背离），三指标取最严。

#### §5.1.10 #10 趋势斜率衰竭详细算法（2026-08-06 修正，替换"均线斜率角度>45°→<30°"伪精确）

> **糊弄判定**：原公式用均线斜率角度（>45°→<30°），依赖量纲和图表比例（同一数据不同坐标比例角度不同），是伪精确。2026前沿用Hurst衰退+ADX峰值回落+价格结构破坏的统计信号组合：

```
# 信号1 — Hurst 指数衰退（趋势持久性消失）
hurst_current = hurst_dfa(close, window=200)      # 当前Hurst（与F2a共用计算）
hurst_recent = hurst_dfa(close, window=100)       # 近期Hurst
hurst_decay = hurst_current < 0.50 and hurst_recent < hurst_current
# 趋势态 Hurst>0.65 → 衰退期 Hurst<0.50（从趋势变为均值回归）

# 信号2 — ADX 峰值回落（趋势强度衰减）
adx_current = ADX(high, low, close, period=14)
adx_peak = max(adx over last 20 days)
adx_decline = adx_peak > 40 and adx_current < 35   # 从强趋势回落

# 信号3 — 价格结构破坏（高低点序列断裂）
# 上升趋势衰竭：最近高点 < 前高，最近低点 < 前低（高低点递减）
higher_highs_broken = close没有创新高 且 high序列出现lower_high
```

**四档系数**：无衰竭→1.0 / ADX回落(>40→<35)→0.85 / Hurst+ADX双衰→0.6 / 三者共振(含结构破坏)→0.3

#### §5.1.12 #12 筹码结构详细算法（2026-08-06 修正，替换换手率代理）

> **糊弄判定**：原公式用"换手率+底部堆积代理"，换手率≠筹码分布——换手率高只代表交易活跃，不代表筹码在哪。2026华泰前沿算法用VWAP中心三角分布换手递推+筹码龄分层+32相对网格映射（MOD-REGIME-005独立模块）：

```
# 华泰2026前沿筹码分布算法（VWAP中心三角分布换手递推）
# 核心公式: C_t(p) = (1-τ_t)×C_{t-1}(p) + τ_t×D_t(p)
#   τ_t = 当日换手率, D_t(p) = 当日三角分布密度, C_t(p) = 价格p处筹码量

# 1. 当日增量三角分布（以VWAP为中心）
vwap = sum(amount) / sum(volume)
price_range = [low, high]
D_t(p) = triangular_pdf(p, center=vwap, range=price_range)

# 2. 换手递推（衰减旧筹码+注入新筹码）
C_t = (1 - τ_t) * C_{t-1} + τ_t * D_t

# 3. 筹码龄分层（时间维度）
# 超短期(1-2天)/短期(3-10天)/中期(11-100天)/长期(101+天)
# 每层独立递推，长期桶占比 = 底部堆积指标

# 4. 32相对网格映射（跨股比较）
# 把绝对价格映射到32个相对网格(0=最低,31=最高)，归一化筹码分布

# 5. 四档判定
long_term_bottom_ratio = sum(C_t[长期桶] at 底部网格) / sum(C_t[长期桶])
# 健康(底部单峰+长龄堆积>60%)→1.0
# 触及上方套牢峰(高位有筹码峰)→0.85
# 底部未堆积(长龄底部<30%)→0.6
# 高位派发(筹码从底部上移)→0.3
```

> **独立模块**：筹码引擎 MOD-REGIME-005 单独 blueprint + 实现，本模块调用其输出。详细算法见 MOD-REGIME-005 蓝图。

### 5.2 2个机会抵消参数（opportunity）

| # | 参数 | 触发条件 | 抵消值 | 数据源 |
|---|------|---------|--------|--------|
| 11 | news_ghost（鬼故事） | NLP三层管道识别鬼故事密集(≥5次/5日) + 价格低位(<250日均线) | +0.10 | news_data → news_nlp（§4.8.4）+ kline_daily |
| 13 | bad_news_flat（利空不跌） | NLP识别重大利空(magnitude≥3) + 次日价格行为验证(低开>1%但收红/平开高开+放量/连续钝化) | +0.10 / +0.15 / +0.20 | news_data → news_nlp（§4.8.4）+ kline_daily |

> **合计上限 0.25**：detect() 内 `min(recovery, 0.25)` clamp，本模块产出时可不 clamp（让 detect 负责）。
> **#11 风险侧**（利好密集→0.85 / 天灾→0.6）：本模块计算后暂存 `params[11]`，待 detect() 扩展启用（遗留，§11）。

### 5.3 7月案例验证基准（10_regime_detector_spec §5.3.4）

> 本模块实现后必须复现此案例（tests/regime/test_regime_feature_builder.py 核心断言）：

| 时点 | 异常参数 | RiskBase | 共振惩罚 | 机会恢复 | RiskSignal |
|------|---------|----------|---------|---------|-----------|
| 7月上旬 | 无 | 1.0 | ×1.0 | 0 | **1.0** |
| 7月11-15 | #1,#5,#9,#10 | 0.85 | ×0.85(4异常) | 0 | **0.72** |
| 7月17 | #1,#7,#8 | 0.3 | ×0.90(3异常) | 0 | **0.30**（clamp下限） |
| 8月4 | #1 + news_ghost + bad_news_flat | 0.6 | ×1.0(1异常) | +0.25 | **0.85** |

## 6. PIT 铁律与 warmup

> **C1 一票否决前提**：特征不能含未来信息，否则 HMM 拟合/walk-forward 全是 look-ahead bias，C1 结果不可信。

### 6.1 PIT 边界规则

| 特征类别 | PIT 锚点 | 规则 |
|---------|---------|------|
| 日频 OHLCV 衍生（F1/F2/F5）| t-1 收盘 | detect(t) 用 [t-W, t-1] 窗口，**不含 t 日** |
| 跨资产相关性（F3）| t-1 收盘 | 60日窗口 [t-60, t-1] |
| 涨跌家数（F4）| t 收盘 | 当日快照（收盘后才有，t 日 detect 用 t 日数据合法） |
| RiskSignal 13参数 | t 收盘 | 当日盘后数据（detect 在收盘后跑，t 日可见） |
| 覆盖层 S1/S2 信号 | t 收盘 | 当日盘后 |

> **关键区分**：HMM 训练用历史特征（PIT 严格 t-1），HMM 推理 `predict_proba(X)` 用最新特征（t 或 t-1，按调用时点）。**回测中 detect(t) 必须只用 t 及以前数据**，禁止用 t+1。

### 6.2 warmup 窗口

- **max 窗口 = 250日**（F2 趋势斜率 250日均线）
- 前 250 日特征为 NaN / 不可用 → detect 返回降级（HMM 均匀分布 + RiskSignal=1.0）
- 回测起始日必须 ≥ 数据起始日 + 250日

### 6.3 NaN 处理

| 场景 | 处理 |
|------|------|
| warmup 期 NaN | X 该行 dropna 或填0（HMM 训练前 `np.nan_to_num`） |
| 单特征缺失（如期权IV缺）| 该特征列填0 + 标记 degraded（对应参数降级） |
| 全特征缺失 | detect 降级（§8） |

## 7. walk-forward HMM 训练数据准备

> 11_regime_backtest_validation_plan §4.5 E1 / §9：HMM 季度重拟合（对照 Morwane）。

| 配置 | 值 | 说明 |
|------|-----|------|
| 重拟合频率 | 季度（每季度末） | 对齐 Morwane |
| train 窗口 | 滚动 5 年（~1260 交易日） | 可调，初始 5 年 |
| test 窗口 | 1 季度（~63 交易日） | 季度内用同一 HMM |
| X 构造 | train 区间每日 5 特征 → (T_train, 5) | `RegimeFeatureBuilder.build_train_matrix(start, end)` |
| Scaler | StandardScaler fit on train only | 防泄漏，随 HMM 重拟合 |

**接口**：
```python
def build_train_matrix(self, start: date, end: date) -> dict[str, Any]:
    """构造 HMM 训练矩阵（walk-forward 季度重拟合用）。
    Returns: {"X": np.ndarray (T,5), "lengths": list[int]|None, "scaler": StandardScaler}
    """
```

## 8. 错误契约与降级

| 错误码 | 场景 | 处理 |
|--------|------|------|
| ZA-REGIME-0010 | ClickHouse 不可用 / 表不存在 | 抛 `RegimeFeatureError`，detect 上层降级为均匀分布+RiskSignal=1.0 |
| ZA-REGIME-0011 | 单表缺失（如 option_iv_surface 缺） | 该维度降级（VIX 用 HV 代理 / 信用利差跳过），log WARN |
| ZA-REGIME-0012 | 特征含 NaN（warmup 外） | 填0 + 标记 degraded，对应参数系数=1.0（不下调，保守） |
| ZA-REGIME-0013 | TableRegistry 查不到 category_id | 抛 KeyError（fail-closed，禁止硬编码表名绕过） |

**降级链**：本模块降级 → RegimeDetector `_run_hmm` 返回均匀分布 1/9 → `_compute_risk_signal` 缺输入返回 1.0 → Shrinkage=ConfidenceSignal×1.0（仅置信度节流）。保证 detect 永不崩溃。

## 9. 依赖关系

### 9.1 上游依赖

| 依赖 | 用途 | 模块 |
|------|------|------|
| TableRegistry | 取 ClickHouse 表名（fail-closed） | MOD-L00-004 |
| ClickHouse driver | 行情数据查询 | zephyr.data.providers |
| pit_manager | PIT 平移（如已存在） | zephyr.shared（待确认） |
| numpy/pandas | 特征计算 | 标准 |

### 9.2 下游消费

| 消费方 | 消费内容 | 模块 |
|--------|---------|------|
| RegimeDetector.detect() | 三 dict 全部 | MOD-REGIME-001 |
| BM-BT-03-E 验证 | X 矩阵 + timestamps（CRPS/校准度归因） | BM-BT |
| B4 转换触发验证 | overlay_signals["transitions"]（标注历史事件） | BM-BT |

### 9.3 depgraph 边

```
MOD-REGIME-002 → MOD-REGIME-001 (RegimeDetector 消费特征)
MOD-REGIME-002 → MOD-L00-004 (TableRegistry 取表名)
MOD-REGIME-002 → D_DATA (ClickHouse 行情)
```

## 10. 验证用例（tests/regime/test_regime_feature_builder.py）

> 必须含 [TTL] 头部走门禁。覆盖：

| 用例类 | 验证内容 | 断言基准 |
|--------|---------|---------|
| 单元·HMM 5特征 | F1-F5 计算正确性 | 手算值 ± 容差 |
| 单元·13参数阈值映射 | raw特征→系数四档 | §5.3.1 阈值表 |
| 集成·7月案例 | RiskSignal 4时点 | 1.0/0.72/0.30/0.85（§5.3） |
| PIT·无未来 | detect(t) 不读 t+1 数据 | 注入 t+1 噪声，结果不变 |
| 降级·ClickHouse缺 | 表缺失时降级 | 抛 ZA-REGIME-0010 / 降级均匀分布 |
| walk-forward | 季度重拟合 X 矩阵 | train/test 窗口正确，无重叠 |
| 契约·维度key对齐 | overlay_signals keys | 与 TRANSITION_CONFIG keys_gte 完全同名 |

## 11. 遗留问题与后续

| # | 遗留 | 处理 |
|---|------|------|
| L1 | #11 风险侧（利好密集/天灾）未启用 | 本模块计算暂存 params[11]，待 MOD-REGIME-001 `risk_param_ids` 扩展 |
| L2 | S2 四机构补强维度（信用/相关/流动/广度）未启用 | 本模块计算暂存 s2_institutional，待 TRANSITION_CONFIG.S2 扩展 |
| L3 | ~~#12 筹码结构用换手率代理~~ | ✅ 已修正（2026-08-06）：华泰前沿算法VWAP三角分布+筹码龄分层，归 MOD-REGIME-005 独立模块 |
| L4 | 信用利差数据源（HY/IG OAS 或 A股信用债利差）未在 §2.1 表中 | 待数据接入后补 category_id |
| L5 | Scaler 随 HMM walk-forward 重拟合的持久化 | 待 walk-forward 实现时定 |
| L6 | ~~A股VIX构建算法待整合~~ | ✅ 已修正（2026-08-06）：CBOE方差互换公式+300ETF+SHIBOR+7日展期+SVI曲面校准，§4.8.3完整整合，S1 vix_panic/S2 vix均更新 |
| L7 | news_nlp 表待新建（NLP三层管道输出） | 需建表 schema + NLP管道实现（规则+FinBERT+LLM） |
| L8 | MOD-REGIME-005 筹码引擎待建（blueprint+实现） | 华泰前沿版，本模块#12/#5/S2底部筹码均依赖 |
| L9 | HMM 特征数 5→6（Hurst+Kalman）需同步更新 regime_detector.py | detect() 签名不变（dict输入），但 _run_hmm 内 n_features 需适配 |
| L10 | money_flow 表已补入§2.1，但 TableRegistry 需注册 category_id | `market_money_flow` → `c1_market.money_flow` |

## 12. 实施阶段（A→B→C 顺序，本模块=A）

> 用户裁定（2026-08-06）：直接进入施工，按 A→B→C 顺序推进，跑通真实数据 C1 一票否决判定。

| 阶段 | 内容 | 产出 | 阻塞 |
|------|------|------|------|
| **A1** | HMM 5特征 + X矩阵 + walk-forward 训练接口 | `build_features()` + `build_train_matrix()` | C1 的 HMM 输入 |
| **A2** | RiskSignal 13参数（11下调+2机会） | `build_risk_signal_inputs()` | C1 的 Shrinkage 输入 |
| **A3** | 8转换维度评分 | `build_overlay_signals()` | B4 转换触发验证 |
| **A4** | 7月案例集成测试 + PIT 验证 | test_regime_feature_builder.py | A1-A3 通过后 |
| **B** | Shrinkage 接入点（MOD-REGIME-003 shrinkage_applier） | 注入 BM-BT-02 | A 完成 |
| **C** | C1 开/关对比器（MOD-REGIME-004 c1_comparison） | C1 报告 | A+B 完成 |

> **A 完成定义**：7月案例 4 时点 RiskSignal 吻合 §5.3.4（1.0/0.72/0.30/0.85）+ PIT 验证通过 + 单元测试全绿。

## 13. 裁定记录

| 日期 | 裁定 | 理由 |
|------|------|------|
| 2026-08-06 | 先出 Module A blueprint 再写代码 | C1 一票否决的地基，特征算错/PIT泄漏全链污染；100% AI 开发需硬契约防漂移；B/C 依赖 A 输出契约 |
| 2026-08-06 | 完整 13 参数 + 8 转换 + S2 十二维度 | 11_regime_backtest_validation_plan §8.1 用户裁定：直接完整版，验证后基于证据简化 |
| 2026-08-06 | #11 双向 / S2 机构补强暂存 | detect() 当前未消费，本模块先计算暂存，避免后续返工 |
| 2026-08-06 | **全面治本修正：14处糊弄点→2026前沿算法** | 用户要求"把所有糊弄人的全部重新算一遍"。6方向调研（Wyckoff/虹吸资金/VIX/筹码/Capitulation/新闻NLP/背离/衰竭）后，14处糊弄点全部替换为2026前沿算法：F2均线斜率→Hurst(DFA)+Kalman；#8模糊虹吸→前5%集中度+HHI+资金集中度；#9 KDJ>90模糊→Pivot-Pair单调配对；#10均线角度伪精确→Hurst衰退+ADX回落；#12换手率代理→华泰前沿VWAP三角分布(MOD-REGIME-005)；S2 capitulation加密货币指标→ACSI A股投降指数；S2 wyckoff名词堆砌→规则法TR+4触发器+FSM；S2 fund北向死数据→超大单IC加权；S2 policy/bad_news_flat定性词→NLP三层管道；T3 mainline逻辑错位→RRG+多周期交叉；T3 sentiment北向死数据→融资+主力资金 |
| 2026-08-06 | HMM 特征数 5→6 | F2拆为Hurst(DFA)+Kalman斜率双子特征，X矩阵(T,5)→(T,6)，同步更新regime_detector.py |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-REGIME-002`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-REGIME-002` 的 26 个 file 节点 | production | `extract_depgraph.py --modules MOD-REGIME-002` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-REGIME-002 | MOD-REGIME-002 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 26 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 14. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 14.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/regime/features/regime_data_loader.py` | ✅ 已实现 | |
| `src/zephyr/regime/features/risk_features.py` | ✅ 已实现 | |
| `src/zephyr/regime/features/wyckoff_engine.py` | ✅ 已实现 | |
| `src/zephyr/regime/regime_feature_builder.py` | ✅ 已实现 | |

### 14.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/regime/features/test_evolution_signals.py` | ✅ 已实现 | |
| `tests/regime/features/test_lppl_detector.py` | ✅ 已实现 | |
| `tests/regime/features/test_s2_breadth_thrust_score.py` | ✅ 已实现 | |
| `tests/regime/features/test_s2_capitulation_score.py` | ✅ 已实现 | |
| `tests/regime/features/test_s2_fund_score.py` | ✅ 已实现 | |
| `tests/regime/features/test_s2_spring_flag.py` | ✅ 已实现 | |
| `tests/regime/features/test_s2_three_yang_flag.py` | ✅ 已实现 | |
| `tests/regime/features/test_s2_valuation_score.py` | ✅ 已实现 | |
| `tests/regime/test_july_case_e2e.py` | ✅ 已实现 | |
| `tests/regime/test_overlay_features.py` | ✅ 已实现 | |
| `tests/regime/test_overlay_signals_builder.py` | ✅ 已实现 | |
| `tests/regime/test_risk_signal_builder.py` | ✅ 已实现 | |
| `tests/regime/test_synthetic_vix.py` | ✅ 已实现 | |

### 14.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §14（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


