﻿---
module_id: DOCUMENT_NAMING_STANDARD_001

standard_id: DOCUMENT_NAMING_STANDARD_001
version: 1.0.0
status: Active
created_date: 2026-04-03
last_updated: 2026-04-03
owner: 首席文档架构?standard_type: 专业量化机构文档命名规范
applicable_scope: 全系统文档管?compliance_level: 专业标准
parent_document: docs/01_FRAMEWORK/DOCUMENT_NUMBERING_STANDARD.md
responsibility:
  - 系统框架、架构设计

---
---
---

# 清风量化系统文档命名规范标准
> **核心职责**: 标准规范制定
> **职责边界**: 
> - ✅ 本文档负责：标准规范制定相关内容
> - ❌ 本文档不负责：其他模块内容


> **标准编号**: `DOC_NAMING_STD_001`
> **版本**: v1.0.0
> **生效日期**: 2026-04-03
> **强制执行**: 所有新建文档必须遵循本标准

---

## 1. 总则

### 1.1 目的
制定统一的文档命名规范，提高文档可读性、可维护性和可检索性，符合专业量化机构标准?
### 1.2 适用范围
本标准适用于清风量化系统所有文档，包括但不限于?- 蓝图文档（BLUEPRINT?- 技术规格书（TECHNICAL_SPECIFICATION?- 实施指南（IMPLEMENTATION_GUIDE?- 操作手册（OPERATION_MANUAL?- 审计报告（AUDIT_REPORT?- 评审报告（REVIEW_REPORT?
### 1.3 基本原则
1. **一致性原?*: 同类文档使用相同的命名模?2. **清晰性原?*: 文件名应清晰表达文档内容和类?3. **简洁性原?*: 避免过长的文件名，控制在50字符以内
4. **可排序性原?*: 文件名应便于按类型和时间排序
5. **避免特殊字符**: 仅使用字母、数字、下划线和连字符

---

## 2. 命名规范

### 2.1 通用格式

```
[文档类型]_[模块名称]_[子模?功能]_[版本/日期].md
```

**示例**:
- `BLUEPRINT_DATA_LINEAGE_TRACKING_v1.0.md`
- `TECHNICAL_SPEC_DATACLEANER_v1.0.md`
- `AUDIT_REPORT_LAYER1_GOVERNANCE_20260403.md`

### 2.2 文档类型标识

| 文档类型 | 标识?| 示例 |
|---------|--------|------|
| 蓝图文档 | `BLUEPRINT` | `BLUEPRINT_DATA_LINEAGE_TRACKING.md` |
| 技术规格书 | `TECHNICAL_SPEC` | `TECHNICAL_SPEC_DATACLEANER.md` |
| 实施指南 | `IMPLEMENTATION_GUIDE` | `IMPLEMENTATION_GUIDE_DATA_CLEANING.md` |
| 操作手册 | `OPERATION_MANUAL` | `OPERATION_MANUAL_QMT_SETUP.md` |
| 审计报告 | `AUDIT_REPORT` | `AUDIT_REPORT_LAYER1_GOVERNANCE_20260403.md` |
| 评审报告 | `REVIEW_REPORT` | `REVIEW_REPORT_DATACLEANER_TECHNICAL.md` |
| 索引文档 | `INDEX` | `INDEX.md` |
| 说明文档 | `README` | `README.md` |

### 2.3 模块命名规范

#### 2.3.1 核心模块
- `DATA_LINEAGE` - 数据血?- `DATA_CLEANING` - 数据清洗
- `DATA_VALIDATION` - 数据校验
- `FACTOR_ENGINE` - 因子引擎
- `STRATEGY_ENGINE` - 策略引擎
- `RISK_CONTROL` - 风险控制
- `PORTFOLIO_OPTIMIZATION` - 组合优化

#### 2.3.2 Layer层标?- `LAYER0` - 数据源层
- `LAYER1` - 数据预处理层
- `LAYER2` - 因子计算?- `LAYER3` - 策略信号?- `LAYER4` - 机器学习?- `LAYER5` - 策略执行?- `LAYER6` - 组合优化?- `LAYER7` - 风险控制?- `LAYER8` - 系统接口?
### 2.4 版本标识规范

