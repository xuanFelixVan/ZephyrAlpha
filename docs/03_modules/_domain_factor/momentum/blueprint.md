---
blueprint_id: MOD-L02-019
module_id: MOD-L02-019
module_name: momentum
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
path: src/zephyr/factor/technical_indicators/momentum.py
granularity: file
---

# MOD-L02-019 momentum 蓝图（动量类技术指标）

> **module_id**: MOD-L02-019 | **域**: D_FACTOR | **优先级**: P1
> 代码：`src/zephyr/factor/technical_indicators/momentum.py`（在产，MATURITY=production）
> depgraph：node 在册（D_FACTOR，granularity=file）；本蓝图为其 blueprint_path 落位件。

## 0. 定位

动量类技术指标库，43 台指标类（KDJ/RSI/WR/ROC/MTM/CMF/UOS/AO/CMO/StochRSI/BIAS/PSY/LWR/DPO/TSI/SMI/FISHER/KST/CONNORSRSI/QQE/STC/RVGI/STOCH/AROON/AROONOSC/BOP/PPO/APO/DX/BRAR/CR/AC/FRACTALS/ELDER/COPPOCK/SQUEEZE/WAVETREND/RMI/PFE/FOSC/CTI/VHF/ER），衡量价格涨跌劲头与超买超卖。继承 `TechnicalIndicatorBase`（indicator_base，MOD-L02-TI-BASE），经注册表装饰器入全局注册表，供 internal_compute_provider 动态接线消费。

## 1. 大白话简介

这一族回答"现在涨（跌）得有没有劲、是不是涨过头了"。KDJ 看随机摆动、RSI 看涨跌天数的力气对比、ROC/MTM 看比 N 天前涨了百分之几；BIAS 看股价偏离均线多远、PSY 数最近上涨天数占比；TSI/FISHER/KST 等是平滑降噪后的劲头读数；BRAR/CR 看人气与意愿的能量。算法口径对齐通达信（KDJ 的 K/D 用通达信 SMA(X,N,1) 平滑而非标准 EMA；RSI 用 SMA(up)/SMA(|Δ|)×100），保证与股民看盘软件读数一致；LWR 是慢速威廉、方向与 KDJ 相反。DX 复用 trend 模块 DMI 的 ±DI，不重复造轮子。

## 2. 输入输出

- 输入：`compute(data: pd.DataFrame)`，行情 OHLCV 列（各台 meta.input_columns 声明，如 KDJ 需 high/low/close）。
- 输出：`pd.DataFrame` 多列（如 KDJ→kdj_k/kdj_d/kdj_j），列名经 meta.output_columns 映射 DDL。
- 错误契约：空 DataFrame→返回空 DataFrame 不抛；缺列→ValueError。
- 纯 pandas/numpy 自实现，无第三方 TA 库依赖；同输入必同输出。

## 3. 指标册承接清单

技术指标册 `docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml` 中 module_id=MOD-L02-019 共 **43 条**：IND-MOM-001 ～ IND-MOM-043（连续无缺号；册内按施工批次乱序排列）。

## 4. 上下游承接

- 上游：行情 OHLCV 数据由 `zephyr.data.implementations.internal_compute_provider` 供数（包级 autodiscover 动态接线：L545/L1113 延迟导入本包+注册表消费）。
- 下游：internal_compute_provider 计算落列（DDL 列映射）→ 指标结果表；sleeve alpha 择时消费。
- 同族依赖：DX 复用 `zephyr.factor.technical_indicators.trend`（MOD-L02-021）的 DMI ±DI。

## 5. 测试

`tests/zephyr/factor/technical_indicators/test_momentum.py`
