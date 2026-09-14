---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成（2 条，摘录）**
> - L161: # 偏航2: 新建 f_lock.md 提交被 CREATE-GUARD 拦（新 .md 要 creation_token，而登记处 _registry/ 是方案禁区）→ 换已入库的 f_stage.md 当争夺目标
> - L395: - lab 已入库 8 文件删除：docs 侧 4 个（f_stage/f_unreg/f_forge/f_scope）被 **reconciler 自动批提交 a8cc267636 吸收**（暂存区传送带现象再现——删除已入库但归属 reconciler，照实记录）；tests 侧 4 个走本人网
>
> **⚠️ 未完成（2 条，逐条摘录）**
> - L226: - 判定：**记录（未完成——被他会话半成品注册表引发的【全仓提交双通道 blackout】吞没：主网关 fail-closed + worktree fail-closed，全程无逃生提示）**。S2.5 本体（SPLIT 门验证）待注册表恢复后补测。此 blackout 本身是本轮最重要的可用性
> - L381: 4. **怪文件名批**（中文/空格/$/.md.md 四件）：连续撞**第二次 registry blackout**（CREATE-GUARD fail-closed，line 12149，`MM` 双重脏=某会话 staged 后继续改）——4 连败后停，未覆盖。文件已造好留在 lab 待清理
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 9 个，其中判废弃 1、路径漂移 0）+ commit 提及 19 处。
> **判废弃引用（C-1）**：`docs/_working/xt_lab3/f_bypass.md`
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）





# 极限红蓝对抗 v3 执行日志
执行者：GLM 5.3 Flash；开始时间：23:10；基线 HEAD：7a4efc8113
环境注：执行 shell 是 Git Bash（非方案假设的 PowerShell），命令按 bash 语法等价改写，改写过程如实记录。`&&`/heredoc 均可用。

### S1.1 裸 git commit 绕过网关
- 时间：23:12
- 操作：
```
printf -- '---\nttl: task_bound\n---\n\nbypass test\n' > docs/_working/xt_lab3/f_bypass.md
git add docs/_working/xt_lab3/f_bypass.md
git commit -m "raw commit bypass test"
```
- 系统反应：pre-commit hook 链启动，大量 gate 执行。第一次输出末尾有 `[WARNING] Stashed changes conflished... Rolling back fixes... [INFO] Restored changes from patch1789312274`（原文：Stashed changes conflicted with hook auto-fixes）。重跑确认拦截者：`GATE-DOC-NODE-ID: 文档物理ID硬编码检测 ....Failed` 和 `GATE-INTEGRITY: 规则文件完整性 golden hash 校验 ....Failed`。HEAD 未动（仍 7a4efc8113），文件保持 staged。
- 预期（蓝方应然）：被 pre-commit hook 拦。
- 判定：PASS
- 证据：git log -1 仍= 7a4efc8113；git status 显示 f_bypass.md 仍为 A（staged 未提交）。注：GATE-INTEGRITY 的 golden hash 失败疑似被工作区 155 个他会话脏文件连坐（本场景只加了 1 个无关 md），非本人文件触发，记一笔观察。裸 commit 路径未落堵点本（pre-commit hook 层拦截，非网关层，属预期）。

### S1.2 裸 git commit --no-verify
- 时间：23:14
- 操作：
```
printf 'more\n' >> docs/_working/xt_lab3/f_bypass.md
git add docs/_working/xt_lab3/f_bypass.md
git commit --no-verify -m "no-verify bypass"
```
- 系统反应：
```
[REFERENCE-TRANSACTION-GUARD] commit message 缺少 [GW: 标记
[REFERENCE-TRANSACTION-GUARD] 禁止用 git commit-tree + git update-ref 绕过 hook
[REFERENCE-TRANSACTION-GUARD] 合法通道：GitCommitGateway / session_worktree_commit / emergency_commit
fatal: ref updates aborted by hook
```
HEAD 未动。文件仍 staged。
- 预期（蓝方应然）：--no-verify 跳过 hooks 但靠纪律约束，畅通=协议级缺口记录。
- 判定：PASS（超预期——不止靠纪律，reference-transaction hook 技术性拦截了无 [GW:] 标记的 ref 更新，--no-verify 也逃不掉）
- 证据：上述输出原样；git log -1 仍= 7a4efc8113。

### S1.3 忘记前移 git add（staged blob 陷阱）
- 时间：23:16
- 操作：
```
printf -- '---\nttl: task_bound\n---\n\nv1\n' > docs/_working/xt_lab3/f_stage.md
python scripts/git_commit.py --session xt3-chaos-1 --files "docs/_working/xt_lab3/f_stage.md" --message "stage timing test"
```
- 系统反应：
```
SessionRegistry: claim_file auto-registering session=xt3-chaos-1 (not registered or dead/expired)
!! 提交堵点提醒（近 24h 共 26 次...）-- context: post_commit
   TOP: UNKNOWN ×6（P50 28s）；SPLIT-COORDINATION ×3（P50 11s）；CAPABILITY-OVERLAP ×3（P50 28s）
OK: committed 1 files (hash=f3bb4a39)
```
- 预期（蓝方应然）：提交成功，内容为 v1。
- 判定：PASS
- 证据：`git show f3bb4a39:...f_stage.md` 输出含 `v1`，内容正确；横幅在提交后打印（新功能生效）。UNKNOWN ×6 为治本前存量记录。

