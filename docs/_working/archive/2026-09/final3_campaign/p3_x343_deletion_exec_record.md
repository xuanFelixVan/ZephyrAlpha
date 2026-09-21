---
ttl: task_bound
completes_when: P14 终局报告落盘
session: st-maxexec-20260920
issue: MAXEXEC-P3
ruling: "#343 (删除包) + #371 (final3 战役授权)"
date: 2026-09-20
---

# P3 裁定#343 .tmp 残留删除包 执行清单

manifest 真源: `.runtime/tmp/x343_deletion_manifest.txt`（2026-09-19T17:09 生成，A 节 65 件 .tmp）。
执行脚本与实测 JSON: `.runtime/tmp/p3_x343_verify.py` / `p3_x343_execute.py` + `p3_x343_{verify_result,pre_count,delete_results,post_count,gitinternal}.json`。

## 1. 删除前后全仓 .tmp 计数对照（口径同 manifest 头注释：排除 .git/ 与 .worktrees/）

| 时点 | 件数 | 字节 |
|---|---|---|
| 删除前实测（2026-09-20） | 66 | 92146507 |
| manifest 时点（2026-09-19T17:09） | 65 | 92146505 |
| 删除后实测（2026-09-20） | 1 | 2 |

说明：删前实测 66 = manifest 65 + manifest 生成后新生 1 件
（`data/governance/.watchdog_state.json_8fwhpx5k.tmp`，2 字节，mtime 2026-09-20T03:21，watchdog 原子写在途件，
不在裁定#343 清单范围内，未删，待其自清或后续裁定）。
预期剩余 = 66 - 65 = 1，实测剩余 1（即上述 watchdog 件）——吻合。

## 2. 执行结果

- A 节 .tmp：65/65 全部现存、字节数与 manifest 逐件一致、逐件验证未被 git 跟踪（`git ls-files --error-unmatch` 无输出）→ 删除 65/65 成功。
- C 节壳件：`tests/signal_ashare/test_sector_strength_aggregator.py`（0 字节，未跟踪）→ 删除成功。
- 合计删除 66/66，异常 0，漂移 0。

### C 节壳件来历（一句话）

commit `eb1fc5f476`（2026-09-13，refactor(tests): tests/signal_ashare 拆分主体——78 移动对落地）将原 140 行测试
移至 `tests/signal_ashare/sector/test_sector_strength_aggregator.py`（已跟踪、现存 140 行）并删除旧路径跟踪；
旧路径残留的 0 字节未跟踪壳即本次删除件，无内容价值。

### C 节其余 10 件 __init__.py：全部保留（合法空包标记，未删）

## 3. 66 件删除明细（路径 | 字节 | mtime | 结果）

