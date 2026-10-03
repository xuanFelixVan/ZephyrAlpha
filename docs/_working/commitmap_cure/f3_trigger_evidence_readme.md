---
ttl: task_bound
completes_when: 内收对审消费完触发证据后随战役册转归档参考
title: F3 触发证据口径与复现命令
---

# F3 触发证据抽取 README（sid=st-f3-triggers-20261003）

生成时间: 2026-10-03 11:46 UTC | 宇宙: docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml 的 gates 数组 = 182 台（148 active + 34 deprecated，实测，勿背数）

## 产物
- `f3_trigger_evidence.csv` — 主表，182 行逐台对账（1 行 = 1 台在册门禁，注册册原始顺序）
- `f3_consumer_detail.csv` — 消费者全量明细（机制,消费者文件,类别=production/test），主表清单列超40条截断指向本表
- `f3_zero_trigger_candidates.csv` — 零触发台汇总（退役候选名单），含双零标记
- `f3_double_zero_list.csv` — 双零名单单列（零触发 ∧ 零消费者）
- 本 README — 口径与复现命令

## 触发口径（主指标"近30天触发" = 下列五项结构化证据之和，均为 .runtime 审计实测）
1. **执行** = gate_execution_stats.jsonl 每次提交链运行中出现在 ms/failed 键的门禁（执行即触发，含拦截）
2. **拦截(commit流)** = commit_block_events.jsonl 的 gate_id 字段
3. **拦截(preflight流)** = preflight_events.jsonl 的 gates_failed（degraded 单列不计入触发）
4. **包装块归因拦截** = commit_block_events.jsonl 中 gate_id=GATE-PRECOMMIT-RUN 包装块的 detail 归因（banner 大写 token + hook=['小写id'] 双路匹配）——pre-commit 通道拦截的唯一留痕位，30天共839次包装块
5. **解析失败** = create_guard_parse_fail.jsonl 全部记到 CREATE-GUARD 名下
- **缓存重用** 单列不计入触发（缓存命中=链路在跑但门禁逻辑未实跑）
- **孪生id触发30天** 列 = 册内裸名/GATE-前缀孪生行的触发数（册内3对：DIRECTORY-CONTRACT、PROTECTED-PATHS、WORKTREE-REQUIRED），用于识别更名残留假零
- **提及其他审计流** = bottleneck_ledger/feature_flags/write_audit/safe_write/worktree_drift_watchdog/emergency_track/gate_audit 等其余 .jsonl 流中 gate_id 的字符串出现（提示性证据，单独列，不计入主指标）
- 时间窗：滚动 30 天/7 天（UTC），NOW=2026-10-03 11:46 UTC

## 消费者口径
全仓文本文件（.py/.md/.yaml/.yml/.json/.csv/.txt/.ps1/.sh/.sql/.js 等）对 gate_id（含去 GATE- 前缀别名）的精确 token 匹配（大小写敏感、词边界）。排除：.git/.runtime/.worktrees/.aidrafts/docs/_working、两份门禁注册册自登记（自登记单列计数，见脚本审计行）、二进制与大文件(>30MB)。
"消费者数"=非注册册自登记的全部引用文件；"非测试消费者数"=剔除 tests/ 后。

