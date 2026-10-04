---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：scripts._archive（35 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：scripts._archive（35 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=18，wired=1，wired_by_header=16；初判汇总：exempt=35

## 簇级说明（exempt 依据）

本簇=scripts/_archive/ 退役保留区（35 台全部初判 exempt）。结论=归档区：脚本已完成历史使命，保留供追溯、不参与运行时；非隐身——季度退役审计为复查条件，审计判可删时走 Owner 门位批量退役。依据=总包令 st-orphtriage-20261004 §任务2 机械判据（chief 授权框架）+ FMS 命名法归档区语义。

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/_archive/construction/create_db_alignment_tasks.py` | 数据库大更新后全项目对齐任务卡创建脚本 | 2026-08-21（44天） | in=0/out=0·suspect_orphan | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/construction/create_dm_phase9_tasks.py` | 已归档脚本——一次性任务卡生成脚本，已执行完毕，不再适用。 | 2026-08-21（44天） | in=0/out=0·suspect_orphan | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/construction/dm014_orphan_edge_repair.py` | DM-014: 孤儿节点补边 v3 —— 增加 test 文件文件名匹配策略 | 2026-08-21（44天） | in=0/out=0·suspect_orphan | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/governance/compare_ba_copies.py` | 全量比对 governance/behavioral_auditor/ 和 security/access_control/behavioral_auditor/ 下的文件。 | 2026-06-22（104天） | in=0/out=0·suspect_orphan | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/governance/create_depgraph_task_cards.py` | depgraph_issue_registry 任务卡批量建卡脚本（直接DB插入版） | 2026-08-21（44天） | in=0/out=0·suspect_orphan | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/governance/d11_compliance/batch_remove_bom.py` | DM-200817: 批量去除UTF-8 BOM | 2026-06-22（104天） | in=0/out=0·suspect_orphan | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/governance/list_no_consumer_orphans.py` | 从 orphan_analysis.json 中提取 NO_CONSUMER_HAS_VALUE 模块清单。 | 2026-06-22（104天） | in=0/out=0·suspect_orphan | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/governance/merge_domain_nodes.py` | Generic merge script for domain cleanup. Usage: python script.py <DOMAIN_ID> | 2026-08-21（44天） | in=0/out=0·suspect_orphan | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/governance/repair/ensure_dep_cycles_view.py` | 已归档脚本——P2迁移后 depgraph.db 已迁移至 PostgreSQL，此脚本不再适用。 | 2026-08-21（44天） | in=0/out=0·suspect_orphan | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/governance/repair/list_source_md_files.py` | 扫描临时工作区源MD文件清单 | 2026-06-22（104天） | in=0/out=0·suspect_orphan | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/_migration_shared.py` | 搬家脚本共享模块——数据加载、批次筛选、原子写入。 | 2026-09-18（16天） | in=8/out=0·wired | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/_verify_manifest.py` | （无文档头，按文件名语义：_verify_manifest） | 2026-06-22（104天） | in=0/out=0·suspect_orphan | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/_verify_step4.py` | 已归档脚本——P2迁移后 depgraph.db 已迁移至 PostgreSQL，此脚本不再适用。 | 2026-08-21（44天） | in=0/out=0·suspect_orphan | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/apply_rulings.py` | （无文档头，按文件名语义：apply_rulings） | 2026-06-29（97天） | in=0/out=0·suspect_orphan | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/check_coverage.py` | （无文档头，按文件名语义：check_coverage） | 2026-06-22（104天） | in=0/out=0·suspect_orphan | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/comprehensive_import_fix.py` | 从 path-migration-mapping.yaml 构建全面的 old→new 模块路径映射，修复所有 .py 文件的 import。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/create_target_dirs.py` | 创建30域目标目录结构。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/domain_prefix_import_fix.py` | 从域目录结构推导 old→new 模块路径映射，修复 import 的域前缀。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/execute_move.py` | 批量文件复制——搬家核心引擎（文件级，复制模式）。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/generate_migration_registry.py` | （无文档头，按文件名语义：generate_migration_registry） | 2026-06-29（97天） | in=0/out=0·suspect_orphan | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/generate_path_migration_mapping.py` | 从 depgraph v3 domain draft 的 physical_files 生成文件级 path-migration-mapping.yaml。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/inject_domain_fields.py` | 正确命名约定见 docs/01_policies_and_standards/_registry/vocabularies/target_layer_vocabulary.yaml v1.0.0 | 2026-07-22（74天） | in=0/out=0·suspect_orphan | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/lock_batch.py` | 锁定搬家批次——验证通过后禁止回滚。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/migrate_security_split.py` | DM-315: 拆分security/目录到多设计域路径 | 2026-06-22（104天） | in=0/out=0·suspect_orphan | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/preflight_check.py` | 搬家预检查——验证搬家可行性。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/rollback_batch.py` | 回滚搬家批次——从 migration-log 反向搬回。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/safe_delete_operational.py` | 安全删除旧运营态脚本：验证通过后才删除旧文件，设计态顶替旧运营态成为新运营态。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/scan_import_impact.py` | （无文档头，按文件名语义：scan_import_impact） | 2026-06-22（104天） | in=0/out=0·suspect_orphan | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/shared_import_fix.py` | 修复 zephyr.shared.* import 引用。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/test_import_fix.py` | 修复 tests/ 目录中的 import 引用。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/unnest_from_mcp_server.py` | Phase 1: 将 src/zephyr/integration/mcp_server/ 下的文件解嵌套回 src/zephyr/。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/update_imports.py` | 批量更新 import 引用。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/update_non_import_refs.py` | 更新非 import 引用——蓝图头部/注册表/YAML/__init__.py。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/verify_batch.py` | 验证搬家批次——5项检查。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
| `scripts/_archive/migration/verify_migration_alignment.py` | 迁移对齐验证脚本：验证旧位置内容在新位置完整存在。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **exempt**（归档区（scripts/_archive/ 退役保留区，总包令 §任务2 机械判据授权）；复查：复查=季度退役审计） |
