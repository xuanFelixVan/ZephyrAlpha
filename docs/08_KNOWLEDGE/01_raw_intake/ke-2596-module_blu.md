---
module_id: KE-2501
title: 9. 对标清单
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 9. 对标清单

9. 对标清单

| 对标 | 来源 | 在我们的实现 |
|------|------|------------|
| ITIL 4 ITAM 五步 | ServiceNow CMDB 最佳实践 | L1~L5 一一对应 |
| ISO 19770 | IT资产管理国际标准 | 状态机 + 生命周期追踪 |
| CMDB SSoT | "单一配置管理数据库"原则 | `unified_asset_index.yaml` = SSoT |
| K8s `kubectl api-resources` | 进集群先看有什么资源 | L3 统一资产索引 = 项目级的 api-resources |
| Linux `man hier` | 进系统先了解目录结构 | §2.1.1 TypeClassifier 基于目录语义 |
| Digital Twin (VibeCode) | 代码库序列化 + 加密清单 | raw-asset-scan.json = 代码库快照 |
| Goldman SecDB immutable log | 不可变审计日志 | 生命周期事件 → MOD-INF-020 审计记录 |
| ITIL Problem Management | 已知问题追踪闭环 | orphan/ghost/drift 的发现→修复→验证闭环 |
| `audit_registration.py` | 当前项目孤儿检测 | 升级为 L4 持续对账的完整版 |

---
