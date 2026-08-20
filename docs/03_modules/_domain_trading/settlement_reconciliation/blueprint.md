---
module_id: MOD-TRADING-003
title: "结算对账器蓝图 — 盘后交易级对账+差异告警+结算报告"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
layer: L03_trading
layer_name: trading
functional_domain: trading
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P1
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-TRADING-003 Settlement & Reconciliation Engine — 结算对账器 蓝图

> **module_id**: MOD-TRADING-003 | **域**: D_TRADING | **层**: L03 交易运营
> **优先级**: P1 | **成熟度**: design | **对标能力**: C-017②(结算对账)
> **SSoT**: depgraph MOD-TRADING-003 | **设计真源**: D:\临时工作区\依赖图\18-D-TRADING-交易运营域.md §1 D-TRADING-02

## 1. 定位

结算对账器——盘后交易级对账基础设施。每日 15:30 后自动比对系统交易记录
(来自 D-EX-CORE 的 Fill)与券商结算单(Broker Settlement Record),
逐笔检测价格/数量/佣金差异及缺失记录, 产出结算报告并触发差异告警。

与 D-EX-CORE-56 持仓对账器互补:
- EX-56: **持仓级**对账(盘中5分钟, 比对 position quantity, 差异→冻结交易)
- TRADING-003: **交易级**对账(盘后15:30, 比对 trade price/qty/commission, 差异→告警+报告)

产出 E-TR-01 SettlementCompleted / E-TR-02 ReconciliationCompleted 事件
(阶段1用回调模式, 阶段2接入事件总线)。

属 A 类基础设施(确定性比对 + 容差检测), 纯消费层不修改 source 状态。
**纯基础设施: 不决定"买什么/何时买", 只负责"核对今天成交和券商结算单是否一致"。**

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | Fill 列表 (系统交易记录, CTR-005) | CTR-005 |
| 输入 | BrokerSettlementRecord 列表 (券商结算单) | 本模块定义 |
| 输入 | ReconciliationConfig (容差配置) | C 类参数 |
| 输入 | settlement_date (结算日期) | — |
| 输出 | ReconciliationResult (对账结果) | E-TR-02 |
| 输出 | SettlementReport (结算报告, 含哈希指纹) | E-TR-01 |
| 输出 | on_discrepancy 回调 (差异告警) | E-TR-02 |

## 3. 核心规则

### 3.1 对账匹配逻辑

逐笔比对系统 Fill 与券商 BrokerSettlementRecord, 按 trade_id (broker_fill_id
或 order_id)配对:

```
配对键: fill.broker_fill_id (优先) 或 fill.order_id (回退)
配对后逐字段比较:
  - price:  abs(fill.fill_price - record.settlement_price) > price_tolerance → PRICE_MISMATCH
  - quantity: abs(fill.filled_quantity - record.settlement_quantity) > quantity_tolerance → QUANTITY_MISMATCH
  - commission: abs(fill.commission - record.commission) > commission_tolerance → COMMISSION_MISMATCH
```

### 3.2 缺失记录检测

```
MISSING_IN_SYSTEM:   broker 有记录但 system 无对应 Fill
MISSING_IN_BROKER:   system 有 Fill 但 broker 无对应记录
```

### 3.3 容差配置 (ReconciliationConfig)

| 参数 | 默认值 | 说明 |
|------|--------|------|
| price_tolerance | 0.01 | 价格差异容忍度(元) |
| quantity_tolerance | 0 | 数量差异容忍度(股, A股必须精确匹配) |
| commission_tolerance | 0.01 | 佣金差异容忍度(元) |

容差全部为 C 类可调参数, 非硬编码。

### 3.4 结算报告哈希指纹

```
report_hash = SHA-256(canonical_json({
    settlement_date, portfolio_id, total_trades, matched_trades,
    drift_count, drifts_summary, generated_at
}))
```

