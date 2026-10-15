---
blueprint_id: MOD-TRADING-009
module_id: MOD-TRADING-009
module_name: trading_order_aggregate
domain: D_TRADING
doc_type: blueprint
ttl: permanent
design_maturity: production
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.1"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_TRADING
path: src/zephyr/trading/trading_order_aggregate.py
granularity: file
responsibility_domain: 
---

# MOD-TRADING-009 trading_order_aggregate 蓝图（核心聚合 AGG-TRD-01 TradingOrder）

> **module_id**: MOD-TRADING-009 | **域**: D_TRADING | **优先级**: P1
> **来源**: B6-08087（AUD-DRAFT-001-DIGEST P1 波 W-P1-23，CAND-TRD-009，D-TRADING §0）
> 代码：`src/zephyr/trading/trading_order_aggregate.py`

## 0. 定位

交易运营域 OMS 侧订单核心聚合（DDD 聚合根）。TSV 现状注记
"部分:src/zephyr/ex_core/order_manager.py"——订单管理逻辑在 EX 域，
TradingOrder 聚合根与领域事件未归位 D-TRADING。

运营视角订单聚合跟踪**业务全生命周期**（接收→派发→执行→成交→结算中→
已结算→已对账），与 EX 域执行段状态机粒度正交：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| ex_core/order_manager | MOD-L06-001 | 执行段状态机（PENDING→SUBMITTED→PARTIAL→FILLED/CANCELLED）+合规双闸+券商路由 | 本件不重复执行段状态机，仅消费其执行结果快照推进运营段状态 |
| trading_contracts/execution/order | MOD-INF-016 | CTR-004 Order 契约 re-export（数据载体） | 本件聚合根引用契约，不重复定义 |
| settlement_reconciliation | MOD-TRADING-003 | 交易级对账引擎（比对+差异+报告） | 本件运营状态 SETTLING→SETTLED→RECONCILED 由对账/结算事件驱动 |

不做什么：不重建执行段状态机（委托 MOD-L06-001）、不直接下单、不做对账
比对（委托 MOD-TRADING-003）。

## 1. 规则（确定性，Fail-Closed）

- **聚合根 TradingOrder**：order_id 唯一 + idempotency_key 幂等（同键重复
  注册返回既有聚合，不新建）。
- **运营状态机**：RECEIVED→DISPATCHED→EXECUTING→FILLED→SETTLING→
  SETTLED→RECONCILED；支路 REJECTED/CANCELLED 终态；非法转换
  Fail-Closed 抛 InvalidOrderTransitionError。
- **领域事件发布**：每次状态迁移产出不可变 OrderDomainEvent
  （order_id/from_status/to_status/occurred_at/payload），经注入式
  event_sink 发布；event_sink 缺失仅落聚合内事件日志（不阻断）。
- **事件溯源**：聚合内 events 元组只增不改（append-only），支持
  replay 重建状态。

---

## 2. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 2.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 2.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §2（本节）→ 知道「哪些已实现、在哪里」
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
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-TRADING-009`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-TRADING-009` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-TRADING-009` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-TRADING-009 | MOD-TRADING-009 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
