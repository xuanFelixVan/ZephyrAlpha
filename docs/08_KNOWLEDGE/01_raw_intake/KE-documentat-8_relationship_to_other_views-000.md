---
module_id: KE-documentat-8_relationship_to_other_views-000
title: §8 Relationship to Other Views / 与其他视图的关系
category: documentation
---

# §8 Relationship to Other Views / 与其他视图的关系

§8 Relationship to Other Views / 与其他视图的关系

> **📊 视图依赖关系图**：见 [`diagrams/view-dependencies.mmd`](diagrams/view-dependencies.mmd)

**视图定位说明**：
- **本视图上游**：BA（业务流驱动）/ AA（模块边界）/ DA（数据载荷）/ TA（技术协议）
- **本视图下游**：SEC（安全域需知道所有外部接入点） / OPS（运维需监控所有集成健康状态）
- **本视图不覆盖**：具体物理部署（→ TA §6）/ 安全认证机制（→ 06-SEC）/ 运维告警（→ 08-OPS）

---
