---
ttl: task_bound
completes_when: 138待裁Owner批复+24认领收敛后转归档
title: F8 孤儿草稿分诊报告
sid: st-f8-orphan-20261004
generated: 2026-10-04T03:02:23
input: docs/_working/commitmap_cure/05_workspace_wip_manifest.yaml
scope: fresh_change_left(28)+derived_sync_left(107)+untracked_new_left(82)=217件
forbidden: stale_not_in_history_do_not_touch 893件全程未触碰未判定(总筹死信抢救人群,永不自动销账)
disposition: 认领建议=HEAD已有等值/超集内容零损失清障；待归档=明显过期战役残件；待裁=机械判据无法定夺
---

# F8 孤儿草稿分诊报告（st-f8-orphan-20261004）

> 纯只读批：本报告为唯一写动作（任务指令显式指定主区输出路径，降级直改理由=零提交只读+claim/release 纪律覆盖）。
判定权归总筹。

## 0. 结论速览

| 输入类别 | 认领建议 | 待归档 | 待裁 | 小计 |
|---|---:|---:|---:|---:|
| fresh_change(28) | 24 | 0 | 4 | 28 |
| derived_sync(107) | 19 | 0 | 88 | 107 |
| untracked_new(82) | 3 | 33 | 46 | 82 |
| **合计** | **46** | **33** | **138** | **217** |

机械实勘修正两条口径（对 05 清单分类的落盘形态）：

- fresh_change(28) 全部=**主区暂存删除**（porcelain `D `，文件仍在 dev HEAD 树）；其草稿=删除动作本身。
- derived_sync(107) 中 48 台=**主区暂存新增**（porcelain `A `，HEAD 无此路径）；其余 59 台=主区已跟踪文件的未暂存修改（机生文档再生成）。
- 二遍 worktree 宿主排查：76 件无主区踪迹候选在全部 28 个注册 worktree 中**零宿主**（无任何 worktree 持有未提交变体），worktree 假说排除，孤儿面收敛于主区 index。

## 1. 机械判据与复算命令

每条判定均可按下表命令复算，无肉眼判罚：

| 判定 | 机械判据 | 复算命令 |
|---|---|---|
| 暂存删除孪生 | HEAD 侧 blob 同内容存在于他径（改名/迁移已落地） | `git ls-tree -r HEAD \| grep <blob>` |
| HEAD等值 | 工作区/暂存 blob == HEAD blob | `git diff --quiet HEAD -- <路径>` |
| HEAD超集 | 相对HEAD仅删行(+0/-N) | `git diff --numstat HEAD -- <路径>` |
| 重排等值 | 新增行≥90%逐行存在于HEAD blob | `git diff -U0 HEAD -- <路径>` |
| 机生时戳漂移 | 新增行去数字归一后≥90%存在于HEAD | 同上+归一对比 |
| CRLF幻影 | `--ignore-cr-at-eol`下零差异 | `git diff --ignore-cr-at-eol HEAD -- <路径>` |
| 暂存新增等值 | index blob 命中 HEAD 树任意路径 | `git ls-tree -r HEAD \| grep $(git rev-parse :<路径>)` |
| 同名等值 | HEAD 同名文件行覆盖≥90% | `git show HEAD:<同名路径>` 比对 |
| blob史 | 精确blob曾入任意引用历史 | `git log --all --no-renames --find-object=<blob>` |
| 过期残件 | 名称内嵌日期≤2026-09-30 的 grid 跑批/原子写 .tmp 残件/session_logs/临时区 | `ls`+名称正则 |
| 活跃claim | .ailocks/registry.json expires_at>now | `cat .ailocks/registry.json` |

## 2. 逐件表·fresh_change_left（28，全部=主区暂存删除）

| # | 路径 | 判定 | 依据 | 证据 |
|---|---|---|---|---|
| 1 | `scripts/check_coverage.ps1` | 认领建议 | HEAD已有等值内容@scripts/_archive/ops/check_coverage.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=d21f822db8f7)；blob孪生@scripts/_archive/ops/check_coverage.ps1, scripts/checks/check_coverage.ps1；尾提交=d5348f700b6(2026-08-18,chore(scripts): AI-AUDIT20-001 审计域治本——①scrip) |
| 2 | `scripts/check_coverage2.ps1` | 认领建议 | HEAD已有等值内容@scripts/_archive/ops/check_coverage2.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=b4efe714af05)；blob孪生@scripts/_archive/ops/check_coverage2.ps1, scripts/checks/check_coverage2.ps1；尾提交=d5348f700b6(2026-08-18,chore(scripts): AI-AUDIT20-001 审计域治本——①scrip) |
| 3 | `scripts/check_risk_memos.ps1` | 认领建议 | HEAD已有等值内容@scripts/checks/check_risk_memos.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=8d80408d72db)；blob孪生@scripts/checks/check_risk_memos.ps1；尾提交=d5348f700b6(2026-08-18,chore(scripts): AI-AUDIT20-001 审计域治本——①scrip) |
| 4 | `scripts/check_risk_memos2.ps1` | 认领建议 | HEAD已有等值内容@scripts/checks/check_risk_memos2.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=975d9e7dd794)；blob孪生@scripts/checks/check_risk_memos2.ps1；尾提交=d5348f700b6(2026-08-18,chore(scripts): AI-AUDIT20-001 审计域治本——①scrip) |
| 5 | `scripts/check_specific_versions.ps1` | 认领建议 | HEAD已有等值内容@scripts/_archive/ops/check_specific_versions.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=41957a008ae2)；blob孪生@scripts/_archive/ops/check_specific_versions.ps1, scripts/checks/check_specific_versions.ps1；尾提交=81c76875403(2026-08-11,feat: position/pf_alloc核心模块骨架→production + e) |
| 6 | `scripts/check_version_drift.ps1` | 认领建议 | HEAD已有等值内容@scripts/_archive/check_version_drift.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=1afb9fa63941)；blob孪生@scripts/_archive/check_version_drift.ps1, scripts/_archive/ops/check_version_drift.ps1；尾提交=81c76875403(2026-08-11,feat: position/pf_alloc核心模块骨架→production + e) |
| 7 | `scripts/check_version_drift_v2.ps1` | 认领建议 | HEAD已有等值内容@scripts/_archive/ops/check_version_drift_v2.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=45a53d9a52f9)；blob孪生@scripts/_archive/ops/check_version_drift_v2.ps1, scripts/checks/check_version_drift_v2.ps1；尾提交=d5348f700b6(2026-08-18,chore(scripts): AI-AUDIT20-001 审计域治本——①scrip) |
| 8 | `scripts/ensure_ai_wrapper_injection.ps1` | 待裁 | 同名他径@scripts/installers/ensure_ai_wrapper_injection.ps1仅覆盖0.58,非等值非超集,删除意图须裁 | porcelain=D ；暂存删除(HEAD侧blob=4e7039813628)；HEAD无blob孪生(内容HEAD独有)；跨径同名@scripts/installers/ensure_ai_wrapper_injection.ps1 旧行覆盖=0.58；尾提交=c79de22c0d7(2026-08-15,[no-lookup:continuation] tracker #58 close: ) |
| 9 | `scripts/find_35_sections.ps1` | 认领建议 | HEAD已有等值内容@scripts/_archive/find_35_sections.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=54c79dc2f66c)；blob孪生@scripts/_archive/find_35_sections.ps1；尾提交=d5348f700b6(2026-08-18,chore(scripts): AI-AUDIT20-001 审计域治本——①scrip) |
| 10 | `scripts/find_55_last_rev.ps1` | 认领建议 | HEAD已有等值内容@scripts/_archive/find_55_last_rev.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=0253462d4d4a)；blob孪生@scripts/_archive/find_55_last_rev.ps1；尾提交=81c76875403(2026-08-11,feat: position/pf_alloc核心模块骨架→production + e) |
| 11 | `scripts/find_insert_points.ps1` | 认领建议 | HEAD已有等值内容@scripts/_archive/find_insert_points.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=0fe28bb2fc8c)；blob孪生@scripts/_archive/find_insert_points.ps1；尾提交=d5348f700b6(2026-08-18,chore(scripts): AI-AUDIT20-001 审计域治本——①scrip) |
| 12 | `scripts/fix_all_drifts_v3.ps1` | 认领建议 | HEAD已有等值内容@scripts/_archive/fix_all_drifts_v3.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=2a94fe211a37)；blob孪生@scripts/_archive/fix_all_drifts_v3.ps1；尾提交=d5348f700b6(2026-08-18,chore(scripts): AI-AUDIT20-001 审计域治本——①scrip) |
| 13 | `scripts/fix_structured_drifts.ps1` | 认领建议 | HEAD已有等值内容@scripts/_archive/fix_structured_drifts.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=fc32df9e060f)；blob孪生@scripts/_archive/fix_structured_drifts.ps1；尾提交=d5348f700b6(2026-08-18,chore(scripts): AI-AUDIT20-001 审计域治本——①scrip) |
| 14 | `scripts/fix_structured_drifts_v2.ps1` | 认领建议 | HEAD已有等值内容@scripts/_archive/fix_structured_drifts_v2.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=2db1eb940489)；blob孪生@scripts/_archive/fix_structured_drifts_v2.ps1；尾提交=d5348f700b6(2026-08-18,chore(scripts): AI-AUDIT20-001 审计域治本——①scrip) |
| 15 | `scripts/list_all_memos.ps1` | 认领建议 | HEAD已有等值内容@scripts/_archive/list_all_memos.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=9a0e898acfc4)；blob孪生@scripts/_archive/list_all_memos.ps1；尾提交=81c76875403(2026-08-11,feat: position/pf_alloc核心模块骨架→production + e) |
| 16 | `scripts/list_versions.ps1` | 认领建议 | HEAD已有等值内容@scripts/_archive/list_versions.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=99690e278a9b)；blob孪生@scripts/_archive/list_versions.ps1；尾提交=81c76875403(2026-08-11,feat: position/pf_alloc核心模块骨架→production + e) |
| 17 | `scripts/run_boot_sla_probe.py` | 待裁 | 同名他径@scripts/tasks/run/run_boot_sla_probe.py仅覆盖0.20,非等值非超集,删除意图须裁 | porcelain=D ；暂存删除(HEAD侧blob=8a35d35a621f)；HEAD无blob孪生(内容HEAD独有)；跨径同名@scripts/tasks/run/run_boot_sla_probe.py 旧行覆盖=0.20；尾提交=69069b9ab43(2026-09-02,style: ruff format 全量一次性成型 CAND-GOVTEST-002 ) |
| 18 | `scripts/run_c4_exam.ps1` | 认领建议 | HEAD已有等值内容@scripts/tasks/run/run_c4_exam.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=8d5bf457fbfe)；blob孪生@scripts/tasks/run/run_c4_exam.ps1；尾提交=395603e3559(2026-09-15,fix(backtest): OneShot ignition ps1 PS5.1 st) |
| 19 | `scripts/run_f06_grid.ps1` | 认领建议 | HEAD已有等值内容@scripts/tasks/run/run_f06_grid.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=bbfe15f2285a)；blob孪生@scripts/tasks/run/run_f06_grid.ps1；尾提交=4ea29d816f7(2026-09-17,feat(factory): F-06 收官三件——幸存者候选面落库+端到端 e2e 测) |
| 20 | `scripts/run_factory_lane_c.ps1` | 认领建议 | HEAD已有等值内容@scripts/tasks/run/run_factory_lane_c.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=bc50ce6ec868)；blob孪生@scripts/tasks/run/run_factory_lane_c.ps1；尾提交=ac52365d3be(2026-10-01,[st-lanech-20261001][车道C病链夜战·总落地袋v3·API直调 ba) |
| 21 | `scripts/run_ttl_rejudge_daily.ps1` | 认领建议 | HEAD已有等值内容@scripts/tasks/run/run_ttl_rejudge_daily.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=5ac89b3ce85e)；blob孪生@scripts/tasks/run/run_ttl_rejudge_daily.ps1；尾提交=75aae01b11b(2026-09-08,fix(data): P0-1 桥切换持久化 + #BRIDGE-WRONG-FILE ) |
| 22 | `scripts/scan_algo_gaps.ps1` | 认领建议 | HEAD已有等值内容@scripts/_archive/scan_algo_gaps.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=7157b3189a33)；blob孪生@scripts/_archive/scan_algo_gaps.ps1；尾提交=d5348f700b6(2026-08-18,chore(scripts): AI-AUDIT20-001 审计域治本——①scrip) |
| 23 | `scripts/search_31.ps1` | 认领建议 | HEAD已有等值内容@scripts/_archive/search_31.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=5f6f3cd13566)；blob孪生@scripts/_archive/search_31.ps1；尾提交=81c76875403(2026-08-11,feat: position/pf_alloc核心模块骨架→production + e) |
| 24 | `scripts/search_40_passive.ps1` | 认领建议 | HEAD已有等值内容@scripts/_archive/search_40_passive.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=cafd385164be)；blob孪生@scripts/_archive/search_40_passive.ps1；尾提交=d5348f700b6(2026-08-18,chore(scripts): AI-AUDIT20-001 审计域治本——①scrip) |
| 25 | `scripts/search_barzykin.ps1` | 认领建议 | HEAD已有等值内容@scripts/_archive/search_barzykin.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=367700bceed2)；blob孪生@scripts/_archive/search_barzykin.ps1；尾提交=d5348f700b6(2026-08-18,chore(scripts): AI-AUDIT20-001 审计域治本——①scrip) |
| 26 | `scripts/verify_zero_drift.ps1` | 认领建议 | HEAD已有等值内容@scripts/_archive/verify_zero_drift.ps1(暂存删除=迁移收尾,提交即零损失收敛) | porcelain=D ；暂存删除(HEAD侧blob=893150abc705)；blob孪生@scripts/_archive/verify_zero_drift.ps1；尾提交=d5348f700b6(2026-08-18,chore(scripts): AI-AUDIT20-001 审计域治本——①scrip) |
| 27 | `src/zephyr/data_eng/quality_sla_breach_predictor.py` | 待裁 | 暂存删除HEAD独有内容(无孪生无同名),删除意图须总筹确认 | porcelain=D ；暂存删除(HEAD侧blob=e22fab1388ba)；HEAD无blob孪生(内容HEAD独有)；尾提交=28618d0a569(2026-09-16,feat(algo-flow): P2-1 出仓波次 grp3 part1/2——480)；家族=SLA预测家族(src+test成对暂存删除) |
| 28 | `tests/data_eng/test_quality_sla_breach_predictor.py` | 待裁 | 暂存删除HEAD独有内容(无孪生无同名),删除意图须总筹确认 | porcelain=D ；暂存删除(HEAD侧blob=852dbf662007)；HEAD无blob孪生(内容HEAD独有)；尾提交=70beb0f7423(2026-09-19,chore(headers): [总包/WP14 续工三] infrastructure)；家族=SLA预测家族(src+test成对暂存删除) |

