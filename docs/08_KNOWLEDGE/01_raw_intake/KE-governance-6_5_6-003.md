---
module_id: KE-governance-6_5_6-003
title: 6.5 6 大核心服务的治理归属
category: governance
---

# 6.5 6 大核心服务的治理归属

6.5 6 大核心服务的治理归属

> 新增于 v2.1.0（2026-04-24）。6 大核心服务（LSG/CE/VMS/Orc/FLE/KB）在三层治理边界中的归属：

| 服务 | Policy 层治理 | Factory 层治理 | Runtime 层治理 |
|------|--------------|--------------|---------------|
| **LSG** | `ai_security_gateway_policy.md` + 四层防御规则集 | `scripts/governance/aisg/` 策略编译器 | Session Log `security_events` 表 + 红队评估季度报告 |
| **CE** | Context 策略白名单 + 压缩质量 SLO | `ContextEngineProtocol` 抽象基类 | FLE `llm_calls` 表 + 压缩质量周报 |
| **VMS** | Collection 元数据契约 + 级联语义表 | `VectorMemoryProtocol` 抽象基类 | Session Log `vms_operations` 表 + 去重检测月报 |
| **Orc** | 任务状态机 + Agent 白名单 | `OrchestratorProtocol` + Sandbox ACL 模板 | `agent_actions` + `sandbox_violations` 表 + 幻觉检测月报 |
| **FLE** | 异常阈值策略 + 动作分派规则 | `FeedbackLoopProtocol` + EMA 参数 | FLE 自监控 anomaly_ledger + 阈值触发审计 |

**治理一致性约束**：6 大核心服务的 Policy 文档必须在 experimental 末全部就位，否则 T7 门禁不通过。
