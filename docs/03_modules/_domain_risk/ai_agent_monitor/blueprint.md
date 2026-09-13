---
module_id: MOD-RK-14
title: "AI/Agent 风险监控器蓝图 — 交易 Agent 行为越界检测"
doc_type: blueprint
status: Active
version: "0.1.2"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-05"
last_updated: "2026-08-17"
blueprint_level: module
blueprint_id: MOD-RK-14
domain_id: D_RISK
path: src/zephyr/risk/core/ai_agent_monitor.py
design_maturity: production
build_status: production
granularity: file
ai_autonomy: ai_modifiable
safety: L
stability: evolving
responsibility_domain: 
---

# MOD-RK-14 AI/Agent 风险监控器 (AiAgentMonitor)

## 1. 定位

D_RISK 域 A 类基础设施——交易 Agent 行为越界检测（ASI/AST/MCP 隐性串谋）。

组装缺口：检测能力散落于 D_FBL_DETECTORS/D_SECURITY/D_AUTONOMY_CORE，本模块将其组装+聚焦为 risk/core/ 内面向交易 Agent 的越界监控。

## 2. 输入/输出

| 方向 | 契约 | 类型 |
|------|------|------|
| 输入 | agent_metrics: {metric_name: float} | dict |
| 输入 | behavior_events: list[AuditEvent] (可选) | list |
| 输出 | AiAgentRiskMetrics | dataclass |
| 输出 | RiskCheckResult (via to_risk_check_result) | dataclass |

## 3. 核心规则

- emergence_state: 来自 EmergentBehaviorDetector (STABLE/CORRELATING/CRITICAL/HYSTERETIC)
- trajectory_anomalies: 来自 AgentTrajectoryAnomalyDetector
- fingerprint_deviation: 来自 A2ABehaviorFingerprint [0, 1]
- risk_score = 0.4×emergence + 0.3×trajectory + 0.3×fingerprint
- is_breached = risk_score > 0.6 或 emergence_state == CRITICAL

## 4. 依赖

- MOD-INF-019 (autonomy_core/agent_observability)
- MOD-LLM-SECURITY (security/llm_defense/llm_security/behavior_audit_logger)
- MOD-FEEDBACK_LOOP (feedback_loop/detectors)

## 5. 验收

- 能检出模拟越界场景（CRITICAL emergence + 高 fingerprint deviation）
- risk_score ∈ [0, 1] 守恒
- RiskCheckResult severity 映射正确

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-14`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-14` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-14` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-14 | MOD-RK-14 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 6. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/core/test_ai_agent_monitor.py` | ✅ 已实现 | |

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


