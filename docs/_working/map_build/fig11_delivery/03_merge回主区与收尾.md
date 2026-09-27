---
ttl: task_bound
completes_when: 图11 封矿且 D11-S07~S09 环节进 config/dev_delivery_map.yaml 四件套后本件转归档参考
title: 图11 作业簿03·merge 回主区与收尾（D11-S07/S08/S09）
owner: st-mapbuild-20260924（W-A1 车道）
---

# 03_merge回主区与收尾

## §0 覆盖环节

- **D11-S07** 合并回主区（merge 正门）
- **D11-S08** 放弃与死会话回收（abort + salvage）
- **D11-S09** 收尾注销与 handoff 交接

族职责一句话：会话的三种终局——成果进主区（merge）、成果作废（abort/salvage）、身份注销（handoff+unregister）；每个终局都留可复原证据。

引用避坑同簿 1。

---

## §1 D11-S07 合并回主区（merge 正门）

### 上
- 触发：`session_worktree_merge`（`session_worktree.py:6714`；参数 `reconcile_verify=True` 默认 :6718、`allow_migration` :6719、`force`——force 使用受审计 :6770 调 `_audit_force_merge_usage` :6682）。
- 规范输入：宪法收尾序列第 1 步"任务完成=merge 回主分支（放弃走 abort）"（AGENTS 并发与提交第 9 条）。
- 前置事件：S06 已在 session 分支产出 commit；主区脏工作树由 auto-clean 处理（见「内」步 3）。

### 下
- 产出=主区（dev）新 commit（`WorktreeManager.merge_session_worktree` `--no-ff` + `_WorktreeLock` 串行化，头 INVARIANTS :15）→ 主区变更再要流转即入 C 道正门（骨架 §2 交接点）；post-merge reconciler 链（:7147-7148 `_run_post_merge_reconcile` :6555←`_run_reconcilers_after_merge` :5578/同步版 :5685）可自产 commit（环路已在骨架 §2 声明）。
- 收尾动作：kill heartbeat daemon（:7161）、drop pre-merge stash（:7184←`_drop_session_pre_merge_stash` :4038）。

