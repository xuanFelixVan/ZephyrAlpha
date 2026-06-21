---
module_id: KE-4207------------v2-1-003
title: 8. 需要更新的相关内容（v2.1 补全）
category: module_blueprint
---

# 8. 需要更新的相关内容（v2.1 补全）

8. 需要更新的相关内容（v2.1 补全）

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` | 版本号 2.1.0 + 完整度 95% + status phase_1_complete | v2.1 盲点补全 |
| 2 | DB YAML SSoT | `D:\ZephyrAlpha\architecture-model\layers\b_db.yaml` | 补全 3 个缺失 .py + 更新 schema_version + 修正 db_file_path | SSoT 漂移修复（§17） |
| 3 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture-model\module_id_registry.yaml` | DB 模块状态 active | 代码施工完成 |
| 4 | KBG-0030 | KBG-0030 | 更新连接管理/备份策略引用 | v2.0 新增 database_manager |
| 5 | AI 自治权限注册表 | GOV-AI-001 | 注册 MOD-INF-012 的 AI 操作权限边界 | blueprint 新增 belongs_to + references 链 |

---
