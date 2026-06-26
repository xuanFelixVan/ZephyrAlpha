---
module_id: KE-2344
status: active
title: 6. 产出物存放目录
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 6. 产出物存放目录

6. 产出物存放目录

> ⚠️ 防路径漂移：蓝图阶段**必须**规划好所有产出物的物理存放路径。
> AI 施工时**必须**严格按此路径存放，**不得**自行创建新路径。
> **所有路径必须是绝对路径**（含盘符）。
> 路径必须与 GOV-DOC-002（trae_028_doc_structure_naming.yaml）§5.1.2 路径映射表一致。
> 新目录/新文件创建必须遵守 **MTH-013 路径架构合规创建原则**——先在索引中查询再创建，不得自行决定目录层级。

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\{layer}\{module-name}\blueprint.md` | 本文件（含设计和施工指引） |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\{layer_id}\` | Python 源码 |
| 测试代码 | `D:\ZephyrAlpha\tests\{layer_id}\` | 测试用例 |

> 💡 **一个文件，全流程覆盖**：对于 100% AI 开发的项目，蓝图和施工指引合并在一份 `blueprint.md` 中。AI 读这一份文件，就同时获得架构定义（第 1-10 节）和实施步骤（第 11 节）。

---
