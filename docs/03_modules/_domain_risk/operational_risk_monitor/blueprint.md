---
module_id: MOD-RK-19
doc_type: blueprint
status: Active
ttl: permanent
blueprint_id: MOD-RK-19
domain_id: D_RISK
path: src/zephyr/risk/core/operational_risk_monitor.py
design_maturity: production
build_status: stable
granularity: file
ai_autonomy: ai_modifiable
safety: L
stability: evolving
responsibility_domain: 
---

# MOD-RK-19 操作风险监控器 (OperationalRiskMonitor)

## 1. 定位

D_RISK 域 A 类基础设施——操作风险阈值解释层。

组装缺口：MOD-EX-003 (auditor.py) 已提供 `OperationalRiskStats`（failure_rate /
fill_rate / latency p50/p95/max/mean），但**无阈值告警**。本模块不重算任何统计，
仅做阈值解释 + RiskCheckResult 转换，将纯统计转换为风险评估结果。

## 2. 输入/输出

| 方向 | 契约 | 类型 |
|------|------|------|
| 输入 | OperationalRiskStats (来自 MOD-EX-003) | dataclass |
| 输出 | OperationalRiskAssessment | dataclass |
| 输出 | RiskCheckResult (via to_risk_check_result) | dataclass |

## 3. 核心规则

阈值默认值真源=alert_threshold_registry.yaml（THD-OPRISK-001/002/003，fail-closed 统读，2026-08-17 AI-THD-001）；构造传参可覆盖。

- failure_rate_breached: failure_rate > 0.05 (默认阈值，行业标准)
- latency_breached: latency_p95_ms > 500.0 (默认阈值，行业标准)
- 严重度倍数: 实际值 >= 2×阈值 → severe
- overall_severity:
  - HALT: 任一维度 severe OR 双维度都突破（非 severe）
  - warning: 单维度突破（非 severe）
  - info: 均未突破

## 4. 依赖

- MOD-EX-003 (ex_core/audit_journal/auditor) — OperationalRiskStats 真源
- MOD-L04-001 (risk_manager_base) — RiskCheckResult

## 5. 验收

- 失败率 > 5% 触发告警
- 延迟 p95 > 500ms 触发告警
- severe (>=2×阈值) → HALT
- 双维度突破 → HALT
- 零提交数据 → info + insufficient data finding
- RiskCheckResult severity 映射正确

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-19`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-19` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-19` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-19 | MOD-RK-19 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 6. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/core/test_operational_risk_monitor.py` | ✅ 已实现 | |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