#### 2.4.1 版本号格?```
v[主版本].[次版本].[修订版本]
```

**示例**:
- `v1.0.0` - 初始版本
- `v1.1.0` - 功能增强
- `v1.1.1` - 问题修复

#### 2.4.2 日期格式
```
YYYYMMDD
```

**示例**:
- `20260403` - 2026???
### 2.5 特殊文档命名

#### 2.5.1 索引文档
- **格式**: `INDEX.md`
- **位置**: 每个目录都应有INDEX.md
- **示例**: `docs/05_IMPLEMENTATION/INDEX.md`

#### 2.5.2 说明文档
- **格式**: `README.md`
- **位置**: 每个主要目录都应有README.md
- **示例**: `docs/05_IMPLEMENTATION/README.md`

#### 2.5.3 归档文档
- **格式**: `[原文件名]_ARCHIVED.md`
- **位置**: `docs/06_ARCHIVE/`
- **示例**: `DATA_CLEANING_ARCHIVED.md`

---

## 3. 命名示例

### 3.1 蓝图文档

| 正确命名 | 错误命名 | 说明 |
|---------|---------|------|
| `BLUEPRINT_DATA_LINEAGE_TRACKING.md` | `data_lineage_blueprint.md` | 使用大写字母和下划线 |
| `BLUEPRINT_QUALITY_MONITORING.md` | `QualityMonitoringBlueprint.md` | 避免驼峰命名 |
| `BLUEPRINT_AUTO_REPAIR_ENGINE.md` | `auto-repair-engine-blueprint.md` | 避免连字?|

### 3.2 技术规格书

| 正确命名 | 错误命名 | 说明 |
|---------|---------|------|
| `TECHNICAL_SPEC_DATACLEANER.md` | `datacleaner_spec.md` | 使用完整单词 |
| `TECHNICAL_SPEC_DATA_VALIDATOR.md` | `DataValidator_Technical_Specification.md` | 使用下划线分?|
| `TECHNICAL_SPEC_FACTOR_ENGINE.md` | `factor-engine-spec.md` | 避免连字?|

### 3.3 审计报告

| 正确命名 | 错误命名 | 说明 |
|---------|---------|------|
| `AUDIT_REPORT_LAYER1_GOVERNANCE_20260403.md` | `layer1_audit_2026-04-03.md` | 使用标准日期格式 |
| `AUDIT_REPORT_LAYER5_DUPLICATES_20260403.md` | `Layer5_Duplicates_Audit.md` | 包含日期标识 |
| `AUDIT_REPORT_SYSTEM_WIDE_20260403.md` | `system-wide-audit-report.md` | 使用下划线分?|

### 3.4 评审报告

| 正确命名 | 错误命名 | 说明 |
|---------|---------|------|
| `REVIEW_REPORT_DATACLEANER_TECHNICAL.md` | `datacleaner_review.md` | 包含评审类型 |
| `REVIEW_REPORT_LAYER1_L2_FEASIBILITY.md` | `L1_L2_Feasibility_Review.md` | 使用标准格式 |
| `REVIEW_REPORT_STRATEGY_ENGINE_FINAL.md` | `strategy-engine-final-review.md` | 避免连字?|

---

## 4. 禁止使用的命名方?
### 4.1 禁止使用中文文件??**错误**: `数据清洗蓝图.md`
?**正确**: `BLUEPRINT_DATA_CLEANING.md`

### 4.2 禁止使用空格
?**错误**: `Data Cleaning Blueprint.md`
?**正确**: `BLUEPRINT_DATA_CLEANING.md`

### 4.3 禁止使用特殊字符
?**错误**: `data-cleaning@blueprint.md`
?**正确**: `BLUEPRINT_DATA_CLEANING.md`

### 4.4 禁止使用过长的文件名
?**错误**: `BLUEPRINT_DATA_PREPROCESSING_LAYER_AUTOMATED_DATA_REPAIR_ENGINE_WITH_AI_ENHANCEMENT.md`
?**正确**: `BLUEPRINT_AUTO_REPAIR_ENGINE.md`

### 4.5 禁止使用模糊命名
?**错误**: `document1.md`, `new_file.md`, `temp.md`
?**正确**: `BLUEPRINT_DATA_LINEAGE_TRACKING.md`

---

## 5. 文件名转换规?
### 5.1 从旧命名转换为新命名

| 旧命?| 新命?| 转换规则 |
|--------|--------|---------|
| `data_cleaning.md` | `IMPLEMENTATION_GUIDE_DATA_CLEANING.md` | 添加文档类型前缀，转换为大写 |
| `DataCleaner_Technical_Specification.md` | `TECHNICAL_SPEC_DATACLEANER.md` | 统一格式，使用下划线分隔 |
| `layer1-audit-report-2026-04-03.md` | `AUDIT_REPORT_LAYER1_GOVERNANCE_20260403.md` | 标准化格式和日期 |
| `BLUEPRINT_DATA_LINEAGE_TRACKING_BLUEPRINT.md` | `BLUEPRINT_DATA_LINEAGE_TRACKING.md` | 去除重复的类型标?|

### 5.2 批量重命名脚?
```python
import os
import re
from pathlib import Path