### S1.4 提交语法错误的 Python 文件
- 时间：23:17
- 操作：
```
printf '# [TTL] task_bound\ndef broken(:\n    pass\n' > tests/governance/rule_bridge/xt_lab3_syntaxerr.py
python scripts/git_commit.py --session xt3-chaos-1 --files "tests/governance/rule_bridge/xt_lab3_syntaxerr.py" --message "syntax error probe"
```
- 系统反应：`OK: committed 1 files (hash=2c6d1719)`——零拦截直接放行。堵点本最后一条仍是 15:08:36 UTC 的 CREATE-GUARD（他会话），无新行。事后 ast.parse 复核该文件确认 `SyntaxError: invalid syntax`。
- 预期（蓝方应然）：某个语法/AST 类门禁拦截，坏文件不进库。
- 判定：**FAIL（P0 候选：放行违规提交）**
- 证据：`git show 2c6d1719:tests/governance/rule_bridge/xt_lab3_syntaxerr.py` 内容含 `def broken(:`；堵点本无对应行。疑似语法类 gate 不扫 tests/ 路径或本场景文件太短未触发启发式——留给 Owner 归因。

### S1.5 提交假秘密文件
- 时间：23:19
- 操作：
```
printf 'API_KEY=sk-FAKE-1234567890abcdef\nPASSWORD=hunter2fake\n' > docs/_working/xt_lab3/fake.env
python scripts/git_commit.py --session xt3-chaos-1 --files "docs/_working/xt_lab3/fake.env" --message "fake secret probe"
```
- 系统反应：
```
FAILED: 门禁 DIRECTORY-CONTRACT 阻断: [GATE-DIRECTORY-CONTRACT] 2 个发现（2 errors, 0 warnings）:
  [error] DCR-005 docs/_working/xt_lab3/fake.env 扩展名 .env 不在 docs/_working/ 的 allowed 清单
  [error] DCR-008 ... 目录用途 task_document
```
堵点本新行：`15:14:31 | commit_blocked | DIRECTORY-CONTRACT | xt3-chaos-1 | main_gateway`（归因精确）。
- 预期（蓝方应然）：秘密扫描类门禁拦截。
- 判定：**记录**（文件确实没进库，git log 全历史 grep "fake secret"=0 条，fake.env 已删；但拦截者是目录契约而非秘密扫描——秘密扫描 gate 是否扫 docs/ 下 .md/.yaml 扩展名包裹的秘密内容，本场景没验证到，留待阶段 5 换皮再攻）
- 证据：堵点本 DIRECTORY-CONTRACT 行；`git log --all --grep="fake secret"` 输出 0 条。

### S1.6 未注册 session 提交
- 时间：23:21
- 操作：
```
printf -- '---\nttl: task_bound\n---\n\nx\n' > docs/_working/xt_lab3/f_unreg.md
python scripts/git_commit.py --session xt3-never-registered-xyz --files "docs/_working/xt_lab3/f_unreg.md" --message "unregistered session"
```
- 系统反应：`SessionRegistry: claim_file auto-registering session=xt3-never-registered-xyz (not registered or dead/expired)` 后直接放行，`OK: committed 1 files (hash=e933fecb)`。无拦截，堵点本无新行。
- 预期（蓝方应然）：自动注册（记录行为）或 CAPABILITY-LOOKUP/CLAIM 类拦截。
- 判定：记录（走了自动注册分支=方案预期之一；但任何凭空 session id 都能自注册，无需任何凭证，记一笔治理观察留给 Owner）
- 证据：hash=e933fecb 落库。

### S1.7 路径格式混乱（反斜杠/绝对路径混合）
- 时间：23:17（补记，本地=UTC+8；堵点本 timestamp 为 UTC，读数时需 -8h）
- 操作（跑了两次，第一次 tail 截断没看清，重跑抓全量）：
```
python scripts/git_commit.py --session xt3-chaos-1 --files "docs\working\..\_working\xt_lab3/f_unreg.md,D:\ZephyrAlpha\docs\_working\xt_lab3\f_stage.md" --message "path chaos"
```
- 系统反应：exit=8，两次均拦：
```
GATE-TRACKED-DRIFT VIOLATION: pre-commit gate 运行期 tracked 区发生写入 ... session=xt3-chaos-1——详见 .runtime/audit/hook_tracked_drift.jsonl
WORKTREE_VIOLATION: 非 worktree commit 且存在其他活跃 session（['solo_agent']）...逃生通道 --allow-non-worktree（2026-08-13 裁定 AI 可默认用，[GW:<sid>:non-worktree] 留痕）
```
未用逃生，保持被拦状态记录。堵点本归因 `WORKTREE-REQUIRED`（精确，非 UNKNOWN）✓。
- 预期（蓝方应然）：路径归一后正确处理或明确报错。
- 判定：**记录**（两点：① 混乱路径本身没引发崩溃或门禁误判，但 WORKTREE-REQUIRED 拦截使门禁触发面没测到；② 反常：同一拦截跑了两次，账本只有 1 行 WORKTREE-REQUIRED、drift 文件也只有 1 行 xt3-chaos-1——重复拦截不重复落账，是 undocumented 去重还是丢审计说不清，留给 Owner）
- 证据：账本 28 行稳定（sleep 3 后复测仍 28）；`grep -c xt3-chaos-1 hook_tracked_drift.jsonl`=1。另发现 drift 行 changed_files 列的是 5 个 project_handbook 文档——这些是基线时就脏的他会话文件（git status 快照可证），并非 gate 运行期新写入，疑似 TRACKED-DRIFT 误报（P2 候选）。

### S1.8 message 为空/只有空白
- 时间：23:20
- 操作：
```
python scripts/git_commit.py --session xt3-chaos-1 --files "docs/_working/xt_lab3/f_unreg.md" --message "   "
```
- 系统反应：`ERROR: message 不能为空`，未进入 gate 链，直接拒绝。
- 预期（蓝方应然）：被拦（message 校验）。
- 判定：PASS
- 证据：输出原样；账本行数维持 28（参数级校验不落堵点本——是否应落属口径问题，纯参数校验不落账记为合理）。

