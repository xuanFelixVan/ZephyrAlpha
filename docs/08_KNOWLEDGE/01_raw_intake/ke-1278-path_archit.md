---
module_id: KE-1191------------path-archit-003
status: active
title: MTH-013：路径架构合规创建原则（Path Architecture Compliance） [MUST — 所有文件/目录创建操作]
category: governance
ttl: permanent
---

# MTH-013：路径架构合规创建原则（Path Architecture Compliance） [MUST — 所有文件/目录创建操作]

MTH-013：路径架构合规创建原则（Path Architecture Compliance） [MUST — 所有文件/目录创建操作]

AI 永远不得自行决定新目录的层级结构。所有路径操作必须经过索引导航——索引中有定义则按定义，索引中无定义则提交 Owner 讨论。

> **对标**：ITIL SACM CI Registration——任何新配置项创建前必须验证其在 CMDB 中的注册状态。Kubernetes Namespace 管理——命名空间按角色创建，不得由 pod 自行声明。Terraform State——所有资源路径必须可追溯到 provider schema。共同模式：**创建先于验证，验证先于行动**。
