# [BLUEPRINT] MOD-INF-003 | docs/03_modules/_domain_infrastructure/runtime_integration/blueprint.md | §ARCH-GIT-CALL-BUDGET
# [MODULE] zephyr.infrastructure.git_batcher
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] stdlib (subprocess, tarfile, io, pathlib, logging, typing)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.session_worktree (collector 批量化); zephyr.gov_enforcement.commit_gates.* (diff helpers 批量化); zephyr.governance.audit.workspace_hygiene_reconciler (auto-sync restore 批量化)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 所有方法返回 dict/list 结构，不抛异常——subprocess 失败返回空容器；git archive --format=tar 单次调用替代 N 次 git show；线程安全（无共享可变状态）
# [MODIFY-GUARD] GitCommandBatcher 类名；git_show_batch/git_diff_cached_names/git_diff_names/git_ls_files_tracked/git_restore_batch 方法签名
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] subprocess 超时/失败返回空 dict/list + log warning；tarfile 解析失败返回空 dict + log warning
# [TESTS] tests/infrastructure/test_git_batcher.py
# [A_module] module_id=MOD-INF-003 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

git_batcher.py — Git 命令批量化工具（ARCH-GIT-CALL-BUDGET P2.2，2026-07-19）

将 N 次独立 git 子进程调用合并为 1 次批量调用，消除逐文件 git 调用反模式
（N 文件 = N subprocess → 1 subprocess）。

病根（第一性原理）
-----------------
git 是昂贵外部资源，每次 ``subprocess.run(["git", ...])`` 在 Windows 上成本
~50-100ms + fscache/fsmonitor 初始化开销。100% AI 开发场景下 session_worktree /
gates / reconcilers 高频调 git，逐文件调用在 14 万文件工作区上是 git.exe 2.48.x
崩溃（0xc0000005 @ 0x13e4d4）的放大源。

批量化方案
----------
- ``git_show_batch``: 用 ``git archive --format=tar`` 一次获取 N 个文件内容
  （替代 N 次 ``git show <ref>:<file>``）
- ``git_diff_cached_names``: 用 ``git diff --cached --name-only`` 一次获取 staged 文件名
- ``git_diff_names``: 用 ``git diff --name-only <ref_spec>`` 一次获取 diff 文件名
- ``git_ls_files_tracked``: 用 ``git ls-files`` 一次获取 tracked 文件列表
- ``git_restore_batch``: 用 ``git restore [--staged] -- <files>`` 一次还原 N 个文件
  （替代 N 次 ``git restore -- <file>``，workspace_hygiene_reconciler 使用）

设计权衡
--------
1. **git archive --format=tar**：比 ``git show`` N 次调用快 N 倍，且避免 N 次
   fscache/fsmonitor 初始化（崩溃路径）。tar 格式可流式解析。
2. **不依赖 pygit2/gitpython**：纯 stdlib + git CLI，零额外依赖。
3. **fail-open**：subprocess 失败返回空容器（不抛异常），调用方需检查空结果。
4. **线程安全**：无共享可变状态，每次调用创建独立的 subprocess。

Usage::

    from zephyr.infrastructure.git_batcher import GitCommandBatcher

    batcher = GitCommandBatcher("/path/to/repo")

    # 批量获取 N 个文件内容（1 次 git archive 替代 N 次 git show）
    contents = batcher.git_show_batch("HEAD", ["src/foo.py", "src/bar.py"])
    # contents == {"src/foo.py": b"...", "src/bar.py": b"..."}

    # 批量获取 staged 文件名
    staged = batcher.git_diff_cached_names()

    # 批量获取 tracked 文件
    tracked = batcher.git_ls_files_tracked(["src/foo.py", "src/bar.py"])

    # 批量还原 N 个文件到 HEAD（1 次 git restore 替代 N 次）
    restored = batcher.git_restore_batch(["src/foo.py", "src/bar.py"])
    # restored == ["src/foo.py", "src/bar.py"]（成功）或 []（失败 fail-open）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 仓库根目录
