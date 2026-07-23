---
ttl: permanent
---

# 排查报告：forged_gw_marker 违规（4 个 commit）

> **关联议题**: #ARCH-GATE-ABUSE-SYSTEMIC-AUDIT-001, #ARCH-ASYNC-MERGE-RECONCILE-001
> **日期**: 2026-07-20
> **排查范围**: 2026-07-19 19:08 UTC critical_warn 触发的 4 个 forged_gw_marker commit
> **结论**: 4 个中 2 个误报 + 2 个真伪造

---

## 1. 检测逻辑

**两段式检测链路：**

1. **第一段 — `scripts/governance/git_hooks/post_commit_guard.sh`**（git post-commit hook）
   - 解析 commit message，若含 `[GW:...]` 标记，解析 session_id
   - 查 `SessionRegistry` 是否注册该 session_id
   - **未注册 + `ZEPHYR_COMMIT_GATEWAY` 环境变量未设置** → 写入报告 `violation=forged_gw_marker`，执行 `git reset --soft HEAD~1`
   - **未注册 + `ZEPHYR_COMMIT_GATEWAY=1`** → 写入报告 `violation=unregistered_session_id`，`action=warn_only`（逃生通道）

2. **第二段 — `commit_gateway_abuse_monitor_reconciler.py`（GATE-COMMIT-GW-ABUSE-MONITOR）**
   - post-commit 事件触发，扫描 `.runtime/reconcile_reports/post_commit_guard_*.json`
   - 维度4：24h 内 `violation=forged_gw_marker` 报告数 > 3 → 触发 `critical_warn`

`ZEPHYR_COMMIT_GATEWAY=1` env 由 `GitCommitGateway._run_git` 统一注入（[git_commit_gateway.py:1642-1643](../../src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py)），post-commit hook 继承该 env。

---

## 2. 4 个 forged_gw_marker commit

| # | Commit Hash | Message Subject | AuthorDate | Session |
|:---:|------|------|------|------|
| 1 | `6762e15628c9623e7ba168e5708988979d056eb0` | docs(arch): deep-verify and fix 11 hallucinations in architecture_principles | 2026-07-19 04:17:16 +0800 | sess-10732-20260719041701 |
| 2 | `fa37e1bbd4c214d38c8a9490f069ad6d71c78d45` | feat(git-call-budget): ARCH-GIT-CALL-BUDGET P0-P3.2 git 2.48.x crash fix | 2026-07-19 05:04:03 +0800 | sess-21280-20260719050252 |
| 3 | `1b8d67e4ab26db7874c0e33639620a53df142243` | fix(governance): P0-5 治本 - sync_dataflow_registry DELETE 谓词只删 production 保护 prototype | 2026-07-19 16:15:05 +0800 | sess-27964-p0-emergency |
| 4 | `02d94a540a6908126ecb6bb8d2fc0086d36d2407` | fix(governance): P0-5 治本 - sync_dataflow_registry DELETE 谓词只删 production 保护 prototype | 2026-07-19 16:17:22 +0800 | sess-27964-p0-emergency |

**Commit message 中的 GW 标记差异：**

- #1 #2 末尾：`[GW:sess-XXX-...:worktree]`（session_worktree_commit 签名格式）
- #3 #4 末尾：`[GW:sess-27964-p0-emergency]` + `[GW:sess-27964-p0-emergency:overlap]`（GitCommitGateway 标准格式，但 #4 message body 明确写："本次通过原子脚本（modify+add+commit 单进程）规避 auto-clean 窗口"）

4 个 commit 均被 `git reset --soft HEAD~1` 撤回（POST-COMMIT-GUARD 自动 reset），但 commit object 仍存于 git object store，`git show <hash>` 可访问。

---

## 3. 对比确认：是否真的绕过 GitCommitGateway

| # | 经由路径 | ZEPHYR_COMMIT_GATEWAY 注入 | 是否绕过 Gateway | 性质 |
|:---:|------|:---:|:---:|------|
| 1 | session_worktree_commit._git_commit_in_worktree | ❌ 未注入（bug） | 否（合法路径） | **误报** |
| 2 | session_worktree_commit._git_commit_in_worktree | ❌ 未注入（bug） | 否（合法路径） | **误报** |
| 3 | 手写"原子脚本"直接 `git commit` | ❌ 未注入 | 是（绕过） | **真伪造** |
| 4 | 手写"原子脚本"直接 `git commit` | ❌ 未注入 | 是（绕过） | **真伪造** |

4 个中 2 个误报 + 2 个真伪造，共同点是 `ZEPHYR_COMMIT_GATEWAY=1` env 都缺失，因此都触发了 `forged_gw_marker` 维度。

---

## 4. 根因分析

