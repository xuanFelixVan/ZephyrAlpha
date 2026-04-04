# 文档治理长效机制

**文档ID**: DOC_GOVERNANCE_MECHANISM_001
**版本**: v1.0.0
**创建日期**: 2026-04-03
**状�?*: Active
**适用范围**: 全系统文档管�?
---

## 一、文档治理目�?
### 1.1 质量目标

| 指标 | 目标�?| 说明 |
|------|--------|------|
| 文档治理合规�?| �?0/100 | 专业机构标准 |
| 职责清晰�?| 100% | 每个文档职责明确 |
| 索引覆盖�?| 100% | 所有活跃文档被索引 |
| 命名规范�?| 100% | 0个中文文件名 |

### 1.2 效率目标

| 指标 | 目标�?| 说明 |
|------|--------|------|
| 文档检索时�?| �?0�?| 快速定位文�?|
| 新增文档审批时间 | �?工作�?| 快速响�?|
| 问题发现周期 | �?�?| 定期审计 |

---

## 二、文档命名规�?
### 2.1 命名原则

**核心原则**:
1. **职责反映**: 文件名必须反映文档核心职�?2. **英文优先**: 使用英文命名，避免中�?3. **版本标识**: 重要文档需包含版本�?4. **层级清晰**: 使用下划线分隔层�?
### 2.2 命名格式

**蓝图文档**: `{MODULE_NAME}_BLUEPRINT.md`
```
STRATEGY_ENGINE_BLUEPRINT.md
RISK_MONITORING_BLUEPRINT.md
```

**技术规格书**: `{MODULE_NAME}_TECHNICAL_SPECIFICATION.md`
```
SCENARIO_ANALYZER_TECHNICAL_SPECIFICATION.md
STRESS_TEST_REPORTER_TECHNICAL_SPECIFICATION.md
```

**使用指南**: `{MODULE_NAME}_USAGE_GUIDE.md`
```
PORTFOLIO_OPTIMIZER_USAGE_GUIDE.md
```

**API文档**: `{MODULE_NAME}_API_REFERENCE.md`
```
LAYER7_REPORT_API_REFERENCE.md
```

### 2.3 禁止的命�?
�?禁止使用:
- 中文文件�?- 空格字符
- 特殊字符（除下划线、连字符外）
- 过于通用的命名（�?`README.md`、`DOCUMENT.md`�?
---

## 三、文档归档流�?
### 3.1 归档触发条件

**自动归档**:
- 文档超过3个版�?- 文档被新文档替代
- 文档职责已合并到其他文档

**手动归档**:
- 审计发现重复文档
- 职责边界不清�?- 文档长期未更新（>6个月�?
### 3.2 归档操作流程

```
1. 识别需要归档的文档
     �?2. 确认保留的文档版�?     �?3. 移动文档到归档目�?     �?4. 添加归档后缀（_ARCHIVED�?     �?5. 创建归档说明文档
     �?6. 更新索引（移除归档文档）
     �?7. 更新相关文档的引�?```

### 3.3 归档目录结构

```
docs/06_ARCHIVE/
├── duplicate_documents/
�?  └── {日期}_{审计名称}/
�?      ├── {文档名}_ARCHIVED.md
�?      └── ARCHIVE_README.md
├── deprecated/
�?  └── {日期}_{模块名}/
�?      └── ...
└── legacy/
    └── v4_development/
        └── ...
```

---

## 四、定期审计机�?
### 4.1 审计频率

| 审计类型 | 频率 | 范围 | 重点 |
|---------|------|------|------|
| 快速扫�?| 每周 | Layer 7 | 职责重叠、重复文�?|
| 深度审计 | 每月 | 全系�?| 五大原则合规�?|
| 专项审计 | 每季�?| 指定模块 | 文档质量评估 |

### 4.2 审计清单

**每周快速扫�?*:
- [ ] 检查是否有新增重复文档
- [ ] 检查职责边界是否清�?- [ ] 检查索引是否完�?
**每月深度审计**:
- [ ] 检查五大原则合规�?- [ ] 检查命名规范�?- [ ] 检查版本管�?- [ ] 检查文档时效�?
### 4.3 问题跟踪

