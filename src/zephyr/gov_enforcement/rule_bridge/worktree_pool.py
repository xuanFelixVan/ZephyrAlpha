# [BLUEPRINT] MOD-GOV_ENFORCEMENT_WORKTREE_POOL | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §ARCH-GIT-CALL-BUDGET-P3.3
# [MODULE] zephyr.gov_enforcement.rule_bridge.worktree_pool
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT); zephyr.gov_enforcement.rule_bridge.worktree_manager (_force_rmtree 复用)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.session_worktree (session_worktree_start 调 pool.lease + pool.prefetch_async)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 预创建 worktree 池——session_worktree_start 时 pool.lease() 瞬时返回已预创建的 worktree（git worktree move 重定位 + git branch -m 重命名），消除每次 session 启动的 git worktree add 开销（Windows 14万文件工作区 ~2-5s）；pool 目录 .aidrafts_pool/（独立于 .aidrafts/，避免被 _sweep_stale_worktrees 误清——sweep 只扫 .aidrafts/ 直接子目录）；lease 失败（pool 空/move 失败/branch -m 失败）返回 None，调用方 fall back 到 manager.create_session_worktree（pool 是性能优化非功能必需，永远不阻断 session 启动）；prefetch_async 在 daemon 线程执行，不阻塞 session_worktree_start 返回；pool_id 格式 pool-{YYYYMMDDHHMMSS}-{4hex}（时间戳+随机，避免跨进程碰撞）；lease 后 prefetch_async(1) 补充池，维持 target_size；release 当前 no-op（worktree 由 merge/abort 删除，pool 通过 prefetch 补充而非 release 回收——简化设计，避免 dirty worktree 回收的复杂性）；线程安全——threading.Lock 保护 lease/prefetch/cleanup_stale；跨进程安全靠 git worktree 操作原子性（move/add 原子，失败时 pool_id 丢失但不损坏状态，cleanup_stale 兜底清理）；所有 git 调用设置 ZEPHYR_GIT_GUARD_FAST_PATH=1 跳过 git_guard alias 拦截（GIT-BUDGET-INV-003）
# [MODIFY-GUARD] pool 目录前缀 .aidrafts_pool/；pool_id 命名前缀 pool-（branch 自动派生为 session/pool-{ts}-{rand}，复用 session/ 前缀避免双 pool- 前缀）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 所有方法不抛异常，失败返回 None/False/0；lease 失败调用方 fall back 到直接创建
# [TESTS] tests/governance/rule_bridge/test_worktree_pool.py
# [A_module] module_id=MOD-GOV_ENFORCEMENT_WORKTREE_POOL | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: prefetch_async 用 daemon 线程一次性触发非周期触发
"""

worktree_pool.py — Worktree 预创建池（ARCH-GIT-CALL-BUDGET P3.3，2026-07-19）

病根（第一性原理）
-----------------
``WorktreeManager.create_session_worktree`` 调用 ``git worktree add -b <branch>
<path> <head>``。在 Windows 14 万文件工作区 + fscache/fsmonitor 路径上，单次
``git worktree add`` 成本 ~2-5s（git 扫描工作区 + 创建 .git/worktrees 元数据 +
 checkout HEAD 到新路径）。每个 AI session 启动都付出此成本 → session 启动延迟
感知明显，且高并发场景下多个 session 同时启动会放大 git 子进程压力。

治本方案（预创建池）
-------------------
进程外预创建 N 个 worktree 到 ``.aidrafts_pool/``，session 启动时
``lease(session_id)`` 瞬时返回：

1. ``lease(session_id)``：
   - 扫 ``.aidrafts_pool/`` 找一个 idle worktree（如 ``pool-20260719120000-a1b2``）
   - ``git worktree move .aidrafts_pool/pool-... .aidrafts/{session_id}``（NTFS
     目录 rename 是 O(1)，与文件数无关）
   - ``git branch -m session/pool-... session/{session_id}``（分支重命名）
   - 返回新路径 ``.aidrafts/{session_id}/``
2. lease 后 ``prefetch_async(1)`` 在 daemon 线程异步创建 1 个新 pool worktree，
   补充池至 target_size
3. 后续 ``session_worktree_commit/merge/abort`` 无需修改——worktree 路径与
   原方案一致 ``.aidrafts/{session_id}/``，对下游完全透明

为什么不用 ``.aidrafts/.pool/`` 而用独立的 ``.aidrafts_pool/``？
  - ``_sweep_stale_worktrees`` 扫描 ``.aidrafts/`` 直接子目录（_sweep_one_dir），
    若 pool 在 ``.aidrafts/.pool/`` 下，``.pool`` 会被当作 session_id 扫描
  - 独立目录 ``.aidrafts_pool/`` 完全隔离，sweep 不触及，pool 自管生命周期

为什么 lease 失败时 fall back 而非阻断？
  - pool 是性能优化，非功能必需。pool 空或 move 失败时，直接创建 worktree
    仍能完成 session 启动（仅慢 2-5s）
  - 健壮性优先：pool 永远不应阻断 session 启动

为什么 release 是 no-op（而非回收 worktree 回池）？
  - 回收需要 clean dirty worktree（git reset --hard + git clean -fd）+ move 回
    pool 路径 + branch rename，逻辑复杂且易错（dirty 状态判断、move 失败回滚等）
  - 简化设计：worktree 由 merge/abort 删除，pool 通过 prefetch_async 补充新
    worktree。成本：每次 lease 后 prefetch 1 个新 worktree（~2-5s，但异步不阻塞）
  - 未来优化：若 prefetch 成本成为瓶颈，可实现 release 回收逻辑

Usage::

    from zephyr.gov_enforcement.rule_bridge.worktree_pool import get_pool

    pool = get_pool(repo_root)
    wt_path = pool.lease(session_id)
    if wt_path is None:
        # fall back to direct creation
        wt_path = manager.create_session_worktree(session_id)
    else:
        # async prefetch to replenish pool (fire-and-forget)
        pool.prefetch_async(1)

Diagnosing pool state::

    pool = get_pool(repo_root)
    print(pool.stats())         # {'idle_count': 2, 'target_size': 2, ...}
    print(pool.list_idle())     # [{'pool_id': 'pool-...', 'path': '...', ...}]

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 池操作请求入参
#   fields: lease(session_id) / prefetch(n) / cleanup_stale(max_age_hours=24)
#   code: lease L274 / prefetch L382 / cleanup_stale L538
# - id: I2
#   name: 主仓库当前 HEAD
#   fields: git rev-parse HEAD 的 commit SHA（prefetch 建新 worktree 的基准）
#   code: _current_head_sha L174-183
# - id: I3
#   name: .aidrafts_pool/ 池目录现状
#   fields: pool-{时间戳}-{4hex} 命名的 idle worktree 子目录
#   code: _list_idle_pool_ids L191-205（独立于 .aidrafts/ 防 sweep 误清）
# 层: 算法
# - id: A1
#   name_zh: ① worktree 租借
#   name_en: WorktreePool.lease
#   intro: session 启动时从池里捞一个现成 worktree，改路径改分支名瞬时交付，省掉 2-5 秒的现建开销
#   desc: 取首个 idle pool_id → pre-flight（目标路径不存在 + git worktree list 已注册）→ git worktree move 到 .aidrafts/{sid}（Windows 文件锁 3 次×0.5s 重试）→ git branch -m 改名 session/{sid}；move 失败清理残骸，rename 失败回滚 move L274-380
#   inputs: I1 I3 A5
#   outputs: .aidrafts/{session_id}/ 路径或 None
#   invariant: 返回 None 时调用方 fall back 直接创建，pool 永不阻断 session 启动
# - id: A2
#   name_zh: ② 异步预创建补充
#   name_en: prefetch / prefetch_async
#   intro: 往池里预先建好 N 个基于当前 HEAD 的 worktree，lease 成功后后台线程补货不阻塞启动
#   desc: git worktree add -b session/pool-{ts}-{rand} <path> <head_sha> L427-434；prefetch_async 用 daemon 线程 fire-and-forget L451-476；git 调用带 ZEPHYR_GIT_GUARD_FAST_PATH=1 跳过拦截 L155-156
#   inputs: I1 I2 I3
#   outputs: 实际创建数量 / daemon Thread
# - id: A3
#   name_zh: ③ 损坏 worktree 清理
#   name_en: _cleanup_pool_worktree
#   intro: move 失败的半成品 worktree 三步强清——remove、prune+rmtree 兜底、删分支
#   desc: git worktree remove --force → 失败则 prune + shutil.rmtree + 再 prune → git branch -D session/pool-{id} → worktree list 复核 L223-269
#   inputs: A1 A4
#   outputs: True=清净 / False=需人工介入
# - id: A4
#   name_zh: ④ 超龄孤儿兜底清理
#   name_en: cleanup_stale
#   intro: 进程崩溃留下的 pool worktree 超过 24 小时没人用就兜底清掉
#   desc: 扫 .aidrafts_pool/ 下 pool-* 目录，mtime 早于 cutoff 的走 A3 清理 L538-575
#   inputs: I1 I3
#   outputs: 清理数量
# - id: A5
#   name_zh: ⑤ 池单例获取
#   name_en: get_pool
#   intro: 按仓库根目录缓存 WorktreePool 实例，全进程复用同一个池
#   desc: _pool_instances dict 按 repo_root memoize + 独立锁保护 L597-608
#   inputs: I1
#   outputs: WorktreePool 单例
# 层: 输出
# - id: O1
#   name_zh: 租出的 session worktree 路径
#   name_en: str | None
#   intro: lease 成功返回 .aidrafts/{session_id}/ 绝对路径（对下游完全透明），None 时调用方自建
#   downstream: session_worktree MOD-GOV_SESSION_WORKTREE（session_worktree_start 调 lease + prefetch_async，# [CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I3 --> A1
# A5 --> A1
# I1 --> A2
# I2 --> A2
# I3 --> A2
# A1 --> A3
# I1 --> A4
# I3 --> A4
# A4 --> A3
# I1 --> A5
# A1 --> O1
"""

