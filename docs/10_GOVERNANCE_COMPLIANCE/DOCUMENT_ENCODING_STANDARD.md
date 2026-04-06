---
module_id: DOCUMENT_ENCODING_STANDARD_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席架构师
responsibility:
  - 机器学习
  - 系统架构
  - 文档治理
layer: Layer 10 (治理与合规层)
standard_type: 专业量化机构级规范
applicable_scope: 全系统文档
compliance_level: 专业标准---


# 文档编码规范
> **核心职责**: 标准规范制定
> **职责边界**: 
> - ✅ 本文档负责：标准规范制定相关内容
> - ❌ 本文档不负责：其他模块内容


> **版本**: v1.0.0
> **创建日期**: 2026-04-07
> **适用范围**: 全系统文档
> **合规级别**: 专业标准

---

## 📋 一、规范概述

### 1.1 目的

本规范旨在统一系统文档的编码格式，确保文档的可读性、可维护性和跨平台兼容性。

### 1.2 适用范围

本规范适用于以下文档类型：
- 所有Markdown文档（*.md）
- 所有配置文件（*.json, *.yaml, *.yml, *.toml）
- 所有Python脚本（*.py）
- 所有文本文件（*.txt）

### 1.3 合规要求

- **强制要求**: 所有新建文档必须符合本规范
- **建议要求**: 现有文档应逐步转换为符合本规范的格式
- **检查机制**: 通过Git Hook和定期检查确保合规性

---

## 📝 二、编码标准

### 2.1 文件编码

#### 2.1.1 强制要求

| 文件类型 | 编码格式 | BOM | 说明 |
|---------|---------|-----|------|
| **Markdown文档** | UTF-8 | ❌ 不允许 | 所有.md文件必须使用UTF-8编码，不允许BOM |
| **JSON文件** | UTF-8 | ❌ 不允许 | 所有.json文件必须使用UTF-8编码 |
| **YAML文件** | UTF-8 | ❌ 不允许 | 所有.yaml和.yml文件必须使用UTF-8编码 |
| **Python脚本** | UTF-8 | ❌ 不允许 | 所有.py文件必须使用UTF-8编码 |
| **文本文件** | UTF-8 | ❌ 不允许 | 所有.txt文件必须使用UTF-8编码 |

#### 2.1.2 禁止使用的编码

以下编码格式禁止使用：
- ❌ GBK
- ❌ GB2312
- ❌ GB18030
- ❌ Big5
- ❌ ISO-8859-1
- ❌ Windows-1252
- ❌ UTF-16
- ❌ UTF-32

### 2.2 换行符

#### 2.2.1 换行符标准

| 操作系统 | 换行符 | Git配置 | 说明 |
|---------|--------|---------|------|
| **Windows** | CRLF (\r\n) | core.autocrlf=true | Git自动转换 |
| **Linux/macOS** | LF (\n) | core.autocrlf=input | Git自动转换 |
| **跨平台** | LF (\n) | core.autocrlf=false | 统一使用LF |

#### 2.2.2 推荐配置

```bash
# 推荐Git配置（跨平台协作）
git config --global core.autocrlf input
git config --global core.safecrlf true
```

### 2.3 文件签名

#### 2.3.1 Markdown文档签名

所有Markdown文档必须包含YAML前置签名，格式如下：

```yaml
---
module_id: MODULE_NAME_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席架构师
layer: Layer X (层级名称)
standard_type: 专业量化机构级文档类型
applicable_scope: 适用范围
compliance_level: 专业标准
---
```

#### 2.3.2 Python脚本签名

所有Python脚本必须包含编码声明和文档字符串：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本名称

描述脚本的功能和用途。

