---
ttl: permanent
doc_type: policy
rule_form: procedural
verifiability: manual
title: Worktree 清理 SOP——四证齐全方可删除（死亡证明/无未合并工作/统筹批准/可恢复证明）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-14
topic: worktree_cleanup_safety
scope: global
related_issues:
  - "#ARCH-AICOLLAB-001（Git Worktree + File Lock + Task Board 三件套）"
  - "#ARCH-GIT-CLEAN-GUARD-FIX（2026-08-11 git clean 灾难）"
  - "wipe 事故裁定书（2026-08-14 三 worktree 被物理清空）"
depends_on:
  - 65_git_safety_governance
  - 66_commit_queue_serialization
  - construction_workflow_sop
related_modules:
  - scripts/session_worktree.py
  - scripts/ops_guard.py
  - src/zephyr/security/access_control/session_concurrency.py
---

# Worktree 清理 SOP——四证齐全方可删除

> 本 SOP 是 **清理任何 session worktree 的唯一合法流程**，2026-08-14 wipe 事故（三 worktree tracked 文件被物理清空）治本方案 S2。
> 事故根因：worktree 清理无所有者、无 SOP、无"分支是否有未合并 commit"强制检查点——某会话临时构造"清理"命令直接物理删除三个活跃 worktree。
> 性质：**操作规范（SOP）**，任何 AI/人工清理 worktree 前必须遵循。
> 关联：[merge_conflict_resolution_sop](merge_conflict_resolution_sop.md)（merge 冲突处理）｜[construction_workflow_sop](construction_workflow_sop.md) Step 12（施工流程 merge 环节）｜[wipe 事故裁定书](../../_working/audit/architecture-reviews/2026-08-14_ai-liq-001_worktree_wipe_incident_review.md)

## 1. 适用范围

| 场景 | 命令 |
|---|---|
| session 完工清理 | `python scripts/session_worktree.py abort <sid>` |
| merge 后自动清理 | `session_worktree.py merge` 内部调用 abort |
| 手动删除 worktree 目录 | `Remove-Item -Recurse .worktrees\<sid>`（**禁止**，须走本 SOP） |
| git worktree 原语清理 | `git worktree remove`（**禁止直接调用**，须走本 SOP） |

**红线**：任何会话禁止对其他会话的 worktree 执行物理删除。清理自己的 worktree 也必须过四证（防误删未提交工作）。

## 2. 四证（缺一不可）

清理任何 worktree 前，必须按顺序取得以下四证。任一证不通过 → 禁止清理。

### 证 1 · 死亡证明（目标会话确已终结）

**标准**：目标 session 的 heartbeat 停跳 >90s 且 SessionRegistry 无活跃记录。

**判定逻辑**（复用 `session_concurrency._is_session_alive` 双判据）：
- `pid>0`（进程绑定 session）：PID 已死 且 距 last_heartbeat >90s
- `pid=0`（逻辑 session）：距 last_heartbeat >90s（daemon 每 30s 刷新，90s=3×interval 容忍 2 次丢失）

**例外**：目标 session 在 registry 中不存在（从未注册或已注销）→ 视为已死亡。

**自查命令**：
```powershell
# 查看 registry 中该 session 的活跃状态
python -c "from zephyr.security.access_control.session_concurrency import SessionRegistry; from pathlib import Path; reg=SessionRegistry(Path('.')); actives={s.session_id for s in reg.list_active()}; print('ACTIVE' if '<sid>' in actives else 'DEAD')"
```

### 证 2 · 无未合并工作证明（分支工作已全部落袋）

**标准**：目标 worktree 分支相对主线**无 ahead commit**，且 `git status` **无 staged 变更**。

**判定命令**：
```powershell
# ① 分支是否有未 merge 的 commit（输出为空=无 ahead）
git log dev..ai/<sid>/<task> --oneline

# ② worktree 内是否有未提交变更（输出为空=干净）
git -C .worktrees/<sid> status --porcelain
```

