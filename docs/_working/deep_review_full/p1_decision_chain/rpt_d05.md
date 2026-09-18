---
ttl: task_bound
doc_type: report
title: 深度审查报告——Regime特征构建器（D05）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：Regime特征构建器（D05）

- 状态: **已审**
- 级别: P0｜类型: 数据管线/算法
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/regime/regime_feature_builder.py:124`（827 行全文通读）；底座特征 `features/market_features.py`、`features/trend_features.py` 一并通读（本对象上游）
- 生产调用方: `index_regime_panel.py:96`（FEATURE_NAMES+RegimeFeatureBuilder 复用）、`scripts/tests/run_c1_shrinkage_validation.py`（real 模式，INVARIANTS 登记）、`risk_signal_builder.py`/`overlay_signals_builder.py`（经 feature_builder 透传数据源）、`framework_composer`（schedule→ShrinkageBacktestEngine）
- 测试文件: **无专属测试**——[TESTS] 头仅锚 `tests/regime/test_cross_sectional_features.py`（只覆盖 ALG-01 横截面特征列）；`tests/regime/test_breadth_fallback.py` 只覆盖广度补洞。核心 `build_features`/`build_shrinkage_schedule`/`_build_feature_risk`/`_quarter_end_dates`/`_ema_smooth_schedule` 无直接单测，仅被 C1 real 脚本与 phase2 验证间接覆盖。

## 1 对象快照

- 审查范围：MOD-REGIME-002 全文件 + 其直接消费的 6 特征底座函数（realized_vol_pct/cross_asset_corr/ad_ratio/volume_anomaly/hurst_dfa/kalman_slope）+ safe_float。排除项：ClickHouse 表真源质量（归 P2 数据域）；cross_sectional_features.py 细节（独立模块，抽审其接口约定）。
- 材料包缺项声明：数据画像（F1-F5 真实分布/NaN 率）未取；运行时日志未取。基线与 HEAD 无漂移（已验证）。
- 变更热力：16 次，域内并列第二热。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | F-A1 **无专属测试缺口（本审查核心确认）**：walk-forward 编排/PIT shift/EMA 平滑/首季度覆盖/风险分级映射五块逻辑零直接断言；C1 real 脚本是重验收但非回归级——任何重构可静默改变 schedule 口径而不红 | regime_feature_builder.py:14（[TESTS] 重锚注记）; tests/regime/ 目录清单 | P1 | `grep -rn "RegimeFeatureBuilder" tests/` 仅 test_breadth_fallback 与 cross_sectional 间接引用 |
| A | F-A2 **detect 异常→schedule=1.0 fail-open**：detect 抛错（含 D01 F-A3 TypeError 炸穿）当日记 warning 后记 1.0（满部署）——风险节流机制在故障日失效，方向=放大敞口；有日志但无告警/计数器 | regime_feature_builder.py:518-520 | P1 | 在窗口数据注入坏行跑 build_shrinkage_schedule，观察异常日=1.0 且无失败清单产出 |
| A | F-A3 warmup/缺失行 nan_to_num→0 进入 detect：窗口内部分 NaN 行被替换为人造 0 特征行，经 RobustScaler transform 后是训练分布外的合成点，HMM 后验被污染且无告警（全 NaN 才走 1.0 通道） | regime_feature_builder.py:505-506,488 | P2 | 造窗口含 3 行 NaN 跑 detect，对比 dropna 后窗口的后验差异 |
| A | F-A4 `_build_feature_risk` 断供判中性：safe_float(NaN/None)→0.0 → vol_pct=0 → risk=1.0——特征断供日危机地板静默失效（checklist #6 家族；数据画像未取，触发频率未知） | regime_feature_builder.py:497-502,778-785; features/regime_data_loader.py:181-189 | P2 | `safe_float(float("nan"))`→0.0；`_build_feature_risk(0,0,0)`→1.0 |
| A | F-A5 **F3 跨资产相关系数口径随数据可用性漂移**：创业板指 399006 于 2010-06 上线，此前 cross_close 只有两列→pair 均值从 1 对变 3 对，corr 均值的水平/波动口径在 2015 前后系统性不同；rolling.corr 短窗内 NaN 由 mean(skipna) 吸收，无口径切换标记 | market_features.py:101-111; regime_feature_builder.py:637-640 | P2 | 对 2010-2012 与 2016-2018 的 F3 序列做分布对比（水平差应显著） |
| A | F-A6 F2a Hurst 200 日窗的统计功效偏薄：DFA 估 H 在 n≈199（收益 198）点噪声大，尺度 4~49 仅约 10 个有效尺度；退化时静默返 0.5（中性）无计数 | trend_features.py:66-100; regime_feature_builder.py:251-252 | P3 | 对纯随机游走序列滚动算 hurst_dfa，观察 0.5 邻域外漂移率 |
| A | F-A7 PIT 链审查通过：features.shift(1)（:402）+scaler 仅 fit 训练窗（:463）+build_train_matrix [q-5y,q] 与 detect (q,next_q] 无重叠；EMA 平滑只看 t 及以前（:733-739）——四道 PIT 检查全部合规 | regime_feature_builder.py:402,463,453-481,733-739 | 已查无 | 逐行核对四处时序 |
| A | F-A8 `_build_feature_risk` 分级逻辑与 docstring 一致（0.90/0.75 阈值×下跌交集），#1 单参数经 _compute_risk_signal 的 risk_base=自身、resonance=1、clamp[0.3,1]——与 D01 侧公式对拍成立 | regime_feature_builder.py:742-785 ↔ regime_detector.py:885-910 | 已查无 | 手算 vol_pct=0.92,slope<0 → risk 0.30 |
| B | F-B1 6 特征列序与 D01 锚定假设一致（FEATURE_NAMES: vol=0, slope=2）——实测核对通过；但契约仅注释级（同 rpt_d01 F-B1） | regime_feature_builder.py:102-109 | 已查无（一致） | 见 rpt_d01 F-B1 |
| B | F-B2 F4 广度双源混用（399106 断更→EQW_ALLA 补位）——历史事故（checklist#6 锚 91a3c77586）的修复在位：补洞有日志计数、比值自归一论证在 docstring；但 fallback 查询失败时"维持 0 填充旧行为"（adv=dec=0→ad_ratio=0 中性），静默降级仅 warning | regime_feature_builder.py:577-635 | P2 | 断开 kline_index_calc 表跑 _load_breadth_fallback 观察 None→0 填充 |
| B | F-B3 指数 close 为价格指数（不复权）——对 HV/z-score/corr 属一阶差分口径，除息跳变影响微小且指数本身无复权概念，口径成立；个股面板已按裁定#257④ 用 close_hfq（:663-668），宁缺毋假 | regime_feature_builder.py:653-668 | 已查无 | 读 _load_stock_panel SQL 注释与 ifNull(nan) 语义 |
| B | F-B4 SQL 全部 f-string 拼接，参数均为内部常量/int() 强转（注入面≈0），但表名经 TableRegistry（宪法 RULE-SSOT 方向正确） | regime_feature_builder.py:550-560,684-694 | 已查无 | 读两处 SQL 构造 |
| C | F-C1 消费方=shrinkage schedule→ScheduleShrinkageProvider→ShrinkageBacktestEngine（裁定#270 边界节流）+index_regime_panel 特征复用；**schedule 缺日行为未在本对象闭环**：首季度边界前的 backtest 日期不进 schedule（detect_start=max(q+1, backtest_start) 而 quarter_ends 始于 data_load_start+train_years）→2015-01-01~2015-03-31 类区间依赖 Provider 缺省（缺省值方向未核，归 framework_composer 收口） | regime_feature_builder.py:435-481 | P2 | 取 backtest_start 早于首个季度边的配置跑 build_shrinkage_schedule，检查 schedule 键范围 |
| C | F-C2 爆炸半径=全账户（本对象是 regime 链唯一数据入口，HMM 6 特征+风险+overlay 三参全经此组装） | regime_feature_builder.py:20-29 | P1(口径) | — |
| D | F-D1 兄弟排查：6 特征无第二实现（D10 复用本 builder）；`_build_feature_risk`（Phase 1 简化版）与 D12 RiskSignalConstructor（Phase 2a 13 参数）是**同一 #1 概念的两套承载**（enable_full_risk 开关切换），阈值口径独立维护——双份承载漂移风险（checklist#4 家族），好在开关显式且默认 Phase 2a 已成生产推荐（docstring :179-182） | regime_feature_builder.py:742-785 ↔ risk_signal_builder.py（rpt_d12） | P2 | 对同一 (vol_pct,slope) 两路各算 #1 比对 |
| D | F-D2 文档 vs 代码：docstring 自称"regime 链数据入口（ClickHouse→特征→检测器）"与实际职责一致；ALG-01 开关"默认 False 输出与历史逐字节一致"可由缓存+列序保证（尾部追加） | regime_feature_builder.py:43-48,276-279 | 已查无 | 开关关跑 build_features 对比列集 |
| E | F-E1 静默失败：F-A2（fail-open 1.0）+F-A4（断供中性）+F-B2（补洞失败→0）三处构成"数据断供→风险机制静默失效"族；均有 warning 级留痕但无失败日清单/告警出口，连续断供不可见 | regime_feature_builder.py:518-520,623-628,497-502 | P1(聚合) | 汇总三通道构造断供剧本 |
| E | F-E2 假阳性：`len(window)<10 or window.dropna().empty→1.0`——warmup 期满部署是保守方向，合规；但"dropna().empty"对**部分** NaN 行不放行（落到 F-A3 的 0 填充），阈值 10 行的定值无配置依据 | regime_feature_builder.py:488-490 | P3 | 边界行数实验 |
| E | F-E3 幂等/重跑：build_features/build_train_matrix 有进程内缓存（_features_cache），同实例重跑一致；跨实例重跑依赖 ClickHouse 数据版本（FINAL 语义），schedule 逐日 detect 确定性成立（D01 侧 n_init 固定 seed） | regime_feature_builder.py:235,309,650 | 已查无 | 同配置两实例对拍 schedule |
| E | F-E4 时序攻击面：features_shifted.loc[:dt] 若特征索引含乱序日期会取错窗——_load_index_kline ORDER BY+sort_index 保证升序（:559,575），EQW 补洞 drop_duplicates(keep last)——入序防御在位 | regime_feature_builder.py:559,575,634 | 已查无 | 乱序注入测试 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| # | 对照项 | 结论 | 来源 |
|---|---|---|---|
| 1 | walk-forward 季度重拟合+滚动训练窗+窗口内标准化 | **对等已有**——滚动重训/标准化仅用训练窗是 quant 文献标准做法（同 rpt_d01 来源 1 的 QuantInsti walk-forward 实现） | [QuantInsti: Regime Adaptive Trading in Python](https://blog.quantinsti.com/regime-adaptive-trading-python/)（QuantInsti） |
| 2 | DFA Hurst 用于市场状态特征 | **对等已有（带保留）**——DFA 估 H 为文献成熟法，但短窗（200 点）功效不足是已知问题，学界多用 ≥512 点；立卡候选：窗长提升或改用 R/S+hurst exponents 交叉验证（改造点=build_features :251 的 window 参数） | [LSEG Developers: Statistical & ML Market Regime Detection](https://developers.lseg.com/en/article-catalog/article/market-regime-detection)（LSEG，含 Hurst/vol 态判定综述） |
| 3 | A/D ratio（涨跌家数广度）作 regime 输入 | **对等已有**——advance/decline breadth 是经典市场广度指标（技术分析文献谱系），tanh(log((a+1)/(d+1)) 归一为项目自有改造，量纲自洽 | [QuantifiedStrategies: HMM Market Regimes](https://www.quantifiedstrategies.com/hidden-markov-model-market-regimes-how-hmm-detects-market-regimes-in-trading-strategies/)（QuantifiedStrategies，广度/波动类特征入 HMM 同款思路） |

## 4 缺陷清单（按严重级）

- **F-A1（P1）无专属测试**：现状=核心编排逻辑零直接断言 → 证据=[TESTS] 头仅锚横截面特征测试 → 影响=C1 real 脚本之外的重构无回归网，schedule 口径可静默漂移（checklist#3 测试缺位家族）；爆炸半径=全账户 Shrinkage → 建议修法=补 build_shrinkage_schedule 合成数据金测试（固定合成 K 线→断言 schedule 键集/PIT 边界/EMA 单调性与 1.0 通道）→ 验证法=`pytest tests/regime -k feature_builder` 现为空。
- **F-A2/E1（P1）fail-open 三通道聚合**：detect 异常→1.0（:518-520）、特征断供→risk 1.0（:778-785）、补洞失败→F4=0（:623-628）——故障日一致向"满部署/中性"降级且无失败日清单产出 → 建议修法=build_shrinkage_schedule 返回结构附 degraded_days 清单（或写 schedule 元数据），上报告警；最低成本=detect 异常日改用最近一日有效 shrinkage 而非 1.0（持有上节流态比突然满仓更符合风险机制语义，需 Owner 裁定方向）→ 验证法=注入坏行统计 1.0 日占比。
- **F-A5（P2）F3 口径随数据可用性漂移**：创业板指上线前 pair 数 1→3 的均值口径跳变 → 建议修法=固定 3 指数可用性掩码（不可用日 F3=NaN 走 dropna，宁缺毋混）或分段子标准化 → 验证法=对比 2012/2016 段 F3 分布。
- **F-A3/A4/B2/C1/D1（P2）**：见日志表；A3 修法=窗口内 NaN 行超阈值整窗降级；A4 修法=safe_float 失败计数暴露；C1 修法=与 framework_composer 收口确认 Provider 缺日默认值方向并文档化。
- **F-A6/E2（P3）**：Hurst 窗功效与 warmup 阈值定值，常规队列。

## 5 挂起疑问

1. ScheduleShrinkageProvider 对 schedule 缺日/非交易日 as-of join 的缺省值方向（1.0 还是 carry-forward）——需 framework_composer 侧证据，影响 F-C1 定级（若缺省=1.0 则与 F-A2 同族 fail-open 放大）。
2. F4 EQW_ALLA 补位源自身的数据画像（缺口率/与 399106 口径衔接段的重叠一致性）未取——两源混用的比值自洽论证是 docstring 推理，未经数据实证（数据画像缺项）。
3. enable_cross_sectional 开关在生产 C1 路是否启用未核（默认 False）——若启用，F-A3 的 0 填充面扩大到 10 列。

## 6 完备性自评

- 六轴全查：A（6 特征逐个数学四问+z-score/分位/tanh 边界行为；walk-forward 编排逐段）、B（7 条输入逐条追源）、C（schedule 消费链+缺日口）、D（特征无双实现确认+#1 双承载登记）、E（五问全过：静默失败 E1、假阳性 E2、断线 E1、幂等 E3、时序 E4）、F（3 条带来源）。
- 长尾清单：①F1-F5 真实数据画像（NaN 率/分位数）未取——A 轴"假设在本项目数据上成立吗"多为推理非实证；②ClickHouse 表结构/quality_flag 语义归 P2 数据域；③cross_sectional_features.py 4 列算法本体未深审（独立对象候选）；④run_c1_shrinkage_validation.py 脚本本体未审。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
