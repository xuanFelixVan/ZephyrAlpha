---
module_id: MOD-SIM-002
title: "策略仿真器蓝图 — 策略沙箱+信号模拟+组合模拟"
doc_type: blueprint
status: Active
version: "0.1.3"
design_maturity: production
build_status: production
ttl: permanent
layer: L_SIMULATION
layer_name: simulation
functional_domain: simulation
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-SIM-002 Strategy Simulator — 策略仿真器 蓝图

> **module_id**: MOD-SIM-002 | **域**: D_SIMULATION | **层**: L_SIMULATION 仿真层
> **优先级**: P0 | **成熟度**: L1 🔵 骨架 → production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-SIM-002 | **设计真源**: D:\临时工作区\依赖图\19-D-SIMULATION-仿真域.md §1 D-SIMULATION-02 + §4 决策5(L2+L3)

## 1. 定位

策略仿真器——策略沙箱, 在隔离环境中对模拟市场数据运行注入的策略, 仿真信号生成(L2)+组合构建(L3)两个流水线阶段, 产出 SimulationResult 供 SIM-012 结果分析器消费。

与 D_BACKTEST 的边界(决策#1): 回测=过去怎样(重放历史, 确定), 仿真=如果怎样(what-if, 可注入模拟场景/合成数据)。本模块是仿真域的执行核心, what-if 特性来自调用方传入的模拟市场数据(可由 SIM-005 场景生成器 / SIM-01 市场仿真产生)。

属 A 类基础设施(确定性编排: 逐 bar 调用注入的 signal_fn → 目标组合 → 撮合 → 净值跟踪), 策略逻辑由调用方注入, 本模块不内置任何策略决策。阈值(佣金/滑点/初始资金)为 C 类可调参数。

设计真源: D-SIMULATION-02 "策略仿真器+策略沙箱+信号模拟+组合模拟 | 专业标配" + 决策5 "SIM-02(L2+L3)"。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 模拟市场数据 DataFrame + StrategySpec(signal_fn 注入) + Config | 来自 SIM-005/SIM-01 或直接传入 |
| 输出 | SimulationResult (equity_curve + trade_log + signal_log + 汇总指标) | 供 SIM-012 result_analyzer 消费 |

## 3. 核心规则 (设计真源 §1 D-SIMULATION-02 + 决策5)

### 3.1 沙箱执行模型 (PIT 无前瞻)

逐 bar 推进, 严格无前瞻:
1. 在 bar i: signal_fn 接收 `market_window = data.iloc[:i]` (bar i 之前的全部数据)
2. 信号决定目标持仓(目标权重), 转换为目标数量 = 目标权重 × 当前总权益 / 执行价
3. 在 bar i 的 **开盘价** 执行交易(含滑点+佣金)
4. 在 bar i 的 **收盘价** 标记权益(mark-to-market)
5. 循环 i=1..N-1 (至少 1 bar 历史)

### 3.2 信号模拟 (L2)

- `Signal(symbol, action, target_weight, confidence)` 不可变
- action: BUY/SELL/HOLD
- target_weight: 目标仓位占比 [0,1] (BUY 时生效; SELL→0; HOLD→不变)
- signal_fn 由调用方注入: `Callable[[SignalContext], list[Signal]]`
- SignalContext 含: bar_index, market_window, holdings, cash, total_equity, timestamp

### 3.3 组合模拟 (L3)

- 目标权重 → 目标数量: `target_qty = target_weight × total_equity / exec_price`
- 与当前持仓 diff → 生成 SimulatedTrade (BUY 加仓/SELL 减仓)
- 执行价: 开盘价 × (1+slippage) [BUY] / × (1-slippage) [SELL]
- 佣金: max(price×qty×commission_rate, min_commission)
- 默认禁止做空 (allow_short=False): SELL 量 ≤ 持仓量

### 3.4 权益跟踪

- 每 bar 记录 EquityPoint(timestamp, equity, cash, positions_value)
- equity = cash + Σ(holdings[sym] × close[sym])
- total_return = (final_equity - initial_capital) / initial_capital

## 4. 关键不变量 (INVARIANTS)

- PIT 无前瞻: signal_fn 只见 bar i 之前的数据 (market_window = data.iloc[:i])
- 纯函数: 不修改输入 market_data
- Config/Signal/SimulatedTrade/EquityPoint/SimulationResult 均 frozen 不可变
- 空/单 bar DataFrame → 返回仅含初始资金的 SimulationResult (不报错)
- 禁止做空时 SELL 超过持仓量 → 截断到持仓量 (不报错)
- 单标的(date index)与多标的(MultiIndex [symbol, date])均支持

## 5. 错误契约

- `StrategySimulationError` (ZA-SIM-0002): market_data 非 DataFrame / 缺必需列(open,close) / strategy_spec.signal_fn 不可调用

## 6. 测试

- `tests/simulation/test_strategy_simulator.py`
- 覆盖: 配置校验、单标的仿真、多标的仿真、PIT无前瞻(signal_fn只见历史)、做空截断、佣金/滑点计算、空/单bar输入、HOLD不交易、买入卖出权益正确、输入校验、signal_log/trade_log 完整性

## 7. 依赖

- 标准库 `dataclasses`/`typing`/`logging`
- `pandas` (数据窗口切片)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 可选消费: MOD-SIM-005 scenario_generator / SIM-01 市场仿真 (数据来源)
- 消费者: MOD-SIM-012 result_analyzer (仿真结果分析)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIM-002`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIM-002` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIM-002` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIM-002 | MOD-SIM-002 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 8.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §8（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


