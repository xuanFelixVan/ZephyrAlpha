---
module_id: KE-module_blu-4_0___________data____________-000
title: 4.0 数据引擎物理布局（`data/`）——数据库文件独立于 Markdown 文档
category: module_blueprint
---

# 4.0 数据引擎物理布局（`data/`）——数据库文件独立于 Markdown 文档

4.0 数据引擎物理布局（`data/`）——数据库文件独立于 Markdown 文档

**设计原则（对标 12-Factor App §3 + ChromaDB 官方 + SQLite 最佳实践）**：

> 代码和数据的生命周期不同——代码通过 Git 版本控制、数据通过迁移脚本演化。Markdown KE 文件（人类可读知识卡片）属于 `docs/` 图书馆，SQLite/ChromaDB 二进制文件（机器运行时数据）属于 `data/` 机房。

**物理路径（环境变量驱动）**：

```yaml
