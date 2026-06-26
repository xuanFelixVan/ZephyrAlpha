---
module_id: KE-308
status: active
title: 3.3 doc_type 与 layer 的联动
category: documentation
ttl: permanent
---

# 3.3 doc_type 与 layer 的联动

3.3 doc_type 与 layer 的联动

`doc_type` 回答"这是什么品种"，`layer` 回答"属于哪个领域"。两者组合定位文档。

> 完整映射表见 vocabulary YAML 各条目的 `allowed_directories` 字段。
> 以下为典型示例（非完整枚举）：

| 组合示例 | 含义 |
|---------|------|
| `doc_type: policy` + `layer: cross_layer` | 全局强制规则 |
| `doc_type: standard` + `layer: cross_layer` | 全局推荐做法 |
| `doc_type: standard` + `layer: ml_train` | 机器学习层推荐做法 |
| `doc_type: blueprint` + `domain: data` | 数据源层蓝图 |
| `doc_type: construction_plan` + `domain: data` | 数据源层施工图 |
| `doc_type: architecture_view` + `layer: cross_layer` | 跨层正式架构视图 |
| `doc_type: plan` + `layer: cross_layer` | 跨层任务书 |
| `doc_type: roadmap` + `layer: cross_layer` | 跨层路线图 |
