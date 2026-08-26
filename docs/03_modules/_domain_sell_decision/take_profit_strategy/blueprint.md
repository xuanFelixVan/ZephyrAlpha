---
module_id: MOD-SELL-004
title: "止盈策略族蓝图 — Chandelier Exit 移动止盈(自动phase判定)"
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

# MOD-SELL-004 | Take Profit Strategy 止盈策略族

> **域**: D_SELL_DECISION | **层**: L03 卖出决策 | **优先级**: P1 | **safety**: M | **ai_autonomy**: ai_modifiable
> **状态**: production | **版本**: 0.1.0 | **SSoT**: depgraph MOD-SELL-004 (node 7604389)

## 1. 模块定位

止盈策略族（BM-SELL-04-A）——移动止盈与移动止损统一为 Chandelier Exit：盈利后的 trailing 既是止盈（锁定利润）也是止损（保护盈利），不维护两套独立%参数，不封顶上涨空间。是 42 号卖出流 MVP 三核心之一（§5.3）。

依据: `42_sell_flow.md` §3.4 compute_exit_price 施工伪代码

## 2. 不变量 (INVARIANTS)

- **phase 自动判定**: 盈利超 1×ATR（unrealized_pnl_pct ≥ atr_pct）→ PROFIT（紧 trailing）；否则 LOSS（宽 trailing）
- **统一公式**: 委托 MOD-SELL-005 Chandelier 核心计算，本模块不重复实现公式（真源唯一）
- **ATR 缺失降级**: 委托 005 统一降级逻辑（固定%，SHORT_TERM 4% / 其他 8%）
- **盈利区参数**: N=22, M=2.0（紧 trailing 锁定利润）
- **亏损区参数**: N=10, M=3.0（宽 trailing 防噪声扫出）

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| InvalidTakeProfitInputError | ZA-SELL-0004 | symbol 空 / 价格≤0 / highest_close_fn 不可调用 |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 依赖 | MOD-SELL-005 stop_loss_strategy | Chandelier 核心 / PositionPhase / validate_position_snapshot | 统一公式真源（委托计算） |
| 依赖 | MOD-SELL-000 position_triage | SellPositionSnapshot | 持仓快照真源 |
| 依赖 | zephyr.shared.foundation.errors | ZephyrBaseError | 错误基类 |
| 产出 | MOD-SELL-007 融合引擎 / D-POSITION | 退出价位 | 融合仲裁与持仓退出锚定 |
| 产出 | MOD-SELL-015 猎杀防护器 | 退出价位 | 偏移防猎杀上游 |

## 5. 核心逻辑

```
unrealized_pnl_pct = (current − entry) / entry
atr_pct            = ATR / entry
phase = PROFIT if unrealized_pnl_pct ≥ atr_pct else LOSS   # 盈利超1×ATR切换
exit_price = Chandelier(phase)  # 委托 MOD-SELL-005
```

> **切换点用 ATR 而非固定+5%**（42号 §3.4）：高波动股 ATR 大→切换阈值自动抬高（防过早锁利）；低波动股 ATR 小→阈值自动降低（快速进入保护模式）。

## 6. 接口

### 输入
```python
TakeProfitStrategy.compute_exit_price(
    position: SellPositionSnapshot,           # symbol/entry/current/strategy_type
    atr_value: float | None,              # ATR(14), None 触发降级
    highest_close_fn: Callable[[int], float],  # 回看N日最高收盘价(调用方注入)
) -> float                                # 退出价位
```

### 输出
`exit_price: float`——止盈/止损统一退出锚定价。

## 7. 设计决策

| 决策 | 理由 |
|------|------|
| 委托 005 计算而非自带公式 | 真源唯一：42号 §3.4"用 Chandelier Exit 统一，不维护两套独立%参数"；本模块只承担 phase 自动判定职责 |
| 移动止盈为主而非固定目标价 | 42号 §4.3：固定止盈封顶上涨空间，趋势策略错失大行情；trailing 不封顶、自动锁定利润 |
| 固定/分批/时间加权止盈不施工 | 42号 §3.4 待裁定表：待 G04 策略类型校准后差异化 |
| 分批退出不在本模块 | 42号 §3.7：simple_scaling_out 三步法归 MOD-SELL-017，MVP 降级一次性退出 |

## 8. 测试计划

- 亏损区（盈利 <1×ATR → loss 宽 trailing）
- 盈利区（盈利 >1×ATR → profit 紧 trailing）
- 边界（盈利恰好 =1×ATR → profit，≥ 判定）
- 策略类型 M 调整经 005 传导（TREND 更宽）
- ATR None / ATR=0 降级固定%（短线 4% / 非短线 8%）
- 输入校验（symbol 空 / entry≤0 / fn 不可调用）

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SELL-004`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SELL-004` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SELL-004` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SELL-004 | MOD-SELL-004 | ✅ |
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
| `src/zephyr/sell_decision/core/take_profit_strategy.py` | ✅ 已实现 | |

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


