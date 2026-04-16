---
module_id: PLAYBOOK_DEAD_LINK_REPAIR
version: 1.0.0
status: Active
created_date: 2026-04-16
last_updated: 2026-04-16
owner: Project Owner
layer: layer_01
document_type: playbook
parent_document: INDEX.md
related_documents:
  - ../../../scripts/audit/sentinel_l1_governance_scan.py
  - ../../09_AUDIT/STATE/SENTINEL_L1_SCAN_LATEST.md
  - ../../../AGENTS.md
---

# 断链修复 Playbook

> **目标**：将项目断链数从当前峰值压回至 ≤ 100 条，并永久维持在此阈值以下
> **检测工具**：`scripts/audit/sentinel_l1_governance_scan.py`
> **状态文件**：`docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_LATEST.md`
> **阈值配置**：`scripts/hooks/pre-commit-governance-check.py` → `BROKEN_LINK_THRESHOLD`

---

## 一、断链分类（必须在修复前分类）

不同类型的断链修复策略完全不同，混在一起操作效率最低。

| 类型 | 描述 | 典型来源 | 修复策略 |
|------|------|---------|---------|
| **A 类** | 文件已删除，引用未清理 | 文件消除流水线删除文件后 INDEX.md 未更新 | 从 INDEX.md 中移除引用条目 |
| **B 类** | 文件已移动/归档，引用未更新 | `git mv` 后未更新旧路径引用 | 将引用更新为新路径 |
| **C 类** | 规划中的占位链接 | MODULE_INVENTORY.md 中指向未创建的 CONSTRUCTION_PLAN 等 | 改写为 `<!-- PLANNED: -->` 注释格式 |
| **D 类** | 索引漂移（目录重组遗留） | 文件夹编号变更、目录合并拆分后遗留旧路径 | 更新引用为新路径，或删除已废弃引用 |

---

## 二、分类方法（运行前置扫描）

```bash
# 生成最新断链报告
python scripts/audit/sentinel_l1_governance_scan.py

# 查看报告
cat docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_LATEST.md
```

对报告中的每条断链，判断其类型：

```bash
# 判断被引用的目标文件是否曾存在（查 git 历史）
git log --all --full-history -- "docs/path/to/missing-file.md"
# → 有历史记录：A 类或 B 类（曾存在后被删/移）
# → 无历史记录：C 类（从未创建，为规划链接）
# → 有历史记录且路径变更：B 类/D 类（路径漂移）
```

---

## 三、修复优先级与 ROI

按单次 session 可消除的断链数量排序：

```
优先级 1（最高 ROI）：A 类 — 批量从 INDEX.md 移除已删文件的条目
  → Wave 1 删除 200 个 openclaw-l2-* 文件后，约 100 条 A 类断链集中在
    docs/01_FRAMEWORK/INDEX.md、docs/02_FACTOR_LIBRARY/INDEX.md 等

优先级 2：B 类 — 归档蓝图的旧路径引用更新
  → 约 15-20 条，集中在 docs/03_BLUEPRINTS/INDEX.md、docs/00_OVERVIEW/INDEX.md

优先级 3：C 类 — 规划链接改写为注释格式
  → 约 100 条，集中在 docs/02_ARCHITECTURE/MODULE_INVENTORY.md 等规划文档

优先级 4（最低 ROI）：D 类 — 索引漂移，需逐条人工判断
```

---

## 四、A 类修复步骤（已删文件的引用清理）

```bash
# 第一步：确认目标文件确实已被删除
git log --all --full-history -- "docs/09_AUDIT/REPORTS/ARCHIVE/openclaw-l2-*.md"

# 第二步：找到所有还在引用这些文件的文档
rg "openclaw-l2-" docs/ --include="*.md" -l

# 第三步：对每个找到的文件，移除或注释掉指向已删文件的链接行
# 示例（在 docs/01_FRAMEWORK/INDEX.md 中）：
# 删除整行：| [OpenClaw L2 报告](../09_AUDIT/REPORTS/ARCHIVE/openclaw-l2-xxx.md) | ... |

# 第四步：验证
python scripts/audit/sentinel_l1_governance_scan.py
# 确认断链数量下降
```

---

## 五、B 类修复步骤（归档/移动文件的路径更新）

```bash
# 第一步：找到所有引用旧路径的文档
rg "05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/smart-order-router" docs/ --include="*.md" -l

# 第二步：确认文件的新路径
ls docs/06_ARCHIVE/bp-archived-*.md | grep smart-order-router

# 第三步：批量替换
# 将旧路径替换为新归档路径，或直接移除（若归档后链接无实际用途）

# 第四步：验证
python scripts/audit/sentinel_l1_governance_scan.py
```

---

## 六、C 类修复步骤（规划链接改写）

```bash
# 找到所有指向尚未创建的 CONSTRUCTION_PLAN 文件的链接
rg "CONSTRUCTION_PLAN_L0[1-9]" docs/ --include="*.md" -l

# 改写格式（在文件中）：
# 改前：[数据处理层施工计划](../04_CONSTRUCTION/PLANS/CONSTRUCTION_PLAN_L01_DATA_PROCESSING.md)
# 改后：<!-- PLANNED: ../04_CONSTRUCTION/PLANS/CONSTRUCTION_PLAN_L01_DATA_PROCESSING.md -->
#       数据处理层施工计划（待创建）
```

---

## 七、流水线会话的断链维护规范

每次文件消除流水线（Pipeline A）的 wave 完成后，必须执行：

```bash
# 1. 运行 Sentinel 扫描
python scripts/audit/sentinel_l1_governance_scan.py

# 2. 对比本次 wave 删除的文件数量与新增断链数量
# 正常比例：删除 N 个文件 → 新增断链 ≤ 2N 条（因为每个文件平均被引用 1-2 次）
# 异常信号：新增断链 >> 2N → 说明有高度被引用的文件被删除，需要额外清理

# 3. 在同一 commit 中包含断链清理（不允许"先删文件、下次再清引用"的跨 commit 操作）
```

---

## 八、阈值恢复路线图

| 里程碑 | 断链目标 | 操作 |
|--------|---------|------|
| 当前状态（2026-04-16） | 435 条 | 临时阈值 500，允许过渡期提交 |
| Wave 1 引用清理完成 | ≤ 300 条 | 清除 openclaw-l2-* 的 A 类引用 |
| 归档蓝图引用更新 | ≤ 250 条 | B 类修复 |
| 规划链接改写 | ≤ 150 条 | C 类改写为注释格式 |
| D 类逐条清理 | ≤ 100 条 | 恢复正常阈值 |
| 阈值恢复 100 | ≤ 100 条 | 修改 `BROKEN_LINK_THRESHOLD = 100` |

恢复正常阈值后，修改 `scripts/hooks/pre-commit-governance-check.py`：
```python
BROKEN_LINK_THRESHOLD = 100  # 恢复正常值，移除临时注释
```

---

## 九、永久预防规则

见 `AGENTS.md` § 十一、链接维护契约，核心要点：

1. **删除文件时**：必须在同一 commit 内清理所有引用，不允许跨 commit
2. **移动文件时**：`git mv` 后立即用 `rg` 找旧路径引用并批量替换
3. **规划链接**：使用 `<!-- PLANNED: path -->` 注释格式，不得用普通 Markdown 链接
4. **流水线操作**：每个 wave 完成后运行 Sentinel 扫描确认断链增量合理
