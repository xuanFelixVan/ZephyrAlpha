---
module_id: KE-module_blu-2_7____________________d-025-0-005
title: 2.7 冲突检测——文本 + 语义双层（决策 D-025-07）
category: module_blueprint
---

# 2.7 冲突检测——文本 + 语义双层（决策 D-025-07）

2.7 冲突检测——文本 + 语义双层（决策 D-025-07）

> **决策 D-025-07**：冲突检测不能仅依赖 git merge（文本级），必须建立**语义冲突检测层**——当两个 Agent 修改"逻辑关联但文本不重叠"的代码时，git 不会报冲突但运行时可能崩溃（Augment 称为 semantic contradictions）。检测策略是 AST diff + 依赖图分析 + 接口契约对比。
>
> **决策依据**：节码的产品缺陷报告可以在多模态场景下 +38.5 pp 的效果，说明错误的粒度对 _world 的性能有非常依赖差异。"semantic contradictions are the hardest class to detect: changes that look correct in isolation can contradict each other, often passing compilation and linting but failing at runtime"。

```yaml
conflict_detection_layers:
  # === Layer 1: 文本冲突（git merge — 已有，自动）===
  text_conflict:
    mechanism: "git merge conflict"
    detection: "行级冲突——git 自动检测"
    resolution: "先 commit 先赢 / 后 commit 需手动 resolve"
    coverage: "约 30% 的实际冲突场景"

  # === Layer 2: 语义冲突（AST + 依赖图 — 新增）===#
  semantic_conflict:
    mechanism: "AST diff + 模块依赖图 + 接口契约对比"
    detection_rules:
      - name: "SC-DETECT-001: Shared Dependency Mutation"
        condition: "两个 Agent 修改同一模块的不同文件——但该模块的公共接口被同时变更"
        action: "标记为语义冲突 → Coordinator 裁决（合并 or 拒绝 or 串行化）"

      - name: "SC-DETECT-002: Interface Contract Divergence"
        condition: "Agent A 产出 {userId: int}，Agent B 消费 expect {user_id: str}"
        action: "Living Spec 校验失败 → 自动回退到最新 Living Spec → 要求 Agent 重新对齐"

      - name: "SC-DETECT-003: Structural Assumption Clash"
        condition: "Agent A 假设数据库有 transactions 表，Agent B 删除了它"
        action: "依赖图断裂 → Coordinator 阻断 Agent B 的合并 → 通知 Owner"

      - name: "SC-DETECT-004: Semantic Loop（Mirror Mirror）"
        condition: "两个 Agent 对同一产出物反复修改——A 改后 B 改回，循环 ≥ 3 轮"
        action: "检测到 outputs 95%+ 相似（语义哈希）→ 强制终止循环 → Coordinator 接管决策"

  # === Layer 3: 模式化行为冲突（Manifest Diff — 辅助）===
  behavioral_conflict:
    mechanism: "变更意图分析——两个变更是否在'语义空间'中冲突"
    scope: "仅限于影响 system_prompts / AGENTS.md / a2a_registry.yaml 的变更"
    action: "任一 Agent 修改上层配置 → 强制序列化——后改必须等前改合并后 rebase"
```