**有未合并工作时的处置**（不是阻断，是存证后放行）：
- 有 ahead commit → 分支本身即存证（commit 已入对象库，永不丢失）→ 证 2 通过
- 有 staged/unstaged 变更 → **先打包存证**：`git -C .worktrees/<sid> stash push -m "quarantine-<sid>-<date>"`，stash ref 登记到 `refs/quarantine/<sid>` 命名空间 → 证 2 通过
- 既无 ahead 又无变更 → 直接通过

### 证 3 · 统筹显式批准（清理动作已登记）

**标准**：清理动作已登记到施工进度跟踪表（`docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/construction_progress_tracker.md`）或统筹会话显式批准。

**登记内容**：目标 sid / 分支名 / ahead commit 数 / stash ref（如有）/ 清理原因 / 执行人。

**例外**：会话清理**自己的** worktree（merge 后自动 abort）→ 无需统筹批准，但证 1/2/4 仍需满足。

### 证 4 · 可恢复证明（删除前打快照）

**标准**：执行删除前，已对分支 ref 打快照（git bundle 或 ref 记录）。

**快照方式**（任选其一）：
```powershell
# 方式 A：git bundle（推荐，含完整 commit 历史）
git bundle create .runtime/quarantine/<sid>.bundle ai/<sid>/<task>

# 方式 B：ref 快照（轻量，记录分支 tip SHA）
git rev-parse ai/<sid>/<task> >> .runtime/quarantine/branch_refs.log
```

**意义**：即使误删，分支 commit 已在对象库/ bundle 中，可秒级恢复（2026-08-14 wipe 事故中分支 ref 完好零损失即实证）。

## 3. 标准流程（7 步）

```
1. 确认目标 sid → 取证 1（死亡证明：heartbeat 停跳 >90s 且 registry 无活跃）
2. 检查分支 ahead commit + git status → 取证 2（无未合并工作）
   → 有 staged 变更则 stash push 存证 refs/quarantine/
3. 登记 tracker 或获统筹批准 → 取证 3（统筹显式批准）
4. git bundle 或记录分支 tip SHA → 取证 4（可恢复证明）
5. 执行清理：python scripts/session_worktree.py abort <sid>
6. 验证：git worktree list 无该 sid；git branch 无 ai/<sid>/*（或保留分支仅删目录）
7. 回填 tracker：标记已清理 + 快照位置
```

## 4. 自动化接入点

`session_worktree.py` 的 `abort` 命令已内置四证检查（S2 治本落地）：

| 证 | 自动化程度 | 说明 |
|---|---|---|
| 证 1 死亡证明 | **自动** | abort 前查 SessionRegistry，目标仍活跃 → 阻断并提示 |
| 证 2 无未合并工作 | **自动** | abort 前查分支 ahead commit + git status，有 staged 变更 → 阻断并提示先 stash |
| 证 3 统筹批准 | **半自动** | 自己 abort 自己免批准；abort 他人需 `--coordinator-approved` 旗标 |
| 证 4 可恢复证明 | **自动** | abort 前自动记录分支 tip SHA 到 `.runtime/quarantine/branch_refs.log` |

**逃生通道**：`--force-skip-checks` 跳过全部检查（仅限证 1 误判/证 2 已人工确认等场景，落审计）。

## 5. 红线

1. **禁止**对其他会话的 worktree 执行 `Remove-Item -Recurse` / `shutil.rmtree` / `git worktree remove`——一律走本 SOP。
2. **禁止**跳过证 1 直接清理"看起来不活跃"的 worktree——heartbeat 90s 内可能正在 commit（wipe 事故中 AI-SELL-001 被删时正在跑 capability 反查）。
3. **禁止**删 `.worktrees/` 根目录整体——每个 worktree 独立过四证。
4. ops_guard（S1）已将对 `.worktrees/*` 的递归删除纳入硬阻断——本 SOP 是流程层补充，与 S1 能力层形成双层防护。

## 6. 验收标准

- [x] S2 四证流程走通一次真实清理（本 SOP 发布后首个 abort 即按此流程）
- [x] 证 1 误判率 0（活跃 session 不会被判死）
- [x] 证 2 漏检率 0（有未合并工作的 worktree 不会被直接删）
- [x] 快照可恢复演示（从 bundle/ref 恢复一个已删 worktree）
