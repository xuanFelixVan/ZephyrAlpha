---
ttl: task_bound
completes_when: 图11 封矿且 D11-S04~S06 环节进 config/dev_delivery_map.yaml 四件套后本件转归档参考
title: 图11 作业簿02·claim 协议与暂存晋升（D11-S04/S05/S06，含 S05 🔨 定性实证）
owner: st-mapbuild-20260924（W-A1 车道）
---

# 02_claim协议与暂存晋升

## §0 覆盖环节

- **D11-S04** 改前 claim（文件锁+基线快照）
- **D11-S05** 在途编辑与暂存晋升（骨架标 🔨，本簿定性收口）
- **D11-S06** 会话内 worktree 提交

族职责一句话：把"谁在改哪个文件、从哪个基线改起"钉成双层机器台账（.ailocks 文件锁 + SessionRegistry held_files），改完在隔离 worktree 内自带门禁地变成 commit。

引用避坑同簿 1（不写 `裁定#<数字>` 紧邻与 `宪法 §N.M` 裸挂形态）。

---

## §1 D11-S04 改前 claim（文件锁+基线快照）

### 上
- 触发：宪法冷启动序列第 3 条"改前 claim：`lock_files.py acquire <file> <sid>`"（AGENTS 宪法原文，人侧指令面）；机器侧前置= S02 已注册 session。
- 输入：待改文件清单 + session_id + `AcquireOptions`（`lock_files.py:422`，含 task/ttl）。

### 下
- ①`.ailocks/` 锁目录 owner.json + registry（`_write_owner` :272 / `_add_to_registry` :1354，registry 互斥 `_registry_mutex` :116，超时 5s 即 DENIED :790）；②SessionRegistry `held_files`（`session_concurrency.py:606 claim_file`）；③gateway `claim_files` 基线快照（下「内」）→ 消费方=FOREIGN-CHANGE-DETECTION gate（commit 时对比，`commit_gates/foreign_change_gate.py`）、S06/S07 阻断判定、S08 salvage、C03 结算（他簿）。
- CLI 快速路径：`git_commit.py:476 _handle_pure_claim`——`--claim-only` 成功 CLAIMED/部分冲突 **exit 7**（:494-501）；`--release-only` 走 `_release_and_verify` 校验后才报 RELEASED（:485-492）。claim 前移协议自 main() 抽出（:479）。

### 内（双层锁体系+基线，父-子-孙）
- **层 1：.ailocks 文件锁（scripts/lock_files.py）**
  - `cmd_acquire`（:549）= `_acquire_prepare`（:449）+ 入册；入册失败**回滚锁目录**防半锁（:558-562 注释"owner.json 存在但 registry 漏登记"）。默认 TTL `DEFAULT_TTL_S=1800.0`（:100，"AI 对话级锁 30 分钟"）。批量面 `cmd_acquire_batch`（:674）/`_add_many_to_registry`（:1315）。
  - 僵尸判据演化（核心分支）：`_is_stale`（:161）——owner 无 session_id=旧格式，维持 PID+TTL 语义（:202-203，2026-06-30 零窗口 PID 真源 TRAE-001）；owner 含 session_id=**裁定 252（2026-09-14）锁存活=会话存活**，探针切 `SessionRegistry._is_session_alive`（:167-198）；会话活但 claim 自身过期且静默超窗 → `_claim_expired_and_idle` 回收（:195/:225，T10 治本 2026-09-17，治"acquire 对 TTL 完全不敏感"的交接班互挡）；registry 不可达退回 PID+TTL fail-open（:200-201）。
  - 编辑期守卫：`pre_write_guard`（:1377）供写文件前软校验（FileLockedError :1364）。
- **层 2：SessionRegistry held_files（src/zephyr/security/access_control/session_concurrency.py）**
  - `claim_file`（:606）四分支：未注册→懒注册并**立即持久化**（:609/:622，即使冲突 session 仍可查）；他人持有→False（:624-632，冲突记 warning，调用方走 lock_files）；自持→幂等 True；无主→入 held_files + 顺带 `last_heartbeat=now` + **`last_activity=now`**（:636-637，claim 是真实治理操作=活性锚点，联动 S03 判死）。千件级批量 `claim_files_batch`（:674）/`release_files_batch`（:645）。