## 3. 逐件表·derived_sync_left（107）

| # | 路径 | 判定 | 依据 | 证据 |
|---|---|---|---|---|
| 1 | `docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md` | 认领建议 | HEAD等值(机生时戳类漂移,去数字归一覆盖1.00) | porcelain=M_docs/03_；diff=+3/-3；新增行HEAD覆盖=0.00；novel:version: "6.0.18"；novel:/ 依赖图 (depgraph) / `blueprint_id=MOD-INF-035` 的 79；尾提交=db88f03eda1(2026-09-17,Merge branch 'ai/st-ledgerp2a-20260916/task-)；mtime=2026-10-04 02:45 |
| 2 | `docs/03_modules/_cross_layer/clone_guard/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.67),价值无法机械判 | porcelain=M_docs/03_；diff=+6/-5；新增行HEAD覆盖=0.00；去数字归一覆盖=0.67；novel:version: "0.1.8"；novel:> module_id: MOD-CLONE_GUARD / version: 0.1.8 / st；尾提交=990ae93f777(2026-09-20,chore(reconciler): batched auto-commit (2 re)；mtime=2026-10-03  |
| 3 | `docs/03_modules/_cross_layer/gate_engine/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.13),价值无法机械判 | porcelain=M_docs/03_；diff=+15/-4；新增行HEAD覆盖=0.00；去数字归一覆盖=0.13；novel:version: "0.8.48"；novel:/ `commit_gates/_capability_registry_io.py` / §0.1；尾提交=a2881d059e5(2026-09-29,chore(reconciler): batched auto-commit (7 re)；mtime=2026-10-0 |
| 4 | `docs/03_modules/_cross_layer/model_profiler/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.00),价值无法机械判 | porcelain=M_docs/03_；diff=+2/-2；新增行HEAD覆盖=0.00；去数字归一覆盖=0.00；novel:build_status: generated；novel:/ build_status / generated / generated / ✅ /；尾提交=ff38b1964c7(2026-09-21,[workclean][W8-r2-G4v3] 改链净版三发（本地预扫 ABS 危险命令)；mtime=2026-10-03 |
| 5 | `docs/03_modules/_cross_layer/red_blue_validator/blueprint.md` | 认领建议 | HEAD等值(机生时戳类漂移,去数字归一覆盖1.00) | porcelain=M_docs/03_；diff=+1/-1；新增行HEAD覆盖=0.00；novel:version: "2.2.9"；尾提交=b93e2ab4013(2026-09-17,chore(derived): watchdog 派生缓存自动收敛——B类白名单稳定漂移)；mtime=2026-10-03 23:56 |
| 6 | `docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md` | 认领建议 | HEAD等值(机生时戳类漂移,去数字归一覆盖1.00) | porcelain=M_docs/03_；diff=+2/-2；新增行HEAD覆盖=0.00；novel:/ 依赖图 (depgraph) / `blueprint_id=MOD-RESOURCE_OPTI；novel:/ file_count / 7 文件 / 13 文件（§0.1） / ❌ /；尾提交=b93e2ab4013(2026-09-17,chore(derived): watchdog 派生缓存自动收敛——B类白名单稳定漂移)；mtime=2 |
| 7 | `docs/03_modules/_cross_layer/shared_core/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.60),价值无法机械判 | porcelain=M_docs/03_；diff=+5/-4；新增行HEAD覆盖=0.00；去数字归一覆盖=0.60；novel:version: "0.19.34"；novel:/ 依赖图 (depgraph) / `blueprint_id=MOD-INF-016` 的 35；尾提交=a2881d059e5(2026-09-29,chore(reconciler): batched auto-commit (7 re)；mtime=2026-10-0 |
| 8 | `docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.00),价值无法机械判 | porcelain=M_docs/03_；diff=+3/-3；新增行HEAD覆盖=0.00；去数字归一覆盖=0.00；novel:build_status: stable；novel:/ 数据流图 (dataflow) / （无节点） / N/A / `apply_dataflowg；尾提交=990ae93f777(2026-09-20,chore(reconciler): batched auto-commit (2 re)；mtime=2026-10 |
| 9 | `docs/03_modules/_domain_backtest/decay_monitor/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.33),价值无法机械判 | porcelain=M_docs/03_；diff=+3/-3；新增行HEAD覆盖=0.00；去数字归一覆盖=0.33；novel:build_status: stable；novel:/ 数据流图 (dataflow) / 1 个 Dataset / 1 个 Job / planne；尾提交=990ae93f777(2026-09-20,chore(reconciler): batched auto-commit (2 re)；mtime=2026-10 |
| 10 | `docs/03_modules/_domain_compliance/compliance_report_registry/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.67),价值无法机械判 | porcelain=M_docs/03_；diff=+3/-3；新增行HEAD覆盖=0.00；去数字归一覆盖=0.67；novel:/ 依赖图 (depgraph) / `blueprint_id=MOD-CMP-009` 的 2 ；novel:/ 数据流图 (dataflow) / （无节点） / N/A / `apply_dataflowg；尾提交=a2881d059e5(2026-09-29,chore(reconciler): batched au |
| 11 | `docs/03_modules/_domain_compliance/discipline_prohibition_checker/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.67),价值无法机械判 | porcelain=M_docs/03_；diff=+3/-3；新增行HEAD覆盖=0.00；去数字归一覆盖=0.67；novel:/ 依赖图 (depgraph) / `blueprint_id=MOD-CMP-002` 的 2 ；novel:/ 数据流图 (dataflow) / （无节点） / N/A / `apply_dataflowg；尾提交=a2881d059e5(2026-09-29,chore(reconciler): batched au |
| 12 | `docs/03_modules/_domain_data/algo_flow/sector_line/index.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；HEAD同名@docs/_working/archive/2026-09/wyf3/index.md 行覆盖=0.44；mtime=2026-10-03 23:56 |
| 13 | `docs/03_modules/_domain_data/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.67),价值无法机械判 | porcelain=M_docs/03_；diff=+3/-3；新增行HEAD覆盖=0.00；去数字归一覆盖=0.67；novel:/ 依赖图 (depgraph) / `blueprint_id=MOD-L00-001` 的 21；novel:/ 数据流图 (dataflow) / （无节点） / N/A / `apply_dataflowg；尾提交=990ae93f777(2026-09-20,chore(reconciler): batched au |
| 14 | `docs/03_modules/_domain_data/boot_autostart_architecture.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.13),价值无法机械判 | porcelain=M_docs/03_；diff=+15/-15；新增行HEAD覆盖=0.00；去数字归一覆盖=0.13；novel:/ Data Scheduler / `ZephyrAlpha_DataScheduler` / A；novel:/ Tick Subscriber / `ZephyrAlpha_TickSubscriber` /；尾提交=c199d30576e(2026-09-20,chore(reconciler): batched  |
| 15 | `docs/03_modules/_domain_data/transport/blueprint.md` | 认领建议 | HEAD已有等值内容,零损失清障 | blob等值=c215dbd218a6；尾提交=ff38b1964c7(2026-09-21,[workclean][W8-r2-G4v3] 改链净版三发（本地预扫 ABS 危险命令)；mtime=2026-10-03 23:56 |
| 16 | `docs/03_modules/_domain_data_security/data_access_auditor/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.00),价值无法机械判 | porcelain=M_docs/03_；diff=+1/-1；新增行HEAD覆盖=0.00；去数字归一覆盖=0.00；novel:数据访问审计：CH/SQLite/Parquet/File(本地文件桥，F128 接线 2026-0；尾提交=6621be45592(2026-08-26,feat(shared,data,data_eng,data_governance,da)；mtime=2026-10-03 23:56 |
| 17 | `docs/03_modules/_domain_execution_core/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.40),价值无法机械判 | porcelain=M_docs/03_；diff=+10/-4；新增行HEAD覆盖=0.00；去数字归一覆盖=0.40；novel:version: "2.2.27"；novel:/ 依赖图 (depgraph) / `blueprint_id=MOD-L06-001` 的 76；尾提交=a2881d059e5(2026-09-29,chore(reconciler): batched auto-commit (7 re)；mtime=2026-10-0 |
| 18 | `docs/03_modules/_domain_execution_core/order_execution_saga/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.50),价值无法机械判 | porcelain=M_docs/03_；diff=+6/-4；新增行HEAD覆盖=0.00；去数字归一覆盖=0.50；novel:version: "0.1.10"；novel:/ 依赖图 (depgraph) / `blueprint_id=MOD-EX-057` 的 6 个；尾提交=990ae93f777(2026-09-20,chore(reconciler): batched auto-commit (2 re)；mtime=2026-10-03 |
| 19 | `docs/03_modules/_domain_factor/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.50),价值无法机械判 | porcelain=M_docs/03_；diff=+6/-5；新增行HEAD覆盖=0.00；去数字归一覆盖=0.50；novel:version: "4.0.26"；novel:build_status: generated；尾提交=990ae93f777(2026-09-20,chore(reconciler): batched auto-commit (2 re)；mtime=2026-10-04 02:45 |
| 20 | `docs/03_modules/_domain_frontend/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.80),价值无法机械判 | porcelain=M_docs/03_；diff=+5/-4；新增行HEAD覆盖=0.00；去数字归一覆盖=0.80；novel:version: "3.4.14"；novel:> module_id: MOD-L08-001 / version: 3.4.14 / statu；尾提交=db88f03eda1(2026-09-17,Merge branch 'ai/st-ledgerp2a-20260916/task-)；mtime=2026-10-03 |
| 21 | `docs/03_modules/_domain_governance/audit_trail/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.67),价值无法机械判 | porcelain=M_docs/03_；diff=+6/-5；新增行HEAD覆盖=0.00；去数字归一覆盖=0.67；novel:version: "2.1.18"；novel:> module_id: MOD-INF-020 / version: 2.1.18 / statu；尾提交=990ae93f777(2026-09-20,chore(reconciler): batched auto-commit (2 re)；mtime=2026-10-03 |
| 22 | `docs/03_modules/_domain_governance/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.22),价值无法机械判 | porcelain=M_docs/03_；diff=+9/-4；新增行HEAD覆盖=0.00；去数字归一覆盖=0.22；novel:version: "0.13.23"；novel:/ 依赖图 (depgraph) / `blueprint_id=MOD-GOVERNANCE` 的；尾提交=a2881d059e5(2026-09-29,chore(reconciler): batched auto-commit (7 re)；mtime=2026-10-0 |
| 23 | `docs/03_modules/_domain_governance/governance_automation/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.25),价值无法机械判 | porcelain=M_docs/03_；diff=+8/-4；新增行HEAD覆盖=0.00；去数字归一覆盖=0.25；novel:version: 5.5.37；novel:/ 依赖图 (depgraph) / `blueprint_id=MOD-INF-005` 的 52；尾提交=a2881d059e5(2026-09-29,chore(reconciler): batched auto-commit (7 re)；mtime=2026-10-03 2 |
| 24 | `docs/03_modules/_domain_governance/registry_governance/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.60),价值无法机械判 | porcelain=M_docs/03_；diff=+5/-3；新增行HEAD覆盖=0.00；去数字归一覆盖=0.60；novel:version: "0.2.15"；novel:/ 依赖图 (depgraph) / `blueprint_id=MOD-INF-037` 的 21；尾提交=a2881d059e5(2026-09-29,chore(reconciler): batched auto-commit (7 re)；mtime=2026-10-03 |
| 25 | `docs/03_modules/_domain_infrastructure_operations/asset_inventory/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.00),价值无法机械判 | porcelain=M_docs/03_；diff=+1/-1；新增行HEAD覆盖=0.00；去数字归一覆盖=0.00；novel:/ 数据流图 (dataflow) / （无节点） / N/A / `apply_dataflowg；尾提交=7f9de37b2af(2026-09-29,[st-nightclean-20260929][G1自裁批·trae_034余指针] )；mtime=2026-10-03 23:56 |
| 26 | `docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/backup_inventory.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.67),价值无法机械判 | porcelain=M_docs/03_；diff=+3/-3；新增行HEAD覆盖=0.00；去数字归一覆盖=0.67；novel:/ 依赖图 (depgraph) / `blueprint_id=MOD-INF-043` 的 22；novel:/ 数据流图 (dataflow) / （无节点） / N/A / `apply_dataflowg；尾提交=990ae93f777(2026-09-20,chore(reconciler): batched au |
| 27 | `docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.67),价值无法机械判 | porcelain=M_docs/03_；diff=+3/-2；新增行HEAD覆盖=0.00；去数字归一覆盖=0.67；novel:version: "2.0.8"；novel:> module_id: MOD-INF-043 / version: 2.0.8 / status；尾提交=a2881d059e5(2026-09-29,chore(reconciler): batched auto-commit (7 re)；mtime=2026-10-03  |
| 28 | `docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.75),价值无法机械判 | porcelain=M_docs/03_；diff=+4/-4；新增行HEAD覆盖=0.00；去数字归一覆盖=0.75；novel:version: 6.1.22；novel:design_maturity: production；尾提交=a2881d059e5(2026-09-29,chore(reconciler): batched auto-commit (7 re)；mtime=2026-10-04 02:45 |
| 29 | `docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.67),价值无法机械判 | porcelain=M_docs/03_；diff=+3/-3；新增行HEAD覆盖=0.00；去数字归一覆盖=0.67；novel:/ 依赖图 (depgraph) / `blueprint_id=MOD-TASK_SYSTEM` ；novel:/ 数据流图 (dataflow) / （无节点） / N/A / `apply_dataflowg；尾提交=990ae93f777(2026-09-20,chore(reconciler): batched au |
| 30 | `docs/03_modules/_domain_library/blueprint.md` | 认领建议 | HEAD等值(机生时戳类漂移,去数字归一覆盖1.00) | porcelain=M_docs/03_；diff=+2/-2；新增行HEAD覆盖=0.00；novel:/ 依赖图 (depgraph) / `blueprint_id=MOD-LIB-001` 的 8 ；novel:/ file_count / 8 文件 / N/A / — /；尾提交=6f17ba47b90(2026-09-28,[chiefzc-sx1r5-dispatch-20260928][总包代投·重投v5])；mtime=2026-10-0 |
| 31 | `docs/03_modules/_domain_pf_alloc/batched_position_builder/blueprint.md` | 认领建议 | HEAD已有等值内容,零损失清障 | blob等值=68dc2cff4493；尾提交=ff38b1964c7(2026-09-21,[workclean][W8-r2-G4v3] 改链净版三发（本地预扫 ABS 危险命令)；mtime=2026-10-03 23:56 |
| 32 | `docs/03_modules/_domain_plan_engine/closing_session_decision/blueprint.md` | 认领建议 | HEAD已有等值内容,零损失清障 | blob等值=420494bf94f6；尾提交=ff38b1964c7(2026-09-21,[workclean][W8-r2-G4v3] 改链净版三发（本地预扫 ABS 危险命令)；mtime=2026-10-03 23:56 |
| 33 | `docs/03_modules/_domain_plan_engine/premarket_constraint_loader/blueprint.md` | 认领建议 | HEAD已有等值内容,零损失清障 | blob等值=ab6edd3af599；尾提交=ff38b1964c7(2026-09-21,[workclean][W8-r2-G4v3] 改链净版三发（本地预扫 ABS 危险命令)；mtime=2026-10-03 23:56 |
| 34 | `docs/03_modules/_domain_plan_engine/tomorrow_boundary_planner/blueprint.md` | 认领建议 | HEAD已有等值内容,零损失清障 | blob等值=993d2bbf416e；尾提交=ff38b1964c7(2026-09-21,[workclean][W8-r2-G4v3] 改链净版三发（本地预扫 ABS 危险命令)；mtime=2026-10-03 23:56 |
| 35 | `docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md` | 认领建议 | HEAD已有等值内容,零损失清障 | blob等值=848233557cfe；尾提交=ff38b1964c7(2026-09-21,[workclean][W8-r2-G4v3] 改链净版三发（本地预扫 ABS 危险命令)；mtime=2026-10-03 23:56 |
| 36 | `docs/03_modules/_domain_portfolio_core/msprt_champion_challenger/blueprint.md` | 认领建议 | HEAD已有等值内容,零损失清障 | blob等值=9d2f8cc427a8；尾提交=ff38b1964c7(2026-09-21,[workclean][W8-r2-G4v3] 改链净版三发（本地预扫 ABS 危险命令)；mtime=2026-10-03 23:56 |
| 37 | `docs/03_modules/_domain_portfolio_core/performance_attribution_engine/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.67),价值无法机械判 | porcelain=M_docs/03_；diff=+3/-3；新增行HEAD覆盖=0.00；去数字归一覆盖=0.67；novel:/ 依赖图 (depgraph) / `blueprint_id=MOD-PF-007` 的 2 个；novel:/ 数据流图 (dataflow) / （无节点） / N/A / `apply_dataflowg；尾提交=a2881d059e5(2026-09-29,chore(reconciler): batched au |
| 38 | `docs/03_modules/_domain_position/budget_change_handler/blueprint.md` | 认领建议 | HEAD已有等值内容,零损失清障 | blob等值=c8a42ca235b1；尾提交=ff38b1964c7(2026-09-21,[workclean][W8-r2-G4v3] 改链净版三发（本地预扫 ABS 危险命令)；mtime=2026-10-03 23:56 |
| 39 | `docs/03_modules/_domain_position/firm_risk_aggregator/blueprint.md` | 认领建议 | HEAD已有等值内容,零损失清障 | blob等值=3ae13321fe21；尾提交=ff38b1964c7(2026-09-21,[workclean][W8-r2-G4v3] 改链净版三发（本地预扫 ABS 危险命令)；mtime=2026-10-03 23:56 |
| 40 | `docs/03_modules/_domain_position/position_checkup_orchestrator/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.00),价值无法机械判 | porcelain=M_docs/03_；diff=+63/-0；新增行HEAD覆盖=0.00；去数字归一覆盖=0.00；novel:responsibility_domain:；novel:## 1. 已实现代码完整路径索引；尾提交=1913eb81320(2026-09-30,[F42-G42-1][st-c9-f42] P1 持仓体检棒新件（MOD-POS-03)；mtime=2026-10-03 23:56 |
| 41 | `docs/03_modules/_domain_position/strategy_book/blueprint.md` | 认领建议 | HEAD已有等值内容,零损失清障 | blob等值=641d400d964d；尾提交=ff38b1964c7(2026-09-21,[workclean][W8-r2-G4v3] 改链净版三发（本地预扫 ABS 危险命令)；mtime=2026-10-03 23:56 |
| 42 | `docs/03_modules/_domain_regime/regime_detector/blueprint.md` | 认领建议 | HEAD已有等值内容,零损失清障 | blob等值=48128bffd601；尾提交=ff38b1964c7(2026-09-21,[workclean][W8-r2-G4v3] 改链净版三发（本地预扫 ABS 危险命令)；mtime=2026-10-03 23:56 |
| 43 | `docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md` | 认领建议 | HEAD已有等值内容,零损失清障 | blob等值=334b2dab9071；尾提交=ff38b1964c7(2026-09-21,[workclean][W8-r2-G4v3] 改链净版三发（本地预扫 ABS 危险命令)；mtime=2026-10-03 23:56 |
| 44 | `docs/03_modules/_domain_reporting/report_archive_sink/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.04),价值无法机械判 | porcelain=M_docs/03_；diff=+30/-2；新增行HEAD覆盖=0.00；去数字归一覆盖=0.04；novel:version: "0.1.2"；novel:design_maturity: production；尾提交=d3f09834b8f(2026-09-30,F115 R1+R2 报告生成薄刀：复盘触发入口+归档持久化出口（D_REPORTING)；mtime=2026-10-03 23:56 |
| 45 | `docs/03_modules/_domain_reporting/review_trigger/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.04),价值无法机械判 | porcelain=M_docs/03_；diff=+31/-3；新增行HEAD覆盖=0.00；去数字归一覆盖=0.04；novel:version: "0.1.2"；novel:design_maturity: production；尾提交=d3f09834b8f(2026-09-30,F115 R1+R2 报告生成薄刀：复盘触发入口+归档持久化出口（D_REPORTING)；mtime=2026-10-03 23:56 |
| 46 | `docs/03_modules/_domain_risk/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.67),价值无法机械判 | porcelain=M_docs/03_；diff=+6/-4；新增行HEAD覆盖=0.00；去数字归一覆盖=0.67；novel:version: "2.2.44"；novel:> module_id: MOD-L04-001 / version: 2.2.44 / statu；尾提交=fc72b533f5b(2026-09-28,[st-zcloseout-20260928][D4]11 份 blueprint.md)；mtime=2026-10-03 |
| 47 | `docs/03_modules/_domain_risk/emergency_stop_confirmation/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.00),价值无法机械判 | porcelain=M_docs/03_；diff=+2/-2；新增行HEAD覆盖=0.00；去数字归一覆盖=0.00；novel:- scripts/installers/deadman_switch.ps1（联动演练，Owner；novel:/ 数据流图 (dataflow) / （无节点） / N/A / `apply_dataflowg；尾提交=990ae93f777(2026-09-20,chore(reconciler): batched au |
| 48 | `docs/03_modules/_domain_risk/fhs_engine/blueprint.md` | 认领建议 | HEAD已有等值内容,零损失清障 | blob等值=d8badd41f4e4；尾提交=ff38b1964c7(2026-09-21,[workclean][W8-r2-G4v3] 改链净版三发（本地预扫 ABS 危险命令)；mtime=2026-10-03 23:56 |
| 49 | `docs/03_modules/_domain_sell_decision/s1_scan_orchestrator/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.02),价值无法机械判 | porcelain=M_docs/03_；diff=+64/-2；新增行HEAD覆盖=0.00；去数字归一覆盖=0.02；novel:version: "0.1.1"；novel:design_maturity: production；尾提交=07427f41c0f(2026-09-30,F45 分支成果队列化落地（来源 ai/st-c9-f45/task-f45-s1-sc)；mtime=2026-10-03 23:56 |
| 50 | `docs/03_modules/_domain_signal/sentiment_cycle/blueprint.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.25),价值无法机械判 | porcelain=M_docs/03_；diff=+4/-4；新增行HEAD覆盖=0.00；去数字归一覆盖=0.25；novel:/ 依赖图 (depgraph) / `blueprint_id=MOD-SIG-140` 的 1 ；novel:/ 数据流图 (dataflow) / （无节点） / N/A / `apply_dataflowg；尾提交=fc72b533f5b(2026-09-28,[st-zcloseout-20260928][D4]11 |
| 51 | `docs/03_modules/_domain_trading/trigger_registry/blueprint.md` | 认领建议 | HEAD已有等值内容,零损失清障 | blob等值=e4ea71421f2d；尾提交=ff38b1964c7(2026-09-21,[workclean][W8-r2-G4v3] 改链净版三发（本地预扫 ABS 危险命令)；mtime=2026-10-03 23:56 |
| 52 | `docs/03_modules/path_ownership_map.yaml` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.00),价值无法机械判 | porcelain=M__docs/03；diff=+7/-7；新增行HEAD覆盖=0.00；去数字归一覆盖=0.00；novel:- path: 'scripts/installers/deadman_switch.ps1'；novel:- path: 'scripts/installers/start_ch_health_probe.；尾提交=a4b503a163(2026-10-02,[st-construct-20261002][batch2-C1 |
| 53 | `docs/_working/ai_layer_vision/OBJ_T_tools/inventory_v0_report.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.75),价值无法机械判 | porcelain=M_docs/_wo；diff=+4/-4；新增行HEAD覆盖=0.00；去数字归一覆盖=0.75；novel:generated_at: 2026-09-30T22:14:35.220968+00:00；novel:- total_tools: 131（计数用字段，禁写死散文）；尾提交=30505c93f6c(2026-09-26,[st-ailayer-final-20260924][allow-multi-doma)；mtime= |
| 54 | `docs/_working/branch_zero_takeover/chaos_drill_plan.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=branch_zero接管战役文档(红蓝审查已收官战役) |
| 55 | `docs/_working/branch_zero_takeover/review_findings_round2.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=branch_zero接管战役文档(红蓝审查已收官战役) |
| 56 | `docs/_working/branch_zero_takeover/t1_takeover_infra.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=branch_zero接管战役文档(红蓝审查已收官战役) |
| 57 | `docs/_working/circulation_chief/logs/lane-datapipe.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=全流通总筹车道日志 |
| 58 | `docs/_working/circulation_chief/logs/lane-f04.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=全流通总筹车道日志 |
| 59 | `docs/_working/circulation_chief/logs/lane-land-docs.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=全流通总筹车道日志 |
| 60 | `docs/_working/circulation_chief/logs/wave4e.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=全流通总筹车道日志 |
| 61 | `docs/_working/circulation_chief/logs/wave4f.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=全流通总筹车道日志 |
| 62 | `docs/_working/commitmap_cure/02_audit_workpaper.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.00),价值无法机械判 | porcelain=M_docs/_wo；diff=+1/-1；新增行HEAD覆盖=0.00；去数字归一覆盖=0.00；novel:- 对账簇（⑧63台）：注册册割裂实证（Catalogs 182 册与运行时正册 91 册两套 id；尾提交=54f3906f67(2026-10-03,[st-commitmap-chief-20261003][对审收官+清障+呈批件批] )；mtime=2026-10-03 23:56 |
| 63 | `docs/_working/commitmap_cure_20261003/00_design_basis.md` | 待裁 | HEAD无此路径且非暂存新增,状态异常 | HEAD无此路径 |
| 64 | `docs/_working/deadletter_cure_20261003/10_mining/bag_attribution.json` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=死信治理战役产出(2026-10-03战役) |
| 65 | `docs/_working/deadletter_cure_20261003/10_mining/bag_classify_result.json` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=死信治理战役产出(2026-10-03战役) |
| 66 | `docs/_working/deadletter_cure_20261003/10_mining/salvage_ledger.json` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=死信治理战役产出(2026-10-03战役) |
| 67 | `docs/_working/deadletter_cure_20261003/20_design/commit_map_and_slimming_plan.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=死信治理战役产出(2026-10-03战役) |
| 68 | `docs/_working/disk_reorg_campaign/vhdx_precheck_20261001.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=盘面整理战役预检件 |
| 69 | `docs/_working/disk_reorg_campaign/vhdx_precheck_20261002.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=盘面整理战役预检件 |
| 70 | `docs/_working/disk_reorg_campaign/vhdx_precheck_20261003.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=盘面整理战役预检件 |
| 71 | `docs/_working/fullconnect_campaign/k_frontend_docs/12_f128_data_security_masking.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.00),价值无法机械判 | porcelain=M_docs/_wo；diff=+16/-0；新增行HEAD覆盖=0.00；去数字归一覆盖=0.00；novel:## 卷末批注 · 翻案执行（2026-09-30 夜战 T1-B2，st-menu-t1b2-20；novel:Owner 本夜批复：**F128 data_security 三件翻案 known-gap→接线复；尾提交=01a950bbf84(2026-09-29,[st-finaldel-chief-20260929] |
| 72 | `docs/_working/fullflow_mine/wiring/wiring_view_20261001.yaml` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56 |
| 73 | `docs/_working/fullflow_mining_chief/98_挖矿总簿_精华重建版.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56 |
| 74 | `docs/_working/fullflow_mining_chief/99_交接卡.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56 |
| 75 | `docs/_working/fullscore_night/02_factory_chain/02_wiring_plan.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=fullscore_night战役文档(2026-10-01战役) |
| 76 | `docs/_working/fullscore_night/03_integrated_backtest/blocked_v2_pool_missing.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=fullscore_night战役文档(2026-10-01战役) |
| 77 | `docs/_working/fullscore_night/03_integrated_backtest/prereg_v2.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=fullscore_night战役文档(2026-10-01战役) |
| 78 | `docs/_working/fullscore_night/10_coordination/NIGHT_STATE.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=fullscore_night战役文档(2026-10-01战役) |
| 79 | `docs/_working/fullscore_night/10_coordination/deferred_claims.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=fullscore_night战役文档(2026-10-01战役) |
| 80 | `docs/_working/fullscore_night/10_coordination/merge_request_st-lanech-20261001.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=fullscore_night战役文档(2026-10-01战役) |
| 81 | `docs/_working/fullscore_night/10_coordination/stash_pop_notice_st-lanech-20261001.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=fullscore_night战役文档(2026-10-01战役) |
| 82 | `docs/_working/fullscore_night/10_coordination/str_auto_001_quarantine_20261001.csv` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=fullscore_night战役文档(2026-10-01战役) |
| 83 | `docs/_working/integrated_backtest/artifacts_v2/W_OOS/trades_IBT-A.csv` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；HEAD同名@docs/_working/integrated_backtest/artifacts/W_OOS/trades_IBT-A.csv 行覆盖=0.01；mtime=2026-10-03 23:56；家族=回测artifacts(数据产物混入docs区) |
| 84 | `docs/_working/integrated_backtest/artifacts_v2/W_POSTD/composed_panel.pkl` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=回测artifacts(数据产物混入docs区) |
| 85 | `docs/_working/integrated_backtest/artifacts_v2/W_POSTD/nav_IBT-A.csv` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；HEAD同名@docs/_working/integrated_backtest/artifacts_v2/W_OOS/nav_IBT-A.csv 行覆盖=0.11；mtime=2026-10-03 23:56；家族=回测artifacts(数据产物混入docs区) |
| 86 | `docs/_working/integrated_backtest/artifacts_v2/W_POSTD/run_summary.yaml` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；HEAD同名@docs/_working/integrated_backtest/artifacts/W_POSTD/run_summary.yaml 行覆盖=0.01；mtime=2026-10-03 23:56；家族=回测artifacts(数据产物混入docs区) |
| 87 | `docs/_working/integrated_backtest/artifacts_v2/W_POSTD/trades_IBT-A.csv` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；HEAD同名@docs/_working/integrated_backtest/artifacts/W_OOS/trades_IBT-A.csv 行覆盖=0.01；mtime=2026-10-03 23:56；家族=回测artifacts(数据产物混入docs区) |
| 88 | `docs/_working/integrated_backtest/artifacts_v2/_regression/ab_neutral_root/W_OOS/nav_IBT-A.csv` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；HEAD同名@docs/_working/integrated_backtest/artifacts_v2/W_OOS/nav_IBT-A.csv 行覆盖=0.01；mtime=2026-10-03 23:56；家族=回测artifacts(数据产物混入docs区) |
| 89 | `docs/_working/integrated_backtest/artifacts_v2/_regression/ab_neutral_root/W_OOS/run_summary.yaml` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；HEAD同名@docs/_working/integrated_backtest/artifacts/W_POSTD/run_summary.yaml 行覆盖=0.01；mtime=2026-10-03 23:56；家族=回测artifacts(数据产物混入docs区) |
| 90 | `docs/_working/integrated_backtest/artifacts_v2/_regression/ab_neutral_root/W_OOS/trades_IBT-A.csv` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；HEAD同名@docs/_working/integrated_backtest/artifacts/W_OOS/trades_IBT-A.csv 行覆盖=0.01；mtime=2026-10-03 23:56；家族=回测artifacts(数据产物混入docs区) |
| 91 | `docs/_working/integrated_backtest/artifacts_v2/_regression/legacyflat_W_OOS/W_OOS/nav_IBT-A.csv` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；HEAD同名@docs/_working/integrated_backtest/artifacts_v2/W_OOS/nav_IBT-A.csv 行覆盖=0.01；mtime=2026-10-03 23:56；家族=回测artifacts(数据产物混入docs区) |
| 92 | `docs/_working/integrated_backtest/artifacts_v2/_regression/legacyflat_W_OOS/W_OOS/run_summary.yaml` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；HEAD同名@docs/_working/integrated_backtest/artifacts/W_POSTD/run_summary.yaml 行覆盖=0.01；mtime=2026-10-03 23:56；家族=回测artifacts(数据产物混入docs区) |
| 93 | `docs/_working/integrated_backtest/artifacts_v2/_regression/legacyflat_W_OOS/W_OOS/trades_IBT-A.csv` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；HEAD同名@docs/_working/integrated_backtest/artifacts/W_OOS/trades_IBT-A.csv 行覆盖=0.00；mtime=2026-10-03 23:56；家族=回测artifacts(数据产物混入docs区) |
| 94 | `docs/_working/map_build/fig14_construction/00_skeleton.md` | 认领建议 | HEAD已有等值内容,零损失清障 | blob等值=80598cc72876；尾提交=18606f28d52(2026-10-02,[全流通清场总包][0119/0120 SSOT死信批重投v4·主区直投+CR-15图1)；mtime=2026-10-03 23:56 |
| 95 | `docs/_working/night_sweep/99_owner_gate_menu.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56 |
| 96 | `docs/_working/night_totalflow_chief/00_skeleton.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；HEAD同名@docs/_working/commit_chain_fullflow/00_skeleton.md 行覆盖=0.08；mtime=2026-10-03 23:56；家族=夜战总flow战役文档(2026-09-25战役) |
| 97 | `docs/_working/night_totalflow_chief/90_red_blue.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=夜战总flow战役文档(2026-09-25战役) |
| 98 | `docs/_working/night_totalflow_chief/99_delivery.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=夜战总flow战役文档(2026-09-25战役) |
| 99 | `docs/_working/night_totalflow_chief/A_mine.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=夜战总flow战役文档(2026-09-25战役) |
| 100 | `docs/_working/night_totalflow_chief/B_mine.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=夜战总flow战役文档(2026-09-25战役) |
| 101 | `docs/_working/night_totalflow_chief/CEF_mine.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=夜战总flow战役文档(2026-09-25战役) |
| 102 | `docs/_working/night_totalflow_chief/D_mine.md` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=夜战总flow战役文档(2026-09-25战役) |
| 103 | `docs/_working/pipeline-research/reports/intake-20260930-2102.yaml` | 待裁 | 暂存新增HEAD独有内容,价值无法机械判 | porcelain=A ；暂存新增HEAD独有；mtime=2026-10-03 23:56；家族=管线调研报告 |
| 104 | `docs/_working/resource_schedule/calibration_report.yaml` | 待裁 | 新增独立内容(add_cov=0.12/norm=0.14),价值无法机械判 | porcelain=M_docs/_wo；diff=+1102/-349；新增行HEAD覆盖=0.12；去数字归一覆盖=0.14；novel:generated_at: '2026-10-02T22:17:10+00:00'；novel:entities: 102；尾提交=1420128a70b(2026-09-21,chore(derived): watchdog 派生缓存自动收敛——B类白名单稳定漂移)；mtime=2026-10-03 23:56 |
| 105 | `docs/_working/resource_schedule/morning_report/latest.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.51),价值无法机械判 | porcelain=M_docs/_wo；diff=+57/-58；新增行HEAD覆盖=0.00；去数字归一覆盖=0.51；novel:generated_at: '2026-10-02T22:31:05+00:00'；novel:# 资源晨报（L-9） — 2026-10-03（Asia/Shanghai）；尾提交=dceb5c1e643(2026-09-22,[接手批][st-gateaudit-20260922] 他会话门禁超时中断 stage)；m |
| 106 | `docs/_working/total_command_closeout/93_owner_menu.md` | 待裁 | 新增独立内容(add_cov=0.17/norm=0.17),价值无法机械判 | porcelain=M_docs/_wo；diff=+8/-0；新增行HEAD覆盖=0.17；去数字归一覆盖=0.17；novel:## 排期登记（2026-09-30 菜单执行夜，T1-F2 车道落册）；novel:> Owner 批文原文："其他全部按照你的建议批准施工"（2026-09-30 菜单执行夜，总筹 ；尾提交=170791e0e36(2026-09-30,[F10/F11·st-nightsweep2-nf2-20260930][Owner |
| 107 | `docs/_working/ultimate_library/COVERAGE.md` | 待裁 | 新增独立内容(add_cov=0.00/norm=0.06),价值无法机械判 | porcelain=M_docs/_wo；diff=+53/-53；新增行HEAD覆盖=0.00；去数字归一覆盖=0.06；novel:- 构建时戳（UTC）：2026-10-02T13:54:06.746292+00:00；novel:- 盘上在扫文件：36066｜馆内在编（file/module）：36340；尾提交=cd0a0bc7304(2026-09-30,[ARCH-APPROVAL:#ARCH-PYTHON-SITECUSTOMIZE] F) |

## 4. 逐件表·untracked_new_left（82）

| # | 路径 | 判定 | 依据 | 证据 |
|---|---|---|---|---|
| 1 | `config/data_masking_policy.yaml` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-10-01 06:30；家族=数据安全wiring家族(与src/zephyr/data_security/wiring/+tests/data_security/test_wiring_*3台同族) |
| 2 | `config/macro_indicator_series_map.yaml` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-10-01 08:21；家族=宏观sensor家族(与src/zephyr/regime/features/macro_regime_sensor.py同族) |
| 3 | `data/backup/` | 待裁 | 数据产物目录(RULE-DATA-OPS域,数据班裁决) | 目录7文件/83.5MB；时间跨2026-09-16~2026-09-17；样例:alt_regime_f23_weekend_20260917/f23_weekend_rows_backup.tsv；样例:alt_regime_f23_weekend_20260917/README.txt；mtime=2026-09-17 05:46 |
| 4 | `data/backups/` | 待裁 | 数据产物目录(RULE-DATA-OPS域,数据班裁决) | 目录44文件/16.0MB；时间跨2026-06-29~2026-09-21；样例:c1_market_limit_up_down_weekend_rows_20260916_pre_ghostclean；样例:c1_market_limit_up_down_weekend_rows_20260916_pre_ghostclean；mtime=2026-09-25 21:59 |
| 5 | `data/cleaning_anomaly_gate/` | 待裁 | 数据产物目录(RULE-DATA-OPS域,数据班裁决) | 目录3文件/0.2MB；时间跨2026-10-01~2026-10-03；样例:2026-10-01_anomaly_report.json；样例:2026-10-02_anomaly_report.json；mtime=2026-10-03 06:50 |
| 6 | `data/cleaning_expectation_gate/` | 待裁 | 数据产物目录(RULE-DATA-OPS域,数据班裁决) | 目录3文件/0.0MB；时间跨2026-10-01~2026-10-03；样例:2026-10-01_expectation_report.json；样例:2026-10-03_expectation_report.json；mtime=2026-10-03 06:50 |
| 7 | `data/cleaning_gate/` | 待裁 | 数据产物目录(RULE-DATA-OPS域,数据班裁决) | 目录5文件/0.0MB；时间跨2026-09-29~2026-10-03；样例:2026-09-29_cleaning_report.json；样例:2026-09-30_cleaning_gate_status_ledger.json；mtime=2026-10-03 06:50 |
| 8 | `data/compliance_log/` | 待裁 | 数据产物目录(RULE-DATA-OPS域,数据班裁决) | 目录3文件/0.1MB；时间跨2026-10-02~2026-10-02；样例:compliance_log.jsonl；样例:checklist/position_limit_verify.json；mtime=2026-09-28 09:15 |
| 9 | `data/databases/rolling_archive_state.json` | 待裁 | 数据产物(RULE-DATA-OPS域,数据班裁决) | HEAD无等值无同名；mtime=2026-09-21 15:37；家族=滚动归档状态(运行时状态文件) |
| 10 | `data/divergence_stats/` | 待裁 | 数据产物目录(RULE-DATA-OPS域,数据班裁决) | 目录1文件/0.0MB；时间跨2026-09-30~2026-09-30；样例:divergence_stats.jsonl；mtime=2026-09-30 23:15 |
| 11 | `data/local_fallback_quarantine/` | 待裁 | 数据产物目录(RULE-DATA-OPS域,数据班裁决) | 目录21文件/23.2MB；时间跨2026-09-15~2026-09-21；样例:_README.txt；样例:c1_market__futures_warehouse_receipt/20260918_083531_108d261；mtime=2026-09-21 10:33 |
| 12 | `data/quality_sentinel/` | 待裁 | 数据产物目录(RULE-DATA-OPS域,数据班裁决) | 目录3文件/0.0MB；时间跨2026-09-19~2026-10-03；样例:2026-09-19_report.json；样例:2026-09-26_report.json；mtime=2026-10-03 06:50 |
| 13 | `data/registers/metaq-io-2018/china_2018_153.rda` | 待裁 | 数据产物(RULE-DATA-OPS域,数据班裁决) | HEAD无等值无同名；mtime=2026-09-24 15:46；家族=metaq R数据件 |
| 14 | `data/registers/metaq-io-2018/china_2020_153.rda` | 待裁 | 数据产物(RULE-DATA-OPS域,数据班裁决) | HEAD无等值无同名；mtime=2026-09-24 15:47；家族=metaq R数据件 |
| 15 | `data/reports/morning_digest.md` | 待裁 | 数据产物(RULE-DATA-OPS域,数据班裁决) | HEAD无等值无同名；mtime=2026-10-01 04:41；家族=晨报产物 |
| 16 | `data/strategy_intake/conditional_tables/_cache_880.parquet` | 待裁 | 数据产物(RULE-DATA-OPS域,数据班裁决) | HEAD无等值无同名；mtime=2026-09-25 03:32；家族=条件表缓存 |
| 17 | `data/strategy_intake/grid_20260915-051517/` | 待归档 | 过期网格跑批产物(目录日期=20260915) | 目录3文件/0.0MB；时间跨2026-09-15~2026-09-15；样例:manifest.csv；样例:negatives.csv；mtime=2026-09-15 05:15 |
| 18 | `data/strategy_intake/grid_20260915-051610/` | 待归档 | 过期网格跑批产物(目录日期=20260915) | 目录3文件/0.0MB；时间跨2026-09-15~2026-09-15；样例:manifest.csv；样例:negatives.csv；mtime=2026-09-15 05:16 |
| 19 | `data/strategy_intake/grid_20260915-052012/` | 待归档 | 过期网格跑批产物(目录日期=20260915) | 目录3文件/0.1MB；时间跨2026-09-15~2026-09-15；样例:manifest.csv；样例:negatives.csv；mtime=2026-09-15 05:27 |
| 20 | `data/strategy_intake/grid_20260915-052749/` | 待归档 | 过期网格跑批产物(目录日期=20260915) | 目录5文件/1.2MB；时间跨2026-09-15~2026-09-15；样例:manifest.csv；样例:negatives.csv；mtime=2026-09-15 07:00 |
| 21 | `data/strategy_intake/grid_20260915-060812/` | 待归档 | 过期网格跑批产物(目录日期=20260915) | 目录3文件/1.2MB；时间跨2026-09-15~2026-09-15；样例:manifest.csv；样例:negatives.csv；mtime=2026-09-15 07:16 |
| 22 | `data/strategy_intake/grid_20260916-012207/` | 待归档 | 过期网格跑批产物(目录日期=20260916) | 目录3文件/0.0MB；时间跨2026-09-16~2026-09-16；样例:manifest.csv；样例:negatives.csv；mtime=2026-09-16 01:23 |
| 23 | `data/strategy_intake/grid_20260916-123551/` | 待归档 | 过期网格跑批产物(目录日期=20260916) | 目录4文件/5.9MB；时间跨2026-09-16~2026-09-16；样例:dual_dsr_candidates.csv；样例:manifest.csv；mtime=2026-09-16 23:35 |
| 24 | `data/strategy_intake/grid_20260916-123552/` | 待归档 | 过期网格跑批产物(目录日期=20260916) | 目录4文件/3.5MB；时间跨2026-09-16~2026-09-16；样例:manifest.csv；样例:negatives.csv；mtime=2026-09-16 23:34 |
| 25 | `data/strategy_intake/grid_20260916-233634/` | 待归档 | 过期网格跑批产物(目录日期=20260916) | 目录3文件/0.0MB；时间跨2026-09-16~2026-09-16；样例:manifest.csv；样例:negatives.csv；mtime=2026-09-16 23:37 |
| 26 | `data/strategy_intake/grid_20260917-000940/` | 待归档 | 过期网格跑批产物(目录日期=20260917) | 目录3文件/0.0MB；时间跨2026-09-17~2026-09-17；样例:manifest.csv；样例:negatives.csv；mtime=2026-09-17 00:10 |
| 27 | `data/strategy_intake/grid_20260917-001854/` | 待归档 | 过期网格跑批产物(目录日期=20260917) | 目录4文件/0.1MB；时间跨2026-09-17~2026-09-17；样例:manifest.csv；样例:negatives.csv；mtime=2026-09-17 00:19 |
| 28 | `data/strategy_intake/grid_20260917-003812/` | 待归档 | 过期网格跑批产物(目录日期=20260917) | 目录4文件/0.1MB；时间跨2026-09-17~2026-09-17；样例:manifest.csv；样例:negatives.csv；mtime=2026-09-17 00:38 |
| 29 | `data/strategy_intake/grid_20260923-063545/` | 待归档 | 过期网格跑批产物(目录日期=20260923) | 目录4文件/0.1MB；时间跨2026-09-23~2026-09-23；样例:manifest.csv；样例:negatives.csv；mtime=2026-09-23 06:39 |
| 30 | `data/strategy_intake/grid_20260924-080309/` | 待归档 | 过期网格跑批产物(目录日期=20260924) | 目录5文件/3.1MB；时间跨2026-09-24~2026-09-24；样例:condition_attribution.csv；样例:manifest.csv；mtime=2026-09-24 10:27 |
| 31 | `data/strategy_intake/grid_20260924-102243/` | 待归档 | 过期网格跑批产物(目录日期=20260924) | 目录4文件/0.1MB；时间跨2026-09-24~2026-09-24；样例:manifest.csv；样例:negatives.csv；mtime=2026-09-24 10:26 |
| 32 | `data/strategy_intake/grid_20260925-232032/` | 待归档 | 过期网格跑批产物(目录日期=20260925) | 目录4文件/3.0MB；时间跨2026-09-26~2026-09-26；样例:manifest.csv；样例:negatives.csv；mtime=2026-09-26 02:35 |
| 33 | `data/strategy_intake/grid_20260926-021530/` | 待归档 | 过期网格跑批产物(目录日期=20260926) | 目录4文件/3.0MB；时间跨2026-09-26~2026-09-26；样例:manifest.csv；样例:negatives.csv；mtime=2026-09-26 02:39 |
| 34 | `data/strategy_intake/grid_20260926-024947/net_returns.parquet` | 待归档 | 过期跑批产物(名称日期=20260926) | HEAD无等值无同名；mtime=2026-09-26 07:47 |
| 35 | `data/strategy_intake/grid_20260926-024947/t2_subspace.json` | 待归档 | 过期跑批产物(名称日期=20260926) | HEAD无等值无同名；mtime=2026-09-30 17:45 |
| 36 | `data/strategy_intake/grid_20260926-024947/t2_subspace_meta.yaml` | 待归档 | 过期跑批产物(名称日期=20260926) | HEAD无等值无同名；mtime=2026-09-30 17:45 |
| 37 | `data/strategy_intake/grid_20261001-051901/` | 待裁 | 近期网格跑批产物(目录日期=20261001) | 目录4文件/0.0MB；时间跨2026-10-01~2026-10-01；样例:manifest.csv；样例:negatives.csv；mtime=2026-10-01 05:19 |
| 38 | `data/strategy_intake/grid_gpu_sectorcond_20260924-0834/` | 待归档 | 过期网格跑批产物(目录日期=20260924) | 目录6文件/4.0MB；时间跨2026-09-24~2026-09-24；样例:is_holdout.npy；样例:momentum_pct.npy；mtime=2026-09-24 08:34 |
| 39 | `data/strategy_intake/grid_t0_conditional_v1/t0_condition_matrix_v1.csv` | 待裁 | 数据产物(RULE-DATA-OPS域,数据班裁决) | HEAD无等值无同名；mtime=2026-09-24 08:15；家族=T0条件矩阵v1(命名版本化,非时戳跑批) |
| 40 | `data/strategy_intake/promotion_advisories/` | 待裁 | 数据产物目录(RULE-DATA-OPS域,数据班裁决) | 目录1文件/0.0MB；时间跨2026-10-01~2026-10-01；样例:ADV-20260930-STR-VREV-025.json；mtime=2026-10-01 04:41；家族=晋升建议产物目录 |
| 41 | `data/strategy_intake/statreplay_baseline/` | 待裁 | 数据产物目录(RULE-DATA-OPS域,数据班裁决) | 目录2文件/0.3MB；时间跨2026-09-24~2026-09-24；样例:baseline_manifest_v0.json；样例:baseline_manifest_v1.json；mtime=2026-09-24 10:02；家族=统计回放基线目录 |
| 42 | `docs/01_policies_and_standards/sop/mining_sop/vertical_map_mounting_policy.md` | 认领建议 | HEAD已有等值内容(同blob已在HEAD树) | HEAD等值blob@docs/01_policies_and_standards/sop/mining_sop/vertical_map_mounting_policy.md；mtime=2026-10-04 01:26；家族=SOP政策文(纵向地图挂载,与10-04 battle_map定性讨论相关) |
| 43 | `docs/03_modules/_domain_factor/algo_flow/technical_indicator_factors_bridge.yaml` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-10-01 22:04；家族=algo_flow桥接配置(与daily_job.yaml同族) |
| 44 | `docs/03_modules/_domain_factor/algo_flow/technical_indicator_factors_daily_job.yaml` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-10-01 22:04；家族=algo_flow桥接配置(与bridge.yaml同族) |
| 45 | `docs/_working/commitmap_cure/03_disposition_table.csv` | 认领建议 | HEAD已有等值内容@docs/_working/commitmap_cure/03_disposition_table.csv(行覆盖1.00) | HEAD同名@docs/_working/commitmap_cure/03_disposition_table.csv 行覆盖=1.00；mtime=2026-10-03 21:03；家族=本战役(commitmap_cure)在用件·总筹自持 |
| 46 | `schemas/categories/market/market_option_daily_stats.py` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-09-23 02:29；家族=期权日统计家族(与scripts/backfill_option_daily_stats.py同族) |
| 47 | `scripts/_archive/ops/register_belt_daemon_task.ps1` | 待归档 | _archive归档区件(本就属归档) | HEAD无等值无同名；mtime=2026-09-22 21:54 |
| 48 | `scripts/_archive/ops/serve_docs_http.bat` | 待归档 | _archive归档区件(本就属归档) | HEAD无等值无同名；mtime=2026-08-01 00:51 |
| 49 | `scripts/audit/pcr_e4_exam.py` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-09-23 02:29；家族=E4考试家族(与backtest/f06_e4_wfa_exam.py同族) |
| 50 | `scripts/backfill_option_daily_stats.py` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-09-23 02:29；家族=期权日统计家族(与schemas/categories/market/market_option_daily_stats.py同族) |
| 51 | `scripts/backtest/f06_e4_wfa_exam.py.tmp.18376.09af50b743f9` | 待归档 | 原子写残件(safe_write临时体未收尾) | HEAD无等值无同名；mtime=2026-10-01 15:01 |
| 52 | `scripts/backtest/f06_e4_wfa_exam.py.tmp.18376.ef6844d6fa56` | 待归档 | 原子写残件(safe_write临时体未收尾) | HEAD无等值无同名；mtime=2026-10-01 04:32 |
| 53 | `scripts/backtest/translated/_c4_engine.py.tmp.18376.0778f70f85b8` | 待归档 | 原子写残件(safe_write临时体未收尾) | HEAD无等值无同名；mtime=2026-10-01 02:16 |
| 54 | `scripts/ch/backfill_rzrq_history.py` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-10-02 17:55；家族=两融历史回填 |
| 55 | `scripts/governance/apply_meta_question_ddl.py` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-09-26 06:30；家族=metaq 283问家族 |
| 56 | `scripts/governance/check_meta_question_batch.py` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-09-28 20:23；家族=metaq 283问家族 |
| 57 | `scripts/governance/commit_queue_landing.py.tmp.18376.b68dcdb5b8c7` | 待归档 | 原子写残件(safe_write临时体未收尾) | HEAD无等值无同名；mtime=2026-10-01 10:32 |
| 58 | `scripts/governance/d5_architecture/generators/generate_data_supply_chain_map.py.tmp.18376.3e473d9809f7` | 待归档 | 原子写残件(safe_write临时体未收尾) | HEAD无等值无同名；mtime=2026-10-01 23:36 |
| 59 | `scripts/governance/standards_governance/__init__.py` | 待裁 | HEAD同名@scripts/arch_guard/fitness_functions/__init__.py但内容分歧(行覆盖0.08) | HEAD同名@scripts/arch_guard/fitness_functions/__init__.py 行覆盖=0.08；mtime=2026-09-19 15:17 |
| 60 | `scripts/governance/wave1a/build_delivery_cards.py` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-10-02 17:55；家族=wave1a交付卡家族(与cross_session_view.py同族) |
| 61 | `scripts/governance/wave1a/cross_session_view.py` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-10-02 17:55；家族=wave1a交付卡家族 |
| 62 | `scripts/patrol/` | 待裁 | 目录,HEAD无对应 | 目录1文件/0.0MB；时间跨2026-09-23~2026-09-23；样例:zcode_workspace_patrol.ps1；mtime=2026-09-23 02:29 |
| 63 | `scripts/sector_line/` | 待裁 | 目录,HEAD无对应 | 目录2文件/0.0MB；时间跨2026-10-02~2026-10-02；样例:build_gpu_input_pack.py；样例:freeze_baseline.py；mtime=2026-09-28 00:34；家族=sector_line家族(与derived_sync暂存新增algo_flow/sector_line/index.md同族) |
| 64 | `scripts/tmp/` | 待归档 | 临时区产物(.runtime同类) | 目录4文件/0.1MB；时间跨2026-10-03~2026-10-04；样例:catchup_guard.lock；样例:scheduler.heartbeat；mtime=2026-10-04 02:47 |
| 65 | `session_logs/st-c9-close4/` | 待归档 | 会话日志(TTL运行时区) | 目录1文件/0.0MB；时间跨2026-09-30~2026-09-30；样例:session_start_commit.txt；mtime=2026-09-30 04:14 |
| 66 | `session_logs/st-flashbiz-20260918/` | 待归档 | 会话日志(TTL运行时区) | 目录1文件/0.0MB；时间跨2026-09-18~2026-09-18；样例:session_start_commit.txt；mtime=2026-09-18 01:35 |
| 67 | `session_logs/st-menu-t1b2-20260930/` | 待归档 | 会话日志(TTL运行时区) | 目录1文件/0.0MB；时间跨2026-09-30~2026-09-30；样例:session_start_commit.txt；mtime=2026-09-30 21:37 |
| 68 | `session_logs/st-nightsweep2-nb2-20260930/` | 待归档 | 会话日志(TTL运行时区) | 目录1文件/0.0MB；时间跨2026-09-30~2026-09-30；样例:session_start_commit.txt；mtime=2026-09-30 06:16 |
| 69 | `src/zephyr/data/quality/` | 待裁 | 整目录源码/测试未落HEAD,成套家族价值须总筹裁 | 目录6文件/0.1MB；时间跨2026-10-01~2026-10-01；样例:archive_sla_burnrate.py；样例:sla_breach_predictor.py；mtime=2026-10-01 05:02 |
| 70 | `src/zephyr/data_security/wiring/` | 待裁 | 整目录源码/测试未落HEAD,成套家族价值须总筹裁 | 目录8文件/0.1MB；时间跨2026-10-01~2026-10-01；样例:audit_sink.py；样例:data_exit_guard.py；mtime=2026-10-01 07:54；家族=数据安全wiring家族(与config/data_masking_policy.yaml+tests/data_security/test_wiring_*3台同族) |
| 71 | `src/zephyr/governance/audit/registry_entry_counts_reconciler.py` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-09-30 02:40；家族=注册册计数对账家族(与tests/governance/test_registry_entry_counts_reconciler.py同族) |
| 72 | `src/zephyr/regime/features/macro_regime_sensor.py` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-10-01 08:21；家族=宏观sensor家族(与config/macro_indicator_series_map.yaml同族) |
| 73 | `tests/backtest/test_n_trial_ledger_t0_family.py` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-10-02 17:55；家族=T0家族n_trial账本测试 |
| 74 | `tests/data_security/test_wiring_audit_sink.py` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-10-01 06:30；家族=数据安全wiring家族 |
| 75 | `tests/data_security/test_wiring_data_exit_guard.py` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-10-01 06:30；家族=数据安全wiring家族 |
| 76 | `tests/data_security/test_wiring_lsg_masking_front.py` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-10-01 06:30；家族=数据安全wiring家族 |
| 77 | `tests/governance/d1_structure/test_untracked_phantom_docs_guard.py` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-10-02 17:55 |
| 78 | `tests/governance/registry_projection/test_state_v2.py` | 认领建议 | HEAD已有等值内容(同blob已在HEAD树) | HEAD等值blob@tests/governance/registry_projection/test_state_v2.py；mtime=2026-10-03 21:06；家族=registry_projection家族(注:与05清单active_wip_left在飞件同族,随其车道) |
| 79 | `tests/governance/standards_governance/` | 待裁 | 整目录源码/测试未落HEAD,成套家族价值须总筹裁 | 目录2文件/0.0MB；时间跨2026-09-28~2026-10-02；样例:test_generate_standard_family_registry.py；样例:__pycache__/test_generate_standard_family_registry.cpython-3；mtime=2026-09-28 18:06 |
| 80 | `tests/governance/test_registry_entry_counts_reconciler.py` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-09-30 02:40；家族=注册册计数对账家族(与src/.../registry_entry_counts_reconciler.py同族) |
| 81 | `tests/strategy_pipeline/test_daily_gate_snapshot_l5.py` | 待裁 | HEAD无等值无同名,价值无法机械判 | HEAD无等值无同名；mtime=2026-09-23 02:29；家族=L5日闸快照测试 |
| 82 | `tests/zephyr/data/quality/` | 待裁 | 整目录源码/测试未落HEAD,成套家族价值须总筹裁 | 目录4文件/0.1MB；时间跨2026-10-01~2026-10-01；样例:test_archive_sla_burnrate.py；样例:test_sla_breach_predictor.py；mtime=2026-10-01 05:02 |

## 5. 待裁件·总筹关注点（家族化归集）

- **散件**（64台）：`scripts/ensure_ai_wrapper_injection.ps1`、`scripts/run_boot_sla_probe.py`、`docs/03_modules/_cross_layer/clone_guard/blueprint.md`、`docs/03_modules/_cross_layer/gate_engine/blueprint.md`、`docs/03_modules/_cross_layer/model_profiler/blueprint.md`、`docs/03_modules/_cross_layer/shared_core/blueprint.md`、`docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md`、`docs/03_modules/_domain_backtest/decay_monitor/blueprint.md`…等
- **回测artifacts**（11台）：`docs/_working/integrated_backtest/artifacts_v2/W_OOS/trades_IBT-A.csv`、`docs/_working/integrated_backtest/artifacts_v2/W_POSTD/composed_panel.pkl`、`docs/_working/integrated_backtest/artifacts_v2/W_POSTD/nav_IBT-A.csv`、`docs/_working/integrated_backtest/artifacts_v2/W_POSTD/run_summary.yaml`、`docs/_working/integrated_backtest/artifacts_v2/W_POSTD/trades_IBT-A.csv`、`docs/_working/integrated_backtest/artifacts_v2/_regression/ab_neutral_root/W_OOS/nav_IBT-A.csv`、`docs/_working/integrated_backtest/artifacts_v2/_regression/ab_neutral_root/W_OOS/run_summary.yaml`、`docs/_working/integrated_backtest/artifacts_v2/_regression/ab_neutral_root/W_OOS/trades_IBT-A.csv`…等
- **fullscore_night战役文档**（8台）：`docs/_working/fullscore_night/02_factory_chain/02_wiring_plan.md`、`docs/_working/fullscore_night/03_integrated_backtest/blocked_v2_pool_missing.md`、`docs/_working/fullscore_night/03_integrated_backtest/prereg_v2.md`、`docs/_working/fullscore_night/10_coordination/NIGHT_STATE.md`、`docs/_working/fullscore_night/10_coordination/deferred_claims.md`、`docs/_working/fullscore_night/10_coordination/merge_request_st-lanech-20261001.md`、`docs/_working/fullscore_night/10_coordination/stash_pop_notice_st-lanech-20261001.md`、`docs/_working/fullscore_night/10_coordination/str_auto_001_quarantine_20261001.csv`
- **夜战总flow战役文档**（7台）：`docs/_working/night_totalflow_chief/00_skeleton.md`、`docs/_working/night_totalflow_chief/90_red_blue.md`、`docs/_working/night_totalflow_chief/99_delivery.md`、`docs/_working/night_totalflow_chief/A_mine.md`、`docs/_working/night_totalflow_chief/B_mine.md`、`docs/_working/night_totalflow_chief/CEF_mine.md`、`docs/_working/night_totalflow_chief/D_mine.md`
- **全流通总筹车道日志**（5台）：`docs/_working/circulation_chief/logs/lane-datapipe.md`、`docs/_working/circulation_chief/logs/lane-f04.md`、`docs/_working/circulation_chief/logs/lane-land-docs.md`、`docs/_working/circulation_chief/logs/wave4e.md`、`docs/_working/circulation_chief/logs/wave4f.md`
- **数据安全wiring家族**（5台）：`config/data_masking_policy.yaml`、`src/zephyr/data_security/wiring/`、`tests/data_security/test_wiring_audit_sink.py`、`tests/data_security/test_wiring_data_exit_guard.py`、`tests/data_security/test_wiring_lsg_masking_front.py`
- **死信治理战役产出**（4台）：`docs/_working/deadletter_cure_20261003/10_mining/bag_attribution.json`、`docs/_working/deadletter_cure_20261003/10_mining/bag_classify_result.json`、`docs/_working/deadletter_cure_20261003/10_mining/salvage_ledger.json`、`docs/_working/deadletter_cure_20261003/20_design/commit_map_and_slimming_plan.md`
- **branch_zero接管战役文档**（3台）：`docs/_working/branch_zero_takeover/chaos_drill_plan.md`、`docs/_working/branch_zero_takeover/review_findings_round2.md`、`docs/_working/branch_zero_takeover/t1_takeover_infra.md`
- **盘面整理战役预检件**（3台）：`docs/_working/disk_reorg_campaign/vhdx_precheck_20261001.md`、`docs/_working/disk_reorg_campaign/vhdx_precheck_20261002.md`、`docs/_working/disk_reorg_campaign/vhdx_precheck_20261003.md`
- **SLA预测家族**（2台）：`src/zephyr/data_eng/quality_sla_breach_predictor.py`、`tests/data_eng/test_quality_sla_breach_predictor.py`
- **宏观sensor家族**（2台）：`config/macro_indicator_series_map.yaml`、`src/zephyr/regime/features/macro_regime_sensor.py`
- **metaq R数据件**（2台）：`data/registers/metaq-io-2018/china_2018_153.rda`、`data/registers/metaq-io-2018/china_2020_153.rda`
- **algo_flow桥接配置**（2台）：`docs/03_modules/_domain_factor/algo_flow/technical_indicator_factors_bridge.yaml`、`docs/03_modules/_domain_factor/algo_flow/technical_indicator_factors_daily_job.yaml`
- **期权日统计家族**（2台）：`schemas/categories/market/market_option_daily_stats.py`、`scripts/backfill_option_daily_stats.py`
- **metaq 283问家族**（2台）：`scripts/governance/apply_meta_question_ddl.py`、`scripts/governance/check_meta_question_batch.py`
- **wave1a交付卡家族**（2台）：`scripts/governance/wave1a/build_delivery_cards.py`、`scripts/governance/wave1a/cross_session_view.py`
- **注册册计数对账家族**（2台）：`src/zephyr/governance/audit/registry_entry_counts_reconciler.py`、`tests/governance/test_registry_entry_counts_reconciler.py`
- **管线调研报告**（1台）：`docs/_working/pipeline-research/reports/intake-20260930-2102.yaml`
- **滚动归档状态**（1台）：`data/databases/rolling_archive_state.json`
- **晨报产物**（1台）：`data/reports/morning_digest.md`
- **条件表缓存**（1台）：`data/strategy_intake/conditional_tables/_cache_880.parquet`
- **T0条件矩阵v1**（1台）：`data/strategy_intake/grid_t0_conditional_v1/t0_condition_matrix_v1.csv`
- **晋升建议产物目录**（1台）：`data/strategy_intake/promotion_advisories/`
- **统计回放基线目录**（1台）：`data/strategy_intake/statreplay_baseline/`
- **E4考试家族**（1台）：`scripts/audit/pcr_e4_exam.py`
- **两融历史回填**（1台）：`scripts/ch/backfill_rzrq_history.py`
- **sector_line家族**（1台）：`scripts/sector_line/`
- **T0家族n_trial账本测试**（1台）：`tests/backtest/test_n_trial_ledger_t0_family.py`
- **L5日闸快照测试**（1台）：`tests/strategy_pipeline/test_daily_gate_snapshot_l5.py`

## 6. 局限与复核指引

- 本批全部结论为机械判据输出；「认领建议」=内容零损失清障依据充分（HEAD等值/超集/孪生），不代表该件无需总筹过目。
- 「待归档」仅当名称/路径机械可判（grid日期/原子写残件/日志区/归档区/临时区）；「待裁」=机械无法定夺，未做价值判断。
- 暂存删除 28 台中 26 台一次性 .ps1 检查/修复脚本名称呈战役工具形态，但内容 HEAD 独有（无孪生），机械上不能证其可删，故全数待裁留证据。
- untracked 待裁件中的成对家族（源码+测试+config）系配置面同批产出，建议总筹按家族整批裁决而非逐台。
- blob 史追溯对超时未跑件已注记 `blob史超时未跑`，复核时可补跑 `git log --all --find-object=<blob>`。
- 3 台 untracked 认领建议件系「HEAD已含等值blob但index缺席」的索引态残迹：内容零差异，`git add` 复位 index 即收敛（如 vertical_map_mounting_policy.md / test_state_v2.py）。
- active_wip_left(7台)不在本批范围（非孤儿，在飞车道）；stale 893件禁区未触碰；二遍 worktree 排查全程零写。

---

**判定权归总筹。**