#   fields: git 仓库绝对路径
#   code: GitCommandBatcher.__init__ L89
# - id: I2
#   name: 批量 git 查询参数
#   fields: ref 引用 / files 相对路径列表 / ref_spec 区间 / staged 标志 / timeout 秒
#   code: git_show_batch(ref, files) L102
# - id: I3
#   name: git CLI 子进程输出
#   fields: git archive tar 字节流 / diff --name-only / ls-files / restore 的 stdout
#   code: run_subprocess_hidden L125（cwd=repo，timeout 默认 60s）
# 层: 算法
# - id: A1
#   name_zh: ① 批量取文件内容
#   name_en: git_show_batch
#   intro: 一次 git archive 拿 N 个文件内容，替代 N 次 git show
#   desc: git archive --format=tar <ref> -- <files> 单次调用；超时/异常/rc≠0 全返回空 dict（fail-open）
#   inputs: I2 I3
#   outputs: {文件路径: 内容字节} 字典
#   invariant: N 文件 = 1 次 subprocess；失败返回空容器不抛异常
# - id: A2
#   name_zh: ② tar 流式解析
#   name_en: _parse_tar_archive
#   intro: 把 archive 的 tar 字节流拆成逐文件的内容字典
#   desc: tarfile.open(mode="r|") 流式遍历 member，isfile 才 extractfile 读出 bytes；TarError 返回空 dict
#   inputs: A1
#   outputs: {file_path: content}
# - id: A3
#   name_zh: ③ 批量取文件名列表
#   name_en: git_diff_cached_names / git_diff_names / git_ls_files_tracked
#   intro: 一次命令拿全部 staged/diff/tracked 文件名，按行拆分返回
#   desc: git diff --cached --name-only / git diff --name-only <ref_spec> / git ls-files，可拼 pathspec 限定范围；stdout 按行 strip 成列表
#   inputs: I2 I3
#   outputs: 文件相对路径列表
# - id: A4
#   name_zh: ④ 批量还原文件
#   name_en: git_restore_batch
#   intro: 一次 git restore 还原 N 个文件，失败不逐个重试防崩溃放大
#   desc: git restore [--staged] -- <files>；rc=0 返回全部 files；失败返回空列表，交给下次 post-commit 事件兜底
#   inputs: I2 I3
#   outputs: 成功还原的文件列表
#   invariant: 禁止逐个重试（GIT-BUDGET-INV-002）
# 层: 输出
# - id: O1
#   name_zh: 批量文件内容与文件名
#   name_en: dict[str, bytes] / list[str]
#   intro: 文件内容字典和各类文件名列表，给收集器和门禁做批量 diff 分析
#   downstream: session_worktree（collector 批量化）；commit_gates.*（diff helpers）；workspace_hygiene_reconciler（# [CONSUMERS] 头）
# - id: O2
#   name_zh: 批量还原结果
#   name_en: restored list
#   intro: auto-sync restore 批量化的成功清单，空列表表示失败待兜底
#   downstream: workspace_hygiene_reconciler（auto-sync restore 批量化）
# [/ALGO_FLOW]
#
# 边:
# I2 --> A1
# I3 --> A1
# A1 --> A2
# I2 --> A3
# I3 --> A3
# I2 --> A4
# I3 --> A4
# A2 --> O1
# A3 --> O1
# A4 --> O2
"""

from __future__ import annotations

import hashlib
import io
import logging
import os
import subprocess
import tarfile
from pathlib import Path
from typing import Optional

from zephyr.shared.infra.process_pool import run_subprocess_hidden

logger = logging.getLogger(__name__)

__all__ = ["GitCommandBatcher"]


class GitCommandBatcher:
    """Git 命令批量化工具——将 N 次子进程调用合并为 1 次。

    所有方法 fail-open：subprocess 失败返回空容器，不抛异常。
    """

    def __init__(self, project_root: Path | str) -> None:
        """初始化批量化工具。

        Args:
            project_root: git 仓库根目录（绝对路径）。
        """
        self._root = Path(project_root)

    def parse_tar_archive(self, tar_bytes) -> dict[str, bytes]:
        """公共接口：parse_tar_archive（Stage 4 公共化）。"""
        return self._parse_tar_archive(tar_bytes)


    def git_show_batch(
        self, ref: str, files: list[str], timeout: int = 60
    ) -> dict[str, bytes]:
        """批量获取 git ref 中指定文件的内容。

        用 ``git archive --format=tar <ref> -- <files>`` 一次获取 N 个文件内容，
        替代 N 次 ``git show <ref>:<file>``。

        Args:
            ref: git 引用（如 "HEAD", "dev", commit SHA）。
            files: 文件相对路径列表。
            timeout: subprocess 超时秒数。

        Returns:
            ``{file_path: file_content_bytes}`` 字典。
            不存在的文件不在结果中（git archive 跳过）。
            subprocess 失败时返回空字典。
        """
        if not files:
            return {}

        try:
            cmd = ["git", "archive", "--format=tar", ref, "--"] + files
            r = run_subprocess_hidden(
                cmd, cwd=str(self._root), capture_output=True, timeout=timeout,
            text=False)
        except subprocess.TimeoutExpired:
            logger.warning("git_show_batch: timeout after %ss (ref=%s, %d files)", timeout, ref, len(files))
            return {}
        except Exception as e:  # noqa: BLE001
            logger.warning("git_show_batch: subprocess failed: %s", e)
            return {}

        if r.returncode != 0:
            stderr = r.stderr.decode("utf-8", errors="replace").strip()[:200]
            logger.warning("git_show_batch: git archive failed (rc=%d): %s", r.returncode, stderr)
            return {}

        return self._parse_tar_archive(r.stdout)

    def git_diff_cached_names(
        self, files: list[str] | None = None, timeout: int = 60
    ) -> list[str]:
        """批量获取 staged 文件名。

        Args:
            files: 可选——限定文件范围（pathspec）。None = 所有 staged 文件。
            timeout: subprocess 超时秒数。

        Returns:
            staged 文件相对路径列表。subprocess 失败时返回空列表。
        """
        cmd = ["git", "diff", "--cached", "--name-only"]
        if files:
            cmd += ["--"] + files
        return self._run_git_name_list(cmd, timeout, "git_diff_cached_names")

    def git_diff_names(
        self, ref_spec: str, files: list[str] | None = None, timeout: int = 60
    ) -> list[str]:
        """批量获取 diff 文件名。

        Args:
            ref_spec: diff 引用规格（如 "HEAD~1..HEAD", "dev..main"）。
            files: 可选——限定文件范围。None = 所有 diff 文件。
            timeout: subprocess 超时秒数。

        Returns:
            diff 文件相对路径列表。subprocess 失败时返回空列表。
        """
        cmd = ["git", "diff", "--name-only", ref_spec]
        if files:
            cmd += ["--"] + files
        return self._run_git_name_list(cmd, timeout, "git_diff_names")

    def git_ls_files_tracked(
        self, files: list[str] | None = None, timeout: int = 60
    ) -> list[str]:
        """批量获取 tracked 文件列表。

        Args:
            files: 可选——限定文件范围。None = 所有 tracked 文件。
            timeout: subprocess 超时秒数。

        Returns:
            tracked 文件相对路径列表。subprocess 失败时返回空列表。
        """
        cmd = ["git", "ls-files"]
        if files:
            cmd += ["--"] + files
        return self._run_git_name_list(cmd, timeout, "git_ls_files_tracked")

    def git_restore_batch(
        self, files: list[str], timeout: int = 60, *, staged: bool = False
    ) -> list[str]:
        """批量 git restore 还原文件（GIT-BUDGET-INV-002 批量化强制）。

        用 ``git restore [--staged] -- <files>`` 一次还原 N 个文件，
        替代 N 次 ``git restore -- <file>``（逐文件调用是 git.exe 崩溃放大源）。

        fail-open：批量失败返回空列表，**不逐个重试**——逐个重试本身是
        GIT-BUDGET-INV-002 反模式。调用方应依赖下次 post-commit 事件兜底。

        Args:
            files: 待还原文件相对路径列表。
            timeout: subprocess 超时秒数。
            staged: True = 还原 staged 状态（``git restore --staged``），
                False = 还原 worktree 到 HEAD（默认，``git restore``）。

        Returns:
            成功还原的文件路径列表（returncode=0 时返回全部 files 副本）。
            subprocess 失败 / returncode!=0 时返回空列表。
        """
        if not files:
            return []

        # P2-6 遥测（2026-08-19 循环审计 R1 治本）：git restore 是主工作区文件级擦除
        # （内容还原到 HEAD），项目记忆硬约束要求全量遥测——操作前内容 hash 落
        # worktree_ops_log.jsonl 支持事后审计恢复；遥测失败绝不阻断主流程。
        pre_hashes: dict[str, str] = {}
        for rel in files:
            try:
                p = self._root / rel
                pre_hashes[rel] = hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.is_file() else ""
            except OSError:
                pre_hashes[rel] = ""

        cmd = ["git", "restore"]
        if staged:
            cmd.append("--staged")
        cmd += ["--"] + files

        try:
            r = run_subprocess_hidden(
                cmd, cwd=str(self._root), capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            logger.warning(
                "git_restore_batch: timeout after %ss (%d files)",
                timeout, len(files),
            )
            return []
        except Exception as e:  # noqa: BLE001 — fail-open
            logger.warning("git_restore_batch: subprocess failed: %s", e)
            return []

        if r.returncode == 0:
            try:
                from zephyr.shared.io.workspace_telemetry import (  # noqa: PLC0415 延迟 import 防循环
                    log_workspace_op,
                )

                for rel in files:
                    log_workspace_op(
                        op="git_restore_batch",
                        session_id=os.environ.get("ZEPHYR_SESSION_ID", ""),
                        source="git_batcher.git_restore_batch",
                        root=self._root,
                        file=rel,
                        content_hash=pre_hashes.get(rel, ""),
                    )
            except Exception:  # noqa: BLE001 — 遥测失败不阻断
                logger.debug("git_restore_batch: telemetry failed", exc_info=True)
            return list(files)

        stderr = r.stderr.strip()[:300]
        logger.warning(
            "git_restore_batch: git restore failed (rc=%d, %d files): %s",
            r.returncode, len(files), stderr,
        )
        return []

    def _parse_tar_archive(self, tar_bytes: bytes) -> dict[str, bytes]:
        """解析 git archive --format=tar 的输出，返回 {file_path: content} 字典。

        fail-open：tarfile 解析失败返回空字典。
        """
        result: dict[str, bytes] = {}
        try:
            bio = io.BytesIO(tar_bytes)
            with tarfile.open(fileobj=bio, mode="r|") as tar:
                for member in tar:
                    if not member.isfile():
                        continue
                    name = member.name
                    # git archive 输出的文件名可能带前缀（如 src/zephyr/...）
                    f = tar.extractfile(member)
                    if f is not None:
                        result[name] = f.read()
        except tarfile.TarError as e:
            logger.warning("_parse_tar_archive: tarfile parse failed: %s", e)
        except Exception as e:  # noqa: BLE001
            logger.warning("_parse_tar_archive: unexpected error: %s", e)
        return result

    def _run_git_name_list(
        self, cmd: list[str], timeout: int, caller: str
    ) -> list[str]:
        """运行返回文件名列表的 git 命令（git diff --name-only / git ls-files）。

        fail-open：subprocess 失败返回空列表。
        """
        try:
            r = run_subprocess_hidden(
                cmd, cwd=str(self._root), capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            logger.warning("%s: timeout after %ss", caller, timeout)
            return []
        except Exception as e:  # noqa: BLE001
            logger.warning("%s: subprocess failed: %s", caller, e)
            return []

        if r.returncode != 0:
            stderr = r.stderr.strip()[:200]
            logger.warning("%s: git command failed (rc=%d): %s", caller, r.returncode, stderr)
            return []

        return [line.strip() for line in r.stdout.split("\n") if line.strip()]
