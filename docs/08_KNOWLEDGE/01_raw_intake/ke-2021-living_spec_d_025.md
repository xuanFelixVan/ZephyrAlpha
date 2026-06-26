---
module_id: KE-1930-------d-025-06-000
status: active
title: 2.6 Living Spec 同步（决策 D-025-06）
category: module_blueprint
ttl: permanent
---

# 2.6 Living Spec 同步（决策 D-025-06）

2.6 Living Spec 同步（决策 D-025-06）

> **决策 D-025-06**：引入 Living Spec（活文档）机制——各 Agent 在开始工作前自动拉取最新的共享接口规范。这是社区验证过的**事前冲突预防**核心手段。不依赖人工每次贴文档，而是 AGENTS.md 路由自动触发加载。对标 Coware + Augment Code spec-driven decomposition。
>
> **决策依据**：社区实战核心教训——"不要在合并时修冲突，要在写代码前就消除冲突的可能"。"AI 的速度放大了不一致性——一个下午出 2000 行，但 Agent 不会主动去看队友的 Agent 写了什么"。Coware 已将此流程产品化。

```yaml
living_spec:
  # === Living Spec 生命周期 ===
  lifecycle:
    - phase: "SCAN"
      action: "Coordinator 扫描当前代码库 → 提取所有接口契约（类签名/API schema/数据模型）"
      output: "living_spec.yaml——结构化接口规范"
      frequency: "每日启动时 + 每次 Agent 完成子任务后增量更新"

    - phase: "SYNC"
      action: "各 Agent 开始新子任务前 → 自动拉取最新 living_spec.yaml"
      enforcement: "Agent 产出的接口必须匹配 living_spec 中的字段名/类型/格式"

    - phase: "VERIFY"
      action: "Agent 完成任务后 → Coordinator 校验产出是否偏离 living_spec"
      deviation_action: "自动标记 → 通知 Owner → 触发 living_spec 更新或 Agent 修正"

  # === Living Spec 存储 ===
  storage:
    path: "docs/03_modules/_b_track_interfaces/living_spec.yaml"
    format: "YAML——人读 + 机读"
    version: "semver——每次更新 bump patch/minor"

  # === Living Spec 与 Agent Card 的关系 ===
  relation:
    agent_card: "声明'我能做什么'（能力）"
    living_spec: "定义'产出应该长什么样'（接口契约）"
    trigger: "Agent Card 匹配 → Living Spec 同步 → 开始施工"
```
