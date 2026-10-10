---
blueprint_id: MOD-L02-021
module_id: MOD-L02-021
module_name: trend
domain: D_FACTOR
doc_type: blueprint
ttl: permanent
design_maturity: production
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.1"
created: 2026-10-05
last_updated: 2026-10-05
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_FACTOR
path: src/zephyr/factor/technical_indicators/trend.py
granularity: file
responsibility_domain: 
---

# MOD-L02-021 trend 蓝图（趋势类技术指标）

> **module_id**: MOD-L02-021 | **域**: D_FACTOR | **优先级**: P1
> 代码：`src/zephyr/factor/technical_indicators/trend.py`（在产，MATURITY=production）
> depgraph：node 在册（D_FACTOR，granularity=file）；本蓝图为其 blueprint_path 落位件。

## 0. 定位

趋势类技术指标库，38 台指标类（MA/EMA/WMA/DEMA/MACD/ADX/DMI/CCI/SAR/TRIX/DKX/HMA/ZLEMA/KAMA/VORTEX/SUPERTREND/MCGINLEY/ICHIMOKU/BBI/ALLIGATOR/GMMA/GANN_HILO/MAMA/FRAMA/JMA/TEMA/TRIMA/T3/VIDYA/AVGPRICE/MEDPRICE/TYPPRICE/WCPRICE/INERTIA/QSTICK/SUPERSMOOTHER/HIGHPASS/PTREND），覆盖均线族、趋向族、自适应均线族、价格变换族与 Ehlers 滤波器族。继承 `TechnicalIndicatorBase`（MOD-L02-TI-BASE），经注册表装饰器入全局注册表。

## 1. 大白话简介

这一族回答"现在往哪个方向走、走了多久、多陡"。均线族（MA/EMA/HMA 等十余种）把每天的杂波抹平看方向；MACD/DMI/ADX/VORTEX 看多头空头谁占上风；SAR 直接在图上打止损反转点；一目均衡表（ICHIMOKU）是复合类，一套九根线看支撑压力与趋势。自适应均线族（KAMA/MAMA/FRAMA/JMA/VIDYA）会按行情吵不吵自动调快慢——震荡时放慢少被骗、单边时提速跟得上；Ehlers 滤波器族（SUPERSMOOTHER/HIGHPASS/PTREND）用信号处理思路把周期噪声滤掉留趋势。AVGPRICE/MEDPRICE/TYPPRICE/WCPRICE 是 OHLC 组合均价四件套。DKX/BBI 对齐 A 股行情软件标配口径（通达信/同花顺 3/6/12/24），读数与看盘软件一致。

## 2. 输入输出

- 输入：`compute(data: pd.DataFrame)`，行情 OHLCV 列（各台 meta.input_columns 声明，如 MACD 需 close）。
- 输出：`pd.DataFrame` 多列（如 MACD→dif/dea/macd 柱），列名经 meta.output_columns 映射 DDL；GMMA 一次出 12 条 EMA 列。
- 错误契约：空 DataFrame→返回空 DataFrame 不抛；缺列→ValueError。
- 纯 pandas/numpy 自实现，同输入必同输出。

## 3. 指标册承接清单

技术指标册 `docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml` 中 module_id=MOD-L02-021 共 **38 条**：IND-TREND-001 ～ IND-TREND-037（37 条，连续无缺号）+ IND-COMP-001（Ichimoku 复合类，批3 candidate→active）。

## 4. 上下游承接

- 上游：行情 OHLCV 数据由 `zephyr.data.implementations.internal_compute_provider` 供数（包级 autodiscover 动态接线：L545/L1113 延迟导入本包+注册表消费）。
- 下游：internal_compute_provider 计算落列（DDL 列映射）→ 指标结果表；sleeve alpha 择时消费。
- 同族依赖：DMI 的 ±DI 被 momentum（MOD-L02-019）的 DX 复用；MACD 底层被 reversal（MOD-L02-020）的 MACDDivergence 复用。

## 5. 测试

`tests/zephyr/factor/technical_indicators/test_trend.py`

---

## 6. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