- **层 3：gateway 基线快照（GitCommitGateway.claim_files，src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:1257）**
  - ARCH-054：claim 成功即捕 `git diff HEAD -- <file>` 基线（:1260/:1303），存 `_claim_snapshots[session][abspath]`（:1324）；**tracker 92 幂等保基线**——本 session 已有记录不重捕获，"基线语义=首次 claim 时刻"，防 CLI 主流程重跑覆盖（:1306-1312）。
  - `adopt_prior_work=True`（裁定 0723 跨 session 续作）：实际基线 diff_size+sha256 落审计 `.runtime/claim_snapshots/{sid}_adopted.jsonl`（`_log_adopted_work` :1320），**存储空基线**让 FOREIGN-CHANGE 放行——与 allow_overlap 的区分逐字在 :1266-1267（"overlap=commit 时绕 gate；adopt=claim 时认领+附审计"）。
  - 性能治本：claim 千件两处 O(N²)（registry 整表重写+逐件 git 子进程）→ `claim_files_batch` + 一次 `git diff --name-only` 预判无 diff 件基线空串（:1269-1284；MagicMock 鸭子探测坑 :1272-1273）。
  - 持久化：快照落 `.runtime/claim_snapshots/`（`_CLAIM_SNAPSHOTS_DIR` :222；S3-C 治本 2026-07-17 崩溃可恢复，原纯内存 dict 崩溃即丢 gate 降级 PASS，:1016-1019/:1026 load_claim_snapshots_from_disk）。
  - **HOT-FILE-BASE-FRESHNESS**（2026-08-23 陈旧快照覆写事故）：`_claim_heads[session]=claim 时 HEAD sha`（:1021-1025，捕获 :1288-1292），commit 时 gate 对比 HEAD——上游推进且改到目标热文件=基于陈旧 base 工作；生命周期与快照同步 release 清理。
  - `release_files`（:1338）commit 后释放+清基线（:1341）。
- **HELD-OVERLAP 判定面**（本环节出口）：worktree 路径 `_check_held_overlap`（session_worktree.py:3074）逐件 `registry.claim_file`，任一失败→**已 claim 件全部回滚释放**（:3095-3100）再报 `HELD_OVERLAP_VIOLATION`（:3102-3112，提示等待 merge/abort 释放或 allow_overlap 逃生）；gateway 路径=HeldOverlapGate（网关头 INVARIANTS :8：命中 HELD_OVERLAP_VIOLATION 阻断，allow_overlap=True 放行并打 `[GW:<sid>:overlap]` 标记）。worktree 内提交跳过该 gate 的原因是 `_WORKTREE_SKIP_GATES`（:367 四件：HELD-OVERLAP/CLAIM-REQUIRED/FOREIGN-CHANGE-DETECTION/WORKTREE-REQUIRED）——隔离下无检测对象、自有 held 机制先行（裁定 D 治本 2026-07-19 禁硬编码数量，:369 注释）。
- 自动化程度：机检全自动；"改前必 claim"纪律由 CLAIM-REQUIRED gate 在 commit 时兜底硬拦（exit 6，`git_commit.py:13` 契约）。

### 下（输出）
- 见「上」段消费方；另 C03（失败保留/成功释放结算，`_retain_claims_after_failure` `git_commit.py:680` 把 .ailocks TTL 收窄至 `--failed-claim-ttl` 缺省 300s :34-36 + 审计 `.runtime/claim_snapshots/` jsonl :708-724；R-04 决策表单一真源在 `_settle_claims_after_commit` :743-746：OK/NOTHING_TO_COMMIT→释放，其余→保留）。

### 旁
- 撞 FOREIGN-CHANGE gate（C05 家族）：claim 是数据生产者、gate 是消费者——同一实体两环节，**引用**（骨架 §3 第 6 行 AGENTS 纪律=引用不另立）。
- 撞 git_commit_gateway 全局锁（C04）：claim 与全局锁是两个不同粒度（文件级 vs 提交流程级）→ 不并，**引用**。
- 五选一结论：本环节无跨图同职责对象，claim 语义唯一真源=此三层。

