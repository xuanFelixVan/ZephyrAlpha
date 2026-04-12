---

module_id: DOCUMENT_METADATA_TEMPLATE

version: 1.0.0

status: Active

created_date: 2026-04-07

last_updated: '2026-04-07'

owner: 首席文档架构师

responsibility:

- 文档模板设计与标准化管理与优化维护

standard_type: 模板

applicable_scope: 全系统文档元数据标准

compliance_level: 专业标准

parent_document: ../INDEX.md

layer: layer_09
---


# 文档元数据模板标准



> **核心职责**: 定义文档元数据的标准化模板

> **职责边界**: 

> - [OK] 本文档负责：元数据标准定义、模板规范、使用指南

> - [NO] 本文档不负责：具体文档创建、元数据验证



---



## 元数据标准



### 必需字段



所有文档必须包含以下元数据字段：



| 字段名 | 类型 | 说明 | 示例 |

|--------|------|------|------|

| **module_id** | string | 模块唯一标识符 | `FACTOR_LIBRARY_INDEX` |

| **version** | string | 文档版本号 | `1.0.0` |

| **status** | enum | 文档状态 | `Active`, `Draft`, `Deprecated`, `Archived` |

| **created_date** | date | 创建日期 | `2026-04-07` |

| **last_updated** | date | 最后更新日期 | `2026-04-07` |

| **owner** | string | 文档负责人 | `首席文档架构师` |



### 推荐字段



以下字段强烈推荐包含：



| 字段名 | 类型 | 说明 | 示例 |

|--------|------|------|------|

| **responsibility** | list | 文档职责列表 | `- 因子库索引` |

| **standard_type** | string | 文档类型 | `索引`, `蓝图`, `标准`, `指南` |

| **applicable_scope** | string | 适用范围 | `因子库全系统` |

| **compliance_level** | enum | 合规级别 | `专业标准`, `企业标准`, `行业标准` |

| **parent_document** | string | 父文档链接 | `../INDEX.md` |



---



## 标准模板



### 基础模板



```yaml

---

module_id: EXAMPLE_PLACEHOLDER_6D26FFF08F

version: 1.0.0

status: Active

created_date: YYYY-MM-DD

last_updated: YYYY-MM-DD

owner: [负责人]

---

```



### 完整模板



```yaml

---

module_id: EXAMPLE_PLACEHOLDER_6D26FFF08F

version: 1.0.0

status: Active

created_date: YYYY-MM-DD

last_updated: YYYY-MM-DD

owner: [负责人]

responsibility:

  - 文档模板设计与标准化管理与优化维护

standard_type: [文档类型]

applicable_scope: [适用范围]

compliance_level: 专业标准

parent_document: [父文档路径]

---

```



---



## 字段规范



### module_id



**命名规则**:

- 使用大写字母和下划线

- 格式: `[目录名]_[文件名]`

- 示例: `FACTOR_LIBRARY_INDEX`, `DATA_SOURCE_BLUEPRINT`



**示例**:

```yaml

module_id: FACTOR_LIBRARY_INDEX

module_id: DATA_SOURCE_BLUEPRINT

module_id: AUDIT_STANDARDS

```



### version



**版本号格式**: `主版本.次版本.修订版本`



**版本规则**:

- 主版本: 重大变更或不兼容更新

- 次版本: 新增功能或重要改进

- 修订版本: 错误修复或小幅改进



**示例**:

```yaml

version: 1.0.0  # 初始版本

version: 1.1.0  # 新增功能

version: 1.1.1  # 错误修复

version: 2.0.0  # 重大变更

```



### status



**状态类型**:



| 状态 | 说明 | 使用场景 |

|------|------|----------|

| **Active** | 活跃状态 | 当前使用的文档 |

| **Draft** | 草稿状态 | 正在编写或审核的文档 |

| **Deprecated** | 废弃状态 | 已废弃但保留的文档 |

| **Archived** | 归档状态 | 历史版本或不再使用的文档 |



**示例**:

```yaml

status: Active      # 当前使用

status: Draft       # 草稿阶段

status: Deprecated  # 已废弃

status: Archived    # 已归档

```



### responsibility



**职责描述规则**:

- 使用简洁明了的描述

- 每个职责独立一行

- 以动词开头（可选）



**示例**:

```yaml

responsibility:

  - 文档模板设计与标准化管理与优化维护

```



### standard_type



**文档类型**:



| 类型 | 说明 | 示例 |

|------|------|------|

| **索引** | 目录索引文件 | INDEX.md |

| **蓝图** | 设计蓝图文档 | *_BLUEPRINT.md |

| **标准** | 标准规范文档 | *_STANDARD.md |

| **指南** | 操作指南文档 | *_GUIDE.md |

| **报告** | 审计或分析报告 | *_REPORT.md |

| **模板** | 文档模板 | *_TEMPLATE.md |



**示例**:

```yaml

standard_type: 索引

standard_type: 蓝图

standard_type: 标准

standard_type: 指南

```



---



## 使用指南



### 新建文档



1. 复制标准模板

2. 填写必需字段

3. 根据需要添加推荐字段

4. 确保元数据格式正确



### 更新文档



1. 更新 `last_updated` 字段

2. 根据变更类型更新 `version`

3. 如有重大变更，更新 `status`



### 归档文档



1. 将 `status` 改为 `Archived`

2. 移动到归档目录

3. 更新相关索引



---



## 检查机制



### 自动检查



使用 `check_metadata_completeness.py` 脚本自动检查：



```bash

python scripts/check_metadata_completeness.py

```



### 检查项目



- [ ] 是否有YAML元数据块

- [ ] 是否包含所有必需字段

- [ ] 字段值是否符合规范

- [ ] 版本号格式是否正确

- [ ] 日期格式是否正确



---



## 最佳实践



### 1. 保持一致性



- 同类文档使用相似的元数据结构

- 版本号遵循语义化版本规范

- 日期格式统一使用 `YYYY-MM-DD`



### 2. 及时更新



- 每次修改文档时更新 `last_updated`

- 重大变更时更新 `version`

- 状态变更时更新 `status`



### 3. 清晰描述



- `responsibility` 使用清晰的职责描述

- `applicable_scope` 明确适用范围

- `owner` 指定明确的负责人



---



## 变更记录



| 版本 | 日期 | 变更内容 | 变更人 |

|------|------|----------|--------|

| v1.0.0 | 2026-04-07 | 初始版本，元数据模板标准 | 首席文档架构师 |

