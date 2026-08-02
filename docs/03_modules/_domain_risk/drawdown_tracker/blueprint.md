---
module_id: MOD-RK-011
title: "回撤实时追踪器蓝图 — 峰值谷值+三级阈值告警"
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

# MOD-RK-011 Drawdown Real-Time Tracker — 回撤实时追踪器 蓝图

> **module_id**: MOD-RK-011 | **域**: D_RISK | **层**: L02 盘中实时监控
> **优先级**: P0 | **成熟度**: L1 🔵 骨架 → production | **对标能力**: C-032●
> **SSoT**: depgraph MOD-RK-011 | **设计真源**: D:\临时工作区\依赖图\11-D-RISK-风控域.md §1 RK-11, §4 E-RK-03

## 1. 定位

回撤实时追踪器——盘中实时跟踪组合净值的最大回撤(峰值/谷值), 三级阈值告警,
回撤恢复检测, 资金曲线诊断。产出 E-RK-03 DrawdownAlerted 事件, EMERGENCY 级触发
RK-17 Kill Switch。

与 POS-007 的区别: POS-007 是*仓位上限联动*(回撤→降仓, 行动导向);
RK-11 是*实时告警*(回撤→分级告警, 监控导向)。RK-11 产出告警事件给前端/自治/报告域。

属 A 类基础设施(峰值谷值计算+阈值判定+恢复检测, 逻辑明确), 阈值为 C 类可调参数。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 组合净值 (实时, 来自 D-EX-CORE / RK-03 监控) | — |
| 输出 | DrawdownSnapshot (峰值/谷值/回撤/级别/恢复状态) | 联动 RK-17 |
| 事件 | E-RK-03 DrawdownAlerted | → D-FRONTEND, D-AUTONOMY, D-REPORTING |

## 3. 核心规则 (设计真源 §1 RK-11, §4 E-RK-03)

### 3.1 三级阈值

| 回撤幅度 | 告警级别 | 说明 |
|----------|----------|------|
| 5% ~ 10% | WARNING | 提醒关注 |
| 10% ~ 15% | CRITICAL | 严重回撤 |
| > 15% | EMERGENCY | 触发 Kill Switch |

(< 5% 为 NONE, 无告警)

### 3.2 峰值谷值跟踪

- peak: 高水位 (单调非减, 仅在新高时上移)
- trough: 自最近峰值以来的最低点 (peak 上移时重置)
- drawdown = (net_value - peak) / peak (≤ 0)

### 3.3 回撤恢复检测

- in_recovery: 当净值从谷底回升但尚未创新高时标记
- 恢复完成: 净值回到/超过峰值 (创新高) → 告警级别降为 NONE, 发恢复事件

### 3.4 事件触发策略

- 仅在告警级别*变化*时发射 E-RK-03 (避免盘中高频刷屏)
- 恢复(降级)也算级别变化, 发射恢复事件

## 4. 关键不变量 (INVARIANTS)

- peak 单调非减; trough ≤ peak; drawdown ≤ 0
- 告警级别由当前回撤唯一决定 (无状态依赖, 除事件去抖)
- EMERGENCY 级必须触发 Kill Switch 评估 (由消费者 RK-17 执行)
- 事件去抖: 连续相同级别不重复发射

## 5. 错误契约

- `InvalidDrawdownInputError` (ZA-RK-0003): 净值非正

## 6. 测试

- `tests/risk/test_drawdown_tracker.py`
- 覆盖: 峰值谷值跟踪、三级阈值、恢复检测、事件去抖、EMERGENCY触发、边界值

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: RK-17 Kill Switch (EMERGENCY 触发), D-FRONTEND, D-AUTONOMY, D-REPORTING
- 数据源: D-EX-CORE 组合净值, RK-03 Portfolio Risk Monitor
