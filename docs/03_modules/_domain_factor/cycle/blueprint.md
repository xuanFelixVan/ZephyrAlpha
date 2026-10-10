---
blueprint_id: MOD-L02-029
module_id: MOD-L02-029
module_name: cycle
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
path: src/zephyr/factor/technical_indicators/cycle.py
granularity: file
responsibility_domain: 
---

# MOD-L02-029 cycle 蓝图（循环族技术指标）

> **module_id**: MOD-L02-029 | **域**: D_FACTOR | **优先级**: P1
> 代码：`src/zephyr/factor/technical_indicators/cycle.py`（在产，MATURITY=production）
> depgraph：node 在册（D_FACTOR，granularity=file）；本蓝图为其 blueprint_path 落位件。

## 0. 定位

循环族技术指标库，8 台指标类/11 输出列：Hilbert Transform 五件套（HT_DCPERIOD/HT_DCPHASE/HT_PHASOR/HT_SINE/HT_TRENDMODE，2026-09-14 批3 新建）+ EBSW + CONTINUATION/GPRED（Ehlers TASC 2025 学术卡清偿）。继承 `TechnicalIndicatorBase`（MOD-L02-TI-BASE）；HT 家族公共基类 `_HTBase` 单遍 `_ht_core` 后按 output_columns 切片，避免五件套各算一遍。

## 1. 大白话简介

这一族把行情当成"波"来听：市场经常在"转圈（循环）"和"直线走（趋势）"两种状态间切换，这族指标负责辨认现在处于哪种状态、这个圈转一圈要几天。HT 五件套用希尔伯特变换从价格里提取瞬时周期/相位——主导周期告诉你当前循环大约多少天（钳位在 6～50 天），正弦波把循环画成波浪、浪谷附近往往是转折点，趋势/循环模式直接给 0/1 开关告诉你是趋势市还是震荡市。实现采用相位累积口径（4 项 WMA 平滑→EMA 降噪→Ehlers 4-tap Hilbert 滤波器→逐根相位差 unwrap 限幅防跳变→瞬时周期=2π/Δφ→平滑），预热 63 根与 TA-Lib 对表。EBSW 是改进版正弦波，CONTINUATION 量趋势延续概率，GPRED 是 Griffiths 线性预测器往前外推。

## 2. 输入输出

- 输入：`compute(data: pd.DataFrame)`，行情 close 列（HT 组实参 price series）。
- 输出：`pd.DataFrame` 多列（HT_PHASOR/HT_SINE 双列，其余单列），列名经 meta.output_columns 映射 DDL。
- 错误契约：空 DataFrame→返回空 DataFrame 不抛；缺列→ValueError；预热 63 根输出 NaN。
- 纯 pandas/numpy 自实现（相位累积口径），同输入必同输出。

## 3. 指标册承接清单

技术指标册 `docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml` 中 module_id=MOD-L02-029 共 **8 条**：IND-CYC-001、IND-CYC-002、IND-CYC-003、IND-CYC-004、IND-CYC-005、IND-CYC-006、IND-CYC-007、IND-CYC-008。

## 4. 上下游承接

- 上游：行情 close 数据由 `zephyr.data.implementations.internal_compute_provider` 供数（包级 autodiscover 动态接线：L545/L1113 延迟导入本包+注册表消费）。
- 下游：internal_compute_provider 计算落列（DDL 列映射）→ 指标结果表。

## 5. 测试

`tests/zephyr/factor/technical_indicators/test_cycle.py`

---

## 6. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/factor/technical_indicators/cycle.py` | ✅ 已实现 | |

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