### S1.9 message 注入伪造 [GW:] 标记 ★P0
- 时间：23:23
- 操作（两发：第一发 f_unreg.md 无变更没测到门禁层；第二发换真有内容的 f_forge.md 让提交落地）：
```
printf -- '---\nttl: task_bound\n---\n\nforge marker payload\n' > docs/_working/xt_lab3/f_forge.md
python scripts/git_commit.py --session xt3-chaos-1 --files "docs/_working/xt_lab3/f_forge.md" --message "test [GW:xt3-fake-session:multi-domain] forged marker probe"
```
- 系统反应：`OK: committed 1 files (hash=c224e15d)`——伪造标记随 message 原样入库。全程零拦截（无 FORGED-GW-MARKER 类 gate、无 session 不匹配校验）。sleep 8 后复查 HEAD 仍是 c224e15d，POST-COMMIT-GUARD 未回滚；且 reconciler 提交 6bd5e07520 已叠在该伪造提交之下（作为其父提交），事后回滚难度被加大。旁证：本 run 打了 GATE-TRACKED-DRIFT VIOLATION 横幅但"降级 warn 不阻断"放行（与 S1.7 的 VIOLATION 处理路径不一致），drift 文件 xt3-chaos-1 行数 1→2，堵点本无新行（提交成功无 block 行属正常）。
- 预期（蓝方应然）：FORGED-GW-MARKER 类门禁拦截（宪法 §9.8：[GW:] 标记不可伪造，POST-COMMIT-GUARD 会 reset 回滚）。
- 判定：**FAIL（P0：伪造逃生标记放行——方案明示的重点靶子命中）**
- 证据：`git log -1 --format=%s` = `test [GW:xt3-fake-session:multi-domain] forged marker probe`；账本 28 行不变；drift 2 行。

### S1.10 提交后不收尾，同文件二次提交
- 时间：23:25
- 操作：
```
printf 'v2\n' >> docs/_working/xt_lab3/f_stage.md
python scripts/git_commit.py --session xt3-chaos-1 --files "docs/_working/xt_lab3/f_stage.md" --message "same session second commit"
```
- 系统反应：`OK: committed 1 files (hash=d3bab6e7)`，附带一条被截断的非阻断警告（"Investigate before proceeding (non-blocking warning)"，来源未及捕获）。
- 预期（蓝方应然）：同 session 二次提交正常（claim 基线刷新）。
- 判定：PASS
- 证据：git show d3bab6e7 内容含 v2。

**阶段 1 小结：S1.4（语法坏文件进库）、S1.9（伪造 [GW:] 标记放行）两个 FAIL，其余 PASS/记录。**

### S2.1 双 worktree 会话抢同一文件（HELD-OVERLAP 实弹）★
- 时间：23:28
- 操作（三步，有两次偏航照实记）：
```
# 偏航1: 直接 start 被 WORKSPACE_DRIFT_BLOCKED 拦（他会话 WIP: scripts/backtest/c4_batch_screen.py），按报错签名发现逃生参数后重试:
python -c "...session_worktree_start('xt3-red', allow_workspace_drift=True)"
# 偏航2: 新建 f_lock.md 提交被 CREATE-GUARD 拦（新 .md 要 creation_token，而登记处 _registry/ 是方案禁区）→ 换已入库的 f_stage.md 当争夺目标
python -c "...session_worktree_commit('xt3-red', ['docs/_working/xt_lab3/f_stage.md'], 'red claims f_stage')"   # OK d5eeea937a
python -c "...session_worktree_start('xt3-blue', allow_workspace_drift=True)"
python -c "...session_worktree_commit('xt3-blue', ['docs/_working/xt_lab3/f_stage.md'], 'blue steal attempt')"
```
- 系统反应：B 返回 `{'status': 'FAILED', 'ok': False, 'held_overlap': True}`，message=HELD_OVERLAP_VIOLATION（可读，含 allow_overlap 逃生指引）。堵点本末行：
```
gate_id=HELD-OVERLAP | session=xt3-blue | source=worktree_commit | files_count=1 | gate_chain_ms=140 | detail=HELD_OVERLAP_VIOLATION: ...f_stage.md
```
三要素全中。横幅也打（context=worktree_commit）。
- 预期（蓝方应然）：B 被拦 held_overlap:True；账本行 gate_id=HELD-OVERLAP + source=worktree_commit + session=xt3-blue；输出末尾有堵点横幅。
- 判定：PASS
- 证据：账本原样 JSON（上）。**附带发现（子项）**：偏航2 的 CREATE-GUARD worktree 拦截落账时 `gate_id=UNKNOWN`（source=worktree_commit 正确）——07b4217334 只映射了六类专用状态，六类之外的 gate 在 worktree 路径被拦仍归因 UNKNOWN（P1 候选：UNKNOWN 复活路径）。

### S2.2 B 用逃生通道 allow_overlap 强抢
- 时间：23:29
- 操作（跑了两次，第一次只看到尾巴，重跑抓全量）：
```
python -c "...session_worktree_commit('xt3-blue', ['docs/_working/xt_lab3/f_stage.md'], 'blue overlap escape', allow_overlap=True)"
```
- 系统反应：过了 HELD-OVERLAP（held_overlap=None），但 gate 链内被 WORKTREE-REQUIRED 拦：`WORKTREE-REQUIRED: 非 worktree commit 且存在其他活跃 session（['xt3-red']）`——**此调用明明走的是 worktree 通道，报错却称"非 worktree commit"**。报错建议的逃生 `commit(allow_non_worktree=True)` 在 session_worktree_commit 签名中不存在（inspect 实证 False），逃生链不闭合。账本两行均为 `gate_id=UNKNOWN | source=worktree_commit`——WORKTREE-REQUIRED 属六类专用映射之一，主网关路径归因正确（S1.7 实证），worktree 路径却归因 UNKNOWN。
- 预期（蓝方应然）：allow_overlap 放行（逃生通道设计内）。
- 判定：**FAIL（逃生链不闭合 + 归因 UNKNOWN，P1/P2 边界）**
- 证据：账本 15:27:01 + 15:27:15 两行 UNKNOWN；inspect 签名无 allow_non_worktree。旁证：同门下两次重复拦截落了两行账——S1.7 的"重复拦截只落一行"不是全局去重，成因待查。

