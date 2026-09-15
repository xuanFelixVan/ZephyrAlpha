---
ttl: task_bound
title: T1-α 节点挖矿：RegimeFeatureBuilder 特征管道（MOD-REGIME-002）
session: st-qoder-t1a-20260915
date: 2026-09-15
parent: S11_assembled_backtest
---

# 挖矿节点 4：RegimeFeatureBuilder 特征管道（MOD-REGIME-002）

> 挖矿日期：2026-09-15 ｜ 会话：st-qoder-t1a-20260915 ｜ 唯源骨架：S11_assembled_backtest/nodes/
> 挖矿依据：regime_supply_chain_mining §5 子节点第 1 件——RSC-1 标签对齐核实对象、
> HMM 可信度的上游根基（特征工程质量直接决定"regime 错=权重错"生死线的输入端）。
> 链条=ClickHouse kline_index → 6 特征生产件（market_features/trend_features）→
> build_train_matrix/walk-forward → detect 窗口 → Shrinkage schedule。
> 产出=数据，采纳裁定归主力会话施工班。

## 1 现状盘点（逐条带 file:line 锚点）

### 1.1 管道架构（regime_feature_builder.py 761 行全读）

- **6 特征**（列序钉死 FEATURE_NAMES L102-109）：
  F1 realized_vol_pct（20日HV的250日分位，market_features.py:48-75）；
  F2a hurst_dfa / F2b kalman_slope（200日 rolling apply，trend_features.py:39-189）；
  F3 cross_asset_corr（000300/000905/399006 两两 60 日相关均值，market_features.py:83-111）；
  F4 ad_ratio（399106 涨跌家数 tanh 归一，market_features.py:119-142）；
  F5 volume_anomaly（20日 z-score，market_features.py:150-171）。
- **walk-forward**（build_shrinkage_schedule L372-537）：QE 季度边界（日历日）→
  训练窗 [q-5y, q] dropna+nan_to_num（build_train_matrix L351-370）→ RobustScaler 仅 fit
  训练窗（L461-463，PIT ✓）→ detect 窗口 features.shift(1) trailing 60 日（L400/483-486，
  PIT ✓）→ EMA α=0.15 平滑（L521-529，凸组合 PIT ✓）。
- **Phase 2a RiskSignalConstructor**（risk_signal_builder.py 344 行全读）：预计算全序列
  shift(1)+O(1) 切片；有效参数 9 个（_ACTIVE_PARAMS L68={1,2,3,5,6,7,8,9,10}）；
  #4/#12 永久 stub=1.0（L263）；#11/#13 opportunity 永久 0.0（L146）。
- **Phase 2c RegimeDataLoader**（regime_data_loader.py 608 行全读）：6 类数据源全
  fail-open（查询失败→None→维度降级，L211-217）；表名走 TableRegistry ✓。
- **生产写方**（print_regime_history.py:126-134, 279-286）：--risk-mode full /
  --overlay on / enable_phase2c=True 均为默认；--end 默认今天。

### 1.2 六向挖矿日志（信号 ✅ / 噪音 ✗ / 受阻 ⛔）

