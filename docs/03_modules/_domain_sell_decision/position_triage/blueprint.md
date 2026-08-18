---
module_id: MOD-SELL-000
title: "持仓分级判定器蓝图 — ATR距离驱动WATCH/MONITOR/HOLD三级"
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

# MOD-SELL-000 | Position Triage 持仓分级判定器

> **域**: D_SELL_DECISION | **层**: L03 卖出决策 | **优先级**: P1 | **safety**: M | **ai_autonomy**: ai_modifiable
> **状态**: production | **版本**: 0.1.0 | **SSoT**: depgraph MOD-SELL-000 (node 7604385)

## 1. 模块定位

持仓 Triage 分级生产方——按持仓盈亏状态与止损距离输出 TriageLevel(WATCH/MONITOR/HOLD)，驱动卖出流扫描频率（Watch 分钟级降级/Monitor 5 分钟级/Hold 事件驱动）。是 42 号卖出流时序编排（§3.2）的入口环节：先分级，不是所有持仓都需同等监控。

依据: `42_sell_flow.md` §3.2 持仓 Triage 分级判定算法

## 2. 不变量 (INVARIANTS)

- **WATCH**: 距止损绝对距离 < 1.5×ATR − delta_abs（亏损接近止损或盈利回撤接近止损）
- **HOLD**: 深度盈利 > 3.0×ATR − delta_abs 且未命中 WATCH（即不接近止损）
- **MONITOR**: 中间状态（spec §3.2"正常持仓"档）
- **ATR 缺失降级**: atr None 或 ≤0 → 直接返回 MONITOR（最保守中间档，WATCH 过度监控/HOLD 漏监控）
- **threshold_delta 硬封顶**: |delta| ≤ 0.10（BM-POS-09 双向反馈契约 §3.3，delta 正值放宽/负值收紧）
- **绝对价格比较**: distance_abs/profit_abs 与 ATR 阈值同量纲比较，与 spec 伪代码数学等价（两边同乘 entry 消去除法，防浮点尾差）
- **无状态设计**: 不持久化，每次扫描重新判定

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| InvalidTriageInputError | ZA-SELL-0000 | symbol 空 / entry_price≤0 / current_price≤0 / stop_loss_price≤0 |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 依赖 | zephyr.shared.foundation.errors | ZephyrBaseError | 错误基类 |
| 依赖 | MOD-POS-003 position_drift_monitor | TriageLevel 枚举 | 消费方已定义枚举（注释"来自 SELL-00"），本模块 import 复用（真源唯一） |
| 产出 | D-POSITION position_drift_monitor | TriageLevel | 漂移监控按分级定告警（消费方已就位） |
| 产出 | MOD-SELL-007 融合引擎 / MOD-SELL-009 紧迫度 | TriageLevel | 分级驱动扫描频率与融合权重 |

## 5. 分级逻辑

```
profit_abs    = current_price - entry_price          # 有利移动(可负)
distance_abs  = |current_price - stop_loss_price|    # 距止损绝对距离
delta_abs     = threshold_delta × entry_price        # 双向反馈(±0.10 封顶)

distance_abs < 1.5×ATR − delta_abs  →  WATCH   (分钟级扫描, MVP 降级自秒级)
profit_abs   > 3.0×ATR − delta_abs  →  HOLD    (事件驱动)
其余                                →  MONITOR (5 分钟级扫描)
ATR 缺失                            →  MONITOR (降级)
```

## 6. 接口

### 输入
```python
PositionTriage.triage(
    position: SellPositionSnapshot,      # symbol/entry_price/current_price/strategy_type
    atr_value: float | None,         # ATR(14), None 触发降级
    stop_loss_price: float,          # 当前止损锚定价(来自 MOD-SELL-005)
    *, threshold_delta: float = 0.0, # BM-POS-09 双向反馈调整量
) -> TriageLevel
```

### 输出
`TriageLevel` 枚举（WATCH/MONITOR/HOLD，str 值与 D-POSITION 消费方完全对齐）。

## 7. 设计决策

| 决策 | 理由 |
|------|------|
| import 消费方 TriageLevel 而非自定枚举 | 真源唯一：position_drift_monitor 先定义（注释"来自 SELL-00"），本模块作为生产方复用其枚举，避免双向同步与值漂移 |
| ATR 缺失降级 MONITOR 而非固定%阈值 | spec §3.2 未给降级参数，发明固定%阈值无依据；MONITOR 是 spec"正常持仓"中间档，最保守 |
| 绝对价格距离比较 | 与 spec 伪代码数学等价（同乘 entry 消去除法），消除浮点计算顺序尾差 |
| 显式标量参数而非 position 对象 | 与本域已有模块（StopHuntingProtector 等）范式一致，可测试性与解耦更优 |
| 无状态静态方法 | 与猎杀防护器同款设计：状态持久化由上层持仓状态机负责 |

## 8. 测试计划

- WATCH 触发（距止损 <1.5×ATR）
- HOLD 触发（深度盈利 >3×ATR 且远离止损）
- MONITOR 中间态
- WATCH 边界（恰好=1.5×ATR 不触发，严格小于）
- ATR None / ATR=0 降级 MONITOR
- threshold_delta 放宽（+delta 更难 WATCH）
- threshold_delta 收紧（-delta 更易 WATCH）
- threshold_delta 硬封顶 ±0.10
- 输入校验（symbol 空/价格≤0 四类）

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SELL-000`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SELL-000` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SELL-000` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SELL-000 | MOD-SELL-000 | ✅ |
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
