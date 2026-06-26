---
module_id: KE-1595------models-000
title: 步骤 2：按域拆分 models
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 步骤 2：按域拆分 models

步骤 2：按域拆分 models

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §9 R1 缓解 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\shared\models_rbac.py` 等 |
| 验收标准 | models.py 仅做 re-export，实际定义在域文件中 |
| G7 检查项 | 所有现有 import 路径不受影响？ |
