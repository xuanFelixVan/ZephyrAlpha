---
module_id: KE-governance-src_zephyr_gates__id__yaml-003
title: 创建门禁（src/zephyr/gates/<id>.yaml）
category: governance_rule
---

# 创建门禁（src/zephyr/gates/<id>.yaml）

创建门禁（src/zephyr/gates/<id>.yaml）
python scripts/scaffold.py gate G7 --title "My Gate" --category kms
```

**scaffold.py 自动完成**（无需 AI 记忆）：
1. **查重**：文件名冲突 + BlueprintSearchServer 功能重复检测 + manifest/registry 条目冲突
2. **创建**：temp-file + atomic rename（RULE-ONE 合规）
3. **注册**：自动更新 `__init__.py` `__all__`（模块）/ `script_manifest.yaml`（脚本）/ `_registry.yaml`（门禁）
4. **返回**：文件路径 + 注册位置 + 导入/运行命令