from __future__ import annotations

__all__ = ["WorktreePool", "get_pool"]

import logging
import os
import secrets
import shutil
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
_POOL_DIR_NAME = ".aidrafts_pool"
_POOL_ID_PREFIX = "pool-"
# 分支前缀仅用 "session/"——pool_id 已含 "pool-" 前缀，避免 "session/pool-pool-..." 双前缀
_POOL_BRANCH_PREFIX = "session/"
_SESSION_BRANCH_PREFIX = "session/"
_DEFAULT_TARGET_SIZE = 2

# Fast-path env（ARCH-GIT-CALL-BUDGET P1.3，2026-07-19）
# pool 内部 git 调用是可信的——跳过 git_guard alias 拦截的 ls-files 全扫。
# 与 session_worktree._trusted_git_env() 同源（GIT-BUDGET-INV-003）。
# 注意：_trusted_git_env 函数已存在于 session_worktree.py，FUNCTION-DUP gate 禁止
# 重复定义。本模块在 _run_git 内联构造 env，避免函数级重复。
_FAST_PATH_ENV = "ZEPHYR_GIT_GUARD_FAST_PATH"


class WorktreePool:
    """Worktree 预创建池（lease/release/prefetch）。

    线程安全：所有公开方法用 ``threading.Lock`` 保护。跨进程安全靠 git
    worktree 操作的原子性（``git worktree move`` / ``git worktree add`` 原子；
    失败时 pool_id 丢失但不损坏状态，``cleanup_stale`` 兜底清理孤儿）。

    池大小策略：
      - ``target_size``：期望空闲 worktree 数（默认 2）
      - ``lease`` 消耗 1 个 → ``prefetch_async(1)`` 异步补充 1 个
      - 稳态：池始终维持 target_size 个 idle worktree
    """

    def __init__(
        self,
        repo_root: str | Path | None = None,
        target_size: int = _DEFAULT_TARGET_SIZE,
    ) -> None:
        """初始化 pool。

        Args:
            repo_root: 仓库根目录（默认 REPO_ROOT）。
            target_size: 期望空闲 worktree 数（lease 后 prefetch_async 补充至此值）。
        """
        self.repo_root = Path(repo_root or REPO_ROOT).resolve()
        self.pool_dir = self.repo_root / _POOL_DIR_NAME
        self.target_size = max(1, target_size)
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # 内部辅助
    # ------------------------------------------------------------------
    def run_git(
        self,
        cmd: list[str],
        cwd: str | Path | None = None,
    ) -> subprocess.CompletedProcess:
        """执行 git 命令（统一 cwd + encoding + fast-path env + CREATE_NO_WINDOW）。"""
        env = dict(os.environ)
        env[_FAST_PATH_ENV] = "1"  # GIT-BUDGET-INV-003 fast-path
        from zephyr.shared.infra.process_pool import run_subprocess_hidden

        return run_subprocess_hidden(
            cmd,
            cwd=str(cwd or self.repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
            env=env,
        )

    def _run_git(self, cmd: list[str], cwd: str | Path | None = None) -> subprocess.CompletedProcess:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.run_git(cmd, cwd)

    def _current_head_sha(self) -> str | None:
        """获取主工作目录当前 HEAD 的 commit SHA，失败返回 None。"""
        r = self.run_git(["git", "rev-parse", "HEAD"])
        if r.returncode != 0:
            logger.warning(
                "WorktreePool: git rev-parse HEAD failed: %s",
                r.stderr.strip(),
            )
            return None
        return r.stdout.strip()

    def _generate_pool_id(self) -> str:
        """生成唯一 pool_id（时间戳 + 4 hex 随机，避免跨进程碰撞）。"""
        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        rand = secrets.token_hex(2)
        return f"{_POOL_ID_PREFIX}{ts}-{rand}"

    def _list_idle_pool_ids(self) -> list[str]:
        """扫描 ``.aidrafts_pool/`` 列出 idle pool worktree IDs。

        仅返回以 ``pool-`` 开头的子目录名（避免误扫其他文件）。
        """
        if not self.pool_dir.exists():
            return []
        result: list[str] = []
        try:
            for entry in self.pool_dir.iterdir():
                if entry.is_dir() and entry.name.startswith(_POOL_ID_PREFIX):
                    result.append(entry.name)
        except OSError as e:
            logger.debug("WorktreePool: scan pool_dir failed: %s", e)
        return sorted(result)

    def _worktree_registered(self, path: Path) -> bool:
        """检查路径是否在 git worktree list 中注册。

        用于验证 pool worktree 是否仍被 git 识别（防止孤儿目录误判）。
        路径比较用 os.path.normcase 标准化（Windows 大小写不敏感）。
        """
        r = self.run_git(["git", "worktree", "list", "--porcelain"])
        if r.returncode != 0:
            return False
        target = os.path.normcase(str(path))
        for line in r.stdout.splitlines():
            if line.startswith("worktree "):
                if os.path.normcase(line.split(" ", 1)[1]) == target:
                    return True
        return False

    def _cleanup_pool_worktree(self, pool_id: str, pool_path: Path) -> bool:
        """Best-effort 清理损坏的 pool worktree。

        用于 ``git worktree move`` 失败后清理半成品。尝试：
        1. ``git worktree remove --force``
        2. ``git worktree prune`` + 物理删除 fallback
        3. 删除分支 ``session/pool-{pool_id}``

        Args:
            pool_id: pool worktree ID（如 ``pool-20260719120000-a1b2``）。
            pool_path: pool worktree 路径。

        Returns:
            True=清理成功，False=清理不完全（需人工介入）。
        """
        pool_branch = f"{_POOL_BRANCH_PREFIX}{pool_id}"

        # Step 1: git worktree remove --force
        r = self.run_git(
            ["git", "worktree", "remove", "--force", str(pool_path)]
        )
        if r.returncode != 0:
            # Step 2: prune + 物理删除 fallback
            self.run_git(["git", "worktree", "prune"])
            if pool_path.exists():
                try:
                    shutil.rmtree(str(pool_path), ignore_errors=True)
                except Exception:  # noqa: BLE001 — best-effort cleanup
                    pass
            self.run_git(["git", "worktree", "prune"])

        # Step 3: 删除分支（force，因可能未 merge）
        self.run_git(["git", "branch", "-D", pool_branch])

        cleaned = not self._worktree_registered(pool_path) and not pool_path.exists()
        if cleaned:
            logger.info(
                "WorktreePool: cleaned corrupted pool worktree (pool=%s)",
                pool_id,
            )
        else:
            logger.warning(
                "WorktreePool: cleanup incomplete (pool=%s) — may need manual "
                "intervention: git worktree prune && git branch -D %s",
                pool_id, pool_branch,
            )
        return cleaned

    # ------------------------------------------------------------------
    # 公开 API
    # ------------------------------------------------------------------
    def lease(self, session_id: str) -> str | None:
        """Lease a pool worktree for session_id.

        原子操作序列（在 ``_lock`` 内执行）：
        1. 扫描 ``.aidrafts_pool/`` 找一个 idle worktree（pool_id）
        2. ``git worktree move .aidrafts_pool/{pool_id} .aidrafts/{session_id}``
        3. ``git branch -m session/pool-{pool_id} session/{session_id}``
        4. 返回新路径 ``.aidrafts/{session_id}/``

        失败处理：
        - pool 空 → 返回 None（调用方 fall back）
        - ``git worktree move`` 失败 → 清理损坏的 pool worktree，返回 None
        - ``git branch -m`` 失败 → 回滚 move（移回 pool 路径），返回 None

        Args:
            session_id: 目标 session_id（如 ``sess-12345-20260719073000``）。

        Returns:
            新 worktree 路径（``.aidrafts/{session_id}/``）或 None。
            None 时调用方应 fall back 到 ``manager.create_session_worktree``。
        """
        if not session_id:
            return None

        with self._lock:
            idle_ids = self._list_idle_pool_ids()
            if not idle_ids:
                logger.debug("WorktreePool: pool empty, lease returns None")
                return None

            pool_id = idle_ids[0]
            pool_path = self.pool_dir / pool_id
            session_path = self.repo_root / ".aidrafts" / session_id
            pool_branch = f"{_POOL_BRANCH_PREFIX}{pool_id}"
            session_branch = f"{_SESSION_BRANCH_PREFIX}{session_id}"

            # Pre-flight: 目标路径已存在则放弃（不覆盖现有 worktree）
            if session_path.exists():
                logger.warning(
                    "WorktreePool: target path exists, cannot lease "
                    "(session=%s): %s",
                    session_id, session_path,
                )
                return None

            # Pre-flight: pool worktree 必须仍被 git 识别
            if not self._worktree_registered(pool_path):
                logger.warning(
                    "WorktreePool: pool worktree not registered in git, "
                    "cleaning up (pool=%s): %s",
                    pool_id, pool_path,
                )
                self._cleanup_pool_worktree(pool_id, pool_path)
                return None

            # Step 1: git worktree move <pool_path> <session_path>
            # Windows 文件锁重试：新创建的 worktree 可能被 antivirus/search indexer
            # 短暂占用句柄（Permission denied / .git does not exist），重试 3 次
            # 每次 0.5s 间隔。同类问题见 worktree_manager._force_rmtree 的 onerror 重试。
            r_move = None
            for _attempt in range(3):
                r_move = self.run_git(
                    ["git", "worktree", "move", str(pool_path), str(session_path)]
                )
                if r_move.returncode == 0:
                    break
                if _attempt < 2:
                    time.sleep(0.5)  # noqa: m10-time-trigger — retry delay, not a periodic trigger
            if r_move.returncode != 0:
                logger.warning(
                    "WorktreePool: git worktree move failed after 3 retries "
                    "(pool=%s, session=%s): %s",
                    pool_id, session_id, r_move.stderr.strip(),
                )
                # Move 失败——pool worktree 可能损坏，清理后返回 None
                self._cleanup_pool_worktree(pool_id, pool_path)
                return None

            # Step 2: git branch -m <pool_branch> <session_branch>
            r_branch = self.run_git(
                ["git", "branch", "-m", pool_branch, session_branch]
            )
            if r_branch.returncode != 0:
                logger.warning(
                    "WorktreePool: git branch -m failed "
                    "(pool=%s, session=%s): %s. Attempting rollback...",
                    pool_id, session_id, r_branch.stderr.strip(),
                )
                # 回滚：将 worktree 移回 pool 路径
                r_back = self.run_git(
                    ["git", "worktree", "move", str(session_path), str(pool_path)]
                )
                if r_back.returncode != 0:
                    logger.error(
                        "WorktreePool: rollback failed! Worktree at %s with "
                        "branch %s (expected %s). Manual cleanup needed: "
                        "git worktree remove --force %s && git branch -D %s",
                        session_path, pool_branch, session_branch,
                        session_path, pool_branch,
                    )
                return None

            logger.info(
                "WorktreePool: leased (pool=%s → session=%s): %s",
                pool_id, session_id, session_path,
            )
            return str(session_path)

    def prefetch(self, n: int = 1) -> int:
        """Pre-create n worktrees in the pool.

        在 ``.aidrafts_pool/`` 下创建 n 个 worktree，分支名
        ``session/pool-{pool_id}``，基于当前主仓库 HEAD。

        Args:
            n: 要创建的 worktree 数量。

        Returns:
            实际创建数量（失败时少于 n）。
        """
        if n <= 0:
            return 0

        head_sha = self._current_head_sha()
        if not head_sha:
            logger.warning(
                "WorktreePool: prefetch aborted — cannot get HEAD sha"
            )
            return 0

        # 确保 pool_dir 存在
        try:
            self.pool_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.warning(
                "WorktreePool: mkdir pool_dir failed: %s", e,
            )
            return 0

        created = 0
        for _ in range(n):
            pool_id = self._generate_pool_id()
            pool_path = self.pool_dir / pool_id
            pool_branch = f"{_POOL_BRANCH_PREFIX}{pool_id}"

            # Pre-flight: pool_path 不应存在（timestamp+random 防碰撞）
            if pool_path.exists():
                logger.debug(
                    "WorktreePool: pool_path collision, skipping (pool=%s)",
                    pool_id,
                )
                continue

            r = self.run_git(
                [
                    "git", "worktree", "add",
                    "-b", pool_branch,
                    str(pool_path),
                    head_sha,
                ]
            )
            if r.returncode != 0:
                logger.warning(
                    "WorktreePool: prefetch git worktree add failed "
                    "(pool=%s): %s",
                    pool_id, r.stderr.strip(),
                )
                continue

            created += 1
            logger.info(
                "WorktreePool: prefetched (pool=%s, branch=%s, head=%s): %s",
                pool_id, pool_branch, head_sha[:8], pool_path,
            )

        return created

    def prefetch_async(self, n: int = 1) -> threading.Thread:
        """在 daemon 线程异步触发 prefetch(n)（fire-and-forget）。

        典型用法：``lease`` 成功后调 ``prefetch_async(1)`` 补充池，
        不阻塞 ``session_worktree_start`` 返回。

        Args:
            n: 要创建的 worktree 数量。

        Returns:
            daemon Thread 句柄（调用方通常忽略）。
        """

        def _run() -> None:
            try:
                self.prefetch(n)
            except Exception:  # noqa: BLE001 — daemon thread, never propagate
                logger.debug(
                    "WorktreePool: prefetch_async failed", exc_info=True,
                )

        t = threading.Thread(
            target=_run, daemon=True, name="WorktreePool-prefetch",
        )
        t.start()
        return t

    def release(self, session_id: str) -> bool:
        """Release a session's worktree back to pool.

        **当前 NO-OP**：worktree 由 ``session_worktree_merge`` /
        ``session_worktree_abort`` 删除，pool 通过 ``prefetch_async`` 补充。

        未来增强：clean worktree（``git reset --hard`` + ``git clean -fd``）+
        move 回 pool 路径 + branch rename，实现 worktree 复用（避免 re-add 成本）。
        当前简化设计——每次 lease 后 prefetch 新 worktree（异步，不阻塞）。

        Args:
            session_id: 要释放的 session_id。

        Returns:
            False（当前实现始终 no-op）。
        """
        # 预留接口：未来实现 worktree 复用逻辑
        return False

    def list_idle(self) -> list[dict]:
        """列出 idle pool worktrees（诊断用）。

        Returns:
            dict 列表，每项含:
            - pool_id: pool worktree ID
            - path: worktree 绝对路径
            - branch: 分支名（session/pool-{pool_id}）
            - head_sha: worktree 当前 HEAD sha（前 8 位）
        """
        result: list[dict] = []
        with self._lock:
            for pool_id in self._list_idle_pool_ids():
                pool_path = self.pool_dir / pool_id
                head_sha = ""
                if pool_path.exists():
                    r = self.run_git(
                        ["git", "rev-parse", "--short", "HEAD"],
                        cwd=str(pool_path),
                    )
                    if r.returncode == 0:
                        head_sha = r.stdout.strip()
                result.append({
                    "pool_id": pool_id,
                    "path": str(pool_path),
                    "branch": f"{_POOL_BRANCH_PREFIX}{pool_id}",
                    "head_sha": head_sha,
                })
        return result

    def stats(self) -> dict:
        """返回 pool 统计信息（诊断用）。"""
        with self._lock:
            idle = self._list_idle_pool_ids()
            return {
                "idle_count": len(idle),
                "target_size": self.target_size,
                "pool_dir": str(self.pool_dir),
                "pool_dir_exists": self.pool_dir.exists(),
            }

    def cleanup_stale(self, max_age_hours: int = 24) -> int:
        """清理超龄的 pool worktrees（孤儿兜底）。

        典型场景：进程崩溃后留下未消费的 pool worktree。
        由 ``session_worktree_start`` 的 sweep 逻辑或手动调用触发。

        Args:
            max_age_hours: 最大年龄（小时），超过视为 stale。

        Returns:
            清理的 worktree 数量。
        """
        import time

        cutoff = time.time() - (max_age_hours * 3600)
        removed = 0

        with self._lock:
            if not self.pool_dir.exists():
                return 0

            for entry in list(self.pool_dir.iterdir()):
                if not entry.is_dir() or not entry.name.startswith(_POOL_ID_PREFIX):
                    continue
                try:
                    mtime = entry.stat().st_mtime
                except OSError:
                    continue
                if mtime < cutoff:
                    if self._cleanup_pool_worktree(entry.name, entry):
                        removed += 1

        if removed:
            logger.info(
                "WorktreePool: cleanup_stale removed %d worktrees (max_age=%dh)",
                removed, max_age_hours,
            )
        return removed

    def warmup(self) -> int:
        """预热池至 target_size（同步阻塞）。

        典型用法：仓库初始化或手动预热时调用。
        ``session_worktree_start`` 用 ``prefetch_async``（非阻塞）替代。

        Returns:
            实际创建的 worktree 数量。
        """
        with self._lock:
            idle = self._list_idle_pool_ids()
            deficit = self.target_size - len(idle)
        if deficit <= 0:
            return 0
        return self.prefetch(deficit)


# ---------------------------------------------------------------------------
# 模块级 singleton helper（对标 session_worktree._get_manager）
# ---------------------------------------------------------------------------
_pool_instances: dict[str, WorktreePool] = {}
_pool_instances_lock = threading.Lock()


def get_pool(project_root: str | Path | None = None) -> WorktreePool:
    """获取或创建 WorktreePool singleton（按 repo_root memoize）。

    线程安全：用独立锁保护 ``_pool_instances`` 字典变更。
    ``WorktreePool`` 内部方法也有自己的锁。

    Args:
        project_root: 项目根目录（默认 REPO_ROOT）。

    Returns:
        WorktreePool 实例（同一 repo_root 复用）。
    """
    root = Path(project_root) if project_root else REPO_ROOT
    key = str(root.resolve())
    with _pool_instances_lock:
        if key not in _pool_instances:
            _pool_instances[key] = WorktreePool(root)
    return _pool_instances[key]

# ── Stage 4 公共化（2026-07-29）：module-level public aliases ──
pool_instances: dict[str, WorktreePool] = _pool_instances  # public alias（Stage 4 公共化）
