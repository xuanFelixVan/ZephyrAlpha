# [BLUEPRINT] MOD-GOV_BATCHED_AUTO_COMMITTER | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §ARCH-GIT-CALL-BUDGET-P2.3
# [MODULE] zephyr.gov_enforcement.rule_bridge.batched_auto_committer
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.git_commit_gateway (GitCommitGateway._commit_auto 复用)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway (_run_post_commit_reconcile 包装); zephyr.gov_enforcement.rule_bridge.session_worktree (_run_reconcilers_after_merge 包装)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 拦截器模式——_commit_auto 入口检查 is_enabled()，命中则 buffer 替代真实 commit；flush() 临时 disable 后调 _commit_auto 聚合提交（squash N→1）；线程不安全（仅 post-commit 单线程上下文使用，reconcile_for 串行遍历 specs）；buffer 清空幂等（flush 后可重复 enable/flush）；所有 reconciler 共享同一 session_id（来自 enable 调用方，reconcile_for 入参）
# [MODIFY-GUARD] BatchedAutoCommitter 类名；enable/disable/is_enabled/buffer/flush/__enter__/__exit__ 方法签名
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] flush 失败返回 CommitResult(COMMIT_FAILED) 不抛异常；buffer 累积无上限（reconciler 数量有限，25 个 spec 最多 25 次 buffer）
# [TESTS] tests/governance/rule_bridge/test_batched_auto_committer.py
# [A_module] module_id=MOD-GOV_BATCHED_AUTO_COMMITTER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

batched_auto_committer.py — Reconciler 批量化 auto-commit 拦截器（ARCH-GIT-CALL-BUDGET P2.3，2026-07-19）

将 post-commit reconciler 阶段的 N 次独立 ``_commit_auto`` 调用合并为 1 次 squash
commit，消除「N reconciler × 1 git commit = N commits」反模式（典型场景：所有已注册
reconciler 中 5 个触发 auto-commit，产生 5 个独立 commit 刷屏 git log；
reconciler 数量以 ReconciliationRegistry 实际注册为准，不硬编码——裁定 D 治本 2026-07-19）。

病根（第一性原理）
-----------------
当前 ``ReconciliationRegistry.reconcile_for`` 遍历所有已注册 spec（数量以 ReconciliationRegistry 实际注册为准，不硬编码——裁定 D 治本 2026-07-19），每个 spec 的
``_reconcile`` 闭包独立调用 ``gateway._commit_auto(session_id, files, msg)``。
``_commit_auto`` 内部完整执行：merge-state check → DIRECTORY-CONTRACT gate →
TTL-METADATA gate → FILE-PLACEMENT-TTL gate → ``_GlobalCommitLock`` 获取 →
``git add`` → ``git diff --cached --quiet`` → ``git commit`` → 锁释放。

单次 ``_commit_auto`` 在 Windows 上成本 ~150-300ms（fscache/fsmonitor + lock
acquisition + 3 gates + 2 git subprocess）。5 个 reconciler 触发 auto-commit =
5 × 200ms = 1s+ 额外延迟 + 5 个独立 commit 刷屏 git log（如 ``chore(manifest):
auto-reconcile``、``chore(path-tree): auto-reconcile``、``chore(catalog):
auto-sync`` 等）。

治本方案（拦截器模式）
---------------------
在 ``_commit_auto`` 入口插入 batcher 检查：

1. ``enable(session_id)``：调用方（``_run_post_commit_reconcile`` /
   ``_run_reconcilers_after_merge``）在 ``reconcile_for`` 前启用 batcher
2. 每个 reconciler 调 ``_commit_auto`` 时被 batcher 拦截 → ``buffer(session_id,
   files, msg)`` 累积到内存列表，返回合成 ``CommitResult(status=OK,
   commit_hash="BUFFERED")``，reconciler 见 OK 返回 ``action="auto_committed"``
3. ``reconcile_for`` 返回后，调用方调 ``flush()`` → 临时 disable batcher →
   合并所有 buffered 文件（去重）+ 合并 message → 单次 ``_commit_auto`` 提交

