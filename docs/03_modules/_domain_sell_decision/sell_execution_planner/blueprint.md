---
module_id: MOD-SELL-019
title: "卖出执行编排器蓝图 — 执行时序映射+跌停排队+KillSwitch清仓排序"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
design_maturity: production
layer: L03_sell_decision
layer_name: sell_decision
functional_domain: sell_decision
responsibility_domain: 
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-13"
last_updated: "2026-08-13"
priority: P1
blueprint_level: module
---

# MOD-SELL-019 | Sell Execution Planner 卖出执行编排器

> **域**: D_SELL_DECISION | **层**: L03 卖出决策 | **优先级**: P1 | **safety**: M | **ai_autonomy**: ai_modifiable
> **状态**: production | **版本**: 0.1.0 | **SSoT**: depgraph MOD-SELL-019 (node 9431508)

## 1. 模块定位

卖出执行编排——卖出信号到执行计划的落地层：①执行时序映射（止损盘中立即/止盈尾盘集中/强制清仓市价立即）②跌停板排队优先级（次日集合竞价挂单顺序）③Kill Switch 强制清仓排序（流动性差先卖防封死跌停）。产出喂给 40 号执行层订单分解/PricingPolicy。承载 42 号 §3.8 T+1 约束与 §3.9 回撤 Protocol 联动的卖出端落地算法。

依据: `42_sell_flow.md` §3.8 卖出执行时序算法 + 跌停板排队优先级算法 + §3.9 Kill Switch 强制清仓排序算法

## 2. 不变量 (INVARIANTS)

- **强制清仓**（KILL_SWITCH/BLACK_SWAN/BREAKOUT_FAIL_K）: 任何时段市价单立即执行，绕过融合，紧迫度 1.0
- **止损触发**（ATR_STOP/CHANDELIER_STOP/SUPPORT_BROKEN）: 盘中触发立即限价单；14:57 前可撤改挂，14:57 后挂收盘竞价单（上交所 2026 修订 §2.4.2 不可撤单）
- **止盈/换仓/退潮**（TRAILING_TP/REBALANCE/SENTIMENT_EBB）: 14:50-14:57 尾盘集中限价单
- **T+1 硬约束**: 当日买入不可卖（交易所物理约束，强制清仓亦不例外）
- **跌停约束**: 非强制清仓信号遇跌停不提交，标记待执行排队次日集合竞价；强制清仓遇跌停仍挂跌停价（P0 优先级）
- **跌停排队排序**: 紧迫度降序 → 亏损升序 → 仓位降序
- **Kill Switch 清仓排序**: 流动性升序（差的先卖防封跌停）→ 仓位降序 → 亏损升序

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| InvalidExecutionPlanInputError | ZA-SELL-0019 | signal_type 非枚举 / current_time 非 time 对象 |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 依赖 | zephyr.shared.foundation.errors | ZephyrBaseError | 错误基类 |
| 消费 | MOD-SELL-009 紧迫度评分 | urgency_score | 跌停排队排序键（调用方组装 LimitDownPosition） |
| 消费 | MOD-SELL-003 突破成败 | BREAKOUT_FAIL_K 信号 | 第 K 次失败强制清仓（K≥3） |
| 产出 | D-EX-CORE（40号执行层） | SellOrderPlan / 排序列表 | 订单分解/OpenOrderResolver/PricingPolicy 挂单价 |

## 5. 核心逻辑

### ① 执行时序映射
```
T+1(当日买入)           → BLOCKED_T1            # 物理约束最优先
强制清仓                → MARKET_ORDER_NOW      # 市价单, 跌停时挂跌停价排队
止损类 + 跌停           → LIMIT_DOWN_QUEUE      # 不提交, 次日集合竞价
止损类 + <14:57         → LIMIT_ORDER_NOW       # 盘中立即限价单
止损类 + ≥14:57         → CLOSING_AUCTION_LIMIT # 收盘竞价不可撤
止盈/换仓/退潮 + 跌停   → LIMIT_DOWN_QUEUE
止盈/换仓/退潮          → TAIL_BATCH_14_50      # 尾盘集中(与41号建仓同窗口反向)
```

### ② 跌停排队优先级（次日集合竞价挂单顺序）
```
sorted by: -urgency_score → unrealized_pnl_pct → -position_value
P0 Kill Switch / P1 回撤L3L4 / P2 ATR止损 → 挂跌停价
P3 止盈换仓 → 次日开盘价-0.5%
```

### ③ Kill Switch 清仓排序
```
sorted by: liquidity_score → -position_value → unrealized_pnl_pct
流动性差先卖（防封死跌停无法成交）——首要目标"全部成交"而非"卖好价"
```

## 6. 接口

### 输入
```python
SellExecutionPlanner.schedule_sell_order(
    signal_type: SellExecutionSignal,   # 9 类执行信号
    current_time: time,                 # 当前时间(14:57 分界)
    *, buy_date: date | None = None,    # 拟卖仓位买入日期(T+1校验)
    is_limit_down: bool = False,        # 当前是否跌停
    today: date | None = None,          # 测试注入
) -> SellOrderPlan

SellExecutionPlanner.rank_limit_down_orders(
    positions_in_limit_down: list[LimitDownPosition],
) -> list[LimitDownPosition]

SellExecutionPlanner.rank_kill_switch_liquidation(
    positions: list[LiquidationPosition],
) -> list[LiquidationPosition]
```

### 输出
- `SellOrderPlan`（action/order_type/window_note/reason）——喂 40 号订单分解
- 排序后持仓列表——喂 40 号 OpenOrderResolver

## 7. 设计决策

| 决策 | 理由 |
|------|------|
| 止损盘中立即而止盈尾盘集中 | 42号 §3.8：止损是"认错"每多持有一秒风险增加；止盈是"锁定利润"被动触发不急于一时，尾盘 U 型高流动性段成交更优 |
| T+1 校验优先于一切信号 | 交易所物理约束：当日买入任何信号都卖不了（含 Kill Switch），Kill Switch 对该类标的只能等次日 |
| 强制清仓遇跌停仍挂单 | 42号 §3.8 优先级表 P0：挂跌停价确保有买盘即成交；普通信号跌停不提交避免无意义占位 |
| 清仓流动性优先而非亏损优先 | 42号 §3.9：Kill Switch 首要目标全部成交，流动性差标的后卖可能封死跌停→暴露无法消除 |
| SellExecutionSignal 与收集器8类信号正交 | 执行编排层分类（KILL_SWITCH/BLACK_SWAN 等非收集器信号源），不复用 SellSignalType 防混淆 |

## 8. 测试计划

- 强制清仓三信号任何时段市价单
- 强制清仓遇跌停仍市价单（备注跌停排队）
- 止损 14:57 前限价单 / 14:57 后收盘竞价单 / 边界恰好 14:57
- 止损/止盈遇跌停排队次日
- 止盈/换仓/退潮尾盘集中
- T+1 当日买入拦截（含 Kill Switch）/ 昨日买入放行
- 输入校验（signal_type/time 非枚举非 time 对象）
- 跌停排队三级排序（紧迫度→亏损→仓位）
- Kill Switch 清仓三级排序（流动性→仓位→亏损）+ 空列表

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SELL-019`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SELL-019` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SELL-019` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SELL-019 | MOD-SELL-019 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 9. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 9.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

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
