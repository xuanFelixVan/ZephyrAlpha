---
module_id: MOD-EX-063
title: "D-TRADING-05 Pre-Market Checker 盘前检查器蓝图 — 限额/纪律预检/数据完整性/系统就绪 MVP"
doc_type: blueprint
status: Active
version: "0.1.0"
ttl: permanent
layer: L06_execution
layer_name: execution_core
functional_domain: execution_core
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P0
blueprint_level: module
blueprint_id: MOD-EX-063
domain_id: D_EX_CORE
path: src/zephyr/ex_core/premarket_checker.py
design_maturity: design
build_status: planned
granularity: file
ai_autonomy: ai_modifiable
safety: H
stability: evolving
responsibility_domain: 
---

# MOD-EX-063 D-TRADING-05 Pre-Market Checker 盘前检查器蓝图

> **module_id**: MOD-EX-063 | **域**: D_EX_CORE | **层**: L06 交易执行
> **优先级**: P0 | **来源**: CAND-EX-007（B10-02209，AUD-DRAFT-001-DIGEST P0 波 W2a）

## 1. 定位

盘前检查 = 机构 OMS 与 vnpy RiskManager 标配的**开盘前就绪闸**。
与存量 MOD-EX-024 `pre_execution_checker.py`（production，逐单四级硬拦：
熔断/时段/快照/否决）分工明确：MOD-EX-024 管**逐单执行前**，本模块管
**当日开盘前**——四道关全量核查，任一不过即当日不就绪（Fail-Closed，C-004 口径）。

四道关（顺序固定，全量评估不短路，报告聚合）：

1. **限额基线**——复用 `RiskLimits` 契约（CTR-003）：取值域校验
   （max_single_position/max_sector_concentration∈(0,1]、max_gross_leverage>0）
   + 基线日期须为当日（过期限额=LIMITS_STALE 阻断）；
2. **纪律预检**——合规/纪律违规清单须为空（违规即阻断）；
3. **数据完整性**——复用 data `quality_gate` 的 `QualityReport`（passed 须为真）；
4. **系统就绪**——子系统就绪映射须全真（未就绪子系统点名阻断）。

接入 boot_hooks：经 `_subscribe_eventbus_consumers` 消费方注册模式
（`subscribe_eventbus()` 幂等），订阅 `premarket.check.requested`，
核查完成发布 `premarket.check.completed`（EventBusBackpressure 字符串主题）。

## 2. 输入 / 输出

| 方向 | 内容 | 契约 |
|------|------|------|
| 输入 | trading_date + 注入探针（限额/纪律/数据质量/系统就绪）+ clock | RiskLimits / QualityReport / Mapping |
| 输出 | PremarketReport（ready、四道关逐项 PremarketCheckItem、evaluated_at） | frozen dataclass |

## 3. 核心规则

1. 四道关全部 Fail-Closed：探针异常 = 该关不过（PROBE_ERROR），绝不放行。
2. 全量评估不短路：四道关逐项出结果，ready = 全部通过。
3. 限额基线日期必须等于 trading_date（过期限额不得用于当日）。
4. 纯编排无 IO；探针全部注入，时钟可注入保判定确定性。
5. `subscribe_eventbus()` 幂等（重复注册去重）；未注册检查器实例时收到
   请求事件记 ERROR 并发布 ready=False（Fail-Closed，不臆造就绪）。

## 4. 依赖

| 依赖 | 模块 | 类型 |
|------|------|------|
| RiskLimits（限额契约） | zephyr.trading.trading_contracts.risk.risk_limits（MOD-INF-016） | import |
| QualityReport（数据质量契约） | zephyr.data.quality_gate（MOD-L00-004） | import |
| bus（事件总线背压） | zephyr.shared.event_bus（MOD-INF-016） | import |
| ZephyrBaseError（错误契约基类） | zephyr.shared.foundation.errors（MOD-INF-016） | import |

boot_hooks（MOD-INF-035）消费方列表登记为运行时装配（本模块提供
`subscribe_eventbus()` 标准入口）。

## 5. 测试锚点

- 四道关全过 → ready=True；
- 过期限额 → LIMITS_STALE 阻断；限额取值域越界阻断；
- 纪律违规清单非空 → 阻断；数据质量 passed=False → 阻断；
- 子系统未就绪点名；任一探针异常 → PROBE_ERROR 阻断（Fail-Closed）；
- 报告 frozen；订阅幂等；未接线收到事件 ready=False。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-EX-063`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-EX-063` 的 2 个 file 节点 | design | `extract_depgraph.py --modules MOD-EX-063` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-EX-063 | MOD-EX-063 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | testing | planned | ❌ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