为什么是拦截器模式而非修改 reconciler？
  - 所有已注册 reconciler 分布在 ``reconciliation_registry.py``（数量以 ReconciliationRegistry 实际注册为准，不硬编码——裁定 D 治本 2026-07-19），逐个
    修改成本高且易引入回归
  - 拦截器只在 ``_commit_auto`` 单一入口插入检查，零侵入 reconciler 代码
  - 向后兼容：batcher 未启用时 ``_commit_auto`` 行为完全不变（``is_enabled()``
    返回 False 直接 fall-through 到原逻辑）

一致性保证
----------
- 磁盘状态：reconciler 在调 ``_commit_auto`` 前已写盘（如 generate_manifest.py
  生成 manifest），batcher 只延迟 commit 不延迟写盘 → 后续 reconciler 看到最新
  磁盘状态，不会重复检测漂移
- git index：buffered 文件未 ``git add``，后续 reconciler 若用 ``git diff``
  检测漂移仍能看到工作区改动（这正是 reconciler 期望的行为——它检测的是
  「磁盘 vs HEAD」差异，不是「staged vs HEAD」）
- session_id：所有 buffer 共享 ``enable(session_id)`` 传入的 session_id，
  ``flush`` 时用此 session_id 调 ``_commit_auto``，GW marker 正确

