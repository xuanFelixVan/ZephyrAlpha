---
module_id: BLUEPRINT_CABINET_EXECUTION_PROTOCOL_001
version: 1.0.0
status: Active
created_date: 2026-04-10
last_updated: '2026-04-10'
owner: 文档负责人（可指定）
responsibility:
  - 图纸柜相关执行协议：防遗漏、防幻觉、可交接给任意 AI
standard_type: 执行协议
applicable_scope: 01_BLUEPRINTS 整理、索引更新及同类文档治理任务
layer: layer_05
---


# 图纸柜执行协议（防忘、防幻觉）

---

## 给用户复制用：「一条指令」

**以后新开对话时，把下面整段原样发给 AI（可先改仓库路径若不同）：**

```text
【图纸柜强制协议 — ZephyrAlpha】
1. 先打开并遵守：docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/BLUEPRINT_CABINET_EXECUTION_PROTOCOL.md
2. 摆放规则真源：docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/01_BLUEPRINTS_REPOSITORY_RULES.md  
   施工门禁 / 蓝图卫生总案真源：docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/
3. 任务与勾选：docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md
4. 禁止凭记忆列举「有哪些文件」或宣称「已完成」：必须用工具列出目录 / 搜索后再写结论。
5. 改完 01_BLUEPRINTS 根目录后必须在仓库根执行：python scripts/governance/generate_01_blueprints_index.py
```

**一句话版（极简）：**

```text
按仓库里 docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/BLUEPRINT_CABINET_EXECUTION_PROTOCOL.md 执行；先读规则再动手；用工具查磁盘再下结论，禁止瞎编。
```

---

## 给 AI 的操作纪律（必须遵守）

1. **真源优先**：与图纸柜能放什么冲突时，以 01_BLUEPRINTS_REPOSITORY_RULES.md 为准。  
2. **先查证、后陈述**：描述「某目录下有哪些文件」「是否已干净」前，必须先 `list_dir` / `glob` / `grep` 或终端列目录，再把结果写入回复。  
3. **禁止幻觉**：不得编造不存在的文件名、路径或脚本名；若未执行命令，不得声称已执行。  
4. **索引同步**：增删或移动 `01_BLUEPRINTS` 根目录下的 `*.md` 后，在仓库根执行：  
   `python scripts/governance/generate_01_blueprints_index.py`  
5. **进度外置**：多步任务以 任务清单 勾选为准；会话结束不等于任务完成，以下次打开清单为准。  
6. **过程稿位置**：带批次日期的报告、分析、清单稿放在 `01_BLUEPRINTS/REPORTS/`，不放根目录。

---

## 任务 3 完成后的自检（可复制到终端）

在 PowerShell 中（仓库根目录）：

```powershell
$bp = "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS"
Get-ChildItem $bp -File -Filter *.md | Where-Object { $_.Name -ne 'INDEX.md' -and $_.Name -notlike '*BLUEPRINT.md' } | Select-Object Name
```

**期望**：无输出（表示根目录除 `INDEX.md` 外均为 `*BLUEPRINT.md`）。

---

## 相关文档

| 文档 | 用途 |
|------|------|
| 项目办公室 AI 交接说明 | 更广义的接手顺序 |
| 蓝图终稿定义 | 终稿含义 |
| [REPORTS 说明](10_GOVERNANCE_COMPLIANCE/TRAINING_SYSTEM/README.md) | 过程稿目录说明 |

---

## 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-04-10 | 首版：用户可复制指令 + AI 纪律 + 任务 3 自检命令 |
