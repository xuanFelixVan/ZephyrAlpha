---
module_id: KE-314----------lifecycle-refer-005
status: active
title: 4.1.1 生命周期引用约束（Lifecycle Reference Constraint）——2026-05-02 新增
category: documentation
---

# 4.1.1 生命周期引用约束（Lifecycle Reference Constraint）——2026-05-02 新增

4.1.1 生命周期引用约束（Lifecycle Reference Constraint）——2026-05-02 新增

> **对标**：Kubernetes Admission Controller（准入控制器拒绝非法请求） + ITIL Change Enablement（变更前评估消费者影响）
>
> **动机**：2026-05-02 审计发现 GOV-MOD-002（draft，已升格 active v1.0.0）被 6 个 active 文件量产级引用、GOV-MOD-007（draft，已升格 active v2.1.0）被 registry_of_registries.yaml 引用。status 字段与 depends_on 之间没有互锁机制——"出生即公民"的默认假设覆盖了 draft 状态的"我还不是正式公民"的真实含义。

##### MUST 规则

| # | 规则 | 违反后果 |
|---|------|---------|
| **LRC-001** | `status: draft` 的文件 **不得** 被任何 `status: active` 的文件通过 `depends_on` 声明依赖 | 消费者获得的规则可能尚未稳定——AI session 行为漂移 |
| **LRC-002** | `status: draft` 的文件 **不得** 被任何 `status: active` 的文件在正文中作为权威引用（`see X §Y` 形式的规范性引用） | 同上 |
| **LRC-003** | 审批 `draft → active` 升格时，必须**先检查消费者清单**——所有已引用该文件的其他文件是否需要同步变更 | 升格后发现消费者与新版不兼容——返工成本 |

##### SHOULD 规则

| # | 规则 |
|---|------|
| **LRC-004** | `draft` 文件被 3 个以上活跃文件引用时，应评估是否已达 `active` 成熟度——实质活跃应升格 |
| **LRC-005** | 新 AI session 读到 `draft` 文件被多个活跃文件引用时，应标记为 MEDIUM Finding 提请 Owner 裁定 |

##### 设计意图：为什么 stage 比 status 更根本

当前 `status` 字段是**描述性**的——它描述文件当前状态，但不约束文件的交互行为。
对标 Kubernetes：alpha API 不能被 stable API 依赖——不是因为手动标了 `status: alpha`，而是因为它没通过 graduation gate。

**未来方向**（beta+）：引入 `lifecycle_stage` 字段，由门禁系统自动推进：

```
draft_stage  →  blueprint_review  →  construction_review  →  active_stage
  （出生）         （蓝图门通过）          （施工门通过）            （生产就绪）
```

`status` 由 `lifecycle_stage` 推导：
- `lifecycle_stage < active_stage` → `status: draft`（不可被 active 文件引用）
- `lifecycle_stage >= active_stage` → `status: active`（可被引用）


##### `lifecycle_stage` 字段定义（beta 落地）

| stage 值 | 含义 | 对应的门 | 等价 status |
|:---------|:-----|:--------|:-----------:|
| `draft` | 草稿阶段——内容未稳定，AI 自由编辑 | 无 | `draft` |
| `blueprint_reviewed` | 已通过蓝图评审——设计方向已确认 | GATE-BP-001（蓝图完整性门） | `draft`（不可被 active 引用） |
| `construction_reviewed` | 已通过施工评审——实现方案已验证 | GATE-CT-001（施工可执行性门） | `draft`（不可被 active 引用） |
| `active` | 生产就绪——可供全项目引用 | GATE-AD-001（active 准入门） | `active` |

**流转约束**：`lifecycle_stage` 只进不退（只能 forward，不能 rollback），对标 Kubernetes API version 的单向演进策略。