| # | 方向 | 判 | 发现（file:line） |
|---|------|----|------------------|
| 1 | F4 广度数据源 | ✅ P0 | **399106 advance_count 自 2026-07-03 断更**（CH 实测：adv>0 最后一天 2026-07-02，仅 2 行 ≥2026-07-01；表 max date 2026-09-15 但 adv=0）。根因：现役两 provider 都不进料——akshare_provider.py:7565 与 miniqmt_provider.py:1385 注释均承认 advance_count/decline_count 由 CH DEFAULT 填充（新浪源不提供）；历史 2015-2026-07 是旧进料。下游连环死：F4 恒 0（tanh(log(1/1))）→ HMM 六分之一输入塌缩 → #7 ad_ratio_extreme_coef 恒 1.0 → overlay 广度/three_yang 维度（overlay_signals_builder.py:61 同源）同吃死数据。regime_feature_builder.py:579 注释"近期断更处填 0"=已知但未立项 |
| 2 | NaN 策略训练/推断一致性 | ✅ P1 | **分布漂移**：训练 dropna 整行剔除（L364），detect 窗口 nan_to_num 零填充（L505）——部分 NaN 行变 0 向量喂 HMM，训练分布无此观测；RobustScaler 空间 0≠中性（(0-median)/IQR 可为极端位置）。当前 2015+ 窗口 warmup 完备未触发；换短 data_load_start / F4 断更后的 reindex+fillna(0)（L572,587-588 双层中和）即静默触发 |
| 3 | inf 钳制方向 | ✅ P1 | posinf/neginf→0.0（L369/L505）：inf 应 clip 到有限界，置 0=在分布中部制造假观测。与 #2 同修 |
| 4 | 13 参数名不副实 | ✅ P1 | 实际有效 9 参数：#4 time_incubation/#12 chip_structure 永久 stub（"Phase 2c 接"未发生，_ACTIVE_PARAMS L68 无 4/12）；#11/#13 机会恢复永久 0.0（NLP 未接，L145-146）→ _compute_risk_signal 的 recovery 项生产死路，Shrinkage 永无上修抵消。spec §5.3.3 的"13 参数"承诺与实现偏差未披露 |
| 5 | 派生涨跌停误分类 | ✅ P2 | kline_daily 派生 ±9.5% 阈值（regime_data_loader.py:416-425）把创业板/科创板 20% 板的大涨大跌**误标**为涨停/跌停（12% 涨幅≠涨停），不止"覆盖 70%"——leader/one_day_mainline T3 维度被系统性虚增 |
| 6 | 多分时聚合注释谎言 | ✅ P3 | _load_single_etf_kline 注释"按交易日聚合"（L525）但代码未聚合（L526 仅 set_index）；聚合实际在消费端 groupby(level)（risk_signal_builder.py:334）——**功能核实正常**（60min 表 trade_date 按日截断、一日多 bar 实测），仅注释误导 |
| 7 | 过期默认值 | ✅ P3 | builder/RegimeDataLoader 默认 backtest_end="2026-06-30" 已过期；生产传参无恙，但 smoke/验证脚本（_smoke_feature_builder.py:14 等）用默认值=静默截断窗口 |
| 8 | 超参无扫描记录 | ✅ P3 | kalman Q/R=0.01、归一化 10×std（trend_features.py:168-188）、Hurst 窗口 200 日（builder L250）、EMA α=0.15（L152）均无调参留痕（与 TDM 节点 SLE-3 同型欠账） |
| 9 | _rolling_apply 性能 | ✗ | 纯 Python 循环 hurst×4000 日（L722-738）——build_features 每进程缓存一次，离线可接受，噪音 |
| 10 | 孤儿件扫描 | ✅ | regime 包内 market_forecast_fusion **零消费**；institutional_regime_scorer / volatility_squeeze_breakout / regime_cycle_analyzer 仅 __init__ 转出口无真实消费方；style_regime_model 消费方在 signal_ashare（链外）；index_regime_panel 消费方=dashboard warroom |

## 2 业界对照（四门）

| 项 | 本仓 | 业界 | 判 |
|----|------|------|----|
| 特征集 | vol 分位+Hurst+Kalman+跨资产相关+广度+量能 z（6 维） | Hamilton/Guidolin 系 regime-switching 常用 vol/breadth/corr 组合，同型 | ✅ 来源可溯 |
| 降 4 态 | BIC+OOS 一致率 0.34<0.7 实证（regime 节点已核） | 状态数选择=标准难题，实证驱动 ✓ | ✅ 交叉验证 |
| 零填充 vs 删除 | 两处不同策略（#2 发现） | hmmlearn 不支持 NaN，必须二选一——但训练/推断必须同策略，业界共识 | ⚠️ A股/工程适配缺口 |
| breadth 数据 | 断更即恒 0 中和 | 美股 adv/dec 有交易所级源；A 股需自算（全市场日 K 涨跌家数可从 kline_daily 派生，零外部依赖） | ❌ 可回测性受损（断更段无法回放真实广度） |

