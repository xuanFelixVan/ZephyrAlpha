---
module_id: KE-954
status: active
title: 5.3 创建模块时的完整步骤（最复杂场景）
category: governance
---

# 5.3 创建模块时的完整步骤（最复杂场景）

5.3 创建模块时的完整步骤（最复杂场景）

模块是横跨最多登记表的工作类型，作为参考模板：

1. **分配 module_id**：查 MOD-ID 登记表，取最后一个 ID 递增
2. **创建物理目录和文件**：`{layer_dir}/{module_name}/` + `index.md` + `blueprint.md` + `delivery/index.md`
3. **登记 MODULE**（module-registry.yaml）：新增 `modules[]` 条目
4. **登记 BPR**（blueprint_registry.yaml）：新增 `blueprints[]` 条目
5. **登记 DOC-INV**：新增文档条目
6. **登记 MOD-ID**：注册新 id
7. **登记 DIR**：注册新目录
8. **登记 AI-AUTH**：声明 AI 自治权限
9. **更新上级层 index.md**：添加模块行
10. **运行校验**：`check_registry_consistency.py` + `check_frontmatter_metadata.py`
