---
blueprint_id: MOD-L02-023
module_id: MOD-L02-023
module_name: volume
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
path: src/zephyr/factor/technical_indicators/volume.py
granularity: file
responsibility_domain: 
---

# MOD-L02-023 volume 蓝图（成交量类技术指标）

> **module_id**: MOD-L02-023 | **域**: D_FACTOR | **优先级**: P1
> 代码：`src/zephyr/factor/technical_indicators/volume.py`（在产，MATURITY=production）
> depgraph：node 在册（D_FACTOR，granularity=file）；本蓝图为其 blueprint_path 落位件。

## 0. 定位

成交量类技术指标库，17 台指标类（OBV/MFI/VWAP/VR/AD/PVT/WVAD/VWMA/ADOSC/EOM/KVO/NVI/PVI/FORCE_INDEX/WAD/VO/MARKETFI），把成交量与价格结合度量资金进出劲道。继承 `TechnicalIndicatorBase`（MOD-L02-TI-BASE），经注册表装饰器入全局注册表。

## 1. 大白话简介

这一族回答"钱是在流进来还是流出去、量能配合得怎么样"。OBV 把上涨日的量累加、下跌日的量扣减，看资金净流入的总账；MFI 是带成交量权重的 RSI；VWAP 是当日的成交均价锚；VR 看上涨量对下跌量的倍数（通达信口径，平盘量两侧都计）；AD/PVT/WVAD/WAD 是各种口径的累积派发线，都是"量在价先"思路的不同实现。ADOSC/KVO/VO 是量的震荡器（快慢线差值），EOM 量"价格被推着走有多省力"，NVI/PVI 分别只看缩量日/放量日的聪明钱动向，FORCE_INDEX 把价格变动乘上量直接称"推力"多重。累积族（OBV/AD/PVT/WAD）首值为 0、无预热 NaN，H=L 等边界情形按设计计 0 不炸。

## 2. 输入输出

- 输入：`compute(data: pd.DataFrame)`，行情 OHLCV+amount 列（各台 meta.input_columns 声明）。
- 输出：`pd.DataFrame` 多列，列名经 meta.output_columns 映射 DDL。
- 错误契约：空 DataFrame→返回空 DataFrame 不抛；缺列→ValueError。
- 纯 pandas/numpy 自实现，同输入必同输出；WAD 取 Tulip 累积 sign 口径，VO 取百分比口径。

## 3. 指标册承接清单

技术指标册 `docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml` 中 module_id=MOD-L02-023 共 **17 条**：IND-VOLUME-001 ～ IND-VOLUME-017（连续无缺号；册内按施工批次乱序排列）。

## 4. 上下游承接

- 上游：行情 OHLCV+amount 数据由 `zephyr.data.implementations.internal_compute_provider` 供数（包级 autodiscover 动态接线：L545/L1113 延迟导入本包+注册表消费）。
- 下游：internal_compute_provider 计算落列（DDL 列映射）→ 指标结果表；sleeve alpha 择时消费。

## 5. 测试

`tests/zephyr/factor/technical_indicators/test_volume.py`

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
