---
blueprint_id: MOD-REGIME-007
module_name: cross_sectional_features
domain: D_REGIME
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: testing
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
---

# MOD-REGIME-007 cross_sectional_features 蓝图

> 紧凑版（92 号清单波 2 ALG-01 落地配套）。设计真源：2026-08 架构审查报告 §4.3 + #ARCH-140。

## 0. 定位

regime 特征集的横截面结构补强：既有 6 特征全部由市场代理指数（沪深300）时序派生，横截面结构事件（指数未崩但小盘股踩踏、离散度/相关性结构剧变）在指数维度不可见。本模块提供 4 个横截面结构特征纯函数，补该盲区。

## 1. 特征清单（输出列序钉死）

| 列名 | 含义 | 口径 |
|---|---|---|
| cross_dispersion | 截面收益离散度 | 个股日收益截面 std（或 IQR/1.35 稳健版，默认 iqr），20 日滚动均值平滑 |
| avg_pairwise_corr | 平均成对相关 | 个股日收益两两 Pearson 相关均值，60 日窗；分层抽样 ~200 只（成交额 10 层等量，确定性种子，20 交易日再平衡） |
| vol_dispersion | 波动率离散 | 个股 20 日已实现波动率（年化×√252）的截面 std |
| momentum_breadth | 动量宽度 | 收盘价强于 MA20 的股票占比（%） |

## 2. 接口

`compute_cross_sectional_features(panel: pd.DataFrame, ...) -> pd.DataFrame`：输入 date×symbol 的 close/volume 面板，按 date 输出 4 列。纯函数无 IO。

## 3. 不变量

- PIT 严格：T 日特征只用 ≤T 数据；trailing 窗口，禁全样本归一
- 截面有效样本 <30 只 → 该日 4 列全 NaN（宁缺毋假）
- 个股缺数据该日剔除出截面，不填补（禁 ffill 造假收益）
- 抽样确定性：同面板同输出（种子 (random_state, t_reb)）
- 新特征列一律尾部追加，禁插既有 FEATURE_NAMES 6 列（detect 消费方列序契约）
- 进 HMM 主特征集必须经配置开关+A/B 对照，默认关

## 4. 接线

`RegimeFeatureBuilder(enable_cross_sectional=False)` 默认关（输出与现状逐字节一致）；开时 4 列 pd.concat 尾部追加，`active_feature_names()` 6→10 列联动 X 矩阵。个股面板支持注入（测试/离线）或经 `_load_stock_panel()` 从 kline_daily 惰性加载（每日成交额 top800）。

## 5. A/B 实证结论（2026-08-22）

真实 kline_daily（2024-01~2026-06，601 交易日）两臂 walk-forward regime 判定高度一致（schedule Pearson 0.9999，|Δ|均值 0.0007）——边际影响小，开关维持默认关，仅作诊断维度观察。报告：docs/_archive/2026-08-22-alg01-cross-sectional-ab.md。

## 6. 边界

- 不做横截面特征的交易信号化（本模块只供 regime 判定/诊断，不接策略链路）
- 抽样面板非全市场精确值（O(N²) 成本权衡，纪律见 §3）
- production 启用挂起等 Owner（宪章 B-007，testing 封顶）

## 7. 测试

tests/regime/test_cross_sectional_features.py（18 用例：PIT 截断/已知答案合成截面/样本不足 NaN/缺数据剔除/开关关逐字节回归）。