### 史
- claim 前移协议从 main() 抽出（git_commit.py:479"提取自原 main L301-315"）。
- 旧 `--release-only` 只释放 SessionRegistry 从不触 .ailocks（T10 病根，`git_commit.py:414` 注释）→ 现校验式释放。
- 原 finally 无条件释放 claim 是"CLAIM-REQUIRED×50/24h 循环源"（`git_commit.py:35-36` 逐字）→ R-04 语义（失败保留）即其治本。
- 旧格式锁（无 session_id，纯 PID+TTL）仍在语义面兼容（lock_files.py:171-172）。

### 新
- trust-hold 自动信任（2026-09-13 Owner 裁定，`foreign_change_gate.py:8` INVARIANTS）：本 session 独占持有+无他人 claim 快照痕迹→"先编辑后 claim"放行+落审计；死会话残留快照=P1 在场证据仍 BLOCK；读取异常 fail-closed 维持阻断。
- P1 post-claim 修改审计 warn-only（claim 后 commit 前变化记 `.runtime/gate_audit/post_claim_modifications.jsonl`，同上 :8）。

---

## §2 D11-S05 在途编辑与暂存晋升【🔨 定性收口：政策有文、专属 promote 代码无面=纪律-only+清理兜底环节】

### 上
- 在途编辑本体=worktree 内 Edit/Write（IDE 层，🌑 同骨架 §6🌑-1）；`staging/` 目录存放"AI Edit/Write 同步到 worktree 的中间产物"（`session_worktree.py:1782-1784` 注释逐字）。
- 政策输入：宪法 .runtime 卫生条（AGENTS 原文："暂存走 `.runtime/sessions/<sid>/staging/`（24h TTL，成果须 promote 到 docs/_working/ 才算交付）"）；共识件 §1 同款表述。

### 下
- 成果两条出路：①promote（人工 Write/cp 到 `docs/_working/`，无工具面——见「内」实证）；②24h 后被 TTL 清理（.md/.csv 疑似未 promote 成果=warn 后**仍删**）。

### 内（promote 代码面实查：全仓 grep "promot*" 交叉过滤，结论=无专属工具）
1. **命中排除法**（复跑命令见簿末 §实查-1）：全仓 .py/.ps1/.sh/.yaml 中 promote 与 staging/session/_working 交集仅三簇，全部**非同物**：
   - `reconciliation_registry.py:10997/:11076`：staging TTL reconciler 的"疑似未 promote 成果"**告警文案**（清理者，非晋升者）；
   - `allow_promote` 参数族（`file_placement_ttl_gate.py:67`；`session_worktree.py:4587/:4835-4837`）：语义=**永久区新增文件准入**（FILE-PLACEMENT-TTL 门禁逃生位，对应 `git_commit.py:13` exit 3"永久区晋升阻断"），与 staging→_working 晋升同名异物；
   - `ml_model_factory.py:222 promote_to_staging`：模型域反向操作（promote INTO staging），非本域。
   → **无任何代码实现 staging→docs/_working 的搬运/登记**。
2. **清理兜底三层**（这才是本环节真实机生面）：
   - `GATE-SESSION-STAGING-LIFECYCLE` reconciler：`make_session_staging_lifecycle_reconciler`（`src/zephyr/governance/audit/reconciliation_registry.py:10989`），trigger=任何 commit（扫 `.runtime/sessions/*/staging/` 成本<0.05s，:10993），`_STAGING_TTL_SECONDS=24*3600`（:11020），mtime>24h 文件删、`.md/.csv` warn 后仍清（:10995-11022），只扫 staging/ 子目录不碰 heartbeat 等同级件（:11007-11009）；priority=802（:10968 邻注释"session_staging=802"）；注册名 :179。
   - abort 即时清理：`_cleanup_session_staging`（`session_worktree.py:1779`，#ARCH-ROOT-TEMP-FILE-ENFORCEMENT-001）——merge **不**清（session 继续复用，:1788）；safe_rmtree 硬断言前缀 `.runtime/sessions`（:1799-1802，CAND-GOVSEC-001①）；fail-open（:1804）。
   - `.runtime` 通用 TTL：`make_runtime_cleanup_reconciler`（`reconciliation_registry.py:7677`，GATE-RUNTIME-CLEANUP，治 handoffs/reconcile_reports 线性增长，:7680-7685）——管总目录不管 staging 专项。
