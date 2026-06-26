---
ttl: task_bound
doc_type: blueprint
completes_when: doc_type 迁移完成且文档归档
---

# 幽灵提交（Ghost Commit）治本——规则更新提案

> **文档ID**: ARCH-PROPOSAL-GHOST-COMMIT-001
> **创建时间**: 2026-06-25
> **任务卡**: OPS-2026062512 / OPS-2026062513 / OPS-2026062514
> **状态**: 提案（待裁定）
> **来源**: 幽灵提交根因调研 + GitCommitGateway 治本实施

---

## 1. 背景与根因

### 1.1 问题现象

多 AI session 共享同一 git 工作区时，一个 session 的未暂存修改会被另一个 session 的 `git commit` 一并提交（"幽灵提交"）。

### 1.2 根因分析

| 根因 | 说明 |
|------|------|
| git index 全局共享 | git 的暂存区（index）是工作区级全局状态，无法 per-session 隔离 |
| pre-commit stash 冲突 | pre-commit hook 的 stash 窗口期与并发 session 的文件操作冲突 |
| 无 commit 串行化 | 多 session 可同时执行 `git commit`，导致 index 状态竞争 |
| DM-202918 覆盖不全 | 仅修了 `TaskRepository.transition(COMPLETED)` 一条路径，未覆盖 AI 手动 commit |

### 1.3 治本方案

**GitCommitGateway** 作为全项目唯一合法 commit 入口，实现：
1. 全局跨进程串行锁（`os.open O_CREAT|O_EXCL`，`.ailocks/git_commit_global.lock`，TTL=1800s）
2. 选择性 stash（`git stash push -- <非本次 files>`，隔离其他 session 未暂存修改）
3. 受限 commit（`git commit --no-verify -F <msg_file> -- <本次 files>`）
4. stash pop 恢复（失败则保留 stash，不丢数据）
5. GW 标记（`ZEPHYR_COMMIT_GATEWAY=1` 环境变量 + `[GW:<session_id>]` commit message 标记）

---

## 2. 规则更新提案

### 2.1 新增硬约束（Hard Constraints）

以下约束已实施验证通过，建议正式写入 `project_memory.md` 的 Hard Constraints 节：

| 编号 | 约束 | 验证状态 |
|------|------|---------|
| HC-GIT-COMMIT-001 | 所有 git commit 操作必须通过 GitCommitGateway 执行，禁止裸 `git commit` | ✅ 15 单元测试 + 10 红蓝场景通过 |
| HC-GIT-COMMIT-002 | GitCommitGateway 必须设置 `ZEPHYR_COMMIT_GATEWAY=1` 环境变量 | ✅ 场景 10 验证 |
| HC-GIT-COMMIT-003 | commit message 必须追加 `[GW:<session_id>]` 标记 | ✅ 场景 7 验证 |
| HC-GIT-COMMIT-004 | 全局串行锁文件为 `.ailocks/git_commit_global.lock`，TTL=1800s | ✅ 场景 8 验证 |
| HC-GIT-COMMIT-005 | 选择性 stash 隔离非本次 files，commit 后必须 pop 恢复 | ✅ 场景 9 验证 |
| HC-GIT-COMMIT-006 | stash pop 失败时必须保留 stash 并返回 `StashConflictWarning`，禁止丢弃数据 | ✅ 单元测试验证 |
| HC-GIT-COMMIT-007 | pre-commit 门禁 `GATE-COMMIT-GW` 必须阻断未通过 Gateway 的裸 commit | ✅ exit 1 阻断验证 |

### 2.2 新增工程约定（Engineering Conventions）

| 编号 | 约定 | 说明 |
|------|------|------|
| EC-GIT-COMMIT-001 | git commit CLI 入口统一为 `python scripts/git_commit.py` | 封装 GitCommitGateway |
| EC-GIT-COMMIT-002 | 代码内 commit 统一调用 `GitCommitGateway().commit()` | 禁止 `subprocess.run(["git", "commit", ...])` |
| EC-GIT-COMMIT-003 | `TaskRepository._auto_commit_on_completion` 必须使用 GitCommitGateway | DM-202918 升级 |
| EC-GIT-COMMIT-004 | commit message 用 `-F <msg_file>` 传入（避免 PowerShell 特殊字符问题） | RULE-TWENTY 裁定2 |
| EC-GIT-COMMIT-005 | 红蓝对抗测试定期执行 `python scripts/governance/repair/concurrent_commit_test.py` | 10 场景全 PASS |

