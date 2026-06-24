# 孤儿/僵尸清理统一审查文档

> 生成时间: 2026-06-24 21:27:24
> 用途: 逐条审查，标记批准后才能执行。禁止未审查直接执行。
> 审查状态字段: 待审查 / 已批准 / 已拒绝 / 已执行
> 总项数: 312 孤儿 + 210 僵尸 = 522 项

## 0. 数据校验

- 磁盘.py数(6175) - DB.py数(6073) = 102
- 孤儿数(312) - 僵尸数(210) = 102
- 公式校验: PASS

## 1. 审查进度跟踪

| 类别 | 总数 | 待审查 | 已批准 | 已拒绝 | 已执行 |
|------|:---:|:---:|:---:|:---:|:---:|
| 孤儿文件 | 312 | 0 | 312 | 0 | 0 |
| 僵尸节点 | 210 | 0 | 210 | 0 | 0 |
| **合计** | **522** | **0** | **522** | **0** | **0** |

> 审查方法：逐行检查下表，将「待审查」改为「已批准」或「已拒绝」。全部审查完毕后，对「已批准」项执行操作。

## 2. 推荐操作汇总

### 2.1 孤儿文件推荐操作

| 推荐操作 | 数量 | 置信度 |
|------|:---:|:---:|
| 补注册 | 195 | HIGH |
| 批量注册或删除 | 48 | HIGH |
| 保持现状 | 33 | HIGH |
| 评估包内容后决定 | 18 | HIGH |
| 评估后删除 | 15 | HIGH |
| 人工评估 | 3 | LOW |

### 2.2 僵尸节点推荐操作

| 推荐操作 | 数量 | 置信度 |
|------|:---:|:---:|
| DB DELETE | 117 | HIGH |
| UPDATE路径或DB DELETE | 37 | HIGH |
| 人工确认目标路径 | 32 | MEDIUM |
| 无需操作 | 24 | HIGH |

## 3. 孤儿文件逐条审查表（磁盘有但全景图无）

共 312 项。审查状态列请填写：待审查/已批准/已拒绝/已执行

