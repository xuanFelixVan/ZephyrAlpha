---
blueprint_id: MOD-L02-022
module_id: MOD-L02-022
module_name: volatility
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
path: src/zephyr/factor/technical_indicators/volatility.py
granularity: file
responsibility_domain: 
---

# MOD-L02-022 volatility 蓝图（波动类技术指标）

> **module_id**: MOD-L02-022 | **域**: D_FACTOR | **优先级**: P1
> 代码：`src/zephyr/factor/technical_indicators/volatility.py`（在产，MATURITY=production）
> depgraph：node 在册（D_FACTOR，granularity=file）；本蓝图为其 blueprint_path 落位件。

## 0. 定位

波动类技术指标库，18 台指标类（ATR/BOLL/Keltner/Donchian/STDDEV/BandWidth/PercentB/HistVol/NATR/TRANGE/MASSI/PARKINSON/GARMAN_KLASS/ROGERS_SATCHELL/YANG_ZHANG/CHOP/CVI/ULCER），度量价格波动幅度与通道结构，含学术已实现波动率（RV）族四件。继承 `TechnicalIndicatorBase`（MOD-L02-TI-BASE），经注册表装饰器入全局注册表。

## 1. 大白话简介

这一族回答"这只票最近晃得多厉害、通道上下面在哪"。ATR 量典型一天上下晃多少格，是止损宽度的重要参考；BOLL/肯特纳/唐奇安三类通道给出"正常波动范围"，冲出去往往意味着行情变了；BandWidth/%B 是布林带的两个衍生读数（通道多窄、价格在带内哪个位置）；HistVol 用对数收益率标准差年化（×sqrt(252)）说清"年化波动率多少"。学术 RV 族四件（Parkinson/Garman-Klass/Rogers-Satchell/Yang-Zhang）利用高低开收全信息把波动估得更准，Yang-Zhang 还专门处理隔夜跳空。口径对齐通达信：ATR 用 MA 平滑（非 Wilder RMA）、STD 用总体标准差 ddof=0。

## 2. 输入输出

- 输入：`compute(data: pd.DataFrame)`，行情 OHLCV 列（各台 meta.input_columns 声明，RV 族需开高低收四价）。
- 输出：`pd.DataFrame` 多列（如 BOLL→上/中/下轨三列），列名经 meta.output_columns 映射 DDL。
- 错误契约：空 DataFrame→返回空 DataFrame 不抛；缺列→ValueError。
- 纯 pandas/numpy 自实现，同输入必同输出。

## 3. 指标册承接清单

技术指标册 `docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml` 中 module_id=MOD-L02-022 共 **18 条**：IND-VOL-001 ～ IND-VOL-018（连续无缺号；册内按施工批次乱序排列）。

## 4. 上下游承接

- 上游：行情 OHLCV 数据由 `zephyr.data.implementations.internal_compute_provider` 供数（包级 autodiscover 动态接线：L545/L1113 延迟导入本包+注册表消费）。
- 下游：internal_compute_provider 计算落列（DDL 列映射）→ 指标结果表；sleeve alpha 择时消费。

## 5. 测试

`tests/zephyr/factor/technical_indicators/test_volatility.py`

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