- `.runtime/.probe_24716.tmp` | 0 | 2026-09-19T01:09:49 | DELETED
- `.runtime/.probe_25384.tmp` | 0 | 2026-09-18T04:47:27 | DELETED
- `.runtime/tmp/ff-instL/basetemp_ex_core/popen-gw1/test_heartbeat_write_failure_d0/live_strategy_biz.tmp` | 356 | 2026-09-18T17:29:26 | DELETED
- `.runtime/tmp/ff-instL/bt_excore2/popen-gw3/test_heartbeat_write_failure_d0/live_strategy_biz.tmp` | 357 | 2026-09-18T17:40:15 | DELETED
- `.runtime/tmp/ff-land2-pc-3/test_heartbeat_write_failure_d0/live_strategy_biz.tmp` | 357 | 2026-09-18T19:09:38 | DELETED
- `.runtime/tmp/ff-land3-pc-4/test_heartbeat_write_failure_d0/live_strategy_biz.tmp` | 356 | 2026-09-18T19:55:59 | DELETED
- `.runtime/tmp/ff-recon/loopcheck_bt/close1/bt04xecefc7a5/test_heartbeat_write_failure_d0/live_strategy_biz.tmp` | 357 | 2026-09-19T00:31:34 | DELETED
- `.runtime/tmp/ff-recon/loopcheck_bt/ex_core/test_heartbeat_write_failure_d0/live_strategy_biz.tmp` | 357 | 2026-09-19T00:06:44 | DELETED
- `.runtime/tmp/ff-recon/loopcheck_bt/fflast/bt04xecefc7a5/test_heartbeat_write_failure_d0/live_strategy_biz.tmp` | 357 | 2026-09-19T01:19:59 | DELETED
- `.runtime/tmp/ff-testint/bt_prov/f18/test_write_failure_non_fatal0/tick_subscriber_biz.tmp` | 273 | 2026-09-18T21:07:22 | DELETED
- `.runtime/tmp/lbdeep/test_write_failure_non_fatal0/tick_subscriber_biz.tmp` | 274 | 2026-09-19T08:04:27 | DELETED
- `.runtime/tmp/st-ff-alarm2-20260918/pc8/test_write_failure_non_fatal0/tick_subscriber_biz.tmp` | 273 | 2026-09-18T21:36:55 | DELETED
- `.runtime/tmp/st-ff-alarm2-20260918/pc9/test_write_failure_non_fatal0/tick_subscriber_biz.tmp` | 273 | 2026-09-18T21:39:32 | DELETED
- `.runtime/tmp/st-ff-cold/_h.tmp` | 6262 | 2026-09-18T21:28:30 | DELETED
- `.runtime/tmp/st-ff-cold/_head.tmp` | 19596 | 2026-09-18T21:25:13 | DELETED
- `config/.trading_decision_map.yaml_cq1c71rt.tmp` | 243361 | 2026-09-18T20:05:35 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_16limbv5.tmp` | 1820405 | 2026-09-18T22:43:12 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_23rfylpx.tmp` | 1812911 | 2026-09-18T20:41:25 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_514tsuxc.tmp` | 1805579 | 2026-09-18T19:36:50 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_5uz8wk6p.tmp` | 1845265 | 2026-09-19T12:12:18 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_5wontak3.tmp` | 1839390 | 2026-09-19T04:01:45 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_7dypj_ec.tmp` | 1782222 | 2026-09-18T08:27:38 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_8pucj4uq.tmp` | 1820405 | 2026-09-18T22:43:08 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_8wnm35hd.tmp` | 1839390 | 2026-09-19T04:01:42 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml__dccq8jf.tmp` | 1808234 | 2026-09-18T20:15:30 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_avzr45x6.tmp` | 1820405 | 2026-09-18T22:42:51 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_b7knvm6h.tmp` | 1844524 | 2026-09-19T05:02:56 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_c4mchw81.tmp` | 1809008 | 2026-09-18T20:16:02 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_eb1l8rnz.tmp` | 1805579 | 2026-09-18T19:36:41 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_fag8wv7w.tmp` | 1808804 | 2026-09-18T20:15:51 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_gmcp13hn.tmp` | 1805751 | 2026-09-18T19:37:12 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_h5jg6ydr.tmp` | 1805579 | 2026-09-18T19:36:47 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_hy125usp.tmp` | 1805579 | 2026-09-18T19:36:44 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_i5h2kkoa.tmp` | 1839390 | 2026-09-19T04:01:36 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_khybl7yo.tmp` | 1807826 | 2026-09-18T20:15:14 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_ok_n1_uw.tmp` | 1808590 | 2026-09-18T20:15:43 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_ozgvlts6.tmp` | 1844524 | 2026-09-19T05:02:59 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_phaa503e.tmp` | 1807826 | 2026-09-18T20:15:18 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_q7380lv4.tmp` | 1820405 | 2026-09-18T22:43:16 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_r4b5stv6.tmp` | 1839390 | 2026-09-19T04:01:39 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_tabztnol.tmp` | 1807826 | 2026-09-18T20:15:11 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_tspm1ryb.tmp` | 1822668 | 2026-09-19T02:31:05 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_ukb_dnft.tmp` | 1788503 | 2026-09-18T11:53:47 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_wbjia7z2.tmp` | 1804845 | 2026-09-18T19:35:05 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_wp0h1vsz.tmp` | 1844303 | 2026-09-19T04:58:00 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_y1gj278j.tmp` | 1844303 | 2026-09-19T04:57:57 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_y6np54hs.tmp` | 1809365 | 2026-09-18T20:16:15 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.capability_canonical_file_registry.yaml_yrtlkyaw.tmp` | 1808804 | 2026-09-18T20:15:54 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.module_translation_registry.yaml_28utiyjn.tmp` | 3312403 | 2026-09-18T20:41:48 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.module_translation_registry.yaml_6go3dsfd.tmp` | 3317038 | 2026-09-18T22:15:51 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.module_translation_registry.yaml_dbv1nihw.tmp` | 3312403 | 2026-09-18T20:40:48 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.module_translation_registry.yaml_dpgjep_l.tmp` | 3122217 | 2026-09-18T07:54:06 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.module_translation_registry.yaml_fovoln63.tmp` | 3297990 | 2026-09-18T08:27:13 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.module_translation_registry.yaml_jrs2xjcp.tmp` | 3297596 | 2026-09-18T08:26:45 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.module_translation_registry.yaml_pousix7r.tmp` | 3312403 | 2026-09-18T20:41:45 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.module_translation_registry.yaml_qgpjpwmm.tmp` | 3131167 | 2026-09-18T07:00:36 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.module_translation_registry.yaml_sa8bs6zl.tmp` | 3317846 | 2026-09-19T08:24:15 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.module_translation_registry.yaml_zgwwcqmo.tmp` | 3317008 | 2026-09-18T22:15:59 | DELETED
- `docs/01_policies_and_standards/_registry/catalogs/.ruling_registry.yaml_et0ow618.tmp` | 318290 | 2026-09-19T12:09:17 | DELETED
- `scripts/_archive/governance/d3_metadata/.fix_n06_module_id_prefix.py_6zxjh7_b.tmp` | 17193 | 2026-09-18T07:53:22 | DELETED
- `scripts/ai_layer/.gen_intake_ref_snapshots.py_oceav7ku.tmp` | 10150 | 2026-09-18T22:59:38 | DELETED
- `scripts/governance/.analyze_change_impact_warn_result.json_em2ila3o.tmp` | 530 | 2026-09-19T06:19:29 | DELETED
- `scripts/governance/.governance_watchdog_warn_result.json_mj4n1zkk.tmp` | 746 | 2026-09-17T10:32:41 | DELETED
- `scripts/script-manifest.yaml.18880.tmp` | 304822 | 2026-09-16T23:24:15 | DELETED
- `scripts/script-manifest.yaml.21196.tmp` | 306296 | 2026-09-18T06:43:35 | DELETED
- `tests/signal_ashare/test_sector_strength_aggregator.py` | 0 | 2026-09-18T18:13:34 | DELETED（C 节壳件）