### 内（八步序全实证，按 merge 体内行号）
1. `_audit_force_merge_usage`（:6770）——force merge 计数审计。
2. **PRE-MERGE-TOPO-CHECK** `_run_pre_merge_topo_check`（调用 :6954←定义 :5828）：subprocess 调主区副本 `check_blueprint_code_alignment.py --json --scan-root <worktree>`（头 :15：MAIN 副本有 DB 配置，--scan-root 仅重定向代码扫描）；HIGH drift（ORPHAN_MODULE_ID/MODULE_ID_DRIFT）**阻断 merge** 且**只过滤 session 自身变更文件**；LOW（CODE_NOT_IN_DEPGRAPH）暂态容忍；降级三分：checker 缺失 fail-closed、DB 不可用/超时/JSON 解析失败 fail-open（`_log_topo_failopen` :5796 留痕）。时序铁律：必须在 auto_clean **之前**（2026-07-17 修复：auto_clean 会把 checker 还原到 HEAD 旧版导致降级——头 :15 逐字）。
3. **auto-clean** `_pre_merge_auto_clean`（:7076←定义 :5283）：主区脏文件收集 `_get_dirty_files` :5042/`_get_clean_target_files` :3916/追踪+未追踪两族 `_collect_tracked_cleanups` :5059/`_collect_untracked_cleanups` :5127/`_execute_cleanups` :5203；被他人 claim 的文件跳过（`_get_other_session_claimed_files` :5374）；stash 留痕+`stash_notice.json`（:5254→`_write_stash_notice` :7261，日志 :5257"recoverable via git stash pop"，宪法并发第 8 条对应面）。
4. **pre-merge gate 预演** `_pre_merge_gate_check`（:7115←定义 :6025）：`git reset --soft merge-base` 模拟 staged 跑 worktree-compatible gate 子集，阻断则 merged=False，HEAD 用 `reset --soft orig_head` 恢复（头 :15）。**重大事实**：常量 `_PRE_MERGE_SKIP_ALL_COMMIT_GATES = True`（:389）——#ARCH-WORKTREE-PRE-MERGE-SYSPATH-001 治本（2026-07-20，:371-387 注释逐字）：pre-merge 阶段因主区 sys.path 与 worktree 代码版本错位会 ImportError 假阻断（DIRECTORY-CONTRACT/TTL-METADATA/ENCODING-SAFETY/RULE-FOUR-WAY-ALIGN），**现行为=只保留 TOPO-CHECK、跳过所有 commit gate**，理由"commit gate 价值已被拓扑检测覆盖，质量类 gate 不依赖主分支状态 pre-commit 跑一次即够"（:385-387）。即第 4 步代码在盘但**默认整体短路**——骨架 S07 格"`:6025 _pre_merge_gate_check`"仍真但语义需加此 flag 注（见溢出 O9）。
5. **执行合并** `_execute_merge_and_build_msg`（:7133←:6479）→ `_merge_with_retry`（:6379）冲突分类 `_classify_merge_failure`（:6311）。
6. **reconcile_verify**（:7147 条件 `reconcile_verify and merged and cleaned`）→ `_run_post_merge_reconcile` :6555（manifest/path_tree/path_ownership/depgraph_ops 等 auto_commit+warn-only，头 :15）。
7. kill daemon（:7161）；8. stash 袋处置（:7184）。
- 配套 CLI 面：`git_commit.py:1053 --merge-finalize`（B2 治本①，AI-FILL-14 截胡事故 2026-08-19，:1056 help 逐字）——gateway 侧 MERGE_HEAD 存在时普通 commit 一律拒（`CommitStatus.MERGE_IN_PROGRESS` 枚举 `git_commit_gateway.py:451`；检查 :2381 `if not merge_finalize and self._is_merge_in_progress()`，二验 :2506/:2564；finalize 全量提交 :2429）；`--enqueue` 与 `--merge_finalize/--reconciler-verify` 互斥（:826-827）；exit 10 契约（`git_commit.py:13`）。
- **`--reconciler-verify` 三前置**（主区 clean/无活跃会话/claim 全成）：真源=AGENTS 冷启动序列第 3 条原文；代码面本次未逐行定位（登记为待补，缺=三前置的 assert 位置）——不猜。
- 自动化程度：全自动，唯 force/allow_migration 是人机闸。

### 旁
- 撞 C10 真落盘（队列侧 merge 语义）：骨架 C10 格"主区快进收敛"与 S07 是两个物理面（队列 worktree 落地 vs 会话 worktree 合并）→ **引用**互指不合并（骨架 §2 交接点原文维持）。
- 撞第二代 CLI `cmd_merge`（scripts/session_worktree.py:293，`--no-ff`/`--squash`/`--yes`，merge 需用户确认 :10）：**融合待裁**（与簿 1 O1 同批——两代 merge 并存，图11 收敛基准需点名第二代）。
- 撞 pre-commit gate 族（C05/C07）：第 4 步只是**复用** gate registry 执行位 → 不构成独立环节（停止判据：同生产者同验证口径）——此即骨架 §1"拆的边界"示例所指的实体。

### 史
- 时序修复 2026-07-17（topo-check 前置于 auto_clean）。
- pre-merge gate 检查 2026-07-04 立、2026-07-20 被 SYSPATH 治本整体短路（第 4 步「重大事实」）——"建了又关"的完整演化在 :389 一个常量+注释里。
- B2 治本① AI-FILL-14 截胡事故（gateway:451 注释）；#ARCH-DEP-001 第二期 topo-check（头 :15）。
- reconcile_verify 默认 True 自 2026-07-04（头 :15"merge 后自动触发所有已注册 reconciler"）。

### 新
- 裁定 D 2026-07-19：merge 面的 gate 数/reconciler 数全部"以实际注册为准不硬编码"（头 :15 三处）。
- 红蓝 v3 P1-2（2026-09-14）归因链同样覆盖 merge 阻断路径（`_wt_block_gate_id` 的 gate_results 直取，`git_commit_gateway.py:1889` 同族 WORKTREE-REQUIRED 直取点）。
- 外部对标一句话：等价于 GitHub PR merge queue 的"merge 前预演+CI 重跑"，本项目以 topo-check+（已短路的）gate 预演替代独立 CI，且把合并串行化押在 `_WorktreeLock` 上。

---

## §2 D11-S08 放弃与死会话回收