### 2.3 新增教训（Lessons Learned）

| 编号 | 教训 | 根因 |
|------|------|------|
| LL-GIT-COMMIT-001 | git index 全局共享是并发提交冲突的根本原因 | 需通过 GitCommitGateway 实现提交串行化和选择性 stash 隔离 |
| LL-GIT-COMMIT-002 | Python try/finally 中 return 会先捕获返回值再执行 finally | finally 内对同名变量重新赋值不改变已捕获的返回值，须在方法末尾统一 return |
| LL-GIT-COMMIT-003 | `_shared` 是 namespace package（无 `__init__.py`），需父目录在 sys.path 中 | import 前必须设置 sys.path |

---

## 3. [ASSUMPTION] 待验证假设

以下假设在当前实施中成立，但需在长期运行中持续验证：

> **[ASSUMPTION-1]** 全局串行锁 TTL=1800s（30 分钟）足够覆盖任何单次 commit 的最大耗时。
> - **验证方式**: 监控 `.ailocks/git_commit_global.lock` 的存活时间
> - **风险**: 若单次 commit 超过 30 分钟（如超大仓库），锁会被其他 session 强制抢占，可能导致 stash 状态不一致
> - **缓解**: commit 耗时超过 60s 时记录 WARNING 日志

> **[ASSUMPTION-2]** 选择性 stash 的 `git stash push -- <files>` 能正确隔离非本次文件。
> - **验证方式**: 红蓝场景 2/3/9 已验证
> - **风险**: git stash 对未跟踪文件（untracked）的处理与已跟踪文件不同
> - **缓解**: `_stash_other_files` 仅 stash 已跟踪的修改文件（`git status --porcelain` 过滤）

> **[ASSUMPTION-3]** `git commit --no-verify` 绕过 pre-commit hooks 不会引入未检测的问题。
> - **验证方式**: GitCommitGateway 在 commit 前已执行 `git add` + `git diff --cached` 检查
> - **风险**: 绕过的 hooks 中可能有代码格式化、lint 等质量门禁
> - **缓解**: GATE-COMMIT-GW 门禁本身通过 env var 检测放行 gateway commit，其他 pre-commit hooks 仍需在 gateway 外执行

> **[ASSUMPTION-4]** Windows 下 `os.open(O_CREAT|O_EXCL)` 的原子性与 Linux 一致。
> - **验证方式**: 红蓝场景 8（全局锁互斥）在 Windows 验证通过
> - **风险**: Windows 文件系统对 O_EXCL 的支持与 NTFS 版本相关
> - **缓解**: 锁文件含 PID + 时间戳，过期可被强制清理

> **[ASSUMPTION-5]** 10 个红蓝对抗场景覆盖了所有幽灵提交的触发路径。
> - **验证方式**: 场景覆盖并发不同文件、未暂存修改、交错 stage、并发同文件、3 session 并发
> - **风险**: 可能有未覆盖的边缘场景（如 4+ session 并发、网络延迟、磁盘满）
> - **缓解**: 定期执行红蓝对抗测试，发现新场景时补充

---

## 4. 实施验证结果

### 4.1 单元测试（15/15 PASS）

| 测试组 | 测试数 | 状态 |
|--------|--------|------|
| TestGlobalCommitLock | 3 | ✅ |
| TestGitCommitGatewayInit | 2 | ✅ |
| TestGitCommitGatewayCommit | 4 | ✅ |
| TestStashIsolation | 3 | ✅ |
| TestEdgeCases | 3 | ✅ |

### 4.2 并发测试（4/4 PASS）

