﻿---
module_id: FILE_NAMING_STANDARD_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 审计报告、合规检查
standard_type: 文档治理规范
applicable_scope: 全系统文件命名规范
compliance_level: 专业标准
parent_document: ../INDEX.md
---
---

# 文件命名规范标准

> **核心职责**: 定义文件命名的标准格式、命名规则和检查机制
> **职责边界**: 
> - ✅ 本文档负责：命名标准制定、命名规则定义、检查机制设计
> - ❌ 本文档不负责：具体文件的命名实施、命名冲突解决

---

## 📋 规范概要

**规范版本**: v1.0.0  
**适用范围**: 全系统所有文件（包括文档和代码）  
**规范目标**: 确保文件命名清晰、一致、无歧义  
**规范性质**: 强制性标准

---

## 🎯 命名基本原则

### 1. 四大核心原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **清晰性** | 文件名应清晰反映文件内容 | ✅ FACTOR_CALCULATION_FRAMEWORK.md |
| **一致性** | 同类文件使用统一的命名格式 | ✅ 所有蓝图文件使用_BLUEPRINT.md后缀 |
| **简洁性** | 文件名应简洁明了，避免过长 | ✅ RISK_BUDGET_SYSTEM.md |
| **可读性** | 文件名应易于阅读和理解 | ✅ PORTFOLIO_OPTIMIZATION.md |

### 2. 禁止事项

| 禁止项 | 原因 | 示例 |
|--------|------|------|
| **中文命名** | 跨平台兼容性问题 | ❌ 风险预算系统.md |
| **空格** | 命令行操作困难 | ❌ Risk Budget System.md |
| **特殊字符** | 系统兼容性问题 | ❌ Risk@Budget#System.md |
| **过长命名** | 可读性差 | ❔ RISK_BUDGET_SYSTEM_PORTFOLIO_OPTIMIZATION_FRAMEWORK_V2.md |

---

## 📝 文档命名规范

### 1. Markdown文档命名规范

#### 1.1 标准格式

```
[模块名称]_[文档类型].md
```

**模块名称**: 使用大写字母和下划线  
**文档类型**: 使用标准后缀

#### 1.2 文档类型后缀

| 文档类型 | 后缀 | 示例 |
|---------|------|------|
| **标准规范** | _STANDARD.md | FACTOR_CALCULATION_STANDARD.md |
| **蓝图设计** | _BLUEPRINT.md | RISK_BUDGET_SYSTEM_BLUEPRINT.md |
| **实施指南** | _GUIDE.md | DEPLOYMENT_GUIDE.md |
| **操作手册** | _MANUAL.md | OPERATION_MANUAL.md |
| **分析报告** | _REPORT.md | AUDIT_REPORT.md |
| **测试文档** | _TEST.md | UNIT_TEST.md |
| **API文档** | _API.md | FACTOR_ENGINE_API.md |
| **配置文档** | _CONFIG.md | SYSTEM_CONFIG.md |

#### 1.3 特殊文档命名

| 文档名称 | 用途 | 示例 |
|---------|------|------|
| **README.md** | 模块说明和快速入门 | 每个目录的README.md |
| **INDEX.md** | 目录索引和导航 | 每个目录的INDEX.md |
| **ARCHITECTURE.md** | 架构设计文档 | 模块架构文档 |
| **CHANGELOG.md** | 变更记录 | 版本变更记录 |

### 2. 版本化文档命名

#### 2.1 版本后缀格式

```
[模块名称]_[文档类型]_V[版本号].md
```

**示例**:
- FACTOR_CALCULATION_STANDARD_V1.md
- RISK_BUDGET_SYSTEM_BLUEPRINT_V2.md

#### 2.2 日期后缀格式

```
[模块名称]_[文档类型]_[YYYYMMDD].md
```

**示例**:
- AUDIT_REPORT_20260407.md
- OPTIMIZATION_REPORT_20260407.md

---

## 💻 代码文件命名规范

### 1. Python文件命名规范

#### 1.1 模块文件

```
[模块名称].py
```

**规则**:
- 使用小写字母和下划线
- 避免使用中文
- 文件名应简洁明了

**示例**:
- ✅ factor_calculator.py
- ✅ risk_budget_system.py
- ❌ FactorCalculator.py
- ❌ 风险预算系统.py

#### 1.2 测试文件

```
test_[模块名称].py
```

**示例**:
- test_factor_calculator.py
- test_risk_budget_system.py

#### 1.3 工具脚本

```
[功能描述]_[工具类型].py
```

**示例**:
- automated_check_mechanism.py
- document_governance_audit.py

### 2. 配置文件命名规范

#### 2.1 YAML配置文件

```
[配置类型].yaml
或
[配置类型].yml
```

**示例**:
- config.yaml
- database.yml
- logging.yaml

#### 2.2 JSON配置文件

```
[配置类型].json
```

**示例**:
- package.json
- tsconfig.json

---

## 🔍 命名检查机制

### 1. 自动化检查

#### 1.1 检查项