防篡改校验, 与 POS-009/EX-15 审计记录器哈希链模式一致。

## 4. 关键不变量 (INVARIANTS)

- 所有金额/数量比较使用 Decimal, 禁止 float
- BrokerSettlementRecord / SettlementDrift / ReconciliationResult / SettlementReport 为 frozen dataclass (不可变)
- reconcile() 纯读不修改 source 状态(不修改 Fill 列表/不修改 Broker 记录)
- on_discrepancy 异常不阻断对账主流程(catch + log)
- 冻结集概念不适用本模块(对账差异触发告警, 不冻结交易——冻结归 EX-56)

## 5. 错误契约

- `InvalidSettlementInputError` (ZA-TR-0003): 输入数据非法(如空结算日期/负价格)

## 6. 数据模型

```python
class DriftType(str, Enum):
    PRICE_MISMATCH = "price_mismatch"
    QUANTITY_MISMATCH = "quantity_mismatch"
    COMMISSION_MISMATCH = "commission_mismatch"
    MISSING_IN_SYSTEM = "missing_in_system"
    MISSING_IN_BROKER = "missing_in_broker"

@dataclass(frozen=True)
class BrokerSettlementRecord:
    trade_id: str           # 券商结算单交易ID (对应 Fill.broker_fill_id)
    order_id: str           # 关联订单ID (回退配对键)
    symbol: str
    settlement_price: Decimal
    settlement_quantity: Decimal
    commission: Decimal
    settlement_date: str    # YYYY-MM-DD

@dataclass(frozen=True)
class SettlementDrift:
    trade_id: str
    symbol: str
    drift_type: DriftType
    system_value: Decimal | None   # 系统侧值 (缺失时为 None)
    broker_value: Decimal | None   # 券商侧值 (缺失时为 None)
    diff: Decimal | None           | 差值 (缺失记录时为 None)

@dataclass(frozen=True)
class ReconciliationResult:
    timestamp: datetime
    settlement_date: str
    matched: bool                   # True=无差异
    drifts: tuple[SettlementDrift, ...]
    total_system_trades: int
    total_broker_trades: int
    matched_trades: int

@dataclass(frozen=True)
class SettlementReport:
    report_id: str
    settlement_date: str
    portfolio_id: str
    generated_at: datetime
    result: ReconciliationResult
    report_hash: str
    schema_version: str = "1.0"
```

## 7. API

```python
class SettlementReconciler:
    def __init__(
        self,
        config: ReconciliationConfig | None = None,
        on_discrepancy: Callable[[ReconciliationResult], None] | None = None,
    ) -> None: ...

    def reconcile(
        self,
        system_fills: list[Fill],
        broker_records: list[BrokerSettlementRecord],
        settlement_date: str,
    ) -> ReconciliationResult: ...

    def generate_report(
        self,
        result: ReconciliationResult,
        portfolio_id: str,
    ) -> SettlementReport: ...
```

## 8. 依赖

- `zephyr.shared.contracts.fill` (Fill, CTR-005)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: D-REPORTING(结算报告), D-AUTONOMY(差异告警), D-PF-CORE(结算完成事件)
- 设计真源: D-TRADING §1 D-TRADING-02, §3.1 E-0100(D-EX-CORE消费), §4.2 E-TR-01/E-TR-02

## 9. 测试

- `tests/trading/test_settlement_reconciliation.py`
- 覆盖: 完全匹配(无差异)、价格差异、数量差异、佣金差异、
  系统缺失记录、券商缺失记录、混合差异、容差边界、
  回调触发/回调异常不阻断、报告哈希一致性、Decimal精度

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-TRADING-003`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-TRADING-003` 的 6 个 file 节点 | production | `extract_depgraph.py --modules MOD-TRADING-003` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-TRADING-003 | MOD-TRADING-003 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 6 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 10.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/trading/test_settlement_reconciliation.py` | ✅ 已实现 | |

### 10.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §10（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