def standardize_filename(filename):
    """
    标准化文件名
    
    规则:
    1. 转换为大?    2. 将空格和连字符替换为下划?    3. 去除重复的类型标?    4. 确保符合命名规范
    """
    # 转换为大?    name = filename.upper()
    
    # 替换空格和连字符为下划线
    name = re.sub(r'[\s\-]+', '_', name)
    
    # 去除重复的类型标?    name = re.sub(r'(BLUEPRINT|TECHNICAL_SPEC|AUDIT_REPORT|REVIEW_REPORT)_\1', r'\1', name)
    
    # 确保?md结尾
    if not name.endswith('.MD'):
        name = name.replace('.MD', '.md')
    
    return name

def batch_rename_documents(directory):
    """
    批量重命名文?    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                old_path = os.path.join(root, file)
                new_name = standardize_filename(file)
                new_path = os.path.join(root, new_name)
                
                if old_path != new_path:
                    print(f"重命? {file} -> {new_name}")
                    # os.rename(old_path, new_path)  # 取消注释以执行重命名
```

---

## 6. 检查与执行

### 6.1 命名规范检查清?
- [ ] 文件名是否使用大写字母和下划?- [ ] 文件名是否包含文档类型标?- [ ] 文件名是否清晰表达文档内?- [ ] 文件名长度是否在50字符以内
- [ ] 文件名是否避免使用特殊字?- [ ] 文件名是否避免使用中?- [ ] 文件名是否符合标准格?
### 6.2 执行步骤

1. **审计阶段**: 检查所有文档是否符合命名规?2. **规划阶段**: 制定重命名计划，记录新旧文件名映?3. **执行阶段**: 批量重命名文?4. **更新阶段**: 更新所有相关链接和索引
5. **验证阶段**: 验证重命名后的文档可正常访问

---

## 7. 例外情况

### 7.1 历史文档
- 已归档的历史文档可保持原有命?- 新建归档文档应添?`_ARCHIVED` 后缀

### 7.2 第三方文?- 第三方文档可保持原有命名
- 应在README中说明命名来?
### 7.3 配置文件
- 配置文件（如.yaml, .json）可使用小写字母
- 应遵循相应的配置文件命名规范

---

## 8. 版本管理

### 8.1 标准版本历史

| 版本 | 日期 | 变更内容 | 作?|
|------|------|----------|------|
| v1.0.0 | 2026-04-03 | 初始版本，制定统一命名规范 | 首席文档架构?|

### 8.2 标准维护
- 本标准由首席文档架构师负责维?- 每季度进行一次标准审查和更新
- 如有疑问或建议，请联系文档治理团?
---

**标准制定?*: 首席文档架构? 
**标准生效日期**: 2026-04-03  
**下次审查日期**: 2026-07-03
