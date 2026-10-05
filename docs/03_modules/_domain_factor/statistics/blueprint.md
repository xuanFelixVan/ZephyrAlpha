---
blueprint_id: MOD-L02-028
module_id: MOD-L02-028
module_name: statistics
domain: D_FACTOR
doc_type: blueprint
ttl: permanent
design_maturity: production
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-10-05
last_updated: 2026-10-05
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_FACTOR
path: src/zephyr/factor/technical_indicators/statistics.py
granularity: file
---

# MOD-L02-028 statistics 蓝图（统计族技术指标）

> **module_id**: MOD-L02-028 | **域**: D_FACTOR | **优先级**: P1
> 代码：`src/zephyr/factor/technical_indicators/statistics.py`（在产，MATURITY=production）
> depgraph：node 在册（D_FACTOR，granularity=file）；本蓝图为其 blueprint_path 落位件。

## 0. 定位

统计族技术指标库，9 台指标类/10 输出列（CORREL/BETA/LINEARREG+TSF 双列/ROLLVAR/LINEARREG_ANGLE/SLOPE/INTERCEPT/STDERR/ZSCORE），滚动统计与线性回归基建，对齐 TA-Lib Statistic Functions 组（通达信无对应函数，口径注明 TA-Lib）。继承 `TechnicalIndicatorBase`（MOD-L02-TI-BASE），经注册表装饰器入全局注册表。

## 1. 大白话简介

这一族是量化统计的"工具尺"：CORREL 量价格和成交量最近 30 天有多同涨同跌（相关系数），BETA 量量价之间的弹性倍数；LINEARREG 一族把最近 14 天收盘价拟合成一条直线——SLOPE 是每天涨多少（斜率）、ANGLE 换算成角度、INTERCEPT 是直线起点、LINEARREG 是拟合值、TSF 是顺着直线往前猜一步的预测值（同类双列）；STDERR 量这些点离拟合线平均偏多远（残差标准误差，sqrt(SSR/(N−2)) 口径）；ROLLVAR 是滚动方差（ddof=0，与 BOLL 的 std 口径一致），ZSCORE 量当前值偏离均值几个标准差——超过 2 就是统计意义上的"异常"。默认 close×volume 对是量价统计的公共基建。

## 2. 输入输出

- 输入：`compute(data: pd.DataFrame)`，行情 OHLCV 列（默认 close×volume 对，滚动窗口）。
- 输出：`pd.DataFrame` 多列（LINEARREG 出 fitted+tsf 双列），列名经 meta.output_columns 映射 DDL。
- 错误契约：空 DataFrame→返回空 DataFrame 不抛；缺列→ValueError。
- 纯 pandas/numpy 自实现，同输入必同输出。

## 3. 指标册承接清单

技术指标册 `docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml` 中 module_id=MOD-L02-028 共 **9 条**：IND-STAT-001、IND-STAT-002、IND-STAT-003、IND-STAT-004、IND-STAT-005、IND-STAT-006、IND-STAT-007、IND-STAT-008、IND-STAT-009。

## 4. 上下游承接

- 上游：行情 OHLCV 数据由 `zephyr.data.implementations.internal_compute_provider` 供数（包级 autodiscover 动态接线：L545/L1113 延迟导入本包+注册表消费）。
- 下游：internal_compute_provider 计算落列（DDL 列映射）→ 指标结果表。
- 同族约定：ROLLVAR ddof=0 与 volatility（MOD-L02-022）BOLL std 口径一致，保证同窗同方差读数。

## 5. 测试

`tests/zephyr/factor/technical_indicators/test_statistics.py`
