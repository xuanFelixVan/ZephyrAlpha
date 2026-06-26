---
module_id: KE-1160---------11-006
status: active
title: IRN-011：零残留原则（铁律11）
category: governance
ttl: permanent
---

# IRN-011：零残留原则（铁律11）

IRN-011：零残留原则（铁律11）

> **对标**：Google Dead Code Elimination Policy · vi2 "文件即债务"原则 · Toyota Production System（Muda——消除浪费） · Extreme Programming YAGNI（You Aren't Gonna Need It）

**定义**：项目的磁盘状态必须始终保持"刚刚施工完成"的整洁度——没有任何文件、代码行、注释是为已完成的 phase 的中间过程服务的。

**核心规则**：

| 规则编号 | 规则 | 检测方式 |
|---------|------|---------|
| ZR-001 | **临时文件即删**：`_temp*`、`_check*`、`_phase_*`、`_test_*` 等前缀的临时文件，phase 完成后立即物理删除——不留"测试时的脚手架" | `detect_temp_files.py` |
| ZR-002 | **被替代即删**：任何文件（文档/代码/配置）的内容被新版本完全替代后，原文件物理删除——不留 superseded 副本 | `detect_ruins_references.py`（路径残留）+ 人工判断 |
| ZR-003 | **孤儿即查**：零入边引用的文件（除锚点/蓝图/Session Log）标记为候选删除——AI 在每 phase 结束时主动报告 | `detect_orphan_py.py` + `detect_orphan_documents.py` |
| ZR-004 | **废墟禁引**：禁止在任何文件中引用已删除/废弃的路径——所有引用必须指向当前存在的文件或 KB namespace | `detect_ruins_references.py` |
| ZR-005 | **残留学债零容忍**：Session Log 中 `decisions` 字段记录的清理决定，必须在下一次 session 开始前核对执行状态——未执行的清理项 = P1 违规 | Session Log 自检 |
| ZR-006 | **文件生命周期闭环**：新建文件 → `status: draft` → `status: active`。废弃路径必须与 GOV-DOC-006 对齐：`deprecated` 仅作为过渡期状态（须填 `superseded_by`、TTL、归档或删除）；**禁止**长期囤积无用的 deprecated 文档——过渡期满后 MUST 删除或归档。**例外**：Session Log / rationale-log（TTL: permanent）不走废弃滞留路径 | `trae_028_doc_structure_naming.yaml` |
| ZR-007 | **新文件准入门禁**：创建任何新文件前，AI 必须先回答三个问题——① 这个文件的内容是否已存在？② 这个文件在下一个 phase 是否仍有价值？③ 这个文件是否可以被已存在的文件通过引用覆盖？ | 行为纪律——每次 Write 前自检 |
| ZR-008 | **Session 终了自净（Boy Scout Rule）**：每次 Session 结束时，AI MUST 至少执行 `detect_temp_files.py` + `detect_orphan_py.py`。发现的临时文件/垃圾文件 → 自动删除；孤儿文件 → 主动报告。对标：vibe coding 社区第一铁律——"Always leave the codebase cleaner than you found it" | Session 结束时强制自检 |
| ZR-009 | **代码级残留自检（AI Artifact Hygiene）**：AI 生成的代码 MUST NOT 含有——① 幻觉 import（import 了不存在的包/模块）；② 空壳 stub 函数（`def foo(): pass` / `raise NotImplementedError`）；③ 被注释掉的死代码块；④ `console.log`/`print()` 调试残留。对标：`vibe-check`（BZPRCHNY）的 20 条 AI 代码气味检测规则 | `detect_residual_files.py`（ORPHAN_SHELL/STALE_IMPORT） + 人工审查 |

**不可删除的例外**：
- 锚点文件（GOV-DOC-007 定义）：`AGENTS.md`、`.trae/rules/project_rules.md`、`docs/01_policies_and_standards/_registry/` 等
- Session Log（TTL: permanent）
- architecture-rationale-log.md（appendix-only 推导链）
- 蓝图文件（`docs/03_modules/**/blueprint.md`）
- KB 中的结构化决策（`namespace=decisions`）

**AI 可直接执行的自检**：
- `detect_residual_files.py` — 检测残留文件
- `detect_temp_files.py` — 检测临时文件
- `detect_ruins_references.py` — 检测废墟路径引用
- `detect_orphan_py.py` — 检测孤立 Python 文件
- `detect_orphan_documents.py` — 检测孤立文档
- `check_dead_links.py` — 检测断链

**违反后果**：临时文件堆积 → 上下文噪音（下一个 AI session 加载时干扰决策质量）→ 架构模型与实际文件状态偏移 → SSoT 污染

**专业对标矩阵**：

| 来源 | 对标内容 |
|------|---------|
| Google SWE | "Dead code is a liability, not an asset"——每个无用文件都会在未来被误读、误改 |
| Toyota Production System | Muda（無駄）——消除不产生价值的浪费。在软件中：每个不承载决策的文件都是 Muda |
| XP / YAGNI | "You Aren't Gonna Need It"——不要为未来的你写代码。已完成的 phase 的脚手架就是不需要的 |
| vi2 Framework | "文件即债务"——每个非代码文件都在为当下的施工便利付出未来的维护成本 |
| ITIL Change Control | 变更后必须验证"所有中间产物已清理"——对标准确映射到 ZR-001/002 |
| ISO 42001 §8 | AI system impact assessment——AI 清理文件前必须评估对系统的影响（对标 §6.8 删除前两步预检） |

**氛围编程社区对标矩阵**：

| 来源 | 对标