3. **骨架 🔨 表述的坐标修正（推翻其半，双证）**：骨架 S05 格写"TTL 清理由 `reconciliation_registry.py:7677 make_runtime_cleanup_reconciler` 兜底"——7677 存在但非 24h staging TTL 真源；双证=① `reconciliation_registry.py:10989-11022` 专项 reconciler（24*3600 常量在案）；② `session_worktree.py:1786` 注释逐字"等待 staging TTL reconciler（priority=802，24h TTL）兜底"。
4. **定性结论**：环节成立但**非机生流程**——"promote"是 AI 手工动作（纪律），机生面只有其反面（超时清理+漏晋升告警）。建议总包把骨架状态由 🔨 改"✅（纪律-only 定性完成，无独立 promote 代码面=实查结论非待发现项）"或维持 🔨 但在叶层标注两语义 promote 消歧（本簿不擅改）。
- 自动化程度：编辑=人机混合；清理=全自动；晋升=**纯人工纪律**。

### 旁
- 撞 FILE-PLACEMENT-TTL gate / exit 3"永久区晋升"（C05/C01 家族）：同名 promote、对象不同（新文件进永久区 vs 暂存成果进 _working）→ **引用**+图中两节点必须异名（防 INV-1 型混淆），坐标已列「内」-1。
- 撞宪法 .runtime 卫生条（AGENTS 第 9 域运维红线第 4 条）：政策文本=节点注解，**引用**不复制（骨架 §3 第 6 行同款纪律）。

### 史
- 该 reconciler 病根史完整在 `reconciliation_registry.py:10973-10985`：trae_071 §7 spec 过 priority=802 但**长期未实现**（被 sess-18504/sess-55092 拖延，持有阻塞）；触发事故=成果文件无声删除（**FINAL_resonance_rank.csv 事件**，:10979）+ 历史会话 staging 垃圾堆积；2026-07-22 落地补齐（#ARCH-TEMP-FILE-LIFECYCLE-001 / #ARCH-ROOT-TEMP-FILE-ENFORCEMENT-001）。
- 即时清理与 TTL 清理的正交设计声明（:10981-10985"事件语义=放弃/完成…两者正交互补"）。

### 新
- CAND-GOVSEC-001① safe_rmtree（resolve+前缀+reparse 硬断言）用于 staging 删除（session_worktree.py:1799-1802）——晚于 reconciler 的删除安全加固。
- 本簿实查即最新态：2026-09-24 主区 `.runtime/sessions/` 存在（含 sess-pytest-pool-A 等测试残留，只读 ls），未见 promote 登记类新工具。

---

## §3 D11-S06 会话内 worktree 提交

### 上
- 触发：`session_worktree_commit`（`session_worktree.py:4580` 公共壳，:4580-4590 签名）→ 选项聚合 `_opts`（allow_promote :4883 等，"monkeypatch 位清单"文档 :4774）。
- 输入=S04 claim 集 + worktree 内已编辑文件。

### 下
- 产物=session 分支上一个 commit（`session/<sid>`）→ 给 S07 merge；同时 `_write_commit_persisted_marker`（:5003←定义 :1723）落"已落盘证明"供跨进程续作（`_read_commit_persisted_marker` :1812 读回，`_clear` :1763）。
- 依赖登记：commit 成功路径 `registry.register_dependency(session_id, dep_sid)`（:4957）。

