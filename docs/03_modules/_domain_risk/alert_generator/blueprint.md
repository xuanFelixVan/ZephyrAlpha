---
module_id: MOD-RK-06
title: "告警生成器蓝图 — 三级告警分类+多通道路由+去重"
doc_type: blueprint
status: Draft
version: "0.1.3"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-05"
last_updated: "2026-08-05"
priority: P0
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: production
---

# MOD-RK-06 Alert Generator — 告警生成器 蓝图

> **module_id**: MOD-RK-06 | **域**: D_RISK | **层**: L2 盘中/盘后监控
> **优先级**: P0 | **成熟度**: design | **对标能力**: BM-RC-04-D
> **SSoT**: depgraph MOD-RK-06 | **设计真源**: 基础设施管线与引擎施工计划 §6.4 G1（临时工作文档，已退役未归档）

## 1. 定位

告警生成器——消费风控编排器产出的 `RiskReport`，将原始违规项按严重程度分为三级
（黄/橙/红），按级别路由到不同通道（日志/邮件/微信），并对同源告警在时间窗口内去重。

属 A 类基础设施（分级规则基于 RiskReport 字段判定，路由规则基于级别映射，
均为纯机制无业务参数）。阈值（去重窗口 5 分钟）为 C 类可调参数，默认值真源=alert_threshold_registry.yaml（THD-ALERT-001=300 秒，fail-closed 统读，2026-08-17 AI-THD-001）；显式传参可覆盖。

**与现有资产的关系**：
- 各监控器（concentration_monitor / tail_risk_monitor / systemic_risk_detector 等）
  已产出原始告警（`RiskReport.active_alerts` 为 string 列表）
- `DefaultRiskManagerOrchestrator.aggregate_report()` 已汇总 `RiskReport`
- 本模块是这些原始告警的**统一出口**——补建分类+路由+去重，不重复造监控逻辑

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | `RiskReport`（含 failed_checks / active_alerts / kill_switch_active / overall_pass） | ← `DefaultRiskManagerOrchestrator.aggregate_report()` |
| 输出 | `list[Alert]`（三级分级告警） | → 日志/邮件/微信通道 |
| 事件 | `AlertDispatchedEvent`（告警派发时发射） | → D_FRONTEND, D_AUTONOMY（未来） |

## 3. 核心规则

### 3.1 三级分类（纯机制，零业务参数）

| 级别 | 判定条件 | 来源字段 |
|------|----------|----------|
| **RED**（红） | `kill_switch_active=True` 或 `overall_pass=False` 且有 HALT 级 failed_check | `RiskReport.kill_switch_active`, `RiskReport.failed_checks` |
| **ORANGE**（橙） | `failed_checks` 非空但无 HALT 级违规，`overall_pass=True` | `RiskReport.failed_checks` |
| **YELLOW**（黄） | `active_alerts` 非空但 `failed_checks` 为空，`overall_pass=True` | `RiskReport.active_alerts` |

> 分级规则基于 RiskReport 字段值判定，无外部参数，满足零参数纯机制要求。

### 3.2 多通道路由

| 级别 | 日志 | 邮件 | 微信 |
|------|:----:|:----:|:----:|
| RED | ✓ | ✓ | ✓ |
| ORANGE | ✓ | ✓ | — |
| YELLOW | ✓ | — | — |

> 通道路由为硬编码映射（级别→通道集合），无外部参数。

### 3.3 去重

- 同一 `source`（来源监控器）+ 同一 `message` 在 5 分钟窗口内只派发一次
- 去重窗口过后自动过期，允许重新派发
- 去重窗口（5 分钟）为 C 类可调参数，默认值真源=alert_threshold_registry.yaml（THD-ALERT-001，fail-closed 统读）

## 4. 接口契约

```python
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

class AlertLevel(Enum):
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"

@dataclass(frozen=True)
class Alert:
    level: AlertLevel
    source: str           # 来源监控器 (concentration/tail_risk/systemic...)
    message: str
    timestamp: datetime
    idempotency_key: str

class AlertGenerator:
    def classify(self, report: RiskReport) -> list[Alert]:
        """将 RiskReport 分类为三级告警列表"""

    def route(self, alert: Alert) -> None:
        """按级别路由到对应通道（日志/邮件/微信）"""

    def deduplicate(self, alerts: list[Alert], window: timedelta) -> list[Alert]:
        """时间窗口内同源告警去重"""
```

## 5. 依赖关系

| 方向 | 模块 | 类型 | 说明 |
|------|------|------|------|
| 消费 | `risk_manager_base.py` (MOD-L04-001) | import_depends | 导入 RiskReport/RiskCheckResult 类型 |
| 被消费 | `default_risk_manager_orchestrator.py` (MOD-L04-001) | import_depends | 编排器调用 AlertGenerator.classify()（G1-S6 接入） |

## 6. 验收标准

- 告警延迟 < 1s（从 RiskReport 到通道派发）
- 级别判定正确率 100%（与 §3.1 规则一致）
- 通道可达（日志必达，邮件/微信 best-effort 不阻断）
- 5 分钟窗口内同源告警去重正确
- 无外部参数依赖（纯机制）

## 7. 施工步骤

1. G1-S1 ✓ depgraph 设计态登记（module_id=MOD-RK-06, 2条边）
2. G1-S2 ← 当前：创建 blueprint.md + 五图对齐验证
3. G1-S3 写代码 `src/zephyr/risk/core/alert_generator.py`
4. G1-S4 测试 `tests/risk/core/test_alert_generator.py`
5. G1-S5 depgraph status: planned→production
6. G1-S6 接入 `DefaultRiskManagerOrchestrator`

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-06`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-06` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-06` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-06 | MOD-RK-06 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/core/test_alert_generator.py` | ✅ 已实现 | |

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


