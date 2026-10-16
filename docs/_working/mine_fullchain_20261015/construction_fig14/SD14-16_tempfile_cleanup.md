---
ttl: task_bound
doc_type: mining_segment
campaign: mine_fullchain_20261015
segment_id: D14-16
figure: fig14 施工升级流（construction_workflow_map）
created: 2026-10-15
ssot: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-11-临时文件清理只清自己不动他人 + 附录 D 锚块
---

# SD14-16 临时文件清理（policy Step 11）

## 1. 定义

Step 10 commit 落地后触发：按三级分类清理本会话产生的临时文件（成果层 docs/_working/ git 跟踪/暂存层 .runtime/sessions/<sid>/staging/ 免跟踪/系统层 .runtime/ 现有 reconciler 维护）+释放 .ailocks+worktree 标记可清理。铁律三条：只清自己不动他人 WIP/禁根目录直写 .runtime//系统层不手动清。临时文件放置 5 铁律（trae_070，DCR-008 硬阻断跨类乱放）。清理由事件触发的对账件承担（机制归图11）。handoff_to=D11-S05/D11-S08/D11-C11。

## 2. 六向台账

| 向 | 内容 | 路径证据 |
|---|---|---|
| 输入面 | commit 已落地（D14-15 产物）；本会话 sid；三级分类表 | 政策 L668-711；`.runtime/sessions/<sid>/staging/`（24h TTL） |
| 输出面 | 清理报告——**无落点**（政策产出物声明与禁报告文件口径冲突，图 note：产出物"清理报告"无落点）；实际凭据=reconciler status 面 | 图 YAML #D14-16 note；`.runtime/reconcile_reports/` |
| SSOT 真源 | `trae_071_temporary_file_lifecycle.yaml`（三级分类+test_residue_reclaim）+`trae_035#task_closure_standard`（清扫三步法）+`trae_070_temporary_file_placement.yaml`（5 铁律+directory_purpose_classification 表） | rules 三件在册 |
| 代码模块 | staging 生命周期对账件 `make_session_staging_lifecycle_reconciler`（priority=802，`src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py` :160/:1903 本批实证）；锁释放 `scripts/lock_files.py`——release 需 ≥3 参（:1892 实证，政策单参形态照抄必失败=D14-G08）；release-all/release-batch 子命令在册（:1673-1674 实证） | 网关+锁脚本 |
| 门禁约束 | `GATE-DIRECTORY-CONTRACT`（DCR-008 硬阻断跨类乱放）+GATE-RUNTIME-CLEANUP reconciler 兜底；事件触发（session_worktree_merge/abort 事件），非时间触发 | trae_070/trae_071 |
| 自动化触发 | post-commit reconciler 自动清 staging（>24h 文件）；GATE-STASH-LIFECYCLE 自动清旧 stash；worktree 可清理判定由 session_worktree_sweep 三重判据自动承担（mark-completed 幽灵已由自动判据替代） | 政策 L686-695（R-07/R-06 更正注记） |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | commit 落地触发链+sid 隔离面明确 |
| 输出面 | fail | "清理报告"无落点——政策自_declared 产出物无法交付（禁报告文件 vs 报告产出物自相矛盾） |
| SSOT 真源 | pass | 三规则册在册 |
| 代码模块 | warn | 清理自动化件实证在盘；但政策 release 命令契约与实现不符（G08，命令契约错非件不存在） |
| 门禁约束 | pass | DCR-008+RUNTIME-CLEANUP 两层在册 |
| 自动化触发 | pass | 事件触发 reconciler 实证（priority=802 与政策一致） |

## 4. 缺口与建议

- 缺口1（D14-G08）：政策命令 `python scripts/lock_files.py release <file> <owner>` 逐件释放与实现契约（release 需 ≥3 参：release <cmd-arg> <file> <owner>；会话整体释放=release-all）不一致——簿03 §5 判本段"真切不开"，X-20 待裁（与 D14-17 合并则本节点作废）。建议：政策命令块按实测契约改写；X-20 合并裁定随总包落。
- 缺口2：产出物"清理报告"与"禁创建报告文件"口径冲突。建议：产出物改为"清理确认进 handoff 包 warnings/清点行"，删报告字样。
- 缺口3：mark-completed 幽灵已由 sweep 三重判据替代——政策该行建议直接删除而非留注记（注记-正文并存的矛盾模式在 Step 9/10/11/12 重复出现，见各段汇总建议）。