### 内（调用序全实证，四段+尾三闸）
1. **staging 段** `_wt_stage_changes`（:4647 起，impl :4764 之前）：HELD-OVERLAP（:4663，见簿 02 §S04 出口）→ **DCR 检测**（:4668←`_run_dcr_check` :3115：subprocess 调 `scripts/governance/d1_structure/check_directory_contract.py` :3127；**脚本缺失/执行失败=fail-closed 阻断** :3133/:3183；2026-07-19 显式注入 PYTHONPATH 治子进程 import :3146）→ **base 新鲜度（commit 档）**（:4693←`_ensure_worktree_base_fresh` :3312，裁定 19-B 2026-07-18：worktree HEAD vs 主区 HEAD 落后则自动对齐——无 session commit→`reset --hard <main HEAD>` 安全；有 commit→`rebase`，冲突 fail-loud 返回 `base_sync_failed=True` 阻断（头 INVARIANTS :15 全语义），治①搭便车提交污染 ②ARCH-REFERENCE L2 新引用误判）→ `_sync_files_to_worktree`（:4712←:3574）。
2. **门禁段** `_run_pre_commit_gates`（:4967←:3774 重试壳）：调 gateway 的 `_gate_registry.check_all` 跑全部 worktree-compatible gate，跳过 `_WORKTREE_SKIP_GATES`（:367）；**关键适配=monkeypatch `_gw.run_git` 重定向 cwd 到 worktree**，否则 `git diff --cached` 查主仓 index 返回空、gate 全体误判（头 :15 逐字）；重试 2/4/8s 三拍（`_GATE_RETRY_DELAYS` :3725，max 3 :3727；锁残留清理 `_cleanup_worktree_locks` :3730）；gate 违规→GATE_VIOLATION 阻断，**gate 框架异常→warn 不阻断**（降级面）。
3. **提交段** `_git_commit_in_worktree`（:4972←:3844）：直接 `git add+commit`——worktree 独立 index，**不走 GitCommitGateway 全局锁**（头 :15；这是与 C 道的主分岔，交接语义见骨架 §2 会话车道"merge 后等价于已 staged 变更集"）。
4. **尾三闸**：persisted marker（:5003）；堵点归因链（红蓝 v3 P1-2 治本 2026-09-14）`_wt_block_gate_id`（:4527：优先直取 `result.gate_results[0].gate_id`，因"拼接 message 正则恒失配落 UNKNOWN"；无 gate_results 回退标志字段+message 正则兜底）→ `_audit_wt_block_event`（:4482）→ `_print_wt_bottleneck_banner`（:4569）。
5. **stash 留痕六件套**（编辑"消失"误判治本，宪法并发第 8 条对应代码面）：`_write_stash_notice`（:7261）写 `.runtime/workspace_alerts/stash_notice.json` 恢复通道；`_check_stash_for_files` :3951 / `_scan_stash_for_files` :3992 / `_detect_changes_in_stash` :4170 / `_recover_changes_from_stash` :4206 / `_drop_session_pre_merge_stash` :4038（drop 归 S07 尾步）+ `_warn_if_changes_missing` :4322。骨架 S06 格引的 `:5254` 实为 **pre-merge 自动清洗**内的一次 stash 写点（`_pre_merge_auto_clean` 族，定义 :5283）——归 S07 面，见溢出 O5。
- 自动化程度：全自动（一次调用十来个内部阶段）；失败形态全 return dict 不抛（头 :15"所有函数返回 dict 不抛异常"）。

### 旁
- 撞 C06 暂存与提交本体（gateway `_commit_locked`）：两代提交面并存（gateway 共享 index+全局锁 vs worktree 独立 index 免锁），骨架 §2 已裁交接关系，处置=**融合**（图内两节点单边连接，不合并实现）。
- 撞 pre-commit shell 门禁（C07）：worktree commit 走 in-process gate 子集，shell 55 台经 GIT_INDEX_FILE 通道另论 → **引用**。
- 撞第二代 CLI（scripts/session_worktree.py exec 子命令带 commit 能力，:39 五命令）：融合待裁（溢出 O1 同批）。

