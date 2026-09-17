---
ttl: task_bound
completes_when: W1 代码已落地(2ac7d910ed)、5 双向钉经变异证红、commit_gates 两轮 0 自有问题
title: W1 — worktree→主仓锚定判定收敛唯一真源（#ARCH-324 落地面假红/失明治本）
owner: ZephyrAlpha-Owner
session: st-anchorfix-20260918
date: 2026-09-18
---

# W1 — 落地面锚定态假红/失明治本

## 1. 根因（#ARCH-324）

队列真落地在 `.runtime/commit_queue/worktree`（父名 `commit_queue`，**非** `.worktrees`）。
旧判定普遍用"父目录名 == `.worktrees`"猜主仓 → 落地 worktree 猜不中 → 读自带
`.runtime` 停更/空副本 → 三种病：
- **假红**：`session_concurrency` 读空 session_registry → SESSION-REQUIRED 误判未注册；
- **假红**：`capability_lookup_required_gate` 读空 `lookup_audit` 目录 → fail-closed 永久阻断；
- **保护失明/假绿**：`split_coordination_gate` 读空/停更 `active_splits.yaml` → 拆分协调窗口静默失效。

## 2. 治本（单源 helper + 消费方去重）

- `shared/io/paths.py`：提级 `main_worktree_root(root)` 为唯一真源——解析 `.git` gitdir
  指针 → 祖先上溯找 `.git` 父目录 → 返回主仓根（覆盖 commit_queue/submodule 布局）；
  `_git_worktree_main_root` 委托之；`anchor_main_root` 复用。`__all__` 加符号。
- `session_concurrency.SessionRegistry.__init__`：`root.parent.name == ".worktrees"`
  名猜 → `anchor_main_root(root)`。实测落地 worktree 现 `_project_root == D:\ZephyrAlpha`。
- `capability_lookup_required_gate`：新增 `_audit_dir() = anchor_main_root(MAIN_REPO_ROOT)/LOOKUP_AUDIT_DIR_REL`，
  `_get_audit_log_path`/`_audit_log_dir_exists` 走它（测试 patch MAIN_REPO_ROOT=tmp → anchor 恒等，不受影响）。
- `split_coordination_gate`：`_load_active_splits` 读端 `anchor_main_root(gateway.project_root)/DECLARATION_REL`；
  `scripts/governance/split_coordination.py` 写端 `_REPO = anchor_main_root(parents[2])`（读写同锚）。
- `depgraph_freshness_gate._main_worktree_root`：委托 `paths.main_worktree_root`，消第二真源。

## 3. 双向钉（经变异证红，落 `tests/`）

| 文件 | 绿测 | 变异测（打回旧行为→必红） |
|------|------|--------------------------|
| test_session_concurrency.py | 落地 worktree 锚主仓读 8 会话 | patch anchor_main_root=旧 `.worktrees` 名猜 → `_project_root != main` 且 load()=={} |
| test_capability_lookup_required_gate.py | patch MAIN_REPO_ROOT=wt → 放行 | patch anchor_main_root=恒等 → 阻断"未调用" |
| test_split_coordination_gate.py | wt 读主仓 foo split | patch anchor_main_root=恒等 → `[], skip 无声明` |
| test_depgraph_freshness_gate.py | 主树副本权威（既有 27 测绿） | — |

## 4. 门禁审计纠正结论（13 个读 `.runtime` 的门）

**教训**：静态摘录会误判；须追进真实路径解析再动承重门。
- 首轮审计误标 `reconciler_health` + `create_guard` 为需修——实证追路径：reconciler
  经 `_governance_db_path → anchor_main_root`（reconciliation_registry.py:893）已正确；
  create_guard 读 tracked YAML（非 `.runtime`）；二者**已正确，不动**。
- 深二轮定位真同病 = `capability_lookup_required`（假红）+ `split_coordination`（失明）——均已修。

## 5. 验收

- `pytest tests/governance/commit_gates tests/session tests/io/test_io_paths.py -q`
  → 连续两轮：2816 passed / 1 failed（唯一红 = foreign `test_current_repo_is_clean`，
  观测面=git index，被 st-crisis-gate 在途 staged `crisis_gate.py` 引入 `ZA-PA-CRISIS` 触发，
  §3.4 不代修，非本次改动）；
- 落地：commit `2ac7d910ed`（恰 9 文件、作者 `t@t`、零热注册表吸收）。
