---
module_id: MIGRATION_GUIDE_V1
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 目录重组实施指南文档
---

﻿---
module_id: IMPL_ARCHIVE_MIGRATION_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
responsibility:
  - 实施指南、部署文档
  - 交易执行
  - 系统架构
standard_type: 专业量化机构实施标准
applicable_scope: 系统实施与部?
compliance_level: 实施标准
parent_document: ../INDEX.md
implementation_status: 进行?---


# 目录重组实施指南
> **核心职责**: 使用指南和教程
> **职责边界**: 
> - ✅ 本文档负责：使用指南和教程相关内容
> - ❌ 本文档不负责：其他模块内容


> **版本**：v4.0
> **更新日期**?026-03-28
> **状?*：待手动执行

---

## 背景

由于部分目录被其他进程锁定，无法自动重命名。请按照以下步骤手动执行目录重命名?

---

## 需要重命名的目?

| 旧名?| 新名?| 说明 |
|--------|--------|------|
| `main/` | `01_FRAMEWORK/` | 核心框架 |
| `factor-library/` | `02_FACTOR_LIBRARY/` | 因子?|
| `trading-tactics/` | `03_TRADING_TACTICS/` | 交易策略 |
| `technical-specs/` | `04_TECHNICAL_SPECS/` | 技术规?|
| `archive/` | `05_ARCHIVE/` | 历史归档 |

---

## 手动执行步骤

### 步骤1：关闭占用进?

关闭以下可能占用目录的应用程序：
- VS Code / Cursor / 其他IDE
- 文件资源管理?
- Markdown编辑?
- Git客户?

### 步骤2：重命名目录

在文件资源管理器中执行以下操作：

```bash
# 或使用命令行（关闭所有占用后?
cd D:\清风量化交易系统4.0\docs

ren main 01_FRAMEWORK
ren factor-library 02_FACTOR_LIBRARY
ren trading-tactics 03_TRADING_TACTICS
ren technical-specs 04_TECHNICAL_SPECS
ren archive 05_ARCHIVE
```

### 步骤3：验证目录结?

最终目录结构应该是?

```
docs/
├── 00_OVERVIEW/          ?已创?
├── 01_FRAMEWORK/         ?待重命名（原main/?
├── 02_FACTOR_LIBRARY/    ?待重命名（原factor-library/?
├── 03_TRADING_TACTICS/  ?待重命名（原trading-tactics/?
├── 04_TECHNICAL_SPECS/  ?待重命名（原technical-specs/?
├── 05_IMPLEMENTATION/    ?已创?
├── 05_ARCHIVE/           ?待重命名（原archive/?
├── SPEC.md
├── README.md
└── ...
```

---

## 已完成的工作

### 已创建的新文?

| 文件 | 位置 | 说明 |
|------|------|------|
| README.md | `00_OVERVIEW/` | 系统总览入口 |
| DATA_FLOW.md | `00_OVERVIEW/` | 数据流与模块依赖 |
| VERSION_HISTORY.md | `00_OVERVIEW/` | 版本演进历史 |

### 待创建的新目?

| 目录 | 说明 |
|------|------|
| `05_IMPLEMENTATION/` | ?已创建（空目录） |

---

## 执行检查清?

```
?关闭所有可能占用目录的应用程序
?执行 ren 命令重命名目?
?验证新目录名称正?
?验证目录内容完整
?更新相关文档中的引用路径
```

---

## 后续步骤

目录重命名完成后，需要：

1. 更新 `00_OVERVIEW/README.md` 中的引用路径
2. 更新 `SPEC.md` 中的目录结构
3. 更新 `quant_system_v4/docs/` 中的引用

---

*最后更新：2026-03-28*
