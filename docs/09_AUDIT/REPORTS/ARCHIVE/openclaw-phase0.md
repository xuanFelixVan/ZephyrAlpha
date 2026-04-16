---
module_id: OPENCLAW_PHASE0
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 首席文档架构师
layer: layer_09
responsibility: REPORTS
---









# OpenClaw 阶段 0 基线报告



> **生成时间**: 2026-04-08T03:35

> **run_id**: OPENCLAW_20260408_033500



## 1. Markdown 总数



| 指标 | 值 |

|------|-----|

| 全仓库 `*.md` 总数 | **2807** |

| 含文件子目录数 | **296** |

| 数据来源 | `generate_md_inventory_by_dir.py` (2026-04-08T03:32) |



## 2. docs/ 一级目录文档量聚合



| 一级目录 | 文件数 | 约字节 | 审计优先级 |

|----------|--------|--------|------------|

| `05_IMPLEMENTATION` | 796 | 12,594,966 | P0 活跃真源 |

| `06_ARCHIVE` | 587 | 8,784,704 | P1 归档治理 |

| `09_AUDIT` | 428 | 5,894,378 | P0 元审计 |

| `01_FRAMEWORK` | 338 | 6,434,560 | P0 架构真源 |

| `02_FACTOR_LIBRARY` | 141 | 305,011 | P1 |

| `08_HUMAN_AI_INTERFACE` | 107 | 350,312 | P1 |

| `10_AI_WORKFLOW` | 69 | 1,477,064 | P1 |

| `09_ARCHIVE` | 57 | 284,494 | P2 |

| `03_TRADING_TACTICS` | 56 | 824,625 | P1 |

| `11_STRATEGIC_DECISION` | 51 | 1,208,112 | P1 |

| `04_EXECUTION` | 30 | 359,836 | P1 |

| `09_RESEARCH_INNOVATION` | 30 | 748,617 | P1 |

| `10_GOVERNANCE_COMPLIANCE` | 21 | 146,446 | P1 |

| `07_RESEARCH` | 18 | 147,007 | P1 |

| `08_KNOWLEDGE` | 13 | 183,441 | P2 |

| `08_KNOWLEDGE_BASE` | 5 | 29,785 | P2 |

| `00_RESOURCES` | 4 | 9,628 | P2 |

| `00_OVERVIEW` | 3 | 16,396 | P2 |

| 其余（06_CONSTRUCTION_DOCS, 07_AI_REPORTING, 根级文件） | ~10 | ~50,000 | P2 |



## 3. audit_scope



- **精读范围**: INDEX.md / README.md / ARCHITECTURE.md / System_Manifest.md / SITEMAP.md（导航三角）

- **扫读+L2 分批**: 其余全部 2807 篇按目录分批执行五问审计

- **L1 机器扫描已完成**: Sentinel L1 扫描结果见 `SENTINEL_L1_SCAN_20260408.json`



## 4. 超大文件 Top 20



| 字节 | 路径 |

|------|------|

| 1,622,704 | `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/AUDIT5_DUPLICATE_SECTION_CLEANUP_REPORT_20260407_175455.md` |

| 609,866 | `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/STRATEGY_EXECUTION_DEEP_CONTENT_AUDIT_REPORT_20260407.md` |

| 455,730 | `docs/09_AUDIT/STATE/ARCHIVE_FILES_REFERENCE_CHECK_REPORT_20260407_184342.md` |

| 342,358 | `docs/09_RESEARCH_INNOVATION/BLUEPRINT.md` |

| 335,176 | `docs/06_ARCHIVE/main/v4_development/qingfeng_v4_draft.md` |

| 246,314 | `docs/09_AUDIT/STATE/MD_FILES_BY_SUBDIRECTORY_20260408.md` |

| 194,118 | `docs/09_AUDIT/REPORTS/ISSUE_HANDOVER_DOCUMENT_20260407.md` |

| 119,218 | `docs/06_ARCHIVE/strategy_pool.md` |

| 115,921 | `docs/06_ARCHIVE/architecture_v4/module_designs/layer_1/L1_VALIDATOR.md` |

| 110,797 | `docs/06_ARCHIVE/architecture_v4/module_designs/layer_9/L9_ANOMALY_DETECTOR.md` |

| 107,012 | `docs/09_AUDIT/REPORTS/DOCUMENT_AUDIT_v5.1.md` |

| 106,968 | `docs/06_ARCHIVE/overlap_DOCUMENT_AUDIT_v5.1_20260407_190203.md` |

| 97,792 | `docs/01_FRAMEWORK/AI_STRATEGY_AUTOMATION_BLUEPRINT.md` |

| 90,363 | `docs/01_FRAMEWORK/DATA_LAYER_IMPLEMENTATION_BLUEPRINT.md` |

| 86,932 | `docs/01_FRAMEWORK/PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md` |

| 86,233 | `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/COMPREHENSIVE_DEEP_AUDIT_20260407_173907.md` |

| 83,908 | `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/DEEP_AUDIT_V6_20260407.md` |

| 82,668 | `docs/09_AUDIT/STATE/MISSING_METADATA_SCAN_REPORT_20260407_170852.md` |

| 79,917 | `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/DEEP_AUDIT_V2_20260407.md` |

| 79,448 | `docs/04_EXECUTION/06_SIMULATION/MULTI_ENGINE_BLUEPRINT.md` |



## 5. Git 只读记录



| 指标 | 值 |

|------|-----|

| 分支 | `backup/layer25-deep-audit-20260407` |

| HEAD | `c62f537c2fe94436d9204c9c76e5a6f08d91135b` |

| 审计快照 tag | `audit-snapshot-20260408` |

| 阶段0完成 tag | `audit-phase0-complete-20260408` |



## 6. Overnight 运行路径



`docs/09_AUDIT/STATE/overnight_runs/20260408_033240`



## 7. L1 机器扫描关键数字



| 指标 | 值 |

|------|-----|

| 内链解析数 | 4,636 |

| 有效链接 | 3,575 |

| 无效链接 | 69 |

| 重复 module_id 组数 | 238 |

| 未检出 module_id 文件数 | 74 |