## 复现命令
```bash
# ① 触发计数（结构化四流，示例：近30天按 gate_id）
python - <<'EOF'
import json, io, collections, datetime
NOW = datetime.datetime.now(datetime.timezone.utc); W30 = NOW - datetime.timedelta(days=30)
cnt = collections.Counter()
for line in io.open(r".runtime/audit/gate_execution_stats.jsonl", encoding="utf-8"):
    try: r = json.loads(line)
    except Exception: continue
    ts = r.get("timestamp"); d = datetime.datetime.fromisoformat(ts) if ts else None
    if d and d >= W30:
        for k in set(list((r.get("ms") or {}).keys()) + list((r.get("reused") or {}).keys()) + list(r.get("failed") or [])):
            cnt[k] += 1
print(cnt.most_common(30))
EOF
# 拦截流：同法读 .runtime/audit/commit_block_events.jsonl 的 gate_id 字段、
#         .runtime/audit/preflight_events.jsonl 的 gates_failed 字段，按 30d/7d 分桶
# ② 消费者反查（示例单台）
grep -rn --include="*.py" --include="*.md" --include="*.yaml" -wE "GATE-PROTECTED-PATHS|PROTECTED-PATHS" src scripts docs config tests | grep -v "docs/_working" | cut -d: -f1 | sort -u
# ③ 队列四态计数（只读条目数，未读任何袋内容）
for d in pending processing done dead dead_archive; do echo -n "$d: "; ls .runtime/commit_queue/$d 2>/dev/null | wc -l; done
# ④ dead 死因 top20（读 .runtime/audit/bottleneck_ledger.jsonl 的 dead_letter 记录，qid 去重后按 reason 首行归一计数）
grep '"dead_letter"' .runtime/audit/bottleneck_ledger.jsonl | head -3
# ⑤ 全量再生（本表由该脚本产出）
python .runtime/tmp/f3_triggers_20261003/f3_extract.py
```

