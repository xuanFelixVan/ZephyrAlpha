---
module_id: KE-365
title: "> ****:"
category: best_practice
source_file: "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/database/P0-02_Data_Dictionary.md"
source_git_deleted: true
original_path: "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/database/P0-02_Data_Dictionary.md"
deleted_in_commit: "df471735fd29b263f7fc120a34231183e2a53dc6"
recovery_date: "2026-04-16"
extracted_date: "2026-04-16"
version: "1.0.0"
status: Active
layer: L01
owner: ZephyrAlpha-Owner
---

# > ****:

## 核心内容摘要
#### 

| ?|  |  | ?| ?|  |  |  |  |  |  |  |
|--------|----------|----------|----------|--------|------|------|----------|----------|----------|----------|----------|
| **id** | BIGSERIAL | ID | 1 ~ 9,223,372,036,854,775,807 |  | ?| PRIMARY KEY | 1 |  | ?| ?| ?|
| **account_code** | VARCHAR(50) | ?| ?0 | ?| ?| NOT NULL, UNIQUE | 'ACC_20260402_001' |  | ?| ACC_YYYYMMDD_XXX |  |
| **account_name** | VARCHAR(100) |  | ?00 | ?| ?| NOT NULL | '' |  | ?|  | /?|
| **account_type** | VARCHAR(20) |  |...

## 关键设计要点
1. 该文件包含重要的技术规格和设计决策
2. 适用于Phase 2施工阶段参考
3. 具体内容请查看原始文件恢复命令

## 适用场景
- Phase 2 施工中L01层的实现参考
- 相关模块的设计决策依据

## 原始文件
- 恢复命令：`git show df471735fd29b263f7fc120a34231183e2a53dc6^:docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/database/P0-02_Data_Dictionary.md`
