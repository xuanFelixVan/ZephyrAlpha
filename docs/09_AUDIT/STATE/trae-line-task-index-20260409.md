---
module_id: TRAE_LINE_TASK_INDEX_20260409_1041
version: 1.1.0
status: Active
created_date: 2026-04-09
last_updated: '2026-04-09'
owner: 仓库 Owner
standard_type: 逐条任务总索引
applicable_scope: Trae / Cursor 接力；与 TRAE_AUTONOMOUS_WORK_DIRECTIVE 配套
parent_document: ./TRAE_AUTONOMOUS_WORK_DIRECTIVE_20260408.md
related_documents:
- ./TRAE_MASTER_EXECUTION_CHECKLIST_20260409.md
layer: layer_09
responsibility: 处理TRAE_LINE_TASK_INDEX_20260409相关业务
---





# Trae 逐条任务总索引（2026-04-09）



> **首选（单一文档 + 全局编号）**：`TRAE_MASTER_EXECUTION_CHECKLIST_20260409.md` — **T0001～T1062**，已合并 Directive/HANDOFF 框架、孤儿、缺 `module_id`、目录普查、审计批次、整改与门禁等。**续跑时只打开此文件，找最小未勾选编号即可。** 再生成：`python scripts/generate_trae_master_execution_checklist.py`。



> **分卷（无全局编号，便于 diff）**：下表 Part A / Part B 与主清单内容对齐；若与主清单不一致，**以主清单为准**。



| 卷 | 文件 | 内容概要 | 再生成命令 |

|----|------|----------|------------|

| **主清单** | `TRAE_MASTER_EXECUTION_CHECKLIST_20260409.md` | 全量编号任务 **1062** 条 | `python scripts/generate_trae_master_execution_checklist.py` |

| **Part A** | `TRAE_LINE_TASK_BACKLOG_20260409.md` | 532 孤儿 + 401 NO-MID + DEDUP + 元任务 | `python scripts/generate_trae_line_task_backlog.py` |

| **Part B** | `TRAE_LINE_TASK_BACKLOG_PARTB_GOVERNANCE_20260409.md` | 一级目录 DIR + 审计批次 + HANDOFF/整改/门禁 | `python scripts/generate_trae_line_task_backlog_partb.py` |



**建议执行顺序（使用主清单时）**



1. 通读 `TRAE_AUTONOMOUS_WORK_DIRECTIVE_20260408.md` + `HANDOFF_ORPHAN_GOVERNANCE_20260408.md`

2. 主清单 **A 段（T0001～）** 框架与真源阅读项先完成或确认遵守

3. 自 **B 段**起按编号推进；孤儿/NO-MID 按批 L1=0 后 commit

4. 每逻辑批：`sentinel_l1_governance_scan.py` → Invalid links = 0 → `git commit`



**不懂编程时**：只把 **主清单** 路径交给 AI，并要求「从最小未勾选 **Txxxx** 继续」。