## 流覆盖度（审计流实测）
| 流 | 行数 | 首条时间 | 末条时间 | 含gate_id提及的行数 |
|---|---|---|---|---|
| algo_flow_translation_sync_runs.jsonl | 193 | 2026-08-20 17:53 | 2026-09-29 18:36 | 21 |
| autonomy_boundary_gate.jsonl | 3 | 2026-08-22 06:04 | 2026-08-22 06:04 | 0 |
| bottleneck_ledger.jsonl | 151550 | 2026-09-15 22:10 | 2026-10-03 11:34 | 0 |
| commit_block_events.jsonl | 3478 | 2026-09-13 11:14 | 2026-10-03 10:34 | 0 |
| create_guard_parse_fail.jsonl | 27 | 2026-09-16 01:52 | 2026-09-30 23:55 | 0 |
| debt_ratchet_lever_20261001.jsonl | 3 | 2026-10-01 03:42 | 2026-10-01 07:05 | 1 |
| emergency_track.jsonl | 3101 | 2026-09-18 10:45 | 2026-10-03 11:46 | 1000 |
| feature_flags.jsonl | 10576 | 2026-10-03 11:07 | 2026-10-03 11:46 | 2861 |
| gate_audit/algo_note_payload_review.jsonl | 88 | 2026-09-10 05:04 | 2026-09-26 21:10 | 11 |
| gate_audit/allow_overlap_usage.jsonl | 6444 | 2026-07-20 02:55 | 2026-10-01 20:23 | 547 |
| gate_audit/asyncio_run_in_context_foreign_staged.jsonl | 4309 | 2026-09-10 14:07 | 2026-10-03 09:32 | 4309 |
| gate_audit/bare_subprocess_foreign_staged.jsonl | 3832 | 2026-09-10 15:10 | 2026-10-03 09:34 | 3832 |
| gate_audit/blueprint_node_id_hardcode_foreign_staged.jsonl | 59 | 2026-09-22 19:27 | 2026-09-30 20:57 | 59 |
| gate_audit/cap_consistency_foreign_staged.jsonl | 736 | 2026-09-12 11:56 | 2026-10-01 17:29 | 736 |
| gate_audit/capability_overlap_foreign_staged.jsonl | 2404 | 2026-09-11 15:50 | 2026-10-03 09:34 | 2404 |
| gate_audit/ch_final_gate_foreign_staged.jsonl | 1096 | 2026-09-22 19:27 | 2026-10-03 09:34 | 1096 |
| gate_audit/ch_version_col_foreign_staged.jsonl | 276 | 2026-09-22 19:27 | 2026-09-27 04:17 | 276 |
| gate_audit/commit_lock_fallback.jsonl | 15 | 2026-09-09 13:41 | 2026-09-23 18:56 | 0 |
| gate_audit/constitution_line_limit_foreign_staged.jsonl | 906 | 2026-09-23 16:55 | 2026-10-03 09:34 | 12 |
| gate_audit/create_guard_foreign_staged.jsonl | 1135 | 2026-09-22 19:27 | 2026-10-03 09:34 | 1135 |
| gate_audit/create_guard_keyword_dup_warn.jsonl | 17 | 2026-10-01 18:59 | 2026-10-01 23:15 | 17 |
| gate_audit/create_guard_merge_evaluation.jsonl | 201 | 2026-09-20 09:50 | 2026-09-27 00:11 | 201 |
| gate_audit/create_guard_token_sim_shadow.jsonl | 214 | 2026-10-01 18:59 | 2026-10-01 23:15 | 214 |
| gate_audit/datetime_now_forbidden_foreign_staged.jsonl | 9758 | 2026-09-11 19:56 | 2026-10-03 11:39 | 9758 |
| gate_audit/depgraph_anchor_cascade.jsonl | 7 | 2026-08-14 06:35 | 2026-09-30 14:03 | 0 |
| gate_audit/depgraph_pre_registration_foreign_staged.jsonl | 1056 | 2026-09-22 19:29 | 2026-10-03 09:34 | 1056 |
| gate_audit/depgraph_write_path_foreign_staged.jsonl | 1007 | 2026-09-23 01:59 | 2026-10-03 09:34 | 1007 |
| gate_audit/derivation_annotation_foreign_staged.jsonl | 993 | 2026-09-22 19:29 | 2026-10-03 09:34 | 993 |
| gate_audit/derived_file_deletion_foreign_staged.jsonl | 763 | 2026-09-22 21:16 | 2026-10-03 09:34 | 51 |
| gate_audit/derived_write_attribution.jsonl | 138 | 2026-09-17 12:41 | 2026-10-02 19:39 | 0 |
| gate_audit/design_node_delete.jsonl | 43 | 2026-08-01 14:42 | 2026-08-25 16:59 | 2 |
| gate_audit/doc_ref_broken_foreign_staged.jsonl | 1326 | 2026-09-22 19:28 | 2026-10-03 09:34 | 1326 |
| gate_audit/empty_handler_foreign_staged.jsonl | 897 | 2026-09-22 19:28 | 2026-10-03 09:34 | 897 |
| gate_audit/file_copy_foreign_staged.jsonl | 1009 | 2026-09-22 19:28 | 2026-10-03 09:32 | 1009 |
| gate_audit/fms_hygiene.jsonl | 223 | 2026-09-26 21:05 | 2026-10-02 13:51 | 223 |
| gate_audit/fms_hygiene_foreign_staged.jsonl | 552 | 2026-09-26 21:05 | 2026-10-03 09:34 | 552 |
| gate_audit/force_merge_usage.jsonl | 233 | 2026-07-21 09:56 | 2026-09-30 13:49 | 0 |
| gate_audit/frontend_truth_source.jsonl | 145 | 2026-09-12 02:27 | 2026-09-24 20:08 | 145 |
| gate_audit/frontend_truth_source_foreign_staged.jsonl | 368 | 2026-09-22 21:32 | 2026-10-03 09:34 | 368 |
| gate_audit/function_dup_foreign_staged.jsonl | 737 | 2026-09-22 19:28 | 2026-10-01 06:49 | 737 |
| gate_audit/gate_domain_fk_foreign_staged.jsonl | 231 | 2026-09-29 21:03 | 2026-10-02 21:27 | 231 |
| gate_audit/gate_panorama_alignment_foreign_staged.jsonl | 183 | 2026-09-22 19:30 | 2026-09-29 18:29 | 183 |
| gate_audit/gateway_index_hygiene.jsonl | 68 | 2026-09-13 23:19 | 2026-10-01 18:02 | 0 |
| gate_audit/git_guard_self_harm.jsonl | 15 | 2026-08-03 16:50 | 2026-08-26 16:35 | 0 |
| gate_audit/governance_actions.jsonl | 15 | 2026-09-17 22:09 | 2026-09-30 14:26 | 0 |
| gate_audit/import_integrity_foreign_staged.jsonl | 3969 | 2026-09-09 09:46 | 2026-10-03 09:34 | 3969 |
| gate_audit/library_blood_flesh.jsonl | 23 | 2026-09-22 22:40 | 2026-09-30 23:57 | 23 |
| gate_audit/manual_only_permanent_foreign_staged.jsonl | 4346 | 2026-09-15 18:07 | 2026-10-03 09:34 | 4346 |
| gate_audit/mcp_version_field_foreign_staged.jsonl | 1134 | 2026-09-22 19:29 | 2026-10-03 09:34 | 1134 |
| gate_audit/msg_exposure_foreign_staged.jsonl | 2508 | 2026-09-11 21:55 | 2026-10-03 09:34 | 2508 |
| gate_audit/msg_style_foreign_staged.jsonl | 1081 | 2026-09-22 19:28 | 2026-10-03 09:34 | 1081 |
| gate_audit/new_file_depgraph_foreign_staged.jsonl | 880 | 2026-09-22 19:27 | 2026-10-03 09:34 | 8 |
| gate_audit/no_bare_getenv_foreign_staged.jsonl | 992 | 2026-09-22 19:28 | 2026-10-03 09:34 | 992 |
| gate_audit/no_bare_sql_foreign_staged.jsonl | 4947 | 2026-09-10 15:10 | 2026-10-03 09:32 | 4947 |
| gate_audit/no_domain_name_zh_foreign_staged.jsonl | 1505 | 2026-09-22 19:26 | 2026-10-03 09:32 | 119 |
| gate_audit/no_god_class_foreign_staged.jsonl | 3534 | 2026-09-10 07:07 | 2026-10-01 06:49 | 3534 |
| gate_audit/no_hardcoded_url_foreign_staged.jsonl | 1266 | 2026-09-22 19:28 | 2026-10-03 09:32 | 1266 |
| gate_audit/no_high_complexity_foreign_staged.jsonl | 3613 | 2026-09-10 05:48 | 2026-10-01 06:49 | 3613 |
| gate_audit/no_long_param_list_foreign_staged.jsonl | 792 | 2026-09-23 01:48 | 2026-10-01 06:49 | 792 |
| gate_audit/no_secret_hardcode_foreign_staged.jsonl | 613 | 2026-09-22 19:29 | 2026-10-03 09:34 | 613 |
| gate_audit/no_upward_import_foreign_staged.jsonl | 1527 | 2026-09-22 19:28 | 2026-10-03 09:32 | 1527 |
| gate_audit/noqa_validation_foreign_staged.jsonl | 2683 | 2026-09-11 21:55 | 2026-10-03 09:34 | 2683 |
| gate_audit/obj_s_ai_exposure_forbidden.jsonl | 1 | - | - | 0 |
| gate_audit/obj_s_env_denial.jsonl | 695 | 2026-09-29 19:13 | 2026-10-03 11:40 | 127 |
| gate_audit/open_without_with_foreign_staged.jsonl | 3554 | 2026-09-10 14:07 | 2026-10-03 09:34 | 3554 |
| gate_audit/ops_guard_delete.jsonl | 58047 | 2026-10-02 10:21 | 2026-10-02 13:57 | 995 |
| gate_audit/orphan_module_foreign_staged.jsonl | 778 | 2026-09-22 19:28 | 2026-10-03 09:34 | 778 |
| gate_audit/perm_trigger_foreign_staged.jsonl | 4339 | 2026-09-15 18:07 | 2026-10-03 09:34 | 4339 |
| gate_audit/post_claim_modifications.jsonl | 52478 | 2026-08-08 08:59 | 2026-10-02 21:26 | 0 |
| gate_audit/protected_paths_bypass.jsonl | 901 | 2026-08-03 13:28 | 2026-10-03 04:20 | 901 |
| gate_audit/pure_assertion_foreign_staged.jsonl | 2790 | 2026-09-13 19:16 | 2026-10-03 09:34 | 2790 |
| gate_audit/pure_shim_foreign_staged.jsonl | 1086 | 2026-09-22 19:27 | 2026-10-03 09:34 | 1086 |
| gate_audit/real_key_reference_scan.jsonl | 50 | 2026-09-23 16:55 | 2026-09-26 22:56 | 3 |
| gate_audit/real_key_reference_scan_foreign_staged.jsonl | 907 | 2026-09-23 16:55 | 2026-10-03 09:34 | 12 |
| gate_audit/registry_code_anchor_foreign_staged.jsonl | 445 | 2026-09-22 21:26 | 2026-10-01 12:33 | 445 |
| gate_audit/registry_mass_deletion.jsonl | 1863 | 2026-09-11 17:04 | 2026-10-03 11:40 | 1862 |
| gate_audit/registry_mass_deletion_foreign_staged.jsonl | 10553 | 2026-09-11 15:51 | 2026-10-03 11:39 | 10553 |
| gate_audit/registry_yaml_parse.jsonl | 2138 | 2026-09-13 19:24 | 2026-10-03 11:34 | 2138 |
| gate_audit/relative_path_literal_foreign_staged.jsonl | 1456 | 2026-09-22 19:29 | 2026-10-03 09:32 | 1456 |
| gate_audit/rename_depgraph_sync_foreign_staged.jsonl | 141 | 2026-09-23 08:19 | 2026-10-03 09:34 | 141 |
| gate_audit/safe_rmtree.jsonl | 83114 | 2026-08-26 06:40 | 2026-10-03 04:18 | 9697 |
| gate_audit/scripts_import_integrity_foreign_staged.jsonl | 1621 | 2026-09-10 19:33 | 2026-09-29 13:23 | 1621 |
| gate_audit/secret_registry_consistency_foreign_staged.jsonl | 1133 | 2026-09-22 19:29 | 2026-10-03 09:34 | 1133 |
| gate_audit/ssot_redefinition_foreign_staged.jsonl | 1148 | 2026-09-22 19:27 | 2026-10-03 09:34 | 1148 |
| gate_audit/stale_staged_cleanup.jsonl | 1 | 2026-09-09 17:17 | 2026-09-09 17:17 | 1 |
| gate_audit/state_vocab_registry.jsonl | 4 | 2026-09-27 02:56 | 2026-09-29 21:07 | 4 |
| gate_audit/state_vocab_registry_foreign_staged.jsonl | 806 | 2026-09-21 22:32 | 2026-10-03 09:34 | 806 |
| gate_audit/syntax_validation_foreign_staged.jsonl | 9 | 2026-09-14 10:07 | 2026-09-14 10:21 | 9 |
| gate_audit/tag_vocab.jsonl | 40 | 2026-09-22 23:44 | 2026-09-30 23:01 | 40 |
| gate_audit/task_order_docs_lock_foreign_staged.jsonl | 906 | 2026-09-23 16:55 | 2026-10-03 09:34 | 12 |
| gate_audit/test_residue_ssot_foreign_staged.jsonl | 1104 | 2026-09-22 19:27 | 2026-10-03 09:34 | 1104 |
| gate_audit/test_source_consistency_foreign_staged.jsonl | 8121 | 2026-09-15 18:07 | 2026-10-03 11:39 | 8121 |
| gate_audit/translation_coverage_foreign_staged.jsonl | 895 | 2026-09-22 19:27 | 2026-10-03 09:34 | 895 |
| gate_audit/trust_hold_adoptions.jsonl | 16751 | 2026-09-13 13:19 | 2026-10-03 09:34 | 3 |
| gate_audit/undefined_name_foreign_staged.jsonl | 4165 | 2026-09-10 05:48 | 2026-10-03 09:32 | 4165 |
| gate_audit/unsafe_dict_spread_foreign_staged.jsonl | 4821 | 2026-09-10 15:10 | 2026-10-03 09:32 | 4821 |
| gate_audit/vocab_chain_foreign_staged.jsonl | 705 | 2026-09-22 19:27 | 2026-10-03 09:34 | 705 |
| gate_audit/vocab_hardcode_foreign_staged.jsonl | 701 | 2026-09-22 19:28 | 2026-10-03 09:34 | 701 |
| gate_audit/worktree_abort.jsonl | 201 | 2026-08-14 10:58 | 2026-10-01 02:43 | 1 |
| gate_audit/worktree_skip.jsonl | 41 | 2026-08-03 19:33 | 2026-09-08 12:47 | 0 |
| gate_audit/worktree_status_snapshots.jsonl | 2556 | 2026-08-14 10:55 | 2026-10-02 21:27 | 491 |
| gate_audit/zephyr_env_direct_access_foreign_staged.jsonl | 3553 | 2026-09-10 14:07 | 2026-10-03 09:34 | 3553 |
| gate_execution_stats.jsonl | 2673 | 2026-09-15 18:19 | 2026-10-03 09:34 | 0 |
| hook_tracked_drift.jsonl | 2651 | 2026-08-15 05:49 | 2026-10-01 21:04 | 390 |
| kill_switch_orchestrator.jsonl | 14 | 2026-09-18 13:19 | 2026-09-19 19:45 | 3 |
| killswitch_response_levels.jsonl | 1 | 2026-08-23 21:00 | 2026-08-23 21:00 | 0 |
| landing_guard.jsonl | 1 | 2026-09-26 01:04 | 2026-09-26 01:04 | 0 |
| lock_wait_events.jsonl | 485 | 2026-09-29 06:19 | 2026-10-03 09:34 | 80 |
| precommit_channel_stats.jsonl | 528 | 2026-09-24 14:26 | 2026-10-03 09:34 | 92 |
| preflight_events.jsonl | 7696 | 2026-09-15 18:09 | 2026-10-03 11:40 | 0 |
| safe_write.jsonl | 103624 | 2026-08-23 06:28 | 2026-10-03 11:44 | 18815 |
| worktree_drift_watchdog.jsonl | 29984 | 2026-09-23 06:41 | 2026-10-03 11:38 | 4985 |
| write_audit.jsonl | 12953 | 2026-10-03 04:50 | 2026-10-03 11:46 | 64 |

