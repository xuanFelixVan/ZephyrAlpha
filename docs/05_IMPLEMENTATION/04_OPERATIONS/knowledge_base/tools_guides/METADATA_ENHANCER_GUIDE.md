---
standard_type: 工具指南
applicable_scope: 元数据管理
compliance_level: 正式标准
parent_document: ../README.md
implementation_status: 已完成
owner: 文档管理员
version: 1.0.0
module_id: METADATA_ENHANCER_GUIDE
created_date: 2026-04-02
last_updated: 2026-04-02
tags: ["工具指南", "元数据", "自动化", "使用手册"]
---
# 元数据增强工具使用指南

**文档版本**: 1.0.0
**最后更新**: 2026-04-02
**文档所有者**: 文档管理员

---

## 1. 工具概述

### 1.1 工具简介

元数据增强工具用于自动推断和补充文档元数据，确保文档元数据完整性和规范性。

### 1.2 主要功能

- ✅ 自动推断元数据
- ✅ 批量添加元数据
- ✅ 验证元数据完整性
- ✅ 生成增强报告

---

## 2. 快速开始

### 2.1 基本使用

**增强元数据**:
```bash
python scripts/metadata_enhancer.py
```

**验证元数据**:
```bash
python scripts/metadata_enhancer.py --validate
```

---

## 3. 功能详解

### 3.1 元数据推断

**推断规则**:
- 从文件路径推断module_id
- 从文件名推断标题
- 从目录结构推断分类

**示例**:
```
文件路径: docs/02_FACTOR_LIBRARY/01_FACTORS/MOMENTUM_FACTOR.md
推断结果:
  - module_id: MOMENTUM_FACTOR
  - category: 02_FACTOR_LIBRARY
  - title: 动量因子
```

### 3.2 元数据验证

**必需字段**:
- owner
- version
- module_id
- created_date
- last_updated

**推荐字段**:
- standard_type
- applicable_scope
- compliance_level
- parent_document

---

## 4. 配置选项

### 4.1 推断规则配置

```yaml
inference_rules:
  module_id:
    source: "filename"
    pattern: "([A-Z_]+)\\.md"
  
  category:
    source: "directory"
    mapping:
      "01_FRAMEWORK": "框架文档"
      "02_FACTOR_LIBRARY": "因子库"
```

---

## 5. 最佳实践

### 5.1 使用模板

**创建文档时使用模板**:
```bash
# 使用文档模板
cp docs/09_AUDIT/TEMPLATES/DOCUMENT_TEMPLATE.md new_document.md
```

### 5.2 定期验证

**每月验证元数据完整性**:
```bash
python scripts/metadata_enhancer.py --validate
```

---

## 6. 参考文档

- [元数据增强工具技术规范](../../05_TECHNICAL_SPECIFICATIONS/METADATA_ENHANCER_SPECIFICATION.md)
- [文档模板](../../09_AUDIT/TEMPLATES/DOCUMENT_TEMPLATE.md)

---

**文档状态**: 正式标准
**下次更新**: 2026-07-02
