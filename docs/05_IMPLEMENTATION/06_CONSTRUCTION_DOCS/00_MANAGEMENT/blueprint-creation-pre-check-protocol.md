---
module_id: BLUEPRINT_CREATION_PRE_CHECK_PROTOCOL
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 项目办公室
layer: layer_05
responsibility: 00_MANAGEMENT
standard_type: 操作规程
applicable_scope: 所有蓝图创建任务
---

# 蓝图创建前核查协议

> **核心原则**: 先查找、后创建 —— 宁可多花 5 分钟搜索，不要花 5 小时修复重复。

## 背景

Layer 11 蓝图终稿任务中，最初标记 11 个蓝图「缺失」，实际全系统搜索后发现 **100% 已存在**，分散在不同子目录中。若直接创建，会导致重复文件、系统臃肿。

## 血的教训 (2026-04-13)

- **5 个 P0 级蓝图**: 2 个已在正确位置，3 个分散在 `01_FRAMEWORK/`、`10_AI_WORKFLOW/`、`05_IMPLEMENTATION/`
- **8 个 P1/P2 级蓝图**: 全部已存在，分散在 `11_STRATEGIC_DECISION/` 的 4 个子目录中
- **后果**: 直接创建 → 重复文件 → 后续需归档/合并 → 增加技术债务

## 创建前必须执行的 5 步核查流程

### 步骤 1: 文件名搜索

在标记任何蓝图「缺失」前，先执行文件名匹配搜索：

```powershell
# 在 docs/ 全目录搜索文件名匹配（替换关键词）
Get-ChildItem -Path 'docs' -Recurse -Filter '*.md' |
  Where-Object { $_.Name -match 'blueprint-name-pattern' } |
  Select-Object FullName, Length | Sort-Object Length -Descending
```

### 步骤 2: 内容关键词搜索

搜索文件内的 module_id、title、核心职责等：

```powershell
# 搜索文件内容中的关键词
Get-ChildItem -Path 'docs' -Recurse -Filter '*.md' |
  Select-String -Pattern 'module_id.*BLUEPRINT_NAME|核心职责.*关键字' |
  Select-Object Filename, Line | Sort-Object Filename
```

### 步骤 3: 必须检查的目录清单

按优先级顺序检查以下位置：

| 优先级 | 检查位置 | 说明 |
|--------|----------|------|
| 🔴 P0 | `docs/11_STRATEGIC_DECISION/` 及其子目录 | 蓝图可能在子目录中而非根目录 |
| 🔴 P0 | `docs/01_FRAMEWORK/` | Layer 1 框架层可能包含战略蓝图 |
| 🔴 P0 | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/` | 施工图纸柜 |
| 🟡 P1 | `docs/10_AI_WORKFLOW/` | AI 工作流层可能有相关实现 |
| 🟡 P1 | `docs/06_ARCHIVE/` | 可能被归档但未删除 |
| 🟡 P1 | `docs/99_ARCHIVE/` | 归档区可能包含历史版本 |
| 🟢 P2 | `.audit_fix_backup/` | 备份目录中可能有原始版本 |
| 🟢 P2 | `.trae/`、`.cursor/` | IDE 配置目录可能包含 |

### 步骤 4: 运行治理脚本

```bash
# 扫描重复文件内容
python scripts/governance/scan_duplicate_file_content.py --ext md

# 扫描同名不同路径的文件
python scripts/governance/scan_basename_collisions.py

# 扫描蓝图重叠候选
python scripts/governance/scan_blueprint_d_overlap_candidates.py

# 目录结构分析
python scripts/analyze_and_fix_folder_structure.py --analyze-only
```

### 步骤 5: Git 历史搜索

```bash
# 搜索 Git 历史中是否曾存在
Git log --all --full-history --oneline -- "*blueprint-name*"
```

## 标记「缺失」的验收标准

只有在**全部**以下条件满足时，才能在清单中标记为「缺失」：

- [ ] 文件名搜索无结果（docs/ 全目录）
- [ ] 关键词搜索无结果（module_id、title、核心职责）
- [ ] 06_ARCHIVE/ 和 99_ARCHIVE/ 检查无结果
- [ ] 子目录（01_asset_allocation/ 等）检查无结果
- [ ] 扫描脚本未发现重复或相似内容
- [ ] Git 历史搜索无结果
- [ ] **Owner 书面确认**（可选但推荐）

## 违规后果

| 违规行为 | 后果 | 修复成本 |
|----------|------|----------|
| 未经搜索直接创建蓝图 | 重复文件 | 需后续归档/合并 |
| 未检查子目录 | 同主题多版本 | 需 canonical 裁决 |
| 未运行扫描脚本 | 未发现重复 | 增加技术债务 |
| 造成系统臃肿 | 目录混乱 | 需大规模清理 |

## 相关文档互指

- [蓝图阶段任务清单（已归档）](./CANON/ARCHIVE/blueprint-phase-closure-task-list.md)
- [项目办公室 AI 交接说明](./project-office-ai-handoff.md)
- [全仓库文件治理任务清单（已归档）](./CANON/ARCHIVE/repo-wide-file-governance-task-list.md)
- [蓝图终稿定义与认可](./blueprint-final-signoff.md)

## 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-04-13 | 初始版本，记录 Layer 11 教训，建立「先查找、后创建」标准流程 |

---

**警告**: 违反本协议直接创建蓝图，将被视为技术债务，需在后续迭代中修复。
