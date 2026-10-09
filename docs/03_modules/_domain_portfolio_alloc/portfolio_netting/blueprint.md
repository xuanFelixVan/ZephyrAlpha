---
module_id: MOD-PA-034
title: "组合层 v0 净额轧平与预算切分蓝图 — L-4 里程碑一"
doc_type: blueprint
status: Active
version: "0.1.1"
design_maturity: production
build_status: generated
ttl: permanent
layer: L02_pf_alloc
layer_name: pf_alloc
functional_domain: pf_alloc
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-10-07"
last_updated: "2026-10-07"
priority: P1
blueprint_level: module
responsibility_domain: 
---

# MOD-PA-034 Portfolio Netting — 组合层 v0 净额轧平与预算切分 蓝图

> **module_id**: MOD-PA-034 | **域**: D_PF_ALLOC | **层**: L02 组合分配
> **优先级**: P1 | **成熟度**: L1 🔵 骨架 → evolving | **建设标记**: ✅可建
> **立项**: L-4 多策略组合层引擎里程碑一（l5_project_cards_20261006.md 卡 L-4 范围①②）
> **SSoT**: depgraph MOD-PA-034 | **蓝图依据**: PP-001 整装组合 V0（trading_map_07_f_portfolio.md TDM-F-C1 预算切分 / TDM-F-C2-01 目标聚合与净额轧平）

## 1. 定位

多策略权重面（每策略一张 date×symbol 的目标权重 DataFrame）→ 净额轧平出组合净权重面。
属 A 类纯函数基础设施：无 IO、无状态、纯向量化；NaN=诚实缺供（不 fillna 掩盖）；
输入校验 fail-closed（非法输入抛 ValueError）。

与邻件的分工（防责任重叠）：
- MOD-PA-002 信号合成器：信号级（StrategySignal 列表，投票/共振/去重）——本件是权重面级（DataFrame 代数和），上游不同。
- MOD-PA-003 多策略资金分配器：单策略内部权重规整（容量/MaxDD/冷启动，权重和=1.0）——本件是跨策略聚合，下游不同。
- MOD-POS-021 FirmRiskAggregator：实盘 Firm 层风险聚合（position 域）——本件是 pf_alloc 研究/回测组合层，域不同。

## 2. 函数契约

### 2.1 net_positions(strategies: dict[str, pd.DataFrame]) -> pd.DataFrame

净额轧平（TDM-F-C2-01 intent netting）：
- 输入：策略名→权重面（index=日期，columns=标的，值=带符号目标权重，正多负空）
- 输出：同标的跨策略权重代数和（买 1000+卖 600=净买 400 的权重面版），符号保留=多空自然表达
- 两策略同票等量反向 → 净零行（对冲净额，省手续费的数学本体）
- NaN 传播诚实：任一策略该格缺供 → 净面该格 NaN（sum 非全并集列取交集语义）

### 2.2 split_capital(weights: pd.DataFrame, budget: dict[str, float]) -> pd.DataFrame

预算切分（TDM-F-C1 Millennium pod 模式，逐策略缩放后再轧平）：
- 输入：多策略权重面（strategy 前缀列或 MultiIndex 列）+ 策略名→资金比例
- 逐策略按 budget 缩放（各 sleeve 账本独立、互不挪用）→ 轧平出组合净面
- budget 须覆盖全部策略名、非负（负预算=ValueError，fail-closed）；未知策略名=ValueError

## 3. 不变量 (INVARIANTS)

- 纯向量化：无逐行 Python 循环，pandas 对齐语义完成
- NaN 诚实缺供：不 fillna、不默认 0 掩盖缺供
- 输入校验 fail-closed：空输入/负预算/未知策略名/非 DataFrame → ValueError
- 代数正确性：同票反向等量权重 → 净零（浮点容差内）
- 符号保留：轧平结果可为负（组合层面空头的自然表达）

## 4. 错误契约 (ERROR_CONTRACT)

| 错误 | 触发条件 |
|------|---------|
| ValueError | 空 strategies/负 budget/未知策略名/非 DataFrame 输入/权重面无列 |

## 5. 依赖关系

| 方向 | 模块 | 说明 |
|------|------|------|
| 依赖 | pandas | 权重面对齐与代数 |
| 产出 | L-4 范围③④（调权全链/组合聚合层） | v0 净面为后续里程碑输入 |

## 6. 挂图

- TDMAP-001:TDM-F-C1（预算切分）
- TDMAP-001:TDM-F-C2-01（目标聚合与净额轧平）

## 7. 测试

tests/research/pf_alloc/test_portfolio_v0.py：轧平代数正确性（反向净零）/预算切分比例精确性/
NaN 缺供不掩盖/fail-closed 校验（负预算/未知策略名抛 ValueError）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-PA-034`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-PA-034` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-PA-034` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-PA-034 | MOD-PA-034 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | generated | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/pf_alloc/core/portfolio_netting.py` | ✅ 已实现 | |

### 8.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/research/pf_alloc/test_portfolio_v0.py` | ✅ 已实现 | |

### 8.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §8（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