**问题等级定义**:
- 🔴 P0�? 职责混乱、重复文档、安全风�?- 🟡 P1�? 索引不完整、命名不规范
- 🟢 P2�? 格式问题、次要优�?
**问题处理时限**:
- P0�? 立即处理（≤24小时�?- P1�? 本周处理（≤1周）
- P1�? 本月处理（≤1月）

---

## 五、职责边界定�?
### 5.1 文档层次结构

```
第一�? 索引文档
├── docs/INDEX.md (主索�?
└── docs/{目录}/INDEX.md (子目录索�?

第二�? 蓝图文档 (概述�?
└── docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/
    └── {MODULE}_BLUEPRINT.md

第三�? 技术规格书 (详细�?
└── docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/
    └── {MODULE}_TECHNICAL_SPECIFICATION.md

第四�? 使用指南 (应用�?
└── docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/
    └── {MODULE}_USAGE_GUIDE.md

第五�? API文档 (接口�?
└── docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/
    └── {MODULE}_API_REFERENCE.md
```

### 5.2 各层职责

| 层级 | 文档类型 | 职责 | 内容范围 |
|------|---------|------|---------|
| 第一�?| 索引文档 | 导航入口 | 链接集合、概�?|
| 第二�?| 蓝图文档 | 架构设计 | 模块概述、架构图、实施路�?|
| 第三�?| 技术规格书 | 详细设计 | 接口定义、数据模型、算法实�?|
| 第四�?| 使用指南 | 应用说明 | 使用示例、最佳实�?|
| 第五�?| API文档 | 接口参�?| API端点、参数说�?|

### 5.3 禁止事项

�?**禁止在蓝图文档中**:
- 包含详细代码实现
- 包含完整API定义
- 复制技术规格书内容

�?**禁止在技术规格书�?*:
- 包含使用示例代码（应放在使用指南�?- 重复蓝图文档的概述内�?- 包含与本模块无关的内�?
---

## 六、新增文档流�?
### 6.1 创建前检�?
1. **职责检�?*: 确认文档职责是否已有文档承担
2. **命名检�?*: 确认文档命名符合规范
3. **位置检�?*: 确认文档放在正确目录

### 6.2 创建时要�?
1. **必须包含YAML头部**:
```yaml
---
module_id: {MODULE_ID}
version: 1.0.0
status: Active
created_date: 2026-04-03
owner: 负责�?---
```

2. **必须包含目录**: 便于导航
3. **必须引用相关文档**: 建立文档关系

### 6.3 创建后操�?
1. **更新索引**: 在对应INDEX.md中添加链�?2. **更新System_Manifest.md**: 如需要全局索引
3. **通知相关人员**: 如有影响范围

---

## 七、违规处�?
### 7.1 自动检�?
**工具检�?*:
- 文档重复度检测工�?- 链接检查工�?- YAML验证工具
- 命名规范检查工�?
### 7.2 人工审查

**审查场景**:
- 新增文档审批
- 定期审计
- 代码审查中的文档检�?
### 7.3 违规处罚

