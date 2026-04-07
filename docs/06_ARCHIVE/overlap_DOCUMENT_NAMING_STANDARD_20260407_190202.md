---
module_id: 02_FACTOR_LIBRARY_04_DATA_SOURCE_DOCUMENT_NAMING_STANDARD
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - DOCUMENT_NAMING标准规范
---

﻿---
module_id: DATA_NAMING_STANDARD_001
version: 1.0.0
status: Active
created_date: 2026-04-05
last_updated: 2026-04-05
owner: 首席文档架构师
responsibility: 文档命名规范与标准化指南
standard_type: 文档治理标准
applicable_scope: 数据源层文档命名
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 已完成
---
---


# 数据源层文档命名规范

> **核心职责**: 数据源层文档命名规范的定义和实现
> **职责边界**: 
> - ✅ 本文档负责：标准规范制定相关内容
> - ❌ 本文档不负责：其他模块内容


## 文档职责说明

**本文档职责**: 文档命名标准
- 定义文档命名标准的核心功能和设计
- 提供实现方案和技术规格
- 维护相关文档引用

**职责边界**:
- ✅ 本文档负责: 文档命名标准的设计和实现方案
- ❌ 本文档不负责: 其他模块功能（由相关模块文档负责）


> 清风量化系统 v5.4 - 文档命名标准化规范
> **版本**: v1.0.0
> **创建日期**: 2026-04-05
> **适用范围**: docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/

---

## 1. 命名原则

### 1.1 核心原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **职责驱动** | 命名必须反映文档核心职责 | `DATA_ACQUISITION.md` |
| **全大写** | 使用全大写字母 | `QUALITY_MANAGEMENT.md` |
| **下划线分隔** | 使用下划线分隔单词 | `DATA_SOURCE_ADAPTERS.md` |
| **简洁明了** | 避免过长的命名 | `MACRO_DATA.md` |
| **一致性** | 同类文档使用统一命名风格 | `*_CONNECTOR.md` |

### 1.2 命名结构

```
[职责前缀]_[核心功能]_[文档类型].md
```

**示例**:
- `DATA_ACQUISITION.md` - 数据采集文档
- `QUALITY_MANAGEMENT.md` - 质量管理文档
- `BAOSTOCK_CONNECTOR.md` - Baostock连接器文档

---

## 2. 文档类型命名规范

### 2.1 特殊文档

| 文档类型 | 命名 | 说明 |
|----------|------|------|
| **目录索引** | `INDEX.md` | 每个子目录的导航索引 |
| **蓝图文档** | `BLUEPRINT.md` | 架构设计蓝图 |
| **自述文档** | `README.md` | 模块说明文档 |

### 2.2 功能文档

| 文档类型 | 命名模式 | 示例 |
|----------|----------|------|
| **连接器** | `*_CONNECTOR.md` | `IFIND_CONNECTOR.md` |
| **适配器** | `*_ADAPTER.md` | `DATA_SOURCE_ADAPTERS.md` |
| **API文档** | `*_API.md` | `SCHEDULER_API.md` |
| **规则文档** | `*_RULES.md` | `CLEANING_RULES.md` |
| **指标文档** | `*_METRICS.md` | `QUALITY_METRICS.md` |
| **系统文档** | `*_SYSTEM.md` | `DATA_QUALITY_CONTROL_SYSTEM.md` |

### 2.3 数据文档

| 文档类型 | 命名模式 | 示例 |
|----------|----------|------|
| **数据源** | `*_DATA_SOURCE.md` | `NEWS_SENTIMENT_DATA_SOURCE.md` |
| **数据需求** | `DATA_REQUIREMENTS.md` | `DATA_REQUIREMENTS.md` |
| **数据采集** | `DATA_ACQUISITION.md` | `DATA_ACQUISITION.md` |
| **宏观数据** | `MACRO_DATA.md` | `MACRO_DATA.md` |

---

## 3. 目录命名规范

### 3.1 目录命名规则

| 规则 | 说明 | 示例 |
|------|------|------|
| **数字前缀** | 使用数字前缀表示顺序 | `02_SCHEDULER/` |
| **全大写** | 使用全大写字母 | `QUALITY_MANAGEMENT/` |
| **下划线分隔** | 使用下划线分隔单词 | `DATA_PIPELINE/` |
| **语义清晰** | 目录名反映内容 | `03_CLEANING/` |

### 3.2 当前目录结构

```
04_DATA_SOURCE/
├── 02_SCHEDULER/           # 数据调度
├── 03_CLEANING/            # 数据清洗
├── 07_DATA_PIPELINE/       # 数据管道
├── IFIND/                  # iFind数据源
│   └── financial_statements/  # 财务数据
└── QUALITY_MANAGEMENT/     # 质量管理
```

---