## 3 堵点清单（按优先级，含验收）

| id | 优先 | 堵点 | 验收 |
|----|------|------|------|
| FPB-1 | P0 | 399106 涨跌家数断更两个月+（结构性：现役 provider 均不进料），F4/#7/overlay 广度维连环死 | 三选一：①kline_daily 全市场派生 adv/dec 回填断更段（零外部依赖，与 FPB-5 派生链同源）；②provider 补进料口；③换数据源。验收=2026-07-03 起回填非零 + 新增"adv/dec 新鲜度"巡检（>3 交易日无新数据告警） |
| FPB-2 | P1 | 训练 dropna vs 推断零填充分布漂移 + inf→0 假观测（#2/#3 合并修） | detect 窗口 NaN 行策略与训练对齐（drop 整行/插值/显式降级 schedule=1.0 三选一）；inf 统一 clip 到 ±3σ 有界；配单测（构造半 NaN 窗口断言不再产 0 向量进 HMM） |
| FPB-3 | P1 | 13 参数名不副实：#4/#12 永久 stub、#11/#13 机会恢复死路 | 二选一：接数据转正（#12 chip 引擎已有 chip_distribution_engine.py 402 行现成件；#11/#13 可接 news_sentiment 已有 loader）或 spec §5.3.3 显式降格为"9+2+2"并披露。机会恢复链路至少打通一条（bad_news_flat ← news_sentiment negative_count，数据已在） |
| FPB-4 | P2 | 派生涨跌停 ±9.5% 误分类 20% 板 | 派生 SQL 按板型分阈值（主板 10%/创业板科创板 20%/北交所 30%/ST 5%，板型经 stk_limit 三级解析链已有真源）；验收=抽样 10 只创业板 2026 年 >9.5% 未封板个股不再误标 |
| FPB-5 | P3 | 过期默认 backtest_end + 超参无留痕 + 孤儿件 | 默认值改动态或显式必填；超参登记调参台账；market_forecast_fusion 等孤儿件按退役审计流程处置（宪法 §4 触发率纪律） |

## 4 子节点清单

| 节点 | 为什么值得挖 | 入口 |
|------|-------------|------|
| overlay_signals_builder 8 转换评分件 | 即 regime 节点 §5 第 3 件（维度生产件），本节点未展开；1288 行 overlay_features + 728 行 builder | src/zephyr/regime/overlay_signals_builder.py |
| ALG-01 横截面特征 A/B | 默认关、X=(T,10) 实验臂从未跑对照（L43-48 自述"先证增量再谈转正"） | cross_sectional_features.py 556 行 + enable_cross_sectional 开关 |
| chip_distribution_engine 转正评估 | FPB-3 的 #12 现成件，402 行从未接入 | src/zephyr/regime/features/chip_distribution_engine.py |

## 5 封矿判定

- **本节点主体封批**：管道四层（特征生产/walk-forward/risk 构造/data loader）全读完毕，
  4 个 P0/P1 实锤（F4 断更/分布漂移/inf 钳制/13 参数偏差）均 concrete 到 file:line+验收；
  PIT 三层链核实一致（正面）；60min 聚合链核实有效（排除一条假信号）。
- **未枯竭部分转子节点**（§4 三件）：overlay 维度生产件（最大剩余矿脉）、ALG-01 A/B、chip 转正。
- 一句话结论：**PIT 纪律和降级链是全链纪律最好的段落之一，但"降级友好"正在反噬——
  F4 断更两个月静默恒 0、stub 永久化、机会恢复死路，全是同一个模式的产物：
  fail-open 把数据债变成了不可见的特征债。修法不是关 fail-open，是给每个降级加装"新鲜度巡检+披露台账"。**
