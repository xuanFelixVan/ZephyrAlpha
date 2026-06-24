---
module_id: KE-2112
status: active
title: 3.4 #13: AIUnderstandabilityConstraint
category: module_blueprint
---

# 3.4 #13: AIUnderstandabilityConstraint

3.4 #13: AIUnderstandabilityConstraint

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\ai_understandability_constraint.py`

实现 `AIUnderstandabilityConstraint` 类：
- **前向编码约束（AI施工时NZC）**：
  - `check_single_file_single_responsibility(file_path)`：每文件 ≤ 1 核心类
  - `check_yaml_zero_ambiguity(yaml_path)`：Python bool 而非 "yes/no"
  - `check_ai_navigable_name(file_path)`：文件名→AI能从文件名推断功能
- **后向审计度量（AI回读时验证）**：
  - `measure_schema_sprawl(config_dir)`：新增 YAML 字段数
  - `measure_import_ambiguity(module_path)`：模糊import数
  - `compute_explainability_score()`：综合可理解性评分
- **AI可理解性总评分 70/100 = 入常规迭代；<70 = AI上下文退化警讯 → 提示Owner回溯**
- 蓝图 L1685-1725 AI理解性约束完整落地