| 测试 | 状态 |
|------|------|
| TestConcurrentCommitDifferentFiles | ✅ |
| TestUnstagedChangesNotPickedUp | ✅ |
| TestInterleavedCommit | ✅ |
| TestConcurrentSameFile | ✅ |

### 4.3 红蓝对抗（10/10 PASS）

| # | 场景 | 结果 | 耗时(ms) |
|---|------|------|----------|
| 1 | 并发提交不同文件——无跨 session 捡拾 | PASS | 953 |
| 2 | 未暂存修改不被并发 commit 捡拾 | PASS | 750 |
| 3 | 交错 stage + commit | PASS | 984 |
| 4 | 并发同一文件——串行化不丢数据 | PASS | 516 |
| 5 | 3 session 并发提交 | PASS | 1406 |
| 6 | 空文件列表——NOTHING_TO_COMMIT | PASS | 172 |
| 7 | GW 标记——[GW:session_id] | PASS | 453 |
| 8 | 全局锁互斥 | PASS | 891 |
| 9 | stash 恢复 | PASS | 750 |
| 10 | 环境变量清理 | PASS | 406 |

### 4.4 门禁验证

| 门禁 | 场景 | 结果 |
|------|------|------|
| GATE-COMMIT-GW | 裸 commit（无 env var） | ✅ exit 1 阻断 |
| GATE-COMMIT-GW | gateway commit（env var=1） | ✅ exit 0 放行 |

---

## 5. 文件清单

### 5.1 新增文件

| 文件 | 用途 |
|------|------|
| `src/zephyr/governance/git_commit_gateway.py` | GitCommitGateway 核心实现 |
| `scripts/git_commit.py` | CLI 封装入口 |
| `scripts/governance/d11_compliance/validate_commit_gateway.py` | GATE-COMMIT-GW 门禁 |
| `scripts/governance/repair/concurrent_commit_test.py` | 红蓝对抗 10 场景脚本 |
| `tests/test_git_commit_gateway.py` | 15 单元测试 |
| `tests/test_git_commit_concurrent.py` | 4 并发测试 |
| `data/red_blue/reports/rb_ghost_commit_test_report.md` | 红蓝对抗报告 |

### 5.2 修改文件

| 文件 | 修改内容 |
|------|---------|
| `src/zephyr/governance/task_repo.py` | `_auto_commit_on_completion` 改用 GitCommitGateway |
| `src/zephyr/governance/__init__.py` | 导出 GitCommitGateway |
| `.pre-commit-config.yaml` | 新增 GATE-COMMIT-GW hook |

---

## 6. 裁定建议

### 6.1 建议立即采纳

- HC-GIT-COMMIT-001 ~ 007：已实施验证通过，建议写入 Hard Constraints
- EC-GIT-COMMIT-001 ~ 005：工程约定已落地，建议写入 Engineering Conventions

### 6.2 建议后续观察

- [ASSUMPTION-1] 锁 TTL=1800s：监控实际 commit 耗时，必要时调整
- [ASSUMPTION-5] 红蓝场景覆盖度：定期执行，发现新场景时补充

### 6.3 不采纳项

无。所有提案均已实施验证通过。

---

## 7. 社区对标

| 方案 | 来源 | 对比 |
|------|------|------|
| STORM（写时一致性） | arXiv 2605.20563 | 比 git-worktree 基线 +18.7%；本项目采用串行化网关替代 worktree |
| AugmentCode | worktree 隔离 + spec 分解 | 本项目不采用 worktree（SSoT 约束 + 已投资 StagingArea 体系） |
| git-worktree | Git 原生 | 每 session 独立工作区；本项目 SSoT 约束不允许多工作区分裂 |

**本项目选择串行化网关而非 worktree 的理由**：
1. SSoT（Single Source of Truth）约束——全景图必须单一真源
2. 已投资 StagingArea 体系——复用 `_CrossProcessLock` 模式
3. 100% AI 开发——串行化比 worktree 更简单，少一层抽象=少一个幻觉源

---

> **提案人**: AI 架构师
> **裁定状态**: 待用户裁定
> **下一步**: 用户确认后，将 HC-GIT-COMMIT-001~007 写入 `project_memory.md` Hard Constraints 节