## 4. 漂移件处置

- manifest A 节 65 件：0 缺失、0 字节漂移、0 已跟踪——无漂移件。
- manifest 外新生 1 件：`data/governance/.watchdog_state.json_8fwhpx5k.tmp`（2 字节，mtime 2026-09-20T03:21）。
  处置：不在 #343 清单范围 + 疑似 watchdog 在途原子写临时件 → 未删，单独列报待裁。

## 5. .git 内 86 件 .tmp 判定（只判定，未执行任何删除）

实测 86 件 / 856109 字节，与 manifest 另注（86 件 / 856109 字节）吻合。

| 归属（.git 所属 repo） | 件数 | 字节 | 判定 |
|---|---|---|---|
| `.runtime/tmp/bt_loop1/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/bt_loop1/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/bt_loop1/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/bt_loop1/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/ff-recon/pc_gov/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/ff-recon/pc_gov/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/ff-recon/pc_gov/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/ff-recon/pc_gov/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/lb1r2/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/lb1r2/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/lb1r2/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/lb1r2/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/loop_gov_r1/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/loop_gov_r1/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/loop_gov_r1/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/loop_gov_r1/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/scratchtests/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/final/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/final/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/final/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/final/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/bt/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/bt/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/bt/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/bt/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c00_control_workspace_hooks/bt/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c00_control_workspace_hooks/bt/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c00_control_workspace_hooks/bt/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c00_control_workspace_hooks/bt/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c01_control_HEAD_hooks/bt/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c01_control_HEAD_hooks/bt/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c01_control_HEAD_hooks/bt/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c01_control_HEAD_hooks/bt/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c02_h1_shadow_token_passport/bt/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c02_h1_shadow_token_passport/bt/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c02_h1_shadow_token_passport/bt/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c02_h1_shadow_token_passport/bt/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c02_isolation_reftx_stubbed+workspace_postcommit/bt/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c02_isolation_reftx_stubbed+workspace_postcommit/bt/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c02_isolation_reftx_stubbed+workspace_postcommit/bt/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c02_isolation_reftx_stubbed+workspace_postcommit/bt/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c03_h2_creation_blanket_exemption/bt/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c03_h2_creation_blanket_exemption/bt/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c03_h2_creation_blanket_exemption/bt/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c03_h2_creation_blanket_exemption/bt/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c04_h3_any_gw_marker_passport/bt/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c04_h3_any_gw_marker_passport/bt/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c04_h3_any_gw_marker_passport/bt/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c04_h3_any_gw_marker_passport/bt/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c05_h4_fork_treated_as_rewind/bt/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c05_h4_fork_treated_as_rewind/bt/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c05_h4_fork_treated_as_rewind/bt/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c05_h4_fork_treated_as_rewind/bt/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c07_h1+reftx_stubbed/bt/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c07_h1+reftx_stubbed/bt/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c07_h1+reftx_stubbed/bt/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/hookmut/c07_h1+reftx_stubbed/bt/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/pc3/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/pc3/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/pc3/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/pc3/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/pc4/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/pc4/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/pc4/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/pc4/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/pc8/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/pc8/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/pc8/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/pc8/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/pc9/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/pc9/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/pc9/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-gov2-20260918/pc9/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-rb-gov-20260918/pc4/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-rb-gov-20260918/pc4/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-rb-gov-20260918/pc4/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-rb-gov-20260918/pc5/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-rb-gov-20260918/pc5/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-rb-gov-20260918/pc5/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-rb-gov-20260918/pc5/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-rb-gov-20260918/pc6/test_fork_move_with_forged_sha0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-rb-gov-20260918/pc6/test_plumbing_emergency_marker0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-rb-gov-20260918/pc6/test_plumbing_fast_forward_wit0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-rb-gov-20260918/pc6/test_update_ref_without_old_is0/repo` | 1 | 209 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `.runtime/tmp/st-ff-rb-gov-20260918/scratch/a1repo` | 1 | 425 | 内嵌测试夹具 repo 自有 .git → 该夹具自己的事，不动 |
| `<主仓 D:\ZephyrAlpha/.git>` | 1 | 838128 | 主仓 git 内部件（emergency_index 紧急提交临时索引）→ 一律不动 |

