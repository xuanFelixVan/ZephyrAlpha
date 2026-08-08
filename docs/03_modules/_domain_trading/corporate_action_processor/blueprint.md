---
module_id: MOD-TRADING-004
title: "公司行动处理器蓝图 — 除权除息/分红/配股/拆股+持仓成本调整"
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

# MOD-TRADING-004 Corporate Action & Fee Processor — 公司行动处理器 蓝图

> **module_id**: MOD-TRADING-004 | **域**: D_TRADING | **层**: L03 交易运营
> **优先级**: P1 | **成熟度**: design | **对标能力**: C-017③④⑤(除权除息/费率/公司行为)
> **SSoT**: depgraph MOD-TRADING-004 | **设计真源**: D:\临时工作区\依赖图\18-D-TRADING-交易运营域.md §1 D-TRADING-03

## 1. 定位

公司行动处理器——A股公司行动事件处理基础设施。处理除权除息/现金分红/送股/
配股/拆股等公司行动事件, 自动调整持仓数量和均价, 产出 E-TR-03
CorporateActionAdjusted 事件通知 D-PF-CORE 更新组合目标。

费率计算部分(佣金/印花税/过户费)已由 MOD-TRADING-002 PnLCalculator 实现,
本模块聚焦公司行动→持仓调整, 不重复费率逻辑。

属 A 类基础设施(确定性数学计算 + 规则驱动), 纯消费层不修改 source 状态。
**纯基础设施: 不决定"买什么/何时买", 只负责"公司行动发生后持仓怎么调"。**

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | CorporateAction (公司行动事件) | 本模块定义 |
| 输入 | symbol, quantity, avg_cost (持仓参数) | — |
| 输出 | PositionAdjustment (持仓调整结果) | E-TR-03 |
| 输出 | CorporateActionResult (批量处理结果) | E-TR-03 |
| 输出 | on_adjusted 回调 (调整通知) | E-TR-03 |

## 3. 核心规则

### 3.1 现金分红 (CASH_DIVIDEND)

```
avg_cost_new = max(0, avg_cost_old - dividend_per_share)
quantity 不变
```

### 3.2 送股 (STOCK_DIVIDEND)

```
quantity_new = quantity_old × (1 + stock_dividend_ratio)
avg_cost_new = avg_cost_old / (1 + stock_dividend_ratio)
```

### 3.3 配股 (RIGHTS_OFFERING)

```
quantity_new = quantity_old × (1 + rights_ratio)
avg_cost_new = (avg_cost_old + rights_price × rights_ratio) / (1 + rights_ratio)
```

### 3.4 拆股 (STOCK_SPLIT)

```
quantity_new = quantity_old × split_ratio       (split_ratio > 1 拆股, < 1 缩股)
avg_cost_new = avg_cost_old / split_ratio
```

### 3.5 除权除息综合 (EX_RIGHTS)

同时含现金分红+送股+配股的复合调整, 按顺序应用:
```
先现金分红 → 再送股 → 最后配股
```

## 4. 关键不变量 (INVARIANTS)

- 所有金额/数量计算使用 Decimal, 禁止 float
- CorporateAction/PositionAdjustment/CorporateActionResult 为 frozen dataclass (不可变)
- process() 纯计算不修改输入持仓状态
- on_adjusted 异常不阻断处理主流程(catch + log)
- avg_cost 调整后不为负(max(0, ...))
- 调整后总市值不变(除现金分红导致现金流出外)

## 5. 错误契约

- `InvalidCorporateActionError` (ZA-TR-0004): 输入数据非法(如负比例/负价格/零持仓)

## 6. 数据模型

```python
class CorporateActionType(str, Enum):
    CASH_DIVIDEND = "cash_dividend"       # 现金分红
    STOCK_DIVIDEND = "stock_dividend"     # 送股
    RIGHTS_OFFERING = "rights_offering"   # 配股
    STOCK_SPLIT = "stock_split"           # 拆股/缩股
    EX_RIGHTS = "ex_rights"               # 除权除息(复合)

@dataclass(frozen=True)
class CorporateAction:
    action_id: str
    symbol: str
    action_type: CorporateActionType
    ex_date: str                    # YYYY-MM-DD 除权除息日
    # 现金分红
    dividend_per_share: Decimal | None = None
    # 送股
    stock_dividend_ratio: Decimal | None = None   # 每10股送N股 → ratio=N/10
    # 配股
    rights_ratio: Decimal | None = None           # 每10股配M股 → ratio=M/10
    rights_price: Decimal | None = None           # 配股价
    # 拆股
    split_ratio: Decimal | None = None            # 1拆K → ratio=K

@dataclass(frozen=True)
class PositionAdjustment:
    action_id: str
    symbol: str
    action_type: CorporateActionType
    original_quantity: Decimal
    original_avg_cost: Decimal
    adjusted_quantity: Decimal
    adjusted_avg_cost: Decimal
    cash_delta: Decimal             # 现金变动(分红为正, 配股为负)

@dataclass(frozen=True)
class CorporateActionResult:
    timestamp: datetime
    ex_date: str
    adjustments: tuple[PositionAdjustment, ...]
    total_cash_delta: Decimal

class CorporateActionProcessor:
    def __init__(
        self,
        on_adjusted: Callable[[CorporateActionResult], None] | None = None,
    ) -> None: ...

    def process(
        self,
        action: CorporateAction,
        quantity: Decimal,
        avg_cost: Decimal,
    ) -> PositionAdjustment: ...

    def apply(
        self,
        actions: list[CorporateAction],
        positions: dict[str, tuple[Decimal, Decimal]],  # symbol -> (qty, avg_cost)
    ) -> CorporateActionResult: ...
```

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: D-PF-CORE(组合目标更新), D-REPORTING(公司行动报告)
- 设计真源: D-TRADING §1 D-TRADING-03, §4.2 E-TR-03

## 8. 测试

- `tests/trading/test_corporate_action_processor.py`
- 覆盖: 现金分红/送股/配股/拆股/除权除息复合、
  零持仓处理、负成本保护(max(0,...))、批量处理、
  回调触发/回调异常不阻断、Decimal精度、输入校验

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-TRADING-004`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-TRADING-004` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-TRADING-004` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-TRADING-004 | MOD-TRADING-004 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 9. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 9.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/trading/test_corporate_action_processor.py` | ✅ 已实现 | |

### 9.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §9（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