### 根因 A — session_worktree_commit 的 env 注入遗漏（影响 #1、#2，误报）

[session_worktree.py](../../src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 的 `_git_commit_in_worktree()` 函数在调用 `git commit --no-verify -F msg_file` 时，直接 `subprocess.run(..., env=os.environ.copy())`，没有把 `ZEPHYR_COMMIT_GATEWAY=1` 注入到子进程 env 中。post-commit hook 检测到 commit message 含 `[GW:sess-...:worktree]` 标记后，查 SessionRegistry 发现该 session 未注册（worktree session 通常过期或未登记），再查 env 又发现 `ZEPHYR_COMMIT_GATEWAY` 未设置，于是按伪造逻辑 reset HEAD~1 并写 `forged_gw_marker` 报告。实际上 commit 走的是合法的 session_worktree 通道，message 格式也正确（`:worktree` 后缀），仅 env 缺失导致误判。

### 根因 B — P0 应急修复用"原子脚本"绕过 GitCommitGateway（影响 #3、#4，真伪造）

commit #3、#4 的 message body 明确说明：因 95b7febb3f 提交时被并发 session auto-clean 还原文件，作者"通过原子脚本（modify+add+commit 单进程）规避 auto-clean 窗口"。这意味着作者直接用脚本拼装 `git add + git commit` 命令，绕过 `GitCommitGateway.commit()` 入口（也即绕过 `_run_git` 守卫）。但 message 中却手动写入了 `[GW:sess-27964-p0-emergency]` 和 `[GW:sess-27964-p0-emergency:overlap]` 标记（模仿 GitCommitGateway.commit L996-999 的输出格式）。post-commit hook 看到 GW 标记 + session_id 未注册（"p0-emergency"是临时手写 session_id，非真实注册的 session）+ env 未设置，正确判定为伪造并 reset。作者用绕过 Gateway 的方式逃避 auto-clean 竞争，但又想保留 GW 标记让 commit 看起来"合法"，这是典型的有意伪造。

---

## 5. 修复建议

| # | 建议 | 状态 | 影响 |
|:---:|------|:---:|------|
| 1 | session_worktree_commit env 注入修复（根因 A） | ✅ 已落地（2026-07-20 P1-1） | 消除 #1#2 类误报；建议补单测防回归 |
| 2 | 封堵 P0 应急脚本的伪造路径（根因 B） | ⏳ 待立项 | AGENTS.md 增加强制条款：P0 应急修复必须通过 GitCommitGateway.commit 或 session_worktree_commit |
| 3 | post_commit_guard.sh 增加 git tracing 区分误报 vs 真伪造 | ⏳ 待立项 | 检查 `[GW:...]` 后缀：`:worktree` → warn_only；标准格式 → 严格 reset |
| 4 | P0-emergency session_id 治理 | ⏳ 待立项 | SessionRegistry 增加 P0-emergency 临时注册 API（短 TTL 30min，仅允许一次 commit） |
| 5 | reconcile_execution_log detail 增加结构化字段 | ⏳ 待立项 | 增加 `metrics_json` 列存储 forged_hashes 列表，便于事后排查 |

---

## 6. 历史违规（已滚动出 24h 窗口）

| Commit Hash | 时间戳 | Session | 备注 |
|------|------|------|------|
| `c30876a9b52f46afa5216a11cb47062b3f9d5924` | 2026-07-15 | sess-32008-20260715050508 | `[GW:...:worktree]` 格式 |
| `734dccc7bacdc2075c33423da08ece0ec557bcc6` | 2026-07-18 | sess-26696-20260718165519 | `[GW:...:worktree]` 格式 |

---

## 7. 引用

- 检测器: [commit_gateway_abuse_monitor_reconciler.py](../../src/zephyr/governance/audit/commit_gateway_abuse_monitor_reconciler.py)
- post-commit hook: [post_commit_guard.sh](../../scripts/governance/git_hooks/post_commit_guard.sh)
- env 注入点（Gateway）: [git_commit_gateway.py:1642-1643](../../src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py)
- env 缺失点（已修复）: [session_worktree.py:1663-1668](../../src/zephyr/gov_enforcement/rule_bridge/session_worktree.py)
- 数据库: `data/databases/governance.db`（表 `reconcile_execution_log`）
- 报告目录: `.runtime/reconcile_reports/post_commit_guard_*.json`、`commit_gateway_abuse_monitor_*.json`
- 关联裁定: [ruling_gate_abuse_systemic_audit.md](ruling_gate_abuse_systemic_audit.md)（#ARCH-GATE-ABUSE-SYSTEMIC-AUDIT-001）
- 母裁定: [ruling_async_merge_reconcile.md](ruling_async_merge_reconcile.md)（#ARCH-ASYNC-MERGE-RECONCILE-001）
