---
module_id: KE-module_blu-2_10_l7___testing___dry-run___-003
title: 2.10 L7 — Testing & Dry-Run（决策 D-018-12）
category: module_blueprint
---

# 2.10 L7 — Testing & Dry-Run（决策 D-018-12）

2.10 L7 — Testing & Dry-Run（决策 D-018-12）

> **决策 D-018-12**：权限配置是可测试代码——需要影响分析、模拟模式和自动化测试框架。
>
> **决策依据**：OPA Rego 单元测试 + D2 policy validation + 企业级权限影响分析。1人+AI 维护下，改了权限没人验证——必须自动化。

```yaml
testing:
  # ─── 权限影响分析 ───
  impact_analysis:
    description: "修改 rbac_roles.yaml 前回答：会影响到多少 Agent、哪些操作"
    query: |
      给定 proposed_change:
        列出所有受影响的 Agent（role_bindings 匹配）
        列出每个 Agent 的权限变化（新增/移除/升级/降级）
        标记有风险的变更（Agent 获得超出当前 maturity 的权限）
    ci_integration: "PR 中修改 rbac_roles.yaml → CI 自动运行 impact_analysis → 输出报告"

  # ─── Dry-Run 模式 ───
  dry_run:
    description: "模拟"如果给这个 Agent 这个权限，在当前上下文下会怎样"——不实际执行"
    modes:
      - "evaluate_agent(agent_id, task_context) → 列出该 Agent 在此任务中所有操作的权限判定"
      - "evaluate_action(agent_id, action) → 单次操作预览判定"
      - "what_if_role_change(agent_id, new_role) → 角色变更前后对比"
    integration: "CI pipeline 中的权限变更预演"

  # ─── 自动化测试框架 ───
  test_framework:
    description: "权限配置 = 可测试代码。每次修改 rbac_roles.yaml 必须通过测试"
    test_types:
      - name: "role_consistency_test"
        description: "每个 Role 的 always_allow/auto_guard/blocked 定义无冲突"
        example: "同一 Role 不能对同一 Tool 同时定义 always_allow 和 blocked"

      - name: "role_coverage_test"
        description: "所有已注册 Tool 至少在一个 Role 中有权限定义（没有孤儿 Tool）"
        example: "MCP 注册的 Tool 必须出现在至少一个 Role 的权限列表中"

      - name: "sequence_guard_test"
        description: "L4 禁止序列规则覆盖所有已知攻击链"
        example: "测试 read_sensitive→send_email 是否被正确阻断"

      - name: "immutable_core_test"
        description: "L0 protected_paths 写入尝试被正确拒绝"
        example: "模拟 Agent 尝试写入 src/zephyr/agent_rbac/rbac_roles.yaml → 预期 BLOCKED"

      - name: "maturity_boundary_test"
        description: "低成熟度 Agent 无法执行需要高成熟度的操作"
        example: "L1 Intern Agent 尝试 auto_guard 操作 → 预期 BLOCKED"
```

---
