---
module_id: KE-1824------------d-022-17-004
status: active
title: 2.24 VIGIL式自愈维护运行时（决策 D-022-17）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.24 VIGIL式自愈维护运行时（决策 D-022-17）

2.24 VIGIL式自愈维护运行时（决策 D-022-17）

> **决策 D-022-17**：引入一个专用的维护Agent（VIGIL模式），它不是做用户任务的Agent，而是专门观察、诊断、修复其他Agent行为的"元Agent"。与L1自愈（同一Agent自修复）不同，VIGIL是外部观察者+修复者。
> **对标**：VIGIL Reflective Runtime——EmoBank情感账本+RBT(Roses/Buds/Thorns)诊断+Core Identity不可变+Adaptive Section仅可修改。

```yaml
vigil_maintenance_runtime:
  architecture: |
    升级引擎 ──observes──▶ 任务Agent(DeepSeek/GLM/Claude)
       ▲                        │
       │                        ▼
       └──diagnoses & repairs── Log Stream
    VIGIL只做维护，不做用户任务

  emotion_bank:
    pattern: "将Agent行为事件转化为结构化情感表示(EmoBank)"
    dimensions: ["stability", "efficiency", "safety_compliance", "goal_alignment"]
    decay: "旧情绪随指数衰减(半衰期=24h)——最近行为权重更高"

  rbt_diagnosis:
    Roses: "稳定正确的行为模式→加强/固化"
    Buds: "新兴的有潜力但未稳定行为→监控/培育"
    Thorns: "系统性故障模式→触发修复/升级"

  core_identity_immutability:
    rule: "Agent的CORE_IDENTITY块(升级规则+安全策略+核心目标)byte-for-byte不可变"
    enforcement: "任何尝试修改→立刻abort+升级为P0"

  adaptive_section:
    rule: "仅ADAPTIVE_SECTION(行为提示词/工作流程细节)可被VIGIL修改"
    constraint: "修改必须基于结构化的诊断证据+差异报告"

  integration_with_escalation:
    rule: "VIGIL的Thorns诊断→自动路由到升级协议"
    severity: "重复Thorn模式→自动升级P1; RBT诊断失败→P0"
```

---
