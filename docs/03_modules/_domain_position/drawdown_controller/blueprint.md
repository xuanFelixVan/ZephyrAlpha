---
module_id: MOD-POS-008
title: "回撤控制器蓝图 — 系统性风险5级+策略止损+黑天鹅处置"
doc_type: blueprint
status: Active
version: "0.1.1"
design_maturity: production
ttl: permanent
layer: L03_position
layer_name: position
functional_domain: position
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P1
blueprint_level: module
responsibility_domain: 
---

# MOD-POS-008 Drawdown Controller — 回撤控制器 蓝图

> **module_id**: MOD-POS-008 | **域**: D_POSITION | **层**: L03 仓位管理
> **优先级**: P1 | **成熟度**: production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-POS-008 | **设计真源**: D:\临时工作区\依赖图\07-D-POSITION-仓位管理域.md §1.3 POS-08, §14.3 黑天鹅模式

## 1. 定位

回撤控制器——消费组合回撤+系统性风险分级(VaR/CVaR)+黑天鹅模式信号，产出分级响应指令
(减仓/清仓/暂停新开/Kill Switch)，是仓位防守的"自动减仓大脑"。

属 A 类基础设施(阈值判定+分级响应, 逻辑明确), 5 级阈值与黑天鹅处置为 C 类可调参数。

**边界**: 不覆盖风控熔断(KS-L4 Kill Switch 由 D-RISK stop_loss 触发), 本模块只产分级响应指令,
不直接执行交易(执行由 D-EX-CORE 承接)。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 | 来源 |
|------|------|-----------|------|
| 输入 | 组合回撤(当前回撤率+峰值净值) | DrawdownInfo | POS-07 Capital Curve Manager |
| 输入 | VaR/CVaR 系统性风险指标 | VarCvarMetrics (CTR-003) | D-RISK risk_limits |
| 输入 | 黑天鹅模式信号(7类) | BlackSwanSignal | D-RISK / D-SIGNAL |
| 输入 | 策略级回撤(单策略 PnL) | StrategyPnl | D-PF-CORE |
| 输出 | 分级响应指令 | DrawdownResponse | → POS-01 仓位上限调整 / D-EX-CORE 执行 |

## 3. 核心规则 (设计真源 §1.3 POS-08)

### 3.1 系统性风险 5 级响应 (基于 VaR/CVaR)

| 级别 | 触发条件 | 响应动作 |
|------|---------|---------|
| 🟢 绿(正常) | VaR < 2% | 正常运行, 无限制 |
| 🟡 黄(警戒) | VaR 2%-4% | 新开仓减半(仓位系数×0.5) |
| 🟠 橙(减仓) | VaR 4%-6% | 禁止新开仓 + 减仓(仓位上限 0.5——2026-08-16 双轮审查 P1-4 裁定：原 cap 0.7 非单调倒挂已修正, 级别严格度由动作语义区分) |
| 🔴 红(大幅减仓) | VaR > 6% | 减仓 50% + 只平不开 |
| ⚫ 黑(清仓) | CVaR > 10% | 全部清仓 |

### 3.2 策略级止损

| 止损类型 | 触发条件 | 动作 |
|---------|---------|------|
| Soft Stop | 单策略回撤 > 5% | 砍仓(关闭该策略持仓) |
| Hard Stop | 单策略回撤 > 10% | 关闭策略(禁止再开仓) |

### 3.3 黑天鹅 7 模式自动处置 (设计真源 §14.3)

| 模式 | 特征信号 | 仓位处置 |
|------|---------|---------|
| BS-001 流动性蒸发 | 成交量骤降至 30% + 买卖价差扩大 3 倍 | 参与率约束收紧至 5% + 暂停做 T |
| BS-002 相关性崩塌 | 跨板块相关性 < 0.1 + 分散化失效 | 集中度强制分散 + 降总仓位 |
| BS-003 波动率爆发 | VIX 类指标 > 2σ + 已实现波动率翻倍 | 仓位减半 + 暂停新开仓 |
| BS-004 融资盘踩踏 | 两融余额单日降 > 10% + 融资保证金上调 | 降杠杆敞口 + 暂停融资标的 |
| BS-005 跨市场传导 | 外围市场暴跌 + 北向资金大幅流出 | 降仓位至市场状态对应档位 |
| BS-006 政策黑天鹅 | 交易规则突变 / 印花税调整 / 行业禁令 | 暂停受影响标的交易 + 评估 |
| BS-007 系统性风险 | 多个 BS 模式同时触发 | Kill Switch(P0) — 委托 D-RISK stop_loss |

### 3.4 回撤回补恢复

- 回撤回补 50% → 逐步恢复仓位上限(每步恢复 25%, 间隔 N 分钟)
- 恢复期间仍受系统性风险级别约束(取 min(回补恢复档, 风险级别档))
- 未回补到峰值前, 禁止扩张超过回撤前仓位

### 3.5 不覆盖风控熔断

- Kill Switch (KS-L4) 由 D-RISK stop_loss 触发, 本模块不触发 Kill Switch
- BS-007 系统性风险 → 本模块产出 Kill Switch **建议**, 委托 stop_loss 执行
- 本模块的响应指令优先级 < 风控熔断(风控熔断覆盖本模块指令)

## 4. 关键不变量 (INVARIANTS)

- 响应级别单调不减: 风险升级时立即生效, 降级时走回补恢复(不跳级)
- DrawdownResponse.position_cap ≤ 1.0 (仓位上限不超过 100%)
- 黑天鹅模式优先级 > 系统性风险级别 > 策略级止损(取最严)
- Soft Stop / Hard Stop 针对单策略, 不影响其他策略
- BS-007 触发时, 其他响应指令让位 Kill Switch 建议

## 5. 错误契约

- `InvalidDrawdownControlError` (ZA-POS-0008): 回撤率越界(<-1 或 >0)、VaR 为负、策略 PnL 缺失

## 6. 测试

- `tests/position/test_drawdown_controller.py`
- 覆盖: 5 级响应判定、Soft/Hard Stop、7 黑天鹅模式、回撤回补恢复、优先级取严、输入校验、
  风控熔断不覆盖语义

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- `zephyr.position.core.capital_curve_manager` (POS-07, DrawdownInfo)
- `zephyr.risk.risk_limits` (D-RISK, VarCvarMetrics)
- 消费者: MOD-POS-001 (仓位上限调整), D-EX-CORE (执行减仓指令)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-POS-008`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-POS-008` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-POS-008` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-POS-008 | MOD-POS-008 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
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