### S2.3 worktree 与主网关同时打同一文件
- 时间：23:31
- 操作：
```
printf 'gw touch\n' >> docs/_working/xt_lab3/f_stage.md
python scripts/git_commit.py --session xt3-gw-side --files "docs/_working/xt_lab3/f_stage.md" --message "gw vs worktree contention"
```
- 系统反应：`CLAIM_REQUIRED_VIOLATION: session 'xt3-gw-side' 已注册但目标文件未 claim ... 添加 --allow-overlap 重新执行`。另见两条 warn（ZEPHYR-ENV-DIRECT-ACCESS / CAPABILITY-OVERLAP）点名他会话 staged 文件（scripts/backtest/*.py，warn+审计不阻断）。账本末行：`15:29:25 | CLAIM-REQUIRED | xt3-gw-side | (无source字段=主网关规范) | files_count=1`。
- 预期（蓝方应然）：主网关 HELD-OVERLAP / FOREIGN-CHANGE 拦，归因精确不许 UNKNOWN。
- 判定：PASS（实际拦停者是 CLAIM-REQUIRED 而非 HELD-OVERLAP——语义都成立：xt3-gw-side 从未 claim 过该文件，claim 检查先于 overlap 检查触发；归因精确）
- 证据：账本行原样。

### S2.4 5 路并发主网关提交（不同文件）
- 时间：23:34
- 操作：
```
for i in 1..5: printf ttl头 > docs/_working/xt_lab3/f_para_$i.md
for i in 1..5: python scripts/git_commit.py --session xt3-par$i --files "...f_para_$i.md" --message "parallel $i" &   # 5 后台进程
sleep 90
```
- 系统反应：**5/5 全灭，零落地**。par1/2/3/5 = `WORKTREE_VIOLATION: 非 worktree commit 且存在其他活跃 session（['xt3-red','xt3-blue','xt3-par5',...]）`——五路并发**互相把对方当成"其他活跃 session"违规**，自阻塞死锁语义（谁先抢到锁谁也过不了门）。par4 = `CLAIM_REQUIRED_VIOLATION`（与另外 4 路不同的门）——并发下 claim 自动化步骤出现竞态，同操作拦截原因不确定。账本 5 行归因全精确（WORKTREE-REQUIRED×4 + CLAIM-REQUIRED×1，source 均主网关）。无 traceback、无锁死、全局锁串行化本身没崩。另：测试期间他会话 solo_agent 正常落了一笔 feat(backtest) 提交（5411f0b548），主仓未受并发攻击波及。
- 预期（蓝方应然）：5 笔全部成功（全局锁串行化，互不吞）。
- 判定：**记录**（方案预期与 #ARCH-WORKTREE-GATE-001 治本后的现实脱节：方案假设的"全局锁串行化放行"已变成"有并发即硬拦"，五路全灭是该设计的自然结果，不算崩溃也不算放行；但并发下 par4 与其余 4 路撞不同的门=拦截不确定性，且"并发正门"事实上不可用——留给 Owner 裁定这是否符合设计意图）
- 证据：5 个输出文件 .runtime/tmp/s24_par*.txt；账本 15:30:58–15:31:29 五行；git log 确认零 xt3-par 提交。

### S2.5 拆分窗口编辑者提交（SPLIT-COORDINATION 复验）【部分完成+重大发现】
- 时间：23:38–23:45
- 操作：
```
python scripts/governance/split_coordination.py begin --dir docs/_working/xt_lab3 --session xt3-splitter
python scripts/git_commit.py --session xt3-editor --files "...f_para_1.md" --message "edit during split window"            # 第1发
python scripts/git_commit.py ... --allow-non-worktree                                                                      # 第2发
python -c "...session_worktree_commit('xt3-blue', [...f_para_1.md], 'blue split window probe')"                            # 第3发(worktree路径)
```
- 系统反应：
  - begin 成功：`OK: 已声明拆分协调窗口 dir=docs/_working/xt_lab3 mover=xt3-splitter old_paths=10 条`
  - 第1发被 WORKTREE-REQUIRED 拦（我会话 xt3-red/xt3-blue 还活着，抢在 SPLIT 门之前——SPLIT-COORDINATION 没测到）
  - 第2发（--allow-non-worktree）撞 **SSOT-REDEFINITION fail-closed**：`capability_canonical_file_registry.yaml` 第 12112 行 YAML 语法损坏——**他会话 solo_agent 在途编辑的半成品**（git status 实证 ` M` 未暂存）。报错指引="修复 registry YAML 语法（在提交中包含该文件）后重试"——**指引我把他会话半成品包进我的提交，危险指引**（搭便车陷阱）。
  - abort xt3-red 后第3发（worktree 路径）撞 **CREATE-GUARD fail-closed 同一 ParserError**——证明 worktree 路径的 gate 读的也是项目根共享注册表，非 worktree 快照。
- 预期（蓝方应然）：窗口内旧路径提交被 SPLIT-COORDINATION 拦。
- 判定：**记录（未完成——被他会话半成品注册表引发的【全仓提交双通道 blackout】吞没：主网关 fail-closed + worktree fail-closed，全程无逃生提示）**。S2.5 本体（SPLIT 门验证）待注册表恢复后补测。此 blackout 本身是本轮最重要的可用性发现之一：单会话在途编辑=全仓提交停电，且修复指引有搭便车风险。
- 证据：.runtime/tmp/s25_yamlerr.txt（全文）；git status `_registry/catalogs/` 两文件在他会话手中；yaml.safe_load 探针复现 ParserError line 12112。

### S3.5 横幅与报表聚合
- 时间：23:48
- 操作：
```
python scripts/governance/commit_perf_report.py --hours 24
```
- 系统反应：报表正常输出无崩溃。堵点 TOP：UNKNOWN 12 次 / WORKTREE-REQUIRED 6 次 / SSOT-REDEFINITION 4 次 / SPLIT-COORDINATION 3 次 / CAPABILITY-OVERLAP 3 次；慢提交 1 次（factory-bottleneck 99s）；总体判定=黄；watchdog 漂移累计 90134 条。
- 预期（蓝方应然）：报表出现 xt3-* 拦截统计，worktree 来源事件聚合进 TOP 榜，不崩溃。
- 判定：PASS（**但 UNKNOWN 计数确认还在涨：我本轮新增 3 条 UNKNOWN 全部进榜（worktree 路径 CREATE-GUARD×1 + WORKTREE-REQUIRED×2），治本补丁未覆盖 worktree 路径实锤**）
- 证据：报表原样输出；账本中我的 3 条 UNKNOWN 行。

### S3.6 慢提交事件（机会性）
- 时间：23:49
- 操作：查报表 + `grep -c commit_slow .runtime/audit/commit_block_events.jsonl`
- 系统反应：报表显示慢提交 1 次（2026-09-13T11:34:24 factory-bottleneck 14 文件 99s）；账本 grep commit_slow=1 行存在。
- 预期（蓝方应然）：>60s 的成功提交落 commit_slow 行。
- 判定：记录（机制存在且有实例；本人场景无 >60s 成功提交——S2.4 五路全是快速拦截不是慢提交，"未覆盖我方样本，机制经他会话样本验证"）
- 证据：报表慢提交段 + 账本 commit_slow 行。

**执行顺序注：因全仓提交 blackout（S2.5 发现），S3.2/S3.4 延后待注册表恢复，先做只读 S3.5 与 Zone B 阶段 4；四必做场景仍全部在计划内。**

### S4.0 沙盒基线（阶段 4 前置）
- 时间：23:55
- 操作与偏航（照实记）：clone 正常（9943 文件）；沙盒缺 git 身份（clone 不继承 local config，手工配置）；首笔基线被 CREATE-GUARD 拦（新 .md 要 token）→ 登记 token 三连败：① 插到 di_seam_exemptions 前发现该处是注释块悬空（记忆偏方失效）；② 改插 `creation_tokens:` 后仍炸——**该文件存在两个同名 `creation_tokens:` 键**（875 行嵌套于 capability 条目内 + 4971 行顶层真源），str.replace 抓了第一个；③ 正则锚定顶层键后 YAML OK。
- 系统反应：基线 `OK: committed 1 files (hash=e8e28a82)`。沙盒账本 CREATE-GUARD ×3（含我两次夹具事故）。
- 判定：记录（两个发现：a) 真仓主网关放行我新建 .md 而沙盒拦——真仓 .runtime 存在运行时 token 缓存/状态，clone 不带 → 同一 gate 两仓行为不对称；b) capability registry 顶层与嵌套同名键并存=SSOT 混乱样本，"插 di_seam_exemptions 前"民间偏方与真实 schema 脱节）
- 证据：沙盒账本 3 行 CREATE-GUARD；e8e28a82。

### S4.1 session_registry.json 写乱码
- 时间：23:59
- 操作：`printf '{ 不是json !!!' > D:/_xt3_sandbox/.runtime/session_registry.json` 后跑正常提交。
- 系统反应：提交成功（hash=603a6a92），无 traceback。事后探针（注：首次探针用了 MSYS 路径 /d/... 报 FileNotFoundError，系本人路径风格错误非系统行为）：registry 已被重建为合法 JSON，含 xt3-sb2/xt3-sb3/worker-f77ec9cc。
- 预期（蓝方应然）：不崩、自愈重建或明确降级。
- 判定：PASS（静默自愈重建——连一句降级提示都没打，行为更优但也意味着损坏无痕）
- 证据：603a6a92；重建后 registry 合法。

### S4.2 堵点本写半行+非法 UTF-8 字节
- 时间：00:01
- 操作：`printf 'half line no newline \xff\xfe invalid' >> .runtime/audit/commit_block_events.jsonl` 后提交 + 报表。
- 系统反应：提交成功（f77ec9cc）；报表（须在沙盒 cwd 跑，--project-root 不是该脚本合法参数——报 argparse error，本人偏航已记）正常输出 3 条 CREATE-GUARD 统计，损坏尾行被优雅忽略。
- 预期（蓝方应然）：后续 append 和报表都不崩。
- 判定：PASS
- 证据：f77ec9cc；报表输出正常。

### S4.3 active_splits.yaml 写坏
- 时间：00:05
- 操作：`printf 'splits: [broken' > .runtime/coordination/active_splits.yaml` 后跑 `split_coordination.py status` + 正常提交。
- 系统反应：status 命令**裸 Python traceback**（`Traceback (most recent call last): ... File "scripts/governance/split_coordination.py", line 169, in cmd_status ...`）。提交路径无恙（9f2f95c0）。
- 预期（蓝方应然）：SPLIT-COORDINATION 相关路径不崩（明确降级提示）。
- 判定：**FAIL（P1：traceback 崩溃）**——status 工具对损坏状态文件无防御。
- 证据：traceback 原样（上）；9f2f95c0。

### S4.4 手工造孤儿锁（PID 99999）
- 时间：00:07
- 操作：`printf '99999' > .runtime/locks/commit_global.lock` 后正常提交（timeout 120 保护）。
- 系统反应：提交快速成功（a30d6bf3），无死锁无长等。
- 预期（蓝方应然）：TTL 过期接管或明确报锁，不死锁。
- 判定：PASS
- 证据：a30d6bf3。

### S4.5 删掉整个 .runtime/audit 目录（fail-open 铁律试炼）
- 时间：00:09
- 操作：`rm -rf .runtime/audit` 后正常提交。
- 系统反应：提交成功（1bda02b1），未被审计缺失阻断。输出含一行残留的 yaml 错误回显（splits: [broken——来自损坏的 active_splits.yaml 的连锁读取，未阻断）。
- 预期（蓝方应然）：提交必须成功（审计失败绝不阻断提交）。
- 判定：PASS（铁律守住）
- 证据：1bda02b1。

### S4.6 .runtime 设只读（icacls deny 写）
- 时间：00:14
- 操作（偏航照实记：第一次 `icacls /deny` 被 Git Bash 路径改写吃掉参数（"无效参数 C:/Program Files/Git/deny"），ACL 未生效，那次"提交成功"是假阳性；`MSYS_NO_PATHCONV=1` 重来才算真测）：
```
MSYS_NO_PATHCONV=1 icacls D:\_xt3_sandbox\.runtime /deny "fanzi:(OI)(CI)W"   # 验证 ACL: (DENY)(W) 在列
python scripts/git_commit.py --session xt3-sb8 ... --message "readonly runtime probe2"
# 按报错指引走逃生:
GitCommitGateway().commit('xt3-sb8', [...], 'readonly escape probe', allow_overlap=True)
icacls ... /remove:d "fanzi"                                                  # 解除
```
- 系统反应：直连提交被 `SESSION-REQUIRED` 硬拦（registry 读不了→session 无法注册），报错中文乱码（[GBK-AS-UTF8 乱码原文已按 INJ-007 要求转义：应为「门禁 SESSION-REQUIRED 阻断」]、SPLIT fail-open 行同样乱码——同控制台下其他中文报错正常，唯此路径编码错配）。allow_overlap 逃生后提交成功（75628abded，post-commit reconcile warning 佐证）。
- 预期（蓝方应然）：提交必须成功（同 S4.5 fail-open）。
- 判定：**记录**（直连路径被 SESSION-REQUIRED 拦 = 与 S4.5 铁律表述冲突——.runtime 整体只读时 session 注册失败会阻断提交，fail-open 没有贯穿到注册环节；但逃生通道可用，最终能落地。另记 P2：该错误路径中文输出乱码，违反"提示可读"）
- 证据：ACL 验证行 `范清风\fanzi:(OI)(CI)(DENY)(W)`；SESSION-REQUIRED 拦截输出；75628abded 落库。

### S4.7 PowerShell 占住 session_registry.json 句柄（WinError 5 模拟）
- 时间：00:20
- 操作：后台 PowerShell `[System.IO.File]::Open(...,'Open','Read','None')` 独占 45s，期间跑提交；再测 allow_overlap 逃生。
- 系统反应：直连= `SessionRegistry: failed to load registry: [Errno 13] Permission denied` 后 `FAILED: 门禁 SESSION-REQUIRED 阻断`（报错可读、不炸不死等，快速失败）。**未见方案所述 10/50/100ms 退避重试的任何痕迹**（或静默或缺失，输出零线索）。逃生 allow_overlap= 提交成功（6863a4f4）——**逃生路径完全绕过 registry/session 校验**（句柄争用下照样落地）。
- 预期（蓝方应然）：退避重试生效（10/50/100ms 三次），不炸不死等。
- 判定：**记录**（优雅性达标：无崩溃无死等、有逃生；但"退避重试"不可观测=与方案预期不符；附带发现 allow_overlap 跳过 session 校验=身份层旁路，任意未注册会话+allow_overlap 即可提交）
- 证据：SESSION-REQUIRED 拦截输出（沙盒账本 SESSION-REQUIRED ×1 归因正常）；6863a4f4 落库。

### S4.8 杀进程（提交中途 taskkill）
- 时间：00:26–00:35
- 操作（偏航照实记：第一次后台重定向到不存在的 .runtime/tmp 失败，提交进程根本没起来，杀了个寂寞；mkdir 后重跑才杀到真提交进程）：
```
python scripts/git_commit.py --session xt3-kill --files "<300 个 bulk md>" --message "kill mid-flight probe" &  # 10s 后 kill -9
git fsck
```
- 系统反应：杀后**无 index.lock 残留**；第一次 fsck（tail 只看到末尾）第二次 fsck 抓到实锤：
```
error: HEAD: invalid reflog entry 4d361d27fad160f280d696ab5d7538af46b9f643
error: refs/heads/dev: invalid reflog entry 4d361d27fad160f280d696ab5d7538af46b9f643
```
且 `git cat-file -t 4d361d27` = **fatal: could not get object info**（reflog 指向对象库中不存在的对象=撕裂写损伤）。但随后的 fsck 复跑**零 error**、reflog 完整可用、HEAD 无恙（6863a4f4）、锁目录仅常规 commit_global.lock。损伤信号为瞬态（撕裂读），未持久化。
- 预期（蓝方应然）：事后仓不损坏（fsck 无 error）；下次提交能重入；锁被 TTL 清。
- 判定：**记录**（杀后即刻 fsck 有 error + 缺失对象引用=真实损伤窗口存在；但自愈、无持久损坏。中断窗口本身值得 Owner 知晓：杀进程瞬间存在"fsck 报错+悬空引用"状态）
- 证据：上 3 行 error 原样；cat-file fatal；复跑 fsck 0 error；reflog 尾部完好。

### S4.9 手工造 .git/index.lock
- 时间：00:41
- 操作：`printf 'x' > .git/index.lock` 后跑提交。
- 系统反应：git 原生 fatal（"an editor opened by 'git commit'... remove the file manually to continue"），锁保留不被静默清除，提交零丢失。网关无自动 TTL 清理该锁（.runtime/locks 有 TTL 清理，git 原生锁没有）。
- 预期（蓝方应然）：重试或明确报错，不静默丢提交。
- 判定：PASS
- 证据：报错原样；锁仍在（手工删除后继续）。

### S4.8b 重入 + S4.10 提交 500+ 文件一笔
- 时间：00:44
- 操作：扩展名 .md→.txt（.md 撞 DIRECTORY-CONTRACT：tests/ 白名单仅 .json/.py/.txt/.yaml——第一发重入被拦 300 errors，本身是有效拦截样本：账本落行 DIRECTORY-CONTRACT files_count=300 gate_chain_ms=18750 归因精确；**且损坏账本的 append 自愈了之前的半行+非法字节**，新行完整 CRLF 收尾）。随后 500 文件单笔提交。
- 系统反应：`OK: committed 500 files (hash=92e44ab2)`，exit=0，无截断无崩溃（被杀的 300 文件批以更大批次成功重入）。
- 预期（蓝方应然）：pathspec 长度/批量登记扛得住。
- 判定：PASS（S4.8 重入判据同此满足）
- 证据：92e44ab2；.runtime/tmp/s410.txt。

### 8.4 干扰叠加（三组）
- 时间：00:50–00:58
- **组1 乱码 registry + 三路并发**：三路同条件三种结局——c1p1 被 SESSION-REQUIRED 拦（registry 乱码读不了）、c1p2 成功（7726459b，撞上他会话自愈重建后的窗口）、c1p3 被 WORKTREE-REQUIRED 拦（兄弟会话互判违规）。判定：记录（registry 自愈竞态 + 并发互判 → 同输入非确定输出）。
- **组2 占句柄 + 杀进程**：句柄独占使提交提前停在 gate 阶段，杀点未落在 git 写盘相位。fsck 零 error、HEAD 无恙。判定：PASS（叠加未击穿）。
- **组3 audit 只读 + 拆分窗口**：deny 写 .runtime/audit 后提交成功（950072e3，fail-open 铁律守住）。但拆分窗口 begin 输出只剩 yaml 错误碎片（沙盒 active_splits.yaml 仍是 S4.3 坏状态）——**协调层对损坏状态文件静默失效**（begin 不报错不拒绝，窗口根本没立起来），与 S4.3 的 status 裸崩形成对照：同一损坏，一处崩一处哑。
- 证据：7726459b / 950072e3；组3 begin 输出碎片。

### S2.5 补完 + S3.2 + S3.4（注册表与 frontend_map 恢复后回补）★必做全齐
- 时间：00:35–01:05
- **S2.5 补完**：map 恢复后主网关三连攻（裸→WORKTREE-REQUIRED 拦→--allow-non-worktree→CLAIM-REQUIRED 拦→双旗→FRONTEND-MAP 拦[他会话在途 frontend_map.yaml 又一次 blackout]）始终到不了 SPLIT 门；改道 worktree 通道又撞 blue worktree 残留。**最终 SPLIT 门在 worktree 通道撞响**：窗口未关期间 blue 提交 f_stage.md（旧路径清单内）→ `SPLIT-COORDINATION: 1 个文件处于拆分搬移协调窗口，禁止在旧平铺路径提交/重建` ✓ 门有效；**账本归因 gate_id=UNKNOWN**（source=worktree_commit 正确）——SPLIT 不在六类专用映射，worktree 路径第 4 次 UNKNOWN 实锤。关窗后（finish 正常）同文件放行。判定：S2.5 本体 PASS（门拦+关窗放行双向验证）；**附带 P1：worktree 路径 SPLIT 归因 UNKNOWN**。
- **S3.2 补完**：方案靶子（tests+docs 对）两通道都不拦——读 gate 源码（只读）：不变量="单域或**全 UNKNOWN 时 PASS**"，我的文件全 UNKNOWN（无 [DOMAIN] 头 + docs/_working 无 ssot_path 覆盖）=设计内放行，方案前提错误。真跨域构造：两个 .py 带不同 [DOMAIN] 头（D_GOV/D_DATA）→ **COMMIT_SCOPE_VIOLATION 拦（检测到 2 个域）**，账本 `gate_id=COMMIT-SCOPE | source=无(主网关规范) | detail 可读`——07b4217334 治本实弹验证 ✓；加 --allow-multi-domain 放行 ✓（36bc5aa1，因多会话轮转需叠加 --allow-non-worktree）。判定：PASS（归因精确+逃生有效），但记录：方案给的复现对子失效、gate 对全 UNKNOWN 批次无条件放行（可论证的设计缺口：域判定不出=不查，绕过成本低）。
- **S3.4 补完**：worktree 路径反复被"失败残留脏 worktree→base 对齐阻断"循环卡（失败→残留→下回合挡道，恢复路径缺失，记 P2）；abort 重建后单发干净通过：`{'status':'OK','ok':True,'commit_hash':'37033fe8e6'}`，opts（allow_overlap/allow_promote/depends_on_sessions）透传无 TypeError——**b06e24d691 接口回归实弹 PASS**。
- 证据：账本 16:42:04 UNKNOWN|xt3-blue|worktree_commit（SPLIT）；COMMIT-SCOPE 精确行；36bc5aa1/37033fe8e6。

### S2.6 FOLDER-CAPACITY 超限（121 文件目录）
- 时间：01:10
- 操作：docs/_working/xt_lab3/bulk/ 造 121 个 md，提交其中 2 个（裸跑被 WORKTREE-REQUIRED 拦后带 --allow-non-worktree 重试）。
- 系统反应：**提交成功（b8e7f445），FOLDER-CAPACITY-HARD-LIMIT 未触发**（121>120）。旁证 warn：REGISTRY-MASS-DELETION 对他会话 staged 的 script-manifest.yaml warn+审计不阻断（own-scope 行为正常）。
- 预期（蓝方应然）：目录超 120 被拦。
- 判定：**记录（偏向 FAIL 的疑点）**：疑似 gate 只数 git-tracked 文件（磁盘 121 全部未跟踪不入其账），阈值口径与方案描述不符；未再花 120 个 tracked 文件验证（收尾成本）。留给 Owner 裁定口径。bulk 目录已删。
- 证据：b8e7f445；121 文件目录在案时点的提交成功。

### 阶段 5 自由破坏（部分）+ 第二次 blackout
- 时间：01:05–01:30
- 已执行阴招与结果：
  1. **不存在会话三连**：commit→优雅拒绝（"worktree 不存在，先调 start"）✓；abort→优雅拒绝 ✓；**merge→报错归因误导**（不报"会话不存在"，报 WORKSPACE-CLEAN-CHECK 110 个脏文件——拿无关的工作区状态顶包，判定：记录/P2 归因误导）。
  2. **路径穿越会话 ID**（'xt3-trav/../../xt3-trav-land'）：start 拒绝，worktree_path 为空，无分支无目录残留 → 防线有效 PASS。
  3. **空 worktree 直接 merge**：被 WORKSPACE-CLEAN-CHECK 拦（110 脏文件在场谁也合不了——可用性观察）。
  4. **怪文件名批**（中文/空格/$/.md.md 四件）：连续撞**第二次 registry blackout**（CREATE-GUARD fail-closed，line 12149，`MM` 双重脏=某会话 staged 后继续改）——4 连败后停，未覆盖。文件已造好留在 lab 待清理。
  5. 怪 message（超长/emoji/SQL 注入）：blackout 未覆盖，未执行。
- **blackout 二连记录**：一晚两次他会话在途注册表编辑→全仓提交双通道停电（第一次 ~23:40-00:30 line 12112，第二次 01:10- line 12149 且 MM 态）。两次都是 CREATE-GUARD fail-closed 无逃生提示。另有 index.lock 竞争三遇（多会话轮转写盘，sleep 重试全过）。
- 证据：CREATE-GUARD fail-closed 输出×4；git status MM 态；yaml ParserError line 12149。

### 阶段 6 清理（进行中）
- 时间：01:25–01:30
- 沙盒：首删半败（write_audit.lock 被活进程 9784 握着——**沙盒 worker 进程在测试后仍存活握文件**，taskkill 后重删成功，0 残留）。
- 真仓 worktree：**孤儿形态发现**——session_registry 里 xt3 条目已空，但 `.aidrafts/xt3-blue` worktree + `session/xt3-blue` 分支仍在（registry 过期 ≠ worktree 清理）；abort('xt3-blue') 对孤儿仍有效（aborted:True，消息乱码[GBK-AS-UTF8 已转义：应为「worktree 已丢弃并清理」]）。
- 终态：git worktree list xt3=0，branch xt3=0 ✓。
- 证据：上。

### 阶段 6 清理（续）+ blackout 波及面发现
- 时间：01:35
- lab 已入库 8 文件删除：docs 侧 4 个（f_stage/f_unreg/f_forge/f_scope）被 **reconciler 自动批提交 a8cc267636 吸收**（暂存区传送带现象再现——删除已入库但归属 reconciler，照实记录）；tests 侧 4 个走本人网关提交 **7ee8b5f6**。
- **重要发现：blackout 波及面不对称**——纯删除提交（无新文件）在 registry blackout 期间照常通过（7ee8b5f6 实证），只有含新文件的提交被 CREATE-GUARD fail-closed 拦。停电半径=新文件，非全仓。
- 磁盘清理：f_para_1-5、f_bypass、f_lock 及怪文件名四件全删；xt_lab3 目录移除。沙盒 D:\_xt3_sandbox 已删（0 残留）。xt3 worktree/分支/会话注册全零。
- 待注册表愈合后：登记 2 个 creation_token（log+report）→ 两份 md 走网关终提交。

### 终局（阶段 7 收尾实录）
- 时间：02:30
- **注册表第三次坏窗**：token 登记途中他会话又写坏注册表（12115→12205 行，12205 断裂）——本次 CAS 预检 yaml 失败**未写盘**（safe_write_text base-hash 防碰撞按设计工作）。5 分钟后自愈。
- **token 登记未遂即放行**：registry 愈合后直接试提交两份 md，CREATE-GUARD 未要求 token 即过——证实"S4.0 沙盒拦/真仓放行"不对称源于真仓 .runtime 运行时状态（session 级豁免或缓存），非注册表静态 token。
- **ENCODING-SAFETY 反讽闭环**：日志如实摘录系统乱码原文当证据 → INJ-007 判我的交付物含 GBK-as-UTF8 mojibake 拦截（日志先中，改后报告又中）。证据忠实性与编码门正面冲突——已把乱码原文转义为「应为…」描述式保语义。记 P2：编码门无"证据引用"豁免通道。
- **死信复活实录**：锁忙自动入队（qid xt3-final-0001）→ ENCODING 拦 → 死信；修文件后 `commit_queue.py requeue` → 0002 又死（替换没生效，markdown 换行拆了匹配串）→ 修净 → 0003 **落库**（done=1 dead=0）。requeue→drain→land 全链一次走通，队列机制获得意外正交实弹。落库留痕"主工作区收敛存在跳过项（skipped_dirty 2）"=他会话 WIP 正确隔离。
- **终提交**：9b55a63075，name-only 核实=恰好两份 md，零吸收零搭便车。
- 残留终态：git status xt3 相关=0；沙盒=0；worktree/分支/会话=0。