Usage::

    # 在 _run_post_commit_reconcile / _run_reconcilers_after_merge 中：
    gateway = GitCommitGateway(project_root=root)
    with gateway.batched_auto_committer(session_id):
        results = gateway._reconciliation_registry.reconcile_for(
            committed_files, session_id, commit_message="",
        )
    # 退出 with 块时自动 flush，产生单个 squash commit

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: reconciler auto-commit 调用入参
#   fields: session_id + files 绝对路径列表 + commit message
#   code: buffer(session_id, files, message) L221-223；enable(session_id) L162
# - id: I2
#   name: GitCommitGateway 实例
#   fields: gateway._commit_auto 复用现有提交流程（DCR/TTL/FPT gate + 全局锁 + git add/commit）
#   code: BatchedAutoCommitter.__init__(gateway) L142-158
# 层: 算法
# - id: A1
#   name_zh: ① 批量模式开关
#   name_en: enable / disable / is_enabled
#   intro: enable 进入拦截模式并记 session_id、清空 buffer；disable 退出模式
#   desc: enable: _enabled=True + _session_id=sid + _buffer=[] L162-174；is_enabled 供 _commit_auto 入口查询 L187-189
#   inputs: I1
#   outputs: batching 模式状态
#   invariant: buffer 清空幂等，可重复 enable/flush
# - id: A2
#   name_zh: ② 提交拦截缓冲
#   name_en: BatchedAutoCommitter.buffer
#   intro: 拦截每个 reconciler 的 _commit_auto，不进 git 只攒进内存列表，回个合成成功回执
#   desc: 累积 BufferedCommit(session_id, files, message) L241-247；返回 CommitResult(OK, commit_hash="BUFFERED") L257-261 让 reconciler 记 auto_committed
#   inputs: I1 A1
#   outputs: 合成 CommitResult（BUFFERED）
#   invariant: 线程不安全，仅限 post-commit 单线程上下文
# - id: A3
#   name_zh: ③ 聚合 flush 提交
#   name_en: BatchedAutoCommitter.flush
#   intro: 把攒下的 N 次提交去重合并成 1 次 squash commit，消除 N reconciler 刷 N 个 commit
#   desc: 临时 disable 防自拦截 → 文件去重保序 L299-305 → message 合并为 bullet 列表 L308-313 → 单次 gateway._commit_auto L321 → finally 清空 buffer L341
#   inputs: A2 I2
#   outputs: CommitResult（OK+hash / NOTHING_TO_COMMIT / COMMIT_FAILED）
#   invariant: 空 buffer 返回 NOTHING_TO_COMMIT；失败也清空 buffer 防重复提交
# - id: A4
#   name_zh: ④ with 上下文协议
#   name_en: __enter__ / __exit__
#   intro: 退出 with 块自动 flush，即使块内异常也 flush 防 buffer 泄漏误拦后续提交
#   desc: __enter__ 返回 self 不自动 enable L345-359；__exit__ 调 flush（异常吞掉只 warn）+ 兜底 disable L361-376，不吞原异常
#   inputs: A3
#   outputs: 自动 flush 触发
# 层: 输出
# - id: O1
#   name_zh: 缓冲合成回执
#   name_en: CommitResult(status=OK, commit_hash="BUFFERED")
#   intro: 拦截期返回给 reconciler 的假成功回执， reconciler 凭此记 action=auto_committed
#   downstream: ReconciliationRegistry 各 reconciler（内部使用）
# - id: O2
#   name_zh: squash 提交结果
#   name_en: CommitResult
#   intro: flush 落地单个聚合 commit（chore(reconciler): batched auto-commit），并记 _last_flush_result 供调用方核验真落地
#   downstream: git_commit_gateway MOD-INF-035 与 session_worktree MOD-GOV_SESSION_WORKTREE（# [CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# I1 --> A2
# A2 --> A3
# I2 --> A3
# A4 --> A3
# A2 --> O1
# A3 --> O2
"""

from __future__ import annotations

__all__ = ["BatchedAutoCommitter", "BufferedCommit"]

import logging
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import CommitResult

logger = logging.getLogger(__name__)

# buffered commit 的合成 hash 标识（reconciler 见此值识别为已 buffer）
_BUFFERED_HASH = "BUFFERED"

# squash commit message 模板（flush 时生成）
_FLUSH_MSG_TEMPLATE = (
    "chore(reconciler): batched auto-commit ({n} reconcilers) by GitCommitGateway post-commit\n\n{entries}"
)


@dataclass
class BufferedCommit:
    """单次被拦截的 _commit_auto 调用记录。

    Attributes:
        session_id: 调用方传入的 session_id（同一 reconcile_for 内一致）。
        files: 待提交的绝对路径列表（可能跨 reconciler 重复，flush 时去重）。
        message: 原始 commit message（reconciler 特定，如
            "chore(manifest): auto-reconcile by GitCommitGateway post-commit"）。
    """

    session_id: str
    files: list[str]
    message: str


class BatchedAutoCommitter:
    """Reconciler auto-commit 批量化拦截器（squash N → 1）。

    生命周期：
      1. ``enable(session_id)`` → 进入 batching 模式，清空 buffer
      2. ``buffer(session_id, files, message)`` 被反复调用（每个 reconciler 一次）
      3. ``flush()`` → 退出 batching 模式，聚合 buffer 单次 _commit_auto
      4. 可重复 enable/flush（幂等，buffer 每次清空）

    也可作为 context manager 使用::

        with gateway.batched_auto_committer(session_id):
            reconcile_for(...)

    退出 with 块自动 flush。异常退出也会 flush（避免 buffer 泄漏导致后续
    reconciler 的 _commit_auto 被错误拦截）。

    线程安全：**非线程安全**。仅设计用于 post-commit / post-merge 单线程
    上下文（``reconcile_for`` 串行遍历 specs，无并发）。多线程场景需调用方
    自行加锁。
    """

    def __init__(self, gateway: "object") -> None:
        """初始化 batcher。

        Args:
            gateway: GitCommitGateway 实例。仅用于在 flush 时调
                ``gateway._commit_auto`` 复用现有 commit 流程（DCR/TTL/FPT gate
                + GlobalCommitLock + git add/commit）。类型注解为 object 避免
                本模块 import git_commit_gateway 产生循环依赖。
        """
        self._gateway = gateway
        self._enabled: bool = False
        self._session_id: str = ""
        self._buffer: list[BufferedCommit] = []
        # 治本 #ARCH-ASSET-INDEX-FALSE-AUTO-COMMIT-001：记录最近一次 flush 结果，
        # 供调用方（_run_post_commit_reconcile_sync_worker 等）在 with 块后验证
        # auto_committed 结果是否真正落地为 git commit。
        self._last_flush_result: "object | None" = None

    # ── 状态控制 ──────────────────────────────────────────────────────

    def enable(self, session_id: str = "") -> None:
        """启用 batching 模式，清空 buffer。

        Args:
            session_id: 本次 batch 的 session_id。所有后续 buffer() 调用
                使用此 session_id（reconcile_for 入参一致）。
        """
        self._enabled = True
        self._session_id = session_id
        self._buffer = []
        logger.debug(
            "BatchedAutoCommitter: enabled (session=%s)",
            session_id,
        )

    def disable(self) -> None:
        """禁用 batching 模式（不清空 buffer，便于诊断）。

        注意：正常流程应使用 flush() 而非 disable()。disable 仅用于异常
        恢复场景（如 flush 失败后强制退出 batch 模式）。
        """
        self._enabled = False
        logger.debug(
            "BatchedAutoCommitter: disabled (buffer size=%d)",
            len(self._buffer),
        )

    def is_enabled(self) -> bool:  # noqa: m03-duplicate  M03豁免: 平凡一行属性getter(return self._enabled)，AI趋同演化非复制粘贴
        """当前是否处于 batching 模式。"""
        return self._enabled

    def buffered_files(self) -> set[str]:
        """返回当前 buffer 中所有文件的相对路径集合（POSIX 风格，相对 project_root）。

        治本 #ARCH-ASSET-INDEX-FALSE-AUTO-COMMIT-001：
        供后序 reconciler（如 workspace_hygiene）检测冲突——避免 ``git restore``
        还原已被前序 reconciler 写盘并 buffer 待提交的文件。

        病根：GATE-ASSET-INDEX(priority=170) 写索引文件 → ``_commit_auto`` 被
        ``buffer()`` 拦截返回合成 OK（未真正提交）；workspace_hygiene(priority=890)
        随后把该文件当 auto-sync 产物 ``git restore`` 还原回 HEAD；flush() 时
        ``git diff --cached --quiet`` 返回 0 → NOTHING_TO_COMMIT，但 reconciler
        已记 auto_committed，造成"日志说已重生实际未重生"的治理盲区。

        Returns:
            buffer 中所有文件的相对路径集合（POSIX 风格）。batcher 未启用或
            buffer 为空时返回空集合。
        """
        if not self._buffer:
            return set()
        root = str(self._gateway.project_root)
        root_abs = os.path.abspath(root)
        result: set[str] = set()
        for entry in self._buffer:
            for f in entry.files:
                rel = os.path.relpath(os.path.abspath(f), root_abs).replace("\\", "/")
                result.add(rel)
        return result

    # ── 拦截入口 ──────────────────────────────────────────────────────

    def buffer(
        self,
        session_id: str,
        files: list[str],
        message: str,
    ) -> "CommitResult":
        """拦截 _commit_auto 调用，累积到 buffer。

        本方法由 ``GitCommitGateway._commit_auto`` 在 ``is_enabled()`` 为 True
        时调用，替代真实 git commit。返回合成 CommitResult(status=OK) 使
        reconciler 见「auto-commit 成功」返回 ``action="auto_committed"``。

        Args:
            session_id: 调用方 session_id（与 enable 一致；不一致时以最新为准）。
            files: 待提交文件绝对路径列表。
            message: commit message。

        Returns:
            合成 CommitResult(status=OK, commit_hash="BUFFERED")。
        """
        # 以最新 session_id 为准（防御性——理论上同一 reconcile_for 内一致）
        if session_id:
            self._session_id = session_id
        self._buffer.append(
            BufferedCommit(
                session_id=self._session_id,
                files=list(files),
                message=message,
            )
        )
        logger.debug(
            "BatchedAutoCommitter: buffered %d files (msg=%r, total buffered=%d)",
            len(files),
            message[:80],
            len(self._buffer),
        )
        # 延迟 import 避免循环依赖
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
            CommitResult,
            CommitStatus,
        )

        return CommitResult(
            status=CommitStatus.OK,
            message=f"buffered {len(files)} files (pending flush)",
            commit_hash=_BUFFERED_HASH,
        )

    # ── 聚合提交 ──────────────────────────────────────────────────────

    def flush(self) -> "CommitResult":
        """聚合 buffer 中所有 _commit_auto 调用，单次 commit 提交。

        流程：
        1. 临时 disable batcher（避免 _commit_auto 再被拦截）
        2. 去重所有 buffered 文件（跨 reconciler 可能改同一文件，如
           capability_canonical_file_registry.yaml 被 catalog + capability
           两个 reconciler 同时更新）
        3. 合并 message（每条原 message 作为 bullet 列出）
        4. 单次 ``gateway._commit_auto(session_id, all_files, combined_msg)``
        5. 清空 buffer，返回 CommitResult

        若 buffer 为空，返回 NOTHING_TO_COMMIT（无 reconciler 触发 auto-commit）。
        若 ``_commit_auto`` 失败，返回对应错误状态，buffer 仍清空（避免重试
        产生重复 commit；调用方见 warn 可手动修复）。

        Returns:
            CommitResult：OK + commit_hash（成功）/ NOTHING_TO_COMMIT（空 buffer）
            / COMMIT_FAILED / LOCK_TIMEOUT 等（_commit_auto 失败）。
        """
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
            CommitResult,
            CommitStatus,
        )

        if not self._buffer:
            # 空 buffer：无 reconciler 触发 auto-commit，正常场景
            self._enabled = False
            return CommitResult(
                status=CommitStatus.NOTHING_TO_COMMIT,
                message="batched flush: empty buffer (no reconciler triggered auto-commit)",
            )

        # 1. 去重文件（保序——首次出现的 reconciler 拥有该文件的「主权」）
        all_files: list[str] = []
        seen: set[str] = set()
        for entry in self._buffer:
            for f in entry.files:
                if f not in seen:
                    seen.add(f)
                    all_files.append(f)

        # 2. 合并 message（每条原 message 作为 bullet）
        entries = "\n".join(f"- {entry.message}" for entry in self._buffer)
        combined_msg = _FLUSH_MSG_TEMPLATE.format(
            n=len(self._buffer),
            entries=entries,
        )

        # 3. 临时 disable，调 _commit_auto（避免被自身拦截）
        self._enabled = False
        buffer_count = len(self._buffer)
        files_count = len(all_files)
        # 清空 buffer 在 finally 中执行——即使 _commit_auto 失败也不留残余
        try:
            result = self._gateway._commit_auto(
                self._session_id,
                all_files,
                combined_msg,
            )
            if result.status == CommitStatus.OK:
                logger.info(
                    "BatchedAutoCommitter: flush 成功 squash %d buffered → 1 commit (hash=%s, files=%d, session=%s)",
                    buffer_count,
                    result.commit_hash,
                    files_count,
                    self._session_id,
                )
            else:
                logger.warning(
                    "BatchedAutoCommitter: flush _commit_auto 返回 %s (msg=%s, buffered=%d, files=%d)",
                    result.status,
                    result.message[:200],
                    buffer_count,
                    files_count,
                )
            # 治本 #ARCH-ASSET-INDEX-FALSE-AUTO-COMMIT-001：记录 flush 结果，
            # 供调用方在 with 块后验证 auto_committed 是否真正落地。
            self._last_flush_result = result
            return result
        finally:
            self._buffer = []

    # ── Context manager 协议 ─────────────────────────────────────────

    def __enter__(self) -> "BatchedAutoCommitter":
        """进入 with 块：返回 self，不自动 enable。

        调用方必须在 with 块内显式调 ``enable(session_id)`` 才会激活拦截。
        这样设计是为了让 session_id 来自 with 块内的局部变量，而非
        ``__enter__`` 调用前的预设。

        典型用法::

            with gateway._batcher as batcher:
                batcher.enable(session_id)
                reconcile_for(...)
            # 退出 with 块时自动 flush
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出 with 块：自动 flush（即使异常也 flush，避免 buffer 泄漏）。

        异常场景下 flush 可能也失败，但至少清空 buffer + disable batcher，
        避免后续 _commit_auto 调用被错误拦截。异常不吞——只 flush，原异常
        继续传播。
        """
        try:
            self.flush()
        except Exception as e:  # noqa: BLE001 — flush 异常不应掩盖 with 块内原异常
            logger.warning(
                "BatchedAutoCommitter: __exit__ flush 异常（已吞，原异常优先）: %s",
                e,
            )
        # 确保 batcher 被禁用（flush 内部已 disable，此处兜底）
        self._enabled = False
        # 不返回 True——不吞 with 块
