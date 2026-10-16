---
ttl: task_bound
doc_type: mining_segment
campaign: mine_fullchain_20261015
segment_id: D14-17
figure: fig14 施工升级流（construction_workflow_map）
created: 2026-10-15
ssot: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-12-worktree-合并与清理有风险暂不清理 + 附录 D 锚块
---

# SD14-17 worktree 合并与清理（policy Step 12）

## 1. 定义

Step 11 清理完成后触发，施工任务到本域终态段：session_worktree merge 回 dev+merge 成功后清理 worktree+合并冲突暂不清理（保留逃生通道=终止分支 B14，非回边）。force merge 安全分类：不可绕过类（commit 持久性验证 `_read_commit_persisted_marker`+base 新鲜度 `_ensure_worktree_base_fresh(stage="merge")`）/可绕过类（WORKSPACE-CLEAN-CHECK/PRE-MERGE-TOPO-CHECK，有 reconciler 兜底）。commit 持久性标记 24h 免疫 sweep。冲突处理 MUST 走 merge_conflict_resolution_sop 三分法。会话收尾序列（宪法 §2.9）=merge 回主分支→release claim→promote→handoff→archive --execute 清车道。handoff_to=D11-S07/D11-S08/D11-S03。verified_scope=production（骨架 ✅）。

## 2. 六向台账

| 向 | 内容 | 路径证据 |
|---|---|---|
| 输入面 | 临时文件已清理（D14-16）；worktree 分支与 commit 持久性标记 | 政策 L714-787；`.runtime/locks/commit_persisted_<sid>.json`（trae_076） |
| 输出面 | worktree 清理确认；72h 隔离区 `refs/quarantine/<sid>`（force_clean 超龄未合并时）；stash_notice（abort 时） | `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py` §session_worktree_sweep/§session_worktree_abort；`.runtime/workspace_alerts/stash_notice.json` |
| SSOT 真源 | `trae_078_force_merge_safety.yaml#force_merge`+`trae_076_worktree_commit_persistence.yaml#commit_persist`+`trae_074_worktree_base_freshness.yaml#base_fresh`+`branch_strategy_policy.md`+`merge_conflict_resolution_policy.md`（三分法） | rules 三件在册+两政策件 |
| 代码模块 | `scripts/session_worktree.py`（CLI 实测子命令 create/exec/merge/abort/list/**archive**——archive 为骨架时点后新增第 6 子命令，本批 add_parser 实证 :1443；政策所指 status/commit/mark-completed/cleanup 四条仍不存在=D14-G07）+网关库同族 `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py`（heartbeat daemon 30s/三类并发阻断/Jaccard≥50%/breaking_change 避让/CROSS-COMMIT-DEP） | 两件在盘 |
| 门禁约束 | force=True 不可绕过 base freshness（#ARCH-FORCE-MERGE-SAFETY-001）；STASH-ACCUMULATION gate（>40 阻断/20-40 warn）；--allow-overlap 逃生（[GW:<sid>:overlap] 留痕+trae_069 阈值兜底）；分支策略 6 禁 | trae_078/074/076/069；`docs/01_policies_and_standards/policies/branch_strategy_policy.md` |
| 自动化触发 | heartbeat daemon 每 30s 刷活性（idle 1800s 自退→90s 后 registry 过期→held_files 释放）；sweep 三重判据（age>30min/不在 active 注册表/tip 在 HEAD 祖先）；archive --execute 死判→V判型→存证→remove→prune→branch -d 链 | 网关库 §符号锚；`AGENTS.md` §2.9 |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 收尾序列/持久性标记面明确 |
| 输出面 | warn | 清理确认无独立结构凭据（archive 台账=机生可查，部分覆盖） |
| SSOT 真源 | pass | 三规则册+两政策件在册 |
| 代码模块 | pass | CLI 子命令/daemon/sweep/quarantine 链实证；幽灵四子命令已入缺口账 |
| 门禁约束 | pass | force 不可绕过类/STASH gate/overlap 逃生三层 |
| 自动化触发 | pass | heartbeat/sweep/archive 三条自动化实证 |

## 4. 缺口与建议

- 缺口1（D14-G07 末段宿主）：政策 Step 12 注释块已自报"无 cleanup 子命令——R-06"（L727-730）但正文命令块仍列 `abort` 承担清理——实际正常收尾主通道已升级为 `archive --execute`（宪法 §2.9 与 CLI help"归档死车道"一致），政策未跟上。建议：政策 Step 12 命令块改写为 merge→archive --execute 序列，abort 保留给放弃场景。
- 缺口2：G07 的四条幽灵子命令在 2026-10-15 复核仍全部不存在（status/commit/mark-completed/cleanup）——gap 有效；但图证据"子命令集五项"已漂移为六项（+archive），machine_facts 重扫即可自愈。建议：无需人工干预，验证 machine_facts 刷新链路即可。
- 缺口3：本段是全链路收班环节，与图11 S07/S08/S03 及宪法 §2.9 三方口径并存（政策 Step 12/宪法/图11）——建议总包确认政策 Step 12 为操作手册、宪法为序列铁律、图11 为机制真源的三层关系并互相引用，防三处漂移。
