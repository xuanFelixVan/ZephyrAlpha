---
module_id: KE-documentat-1_3____03-aa-003
title: 1.3 与 `03-AA` 的边界铁律
category: documentation
---

# 1.3 与 `03-AA` 的边界铁律

1.3 与 `03-AA` 的边界铁律

**铁律**：03-AA 定义的是 `src/zephyr/` 14 层 Python 后端架构（L00-L13 + shared + api_gateway 子模块），本视图（10-FE）定义的是 `frontend/` 前端独立平台架构。两者**物理隔离、技术栈异构、独立构建、独立部署**。

**接触点**：仅在 L08 `api_gateway/` 子模块（FastAPI + WebSocket + OpenAPI Spec 生成）——这是前后端**唯一合法对接点**。任何试图让前端直接访问 L00-L07/L09-L13 的设计均违反 ADR-0007。