## 队列侧（.runtime/commit_queue/ 条目计数，纯计数未读内容）
| blobs | 11373 |
| dead | 1249 |
| dead_archive | 1 |
| dead_purged_20260920 | 113 |
| done | 501 |
| hold_st_gov2 | 2 |
| hold_stress_phaseB_20260923 | 1 |
| pending | 1 |
| processing | 0 |
| worktree | 44 |
| worktrees | 4 |
顶层散文件(含 .seq 序号器): 876

## dead 死因 Top20（bottleneck_ledger.jsonl 的 dead_letter，qid 去重=3610 袋，按归一化 reason 首行）
| # | 袋数 | 归一化死因首行 |
|---|---|---|
| 1 | 370 | 网关落盘失败（COMMIT_FAILED）: 门禁 GATE-PRECOMMIT-RUN 阻断: 落地前 pre-commit run 在 staged 面（own-scope 临时索引）发现本提交文件的违规（裁定#34 |
| 2 | 90 | 网关落盘失败（COMMIT_FAILED）: 门禁 TRANSLATION-COVERAGE 阻断: TRANSLATION-COVERAGE: 1 个新建 .py 文件在翻译真源（module_translation_ |
| 3 | 80 | landing 异常: LandingEnvironmentError: landing 环境不可用（repo_root=D:\ZephyrAlpha）: GateAutoRegistrationError: gate  |
| 4 | 76 | 网关落盘失败（COMMIT_FAILED）: 门禁 COMPLEXITY-GUARD 阻断: [NO-HIGH-COMPLEXITY] NO-HIGH-COMPLEXITY：检测到高循环复杂度函数（>15）， |
| 5 | 71 | landing 异常: OSError: [WinError 233] 管道的另一端上无任何进程。 |
| 6 | 62 | landing 异常: RuntimeError: [landing] 注册表三向合并失败（死信回退人工）: docs/01_policies_and_standards/_registry/catalogs/capab |
| 7 | 57 | NOTHING_TO_COMMIT 但快照未真应用 (blob 与 old_dev 不符: ['scripts/governance/meta/rules_integrity_db.json'])——应用静默丢失，死信回 |
| 8 | 48 | 网关落盘失败（COMMIT_FAILED）: 门禁 ALGO-NOTE-SYNC 阻断: ALGO-NOTE-SYNC：1 个节点的实现代码在本 commit 被触碰，但其大白话算法说明未同步——算法改了大白话必须跟着改 |
| 9 | 43 | 网关落盘失败（COMMIT_FAILED）: 门禁 DANGLING-REFERENCE 阻断: 新增 AGENTS.md 悬空引用（DANGLING_REFERENCE_VIOLATION）——以下文件引用了 AGEN |
| 10 | 42 | landing 异常: RuntimeError: [landing] 注册表三向合并失败（死信回退人工）: docs/01_policies_and_standards/_registry/catalogs/modul |
| 11 | 40 | 网关落盘失败（COMMIT_FAILED）: 门禁 IMPORT-INTEGRITY 阻断: IMPORT-INTEGRITY: 悬空 import（目标模块不可解析，#ARCH-CROSS-COMMIT-ATOMICI |
| 12 | 35 | 网关落盘失败（COMMIT_FAILED）: 门禁 DEPGRAPH-ENFORCEMENT 阻断: [NEW-FILE-DEPGRAPH-ENFORCEMENT] NEW-FILE-DEPGRAPH-ENFORCEME |
| 13 | 33 | 网关落盘失败（COMMIT_FAILED）: 门禁 REGISTRY-MASS-DELETION 阻断: REGISTRY-MASS-DELETION: 登记表净删行/条目数减少（<num>-09-09 <num> 行蒸 |
| 14 | 33 | 网关落盘失败（COMMIT_FAILED）: 门禁 PERMANENT-SYSTEM-TRIGGER 阻断: [MANUAL-ONLY-PERMANENT] 永久系统脚本使用 manual 触发模式（argparse/i |
| 15 | 31 | 网关落盘失败（COMMIT_FAILED）: 门禁 TEST-SOURCE-CONSISTENCY 阻断: TEST-SOURCE-CONSISTENCY (§5.178)：检测到测试-源码符号漂移 |
| 16 | 29 | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATHS: staged files contain protected paths (1 hit(s)) |
| 17 | 29 | 网关落盘失败（COMMIT_FAILED）: 门禁 SSOT-REDEFINITION 阻断: SSoT 符号重复定义（硬阻断）： |
| 18 | 28 | 网关落盘失败（COMMIT_FAILED）: 门禁 NO-HIGH-COMPLEXITY 阻断: NO-HIGH-COMPLEXITY：检测到高循环复杂度函数（>15）， |
| 19 | 28 | 网关落盘失败（COMMIT_FAILED）: 门禁 MSG-EXPOSURE 阻断: 错误消息暴露敏感信息（路径/tx_id/凭据/连接串等应放入 details 字段而非消息文本，5.99.20 治本）: script |
| 20 | 27 | 网关落盘失败（COMMIT_FAILED）: 门禁 MUTABLE-CONST-WITHOUT-FINAL 阻断: MUTABLE-CONST-WITHOUT-FINAL：检测到模块级可变常量缺 Final 标注（5.1 |

