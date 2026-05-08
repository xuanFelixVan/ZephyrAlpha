---
module_id: KE-governance-3_3___________opa_gatekeeper_2-005
title: 3.3 四档执行约定（对标 OPA Gatekeeper 2026）
category: governance
---

# 3.3 四档执行约定（对标 OPA Gatekeeper 2026）

3.3 四档执行约定（对标 OPA Gatekeeper 2026）

| 档位 | 行为 | 使用场景 |
|---|---|---|
| **deny** | 直接拒绝 | L3 三件套 / 量化红线 / OCP 冻结 |
| **dryrun** | 仅记录不拦截 | 新规则过渡期（7-14 天观察） |
| **warn** | 警告但放行 | 非强制规则 / 建议项 |
| **disabled** | 临时关闭 | 紧急场景 / 故障诊断 |

**档位升级路径**：dryrun（7-14d）→ warn（7d）→ deny → 紧急时降 disabled → retrospective 决定回滚。

---
