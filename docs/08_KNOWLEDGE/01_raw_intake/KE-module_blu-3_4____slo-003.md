---
module_id: KE-module_blu-3_4____slo-003
title: 3.4 性能 SLO
category: module_blueprint
---

# 3.4 性能 SLO

3.4 性能 SLO

| 指标 | 目标 | 测量方式 |
|------|------|----------|
| route() 延迟 | p99 < 50ms | Telemetry metrics |
| dispatch() 延迟 | p99 < 200ms | Telemetry metrics |
| execute() 吞吐 | >= 10 concurrent | 压测 |
| 断路器恢复 | < 30s | 故障注入测试 |

- **输入**：已通过 `MOD-INF-006` / Gate 的 `TaskCard`（或等价 task 句柄）+ 组织策略（`GOV-AI-002` 路由树）。
- **输出**：**路由决策**（目标模型 profile、管线区段、门禁集合、预算钩子）供 Orchestrator / Runtime 执行。
- **失败语义**：对齐 **fail-closed / degraded mode** 由 `MOD-INF-014`、`MOD-INF-001` 在链路下游执行；本层只产出**结构化决策或阻断原因码**。

具体 **Pydantic / Protocol** 签名以 **`MOD-INF-009` §接口契约** 为准；蓝图真源 `docs/03_modules/_cross_layer/pipeline/blueprint.md`；代码落位 `src/zephyr/pipeline/`。

---