## 结构化流中无法归属到 182 台的 id（运行时正册 G1/EN_xxx 等另一套 id 体系，两册零交集，供 Owner 参考）
REAL-KEY-REFERENCE-SCAN×874, TASK-ORDER-DOCS-LOCK×864, CONSTITUTION-LINE-LIMIT×864, GATE-PRECOMMIT-RUN×839, QUEUE-LANDING×163, G1×124, FOREIGN-CHANGE×92, TRACKED-DRIFT-READONLY×24, OTHER-GATE×13

## 口径警示（内收判据使用须知）
- commit-gate 通道（93 台）只记"拦截"不记"放行"：零拦截 ≠ 零执行。主表对这类零触发行的备注列已标注，退役前需结合装载面（own_scope/always_run/entry）复核。
- gate_execution_stats 覆盖 pre-commit 通道提交链；feature_flags/write_audit 等流仅作提及面参考。
- 零触发 = 近30天五项结构化证据全 0（提及面不计入；"仅提及无结构化触发"在主表备注列标灰区）；双零 = 零触发 ∧ 全仓零消费者（不含注册册自登记）。
- 更名残留假零已消除：初版按裸 id 口径得 47 台零触发，经包装块归因+孪生核验后收敛为终版名单（零触发 CSV 为准）。
- 双零终版为 0 台：每台零触发门禁至少有 1 处生产引用（装载/文档），退役主张只能以零触发为主证据、逐台核装载面。
- 本班红线遵守：除五件产出表外零写入；.runtime/commit_queue/ 仅目录条目计数。
