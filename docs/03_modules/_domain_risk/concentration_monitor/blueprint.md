---
module_id: MOD-RK-07
title: "集中度风险监控器蓝图 — HHI+行业暴露+个股集中度"
doc_type: blueprint
status: Active
version: "0.1.0"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P0
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-RK-07 Concentration Risk Monitor — 集中度风险监控器 蓝图

> **module_id**: MOD-RK-07 | **域**: D_RISK | **层**: L1 Pre-Trade + L2 盘中监控
> **优先级**: P0 | **成熟度**: production | **对标能力**: C-004●
> **SSoT**: depgraph MOD-RK-07 | **设计真源**: D:\临时工作区\依赖图\11-D-RISK-风控域.md §1.2 RK-07, §7.5 行业集中度

## 1. 定位

集中度风险监控器——计算持仓集中度三大指标(HHI/个股/行业), 三级告警,
供 RK-02 Pre-Trade Hard Block + RK-03 实时监控。Pre-Trade 阶段拦截超限仓位, 盘中监控集中度漂移。

属 A 类基础设施(权重归一化+平方和+分组聚合, 数学逻辑明确), 阈值为 C 类可调参数。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 权重字典 {symbol: weight} + 可选行业映射 | — |
| 输出 | ConcentrationSnapshot(hhi/max_single/max_industry/level/breach_reasons) | 联动 RK-02, RK-03 |
| 事件 | ConcentrationAlertedEvent (级别变化时发射) | → D-FRONTEND, D-AUTONOMY |

## 3. 核心规则 (设计真源 §1.2 RK-07, §7.4/§7.5)

### 3.1 三大指标

| 指标 | 计算 | 阈值 |
|------|------|------|
| HHI | Σ w_i² ∈ [1/N, 1] | warning 0.10 / critical 0.18 |
| 个股集中度 | max(w_i) | limit 0.10(10%NAV), warning 8% |
| 行业暴露 | max(Σ w_i by industry) | limit 0.30, warning 24% |

### 3.2 三级告警

| 级别 | 触发条件 | 执行动作 |
|------|----------|---------|
| NONE | 所有指标在 warning 内 | 放行 |
| WARNING | 达 warning 阈值 | 告警, RK-02 可 Soft Block |
| CRITICAL | 超硬上限 | RK-02 Hard Block |

### 3.3 事件去抖

- 仅告警级别*变化*时发射 ConcentrationAlertedEvent (含升级/降级/恢复)

## 4. 关键不变量 (INVARIANTS)

- 权重自动归一化 (Σw=1); 拒绝负权重
- HHI ∈ [1/N, 1]; max_single_weight ≤ 1
- 告警级别取所有指标最严重级别
- 无行业映射时跳过行业检查 (避免误报)
- 事件去抖: 连续相同级别不重复发射

## 5. 错误契约

- `InvalidConcentrationInputError` (ZA-RK-0007): 权重为负/权重和为零/配置非法

## 6. 测试

- `tests/risk/test_concentration_monitor.py`
- 覆盖: HHI计算、个股/行业集中度、三级告警、事件去抖、权重归一化、行业映射、监听器隔离

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: RK-02 Pre-Trade Checker (Hard Block), RK-03 Portfolio Risk Monitor, RK-13 Crowding Monitor
