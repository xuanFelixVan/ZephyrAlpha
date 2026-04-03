---
standard_type: 管理标准
applicable_scope: 系统实施
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
owner: 实施负责人
version: 1.0.0
module_id: IMP_DOCUMENT_QUALITY_GAT
created_date: 2026-04-02
last_updated: 2026-04-02
---
# 文档质量门禁标准

**版本**: v1.0.0
**生效日期**: 2026-04-02
**适用范围**: 所有新增和修改的文档

---

## 1. 质量门禁概述

### 1.1 目标

确保所有新增和修改的文档符合专业量化机构标准，提高文档质量和可维护性。

### 1.2 适用场景

- 新增文档创建
- 现有文档修改
- 文档版本更新
- 文档归档操作

### 1.3 门禁级别

| 级别 | 说明 | 强制性 | 示例 |
|------|------|--------|------|
| **P0 - 阻断** | 必须通过，否则不允许提交 | 强制 | 元数据缺失、版本号错误 |
| **P1 - 警告** | 建议修复，允许临时绕过 | 建议 | 推荐字段缺失、链接警告 |
| **P2 - 提示** | 优化建议，不影响提交 | 可选 | 文档结构优化、格式改进 |

---

## 2. 质量检查项

### 2.1 P0 - 阻断级检查

#### 2.1.1 元数据完整性

**检查项**: 必需元数据字段是否存在

**必需字段**:
```yaml
---
module_id: [模块ID]
version: [版本号]
status: [状态]
created_date: [创建日期]
last_updated: [更新日期]
owner: [负责人]
---
```

**通过条件**: 所有必需字段都存在且格式正确

**失败处理**: 阻止提交，提示缺失字段

#### 2.1.2 版本号格式

**检查项**: 版本号是否符合语义化版本规范

**格式要求**: `X.Y.Z` 或 `vX.Y.Z`
- X: 主版本号 (非负整数)
- Y: 次版本号 (非负整数)
- Z: 修订号 (非负整数)

**示例**:
- ✅ 正确: `1.0.0`, `v5.1.0`, `2.3.4`
- ❌ 错误: `1.0`, `v1`, `1.0.0.0`

**通过条件**: 版本号格式正确

**失败处理**: 阻止提交，提示版本号格式错误

#### 2.1.3 文档ID唯一性

**检查项**: `module_id` 是否唯一

**通过条件**: `module_id` 在系统中唯一

**失败处理**: 阻止提交，提示ID冲突

### 2.2 P1 - 警告级检查

#### 2.2.1 推荐元数据字段

**检查项**: 推荐元数据字段是否存在

**推荐字段**:
```yaml
standard_type: [标准类型]
applicable_scope: [适用范围]
compliance_level: [合规级别]
parent_document: [父文档]
implementation_status: [实现状态]
```

**通过条件**: 至少包含3个推荐字段

**失败处理**: 警告提示，允许提交

#### 2.2.2 内部链接有效性

**检查项**: 文档内部链接是否有效

**通过条件**: 所有内部链接指向存在的文件

**失败处理**: 警告提示，建议修复

#### 2.2.3 文档分类规范性

**检查项**: 文档是否在标准分类目录下

**标准分类**:
- `01_FRAMEWORK`
- `02_FACTOR_LIBRARY`
- `03_TRADING_TACTICS`
- `04_EXECUTION`
- `05_IMPLEMENTATION`
- `06_ARCHIVE`
- `07_RESEARCH`
- `08_AI_GOVERNANCE`
- `09_AUDIT`

**通过条件**: 文档在标准分类目录下

**失败处理**: 提示建议，允许提交

### 2.3 P2 - 提示级检查

#### 2.3.1 文档结构完整性

**检查项**: 文档是否包含标准章节

**推荐章节**:
- 概述/简介
- 设计原则
- 实施方案
- 使用示例
- 参考资料

**通过条件**: 文档结构清晰，包含必要章节

**失败处理**: 优化建议，不影响提交

#### 2.3.2 代码示例有效性

**检查项**: 代码示例是否可执行

**通过条件**: 代码示例语法正确

**失败处理**: 优化建议，不影响提交

---

## 3. 质量门禁流程