| 检查项 | 规则 | 严重程度 |
|--------|------|---------|
| **中文检查** | 文件名不得包含中文字符 | 🔴 高风险 |
| **空格检查** | 文件名不得包含空格 | 🟡 中风险 |
| **特殊字符检查** | 文件名不得包含特殊字符 | 🟡 中风险 |
| **长度检查** | 文件名长度不超过100字符 | 🟢 低风险 |
| **格式检查** | 文件名符合标准格式 | 🟡 中风险 |

#### 1.2 检查脚本

使用 `automated_check_mechanism.py` 进行自动化检查：

```python
def check_filename_naming(file_path):
    """检查文件命名规范"""
    file_name = os.path.basename(file_path)
    
    # 检查是否包含中文
    has_chinese = any('\u4e00' <= char <= '\u9fff' for char in file_name)
    
    # 检查是否包含空格
    has_space = ' ' in file_name
    
    # 检查是否符合命名规范
    is_standard = bool(re.match(r'^[A-Z_0-9]+\.md$', file_name))
    
    return {
        'has_chinese': has_chinese,
        'has_space': has_space,
        'is_standard': is_standard,
        'is_valid': not has_chinese and not has_space and is_standard
    }
```

### 2. 定期审查

#### 2.1 审查频率

- **每周检查**: 自动化检查所有文件命名
- **新建文件**: 创建时检查命名规范
- **问题发现**: 发现命名问题时立即审查

#### 2.2 审查流程

```
1. 自动化扫描
   ├── 扫描所有文件
   ├── 检查命名规范
   └── 生成检查报告

2. 问题分类
   ├── 高风险问题（中文命名）
   ├── 中风险问题（空格、特殊字符）
   └── 低风险问题（格式不规范）

3. 问题修复
   ├── 自动重命名（标准映射）
   ├── 人工确认（复杂情况）
   └── 更新引用链接

4. 验证确认
   ├── 确认命名符合规范
   ├── 确认引用链接有效
   └── 更新审查记录
```

---

## 📊 命名质量标准

### 1. 质量指标

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| **规范符合率** | ≥95% | 符合规范文件数 ÷ 总文件数 |
| **中文命名率** | 0% | 中文命名文件数 ÷ 总文件数 |
| **空格命名率** | 0% | 包含空格文件数 ÷ 总文件数 |
| **格式一致性** | ≥90% | 格式一致文件数 ÷ 总文件数 |

### 2. 质量等级

| 等级 | 规范符合率 | 状态 | 行动 |
|------|-----------|------|------|
| **优秀** | ≥99% | ✅ | 保持现状 |
| **良好** | 95-99% | ✅ | 持续改进 |
| **合格** | 90-95% | ⚠️ | 立即改进 |
| **不合格** | <90% | ❌ | 紧急修复 |

---

## 🚫 常见问题与解决方案

### 1. 中文命名问题

**问题**: 文件名包含中文字符  
**影响**: 跨平台兼容性问题、命令行操作困难  
**解决**: 使用英文命名，建立中文到英文映射表

**映射示例**:

| 中文文件名 | 英文文件名 |
|-----------|-----------|
| 资产类别定义.md | ASSET_CLASS_DEFINITION.md |
| 资产配置模型.md | ASSET_ALLOCATION_MODEL.md |
| 风险调整机制.md | RISK_ADJUSTMENT_MECHANISM.md |

### 2. 空格命名问题

**问题**: 文件名包含空格  
**影响**: 命令行操作困难、URL编码问题  
**解决**: 使用下划线替代空格

**示例**:
- ❌ Risk Budget System.md
- ✅ RISK_BUDGET_SYSTEM.md

### 3. 命名不一致问题

**问题**: 同类文件命名格式不一致  
**影响**: 可读性差、维护困难  
**解决**: 制定统一命名规范，批量重命名

**示例**:
- ❌ factor_calculator.py, FactorEngine.py, risk-budget.py
- ✅ factor_calculator.py, factor_engine.py, risk_budget.py

---

## 📚 最佳实践案例

### 案例1: 标准文档命名

```
docs/
├── 02_FACTOR_LIBRARY/
│   ├── README.md
│   ├── INDEX.md
│   ├── 01_STANDARDS/
│   │   ├── FACTOR_CALCULATION_STANDARD.md
│   │   ├── FACTOR_CLASSIFICATION_STANDARD.md
│   │   └── FACTOR_QUALITY_STANDARD.md
│   └── 02_BLUEPRINTS/
│       ├── FACTOR_ENGINE_BLUEPRINT.md
│       └── RISK_BUDGET_SYSTEM_BLUEPRINT.md
```

### 案例2: 报告文档命名

```
docs/
├── 09_AUDIT/
│   ├── REPORTS/
│   │   ├── AUDIT_REPORT_20260407.md
│   │   └── OPTIMIZATION_REPORT_20260407.md
│   └── STATE/
│       ├── automated_check_result_20260407_031229.json
│       └── audit_state_20260407.json
```

### 案例3: 代码文件命名

```
scripts/
├── automated_check_mechanism.py
├── document_governance_audit.py
├── fix_duplicate_module_id.py
└── tests/
    ├── test_factor_calculator.py
    └── test_risk_budget_system.py
```

---

## 📝 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本，文件命名规范标准 | 首席文档架构师 |