Author: 作者
Date: 2026-04-07
"""
```

---

## 🔍 三、检查机制

### 3.1 Git Hook检查

#### 3.1.1 Pre-commit Hook

在每次Git提交前，自动检查文档编码：

- ✅ 检查文件编码是否为UTF-8
- ✅ 检查文件是否包含BOM
- ✅ 检查换行符是否符合规范
- ✅ 检查文件签名是否完整

#### 3.1.2 检查结果处理

| 检查结果 | 处理方式 | 说明 |
|---------|---------|------|
| **通过** | 允许提交 | 所有检查项均通过 |
| **警告** | 允许提交 | 建议修复，但不强制 |
| **错误** | 禁止提交 | 必须修复后才能提交 |

### 3.2 定期检查

#### 3.2.1 检查频率

- **每周检查**: 每周一自动运行全系统文档编码检查
- **每月检查**: 每月1日生成文档编码合规报告

#### 3.2.2 检查工具

使用以下脚本进行定期检查：

```bash
# 检查所有文档编码
python scripts/check_encoding_issues.py

# 检查所有INDEX.md链接
python scripts/validate_index_links.py

# 生成合规报告
python scripts/generate_compliance_report.py
```

---

## 🛠️ 四、修复工具

### 4.1 编码转换工具

#### 4.1.1 批量转换脚本

使用以下脚本批量转换文档编码：

```bash
# 转换所有非UTF-8文档为UTF-8
python scripts/fix_encoding_issues.py
```

#### 4.1.2 单文件转换

使用VS Code或其他编辑器手动转换：

1. 打开文件
2. 点击右下角编码显示
3. 选择"Reopen with Encoding"
4. 选择正确的编码
5. 再次点击编码显示
6. 选择"Save with Encoding"
7. 选择"UTF-8"

### 4.2 BOM移除工具

#### 4.2.1 批量移除BOM

```bash
# 移除所有文件的BOM
python scripts/remove_bom.py
```

#### 4.2.2 单文件移除BOM

使用VS Code：

1. 打开文件
2. 点击右下角编码显示
3. 选择"Save with Encoding"
4. 选择"UTF-8"（不带BOM）

---

## 📊 五、合规指标

### 5.1 合规率目标

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| **UTF-8编码率** | 100% | UTF-8文件数 ÷ 总文件数 |
| **无BOM率** | 100% | 无BOM文件数 ÷ 总文件数 |
| **签名完整率** | ≥95% | 签名完整文件数 ÷ 总文件数 |
| **总体合规率** | ≥95% | 合规文件数 ÷ 总文件数 |

### 5.2 合规报告

每月生成文档编码合规报告，包括：

- 总体合规率
- 各类文件合规率
- 不合规文件列表
- 修复建议

---

## 📚 六、最佳实践

### 6.1 文档创建

#### 6.1.1 使用模板

创建新文档时，使用标准模板：

```bash
# 创建Markdown文档
python scripts/create_document.py --type blueprint --name MODULE_NAME

# 创建Python脚本
python scripts/create_script.py --name script_name
```

#### 6.1.2 编辑器配置

推荐编辑器配置：

**VS Code settings.json:**
```json
{
    "files.encoding": "utf8",
    "files.autoGuessEncoding": false,
    "files.eol": "\n",
    "files.insertFinalNewline": true,
    "files.trimTrailingWhitespace": true
}
```

### 6.2 文档维护

#### 6.2.1 定期检查

每周运行一次文档编码检查：

```bash
python scripts/check_encoding_issues.py
```

#### 6.2.2 及时修复

发现编码问题后，及时修复：

```bash
python scripts/fix_encoding_issues.py
```

---

## 🔗 七、相关文档

- [文档治理Git Hook](.git/hooks/pre-commit)
- [编码检查脚本](scripts/check_encoding_issues.py)
- [编码修复脚本](scripts/fix_encoding_issues.py)
- [链接验证脚本](scripts/validate_index_links.py)

---

## 📈 八、版本历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 首席架构师 |

---

**规范版本**: v1.0.0 | **创建日期**: 2026-04-07 | **状态**: Active