### 史
- `--no-verify` 绕过漏洞 2026-07-03 治（直接 git commit 不过 gate → 引入 `_run_pre_commit_gates`，头 :15 逐字）。
- ARCH-041：worktree 绕 gateway 致 directory_contract 不触发 → 2026-07 补 DCR subprocess 对标（:3115 docstring）。
- 裁定 D 2026-07-19：gate 数量/_WORKTREE_SKIP_GATES 成员禁硬编码进文档注释（:369/:15 内嵌纪律）。
- monkeypatch cwd 适配为后补关键件（初版 gate 在主仓 index 上空跑）。

### 新
- 红蓝 v3 P1-2（2026-09-14）堵点归因链（:4527）——commit 被拦时把 gate_id 精确写进堵点台账，替代 message 正则猜测。
- tracker 92 单一真源 skip 面（gateway 头 :8 末段：wt_session 非 None 时 skip=_WORKTREE_SKIP_GATES，"物理隔离下无检测对象，对齐 merge 预演口径"）。

---

## §末-1 溢出条目

| # | 条目 | 建议落点 | 证据 |
|---|------|---------|------|
| O5 | 骨架 S06 真源格"`:5254/7261` stash 留痕"：5254 属 pre-merge 自动清洗（`_pre_merge_auto_clean` :5283 调用链，S07 面），7261 为公共函数定义；S06 面 stash 家族应指 :3951-:4322 六件套 | S06/S07 真源格对调补注 | session_worktree.py:5254 上文即 "session_worktree_pre_merge: stashed"（:5257 日志） |
| O6 | S05 状态标记定性建议（🔨→"纪律-only 实证完成"）+ promote 双语义消歧条目（allow_promote=永久区准入≠staging 晋升） | S05 状态列+C05 叶层 | 本簿 §2「内」-1 全证据链 |
| O7 | S04 真源格建议补：`pre_write_guard`（lock_files.py:1377）、`_claim_expired_and_idle`（:225，T10 2026-09-17）、HOT-FILE-BASE-FRESHNESS（gateway:1021，2026-08-23） | S04 真源映射 | 各行号 |
| O8 | C03 与 S04 存在同一 R-04 决策表双写风险（`git_commit.py:743 _settle_claims_after_commit` 自述"单一真源"在 CLI 层）：图节点引用口径需总包定 | S04/C03 交接注 | git_commit.py:743-746 |

## §末-2 自审裁定

**干**。六向齐；S05 🔨 定性按任务要求实查收口（结论+排除法+兜底三层+骨架坐标推翻双证）；S04 三层锁体系与 S06 四段链全部行号化。溢=4 条（O5-O8）。欠账：无方向性缺失；S06"孙层"中 `_git_commit_in_worktree` 内部 add/commit 细节未逐行（属叶层，停止判据：同生产者同口径不再拆）。

## §末-3 实查命令（可复跑）

```bash
cd D:/ZephyrAlpha/.aidrafts/st-mapbuild-20260924
# 1) promote 代码面复判（应为空集：staging 晋升工具）
grep -rniE "promot" --include="*.py" --include="*.ps1" --include="*.sh" --include="*.yaml" scripts src config \
  | grep -iE "staging|sessions/|_working" | grep -v "疑似未 promote\|promote_to_staging\|allow_promote"
# 2) staging TTL 双证
grep -n "_STAGING_TTL_SECONDS\|_SUSPECTED_OUTPUT_EXTS\|def make_session_staging_lifecycle_reconciler" src/zephyr/governance/audit/reconciliation_registry.py
grep -n "priority=802，24h TTL" src/zephyr/gov_enforcement/rule_bridge/session_worktree.py
# 3) claim 三层 API 面
grep -n "def cmd_acquire\|def pre_write_guard\|def _claim_expired_and_idle" scripts/lock_files.py
grep -n "def claim_file\|def claim_files_batch" src/zephyr/security/access_control/session_concurrency.py
grep -n "def claim_files\|_claim_heads\[" src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py
# 4) S06 调用序（staging→gates→commit）
grep -n "_check_held_overlap(root\|_run_dcr_check(root\|_ensure_worktree_base_fresh(root, wt_path, session_id\|_sync_files_to_worktree(root\|_run_pre_commit_gates(root\|_git_commit_in_worktree(" src/zephyr/gov_enforcement/rule_bridge/session_worktree.py
```
