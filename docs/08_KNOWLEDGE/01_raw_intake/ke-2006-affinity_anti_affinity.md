---
module_id: KE-1915---anti-affinity---000
status: active
title: 2.5 Affinity / Anti-Affinity 约束矩阵（对标 K8s podAffinity/podAntiAffinity + Inter-Pod
category: module_blueprint
---

# 2.5 Affinity / Anti-Affinity 约束矩阵（对标 K8s podAffinity/podAntiAffinity + Inter-Pod

2.5 Affinity / Anti-Affinity 约束矩阵（对标 K8s podAffinity/podAntiAffinity + Inter-Pod Affinity）

> **B93 第七轮审计**——双盲审查的独立性要求 M3(生成) 和 M7(审查) 必须用不同模型，否则双盲退化到单盲。

| 约束类型 | 约束项 | 节点A | 节点B | 权重 | 说明 |
|:---:|------|:---:|:---:|:---:|------|
| **mandatoryAntiAffinity** | model | M3 | M7 | hard | 双盲审查必须用不同模型——M3 deepseek ↔ M7 glm，禁止同模 |
| **preferredAntiAffinity** | model | M8 | M9 | soft | 建议合规检查 + 风险评估用不同模型，交叉覆盖不同类型漏洞 |
| **mandatoryAffinity** | sandbox | M1~M4 | — | hard | A 区生产模块必须在 full/standard sandbox，不可降级到 restricted |
| **mandatoryAffinity** | pipeline | A 区全部 | — | hard | A 区产出物必须经 M5 打包→M6 边界标记（AP2），不可跨区直通 |
| **preferredAffinity** | model | M8~M11 | — | soft | B 区后半段（report+gating）优先用 deepseek，降低审查成本 |

**M3↔M7 antiAffinity 硬约束影响**：如果 deepseek 不可用 → M3 降级到 glm → 此时 M7 被迫改用 claude（因为不能和 M3 同模）→ claude 成本上升但保证双盲独立性。这是双盲审计体系的安全底线。

---