### 上
- 主动面：`session_worktree_abort`（`session_worktree.py:7497`，宪法收尾"放弃走 abort"）。
- 被动面：`lock_files.py:786 cmd_cleanup(auto_salvage=True)`（cleanup 顺带 salvage，DEF 参数 :786）与显式 `cmd_salvage`（:1235，`--dry-run` 支持）；死会话 stale claim 挡道逃生=网关 `release_files`（`git_commit_gateway.py:1338`，宪法并发第 7 条）。

### 下
- abort 产物：quarantine 存证 patch（`.runtime/quarantine/<sid>-retire-<ts>.patch`，`_generate_retire_patch_evidence` :957；脏文件>0 先生成，证链失败 **fail-closed 不删 worktree**，:73-75 注释+先例"sweep quarantine ref 保存失败不清理"）→ `_log_worktree_delete` :465（Phase 4 遥测删除点，abort 内调用约 :7598）→ kill daemon（约 :7631）→ `_cleanup_session_staging`（约 :7649←:1779）→ `registry.unregister`（约 :7652←session_concurrency.py:473）。
- salvage 产物：三件套处置+全量审计 `.ailocks/salvage_audit.jsonl`（`_salvage_audit` :918，路径 :921 `LOCK_ROOT/salvage_audit.jsonl`，fail-open）→ 活会话零打扰（判死证不足即整体不动）。

### 内（abort 小面 + salvage 大面）
- salvage 主入口 `salvage_dead_session`（:1160 docstring 即完整契约）：
  - **双证判死** `_death_evidence`（:983）：证据①=registry 有条目且 `_is_session_alive`=False（心跳超 90s/PID 亡/TTL 超），无条目则退"全部 claim PID 死/零"进程证（零 claim 且无条目=无任何死亡证据→不成立）（:991-994）；证据②=全部 .ailocks claim `expires_at<now`（任一新鲜不回收——"会话可能处心跳间隙但 claim 新鲜，正在干活"）；无 .ailocks claim 时仅当①是"条目证死"才成立（裁定 252 锁存活=会话存活语义的延伸，:995-999）；判活设施异常=fail-closed 不判死（:1015，方向=防误收）。S18 R-10 反例红线"误收活会话"逐字在 :989。
  - 三件套（:1169-1173 契约+实现）：①主区该会话 MERGE_HEAD→`git merge --abort`（归属判定 `_merge_head_attributed_to` :1041，不明→`not_attributed` 保留待人工、绝不误 abort :1196-1199）；②其 claim 路径 staged/WIP→`git stash push` 归档禁丢弃可 pop（`_stash_claimed_paths` :1090；merge 存续且未 abort 时跳过——"**merge index 神圣**" :1214/:1224）；③释放全部 claim 两登记处（`.ailocks` `_force_release_locks` :1129 + SessionRegistry `_force_release_session_registry` :1143）。
  - `dry_run=True` 只判证与归因不动 git/锁（:1174）。
- worktree 侧配套（abort/sweep 共享）：退役文件三分类 `_classify_retire_file_content`（:895，derived/crlf_phantom/substantive 常量 :858-860）；force-clean 四证明审计 `_audit_sweep_force_clean`（:789：证 3"统筹批准=AUTO（72h quarantine 窗=软批准）"、证 4 可恢复=quarantine ref 前置补偿 :801-828）；quarantine ref 保存/恢复配方（`_quarantine_branch_ref` :749，恢复命令逐字 :758）。
- 自动化程度：cleanup/salvage 全自动（双证门控）；MERGE_HEAD 归属不明自动降级人工。

### 旁
- 撞 `worktree_drift_watchdog`（吸收，骨架 §3 第 8 行）：其头 INVARIANTS #ARCH-308 A1"死会话清扫只卸 staged/删 claim 快照/释放锁（工作树内容永不销毁——git reset HEAD 仅动 index；_adopted.jsonl 审计证据永不删；**PID 存活会话即使心跳超时判死也不清扫**——保守双检）"=本环节第三套清扫器（对象=漂移 watchdog 视野内的会话，与 salvage 判死口径同源 `_is_session_alive`）→ S08 子环节，**吸收**成立。
- 撞 `worktree_lifecycle` 状态机 quarantined 态（created/active/idle/quarantined…，config/worktree_state_machine.yaml states 段）：本环节即 created/active→quarantined/退役转换的执行面 → **引用**状态表。
- 撞宪法并发第 8 条（编辑"消失"=stash 非丢失）：处置=引用（S06/S07 已挂代码坐标）。

