---
blueprint_id: MOD-SIG-086
module_id: MOD-SIG-086
module_name: selection_funnel_skeleton
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: production
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.1"
created: 2026-08-24
last_updated: 2026-08-24
owner: ZephyrAlpha-Owner
responsibility_domain: 
---

# MOD-SIG-086 selection_funnel_skeleton 蓝图

> 设计真源：21 号备忘录 §3.6（BM-SEL-16/17/18）+ SIGNAL-ARCH-001 双域归并 Owner 裁定（A4 落地）。
> 代码：`src/zephyr/signal_ashare/screening/selection_funnel_skeleton.py`

## 0. 定位

选股漏斗四层容量链（~7000→~1200→~300→~50，对应 BM-SEL-16/17/18 三层处理 +
容量链末段）的**层序、接口与数据流唯一真源**。SIGNAL-ARCH-001 裁定：双域
（D_FUNDAMENTAL_SIGNAL 的 selection_funnel.py 与 D_ASHARE_SIGNAL 的
tiered_screening_filter.py）各自实现归并为本骨架 + 两域薄适配层，适配层委托
骨架并注入本域参数/钩子，对外 API 签名不变。

落点 signal_ashare 的理由：与 A 股漏斗族（MOD-SIG-046/047/048/049）同域内聚；
signal_fundamental → signal_ashare 只读 import 有 sector_rrg 先例；shared 层定位
基础设施，信号业务契约不下放。

## 1. 接口

```python
def run_graded_exclusion(records, *, symbol_of, hooks: GradedExclusionHooks,
                         thresholds: GradedFilterThresholds, degraded=False) -> ExclusionOutcome
def run_preliminary_gates(records, *, symbol_of, hooks: PreliminaryGateHooks,
                          thresholds: PreliminaryThresholds,
                          capacity: CapacityTruncation | None = None, degraded=False) -> GateOutcome
def run_fine_scoring(records, *, symbol_of, hooks: FineScoreHooks, weights: FineScoreWeights,
                     top_n=50, degraded=False, tie_break="stable") -> tuple[ScoredItem, ...]
def run_funnel_chain(records, *, symbol_of, run_graded, run_screen, run_score) -> FunnelChainResult
def subset_by_kept(records, *, symbol_of, kept) -> list
def density_penalty_from_summary(density) -> float  # 鸭子类型；None→0.0
```

域特性注入位：板块幅度自推导（GradedExclusionHooks.is_limit_locked 闭包）/
容量截断（CapacityTruncation 参数，不注入则不截断）/密度鸭子类型
（FineScoreHooks.density_penalty + density_penalty_from_summary 规范取法）/
fundamental AUM 分级排除（GradedExclusionHooks.extra_tier_checks，位于成交额
与弃庄概率之间）/精筛同分双口径（tie_break: stable=fundamental 输入序，
symbol=A 股域字典序）。

## 2. 输出契约

`ExclusionOutcome(kept/excluded)`、`GateOutcome(kept/excluded/truncated)`、
`ScoredItem(symbol/raw_score/z_score/rank)`、`FunnelChainResult(graded/screened/scored)`。
骨架输出为域中立类型，适配层负责包装为本域结果（GradedFilterResult/
TieredFilterResult/PreliminaryScreenResult/FineSelectionResult 等）。

## 3. 不变量

- 漏斗单调收敛：各层 kept ⊆ 输入；一层只排除不评分、三层只评分不排除
- 排除归因串两域一致（physical:*/gate:new_stock/tier:*/prob:*/dim:*）
- 纯函数无副作用；不 import 密度预测实现（鸭子类型解耦）；不感知板块枚举
- 精筛 std≈0 时 Z 置 0 按 raw 兜底排名；同名标的后出现记录覆盖

## 4. 降级行为

- 一层未就绪 → 仅物理排除（涨跌停封死/停牌硬剔除，ST/门禁/分级/概率放行）
- 二层未就绪 → 全量放行进精筛（算力风险告警由调用方负责）
- 三层未就绪 → 等权综合评分（四维基础分+主力五维等权）
- ERROR_CONTRACT：capacity.target<=0 → ValueError（降级路径同效，对齐 047 口径）；
  tie_break 非法值 → ValueError；密度摘要缺字段 → AttributeError（装配层职责）

## 5. 边界（不做）

- 不实现任何域特有规则本体（板块幅度表在 046 适配层、AUM 阈值在 fundamental 适配层）
- MOD-SIG-047（容量截断）/MOD-SIG-048（密度鸭子类型）两模块本批不迁移，骨架仅
  提供等价注入位保真；后续是否改薄适配由 Owner 另行裁定
- 权重/阈值按 memo 契约"经验初值待 G09/实盘校准"口径落常量，不做过拟合调参

## 6. 测试

tests/signal_ashare/screening/test_selection_funnel_skeleton.py（21 例：三层排除/放行语义、
降级链路、extra_tier_checks 注入位、容量截断注入位、密度鸭子类型、tie_break 双口径、
链式数据流）

---

## 7. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 7.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/signal_ashare/screening/selection_funnel_skeleton.py` | ✅ 已实现 | |

### 7.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §7（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-086`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-086` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIG-086` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-086 | MOD-SIG-086 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