**轻微违规** (P2�?:
- 口头警告
- 要求限期整改

**中等违规** (P1�?:
- 书面警告
- 暂停文档创建权限
- 要求提交整改计划

**严重违规** (P0�?:
- 冻结文档权限
- 强制归档或删�?- 纳入绩效考核

---

## 八、工具支�?
### 8.1 已有工具

| 工具名称 | 功能 | 位置 | 状�?|
|---------|------|------|------|
| duplicate_detector.py | 重复文档检�?| scripts/ | �?已完�?|
| link_checker.py | 死链接检�?| scripts/ | �?已完�?|
| document_integrity_checker.py | 文档完整性检�?| scripts/ | �?已完�?|
| documentation_debt_assessor.py | 文档债务评估 | scripts/ | �?已完�?|
| blueprint_validator.py | 蓝图质量验证 | scripts/ | �?已完�?|
| boundary_checker.py | 职责边界检�?| scripts/ | �?已完�?|
| architecture_analyzer.py | 架构分析 | scripts/ | �?已完�?|

### 8.2 工具使用说明

#### 8.2.1 重复文档检测工�?
**使用场景**: 检测文档内容重复、module_id重复、职责重�?
**使用方法**:
```bash
# 检测指定目录的重复文档
python scripts/duplicate_detector.py --dir docs/10_AI_WORKFLOW --threshold 0.7 --output reports/duplicate_check.json

# 检测全系统重复文档
python scripts/duplicate_detector.py --dir docs/ --threshold 0.8 --output reports/full_duplicate_check.json
```

**参数说明**:
- `--dir`: 要检查的目录路径
- `--threshold`: 相似度阈值（0.0-1.0），默认0.7
- `--output`: 输出报告文件路径

#### 8.2.2 链接检查工�?
**使用场景**: 检查内部链接、外部链接、路径层级违�?
**使用方法**:
```bash
# 检查指定目录的链接
python scripts/link_checker.py --dir docs/10_AI_WORKFLOW --max-depth 3 --output reports/link_check.json

# 检查全系统链接
python scripts/link_checker.py --dir docs/ --max-depth 4 --output reports/full_link_check.json
```

**参数说明**:
- `--dir`: 要检查的目录路径
- `--max-depth`: 最大路径层级，默认3
- `--output`: 输出报告文件路径

#### 8.2.3 文档完整性检查工�?
**使用场景**: 检查文档大小异常、YAML头部完整性、文档结构完整�?
**使用方法**:
```bash
# 检查指定目录的文档完整�?python scripts/document_integrity_checker.py --dir docs/10_AI_WORKFLOW --min-size 100 --output reports/integrity_check.json

# 检查全系统文档完整�?python scripts/document_integrity_checker.py --dir docs/ --min-size 50 --output reports/full_integrity_check.json
```

**参数说明**:
- `--dir`: 要检查的目录路径
- `--min-size`: 最小文件大小（字节），默认100
- `--output`: 输出报告文件路径
- `--no-yaml`: 跳过YAML头部检�?- `--no-structure`: 跳过文档结构检�?
### 8.3 定期审计工具集成

**每周快速扫描脚�?*:
```bash
# 每周一执行
python scripts/duplicate_detector.py --dir docs/ --threshold 0.8 --output reports/weekly/duplicate_check.json
python scripts/link_checker.py --dir docs/ --max-depth 3 --output reports/weekly/link_check.json
python scripts/document_integrity_checker.py --dir docs/ --min-size 100 --output reports/weekly/integrity_check.json
```

**每月深度审计脚本**:
```bash
# 每月第一周执�?python scripts/architecture_analyzer.py --verbose --report --output reports/monthly/architecture_analysis.json
python scripts/boundary_checker.py --verbose --report --output reports/monthly/boundary_check.json
python scripts/documentation_debt_assessor.py --verbose --report --category all --output reports/monthly/debt_assessment.json
python scripts/blueprint_validator.py --verbose --report --output reports/monthly/blueprint_validation.json
```

### 8.4 建议新增工具

| 工具名称 | 功能 | 优先�?|
|---------|------|--------|
| naming_validator.py | 命名规范检�?| P1 |
| yaml_validator.py | YAML头部验证 | P1 |
| auto_fixer.py | 自动修复常见问题 | P2 |

---

## 九、版本历�?
| 版本 | 日期 | 作�?| 变更说明 |
|------|------|------|----------|
| v1.0.0 | 2026-04-03 | 蓝图架构�?| 初始版本 |

---

## 十、参考文�?
- [专业文档治理审计指南](./09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md)
- [文档治理审计检查清单](./09_AUDIT/TEMPLATES/DOCUMENT_GOVERNANCE_AUDIT_CHECKLIST.md)
- [审计标准](./09_AUDIT/STANDARDS/AUDIT_STANDARDS.md)