### 史
- "被回收"事故的规则化：S18 R-10 反例红线（lock_files.py:989 注释点名"误收活会话"）；merge index 神圣条款（:1224）。
- 2026-06-30 锁体系零窗口 PID 判死（:202-203）→ 裁定 252（2026-09-14）锁存活=会话存活改判活轨（:167-172 逐字"acquire 后锁即被自清理，防线永不命中"红蓝 v4 F2/v4.5 实弹）。
- 旧 cleanup 无 salvage（cmd_cleanup auto_salvage 参数化=后补，:786 签名）。

### 新
- T10（2026-09-17）`_claim_expired_and_idle`（:225）进判 stale 链（簿 02 S04 同款，此处影响 salvage 证据②的新鲜度判据）。
- watchdog #ARCH-308 A2（2026-09 后）派生自动收敛"零在场会话"双检（`list_active ∪ raw PID`）走 `_commit_auto` 无递归——与队列 C12 改道衔接（跨簿交接点）。

---

## §3 D11-S09 收尾注销与 handoff 交接

### 上
- commit finally 自动：`git_commit_gateway.py:3538-3545`（P4-T2：`CommitStatus.OK` 才 `session_shutdown(session_id, summary=full_message)`，import :3541，失败仅 warn :3544-3545"crash recovery"定位注释 :3538）。
- 人工面：宪法收尾序列（merge 回主→release 全部 claim `git_commit.py --release-only`→staging 成果 promote 或确认 TTL→（多会话）写 handoff→汇报）；close-door STEP0。

### 下
- `handoff_<sid>.json` → 下一会话 S01 `read_latest_handoff()`（session_concurrency.py:839-850 按 mtime，:842 注"供 session_startup 读取上一 session 交接——跨 session 上下文恢复"）。
- close-door 断言消费 `list_active()`（政策 §6 原文命令 :219-222：活跃 >1 → assert 失败，"关门前须协调"；语义三条 :224-228：handoff 交接+等待完成或显式注销，仅 ≤1（自己）方可关门）。

### 内
- 父：`SessionHandoff`（`session_concurrency.py:786`，docstring：P2-SES，对标 drift_detector/blueprint §6.14 Cross-Session HandoffPackage，存储 `.runtime/handoffs/`，常量 `_HANDOFF_DIR` :171）。
- 子①`write_handoff`（:798-829）：五字段 package `{session_id, timestamp, summary, pending_tasks[], warnings[]}`（:806-812）；**per-pid tmp 名**治跨进程互踩（:814-815 注释逐字"共享 tmp 名跨进程互踩报 WinError 2"）+`os.replace` 原子落盘（:821）；失败 unlink tmp 仅 warn（:824-828）。
- 子②读面：`read_handoff`（:831）/`read_latest_handoff`（:839，首次运行无文件返回 None :843）。
- 子③注销链：`session_shutdown`（phase_manager.py:368-390，返回 {written,path}，K8s preStop 对标 :372）；`unregister`（:473）；claim 释放（网关 release_files :1338 + lock_files cmd_release :635/batch :722/release_all :753）；heartbeat 文件清理（`cleanup_heartbeat_file`，簿 01 S03）。
- 政策 schema 对账：政策 §4.3 交接包 schema（policy:183-196 示例五字段）与代码 package 五字段**一致**（session_id/timestamp/summary/pending_tasks/warnings）；时间格式差异（政策示例 ISO 字符串 vs 代码 `time.time()` epoch float :808）=叶级偏差，图节点挂 schema 双坐标即可（溢 O10）。
- 自动化程度：每次成功 commit 自动写（非仅会话终——summary=该 commit message，粒度=commit 级快照）；close-door 断言=人工触发机检。

### 旁
- 撞 S01 读端=同件两面 → 图内单边（handoff 写/读对，骨架 S01 格已用 read_latest_handoff 作「上」输入，无重复建设）。
- 撞政策文档（parallel_session_coordination_policy §2-§6）：契约文本，处置=**吸收**（其 schema/路径作为 S03/S09 节点挂载件——骨架 §3 第 3 行判定维持，本簿提供代码行号支撑）。