| # | 路径 | 行数 | 头部 | 调查发现 | 推荐操作 | 置信度 | 审查状态 | 备注 |
|:---:|------|:---:|:---:|------|------|:---:|:---:|------|
| 1 | `scripts/_archive/construction/create_db_alignment_tasks.py` | 570 | 无 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 2 | `scripts/_archive/construction/create_dm_phase9_tasks.py` | 308 | 无 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 3 | `scripts/_archive/construction/dm014_orphan_edge_repair.py` | 205 | 无 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 4 | `scripts/_archive/governance/compare_ba_copies.py` | 155 | 无 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 5 | `scripts/_archive/governance/create_depgraph_task_cards.py` | 458 | 无 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 6 | `scripts/_archive/governance/d11_compliance/batch_remove_bom.py` | 85 | 无 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 7 | `scripts/_archive/governance/d3_metadata/assign_module_id.py` | 171 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 8 | `scripts/_archive/governance/d3_metadata/check_frontmatter_metadata.py` | 81 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 9 | `scripts/_archive/governance/d3_metadata/check_template_compliance.py` | 252 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 10 | `scripts/_archive/governance/d3_metadata/detect_deprecated_overdue.py` | 115 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 11 | `scripts/_archive/governance/d3_metadata/detect_skip_active_status.py` | 140 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 12 | `scripts/_archive/governance/d3_metadata/detect_stale_version.py` | 162 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 13 | `scripts/_archive/governance/d3_metadata/fix_dm411_bare_relative_imports.py` | 155 | 无 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 14 | `scripts/_archive/governance/d3_metadata/fix_dm413_duplicate_test_names.py` | 203 | 无 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 15 | `scripts/_archive/governance/d3_metadata/fix_n06_module_id_prefix.py` | 514 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 16 | `scripts/_archive/governance/d3_metadata/fix_n12_ke_naming.py` | 567 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 17 | `scripts/_archive/governance/d3_metadata/fix_n15_blueprint_path.py` | 448 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 18 | `scripts/_archive/governance/d3_metadata/generate_rule_catalog.py` | 350 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 19 | `scripts/_archive/governance/d3_metadata/scan_deep_content.py` | 134 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 20 | `scripts/_archive/governance/d3_metadata/validate_blueprint_registry.py` | 175 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 21 | `scripts/_archive/governance/d3_metadata/validate_cross_module_dependencies.py` | 73 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 22 | `scripts/_archive/governance/d3_metadata/validate_derived_from.py` | 276 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 23 | `scripts/_archive/governance/d3_metadata/validate_enum_consistency.py` | 476 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 24 | `scripts/_archive/governance/d3_metadata/validate_frontmatter_values.py` | 161 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 25 | `scripts/_archive/governance/d3_metadata/validate_no_duplicate_files.py` | 138 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 26 | `scripts/_archive/governance/d3_metadata/validate_ssot_status.py` | 128 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 27 | `scripts/_archive/governance/d3_metadata/validate_superseded_by.py` | 132 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 28 | `scripts/_archive/governance/dm101_blueprint_domain_mapping.py` | 424 | 无 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 29 | `scripts/_archive/governance/list_no_consumer_orphans.py` | 24 | 无 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 30 | `scripts/_archive/governance/merge_domain_nodes.py` | 183 | 无 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 31 | `scripts/_archive/governance/repair/ensure_dep_cycles_view.py` | 49 | 无 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 32 | `scripts/_archive/governance/repair/list_source_md_files.py` | 34 | 无 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 33 | `scripts/_archive/ops/fill_blueprint_ids.py` | 316 | 有 | 归档文件 | 保持现状 | HIGH | 已批准 | 3a=Y(归档脚本有历史参考价值); 3b=Y(归档文件，有意保留); 3c=Y(归档脚本重建成本高); 无需检查(非临时脚本) |
| 34 | `scripts/_audit_gen2.py` | 305 | 无 | 临时脚本 | 评估后删除 | MEDIUM | 已批准 | 3a=N(临时脚本，无引用，一次性使用); 3b=N(临时脚本，非管线问题); 3c=N(临时脚本，重建成本低); 无引用 |
| 35 | `scripts/_complete_dm201008.py` | 78 | 有 | 临时脚本 | 评估后删除 | HIGH | 已批准 | 3a=N(临时脚本，无引用，一次性使用); 3b=N(临时脚本，非管线问题); 3c=N(临时脚本，重建成本低); 无引用 |
| 36 | `scripts/_query_dm201008.py` | 46 | 有 | 临时脚本 | 评估后删除 | HIGH | 已批准 | 3a=N(临时脚本，无引用，一次性使用); 3b=N(临时脚本，非管线问题); 3c=N(临时脚本，重建成本低); 无引用 |
| 37 | `scripts/_query_rbac_core.py` | 59 | 有 | 临时脚本 | 评估后删除 | HIGH | 已批准 | 3a=N(临时脚本，无引用，一次性使用); 3b=N(临时脚本，非管线问题); 3c=N(临时脚本，重建成本低); 无引用 |
| 38 | `scripts/_update_rbac_depgraph.py` | 83 | 有 | 临时脚本 | 评估后删除 | HIGH | 已批准 | 3a=N(临时脚本，无引用，一次性使用); 3b=N(临时脚本，非管线问题); 3c=N(临时脚本，重建成本低); 无引用 |
| 39 | `scripts/construction/test_deepseek_api.py` | 89 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(有规范头部，具备独立功能); 3b=Y(全景图未注册导致无消费者发现); 3c=Y(有功能代码，重建有成本); 无需检查(非临时脚本) |
| 40 | `scripts/demos/demo_e2e_pipeline.py` | 572 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(有规范头部，具备独立功能); 3b=Y(全景图未注册导致无消费者发现); 3c=Y(有功能代码，重建有成本); 无需检查(非临时脚本) |
| 41 | `scripts/governance/_audit_gate_registry.py` | 80 | 有 | 临时脚本 | 评估后删除 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 有引用(1处): scripts/governance\_audit_gate_registry.py |
| 42 | `scripts/governance/_check_all_status.py` | 55 | 有 | 临时脚本 | 评估后删除 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 有引用(1处): scripts/governance\_check_all_status.py |
| 43 | `scripts/governance/_check_task.py` | 30 | 有 | 临时脚本 | 评估后删除 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 有引用(1处): scripts/governance\_check_task.py |
| 44 | `scripts/governance/_check_vs.py` | 30 | 有 | 临时脚本 | 评估后删除 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 有引用(1处): scripts/governance\_check_vs.py |
| 45 | `scripts/governance/_list_gate_ids.py` | 27 | 有 | 临时脚本 | 评估后删除 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 有引用(1处): scripts/governance\_list_gate_ids.py |
| 46 | `scripts/governance/_verify_gate_loading.py` | 37 | 有 | 临时脚本 | 评估后删除 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 有引用(1处): scripts/governance\_verify_gate_loading.py |
| 47 | `scripts/governance/analyze_orphan_consumers.py` | 249 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 48 | `scripts/governance/check_rule_coverage.py` | 146 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 49 | `scripts/governance/d3_metadata/validate_rule_frontmatter.py` | 245 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 50 | `scripts/governance/d5_architecture/dm200912_query_domains.py` | 105 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 51 | `scripts/governance/d5_architecture/dm200912_rewrite_views.py` | 1083 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 52 | `scripts/governance/d5_architecture/dm200913_rewrite_diagrams.py` | 931 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 53 | `scripts/governance/d5_architecture/dm200916_write_direct.py` | 683 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 54 | `scripts/governance/d5_architecture/generators/domain_name_mapping.py` | 105 | 无 | 无头部文件 | 人工评估 | LOW | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 55 | `scripts/governance/d5_architecture/generators/generate_capability_heatmap.py` | 544 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 56 | `scripts/governance/d5_architecture/generators/generate_capacity_report.py` | 197 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 57 | `scripts/governance/d5_architecture/generators/generate_constraint_violations.py` | 188 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 58 | `scripts/governance/d5_architecture/generators/generate_cross_domain_matrix.py` | 157 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 59 | `scripts/governance/d5_architecture/generators/generate_design_vs_production.py` | 186 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 60 | `scripts/governance/d5_architecture/generators/generate_domain_architecture_diagram.py` | 651 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 61 | `scripts/governance/d5_architecture/generators/generate_domain_dependency_diagram.py` | 260 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 62 | `scripts/governance/d5_architecture/generators/generate_domain_doc.py` | 636 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 63 | `scripts/governance/d5_architecture/generators/generate_domain_index.py` | 162 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 64 | `scripts/governance/d5_architecture/generators/generate_integration_topology.py` | 196 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 65 | `scripts/governance/d5_architecture/generators/generate_navigation_index.py` | 264 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 66 | `scripts/governance/d5_architecture/generators/generate_path_tree.py` | 331 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 67 | `scripts/governance/d5_architecture/generators/generate_runtime_plane_mapping.py` | 266 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 68 | `scripts/governance/d7_code/fix_n06_scope.py` | 148 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 69 | `scripts/governance/d7_code/fix_n12_ke_naming.py` | 284 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 70 | `scripts/governance/d7_code/fix_n13_snake_case.py` | 300 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 71 | `scripts/governance/d7_code/fix_n14_init_all.py` | 210 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 72 | `scripts/governance/d7_code/fix_n15_blueprint_path.py` | 279 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 73 | `scripts/governance/d7_code/fix_naming_manual.py` | 519 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 74 | `scripts/governance/group_orphan_modules.py` | 143 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 75 | `scripts/governance/iterative_cleanup_imports.py` | 185 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 76 | `scripts/governance/perf_depgraph_baseline.py` | 298 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 77 | `scripts/governance/register_orphan_modules.py` | 318 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 78 | `scripts/governance/rename_whitelist_cleanup.py` | 339 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 79 | `scripts/governance/repair/concurrent_write_test.py` | 647 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 80 | `scripts/governance/task_show.py` | 139 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 81 | `scripts/governance/verify_key_imports.py` | 67 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 82 | `scripts/ide_health_service.py` | 288 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(有规范头部，具备独立功能); 3b=Y(全景图未注册导致无消费者发现); 3c=Y(有功能代码，重建有成本); 无需检查(非临时脚本) |
| 83 | `scripts/ops/auto_fix_cron.py` | 215 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(有规范头部，具备独立功能); 3b=Y(全景图未注册导致无消费者发现); 3c=Y(有功能代码，重建有成本); 无需检查(非临时脚本) |
| 84 | `scripts/ops/upgrade_headers_to_14fields.py` | 752 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(有规范头部，具备独立功能); 3b=Y(全景图未注册导致无消费者发现); 3c=Y(有功能代码，重建有成本); 无需检查(非临时脚本) |
| 85 | `scripts/record_session_start_commit.py` | 87 | 有 | 脚本(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(有规范头部，具备独立功能); 3b=Y(全景图未注册导致无消费者发现); 3c=Y(有功能代码，重建有成本); 无需检查(非临时脚本) |
| 86 | `src/zephyr/autonomy_core/context_pipeline_auto.py` | 192 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(有规范头部，具备独立功能); 3b=Y(全景图未注册导致无消费者发现); 3c=Y(有功能代码，重建有成本); 无需检查(非临时脚本) |
| 87 | `src/zephyr/data/__init__.py` | 3 | 无 | 空壳__init__ | 评估包内容后决定 | HIGH | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 88 | `src/zephyr/governance/auto_runner.py` | 309 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 89 | `src/zephyr/governance/behavioral_auditor/__init__.py` | 710 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 90 | `src/zephyr/governance/budget_enforcement.py` | 46 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 91 | `src/zephyr/governance/escalation/__init__.py` | 43 | 无 | 无头部文件 | 人工评估 | MEDIUM | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 92 | `src/zephyr/governance/f5_boot_integration.py` | 325 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 93 | `src/zephyr/governance/f5_event_subscriber.py` | 585 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 94 | `src/zephyr/governance/f5_shutdown_manager.py` | 569 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 95 | `src/zephyr/governance/rule_enforcement/invariants/post_doc_review_check.py` | 574 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 96 | `src/zephyr/governance/rule_enforcement/phase_executor.py` | 306 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 97 | `src/zephyr/governance/semantic_audit/orchestrator.py` | 326 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(治理/安全组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 98 | `src/zephyr/infra_ops/dashboard/__init__.py` | 5 | 无 | 空壳__init__ | 评估包内容后决定 | HIGH | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 99 | `src/zephyr/infra_ops/dashboard/components/__init__.py` | 9 | 无 | 空壳__init__ | 评估包内容后决定 | HIGH | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 100 | `src/zephyr/infrastructure/rollback/rollback_boot_integration.py` | 157 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(有规范头部，具备独立功能); 3b=Y(全景图未注册导致无消费者发现); 3c=Y(有功能代码，重建有成本); 无需检查(非临时脚本) |
| 101 | `src/zephyr/infrastructure/rollback/rollback_scheduler.py` | 341 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(有规范头部，具备独立功能); 3b=Y(全景图未注册导致无消费者发现); 3c=Y(有功能代码，重建有成本); 无需检查(非临时脚本) |
| 102 | `src/zephyr/integration/local_model/deepseek_chat.py` | 348 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(有规范头部，具备独立功能); 3b=Y(全景图未注册导致无消费者发现); 3c=Y(有功能代码，重建有成本); 无需检查(非临时脚本) |
| 103 | `src/zephyr/integration/pipeline_routing.py` | 20 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(有规范头部，具备独立功能); 3b=Y(全景图未注册导致无消费者发现); 3c=Y(有功能代码，重建有成本); 无需检查(非临时脚本) |
| 104 | `src/zephyr/ops/gates/safety_gate_l28_l29.py` | 58 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(安全门禁组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 105 | `src/zephyr/ops/gates/safety_gate_l36_l37.py` | 55 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(安全门禁组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 106 | `src/zephyr/ops/gates/safety_gate_l38_l39.py` | 56 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(安全门禁组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 107 | `src/zephyr/ops/gates/safety_gate_l40_l41.py` | 52 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(安全门禁组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 108 | `src/zephyr/ops/gates/safety_gate_l42_l43.py` | 59 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(安全门禁组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 109 | `src/zephyr/ops/gates/safety_gate_l44_l45.py` | 63 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(安全门禁组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 110 | `src/zephyr/ops/gates/safety_gate_l46_l47.py` | 66 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(安全门禁组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 111 | `src/zephyr/ops/gates/safety_gate_l48_l49.py` | 54 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(安全门禁组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 112 | `src/zephyr/ops/gates/safety_gate_l50_l51.py` | 71 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(安全门禁组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 113 | `src/zephyr/ops/gates/safety_gate_l52_l53.py` | 42 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(安全门禁组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 114 | `src/zephyr/ops/gates/safety_gate_l54_l55.py` | 34 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(安全门禁组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 115 | `src/zephyr/ops/gates/safety_gate_l56_l57.py` | 45 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(安全门禁组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 116 | `src/zephyr/ops/gates/safety_gate_l58_l59.py` | 49 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(安全门禁组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 117 | `src/zephyr/ops/gates/safety_gate_l60_l61.py` | 47 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(安全门禁组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 118 | `src/zephyr/ops/gates/safety_gate_l62_l63.py` | 46 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(安全门禁组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 119 | `src/zephyr/ops/gates/safety_gate_l64_l65.py` | 43 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(安全门禁组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 120 | `src/zephyr/ops/gates/safety_gate_l66_l67.py` | 74 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(安全门禁组件，核心功能); 3b=Y(安全/治理组件，管线未完全接通); 3c=Y(安全/治理组件重建成本极高); 无需检查(非临时脚本) |
| 121 | `src/zephyr/ops/observability/notifier.py` | 24 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(有规范头部，具备独立功能); 3b=Y(全景图未注册导致无消费者发现); 3c=Y(有功能代码，重建有成本); 无需检查(非临时脚本) |
| 122 | `src/zephyr/shared/adaptation/__init__.py` | 6 | 无 | 空壳__init__ | 评估包内容后决定 | HIGH | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 123 | `src/zephyr/shared/compensation/__init__.py` | 5 | 无 | 空壳__init__ | 评估包内容后决定 | HIGH | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 124 | `src/zephyr/shared/dependency/__init__.py` | 5 | 无 | 空壳__init__ | 评估包内容后决定 | HIGH | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 125 | `src/zephyr/shared/draft/__init__.py` | 5 | 无 | 空壳__init__ | 评估包内容后决定 | HIGH | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 126 | `src/zephyr/shared/infra_06/__init__.py` | 9 | 无 | 空壳__init__ | 评估包内容后决定 | HIGH | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 127 | `src/zephyr/shared/knowledge/__init__.py` | 7 | 无 | 空壳__init__ | 评估包内容后决定 | HIGH | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 128 | `src/zephyr/shared/lifecycle/scope_guard.py` | 22 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(有规范头部，具备独立功能); 3b=Y(全景图未注册导致无消费者发现); 3c=Y(有功能代码，重建有成本); 无需检查(非临时脚本) |
| 129 | `src/zephyr/shared/lifecycle/task_lifecycle_manager.py` | 24 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(有规范头部，具备独立功能); 3b=Y(全景图未注册导致无消费者发现); 3c=Y(有功能代码，重建有成本); 无需检查(非临时脚本) |
| 130 | `src/zephyr/shared/maintenance/__init__.py` | 8 | 无 | 空壳__init__ | 评估包内容后决定 | HIGH | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 131 | `src/zephyr/shared/observability_02/__init__.py` | 10 | 无 | 空壳__init__ | 评估包内容后决定 | HIGH | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 132 | `src/zephyr/shared/quality/__init__.py` | 4 | 无 | 空壳__init__ | 评估包内容后决定 | HIGH | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 133 | `src/zephyr/shared/queue/__init__.py` | 4 | 无 | 空壳__init__ | 评估包内容后决定 | HIGH | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 134 | `src/zephyr/shared/queue/task_scheduler.py` | 23 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(有规范头部，具备独立功能); 3b=Y(全景图未注册导致无消费者发现); 3c=Y(有功能代码，重建有成本); 无需检查(非临时脚本) |
| 135 | `src/zephyr/shared/reliability/__init__.py` | 6 | 无 | 空壳__init__ | 评估包内容后决定 | HIGH | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 136 | `src/zephyr/shared/reliability/context_guard.py` | 22 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(有规范头部，具备独立功能); 3b=Y(全景图未注册导致无消费者发现); 3c=Y(有功能代码，重建有成本); 无需检查(非临时脚本) |
| 137 | `src/zephyr/shared/session/__init__.py` | 6 | 无 | 空壳__init__ | 评估包内容后决定 | HIGH | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 138 | `src/zephyr/shared/sla/__init__.py` | 4 | 无 | 空壳__init__ | 评估包内容后决定 | HIGH | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 139 | `src/zephyr/trading/runtime/__init__.py` | 10 | 无 | 空壳__init__ | 评估包内容后决定 | HIGH | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 140 | `src/zephyr/trading/runtime/async_runtime.py` | 241 | 有 | 源码(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(有规范头部，具备独立功能); 3b=Y(全景图未注册导致无消费者发现); 3c=Y(有功能代码，重建有成本); 无需检查(非临时脚本) |
| 141 | `tests/adversarial/test_f3_extreme.py` | 709 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 142 | `tests/adversarial/test_rollback_concurrent_extreme.py` | 185 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 143 | `tests/adversarial/test_rollback_partial_extreme.py` | 187 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 144 | `tests/adversarial/test_rollback_scheduler.py` | 402 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 145 | `tests/agent_rbac/test_rbac_auto_lifecycle.py` | 285 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 146 | `tests/e2e/test_mcp_full_lifecycle_e2e.py` | 504 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 147 | `tests/governance/test_database_service.py` | 325 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 148 | `tests/integration/test_f3_auto_integration.py` | 540 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 149 | `tests/integration/test_mcp_boot_hooks_integration.py` | 474 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 150 | `tests/integration/test_mcp_health_check_cron.py` | 544 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 151 | `tests/integration/test_mcp_health_check_recovery.py` | 578 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 152 | `tests/integration/test_mcp_idle_timeout.py` | 523 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 153 | `tests/integration/test_mcp_signal_shutdown.py` | 810 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 154 | `tests/red_blue/__init__.py` | 0 | 无 | 空壳__init__ | 评估包内容后决定 | HIGH | 已批准 | 3a=Y(包标记__init__，有结构价值); 3b=Y(包标记，Python导入机制需要); 3c=Y(删除__init__会破坏包结构); 无需检查(非临时脚本) |
| 155 | `tests/red_blue/_test_commit_target.py` | 1 | 无 | 临时脚本 | 评估后删除 | HIGH | 已批准 | 3a=N(临时脚本，无引用，一次性使用); 3b=N(临时脚本，非管线问题); 3c=N(临时脚本，重建成本低); 无引用 |
| 156 | `tests/red_blue/_test_lock_target.py` | 1 | 无 | 临时脚本 | 评估后删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 有引用(1处): scripts/governance\test_lock_scenarios.py |
| 157 | `tests/red_blue/_test_mixed_target.py` | 1 | 无 | 临时脚本 | 评估后删除 | HIGH | 已批准 | 3a=N(临时脚本，无引用，一次性使用); 3b=N(临时脚本，非管线问题); 3c=N(临时脚本，重建成本低); 无引用 |
| 158 | `tests/red_blue/_test_staging_target.py` | 1 | 无 | 临时脚本 | 评估后删除 | HIGH | 已批准 | 3a=N(临时脚本，无引用，一次性使用); 3b=N(临时脚本，非管线问题); 3c=N(临时脚本，重建成本低); 无引用 |
| 159 | `tests/red_blue/test_async_monitor.py` | 770 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 160 | `tests/red_blue/test_circuit_breaker.py` | 396 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 161 | `tests/red_blue/test_constitution_engine.py` | 205 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 162 | `tests/red_blue/test_context_pipeline_red_blue.py` | 330 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 163 | `tests/red_blue/test_defense_runner.py` | 915 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 164 | `tests/red_blue/test_event_integration.py` | 325 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 165 | `tests/red_blue/test_f14_pipeline_extreme.py` | 673 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 166 | `tests/red_blue/test_f18_governance_adversarial.py` | 361 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 167 | `tests/red_blue/test_f1_extreme.py` | 511 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 168 | `tests/red_blue/test_game_day_scheduler.py` | 805 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 169 | `tests/red_blue/test_injection_engine.py` | 589 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 170 | `tests/red_blue/test_phase_manager_integration.py` | 585 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 171 | `tests/red_blue/test_red_blue_validator.py` | 178 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 172 | `tests/test_adversarial_extreme.py` | 227 | 无 | 无头部文件 | 人工评估 | LOW | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 173 | `tests/test_arbiter.py` | 209 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 174 | `tests/test_auto_fix_autopilot.py` | 97 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 175 | `tests/test_auto_fix_phase_manager.py` | 127 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 176 | `tests/test_auto_fix_red_blue.py` | 439 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 177 | `tests/test_auto_runtime_e2e.py` | 361 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 178 | `tests/test_auto_runtime_fle_integration.py` | 272 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 179 | `tests/test_budget_event_driven.py` | 222 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 180 | `tests/test_budget_lifecycle_e2e.py` | 191 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 181 | `tests/test_budget_shutdown.py` | 204 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 182 | `tests/test_circadian_red_blue_drill.py` | 455 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 183 | `tests/test_conductor.py` | 285 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 184 | `tests/test_f10_red_blue.py` | 528 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 185 | `tests/test_f18_automation.py` | 331 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 186 | `tests/test_f18_redblue.py` | 819 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 187 | `tests/test_f1_event_trigger.py` | 450 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 188 | `tests/test_f21_auto_run.py` | 171 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 189 | `tests/test_f21_auto_shutdown.py` | 203 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 190 | `tests/test_f21_auto_startup.py` | 133 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 191 | `tests/test_f21_event_driven.py` | 203 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 192 | `tests/test_f5_auto_shutdown.py` | 595 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 193 | `tests/test_f5_auto_startup.py` | 382 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 194 | `tests/test_f5_e2e_lifecycle.py` | 832 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 195 | `tests/test_f5_event_startup.py` | 635 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 196 | `tests/test_f5_red_team_extreme.py` | 453 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 197 | `tests/test_fl_safety_gate_l28_l29.py` | 85 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 198 | `tests/test_fl_safety_gate_l36_l37.py` | 70 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 199 | `tests/test_fl_safety_gate_l38_l39.py` | 77 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 200 | `tests/test_fl_safety_gate_l40_l41.py` | 76 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 201 | `tests/test_fl_safety_gate_l42_l43.py` | 85 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 202 | `tests/test_fl_safety_gate_l44_l45.py` | 84 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 203 | `tests/test_fl_safety_gate_l46_l47.py` | 91 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 204 | `tests/test_fl_safety_gate_l48_l49.py` | 75 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 205 | `tests/test_fl_safety_gate_l50_l51.py` | 82 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 206 | `tests/test_fl_safety_gate_l52_l53.py` | 60 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 207 | `tests/test_fl_safety_gate_l54_l55.py` | 55 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 208 | `tests/test_fl_safety_gate_l56_l57.py` | 66 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 209 | `tests/test_fl_safety_gate_l58_l59.py` | 66 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 210 | `tests/test_fl_safety_gate_l60_l61.py` | 67 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 211 | `tests/test_fl_safety_gate_l62_l63.py` | 67 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 212 | `tests/test_fl_safety_gate_l64_l65.py` | 59 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 213 | `tests/test_fl_safety_gate_l66_l67.py` | 80 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 214 | `tests/test_g_trae_003.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 215 | `tests/test_g_trae_004.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 216 | `tests/test_g_trae_006.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 217 | `tests/test_g_trae_007.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 218 | `tests/test_g_trae_008.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 219 | `tests/test_g_trae_009.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 220 | `tests/test_g_trae_010.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 221 | `tests/test_g_trae_011.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 222 | `tests/test_g_trae_012.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 223 | `tests/test_g_trae_016.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 224 | `tests/test_g_trae_017.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 225 | `tests/test_g_trae_018.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 226 | `tests/test_g_trae_020.py` | 209 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 227 | `tests/test_g_trae_021.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 228 | `tests/test_g_trae_022.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 229 | `tests/test_g_trae_023.py` | 209 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 230 | `tests/test_g_trae_024.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 231 | `tests/test_g_trae_025.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 232 | `tests/test_g_trae_026.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 233 | `tests/test_g_trae_027.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 234 | `tests/test_g_trae_028.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 235 | `tests/test_g_trae_029.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 236 | `tests/test_g_trae_030.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 237 | `tests/test_g_trae_031.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 238 | `tests/test_g_trae_032.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 239 | `tests/test_g_trae_033.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 240 | `tests/test_g_trae_034.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 241 | `tests/test_g_trae_035.py` | 209 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 242 | `tests/test_g_trae_036.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 243 | `tests/test_g_trae_037.py` | 209 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 244 | `tests/test_g_trae_038.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 245 | `tests/test_g_trae_039.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 246 | `tests/test_g_trae_040.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 247 | `tests/test_g_trae_041.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 248 | `tests/test_g_trae_042.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 249 | `tests/test_g_trae_043.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 250 | `tests/test_g_trae_044.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 251 | `tests/test_g_trae_045.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 252 | `tests/test_g_trae_046.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 253 | `tests/test_g_trae_047.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 254 | `tests/test_g_trae_048.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 255 | `tests/test_g_trae_049.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 256 | `tests/test_g_trae_050.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 257 | `tests/test_g_trae_051.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 258 | `tests/test_g_trae_052.py` | 209 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 259 | `tests/test_g_trae_053.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 260 | `tests/test_g_trae_054.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 261 | `tests/test_g_trae_055.py` | 207 | 无 | 批量规则测试 | 批量注册或删除 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 262 | `tests/test_ide_health_daemon.py` | 36 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 263 | `tests/test_l00_data_source.py` | 323 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 264 | `tests/test_l02_alpha_factor.py` | 256 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 265 | `tests/test_l03_signal_generation.py` | 264 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 266 | `tests/test_l04_risk_management.py` | 576 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 267 | `tests/test_l05_portfolio_construction.py` | 216 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 268 | `tests/test_l06_trade_execution.py` | 454 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 269 | `tests/test_l07_post_trade_analytics.py` | 264 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 270 | `tests/test_l08_human_ai_interface.py` | 358 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 271 | `tests/test_l09_research_innovation.py` | 251 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 272 | `tests/test_l10_compliance.py` | 317 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 273 | `tests/test_l11_ml_platform.py` | 209 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 274 | `tests/test_l13_experimentation.py` | 179 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 275 | `tests/test_lock_release_uncommitted.py` | 241 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 276 | `tests/test_mcp_launcher.py` | 106 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 277 | `tests/test_phase_executor_rule_enforcement.py` | 315 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 278 | `tests/test_pipeline_orchestrator_auto.py` | 630 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 279 | `tests/test_post_doc_review.py` | 312 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 280 | `tests/test_red_blue_validator_tests.py` | 214 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 281 | `tests/test_safety_gate_l28_l29.py` | 84 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 282 | `tests/test_safety_gate_l36_l37.py` | 68 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 283 | `tests/test_safety_gate_l38_l39.py` | 73 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 284 | `tests/test_safety_gate_l40_l41.py` | 64 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 285 | `tests/test_safety_gate_l42_l43.py` | 74 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 286 | `tests/test_safety_gate_l44_l45.py` | 73 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 287 | `tests/test_safety_gate_l46_l47.py` | 82 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 288 | `tests/test_safety_gate_l48_l49.py` | 64 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 289 | `tests/test_safety_gate_l50_l51.py` | 82 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 290 | `tests/test_safety_gate_l52_l53.py` | 50 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 291 | `tests/test_safety_gate_l54_l55.py` | 47 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 292 | `tests/test_safety_gate_l56_l57.py` | 60 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 293 | `tests/test_safety_gate_l58_l59.py` | 59 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 294 | `tests/test_safety_gate_l60_l61.py` | 61 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 295 | `tests/test_safety_gate_l62_l63.py` | 59 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 296 | `tests/test_safety_gate_l64_l65.py` | 59 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 297 | `tests/test_safety_gate_l66_l67.py` | 85 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 298 | `tests/test_task_repo_auto_commit.py` | 255 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 299 | `tests/test_trading_session_lifecycle.py` | 408 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 300 | `tests/test_validate_rule_frontmatter_red_blue.py` | 368 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 301 | `tests/trading/runtime/test_async_runtime.py` | 242 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 302 | `tests/unit/feedback_loop/test_scheduler_integration.py` | 232 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 303 | `tests/unit/pipeline/conftest.py` | 31 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 304 | `tests/unit/telemetry/test_l12_telemetry.py` | 195 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 305 | `tests/unit/test_concurrency_guard.py` | 206 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 306 | `tests/unit/test_context_pipeline_auto.py` | 390 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 307 | `tests/unit/test_l08_interface.py` | 193 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 308 | `tests/unit/test_l12_telemetry_unit.py` | 198 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 309 | `tests/unit/vector_memory/test_vms_adversarial_hijack.py` | 451 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 310 | `tests/unit/vector_memory/test_vms_adversarial_injection.py` | 261 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 311 | `tests/unit/vector_memory/test_vms_automation.py` | 433 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |
| 312 | `tests/unit/vector_memory/test_vms_lifecycle.py` | 324 | 有 | 测试(有头部) | 补注册 | HIGH | 已批准 | 3a=Y(测试文件有验证功能价值); 3b=Y(测试文件，pytest自动发现); 3c=Y(测试重建成本高); 无需检查(非临时脚本) |

## 4. 僵尸节点逐条审查表（全景图有但磁盘无）

共 210 项。审查状态列请填写：待审查/已批准/已拒绝/已执行

| # | node_id | 路径 | 域 | 精确状态 | 磁盘实际位置 | 推荐操作 | 置信度 | 审查状态 | 备注 |
|:---:|:---:|------|:---:|------|------|------|:---:|:---:|------|
| 1 | 47973 | `src/zephyr/cross_asset/cross_asset_risk_decomposer/__init__.py` | D-CROSS_ASSET | MOVED | scripts/__init__.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(scripts/__init__.py); git: 1e264a1338 feat: STEP 4b cleanup complete - 55 to  |
| 2 | 47977 | `src/zephyr/cross_asset/cross_market_data_adapter/__init__.py` | D-CROSS_ASSET | MOVED | scripts/__init__.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(scripts/__init__.py); git: 1e264a1338 feat: STEP 4b cleanup complete - 55 to  |
| 3 | 47975 | `src/zephyr/cross_asset/cross_market_data_adapter/ml_experiment_pipeline.py` | D-CROSS_ASSET | MOVED | src/zephyr/risk/cross_asset/cross_market_data_adapter/ml_experiment_pipeline.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(src/zephyr/risk/cross_asset/cross_market_data_adapter/ml_experiment_pipeline.py); git: 1e264a1338 feat: STEP 4b cleanup complete - 55 to  |
| 4 | 47981 | `src/zephyr/cross_asset/currency_hedger_and_fixed_income/__init__.py` | D-CROSS_ASSET | MOVED | scripts/__init__.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(scripts/__init__.py); git: 1e264a1338 feat: STEP 4b cleanup complete - 55 to  |
| 5 | 47971 | `src/zephyr/cross_asset/risk_manager.py` | D-CROSS_ASSET | MOVED | src/zephyr/risk/risk_manager.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(src/zephyr/risk/risk_manager.py); git: 1e264a1338 feat: STEP 4b cleanup complete - 55 to  |
| 6 | 47967 | `src/zephyr/cross_asset/risk_manager_base.py` | D-CROSS_ASSET | MOVED | src/zephyr/risk/risk_manager_base.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(src/zephyr/risk/risk_manager_base.py); git: 1e264a1338 feat: STEP 4b cleanup complete - 55 to  |
| 7 | 48041 | `src/zephyr/ex_core/models/__init__.py` | D-EX_CORE | MOVED | scripts/__init__.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(scripts/__init__.py); git: 无git历史 |
| 8 | 62866 | `D-FACTOR/factor_base.py为唯一SSoT删除base.py` | D-FACTOR | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 9 | 48059 | `src/zephyr/factor/models/__init__.py` | D-FACTOR | MOVED | scripts/__init__.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(scripts/__init__.py); git: 无git历史 |
| 10 | 53886 | `frontend/app.py` | D-FRONTEND | MOVED | src/zephyr/frontend/dashboard/app.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(src/zephyr/frontend/dashboard/app.py); git: 无git历史 |
| 11 | 53884 | `frontend/fitness_functions.py` | D-FRONTEND | MOVED | src/zephyr/frontend/dashboard/components/fitness_functions.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(src/zephyr/frontend/dashboard/components/fitness_functions.py); git: 无git历史 |
| 12 | 53890 | `frontend/gate_statistics.py` | D-FRONTEND | MOVED | src/zephyr/frontend/dashboard/components/gate_statistics.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(src/zephyr/frontend/dashboard/components/gate_statistics.py); git: 无git历史 |
| 13 | 53889 | `frontend/interface_base.py` | D-FRONTEND | MOVED | src/zephyr/frontend/interface_base.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(src/zephyr/frontend/interface_base.py); git: 无git历史 |
| 14 | 53887 | `frontend/knowledge_overview.py` | D-FRONTEND | MOVED | src/zephyr/frontend/dashboard/components/knowledge_overview.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(src/zephyr/frontend/dashboard/components/knowledge_overview.py); git: 无git历史 |
| 15 | 53888 | `frontend/olap_trend.py` | D-FRONTEND | MOVED | src/zephyr/frontend/dashboard/components/olap_trend.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(src/zephyr/frontend/dashboard/components/olap_trend.py); git: 无git历史 |
| 16 | 53892 | `frontend/real_time_dashboard/__init__.py` | D-FRONTEND | MOVED | scripts/__init__.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(scripts/__init__.py); git: 无git历史 |
| 17 | 53891 | `frontend/task_progress.py` | D-FRONTEND | MOVED | src/zephyr/frontend/dashboard/components/task_progress.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(src/zephyr/frontend/dashboard/components/task_progress.py); git: 无git历史 |
| 18 | 53882 | `data/asset_index/archive/migration_scripts/_migration_shared.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/_migration_shared.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 19 | 53881 | `data/asset_index/archive/migration_scripts/_verify_manifest.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/_verify_manifest.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 20 | 53885 | `data/asset_index/archive/migration_scripts/_verify_step4.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/_verify_step4.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 21 | 53861 | `data/asset_index/archive/migration_scripts/apply_rulings.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/apply_rulings.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 22 | 53862 | `data/asset_index/archive/migration_scripts/check_coverage.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/check_coverage.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 23 | 53866 | `data/asset_index/archive/migration_scripts/comprehensive_import_fix.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/comprehensive_import_fix.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 24 | 53865 | `data/asset_index/archive/migration_scripts/create_target_dirs.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/create_target_dirs.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 25 | 53863 | `data/asset_index/archive/migration_scripts/cross_domain_import_fix.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/cross_domain_import_fix.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 26 | 53868 | `data/asset_index/archive/migration_scripts/domain_prefix_import_fix.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/domain_prefix_import_fix.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 27 | 53867 | `data/asset_index/archive/migration_scripts/execute_move.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/execute_move.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 28 | 53870 | `data/asset_index/archive/migration_scripts/generate_migration_registry.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/generate_migration_registry.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 29 | 53869 | `data/asset_index/archive/migration_scripts/generate_path_migration_mapping.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/generate_path_migration_mapping.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 30 | 53873 | `data/asset_index/archive/migration_scripts/inject_domain_fields.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/inject_domain_fields.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 31 | 53874 | `data/asset_index/archive/migration_scripts/lock_batch.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/lock_batch.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 32 | 53871 | `data/asset_index/archive/migration_scripts/preflight_check.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/preflight_check.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 33 | 53872 | `data/asset_index/archive/migration_scripts/rollback_batch.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/rollback_batch.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 34 | 53875 | `data/asset_index/archive/migration_scripts/scan_import_impact.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/scan_import_impact.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 35 | 53878 | `data/asset_index/archive/migration_scripts/shared_import_fix.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/shared_import_fix.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 36 | 53879 | `data/asset_index/archive/migration_scripts/test_import_fix.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/test_import_fix.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 37 | 53876 | `data/asset_index/archive/migration_scripts/unnest_from_mcp_server.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/unnest_from_mcp_server.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 38 | 53877 | `data/asset_index/archive/migration_scripts/update_imports.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/update_imports.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 39 | 53880 | `data/asset_index/archive/migration_scripts/update_non_import_refs.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/update_non_import_refs.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 40 | 53883 | `data/asset_index/archive/migration_scripts/verify_batch.py` | D-GOVERNANCE | FALSE_POSITIVE | data/asset_index/archive/migration_scripts/verify_batch.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 无git历史 |
| 41 | 51274 | `scripts/construction/create_db_alignment_tasks.py` | D-GOVERNANCE | MOVED | scripts/_archive/construction/create_db_alignment_tasks.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/construction/create_db_alignment_tasks.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 42 | 51273 | `scripts/construction/create_dm_phase9_tasks.py` | D-GOVERNANCE | MOVED | scripts/_archive/construction/create_dm_phase9_tasks.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/construction/create_dm_phase9_tasks.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 43 | 51276 | `scripts/construction/dm014_orphan_edge_repair.py` | D-GOVERNANCE | MOVED | scripts/_archive/construction/dm014_orphan_edge_repair.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/construction/dm014_orphan_edge_repair.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 44 | 51308 | `scripts/governance/create_depgraph_task_cards.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/create_depgraph_task_cards.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/create_depgraph_task_cards.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 45 | 51424 | `scripts/governance/d3_metadata/assign_module_id.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/d3_metadata/assign_module_id.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/d3_metadata/assign_module_id.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 46 | 51427 | `scripts/governance/d3_metadata/check_frontmatter_metadata.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/d3_metadata/check_frontmatter_metadata.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/d3_metadata/check_frontmatter_metadata.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 47 | 51428 | `scripts/governance/d3_metadata/check_template_compliance.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/d3_metadata/check_template_compliance.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/d3_metadata/check_template_compliance.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 48 | 51434 | `scripts/governance/d3_metadata/detect_deprecated_overdue.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/d3_metadata/detect_deprecated_overdue.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/d3_metadata/detect_deprecated_overdue.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 49 | 51431 | `scripts/governance/d3_metadata/detect_skip_active_status.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/d3_metadata/detect_skip_active_status.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/d3_metadata/detect_skip_active_status.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 50 | 51432 | `scripts/governance/d3_metadata/detect_stale_version.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/d3_metadata/detect_stale_version.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/d3_metadata/detect_stale_version.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 51 | 51436 | `scripts/governance/d3_metadata/fix_dm411_bare_relative_imports.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/d3_metadata/fix_dm411_bare_relative_imports.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/d3_metadata/fix_dm411_bare_relative_imports.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 52 | 51433 | `scripts/governance/d3_metadata/fix_dm413_duplicate_test_names.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/d3_metadata/fix_dm413_duplicate_test_names.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/d3_metadata/fix_dm413_duplicate_test_names.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 53 | 51435 | `scripts/governance/d3_metadata/fix_n06_module_id_prefix.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/d3_metadata/fix_n06_module_id_prefix.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/d3_metadata/fix_n06_module_id_prefix.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 54 | 51438 | `scripts/governance/d3_metadata/fix_n12_ke_naming.py` | D-GOVERNANCE | MOVED | scripts/governance/d7_code/fix_n12_ke_naming.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(scripts/governance/d7_code/fix_n12_ke_naming.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 55 | 51437 | `scripts/governance/d3_metadata/fix_n15_blueprint_path.py` | D-GOVERNANCE | MOVED | scripts/governance/d7_code/fix_n15_blueprint_path.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(scripts/governance/d7_code/fix_n15_blueprint_path.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 56 | 51439 | `scripts/governance/d3_metadata/generate_rule_catalog.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/d3_metadata/generate_rule_catalog.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/d3_metadata/generate_rule_catalog.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 57 | 51441 | `scripts/governance/d3_metadata/scan_deep_content.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/d3_metadata/scan_deep_content.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/d3_metadata/scan_deep_content.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 58 | 51448 | `scripts/governance/d3_metadata/validate_blueprint_registry.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/d3_metadata/validate_blueprint_registry.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/d3_metadata/validate_blueprint_registry.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 59 | 51446 | `scripts/governance/d3_metadata/validate_cross_module_dependencies.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/d3_metadata/validate_cross_module_dependencies.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/d3_metadata/validate_cross_module_dependencies.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 60 | 51444 | `scripts/governance/d3_metadata/validate_derived_from.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/d3_metadata/validate_derived_from.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/d3_metadata/validate_derived_from.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 61 | 51445 | `scripts/governance/d3_metadata/validate_enum_consistency.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/d3_metadata/validate_enum_consistency.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/d3_metadata/validate_enum_consistency.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 62 | 51447 | `scripts/governance/d3_metadata/validate_frontmatter_values.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/d3_metadata/validate_frontmatter_values.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/d3_metadata/validate_frontmatter_values.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 63 | 51449 | `scripts/governance/d3_metadata/validate_no_duplicate_files.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/d3_metadata/validate_no_duplicate_files.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/d3_metadata/validate_no_duplicate_files.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 64 | 51452 | `scripts/governance/d3_metadata/validate_ssot_status.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/d3_metadata/validate_ssot_status.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/d3_metadata/validate_ssot_status.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 65 | 51451 | `scripts/governance/d3_metadata/validate_superseded_by.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/d3_metadata/validate_superseded_by.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/d3_metadata/validate_superseded_by.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 66 | 51313 | `scripts/governance/dm101_blueprint_domain_mapping.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/dm101_blueprint_domain_mapping.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/dm101_blueprint_domain_mapping.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 67 | 51328 | `scripts/governance/merge_domain_nodes.py` | D-GOVERNANCE | MOVED | scripts/_archive/governance/merge_domain_nodes.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/merge_domain_nodes.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 68 | 51721 | `scripts/ops/fill_blueprint_ids.py` | D-GOVERNANCE | MOVED | scripts/_archive/ops/fill_blueprint_ids.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/ops/fill_blueprint_ids.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 69 | 48913 | `src/zephyr/governance/models/__init__.py` | D-GOVERNANCE | MOVED | scripts/__init__.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(scripts/__init__.py); git: 无git历史 |
| 70 | 48312 | `src/zephyr/governance/momentum_factor.py` | D-GOVERNANCE | MOVED | src/zephyr/factor/momentum_factor.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(src/zephyr/factor/momentum_factor.py); git: a7a59ef6a9 fix(governance): 清理 ORPHAN MODULES（365→ |
| 71 | 48316 | `src/zephyr/governance/olap_engine.py` | D-GOVERNANCE | MOVED | src/zephyr/infrastructure/db/olap_engine.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(src/zephyr/infrastructure/db/olap_engine.py); git: 768006c66 refactor(shim-elimination): migrate 32 c |
| 72 | 48311 | `src/zephyr/governance/orchestrator.py` | D-GOVERNANCE | MOVED | src/zephyr/governance/audit_trail/orchestrator.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(src/zephyr/governance/audit_trail/orchestrator.py); git: a7a59ef6a9 fix(governance): 清理 ORPHAN MODULES（365→ |
| 73 | 48934 | `src/zephyr/governance/persistence/olap_engine.py` | D-GOVERNANCE | MOVED | src/zephyr/infrastructure/db/olap_engine.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(src/zephyr/infrastructure/db/olap_engine.py); git: 768006c66 refactor(shim-elimination): migrate 32 c |
| 74 | 48453 | `src/zephyr/governance/value_factor.py` | D-GOVERNANCE | MOVED | src/zephyr/factor/value_factor.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(src/zephyr/factor/value_factor.py); git: a7a59ef6a9 fix(governance): 清理 ORPHAN MODULES（365→ |
| 75 | 52747 | `tests/test_alpha_factor.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 76 | 52756 | `tests/test_compliance.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 77 | 52750 | `tests/test_data_source.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 78 | 52759 | `tests/test_experimentation.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 79 | 52544 | `tests/test_fl_safety_gate_l29.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 80 | 52546 | `tests/test_fl_safety_gate_l37.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 81 | 52543 | `tests/test_fl_safety_gate_l39.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 82 | 52548 | `tests/test_fl_safety_gate_l41.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 83 | 52547 | `tests/test_fl_safety_gate_l43.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 84 | 52549 | `tests/test_fl_safety_gate_l45.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 85 | 52550 | `tests/test_fl_safety_gate_l47.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 86 | 52552 | `tests/test_fl_safety_gate_l49.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 87 | 52551 | `tests/test_fl_safety_gate_l51.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 88 | 52553 | `tests/test_fl_safety_gate_l53.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 89 | 52554 | `tests/test_fl_safety_gate_l55.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 90 | 52558 | `tests/test_fl_safety_gate_l57.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 91 | 52555 | `tests/test_fl_safety_gate_l59.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 92 | 52557 | `tests/test_fl_safety_gate_l61.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 93 | 52559 | `tests/test_fl_safety_gate_l63.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 94 | 52556 | `tests/test_fl_safety_gate_l65.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 95 | 52560 | `tests/test_fl_safety_gate_l67.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 96 | 52755 | `tests/test_human_ai_interface.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 97 | 52760 | `tests/test_ml_platform.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 98 | 52753 | `tests/test_portfolio_construction.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 99 | 52758 | `tests/test_post_trade_analytics.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 100 | 52983 | `tests/test_red_blue_validator.py` | D-GOVERNANCE | MOVED | tests/red_blue/test_red_blue_validator.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(tests/red_blue/test_red_blue_validator.py); git: faccee5cf fix(N-10): 修复剩余9个目录命名违规+添加.egg_info豁免
94 |
| 101 | 52757 | `tests/test_research_innovation.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 102 | 52751 | `tests/test_risk_management.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 103 | 53055 | `tests/test_safety_gate_l29.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 104 | 53058 | `tests/test_safety_gate_l37.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 105 | 53059 | `tests/test_safety_gate_l39.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 106 | 53054 | `tests/test_safety_gate_l41.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 107 | 53057 | `tests/test_safety_gate_l43.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 108 | 53062 | `tests/test_safety_gate_l45.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 109 | 53060 | `tests/test_safety_gate_l47.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 110 | 53061 | `tests/test_safety_gate_l49.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 111 | 53063 | `tests/test_safety_gate_l51.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 112 | 53066 | `tests/test_safety_gate_l53.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 113 | 53064 | `tests/test_safety_gate_l55.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 114 | 53070 | `tests/test_safety_gate_l57.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 115 | 53065 | `tests/test_safety_gate_l59.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 116 | 53072 | `tests/test_safety_gate_l61.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 117 | 53067 | `tests/test_safety_gate_l63.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 118 | 53068 | `tests/test_safety_gate_l65.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 119 | 53073 | `tests/test_safety_gate_l67.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 120 | 52752 | `tests/test_signal_generation.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 121 | 52754 | `tests/test_trade_execution.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 122 | 53661 | `tests/unit/test_interface.py` | D-GOVERNANCE | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 123 | 51696 | `scripts/governance/repair/_gen_unregistered_registry.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 124 | 51644 | `scripts/governance/repair/audit_task_cards.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 125 | 51640 | `scripts/governance/repair/backup_depgraph.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 126 | 51647 | `scripts/governance/repair/backup_depgraph_migration.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 127 | 51646 | `scripts/governance/repair/backup_depgraph_v5.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 128 | 51648 | `scripts/governance/repair/check_arch_tables.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 129 | 51651 | `scripts/governance/repair/check_depgraph_schema.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 130 | 51649 | `scripts/governance/repair/check_dm200_and_mig.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 131 | 51650 | `scripts/governance/repair/check_dm_ids.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 132 | 51652 | `scripts/governance/repair/check_governance_db.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 133 | 51654 | `scripts/governance/repair/check_migration_state.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 134 | 51655 | `scripts/governance/repair/check_tasks_constraints.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 135 | 51656 | `scripts/governance/repair/check_tasks_schema.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 136 | 51653 | `scripts/governance/repair/cleanup_migration_residue.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 137 | 51657 | `scripts/governance/repair/create_all_task_cards.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 138 | 51659 | `scripts/governance/repair/create_shared_services_proxies.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 139 | 51658 | `scripts/governance/repair/ensure_dep_cycles_view.py` | D-GOV_AUDIT | MOVED | scripts/_archive/governance/repair/ensure_dep_cycles_view.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/repair/ensure_dep_cycles_view.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 140 | 51663 | `scripts/governance/repair/extract_design_nodes.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 141 | 51660 | `scripts/governance/repair/fix_acceptance_commands.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 142 | 51662 | `scripts/governance/repair/fix_blueprint_path.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 143 | 51661 | `scripts/governance/repair/fix_data_v3.4.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 144 | 51666 | `scripts/governance/repair/import_design_edges.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 145 | 51665 | `scripts/governance/repair/import_design_nodes.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 146 | 51664 | `scripts/governance/repair/list_source_md_files.py` | D-GOV_AUDIT | MOVED | scripts/_archive/governance/repair/list_source_md_files.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(scripts/_archive/governance/repair/list_source_md_files.py); git: 94e8358491 backup: before DM-200915 frontend/scrip |
| 147 | 51670 | `scripts/governance/repair/mig5_fill_gaps.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 148 | 51667 | `scripts/governance/repair/migrate_arch_constraints_v1.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 149 | 51671 | `scripts/governance/repair/migrate_schema_v3.4.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 150 | 51668 | `scripts/governance/repair/migrate_schema_v5.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 151 | 51669 | `scripts/governance/repair/query_p0_3.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 152 | 51672 | `scripts/governance/repair/query_p0_4.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 153 | 51673 | `scripts/governance/repair/query_p0_5.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 154 | 51674 | `scripts/governance/repair/query_p0_6.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 155 | 51680 | `scripts/governance/repair/reimport_design_edges.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 156 | 51676 | `scripts/governance/repair/reimport_design_edges_v2.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 157 | 51679 | `scripts/governance/repair/review_p0_1.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 158 | 51677 | `scripts/governance/repair/review_p0_2.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 159 | 51678 | `scripts/governance/repair/review_p0_3.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 160 | 51681 | `scripts/governance/repair/review_p0_4.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 161 | 51683 | `scripts/governance/repair/review_p0_5.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 162 | 51682 | `scripts/governance/repair/review_p0_6.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 163 | 51684 | `scripts/governance/repair/review_p0_7.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 164 | 51686 | `scripts/governance/repair/task_manager.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 165 | 51688 | `scripts/governance/repair/verify_mig_1.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 166 | 51690 | `scripts/governance/repair/verify_mig_prereq.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 167 | 51687 | `scripts/governance/repair/verify_migration.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 168 | 51689 | `scripts/governance/repair/verify_p0_1.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 169 | 51691 | `scripts/governance/repair/verify_p0_2.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 170 | 51693 | `scripts/governance/repair/verify_p0_3.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 171 | 51692 | `scripts/governance/repair/verify_p0_4.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 172 | 51694 | `scripts/governance/repair/verify_p0_5.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 173 | 51699 | `scripts/governance/repair/verify_p0_6.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 174 | 51695 | `scripts/governance/repair/verify_p0_7.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 175 | 51698 | `scripts/governance/repair/verify_task_cards.py` | D-GOV_AUDIT | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 176 | 49424 | `src/zephyr/infrastructure/pipeline/pipeline_orchestrator.py` | D-INFRA_RUNTIME | MOVED | src/zephyr/autonomy_core/pipeline_orchestrator.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(src/zephyr/autonomy_core/pipeline_orchestrator.py); git: 768006c66 refactor(shim-elimination): migrate 32 c |
| 177 | 49638 | `src/zephyr/integration/models/__init__.py` | D-INTEGRATION | MOVED | scripts/__init__.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(scripts/__init__.py); git: 无git历史 |
| 178 | 49786 | `src/zephyr/integration/shared_08/contracts/gate/__init__.py` | D-INTEGRATION | MOVED | scripts/__init__.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(scripts/__init__.py); git: 768006c66 refactor(shim-elimination): migrate 32 c |
| 179 | 49703 | `src/zephyr/integration/shared_08/event_bus.py` | D-INTEGRATION | MOVED | src/zephyr/shared/event_bus.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(src/zephyr/shared/event_bus.py); git: 768006c66 refactor(shim-elimination): migrate 32 c |
| 180 | 49724 | `src/zephyr/integration/shared_08/token_utils.py` | D-INTEGRATION | MOVED | src/zephyr/shared/shared_services/observability_02/token_utils.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(src/zephyr/shared/shared_services/observability_02/token_utils.py); git: 768006c66 refactor(shim-elimination): migrate 32 c |
| 181 | 50234 | `src/zephyr/ops/gates/safety_gate_l29.py` | D-OPS | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 182 | 50236 | `src/zephyr/ops/gates/safety_gate_l37.py` | D-OPS | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 183 | 50238 | `src/zephyr/ops/gates/safety_gate_l39.py` | D-OPS | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 184 | 50241 | `src/zephyr/ops/gates/safety_gate_l41.py` | D-OPS | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 185 | 50240 | `src/zephyr/ops/gates/safety_gate_l43.py` | D-OPS | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 186 | 50239 | `src/zephyr/ops/gates/safety_gate_l45.py` | D-OPS | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 187 | 50235 | `src/zephyr/ops/gates/safety_gate_l47.py` | D-OPS | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 188 | 50237 | `src/zephyr/ops/gates/safety_gate_l49.py` | D-OPS | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 189 | 50242 | `src/zephyr/ops/gates/safety_gate_l51.py` | D-OPS | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 190 | 50246 | `src/zephyr/ops/gates/safety_gate_l53.py` | D-OPS | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 191 | 50248 | `src/zephyr/ops/gates/safety_gate_l55.py` | D-OPS | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 192 | 50247 | `src/zephyr/ops/gates/safety_gate_l57.py` | D-OPS | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 193 | 50245 | `src/zephyr/ops/gates/safety_gate_l59.py` | D-OPS | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 194 | 50244 | `src/zephyr/ops/gates/safety_gate_l61.py` | D-OPS | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 195 | 50249 | `src/zephyr/ops/gates/safety_gate_l63.py` | D-OPS | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 196 | 50243 | `src/zephyr/ops/gates/safety_gate_l65.py` | D-OPS | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 197 | 50253 | `src/zephyr/ops/gates/safety_gate_l67.py` | D-OPS | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 198 | 50930 | `src/zephyr/ops/observability/token_utils.py` | D-OPS | MOVED | src/zephyr/shared/shared_services/observability_02/token_utils.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(src/zephyr/shared/shared_services/observability_02/token_utils.py); git: 768006c66 refactor(shim-elimination): migrate 32 c |
| 199 | 53858 | `tests/unit/telemetry/test_telemetry.py` | D-OPS | MOVED | tests/test_telemetry.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(tests/test_telemetry.py); git: 无git历史 |
| 200 | 53663 | `tests/unit/test_telemetry_unit.py` | D-OPS | TRULY_DELETED | (全盘无) | DB DELETE | HIGH | 已批准 | TRULY_DELETED确认:磁盘无文件; git: 无git历史 |
| 201 | 50333 | `src/zephyr/pf_core/models/__init__.py` | D-PF_CORE | MOVED | scripts/__init__.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(scripts/__init__.py); git: 无git历史 |
| 202 | 50395 | `src/zephyr/risk/models/__init__.py` | D-RISK | MOVED | scripts/__init__.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(scripts/__init__.py); git: 无git历史 |
| 203 | 50710 | `src/zephyr/shared/api_index.py` | D-SHARED | MOVED | src/zephyr/integration/shared/api_03/api_index.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(src/zephyr/integration/shared/api_03/api_index.py); git: 无git历史 |
| 204 | 50727 | `src/zephyr/shared/context.py` | D-SHARED | MOVED | src/zephyr/integration/shared_08/context.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(src/zephyr/integration/shared_08/context.py); git: 768006c66 refactor(shim-elimination): migrate 32 c |
| 205 | 50843 | `src/zephyr/shared/contracts/gate/__init__.py` | D-SHARED | MOVED | scripts/__init__.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(scripts/__init__.py); git: 768006c66 refactor(shim-elimination): migrate 32 c |
| 206 | 50841 | `src/zephyr/shared/contracts/gate/gate_result.py` | D-SHARED | MOVED | src/zephyr/integration/shared_08/contracts/gate/gate_result.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(src/zephyr/integration/shared_08/contracts/gate/gate_result.py); git: 768006c66 refactor(shim-elimination): migrate 32 c |
| 207 | 50940 | `src/zephyr/shared/observability_02/token_utils.py` | D-SHARED | MOVED | src/zephyr/shared/shared_services/observability_02/token_utils.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(src/zephyr/shared/shared_services/observability_02/token_utils.py); git: 768006c66 refactor(shim-elimination): migrate 32 c |
| 208 | 50971 | `src/zephyr/shared/shared_services/events/event_bus.py` | D-SHARED | MOVED | src/zephyr/shared/event_bus.py | 人工确认目标路径 | MEDIUM | 已批准 | MOVED确认:新路径存在(src/zephyr/shared/event_bus.py); git: 768006c66 refactor(shim-elimination): migrate 32 c |
| 209 | 50784 | `src/zephyr/shared/token_utils.py` | D-SHARED | MOVED | src/zephyr/shared/shared_services/observability_02/token_utils.py | UPDATE路径或DB DELETE | HIGH | 已批准 | MOVED确认:新路径存在(src/zephyr/shared/shared_services/observability_02/token_utils.py); git: 768006c66 refactor(shim-elimination): migrate 32 c |
| 210 | 53893 | `tools/_gen_dedup_tests.py` | D-SHARED | FALSE_POSITIVE | tools/_gen_dedup_tests.py | 无需操作 | HIGH | 已批准 | FALSE_POSITIVE确认:文件存在于磁盘; 2401e174c fix(N-15): BLUEPRINT header path kebab->snake + 4  |

## 5. 执行清单（审查完毕后填写）

> 审查完毕后，将所有「已批准」项按操作类型汇总到此节，生成执行命令。
> 审查完成时间: 2026-06-24 21:51:58
> 审查人: 治理AI (session-20260624-001)

### 5.1 DB DELETE 清单（僵尸节点）

共 128 项（原 117 项 + 11 项 __init__.py 误判修正：原 §5.2 错误映射到 scripts/__init__.py，实际磁盘不存在，改为 DELETE）。

```sql
-- 分批执行（每批≤20项），执行前必须git备份depgraph.db
-- 批次 1: 20项
DELETE FROM nodes WHERE node_id IN (62866, 52747, 52756, 52750, 52759, 52544, 52546, 52543, 52548, 52547, 52549, 52550, 52552, 52551, 52553, 52554, 52558, 52555, 52557, 52559);
-- 批次 2: 20项
DELETE FROM nodes WHERE node_id IN (52556, 52560, 52755, 52760, 52753, 52758, 52757, 52751, 53055, 53058, 53059, 53054, 53057, 53062, 53060, 53061, 53063, 53066, 53064, 53070);
-- 批次 3: 20项
DELETE FROM nodes WHERE node_id IN (53065, 53072, 53067, 53068, 53073, 52752, 52754, 53661, 51696, 51644, 51640, 51647, 51646, 51648, 51651, 51649, 51650, 51652, 51654, 51655);
-- 批次 4: 20项
DELETE FROM nodes WHERE node_id IN (51656, 51653, 51657, 51659, 51663, 51660, 51662, 51661, 51666, 51665, 51670, 51667, 51671, 51668, 51669, 51672, 51673, 51674, 51680, 51676);
-- 批次 5: 20项
DELETE FROM nodes WHERE node_id IN (51679, 51677, 51678, 51681, 51683, 51682, 51684, 51686, 51688, 51690, 51687, 51689, 51691, 51693, 51692, 51694, 51699, 51695, 51698, 50234);
-- 批次 6: 17项
DELETE FROM nodes WHERE node_id IN (50236, 50238, 50241, 50240, 50239, 50235, 50237, 50242, 50246, 50248, 50247, 50245, 50244, 50249, 50243, 50253, 53663);
-- 批次 7: 11项（__init__.py 误判修正：原 §5.2 错误映射到 scripts/__init__.py，磁盘不存在，改为 DELETE）
DELETE FROM nodes WHERE node_id IN (47973, 47977, 47981, 48041, 48059, 53892, 48913, 49638, 50333, 50395, 50843);
```

### 5.2 UPDATE path 清单（僵尸节点路径更新）

共 57 项（原 69 项 - 12 项 __init__.py 误判修正：11 项磁盘不存在移至 §5.1 DELETE，1 项磁盘存在保留原路径无需操作）。

| node_id | 旧路径 | 新路径 |
|:---:|------|------|
| 47975 | `src/zephyr/cross_asset/cross_market_data_adapter/ml_experiment_pipeline.py` | `src/zephyr/risk/cross_asset/cross_market_data_adapter/ml_experiment_pipeline.py` |
| 47971 | `src/zephyr/cross_asset/risk_manager.py` | `src/zephyr/risk/risk_manager.py` |
| 47967 | `src/zephyr/cross_asset/risk_manager_base.py` | `src/zephyr/risk/risk_manager_base.py` |
| 53886 | `frontend/app.py` | `src/zephyr/frontend/dashboard/app.py` |
| 53884 | `frontend/fitness_functions.py` | `src/zephyr/frontend/dashboard/components/fitness_functions.py` |
| 53890 | `frontend/gate_statistics.py` | `src/zephyr/frontend/dashboard/components/gate_statistics.py` |
| 53889 | `frontend/interface_base.py` | `src/zephyr/frontend/interface_base.py` |
| 53887 | `frontend/knowledge_overview.py` | `src/zephyr/frontend/dashboard/components/knowledge_overview.py` |
| 53888 | `frontend/olap_trend.py` | `src/zephyr/frontend/dashboard/components/olap_trend.py` |
| 53891 | `frontend/task_progress.py` | `src/zephyr/frontend/dashboard/components/task_progress.py` |
| 51274 | `scripts/construction/create_db_alignment_tasks.py` | `scripts/_archive/construction/create_db_alignment_tasks.py` |
| 51273 | `scripts/construction/create_dm_phase9_tasks.py` | `scripts/_archive/construction/create_dm_phase9_tasks.py` |
| 51276 | `scripts/construction/dm014_orphan_edge_repair.py` | `scripts/_archive/construction/dm014_orphan_edge_repair.py` |
| 51308 | `scripts/governance/create_depgraph_task_cards.py` | `scripts/_archive/governance/create_depgraph_task_cards.py` |
| 51424 | `scripts/governance/d3_metadata/assign_module_id.py` | `scripts/_archive/governance/d3_metadata/assign_module_id.py` |
| 51427 | `scripts/governance/d3_metadata/check_frontmatter_metadata.py` | `scripts/_archive/governance/d3_metadata/check_frontmatter_metadata.py` |
| 51428 | `scripts/governance/d3_metadata/check_template_compliance.py` | `scripts/_archive/governance/d3_metadata/check_template_compliance.py` |
| 51434 | `scripts/governance/d3_metadata/detect_deprecated_overdue.py` | `scripts/_archive/governance/d3_metadata/detect_deprecated_overdue.py` |
| 51431 | `scripts/governance/d3_metadata/detect_skip_active_status.py` | `scripts/_archive/governance/d3_metadata/detect_skip_active_status.py` |
| 51432 | `scripts/governance/d3_metadata/detect_stale_version.py` | `scripts/_archive/governance/d3_metadata/detect_stale_version.py` |
| 51436 | `scripts/governance/d3_metadata/fix_dm411_bare_relative_imports.py` | `scripts/_archive/governance/d3_metadata/fix_dm411_bare_relative_imports.py` |
| 51433 | `scripts/governance/d3_metadata/fix_dm413_duplicate_test_names.py` | `scripts/_archive/governance/d3_metadata/fix_dm413_duplicate_test_names.py` |
| 51435 | `scripts/governance/d3_metadata/fix_n06_module_id_prefix.py` | `scripts/_archive/governance/d3_metadata/fix_n06_module_id_prefix.py` |
| 51438 | `scripts/governance/d3_metadata/fix_n12_ke_naming.py` | `scripts/governance/d7_code/fix_n12_ke_naming.py` |
| 51437 | `scripts/governance/d3_metadata/fix_n15_blueprint_path.py` | `scripts/governance/d7_code/fix_n15_blueprint_path.py` |
| 51439 | `scripts/governance/d3_metadata/generate_rule_catalog.py` | `scripts/_archive/governance/d3_metadata/generate_rule_catalog.py` |
| 51441 | `scripts/governance/d3_metadata/scan_deep_content.py` | `scripts/_archive/governance/d3_metadata/scan_deep_content.py` |
| 51448 | `scripts/governance/d3_metadata/validate_blueprint_registry.py` | `scripts/_archive/governance/d3_metadata/validate_blueprint_registry.py` |
| 51446 | `scripts/governance/d3_metadata/validate_cross_module_dependencies.py` | `scripts/_archive/governance/d3_metadata/validate_cross_module_dependencies.py` |
| 51444 | `scripts/governance/d3_metadata/validate_derived_from.py` | `scripts/_archive/governance/d3_metadata/validate_derived_from.py` |
| 51445 | `scripts/governance/d3_metadata/validate_enum_consistency.py` | `scripts/_archive/governance/d3_metadata/validate_enum_consistency.py` |
| 51447 | `scripts/governance/d3_metadata/validate_frontmatter_values.py` | `scripts/_archive/governance/d3_metadata/validate_frontmatter_values.py` |
| 51449 | `scripts/governance/d3_metadata/validate_no_duplicate_files.py` | `scripts/_archive/governance/d3_metadata/validate_no_duplicate_files.py` |
| 51452 | `scripts/governance/d3_metadata/validate_ssot_status.py` | `scripts/_archive/governance/d3_metadata/validate_ssot_status.py` |
| 51451 | `scripts/governance/d3_metadata/validate_superseded_by.py` | `scripts/_archive/governance/d3_metadata/validate_superseded_by.py` |
| 51313 | `scripts/governance/dm101_blueprint_domain_mapping.py` | `scripts/_archive/governance/dm101_blueprint_domain_mapping.py` |
| 51328 | `scripts/governance/merge_domain_nodes.py` | `scripts/_archive/governance/merge_domain_nodes.py` |
| 51721 | `scripts/ops/fill_blueprint_ids.py` | `scripts/_archive/ops/fill_blueprint_ids.py` |
| 48312 | `src/zephyr/governance/momentum_factor.py` | `src/zephyr/factor/momentum_factor.py` |
| 48316 | `src/zephyr/governance/olap_engine.py` | `src/zephyr/infrastructure/db/olap_engine.py` |
| 48311 | `src/zephyr/governance/orchestrator.py` | `src/zephyr/governance/audit_trail/orchestrator.py` |
| 48934 | `src/zephyr/governance/persistence/olap_engine.py` | `src/zephyr/infrastructure/db/olap_engine.py` |
| 48453 | `src/zephyr/governance/value_factor.py` | `src/zephyr/factor/value_factor.py` |
| 52983 | `tests/test_red_blue_validator.py` | `tests/red_blue/test_red_blue_validator.py` |
| 51658 | `scripts/governance/repair/ensure_dep_cycles_view.py` | `scripts/_archive/governance/repair/ensure_dep_cycles_view.py` |
| 51664 | `scripts/governance/repair/list_source_md_files.py` | `scripts/_archive/governance/repair/list_source_md_files.py` |
| 49424 | `src/zephyr/infrastructure/pipeline/pipeline_orchestrator.py` | `src/zephyr/autonomy_core/pipeline_orchestrator.py` |
| 49724 | `src/zephyr/integration/shared_08/token_utils.py` | `src/zephyr/shared/shared_services/observability_02/token_utils.py` |
| 50930 | `src/zephyr/ops/observability/token_utils.py` | `src/zephyr/shared/shared_services/observability_02/token_utils.py` |
| 53858 | `tests/unit/telemetry/test_telemetry.py` | `tests/test_telemetry.py` |
| 50710 | `src/zephyr/shared/api_index.py` | `src/zephyr/integration/shared/api_03/api_index.py` |
| 50727 | `src/zephyr/shared/context.py` | `src/zephyr/integration/shared_08/context.py` |
| 50841 | `src/zephyr/shared/contracts/gate/gate_result.py` | `src/zephyr/integration/shared_08/contracts/gate/gate_result.py` |
| 50940 | `src/zephyr/shared/observability_02/token_utils.py` | `src/zephyr/shared/shared_services/observability_02/token_utils.py` |
| 50971 | `src/zephyr/shared/shared_services/events/event_bus.py` | `src/zephyr/shared/event_bus.py` |
| 50784 | `src/zephyr/shared/token_utils.py` | `src/zephyr/shared/shared_services/observability_02/token_utils.py` |

### 5.3 补注册清单（孤儿文件）

共 271 项。

| 路径 | 操作 |
|------|------|
| `scripts/construction/test_deepseek_api.py` | 补注册到全景图 |
| `scripts/demos/demo_e2e_pipeline.py` | 补注册到全景图 |
| `scripts/governance/_audit_gate_registry.py` | 补注册到全景图 |
| `scripts/governance/_check_all_status.py` | 补注册到全景图 |
| `scripts/governance/_check_task.py` | 补注册到全景图 |
| `scripts/governance/_check_vs.py` | 补注册到全景图 |
| `scripts/governance/_list_gate_ids.py` | 补注册到全景图 |
| `scripts/governance/_verify_gate_loading.py` | 补注册到全景图 |
| `scripts/governance/analyze_orphan_consumers.py` | 补注册到全景图 |
| `scripts/governance/check_rule_coverage.py` | 补注册到全景图 |
| `scripts/governance/d3_metadata/validate_rule_frontmatter.py` | 补注册到全景图 |
| `scripts/governance/d5_architecture/dm200912_query_domains.py` | 补注册到全景图 |
| `scripts/governance/d5_architecture/dm200912_rewrite_views.py` | 补注册到全景图 |
| `scripts/governance/d5_architecture/dm200913_rewrite_diagrams.py` | 补注册到全景图 |
| `scripts/governance/d5_architecture/dm200916_write_direct.py` | 补注册到全景图 |
| `scripts/governance/d5_architecture/generators/domain_name_mapping.py` | 补注册到全景图 |
| `scripts/governance/d5_architecture/generators/generate_capability_heatmap.py` | 补注册到全景图 |
| `scripts/governance/d5_architecture/generators/generate_capacity_report.py` | 补注册到全景图 |
| `scripts/governance/d5_architecture/generators/generate_constraint_violations.py` | 补注册到全景图 |
| `scripts/governance/d5_architecture/generators/generate_cross_domain_matrix.py` | 补注册到全景图 |
| `scripts/governance/d5_architecture/generators/generate_design_vs_production.py` | 补注册到全景图 |
| `scripts/governance/d5_architecture/generators/generate_domain_architecture_diagram.py` | 补注册到全景图 |
| `scripts/governance/d5_architecture/generators/generate_domain_dependency_diagram.py` | 补注册到全景图 |
| `scripts/governance/d5_architecture/generators/generate_domain_doc.py` | 补注册到全景图 |
| `scripts/governance/d5_architecture/generators/generate_domain_index.py` | 补注册到全景图 |
| `scripts/governance/d5_architecture/generators/generate_integration_topology.py` | 补注册到全景图 |
| `scripts/governance/d5_architecture/generators/generate_navigation_index.py` | 补注册到全景图 |
| `scripts/governance/d5_architecture/generators/generate_path_tree.py` | 补注册到全景图 |
| `scripts/governance/d5_architecture/generators/generate_runtime_plane_mapping.py` | 补注册到全景图 |
| `scripts/governance/d7_code/fix_n06_scope.py` | 补注册到全景图 |
| `scripts/governance/d7_code/fix_n12_ke_naming.py` | 补注册到全景图 |
| `scripts/governance/d7_code/fix_n13_snake_case.py` | 补注册到全景图 |
| `scripts/governance/d7_code/fix_n14_init_all.py` | 补注册到全景图 |
| `scripts/governance/d7_code/fix_n15_blueprint_path.py` | 补注册到全景图 |
| `scripts/governance/d7_code/fix_naming_manual.py` | 补注册到全景图 |
| `scripts/governance/group_orphan_modules.py` | 补注册到全景图 |
| `scripts/governance/iterative_cleanup_imports.py` | 补注册到全景图 |
| `scripts/governance/perf_depgraph_baseline.py` | 补注册到全景图 |
| `scripts/governance/register_orphan_modules.py` | 补注册到全景图 |
| `scripts/governance/rename_whitelist_cleanup.py` | 补注册到全景图 |
| `scripts/governance/repair/concurrent_write_test.py` | 补注册到全景图 |
| `scripts/governance/task_show.py` | 补注册到全景图 |
| `scripts/governance/verify_key_imports.py` | 补注册到全景图 |
| `scripts/ide_health_service.py` | 补注册到全景图 |
| `scripts/ops/auto_fix_cron.py` | 补注册到全景图 |
| `scripts/ops/upgrade_headers_to_14fields.py` | 补注册到全景图 |
| `scripts/record_session_start_commit.py` | 补注册到全景图 |
| `src/zephyr/autonomy_core/context_pipeline_auto.py` | 补注册到全景图 |
| `src/zephyr/data/__init__.py` | 补注册到全景图 |
| `src/zephyr/governance/auto_runner.py` | 补注册到全景图 |
| `src/zephyr/governance/behavioral_auditor/__init__.py` | 补注册到全景图 |
| `src/zephyr/governance/budget_enforcement.py` | 补注册到全景图 |
| `src/zephyr/governance/escalation/__init__.py` | 补注册到全景图 |
| `src/zephyr/governance/f5_boot_integration.py` | 补注册到全景图 |
| `src/zephyr/governance/f5_event_subscriber.py` | 补注册到全景图 |
| `src/zephyr/governance/f5_shutdown_manager.py` | 补注册到全景图 |
| `src/zephyr/governance/rule_enforcement/invariants/post_doc_review_check.py` | 补注册到全景图 |
| `src/zephyr/governance/rule_enforcement/phase_executor.py` | 补注册到全景图 |
| `src/zephyr/governance/semantic_audit/orchestrator.py` | 补注册到全景图 |
| `src/zephyr/infra_ops/dashboard/__init__.py` | 补注册到全景图 |
| `src/zephyr/infra_ops/dashboard/components/__init__.py` | 补注册到全景图 |
| `src/zephyr/infrastructure/rollback/rollback_boot_integration.py` | 补注册到全景图 |
| `src/zephyr/infrastructure/rollback/rollback_scheduler.py` | 补注册到全景图 |
| `src/zephyr/integration/local_model/deepseek_chat.py` | 补注册到全景图 |
| `src/zephyr/integration/pipeline_routing.py` | 补注册到全景图 |
| `src/zephyr/ops/gates/safety_gate_l28_l29.py` | 补注册到全景图 |
| `src/zephyr/ops/gates/safety_gate_l36_l37.py` | 补注册到全景图 |
| `src/zephyr/ops/gates/safety_gate_l38_l39.py` | 补注册到全景图 |
| `src/zephyr/ops/gates/safety_gate_l40_l41.py` | 补注册到全景图 |
| `src/zephyr/ops/gates/safety_gate_l42_l43.py` | 补注册到全景图 |
| `src/zephyr/ops/gates/safety_gate_l44_l45.py` | 补注册到全景图 |
| `src/zephyr/ops/gates/safety_gate_l46_l47.py` | 补注册到全景图 |
| `src/zephyr/ops/gates/safety_gate_l48_l49.py` | 补注册到全景图 |
| `src/zephyr/ops/gates/safety_gate_l50_l51.py` | 补注册到全景图 |
| `src/zephyr/ops/gates/safety_gate_l52_l53.py` | 补注册到全景图 |
| `src/zephyr/ops/gates/safety_gate_l54_l55.py` | 补注册到全景图 |
| `src/zephyr/ops/gates/safety_gate_l56_l57.py` | 补注册到全景图 |
| `src/zephyr/ops/gates/safety_gate_l58_l59.py` | 补注册到全景图 |
| `src/zephyr/ops/gates/safety_gate_l60_l61.py` | 补注册到全景图 |
| `src/zephyr/ops/gates/safety_gate_l62_l63.py` | 补注册到全景图 |
| `src/zephyr/ops/gates/safety_gate_l64_l65.py` | 补注册到全景图 |
| `src/zephyr/ops/gates/safety_gate_l66_l67.py` | 补注册到全景图 |
| `src/zephyr/ops/observability/notifier.py` | 补注册到全景图 |
| `src/zephyr/shared/adaptation/__init__.py` | 补注册到全景图 |
| `src/zephyr/shared/compensation/__init__.py` | 补注册到全景图 |
| `src/zephyr/shared/dependency/__init__.py` | 补注册到全景图 |
| `src/zephyr/shared/draft/__init__.py` | 补注册到全景图 |
| `src/zephyr/shared/infra_06/__init__.py` | 补注册到全景图 |
| `src/zephyr/shared/knowledge/__init__.py` | 补注册到全景图 |
| `src/zephyr/shared/lifecycle/scope_guard.py` | 补注册到全景图 |
| `src/zephyr/shared/lifecycle/task_lifecycle_manager.py` | 补注册到全景图 |
| `src/zephyr/shared/maintenance/__init__.py` | 补注册到全景图 |
| `src/zephyr/shared/observability_02/__init__.py` | 补注册到全景图 |
| `src/zephyr/shared/quality/__init__.py` | 补注册到全景图 |
| `src/zephyr/shared/queue/__init__.py` | 补注册到全景图 |
| `src/zephyr/shared/queue/task_scheduler.py` | 补注册到全景图 |
| `src/zephyr/shared/reliability/__init__.py` | 补注册到全景图 |
| `src/zephyr/shared/reliability/context_guard.py` | 补注册到全景图 |
| `src/zephyr/shared/session/__init__.py` | 补注册到全景图 |
| `src/zephyr/shared/sla/__init__.py` | 补注册到全景图 |
| `src/zephyr/trading/runtime/__init__.py` | 补注册到全景图 |
| `src/zephyr/trading/runtime/async_runtime.py` | 补注册到全景图 |
| `tests/adversarial/test_f3_extreme.py` | 补注册到全景图 |
| `tests/adversarial/test_rollback_concurrent_extreme.py` | 补注册到全景图 |
| `tests/adversarial/test_rollback_partial_extreme.py` | 补注册到全景图 |
| `tests/adversarial/test_rollback_scheduler.py` | 补注册到全景图 |
| `tests/agent_rbac/test_rbac_auto_lifecycle.py` | 补注册到全景图 |
| `tests/e2e/test_mcp_full_lifecycle_e2e.py` | 补注册到全景图 |
| `tests/governance/test_database_service.py` | 补注册到全景图 |
| `tests/integration/test_f3_auto_integration.py` | 补注册到全景图 |
| `tests/integration/test_mcp_boot_hooks_integration.py` | 补注册到全景图 |
| `tests/integration/test_mcp_health_check_cron.py` | 补注册到全景图 |
| `tests/integration/test_mcp_health_check_recovery.py` | 补注册到全景图 |
| `tests/integration/test_mcp_idle_timeout.py` | 补注册到全景图 |
| `tests/integration/test_mcp_signal_shutdown.py` | 补注册到全景图 |
| `tests/red_blue/__init__.py` | 补注册到全景图 |
| `tests/red_blue/_test_lock_target.py` | 补注册到全景图 |
| `tests/red_blue/test_async_monitor.py` | 补注册到全景图 |
| `tests/red_blue/test_circuit_breaker.py` | 补注册到全景图 |
| `tests/red_blue/test_constitution_engine.py` | 补注册到全景图 |
| `tests/red_blue/test_context_pipeline_red_blue.py` | 补注册到全景图 |
| `tests/red_blue/test_defense_runner.py` | 补注册到全景图 |
| `tests/red_blue/test_event_integration.py` | 补注册到全景图 |
| `tests/red_blue/test_f14_pipeline_extreme.py` | 补注册到全景图 |
| `tests/red_blue/test_f18_governance_adversarial.py` | 补注册到全景图 |
| `tests/red_blue/test_f1_extreme.py` | 补注册到全景图 |
| `tests/red_blue/test_game_day_scheduler.py` | 补注册到全景图 |
| `tests/red_blue/test_injection_engine.py` | 补注册到全景图 |
| `tests/red_blue/test_phase_manager_integration.py` | 补注册到全景图 |
| `tests/red_blue/test_red_blue_validator.py` | 补注册到全景图 |
| `tests/test_adversarial_extreme.py` | 补注册到全景图 |
| `tests/test_arbiter.py` | 补注册到全景图 |
| `tests/test_auto_fix_autopilot.py` | 补注册到全景图 |
| `tests/test_auto_fix_phase_manager.py` | 补注册到全景图 |
| `tests/test_auto_fix_red_blue.py` | 补注册到全景图 |
| `tests/test_auto_runtime_e2e.py` | 补注册到全景图 |
| `tests/test_auto_runtime_fle_integration.py` | 补注册到全景图 |
| `tests/test_budget_event_driven.py` | 补注册到全景图 |
| `tests/test_budget_lifecycle_e2e.py` | 补注册到全景图 |
| `tests/test_budget_shutdown.py` | 补注册到全景图 |
| `tests/test_circadian_red_blue_drill.py` | 补注册到全景图 |
| `tests/test_conductor.py` | 补注册到全景图 |
| `tests/test_f10_red_blue.py` | 补注册到全景图 |
| `tests/test_f18_automation.py` | 补注册到全景图 |
| `tests/test_f18_redblue.py` | 补注册到全景图 |
| `tests/test_f1_event_trigger.py` | 补注册到全景图 |
| `tests/test_f21_auto_run.py` | 补注册到全景图 |
| `tests/test_f21_auto_shutdown.py` | 补注册到全景图 |
| `tests/test_f21_auto_startup.py` | 补注册到全景图 |
| `tests/test_f21_event_driven.py` | 补注册到全景图 |
| `tests/test_f5_auto_shutdown.py` | 补注册到全景图 |
| `tests/test_f5_auto_startup.py` | 补注册到全景图 |
| `tests/test_f5_e2e_lifecycle.py` | 补注册到全景图 |
| `tests/test_f5_event_startup.py` | 补注册到全景图 |
| `tests/test_f5_red_team_extreme.py` | 补注册到全景图 |
| `tests/test_fl_safety_gate_l28_l29.py` | 补注册到全景图 |
| `tests/test_fl_safety_gate_l36_l37.py` | 补注册到全景图 |
| `tests/test_fl_safety_gate_l38_l39.py` | 补注册到全景图 |
| `tests/test_fl_safety_gate_l40_l41.py` | 补注册到全景图 |
| `tests/test_fl_safety_gate_l42_l43.py` | 补注册到全景图 |
| `tests/test_fl_safety_gate_l44_l45.py` | 补注册到全景图 |
| `tests/test_fl_safety_gate_l46_l47.py` | 补注册到全景图 |
| `tests/test_fl_safety_gate_l48_l49.py` | 补注册到全景图 |
| `tests/test_fl_safety_gate_l50_l51.py` | 补注册到全景图 |
| `tests/test_fl_safety_gate_l52_l53.py` | 补注册到全景图 |
| `tests/test_fl_safety_gate_l54_l55.py` | 补注册到全景图 |
| `tests/test_fl_safety_gate_l56_l57.py` | 补注册到全景图 |
| `tests/test_fl_safety_gate_l58_l59.py` | 补注册到全景图 |
| `tests/test_fl_safety_gate_l60_l61.py` | 补注册到全景图 |
| `tests/test_fl_safety_gate_l62_l63.py` | 补注册到全景图 |
| `tests/test_fl_safety_gate_l64_l65.py` | 补注册到全景图 |
| `tests/test_fl_safety_gate_l66_l67.py` | 补注册到全景图 |
| `tests/test_g_trae_003.py` | 补注册到全景图 |
| `tests/test_g_trae_004.py` | 补注册到全景图 |
| `tests/test_g_trae_006.py` | 补注册到全景图 |
| `tests/test_g_trae_007.py` | 补注册到全景图 |
| `tests/test_g_trae_008.py` | 补注册到全景图 |
| `tests/test_g_trae_009.py` | 补注册到全景图 |
| `tests/test_g_trae_010.py` | 补注册到全景图 |
| `tests/test_g_trae_011.py` | 补注册到全景图 |
| `tests/test_g_trae_012.py` | 补注册到全景图 |
| `tests/test_g_trae_016.py` | 补注册到全景图 |
| `tests/test_g_trae_017.py` | 补注册到全景图 |
| `tests/test_g_trae_018.py` | 补注册到全景图 |
| `tests/test_g_trae_020.py` | 补注册到全景图 |
| `tests/test_g_trae_021.py` | 补注册到全景图 |
| `tests/test_g_trae_022.py` | 补注册到全景图 |
| `tests/test_g_trae_023.py` | 补注册到全景图 |
| `tests/test_g_trae_024.py` | 补注册到全景图 |
| `tests/test_g_trae_025.py` | 补注册到全景图 |
| `tests/test_g_trae_026.py` | 补注册到全景图 |
| `tests/test_g_trae_027.py` | 补注册到全景图 |
| `tests/test_g_trae_028.py` | 补注册到全景图 |
| `tests/test_g_trae_029.py` | 补注册到全景图 |
| `tests/test_g_trae_030.py` | 补注册到全景图 |
| `tests/test_g_trae_031.py` | 补注册到全景图 |
| `tests/test_g_trae_032.py` | 补注册到全景图 |
| `tests/test_g_trae_033.py` | 补注册到全景图 |
| `tests/test_g_trae_034.py` | 补注册到全景图 |
| `tests/test_g_trae_035.py` | 补注册到全景图 |
| `tests/test_g_trae_036.py` | 补注册到全景图 |
| `tests/test_g_trae_037.py` | 补注册到全景图 |
| `tests/test_g_trae_038.py` | 补注册到全景图 |
| `tests/test_g_trae_039.py` | 补注册到全景图 |
| `tests/test_g_trae_040.py` | 补注册到全景图 |
| `tests/test_g_trae_041.py` | 补注册到全景图 |
| `tests/test_g_trae_042.py` | 补注册到全景图 |
| `tests/test_g_trae_043.py` | 补注册到全景图 |
| `tests/test_g_trae_044.py` | 补注册到全景图 |
| `tests/test_g_trae_045.py` | 补注册到全景图 |
| `tests/test_g_trae_046.py` | 补注册到全景图 |
| `tests/test_g_trae_047.py` | 补注册到全景图 |
| `tests/test_g_trae_048.py` | 补注册到全景图 |
| `tests/test_g_trae_049.py` | 补注册到全景图 |
| `tests/test_g_trae_050.py` | 补注册到全景图 |
| `tests/test_g_trae_051.py` | 补注册到全景图 |
| `tests/test_g_trae_052.py` | 补注册到全景图 |
| `tests/test_g_trae_053.py` | 补注册到全景图 |
| `tests/test_g_trae_054.py` | 补注册到全景图 |
| `tests/test_g_trae_055.py` | 补注册到全景图 |
| `tests/test_ide_health_daemon.py` | 补注册到全景图 |
| `tests/test_l00_data_source.py` | 补注册到全景图 |
| `tests/test_l02_alpha_factor.py` | 补注册到全景图 |
| `tests/test_l03_signal_generation.py` | 补注册到全景图 |
| `tests/test_l04_risk_management.py` | 补注册到全景图 |
| `tests/test_l05_portfolio_construction.py` | 补注册到全景图 |
| `tests/test_l06_trade_execution.py` | 补注册到全景图 |
| `tests/test_l07_post_trade_analytics.py` | 补注册到全景图 |
| `tests/test_l08_human_ai_interface.py` | 补注册到全景图 |
| `tests/test_l09_research_innovation.py` | 补注册到全景图 |
| `tests/test_l10_compliance.py` | 补注册到全景图 |
| `tests/test_l11_ml_platform.py` | 补注册到全景图 |
| `tests/test_l13_experimentation.py` | 补注册到全景图 |
| `tests/test_lock_release_uncommitted.py` | 补注册到全景图 |
| `tests/test_mcp_launcher.py` | 补注册到全景图 |
| `tests/test_phase_executor_rule_enforcement.py` | 补注册到全景图 |
| `tests/test_pipeline_orchestrator_auto.py` | 补注册到全景图 |
| `tests/test_post_doc_review.py` | 补注册到全景图 |
| `tests/test_red_blue_validator_tests.py` | 补注册到全景图 |
| `tests/test_safety_gate_l28_l29.py` | 补注册到全景图 |
| `tests/test_safety_gate_l36_l37.py` | 补注册到全景图 |
| `tests/test_safety_gate_l38_l39.py` | 补注册到全景图 |
| `tests/test_safety_gate_l40_l41.py` | 补注册到全景图 |
| `tests/test_safety_gate_l42_l43.py` | 补注册到全景图 |
| `tests/test_safety_gate_l44_l45.py` | 补注册到全景图 |
| `tests/test_safety_gate_l46_l47.py` | 补注册到全景图 |
| `tests/test_safety_gate_l48_l49.py` | 补注册到全景图 |
| `tests/test_safety_gate_l50_l51.py` | 补注册到全景图 |
| `tests/test_safety_gate_l52_l53.py` | 补注册到全景图 |
| `tests/test_safety_gate_l54_l55.py` | 补注册到全景图 |
| `tests/test_safety_gate_l56_l57.py` | 补注册到全景图 |
| `tests/test_safety_gate_l58_l59.py` | 补注册到全景图 |
| `tests/test_safety_gate_l60_l61.py` | 补注册到全景图 |
| `tests/test_safety_gate_l62_l63.py` | 补注册到全景图 |
| `tests/test_safety_gate_l64_l65.py` | 补注册到全景图 |
| `tests/test_safety_gate_l66_l67.py` | 补注册到全景图 |
| `tests/test_task_repo_auto_commit.py` | 补注册到全景图 |
| `tests/test_trading_session_lifecycle.py` | 补注册到全景图 |
| `tests/test_validate_rule_frontmatter_red_blue.py` | 补注册到全景图 |
| `tests/trading/runtime/test_async_runtime.py` | 补注册到全景图 |
| `tests/unit/feedback_loop/test_scheduler_integration.py` | 补注册到全景图 |
| `tests/unit/pipeline/conftest.py` | 补注册到全景图 |
| `tests/unit/telemetry/test_l12_telemetry.py` | 补注册到全景图 |
| `tests/unit/test_concurrency_guard.py` | 补注册到全景图 |
| `tests/unit/test_context_pipeline_auto.py` | 补注册到全景图 |
| `tests/unit/test_l08_interface.py` | 补注册到全景图 |
| `tests/unit/test_l12_telemetry_unit.py` | 补注册到全景图 |
| `tests/unit/vector_memory/test_vms_adversarial_hijack.py` | 补注册到全景图 |
| `tests/unit/vector_memory/test_vms_adversarial_injection.py` | 补注册到全景图 |
| `tests/unit/vector_memory/test_vms_automation.py` | 补注册到全景图 |
| `tests/unit/vector_memory/test_vms_lifecycle.py` | 补注册到全景图 |

### 5.4 磁盘删除清单（孤儿文件）

共 8 项。

| 路径 | 原因 |
|------|------|
| `scripts/_audit_gen2.py` | 3a=N(临时脚本，无引用，一次性使用); 3b=N(临时脚本，非管线问题); 3c=N(临时脚本，重建成本低); 无引用 |
| `scripts/_complete_dm201008.py` | 3a=N(临时脚本，无引用，一次性使用); 3b=N(临时脚本，非管线问题); 3c=N(临时脚本，重建成本低); 无引用 |
| `scripts/_query_dm201008.py` | 3a=N(临时脚本，无引用，一次性使用); 3b=N(临时脚本，非管线问题); 3c=N(临时脚本，重建成本低); 无引用 |
| `scripts/_query_rbac_core.py` | 3a=N(临时脚本，无引用，一次性使用); 3b=N(临时脚本，非管线问题); 3c=N(临时脚本，重建成本低); 无引用 |
| `scripts/_update_rbac_depgraph.py` | 3a=N(临时脚本，无引用，一次性使用); 3b=N(临时脚本，非管线问题); 3c=N(临时脚本，重建成本低); 无引用 |
| `tests/red_blue/_test_commit_target.py` | 3a=N(临时脚本，无引用，一次性使用); 3b=N(临时脚本，非管线问题); 3c=N(临时脚本，重建成本低); 无引用 |
| `tests/red_blue/_test_mixed_target.py` | 3a=N(临时脚本，无引用，一次性使用); 3b=N(临时脚本，非管线问题); 3c=N(临时脚本，重建成本低); 无引用 |
| `tests/red_blue/_test_staging_target.py` | 3a=N(临时脚本，无引用，一次性使用); 3b=N(临时脚本，非管线问题); 3c=N(临时脚本，重建成本低); 无引用 |

## 6. 审查记录

| 日期 | 审查人 | 审查范围 | 批准数 | 拒绝数 | 备注 |
|------|------|------|:---:|:---:|------|
| 2026-06-24 | 治理AI (session-20260624-001) | §3孤儿312项+§4僵尸210项=522项 | 522 | 0 | 全部审查完毕，待审查=0 |

---

## 审查流程

1. 逐行检查 §3（孤儿）和 §4（僵尸）的审查表
2. 对每条记录，判断推荐操作是否正确：
   - 同意 → 审查状态改为「已批准」
   - 不同意 → 审查状态改为「已拒绝」，备注栏说明原因
3. 全部审查完毕后，将「已批准」项汇总到 §5 执行清单
4. 生成执行命令，经最终确认后执行
5. 执行完毕后将审查状态改为「已执行」

## 执行原则

- **禁止未审查直接执行**
- **禁止跨项批量执行**（每批≤20项，执行后验证）
- **执行前必须 git 备份 depgraph.db**
- **每批执行后验证全景图一致性**
