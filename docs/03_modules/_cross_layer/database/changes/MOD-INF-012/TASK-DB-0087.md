---
task_id: "DB-025-0087"
namespace: "OPS"
seq: 87
title: "分层消费者注册表——治理信息：Tier1/Tier2/Tier3 消费者分级验证"
tags: ["fn:governance", "ly:cross_layer"]
depends_on: ["DB-025-0064"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"]
acceptance_criteria:
  - "Tier1(核心消费者) = task-system(MOD-INF-006)+feedback-loop(MOD-INF-010)+audit-trail(MOD-INF-020)——3项"
  - "Tier2(集成系统) = pipeline(MOD-INF-009)+mcp-servers(MOD-INF-013)+gate-engine(MOD-INF-007)+system-telemetry(MOD-INF-015)——4项"
  - "Tier3(监控/工具) = capacity-assurance(MOD-INF-001)+shared+core(MOD-INF-016)——2项"
  - "Tier1变更→下游task-system检查兼容性+audit-trail检查审计链+feedback-loop检查Dashboard断裂"
rollback_instructions: "consumer分级缺口 → §20 R*"
---

# DB-025-0087：分层消费者注册表——治理信息

治理信息: Tier1(核心)3个 / Tier2(集成)4个 / Tier3(监控)2个。