### 3.1 新增文档流程

```
1. 创建文档
   ↓
2. 填写元数据
   ↓
3. 运行质量检查
   ↓
4. P0检查通过?
   ├─ 是 → 继续
   └─ 否 → 修复问题 → 返回步骤2
   ↓
5. P1检查通过?
   ├─ 是 → 继续
   └─ 否 → 警告提示，选择是否继续
   ↓
6. 提交文档
   ↓
7. 记录审计日志
```

### 3.2 修改文档流程

```
1. 修改文档
   ↓
2. 更新元数据 (last_updated, version等)
   ↓
3. 运行质量检查
   ↓
4. P0检查通过?
   ├─ 是 → 继续
   └─ 否 → 修复问题 → 返回步骤2
   ↓
5. 提交修改
   ↓
6. 记录审计日志
```

---

## 4. 自动化检查工具

### 4.1 检查脚本

**脚本位置**: `scripts/document_quality_gate.py`

**使用方式**:
```bash
# 检查单个文件
python scripts/document_quality_gate.py --file docs/example.md

# 检查多个文件
python scripts/document_quality_gate.py --files docs/file1.md docs/file2.md

# 检查所有修改的文件
python scripts/document_quality_gate.py --changed
```

### 4.2 检查报告

**报告格式**: JSON

**报告内容**:
```json
{
  "file_path": "docs/example.md",
  "check_time": "2026-04-02T03:15:00",
  "passed": true,
  "p0_checks": {
    "metadata_complete": true,
    "version_format": true,
    "module_id_unique": true
  },
  "p1_checks": {
    "recommended_metadata": false,
    "internal_links": true,
    "classification": true
  },
  "p2_checks": {
    "document_structure": true,
    "code_examples": true
  },
  "issues": [
    {
      "level": "P1",
      "type": "missing_recommended_metadata",
      "message": "缺少推荐字段: parent_document, implementation_status",
      "suggestion": "建议添加这些字段以提高文档质量"
    }
  ]
}
```

---

## 5. 例外处理

### 5.1 例外申请

对于特殊情况，可以申请例外：

**申请流程**:
1. 填写例外申请表
2. 说明例外原因
3. 提供替代方案
4. 获得批准后执行

**例外类型**:
- 临时文档: 可豁免部分检查
- 归档文档: 可豁免更新检查
- 外部引用: 可豁免链接检查

### 5.2 例外记录

所有例外必须记录在案：

**记录位置**: `docs/05_IMPLEMENTATION/04_OPERATIONS/quality_gate_exceptions.md`

**记录内容**:
- 例外文件路径
- 例外原因
- 批准人
- 批准时间
- 有效期

---

## 6. 持续改进

### 6.1 定期评估

**评估频率**: 每月一次

**评估内容**:
- 门禁规则有效性
- 误报率分析
- 漏报率分析
- 用户反馈收集

### 6.2 规则优化

**优化流程**:
1. 收集问题和建议
2. 分析根本原因
3. 制定优化方案
4. 测试验证
5. 发布更新

---

## 7. 培训与支持

### 7.1 培训材料

- 文档质量标准培训PPT
- 质量门禁使用指南
- 常见问题FAQ

### 7.2 支持渠道

- 技术支持邮箱
- 在线帮助文档
- 定期答疑会议

---

## 8. 附录

### 附录A: 质量门禁检查清单

- [ ] P0: 元数据完整性
- [ ] P0: 版本号格式
- [ ] P0: 文档ID唯一性
- [ ] P1: 推荐元数据字段
- [ ] P1: 内部链接有效性
- [ ] P1: 文档分类规范性
- [ ] P2: 文档结构完整性
- [ ] P2: 代码示例有效性

### 附录B: 相关文档

- [VERSION_MANAGEMENT_STANDARD.md](./VERSION_MANAGEMENT_STANDARD.md) - 版本管理标准
- [DOCUMENT_NUMBERING_STANDARD.md](./DOCUMENT_NUMBERING_STANDARD.md) - 文档编号标准
- [PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md](../../09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md) - 专业文档治理审计指南

---

**标准版本**: v1.0.0
**生效日期**: 2026-04-02
**维护责任人**: 首席文档架构师