### 史
- 接入史（政策 §8 实现状态表逐字，:245-255）：SessionRegistry ✅落地+✅接入 commit path（P4-T1 commit 2a5ebe48）；SessionHandoff ✅落地+✅接入 session_shutdown（P4-T2 commit 01a99f1f+da66d3d0）；SessionConflictDetector ✅落地但 **P4-T1 用 claim_file 取代**（"更简洁，session 隔离 stash 内联实现"）—— detector 类仍在盘（:861）=有壳无消费主链；close-door STEP0 ✅（P1-T1，"P4-T1 落地后 registry 有数据，检查真正有效"）。
- 骨架 S09 格"政策 §8 L250 已接入"复核**成立**（该行在 §8 表 SessionHandoff 行）。

### 新
- 主区实查（只读，2026-09-24）：`.runtime/handoffs/` 非空（handoff_A.json、handoff_AI-NIGHT-A2-001.json…），与骨架"实查非空"一致。
- handoff 被 GATE-RUNTIME-CLEANUP 纳管（reconciliation_registry.py:7682"handoffs/（700+ session 交接包）"容量病根）——写端与 TTL 端配对，图节点应带清理边。

---

## §末-1 溢出条目

| # | 条目 | 建议落点 | 证据 |
|---|------|---------|------|
| O9 | S07 真源格须加 `_PRE_MERGE_SKIP_ALL_COMMIT_GATES=True`（:389）：pre-merge gate 预演默认整体短路、唯 topo-check 存活——否则施工者照骨架读 :6025 会误以为 gate 在拦 | S07 状态列/真源格加注 | session_worktree.py:371-389 注释块 |
| O10 | S09 交接包 timestamp 字段政策示例（ISO）与代码（epoch float）不一致 | S09 叶层注 | policy:183-196 vs session_concurrency.py:808 |
| O11 | `--reconciler-verify` 三前置（主区 clean/无活跃会话/claim 全成）的代码 assert 位本簿未定位（缺=在 gateway 或 CLI 的 assert 清单）；政策/宪法层有文 | S07 待补行 | 本簿 §1「内」登记为待补 |
| O12 | SessionConflictDetector 类在盘但政策 §8 自述"已被 claim_file 取代"——退役评估候选（零消费面需 W-C/W-D 簿交叉确认后再定，不单车道动） | S09 史向注 | policy §8 表第 3 行；session_concurrency.py:861 |

## §末-2 自审裁定

**干（S07 含一处点名待补）**。六向齐；S07 八步序全行号化并抓到"pre-merge gate 预演默认短路"这一骨架坐标会误导的事实（O9）；S08 双证判死+三件套+merge-index 神圣全落实；S09 政策 schema 与代码逐字段对账。欠=O11（reconciler-verify 三前置 assert 位，缺一行坐标，补法已写明）。溢=4 条（O9-O12）。

## §末-3 实查命令（可复跑）

```bash
cd D:/ZephyrAlpha/.aidrafts/st-mapbuild-20260924
# 1) S07 merge 八步调用序
grep -n "_run_pre_merge_topo_check(\|_pre_merge_auto_clean(root\|_pre_merge_gate_check(\|_execute_merge_and_build_msg(\|_run_post_merge_reconcile(\|_kill_heartbeat_daemon(session_id\|_drop_session_pre_merge_stash(root" src/zephyr/gov_enforcement/rule_bridge/session_worktree.py | grep -v "def "
# 2) pre-merge 短路常量（O9）
sed -n '371,390p' src/zephyr/gov_enforcement/rule_bridge/session_worktree.py
# 3) S08 双证与三件套
grep -n "def _death_evidence\|def salvage_dead_session\|merge index 神圣\|salvage_audit.jsonl" scripts/lock_files.py
# 4) S09 接入面
grep -n "session_shutdown" src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py | head -3
sed -n '245,255p' docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md
# 5) 活体面（主区只读）
ls /d/ZephyrAlpha/.runtime/handoffs | head -3; tail -2 /d/ZephyrAlpha/.ailocks/salvage_audit.jsonl 2>/dev/null | cut -c1-120
```
