---
blueprint_id: MOD-L02-031
module_id: MOD-L02-031
module_name: chips
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
path: src/zephyr/factor/technical_indicators/chips.py
granularity: file
responsibility_domain: 
---

# MOD-L02-031 chips 蓝图（筹码族技术指标）

> **module_id**: MOD-L02-031 | **域**: D_FACTOR | **优先级**: P1
> 代码：`src/zephyr/factor/technical_indicators/chips.py`（在产，MATURITY=production）
> depgraph：node 在册（D_FACTOR，granularity=file）；本蓝图为其 blueprint_path 落位件。

## 0. 定位

筹码族技术指标库，5 台指标类（CYQ 筹码分布 6 列/SCR 筹码集中度/CHIP_CONC_90/CHIP_CONC_70/CYC 成本均线 4 列，批10 施工 2026-09-21），基于换手率迭代的持仓成本分布模型。技术指标输入首次引入换手率 turnover_rate（c1_market.stock_daily_basic，仅 daily 周期）。继承 `TechnicalIndicatorBase`（MOD-L02-TI-BASE）；`_ChipsValidateMixin` 覆盖 validate 实现换手率软降级语义，`_ChipGrid` 封装价格网格+筹码质量分布的演进状态（越界扩张/当日铺量/衰减/日指标）。

## 1. 大白话简介

这一族回答"现在持仓的人平均成本是多少、谁赚谁亏、筹码集中不集中"。CYQ 用换手率一天天往前推演：每天有一部分旧筹码被换手"洗"给新买家，推演出全市场筹码堆在哪些价位上，由此算出获利盘比例（多少持仓是赚钱的）、平均成本线和 5/15/85/95 分位成本——算法只用过去+当日数据（PIT 安全），独立复算与中证 000852 近 20 日逐日 0 偏差对表。SCR/CHIP_CONC_90/70 是筹码集中度：数值越小说明筹码越挤在少数价位（庄家锁仓特征），90/70 是统计价位宽度的两个口径。CYC 是成本均线（通达信 CYC1/2/3/∞ 口径），把均价按换手率加权滚出来，比普通均线更贴近真实持仓成本。换手率是软输入：非 daily 周期或基础表缺数时按设计降级——CYQ/SCR 返回空 DataFrame（落表 NULL，不前填不前视），CYC 的 cyc_5/13/34 照算、cyc_inf 全 NaN。

## 2. 输入输出

- 输入：`compute(data: pd.DataFrame)`，行情 OHLCV+amount 硬列+换手率 turnover_rate 软列（仅 daily 周期由 provider 并入）。
- 输出：`pd.DataFrame` 多列（CYQ→获利盘/平均成本/cost_5/15/85/95 六列；CYC→cyc_5/13/34/inf 四列），列名经 meta.output_columns 映射 DDL。
- 错误契约：空 DataFrame→返回空 DataFrame 不抛；缺 OHLCV 硬列→ValueError；缺 turnover_rate→返回空 DataFrame 不抛（设计内降级）。

## 3. 指标册承接清单

技术指标册 `docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml` 中 module_id=MOD-L02-031 共 **5 条**：IND-CHIPS-001、IND-CHIPS-002、IND-CHIPS-003、IND-CHIPS-004、IND-CHIPS-005（CYQ/SCR/CHIP_CONC_90/CHIP_CONC_70/CYC）。

## 4. 上下游承接

- 上游：行情 OHLCV+amount（硬输入）与 `c1_market.stock_daily_basic` 换手率 turnover_rate（软输入，批9 数据批）由 `zephyr.data.implementations.internal_compute_provider` 供数（延迟导入本包+注册表消费）。
- 下游：internal_compute_provider 计算落列（DDL 列映射）→ 指标结果表。

## 5. 测试

`tests/zephyr/factor/technical_indicators/test_chips.py`

---

## 6. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/factor/analysis/tech_factor_pipeline.py` | ✅ 已实现 | |
| `src/zephyr/factor/technical_indicators/chips.py` | ✅ 已实现 | |

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
