---
module_id: MOD-007
title: Task Pipeline Service Interface / 任务双管线服务接口规范
doc_type: architecture_view
status: Active
version: "1.0.0"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: human_plus_agent
created_date: "2026-05-06"
last_updated: "2026-05-06"
ttl: permanent
design_maturity: design
template_source: "vector_memory-service-interface.md（B 轨接口目录结构对齐）"
truth_source:
  - "03_modules/_cross_layer/pipeline/blueprint.md（MOD-INF-009 — 详细设计与 CT 锚点；Phase 5 真源）"
  - "architecture_model/layers/b_pipeline.yaml（Pipeline YAML SSoT）"
related_kb: []
integration_points:
  - "Agent Orchestrator（downstream，任务调度与状态机消费 Pipeline 路由决策）"
  - "LLM Security Gateway MOD-LLM_SECURITY（Pipeline L1/L3 输入输出检测）"
  - "Task System MOD-TASK_SYSTEM（M1–M11 节点与任务卡消费方）"
  - "Database MOD-DATABASE（deferred queue / task_repo 查询）"
tags:
  - pipeline
  - m1-m11
  - b-track
  - service-interface
depends_on:
  - target: AI-ENG-ORC-001
    at: "§编排边界"
    why: "Orchestrator 消费本接口的调度/decision surface"
mod_master_blueprint: "MOD-MASTER_BLUEPRINT"
mod_master_contracts:
  - "CT-PIPE-ORC-001"
---

# Task Pipeline Service Interface / 任务双管线服务接口规范

> **定位**：B 轨第 6 份核心服务接口——与 VMS/CTX/ORC/FLE/LSG 并列。权威设计细节在 **`MOD-INF-009`** 蓝图；本文件给出**稳定对外边界**（消费者、契约编号、真源指针），避免在长蓝图中检索接口轮廓。

---

## 1. 读者指南

| 章节 | 内容 |
|------|------|
| §1 | 服务职责与真源 |
| §2 | 对外抽象（命名 / 协议形态） |
| §3 | 与集成总蓝图契约对齐 |

---

## 2. 服务职责（一句话）

**Task Pipeline** 负责任务在 **A 区（M1–M5）** 与 **B 区（M6–M11）** 之间的**模型路由、门禁组合、sandbox 配置与降级策略**，使每个 `TaskCard` 在执行路径上绑定一致的策略剖面。

---

## 3. 对外抽象（实现无关）

### 3.1 Protocol 签名

```python
class PipelineServiceProtocol:
    async def route(self, task_id: str, task_type: str, priority: str,
                    model_affinity: dict | None = None) -> PipelineRouteDecision:
        """路由决策——根据task_type/priority/model_affinity选择A区/B区管线"""

    async def dispatch(self, task_id: str, route: PipelineRouteDecision) -> DispatchResult:
        """调度执行——按路由决策分配模块和模型"""

    async def execute(self, dispatch_id: str) -> PipelineResult:
        """执行管线——按M1-M11模块序列执行"""

    async def cancel(self, dispatch_id: str, reason: str) -> CancelResult:
        """取消执行——安全中断正在运行的管线"""

    async def get_status(self, dispatch_id: str) -> DispatchStatus:
        """查询状态——获取当前管线执行进度"""

    async def list_active(self, filters: dict | None = None) -> list[DispatchSummary]:
        """活跃调度列表——监控面板用"""
```

### 3.2 核心数据模型

| 模型 | 字段数 | 说明 |
|------|--------|------|
| `PipelineRouteDecision` | 8 | task_type, priority, zone(A/B), modules[], model, affinity_score, circuit_breaker_state, metadata |
| `DispatchResult` | 5 | dispatch_id, pipeline_id, assigned_model, status, created_at |
| `PipelineResult` | 6 | dispatch_id, modules_executed[], status, artifacts[], metrics, duration_ms |
| `CircuitBreakerState` | 4 | state(open/half_open/closed), failure_count, last_failure_at, cooldown_ms |
| `CancelResult` | 3 | dispatch_id, cancelled, reason |
| `DispatchStatus` | 5 | dispatch_id, current_module, progress_pct, elapsed_ms, estimated_remaining_ms |
| `DispatchSummary` | 4 | dispatch_id, task_id, status, started_at |

### 3.3 错误码

| 错误码 | 含义 | 降级策略 |
|--------|------|----------|
| `-32050` | PIPELINE_ROUTE_FAILED | 降级到默认A区管线 |
| `-32051` | PIPELINE_DISPATCH_TIMEOUT | 重试1次后标记FAILED |
| `-32052` | PIPELINE_MODULE_ERROR | 跳过当前模块继续执行 |
| `-32053` | PIPELINE_CIRCUIT_OPEN | 等待断路器半开状态 |
| `-32054` | PIPELINE_CANCELLED | 正常取消，无降级 |

### 3.4 性能 SLO

| 指标 | 目标 | 测量方式 |
|------|------|----------|
| route() 延迟 | p99 < 50ms | Telemetry metrics |
| dispatch() 延迟 | p99 < 200ms | Telemetry metrics |
| execute() 吞吐 | >= 10 concurrent | 压测 |
| 断路器恢复 | < 30s | 故障注入测试 |

- **输入**：已通过 `MOD-TASK_SYSTEM` / Gate 的 `TaskCard`（或等价 task 句柄）+ 组织策略（`GOV-AI-002` 路由树）。
- **输出**：**路由决策**（目标模型 profile、管线区段、门禁集合、预算钩子）供 Orchestrator / Runtime 执行。
- **失败语义**：对齐 **fail-closed / degraded mode** 由 `MOD-LLM_SECURITY`、`MOD-INF-001` 在链路下游执行；本层只产出**结构化决策或阻断原因码**。

具体 **Pydantic / Protocol** 签名以 **`MOD-INF-009` §接口契约** 为准；蓝图真源 `docs/03_modules/_cross_layer/pipeline/blueprint.md`；代码落位 `src/zephyr/pipeline/`。

---

## 4. 与 MOD-MASTER_BLUEPRINT 契约对齐

| 契约 / 引用 | 说明 |
|-------------|------|
| `CT-PIPE-ORC-001` | Pipeline ↔ Agent Orchestrator 集成边界 |
| `GOV-AI-002` | 模型路由策略真源 |

---

## 5. 变更同步

| 变更类型 | 必须先更新的真源 |
|----------|------------------|
| 路由阶段 / M1–M11 语义 | `MOD-INF-009`（`_cross_layer/pipeline/blueprint.md`）+ `b_pipeline.yaml` |
| 与 Orchestrator 边界 | 本文件 §2 + `_b_track_interfaces/agent_orchestrator_interface.md` |
