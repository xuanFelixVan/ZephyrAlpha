---
module_id: NEW_DIRECTORY_CREATION_WORKFLOW
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 文档治理系统
responsibility:
  - 新目录创建标准操作程序
layer: layer_09
---

# 新目录创建工作流程 (SOP)

**文档编号**: NEW_DIR_WORKFLOW_001  
**版本**: 1.0.0  
**责任层级**: Layer 09 - 审计与质量  
**适用对象**: 所有需要创建新文档目录的人员/AI Agent

```---

## 一、概述

本文档定义在 `docs/` 目录下创建新文件夹的标准操作程序(SOP)，确保目录结构符合文档治理标准，避免目录映射缺失、Layer归属错误等问题。

```---

## 二、创建前检查清单

### 2.1 必要性评估

- [ ] **确认目录是否必要**：是否有现有目录可以容纳该内容？
- [ ] **确认Layer归属**：根据内容性质确定正确的Layer (0-11)
- [ ] **查阅文档地图**：参考 `document-repository-layout-standard.md` 确认位置

### 2.2 命名规范检查

目录命名必须符合以下规范：

| 类型 | 格式示例 | 正则表达式 |
|------|----------|------------|
| 主目录 | `01_FRAMEWORK`, `02_FACTOR_LIBRARY` | `^\\d{2}_[A-Z_]+$` |
| 归档目录 | `06_ARCHIVE`, `09_ARCHIVE` | `^\\d{2}_ARCHIVE$` |
| 知识目录 | `08_KNOWLEDGE_BASE` | `^\\d{2}_[A-Z_]+$` |
| 子目录 | `01_asset_allocation`, `CONFIG_MANAGEMENT` | `^[a-z0-9_]+\|[A-Z_]+$` |

**禁止使用的命名**：
- `temp`, `tmp`, `backup`, `old`, `test`
- 中文命名
- 空格或特殊字符

```---

## 三、标准创建流程

### 步骤 1: 确定完整路径

```
docs/
├── 01_FRAMEWORK/                    # Layer 1 - 框架
├── 02_FACTOR_LIBRARY/               # Layer 2 - 因子库
│   └── <新子目录>/                  # ← 在此创建
├── 03_TRADING_TACTICS/              # Layer 3 - 交易战术
├── ...
```

### 步骤 2: 创建目录

```bash
# 示例：在 02_FACTOR_LIBRARY 下创建新子目录
mkdir -p docs/02_FACTOR_LIBRARY/NEW_MODULE_NAME
```

### 步骤 3: 创建标准 INDEX.md

每个新目录**必须**包含 `INDEX.md` 文件：

```markdown
```---
layer: layer_02
version: 1.0.0
status: Active
responsibility:
  - NEW_MODULE_NAME目录索引管理
```---

# NEW_MODULE_NAME 目录索引

## 目录说明

本目录包含...（简要说明目录内容）

## 文件清单

| 文件名 | 说明 | 状态 |
|--------|------|------|
| INDEX.md | 本索引文件 | Active |

## 子目录

（如有子目录，在此列出）

## 相关链接

- [返回上级目录](../INDEX.md)
- [Layer 2 因子库索引](../../INDEX.md)
```

### 步骤 4: 更新 SITEMAP.md

在 `docs/SITEMAP.md` 中添加新目录映射：

```markdown
### Layer 2: 因子库 (02_FACTOR_LIBRARY)

| 目录 | 说明 | 文档数 |
|------|------|--------|
| ... | ... | ... |
| NEW_MODULE_NAME | 新模块说明 | 1 |
```

### 步骤 5: 验证合规性

运行验证脚本：

```bash
# 验证目录深度
python scripts/validate_new_directory.py docs/02_FACTOR_LIBRARY/NEW_MODULE_NAME

# 运行全量检查
python scripts/run_comprehensive_audit.py --check C-06,C-13,C-14
```

```---

## 四、审批流程

### 4.1 审批层级

| 目录类型 | 审批要求 | 审批人 |
|----------|----------|--------|
| Layer级主目录 (01-11) | 需要书面决策记录 | Layer 11 战略决策 |
| 子目录 | 自动审批 | 系统自动 |
| ARCHIVE目录 | 需要审计审批 | Layer 09 审计 |

### 4.2 新Layer目录创建要求

如需创建新的Layer级目录（如 `12_NEW_LAYER`）：

1. 编写决策记录 (ADR)
2. 更新 `ARCHITECTURE.md` 定义新Layer职责
3. 更新 `document-repository-layout-standard.md`
4. 获得Layer 11书面批准

```---

## 五、自动化脚本

### 5.1 快速创建脚本

```bash
# 使用脚本自动创建合规目录
python scripts/create_new_directory.py
```

脚本将：
1. 交互式询问目录位置和名称
2. 自动验证命名规范
3. 自动生成标准 INDEX.md
4. 自动更新 SITEMAP.md
5. 执行合规性验证

### 5.2 验证脚本

```bash
# 验证单个目录
python scripts/validate_directory.py docs/XX_DIRECTORY_NAME

# 输出示例：
# ✅ 命名规范：通过
# ✅ 目录深度：3层（≤6层）
# ✅ INDEX.md：存在
# ✅ Layer映射：一致
# ⚠️  SITEMAP同步：缺失（请更新SITEMAP.md）
```

```---

## 六、常见问题

### Q1: 不确定应该放在哪个Layer？

参考 [`docs/01_FRAMEWORK/ARCHITECTURE.md`](../../01_FRAMEWORK/ARCHITECTURE.md) 中的Layer定义表：

- Layer 01: 框架与架构
- Layer 02: 因子库
- Layer 03: 交易战术
- Layer 04: 执行层
- Layer 05: 实施层
- Layer 06: 归档区
- Layer 07: 研究创新
- Layer 08: 人机接口
- Layer 09: 审计与质量
- Layer 10: 治理合规
- Layer 11: 战略决策

### Q2: 子目录可以嵌套多深？

**最大深度：6层**（从 `docs/` 开始计数）

示例合规路径（6层）：
```
docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/01_TIME_SERIES/01_DAILY/01_ADJUSTED/INDEX.md
  1      2               3            4              5           6
```

### Q3: 如何处理跨Layer的内容？

**原则**：按主要职责归属单一Layer

如内容涉及多个Layer：
1. 确定主要职责所在的Layer
2. 在其他Layer创建 **符号链接文档** 或 **引用文档**
3. 禁止在不同Layer创建同名目录

```---

## 七、检查清单摘要

创建新目录后，确认完成以下事项：

- [ ] 目录命名符合规范
- [ ] 目录深度 ≤ 6层
- [ ] 创建了标准 INDEX.md
- [ ] 更新了 SITEMAP.md
- [ ] 通过了合规性验证
- [ ] （如需要）获得了适当层级的审批

```---

## 八、相关文档

| 文档 | 说明 |
|------|------|
| [`document-repository-layout-standard.md`](../STANDARDS/document-repository-layout-standard.md) | 仓库布局标准 |
| [`ARCHITECTURE.md`](../../01_FRAMEWORK/ARCHITECTURE.md) | Layer架构定义 |
| [`document-defect-prevention-standard.md`](../STANDARDS/document-defect-prevention-standard.md) | 缺陷预防标准 (D-06) |

```---

**最后更新**: 2026-04-13  
**维护责任人**: 文档治理委员会