## 4. YAML头部规范

### 4.1 必需字段

```yaml
---
module_id: [唯一标识符]
version: [版本号]
status: [文档状态]
created_date: [创建日期]
last_updated: [最后更新日期]
owner: [文档所有者]
standard_type: [文档类型]
applicable_scope: [适用范围]
compliance_level: [合规级别]
parent_document: [父文档路径]
implementation_status: [实施状态]
---
```

### 4.2 可选字段

```yaml
implementation_progress: [实施进度]
architecture_layer: [架构层]
timeframe_support: [时间框架支持]
change_log: [变更记录]
related_documents: [相关文档]
keywords: [关键词]
---
```

### 4.3 字段说明

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `module_id` | string | 唯一标识符 | `DATA_ACQUISITION_001` |
| `version` | string | 版本号 | `1.0.0` |
| `status` | enum | 文档状态 | `Active`/`Draft`/`Archived` |
| `created_date` | date | 创建日期 | `2026-04-05` |
| `last_updated` | date | 最后更新日期 | `2026-04-05` |
| `owner` | string | 文档所有者 | `首席文档架构师` |
| `standard_type` | string | 文档类型 | `数据处理文档` |
| `applicable_scope` | string | 适用范围 | `数据采集系统` |
| `compliance_level` | enum | 合规级别 | `专业标准`/`初始标准` |
| `parent_document` | string | 父文档路径 | `./INDEX.md` |
| `implementation_status` | enum | 实施状态 | `进行中`/`已完成`/`设计阶段` |

---

## 5. 变更记录规范

### 5.1 变更记录章节

每个文档应包含变更记录章节：

```markdown
## 📝 变更历史

| 版本 | 日期 | 变更内容 | 变更者 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-05 | 初始版本 | 首席文档架构师 |
| v1.0.1 | 2026-04-06 | 修复职责重叠 | Audit Sentinel |
```

### 5.2 版本号规则

使用语义化版本号：`MAJOR.MINOR.PATCH`

- **MAJOR**: 重大变更（架构调整）
- **MINOR**: 功能变更（新增内容）
- **PATCH**: 问题修复（修正错误）

---

## 6. 命名检查清单

### 6.1 文件命名检查

- [ ] 使用全大写字母
- [ ] 使用下划线分隔单词
- [ ] 命名反映文档职责
- [ ] 避免过长的命名（<50字符）
- [ ] 使用标准文档类型后缀

### 6.2 目录命名检查

- [ ] 使用数字前缀表示顺序
- [ ] 使用全大写字母
- [ ] 使用下划线分隔单词
- [ ] 目录名语义清晰
- [ ] 包含INDEX.md索引文件

### 6.3 YAML头部检查

- [ ] 包含所有必需字段
- [ ] 字段值格式正确
- [ ] module_id唯一
- [ ] 版本号符合规范
- [ ] 日期格式正确

---

## 7. 命名示例

### 7.1 优秀命名示例

| 文件名 | 职责 | 评价 |
|--------|------|------|
| `DATA_ACQUISITION.md` | 数据采集 | ✅ 简洁明了 |
| `QUALITY_MANAGEMENT.md` | 质量管理 | ✅ 职责清晰 |
| `BAOSTOCK_CONNECTOR.md` | Baostock连接器 | ✅ 符合规范 |
| `SCHEDULER_API.md` | 调度器API | ✅ 类型明确 |

### 7.2 需要优化的命名

| 当前命名 | 问题 | 建议命名 |
|----------|------|----------|
| `A_SHARE_HISTORICAL_DATA_PROCESSING_BLUEPRINT.md` | 过长 | `HISTORICAL_DATA_BLUEPRINT.md` |
| `THS_BD_COMPLETE_INDICATOR_LIST.md` | 缩写不明确 | `IFIND_INDICATOR_LIST.md` |

---

## 8. 实施指南

### 8.1 新文档创建

1. 确定文档职责和类型
2. 选择合适的命名模式
3. 检查命名是否冲突
4. 创建标准YAML头部
5. 添加变更记录章节

### 8.2 旧文档优化

1. 扫描现有文档命名
2. 识别不符合规范的命名
3. 制定重命名计划
4. 更新所有引用链接
5. 提交Git变更

---

## 9. 维护责任

| 角色 | 职责 |
|------|------|
| **首席文档架构师** | 制定和维护命名规范 |
| **Audit Sentinel** | 定期审计命名合规性 |
| **文档创建者** | 遵循命名规范创建文档 |

---

## 📝 变更历史

| 版本 | 日期 | 变更内容 | 变更者 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-05 | 初始版本，制定命名规范 | 首席文档架构师 |

---

**文档状态**: ✅ 已完成  
**最后更新**: 2026-04-05  
**维护人员**: 首席文档架构师