明细特征：85 件内嵌件几乎全为 `repo/.git/t_index.tmp`（209 字节/件，plumbing/emergency 红蓝对抗测试夹具
test_fork_move_with_forged_sha0 / test_plumbing_emergency_marker0 / test_plumbing_fast_forward_wit0 /
test_update_ref_without_old_is0 残留）+ 1 件 `scratch/a1repo/.git/atk_index.tmp`（425 字节）；
主仓 1 件 `.git/emergency_index_mf61gn5t.tmp`（838128 字节）。全量路径见 `.runtime/tmp/p3_x343_gitinternal.json`。

## 6. 红证

- 删除后复扫全仓 .tmp（排除 .git/.worktrees）：1 件 / 2 字节，
  与预期剩余（1 件新生 watchdog 件）一致——裁定#343 清单内 65 件 .tmp 已零残留。
- 逐件删除结果记录：`.runtime/tmp/p3_x343_delete_results.json`（66 条 DELETED）。
- 删除件全部未跟踪，git 工作区不产生删除差异（`git status` 无 66 件相关条目）。

## 7. 提交

- 本清单 md 单件走正门 `scripts/git_commit.py`（队列模式）。
- token 登记：`batch_creation_tokens.py --prefix docs/_working/final3_campaign` 幂等通过。
