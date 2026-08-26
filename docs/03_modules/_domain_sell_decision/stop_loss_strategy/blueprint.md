---
module_id: MOD-SELL-005
title: "止损策略族蓝图 — Chandelier Exit 统一止损 + ATR自适应时间止损"
doc_type: blueprint
status: Active
version: "0.1.2"
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

# MOD-SELL-005 | Stop Loss Strategy 止损策略族

> **域**: D_SELL_DECISION | **层**: L03 卖出决策 | **优先级**: P1 | **safety**: M | **ai_autonomy**: ai_modifiable
> **状态**: production | **版本**: 0.1.0 | **SSoT**: depgraph MOD-SELL-005 (node 7604390)

## 1. 模块定位

止损策略族（BM-SELL-04-B）——Chandelier Exit 统一 ATR 波动率止损与移动止损（一套公式两个参数，替代两套独立%参数），配套 ATR 自适应时间止损（收集器第⑦类 TIME_STOP 信号算法源）。是 42 号卖出流 MVP 三核心之一（§5.3）。

依据: `42_sell_flow.md` §3.3 Chandelier Exit 施工公式 + §3.2 时间止损施工算法

## 2. 不变量 (INVARIANTS)

- **Chandelier Exit**: 止损线 = Highest_Close(N) − M × ATR(14)
- **亏损区(loss)**: N=10, M=3.0（宽 trailing 防噪声扫出）
- **盈利区(profit)**: N=22, M=2.0（紧 trailing 锁定利润）
- **策略类型 M 调整**（MVP 简化版，替代 MOD-SELL-014 完整范式）: TREND→M+0.5 / MEAN_REVERSION→M−0.5 / 其他不调整
- **ATR 缺失降级**: 固定%止损（SHORT_TERM 4% / 其他 8%，eastmoney 2026-07）
- **时间止损**: 持仓 ≥5 交易日且有利移动 < 1×ATR → FORCE_EXIT_EVALUATION
- **phase 显式传入**: 与 MOD-SELL-004 自动判定 phase 分工（调用方已持有 phase 上下文场景）

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| SellStopLossInputError | ZA-SELL-0005 | symbol 空 / 价格≤0 / highest_close_fn 不可调用 / phase 非枚举 / holding_days<0 |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 依赖 | MOD-SELL-000 position_triage | SellPositionSnapshot / StrategyType | 持仓快照与策略类型枚举真源 |
| 依赖 | zephyr.shared.foundation.errors | ZephyrBaseError | 错误基类 |
| 产出 | MOD-SELL-015 猎杀防护器 | 原始止损位 | 止损位偏移 1-2% 防猎杀（消费 AdjustedStopLevel 上游） |
| 产出 | MOD-SELL-004 止盈策略 | Chandelier 核心 | 004 委托本模块计算（真源唯一） |
| 产出 | MOD-SELL-001 收集器第⑦类 | TimeStopSignal | check_time_stop 产出 FORCE_EXIT_EVALUATION |
| 产出 | MOD-SELL-007 融合引擎 / D-POSITION | 止损价位 | 融合仲裁与持仓止损锚定 |

## 5. 核心逻辑

### ① Chandelier Exit 止损
```
止损线 = Highest_Close(N) − M × ATR(14)
亏损区: N=10, M=3.0 (+策略调整)     # 入场后未盈利, 宽
盈利区: N=22, M=2.0 (+策略调整)     # 盈利超1×ATR后, 紧
ATR缺失: entry × (1 − 4%|8%)        # 短线/其他降级
```

### ② ATR 自适应时间止损（第⑦类信号源）
```
favorable_move = current_price − entry_price
threshold      = 1.0 × ATR          # ATR缺失降级 1% 固定阈值
favorable_move < threshold 且 holding_days ≥ 5 → FORCE_EXIT_EVALUATION
```
> 用 1×ATR 而非固定 N 天：ATR 自带波动率调整（高波动股阈值抬高给更多时间，低波动股更快触发）。journalplus 2026 实证：5 日未移动 1×ATR 的持仓后续盈利概率 <35%。

## 6. 接口

### 输入
```python
StopLossStrategy.compute_stop_loss(
    position: SellPositionSnapshot,           # symbol/entry/current/strategy_type
    atr_value: float | None,              # ATR(14), None 触发降级
    highest_close_fn: Callable[[int], float],  # 回看N日最高收盘价(调用方注入K线)
    phase: PositionPhase,                 # LOSS/PROFIT 显式传入
) -> float                                # 止损价位

StopLossStrategy.check_time_stop(
    position: SellPositionSnapshot,
    atr_value: float | None,
    holding_days: int,                    # 已持仓交易日数
) -> TimeStopSignal | None                # FORCE_EXIT_EVALUATION 或 None
```

### 输出
- `stop_price: float`——Chandelier 止损锚定价
- `TimeStopSignal.FORCE_EXIT_EVALUATION`——喂给收集器第⑦类 TIME_STOP 信号

## 7. 设计决策

| 决策 | 理由 |
|------|------|
| Chandelier 统一 ATR 止损+移动止损 | 42号 §3.3：volatilitybox 2026-03 回测 595+ 标的 ATR 倍数止损比固定%减少 34% 过早止损；一套公式两个参数极简统一 |
| highest_close_fn 注入而非内置K线读取 | A类基础设施职责边界：不依赖数据层，调用方注入 K 线 close rolling max，可测试性最优 |
| phase 显式传入（与004自动判定分工） | 42号 §3.3 v1.5.2：扳机清单按 phase 分支等调用方已持有 phase 上下文的场景用本函数 |
| 策略类型 M±0.5 最小集 | 42号 §2.3/§4.1：MVP 用 Chandelier 阶段切换+策略调整替代 MOD-SELL-014 完整范式（待 G04 校准） |
| 与 risk 域 default_stop_loss_engine 并存 | 分层防御：本模块管策略级退出价位，risk 域管账户级硬止损（42号 §7 待定问题，倾向并存） |
| 时间止损降级 1% 固定阈值 | ATR 缺失时仍需可判定；1% 为保守有利移动门槛（低于此说明标的停滞） |

## 8. 测试计划

- 亏损区/盈利区 Chandelier 参数（N=10/M=3.0 与 N=22/M=2.0）
- 策略类型 M 调整（TREND +0.5 / MEAN_REVERSION −0.5 / SHORT_TERM 不调整）
- ATR None / ATR=0 降级固定%（短线 4% / 非短线 8%）
- 输入校验（symbol 空 / fn 不可调用 / phase 非枚举）
- 时间止损触发（5 天未移动 1×ATR）
- 时间止损不触发（已移动 / 不足 5 天）
- 时间止损 ATR 缺失降级 1% 阈值
- holding_days 负值校验

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SELL-005`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SELL-005` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SELL-005` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SELL-005 | MOD-SELL-005 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 9. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 9.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/sell_decision/core/stop_loss_strategy.py` | ✅ 已实现 | |

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


