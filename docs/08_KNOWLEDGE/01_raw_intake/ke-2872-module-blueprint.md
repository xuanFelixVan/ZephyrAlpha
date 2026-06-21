---
module_id: KE-2772-------module-blueprint-003
title: Level 2：单模块蓝图（Module Blueprint）
category: module_blueprint
---

# Level 2：单模块蓝图（Module Blueprint）

Level 2：单模块蓝图（Module Blueprint）

| 属性 | 值 |
|------|-----|
| 蓝图层 | MODULE |
| ID 前缀 | `MOD-{LAYER}-{NNN}` 或 `MOD-{DOMAIN}-{NNN}` |
| 职责 | 定义**单个系统/模块**的完整设计——边界、状态机、Schema、API、存储、门禁 |
| 包含内容 | (§1-§11 架构设计) + (§12 施工指引) + 消费者注册表 + 依赖声明 |
| 引用关系 | 模块蓝图 MUST 声明 `belongs_to: {上级域蓝图或总蓝图 ID}` |
| 关键约束 | 模块蓝图引用集成合同（CT-*），但集成合同的定义在上级蓝图（域蓝图或总蓝图）|
| 对标 | TOGAF Capability Architecture + K8s Component-level Architecture |
| 加载策略 | AI 仅在需要该模块时阅读完整蓝图 |

**当前已有**：19 份模块蓝图（INF-001~017 + KB-001 + MASTER-001）
