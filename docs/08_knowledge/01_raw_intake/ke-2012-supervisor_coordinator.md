---
module_id: KE-1921-----003
status: active
title: 2.5 Supervisor/Coordinator 模式（决策 D-025-05）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.5 Supervisor/Coordinator 模式（决策 D-025-05）

2.5 Supervisor/Coordinator 模式（决策 D-025-05）

> **决策 D-025-05**：A2A 的协调者是**规则驱动的 Coordinator**（确定性规则引擎），而非 LLM 驱动的 Supervisor（Anthropic Claude Code 的 Team Lead。理由：① LLM 驱动的协调者自身也会死锁/幻觉/被操纵——引入新的攻击面；② 1人+AI 场景下规则数量有限，确定性引擎足够；③ Token 成本——规则引擎判定零 Token 消耗（对标 MOD-INF-022 §2.4 经济护栏）。
>
> **决策依据**：DPBench 证明启用 Agent 间 LLM 通信后 5-Agent 死锁率从 25% 跳升到 65%——"通信本身加剧死锁"。Supervisor 自身是 LLM = 在最需要确定性的层级引入了最大不确定性。

```yaml
supervisor_coordinator:
  # === Coordinator 类型 ===
  coordinator_type: "Rule-based Coordinator"
  not: "LLM-based Supervisor"
  reason: "确定性、零 Token、不可操纵"

  # === Coordinator 职责 ===
  responsibilities:
    - role: "Task Decomposition"
      description: "接收高层任务 → 按 spec-scoped 原则分解为互不重叠的子任务"
      rules:
        - "修改同一文件 = 序列化"
        - "修改同一目录不同文件 = 可并行但需 spec 对齐"
        - "修改不同目录 = 安全并行"

    - role: "Agent Assignment"
      description: "按 Agent Card capabilities 自动匹配 → 路由到目标 Agent"
      matching: "Filter（能力覆盖）+ Score（负载 × 历史成功率）——对标 K8s Scheduler Filter/Score 两阶段"
      anti_pattern: "禁止将同一子任务分配给两个 Agent"

    - role: "Progress Monitoring"
      description: "收集各 Agent 的 Task Status → 检测停滞/超时/死锁 → 触发 §2.9"
      heartbeat: "每 30s 各 Agent 上报 progress snapshot"

    - role: "Result Integration"
      description: "各子任务 COMPLETED → Coordinator 整合结果 → 验证一致性 → 交付"

  # === Coordinator 安全约束 ===
  constraints:
    - rule: "Coordinator 自身不执行 Agent 任务——只分解+分配+监控+整合"
    - rule: "Coordinator 的判定逻辑对 AI 只读（对标 MOD-INF-022 §2.5）"
    - rule: "Coordinator 决策全部写入 Audit Trail（MOD-INF-020）"
```
