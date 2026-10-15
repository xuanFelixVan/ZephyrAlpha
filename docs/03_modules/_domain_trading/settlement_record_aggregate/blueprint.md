---
blueprint_id: MOD-TRADING-010
module_id: MOD-TRADING-010
module_name: settlement_record_aggregate
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
path: src/zephyr/trading/settlement_record_aggregate.py
granularity: file
responsibility_domain: 
---

# MOD-TRADING-010 settlement_record_aggregate 蓝图（核心聚合 AGG-TRD-02 SettlementRecord）

> **module_id**: MOD-TRADING-010 | **域**: D_TRADING | **优先级**: P1
> **来源**: B6-08088（AUD-DRAFT-001-DIGEST P1 波 W-P1-23，CAND-TRD-010，D-TRADING §0）
> 代码：`src/zephyr/trading/settlement_record_aggregate.py`

## 0. 定位

交易运营域结算记录核心聚合（DDD 聚合根）。TSV 现状注记
"部分:src/zephyr/trading/settlement_reconciliation.py"——对账逻辑已有，
SettlementRecord 聚合与差异事件未成形。

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| settlement_reconciliation | MOD-TRADING-003 | 纯对账引擎：逐笔比对+SettlementDrift+ReconciliationResult+告警回调（无生命周期、无工单） | 本件消费其差异结果建聚合，不重复比对逻辑 |
| broker_settlement_adapter | MOD-TRADING-005 | 券商结算单适配（记录源） | 数据流上游 |
| recon_runner | MOD-TRADING-007 | 回测 vs 模拟盘三层对账编排（写库） | 场景互补，非结算记录聚合 |

不做什么：不重建对账比对（委托 MOD-TRADING-003）、不查券商（委托
MOD-TRADING-005）、不写库（工单事件经 event_sink 发布，落库留装配批）。

## 1. 规则（确定性，Fail-Closed）

- **聚合根 SettlementRecord**：settlement_id 唯一 + idempotency_key 幂等
  （同键重复注册返回既有聚合）。
- **结算状态机**：PENDING→MATCHED / DISCREPANT→RESOLVED→CONFIRMED；
  非法转换 Fail-Closed 抛 InvalidSettlementTransitionError。
- **差异分类**：将对账差异归三档——PRICE_QTY_MISMATCH（价格/数量类）、
  MISSING_RECORD（缺失类）、FEE_REFERENCE（费用参考类，仅参考不升级工单）。
- **差异处理工单事件**：DISCREPANT 迁移产出 DiscrepancyTicket（ticket_id/
  category/drift_ids/status=OPEN），经注入式 event_sink 发布；
  工单关闭（RESOLVED）同步产出事件；event_sink 缺失仅落聚合内日志。

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
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-TRADING-010`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-TRADING-010` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-TRADING-010` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-TRADING-010 | MOD-TRADING-010 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
