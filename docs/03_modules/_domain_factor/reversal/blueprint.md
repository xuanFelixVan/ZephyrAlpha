---
blueprint_id: MOD-L02-020
module_id: MOD-L02-020
module_name: reversal
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
path: src/zephyr/factor/technical_indicators/reversal.py
granularity: file
responsibility_domain: 
---

# MOD-L02-020 reversal 蓝图（反转类技术指标）

> **module_id**: MOD-L02-020 | **域**: D_FACTOR | **优先级**: P1
> 代码：`src/zephyr/factor/technical_indicators/reversal.py`（在产，MATURITY=production）
> depgraph：node 在册（D_FACTOR，granularity=file）；本蓝图为其 blueprint_path 落位件。

## 0. 定位

反转类技术指标库，4 台指标类（RSIDivergence/MACDDivergence/BOLLBreakout/VolumePriceDivergence），输出离散转向信号。原第 5 件 CandlestickPattern 已按裁定#233 退役。继承 `TechnicalIndicatorBase`（MOD-L02-TI-BASE），经注册表装饰器入全局注册表。

## 1. 大白话简介

这一族专门捕捉"涨势/跌势快到头了"的拐点信号：RSI 背离看价格创新高但 RSI 没跟上（劲道衰竭），MACD 背离看均线动能与价格脱节，布林突破看价格冲出通道后的回归，量价背离看放量不涨/缩量新高的不协调。背离检测是居中窗口找局部峰谷、比较相邻两峰/谷的价格与指标值（价新高+指标更低=顶背离），信号打在峰/谷确认点（极值点+peak_order），不偷看未来数据。输出只有三档：0=无信号、1=看涨、-1=看跌，下游拿来就能当开关用。

## 2. 输入输出

- 输入：`compute(data: pd.DataFrame)`，行情 OHLCV 列（各台 meta.input_columns 声明）。
- 输出：信号列 Float64（0.0=无信号，1.0=正信号看涨，-1.0=负信号看跌），列名经 meta.output_columns 映射 DDL。
- 错误契约：空 DataFrame→返回空 DataFrame 不抛；缺列→ValueError。
- 纯 pandas/numpy 自实现，同输入必同输出，无前视。

## 3. 指标册承接清单

技术指标册 `docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml` 中 module_id=MOD-L02-020 共 **5 条**：IND-REV-001、IND-REV-002、IND-REV-003、IND-REV-004、IND-REV-005。

## 4. 上下游承接

- 上游：行情 OHLCV 数据由 `zephyr.data.implementations.internal_compute_provider` 供数（包级 autodiscover 动态接线：L545/L1113 延迟导入本包+注册表消费）。
- 下游：internal_compute_provider 计算落列（DDL 列映射）→ 指标结果表；sleeve alpha 择时消费。
- 同族依赖：RSIDivergence/MACDDivergence 依赖 momentum（MOD-L02-019）的 RSI 与 trend（MOD-L02-021）的 MACD 底层计算。

## 5. 测试

`tests/zephyr/factor/technical_indicators/test_reversal.py`

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
