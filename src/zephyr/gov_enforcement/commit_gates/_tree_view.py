# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates._tree_view
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers
# [CONSUMERS] scripts/governance/replay_gate_verdicts.py（重放安全网，未接线进任何门禁）
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 只读观测面——四个入口语义逐一对齐 _diff_helpers（read_staged_file/staged_files/added_lines/read_head_file），fail-open 口径零改动；仓库态唯一经 git（cat-file/show/diff <rev> <rev>/ls-tree），本模块自身零工作树直读；内置 WorktreeReadProbe 双通道计数（git 命令分类 + 进程内文件系统直读归因）；SharedIndexCommitTreeView 仅用于"模拟今天共享 index"对照实验，不改变任何判据语义；本模块未被任何 gate 导入=零生产影响面
# [MODIFY-GUARD] 类 CommitTreeView(base_rev,head_rev,gateway=None).run_git(cmd,cwd=None)->CompletedProcess；四方法签名与 _diff_helpers 同名函数逐参对齐（gateway 位置换成 self）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 永不静默改口径——无法映射到 rev 域的 git 命令按 strict/passthrough 两模式处理（默认 passthrough 且计数上报）；异常降级返回值与 _diff_helpers 一致（None/[]）
# [TESTS] tests/governance/test_gate_replay_harness.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
r"""_tree_view.py — 不可变提交树视图 CommitTreeView（S1 治本前置安全网）

一句话
------
把门禁今天从"共享暂存区"读到的四类观测，改从两个不可变 rev
(``base_rev``/``head_rev``) 复现——同一套判据、同一份 fail-open 口径，
唯一变化是读的对象从"本机暂态 index + 工作树"变成"提交树"。

为什么需要它（提交链提速夜战背景）
----------------------------------
单文件门禁链 64s 的根因：门禁经 ``git diff --cached`` / ``git show :path``
读共享暂存区，成本与本件 diff 无关、只与 index 规模有关（实测窗口内
index 挂着数百个他会话 staged 文件）。治本方向 S1＝门禁改读"不可变提交树
视图"。S1 一次动 72 台门咽喉，失败模式是**静默假绿**，故发布判据必须是
"重放历史提交、逐台 verdict 与当时 100% 全等"。本模块是该重放安全网的
读侧原语：**先于**任何门禁改指存在。

四类观测的映射（与 ``_diff_helpers`` 一一对应）
------------------------------------------------
======================================  ======================================
``_diff_helpers`` 现状（共享 index）     本视图（不可变 rev 域）
======================================  ======================================
``git show :path``                      ``git show <head_rev>:path``
``git diff --cached --name-only``       ``git diff <base_rev> <head_rev>
 --diff-filter=AM[|AMR]                  --name-only --diff-filter=AM[|AMR]``
``git diff --cached --unified=0         ``git diff <base_rev> <head_rev>
  --ignore-cr-at-eol -- path``            --unified=0 --ignore-cr-at-eol -- path``
``git show HEAD:path``                  ``git show <base_rev>:path``
======================================  ======================================

关键不变式（工作树直读探针）
----------------------------
CommitTreeView 只能经 ``git`` 读仓库态。任何"退回到磁盘/工作树"的路径都必须
留痕，否则 S1 会静默换口径。探针两条通道：

1. **命令通道** ``WorktreeReadProbe.git_worktree_reads``：每条经过视图的 git
   命令按 ``map_git_command`` 分类——``index->tree`` / ``head->base`` /
   ``tree-scope`` / ``repo`` 为合法仓库态读；``worktree``（status、裸
   ``git diff``、裸 ``ls-files`` …）与 ``unmapped`` 计为直读尝试。
2. **进程内通道** ``WorktreeReadProbe.fs_reads``：``with probe.arm()`` 期间
   临时替换 ``builtins.open`` / ``os.path.*`` / ``pathlib.Path.*``，按"最近
   非本模块调用帧"归因记录工作树读取。视图自身方法必须恒 0；某门"用 tree
   视图却读磁盘"→ 归因到该门的模块名＝绊线。

两模式（默认测量模式，语义不改）：
- ``strict=False``（默认）：无法映射的命令原样透传给真实 git，但计数上报
  ——这正是"哪些门还在读工作树"的运行时证据。
- ``strict=True``：抛 :class:`WorktreeReadBlocked`，用于红证测试。

只读声明
--------
本模块不写任何文件（探针记录在内存）、不改任何门禁、不被任何门禁导入。
接线进门禁是后续批次的事，且必须先有重放基线（见
``scripts/governance/replay_gate_verdicts.py``）。
# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/t/tree_view.yaml
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeVar, Any, Callable, Iterable, Final

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _parse_diff_with_line_numbers,
)

logger = logging.getLogger(__name__)

__all__: Final = [
    "GitCommandMap",
    "IndexNoiseSource",
    "MemoryNoiseSource",
    "RealIndexNoiseSource",
    "SharedIndexCommitTreeView",
    "CommitTreeView",
    "WorktreeReadBlocked",
    "WorktreeReadProbe",
    "map_git_command",
]

_THIS_MODULE = __name__

# 归因时跳过的"不算读者"的帧（标准库内部转发 + 本模块自身）
_ATTRIBUTION_SKIP_PREFIXES = (
    _THIS_MODULE,
    "pathlib",
    "subprocess",
    "importlib",
    "logging",
    "contextlib",
    "zephyr.shared.infra.process_pool",
)

# git 取值型全局选项（其后一个 token 是值，不能当子命令）
_GIT_OPT_WITH_VALUE = frozenset(
    {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--super-prefix"}
)

# 明确读工作树（或写）的子命令——tree 视图无法服务其请求
_WORKTREE_SUBCMDS = frozenset(
    {
        "status",
        "stash",
        "clean",
        "add",
        "rm",
        "mv",
        "checkout",
        "restore",
        "apply",
        "update-index",
        "write-tree",
        "read-tree",
        "commit",
        "diff-files",
        "diff-index",  # 不带 HEAD 时 = 工作树 vs index
        "fsck",
        "prune",
        "worktree",
        "grep",
    }
)

# 纯仓库态读（rev 域自洽，passthrough 即可）
_REPO_READ_SUBCMDS = frozenset(
    {
        "cat-file",
        "ls-tree",
        "log",
        "rev-list",
        "blame",
        "merge-base",
        "describe",
        "config",
        "name-rev",
        "hash-object",
        "shortlog",
        "show-ref",
        "for-each-ref",
        "symbolic-ref",
        "diff-tree",
        "archive",
    }
)

# 输出会被门禁当"当前 HEAD"解读的命令——HEAD / HEAD:path / HEAD^ 需改指 base
_HEAD_SENSITIVE_SUBCMDS = frozenset({"rev-parse", "rev-list", "merge-base", "describe", "log"})

# 需要把裸 HEAD / HEAD: 锚点改指 base 的全部读子命令
_HEAD_AWARE_SUBCMDS = (
    _REPO_READ_SUBCMDS
    | _HEAD_SENSITIVE_SUBCMDS
    | frozenset({"cat-file", "ls-tree", "show", "diff", "diff-tree", "blame"})
)


def _rewrite_head_anchors(argv: list[str], start: int, base_rev: str) -> tuple[list[str], bool]:
    """把 ``HEAD`` / ``HEAD:path`` / ``HEAD^`` 类锚点改指 base（视图的"提交前态"）。

    生产链上 ``HEAD`` 恒等于本次提交的父提交，重放时今天的 HEAD 早已前移——
    不改指会让"提交前版本"读到错的内容（口径静默漂移，正是 S1 的假绿模式）。
    """
    out = list(argv)
    changed = False
    for i in range(start, len(out)):
        tok = out[i]
        if tok == "HEAD" or tok.startswith("HEAD^") or tok.startswith("HEAD~"):
            out[i] = base_rev + tok[4:]
            changed = True
        elif tok.startswith("HEAD:"):
            out[i] = f"{base_rev}{tok[4:]}"
            changed = True
    return out, changed


_KIND_INDEX_TO_TREE = "index->tree"
_KIND_HEAD_TO_BASE = "head->base"
_KIND_TREE_SCOPE = "tree-scope"
_KIND_REPO = "repo"
_KIND_WORKTREE = "worktree"

_OK_KINDS = frozenset({_KIND_INDEX_TO_TREE, _KIND_HEAD_TO_BASE, _KIND_TREE_SCOPE, _KIND_REPO})


class WorktreeReadBlocked(RuntimeError):
    """strict 模式下被拒绝的工作树直读（红证/绊线用）。"""

    error_code = "ZA-TREEVIEW-001"


@dataclass
class GitCommandMap:
    """一条 git 命令的映射结果。

    Attributes:
        kind: 分类（``index->tree`` / ``head->base`` / ``tree-scope`` / ``repo`` /
            ``worktree``）。
        argv: 改写后的 argv（passthrough 时等于入参）。
        rewritable: 是否存在等价的纯仓库态读法（False=该命令本质上依赖工作树）。
    """

    kind: str
    argv: list[str] = field(default_factory=list)
    rewritable: bool = True

    @property
    def touches_worktree(self) -> bool:
        """该命令是否构成工作树直读（探针计数口径）。"""
        return self.kind == _KIND_WORKTREE or not self.rewritable


def _git_subcmd(argv: list[str]) -> tuple[int, str]:
    """返回 (子命令下标, 子命令名)；非 git 调用返回 (-1, "")。"""
    if len(argv) < 2 or argv[0] != "git":
        return -1, ""
    i = 1
    while i < len(argv):
        tok = argv[i]
        if tok in _GIT_OPT_WITH_VALUE:
            i += 2
            continue
        if tok.startswith("-"):
            i += 1
            continue
        return i, tok
    return -1, ""


def _split_pathspec(argv: list[str], start: int) -> tuple[list[str], list[str]]:
    """把子命令参数切成 (选项段, pathspec 段)——以首个裸 ``--`` 为界。"""
    if "--" in argv[start:]:
        j = argv.index("--", start)
        return argv[start:j], argv[j + 1 :]
    return argv[start:], []


def map_git_command(argv: list[str], base_rev: str, head_rev: str) -> GitCommandMap:
    """把门禁发出的 git 命令映射到不可变 rev 域（核心改写表）。

    Args:
        argv: 门禁原始命令（如 ``["git", "show", ":a.py"]``）。
        base_rev: 视图的"提交前仓库态"＝父提交。
        head_rev: 视图的"本件内容"＝目标提交。

    Returns:
        :class:`GitCommandMap`——未命中改写规则的 passthrough 命令保留原 argv。
    """
    idx, sub = _git_subcmd(list(argv))
    if idx < 0:
        return GitCommandMap(kind=_KIND_WORKTREE, argv=list(argv), rewritable=False)
    cmd = list(argv)

    if sub == "show":
        return _map_show(cmd, idx, base_rev, head_rev)

    if sub == "diff":
        return _map_diff(cmd, idx, base_rev, head_rev)

    if sub == "ls-files":
        return _map_ls_files(cmd, idx, head_rev)

    if sub in _HEAD_AWARE_SUBCMDS:
        rewritten, changed = _rewrite_head_anchors(cmd, idx + 1, base_rev)
        if changed:
            return GitCommandMap(kind=_KIND_HEAD_TO_BASE, argv=rewritten)
        return GitCommandMap(kind=_KIND_REPO, argv=cmd)

    return GitCommandMap(kind=_KIND_WORKTREE, argv=cmd, rewritable=False)

    if sub in _WORKTREE_SUBCMDS:
        return GitCommandMap(kind=_KIND_WORKTREE, argv=cmd, rewritable=False)


def _map_show(cmd: list[str], idx: int, base_rev: str, head_rev: str) -> GitCommandMap:
    """git show 改写：``:p``→head 树、``HEAD:p``→base 树；裸 show=仓库态读 passthrough。"""
    rest = cmd[idx + 1 :]
    new_rest: list[str] = []
    kinds = []
    changed = False
    for tok in rest:
        if tok == ":":
            new_rest.append(tok)
            continue
        if tok.startswith(":"):
            new_rest.append(f"{head_rev}{tok}")
            kinds.append(_KIND_INDEX_TO_TREE)
            changed = True
            continue
        if tok.startswith("HEAD:"):
            new_rest.append(f"{base_rev}{tok[4:]}")
            kinds.append(_KIND_HEAD_TO_BASE)
            changed = True
            continue
        new_rest.append(tok)
        kinds.append(_KIND_REPO if tok.startswith(("-", "@")) else _KIND_TREE_SCOPE)
    if changed:
        return GitCommandMap(kind=kinds[0], argv=cmd[: idx + 1] + new_rest)
    # `git show`（裸）或 `git show <rev>`＝仓库态读，passthrough
    return GitCommandMap(kind=_KIND_TREE_SCOPE, argv=cmd)


def _map_diff(cmd: list[str], idx: int, base_rev: str, head_rev: str) -> GitCommandMap:
    """git diff 改写：--cached→两树对比；显式双 rev=仓库态读；其余=工作树直读。"""
    opts, paths = _split_pathspec(cmd, idx + 1)
    if "--cached" in opts:
        opts = [o for o in opts if o != "--cached"]
        new_argv = cmd[: idx + 1] + [base_rev, head_rev] + opts
        if paths:
            new_argv += ["--"] + paths
        return GitCommandMap(kind=_KIND_INDEX_TO_TREE, argv=new_argv)
    # 无 --cached：git diff 语义按显式 rev 个数分层——
    #   0 个 = index vs 工作树；1 个 = 该 rev vs 工作树 ⇒ 两者皆工作树直读
    #   ≥2 个 = 两棵树对比 ⇒ 合法仓库态读（锚点仍改指 base 以复现当时口径）
    positional = [t for t in opts if not t.startswith("-")]
    if len(positional) >= 2:
        rewritten, changed = _rewrite_head_anchors(cmd, idx + 1, base_rev)
        return GitCommandMap(kind=_KIND_HEAD_TO_BASE if changed else _KIND_TREE_SCOPE, argv=rewritten)
    return GitCommandMap(kind=_KIND_WORKTREE, argv=cmd)


def _map_ls_files(cmd: list[str], idx: int, head_rev: str) -> GitCommandMap:
    """git ls-files 改写：--cached→head 树 ls-tree；裸 ls-files=工作树态，视图无等价物。"""
    opts, paths = _split_pathspec(cmd, idx + 1)
    if "--cached" in opts:
        new_argv = ["git", "ls-tree", "-r", "--name-only", head_rev]
        if paths:
            new_argv += ["--"] + paths
        return GitCommandMap(kind=_KIND_INDEX_TO_TREE, argv=new_argv)
    # 不带 --cached 的 ls-files 读工作树/未跟踪态——tree 视图无等价物
    return GitCommandMap(kind=_KIND_WORKTREE, argv=cmd)


@dataclass
class ProbeEvent:
    """一次被记录的读事件。"""

    channel: str
    detail: str
    module: str = ""
    count: int = 1


class WorktreeReadProbe:
    """工作树直读探针（两条通道，见模块 docstring）。

    用法::

        view = CommitTreeView(base, head, gateway=host, probe=WorktreeReadProbe())
        with view.probe.arm(project_root="D:/ZephyrAlpha"):
            passed, detail = spec.check(view, files)
        print(view.probe.summary())
    """

    def __init__(self) -> None:
        self.git_commands: list[ProbeEvent] = []
        self.git_worktree_reads: list[ProbeEvent] = []
        self.fs_reads: list[ProbeEvent] = []
        self._seen_fs: set[tuple[str, str]] = set()
        self._armed = False
        self._inside = False

    # ── 命令通道 ──
    def record_git(self, argv: list[str], mapped: GitCommandMap) -> None:
        """记录一条经过视图的 git 命令。"""
        self.git_commands.append(ProbeEvent(kind_of(mapped), " ".join(argv)))
        if mapped.touches_worktree:
            self.git_worktree_reads.append(ProbeEvent("git-worktree", " ".join(argv)))

    # ── 进程内通道 ──
    def record_fs(self, path: str, module: str) -> None:
        """记录一次进程内工作树直读（归因到调用模块）。"""
        key = (module, path)
        if key in self._seen_fs:
            return
        self._seen_fs.add(key)
        self.fs_reads.append(ProbeEvent("fs", path, module=module))

    @property
    def view_own_fs_reads(self) -> list[ProbeEvent]:
        """视图自身触发的磁盘直读——不变式要求恒 0。"""
        return [e for e in self.fs_reads if e.module.startswith(_THIS_MODULE)]

    def summary(self) -> dict[str, Any]:
        """探针快照（供驱动器落 jsonl）。"""
        by_module: dict[str, int] = {}
        for e in self.fs_reads:
            by_module[e.module] = by_module.get(e.module, 0) + 1
        return {
            "git_commands": len(self.git_commands),
            "git_worktree_reads": len(self.git_worktree_reads),
            "git_worktree_read_samples": [e.detail for e in self.git_worktree_reads[:5]],
            "fs_reads": len(self.fs_reads),
            "fs_reads_by_module": by_module,
            "view_own_fs_reads": len(self.view_own_fs_reads),
        }

    # ── 打桩窗口 ──
    @contextmanager
    def arm(self, project_root: str | Path = "."):
        """临时替换进程内文件系统入口，记录工作树直读（仅测量期使用）。"""
        if self._armed:
            yield self
            return
        import builtins
        import pathlib

        root = os.path.normcase(os.path.realpath(str(project_root)))
        root_cased = os.path.realpath(str(project_root))
        saved: dict[str, Any] = {}
        self._armed = True

        def _maybe(path: str | Path | None) -> None:
            if self._inside or path is None:
                return
            try:
                s = os.fspath(path)
            except TypeError:
                return
            if isinstance(s, int):  # open(fd)
                return
            candidate = s if os.path.isabs(s) else os.path.join(os.getcwd(), s)
            resolved = os.path.realpath(candidate)
            nc = os.path.normcase(resolved)
            if not nc.startswith(root) or os.path.normcase(".git") in nc:
                return
            module = _caller_module()
            self._inside = True
            try:
                # 记账用**原大小写**相对路径（Windows normcase 会整条小写，
                # 报表里读不出真源文件名）
                disp = os.path.relpath(resolved, root_cased)
                self.record_fs(disp.replace("\\", "/"), module)
            finally:
                self._inside = False

        _T = TypeVar("_T")

        def _wrap(fn: Callable[..., _T]) -> Callable[..., _T]:
            def inner(*args: Any, **kwargs: Any) -> _T:
                _maybe(args[0] if args else kwargs.get("file") or kwargs.get("path"))
                return fn(*args, **kwargs)

            inner.__wrapped_probe__ = fn  # type: ignore[attr-defined]
            inner.__name__ = getattr(fn, "__name__", "wrapped")
            return inner

        targets: list[tuple[Any, str]] = [
            (builtins, "open"),
            (os.path, "exists"),
            (os.path, "isfile"),
            (os.path, "isdir"),
            (os.path, "getsize"),
            (os, "listdir"),
            (os, "scandir"),
            (os, "stat"),
        ]
        for attr in ("exists", "is_file", "is_dir", "open", "read_text", "read_bytes", "iterdir", "glob"):
            targets.append((pathlib.Path, attr))
        try:
            self._inside = True
            for holder, attr in targets:
                original = getattr(holder, attr)
                saved[f"{id(holder)}:{attr}"] = (holder, attr, original)
                setattr(holder, attr, _wrap(original))
            self._inside = False
        except Exception:  # noqa: BLE001 — 打桩失败=不测量，绝不影响被测代码
            logger.warning("WorktreeReadProbe.arm 打桩失败，探针退化为命令通道 only", exc_info=True)
        try:
            yield self
        finally:
            self._inside = True
            for holder, attr, original in saved.values():
                try:
                    setattr(holder, attr, original)
                except Exception:  # noqa: BLE001
                    logger.debug("探针还原 %s.%s 失败", holder, attr, exc_info=True)
            self._armed = False
            self._inside = False


def _caller_module(max_depth: int = 30) -> str:
    """最近非噪声调用帧的模块名（探针归因用）。"""
    try:
        frame = sys._getframe(1)
    except Exception:  # noqa: BLE001 — 无帧可用（极窄栈）
        return "<unknown>"
    for _ in range(max_depth):
        if frame is None:
            break
        name = str(frame.f_globals.get("__name__", ""))
        if name and not name.startswith(_ATTRIBUTION_SKIP_PREFIXES):
            return name
        frame = frame.f_back
    return "<stdlib-or-unknown>"


def kind_of(mapped: GitCommandMap) -> str:
    """映射结果分类标签（探针记录用）。"""
    return mapped.kind


def _default_git_runner(project_root: Path) -> Callable[[list[str], str | None], subprocess.CompletedProcess]:
    """无宿主 gateway 时的 git 执行器。

    字节口径与生产一致：stdout 以 **bytes** 取回后按网关解码链处理（生产
    ``GitCommitGateway.run_git`` 走临时文件读回 + ``_decode_gateway_output``，
    **不做** newline 翻译——视图若用 text=True 会把 CRLF 文件的 ``git show``
    内容翻译掉，导致与真门禁读到不同字节，重放基线失效）。
    """

    from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (  # noqa: PLC0415
        _decode_gateway_output,
    )
    from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: PLC0415

    def _run(argv: list[str], cwd: str | None) -> subprocess.CompletedProcess:
        proc = run_subprocess_hidden(
            argv,
            cwd=str(cwd or project_root),
            capture_output=True,
            text=False,
            timeout=30,
        )
        return subprocess.CompletedProcess(
            args=argv,
            returncode=proc.returncode,
            stdout=_decode_gateway_output(proc.stdout or b""),
            stderr=_decode_gateway_output(proc.stderr or b""),
        )

    return _run


class CommitTreeView:
    """不可变提交树视图——门禁的只读仓库态替身。

    既是 :class:`CommitTreeView` 观测 API 的持有者，也是**可直接递给 gate 的
    gateway 替身**（duck-type：``run_git`` + ``project_root`` + 未实现属性透传
    给宿主），因此 72 台门无需改动即可在重放里跑在 rev 域上。

    Args:
        base_rev: 提交前仓库态（父提交）。对应今天 ``HEAD`` / ``git show HEAD:p``。
        head_rev: 本件内容（目标提交）。对应今天的 index 版本 ``git show :p``。
        gateway: 宿主 gateway（提供 ``run_git`` 以逐字节复用生产解码/缓存口径）；
            None 时用内置执行器（口径同上，仍走网关解码链）。
        project_root: 仓库根（gate 侧 ``_norm_rel``/审计路径依赖它）。
        strict: True 时工作树直读抛 :class:`WorktreeReadBlocked`。
        probe: 探针（None 则新建）。
    """

    def __init__(
        self,
        base_rev: str,
        head_rev: str,
        *,
        gateway: object | None = None,
        project_root: str | Path | None = None,
        strict: bool = False,
        probe: WorktreeReadProbe | None = None,
        view_label: str = "own_tree",  # noqa: long-param-list  构造器协议契约（基类鸭子协议对称面）
    ) -> None:
        self.base_rev = base_rev
        self.head_rev = head_rev
        self.strict = strict
        self.probe = probe or WorktreeReadProbe()
        self.view_label = view_label
        self._host = gateway
        root = project_root or getattr(gateway, "project_root", None) or Path.cwd()
        self.project_root = Path(str(root))
        self._run = (
            (lambda argv, cwd=None: gateway.run_git(argv, cwd))
            if gateway is not None
            else _default_git_runner(self.project_root)
        )
        self._own_cache: list[str] | None = None

    # ── gateway duck-type：未知属性透传宿主（_registry / session_id 等）──
    def __getattr__(self, item: str) -> Any:
        host = self.__dict__.get("_host")
        if host is None:
            raise AttributeError(item)
        return getattr(host, item)

    # ── 底层：带映射与探针的 git 执行 ──
    def run_git(self, cmd: list[str], cwd: str | None = None) -> subprocess.CompletedProcess:
        """门禁唯一 git 入口（与 ``gateway.run_git`` 同契约）。"""
        argv = [str(c) for c in cmd]
        mapped = map_git_command(argv, self.base_rev, self.head_rev)
        self.probe.record_git(argv, mapped)
        if mapped.touches_worktree:
            if self.strict:
                raise WorktreeReadBlocked(f"CommitTreeView(strict) 拒绝工作树直读：{' '.join(argv)}")
            # 测量模式：透传真实 git（口径不变），已在探针留痕
        return self._run(mapped.argv, cwd)

    def _ok(self, cmd: list[str]) -> subprocess.CompletedProcess:
        proc = self.run_git(cmd)
        return proc

    # ── 四类观测（与 _diff_helpers 逐参对齐）──
    def read_staged_file(self, py_file: str) -> str | None:
        """本件文件内容＝``git show <head_rev>:path``（对齐 ``_read_staged_file``）。

        fail-open 口径同原实现：rc!=0 或异常 → None。
        """
        try:
            result = self.run_git(["git", "show", f"{self.head_rev}:{py_file}"])
            if result.returncode == 0:
                return result.stdout
        except Exception:  # noqa: BLE001 — 与原实现同款 broad catch（fail-open 口径不变）
            pass
        return None

    def staged_files(
        self, gate_name: str = "gate", include_renamed: bool = False, suffixes: tuple[str, ...] = (".py",)
    ) -> list[str]:
        """本件 added/modified 文件清单（对齐 ``_get_staged_py_files``）。

        ``git diff <base_rev> <head_rev> --name-only --diff-filter=AM[|AMR]``。
        fail-open：rc!=0 / 异常 → ``[]`` 并 warning（原口径逐字保留）。
        """
        filt = "--diff-filter=AMR" if include_renamed else "--diff-filter=AM"
        try:
            result = self.run_git(["git", "diff", self.base_rev, self.head_rev, "--name-only", filt])
            if result.returncode != 0:
                logger.warning("%s fail-open: git diff 失败(rc=%d)。", gate_name, result.returncode)
                return []
            return [f.replace("\\", "/") for f in result.stdout.strip().splitlines() if f and f.endswith(suffixes)]
        except Exception as e:  # noqa: BLE001 — 与原实现同款 broad catch
            logger.warning("%s fail-open: git diff 异常(%s: %s)。", gate_name, type(e).__name__, e, exc_info=True)
            return []

    def added_lines(self, py_file: str, gate_name: str = "gate") -> list[tuple[int, str]]:
        """本件 added 行（对齐 ``_get_added_lines``，含 ``--ignore-cr-at-eol``）。"""
        try:
            result = self.run_git(
                [
                    "git",
                    "diff",
                    self.base_rev,
                    self.head_rev,
                    "--unified=0",
                    "--ignore-cr-at-eol",
                    "--",
                    py_file,
                ]
            )
            if result.returncode != 0:
                return []
            return _parse_diff_with_line_numbers(result.stdout)
        except Exception as e:  # noqa: BLE001 — 与原实现同款 broad catch
            logger.warning("%s: git diff 失败 file=%s, %s", gate_name, py_file, e)
            return []

    def read_head_file(self, py_file: str) -> str | None:
        """提交前版本内容＝``git show <base_rev>:path``（对齐 ``_read_head_file``）。"""
        try:
            result = self.run_git(["git", "show", f"{self.base_rev}:{py_file}"])
            if result.returncode == 0:
                return result.stdout
        except Exception:  # noqa: BLE001 — 与原实现同款 broad catch
            pass
        return None

    def repo_state_has_file(self, py_file: str) -> bool:
        """存在性观测＝纯仓库态（``ls-tree <head>``），**无磁盘回落支路**。

        对齐 ``_repo_state_has_file`` 的主证据支路；原实现在 git 失败/查无时回落
        ``os.path.exists``——该回落正是视图不变式禁止的"口径偷换"，故本方法在
        git 故障时返回 False 并告警留痕（strict 模式抛错）。
        """
        result = self.run_git(["git", "ls-tree", "-r", "--name-only", self.head_rev, "--", py_file])
        if result.returncode != 0:
            logger.warning(
                "repo_state_has_file: git rc=%d（ls-tree %s）——无磁盘回落支路，判 False（留痕）",
                result.returncode,
                py_file,
            )
            if self.strict:
                raise WorktreeReadBlocked(f"ls-tree 失败 rc={result.returncode}: {py_file}")
            return False
        return bool(result.stdout.strip())

    # ── gateway 公共 helper 的视图版（防"绕道宿主 = 绕过视图"盲区）──
    def is_git_tracked(self, rel_path: str) -> bool:
        """``gateway.is_git_tracked`` 的视图版——**经 self.run_git** 发出。

        宿主原实现自带裸 subprocess（不经 ``gateway.run_git``），门用它就等于
        绕过视图；此处刻意改走视图通道，令探针能如实记下一条工作树直读。
        """
        result = self.run_git(["git", "ls-files", "--error-unmatch", "--", f":(icase){rel_path}"])
        return result.returncode == 0

    def _is_staged_delete(self, rel_path: str) -> bool:
        """``gateway._is_staged_delete`` 的视图版（同上，经视图通道）。"""
        if self.is_git_tracked(rel_path):
            return False
        result = self.run_git(["git", "cat-file", "-e", f"HEAD:{rel_path}"])
        return result.returncode == 0

    # ── 视图自身元数据 ──
    def own_files(self) -> list[str]:
        """本件全部改动文件（不过滤扩展名），作为 ``check_all`` 的 files 入参。"""
        if self._own_cache is None:
            result = self.run_git(["git", "diff", self.base_rev, self.head_rev, "--name-only", "--diff-filter=AMD"])
            self._own_cache = (
                [f.replace("\\", "/") for f in result.stdout.strip().splitlines() if f]
                if result.returncode == 0
                else []
            )
        return list(self._own_cache)

    def summary(self) -> dict[str, Any]:
        """视图快照（落 jsonl 用）。"""
        return {
            "view": self.view_label,
            "base_rev": self.base_rev,
            "head_rev": self.head_rev,
            "own_files": len(self.own_files()),
            **self.probe.summary(),
        }


class IndexNoiseSource:
    """外来 staged 文件的读侧接口（"模拟今天共享 index"的内容来源）。

    子类实现 ``staged_names`` / ``read`` / ``diff_text`` 三件即可；``added_lines``
    由 ``diff_text`` 派生，口径与 ``_diff_helpers._get_added_lines`` 一致。
    """

    def is_noise(self, py_file: str) -> bool:  # pragma: no cover - 接口默认
        return False

    def staged_names(self, diff_filter: str) -> list[str]:  # pragma: no cover
        return []

    def read(self, py_file: str) -> str | None:  # pragma: no cover
        return None

    def diff_text(self, py_file: str) -> str:
        """该外来文件的 ``git diff --cached --unified=0`` 原文（门禁自行解析）。"""
        return ""

    def added_lines(self, py_file: str) -> list[tuple[int, str]]:
        return _parse_diff_with_line_numbers(self.diff_text(py_file))


class RealIndexNoiseSource(IndexNoiseSource):
    """真源版噪声＝今天真实 index 里的他会话 staged 文件。

    读法与今天的门禁逐字节相同（``git show :path`` / ``git diff --cached``），
    只是这些调用**不经** rev 改写——因为它们要模拟的正是"共享 index 口径"。
    """

    def __init__(self, runner, noise_files: Iterable[str]) -> None:
        self._runner = runner
        self._files = list(noise_files)
        self._set = set(self._files)
        self._blob_cache: dict[str, str | None] = {}
        self._diff_cache: dict[str, str] = {}

    @staticmethod
    def _strip(path: str) -> str:
        return path.split("#noise")[0]

    def is_noise(self, py_file: str) -> bool:
        return py_file in self._set

    def staged_names(self, diff_filter: str) -> list[str]:
        result = self._runner(["git", "diff", "--cached", "--name-only", f"--diff-filter={diff_filter}"])
        if result.returncode != 0:
            return []
        return [f.replace("\\", "/") for f in result.stdout.strip().splitlines() if f]

    def read(self, py_file: str) -> str | None:
        key = self._strip(py_file)
        if key in self._blob_cache:
            return self._blob_cache[key]
        result = self._runner(["git", "show", ":" + key])
        content = result.stdout if result.returncode == 0 else None
        self._blob_cache[key] = content
        return content

    def diff_text(self, py_file: str) -> str:
        key = self._strip(py_file)
        cached = self._diff_cache.get(key)
        if cached is not None:
            return cached
        result = self._runner(["git", "diff", "--cached", "--unified=0", "--ignore-cr-at-eol", "--", key])
        text = result.stdout if result.returncode == 0 else ""
        self._diff_cache[key] = text
        return text


class MemoryNoiseSource(IndexNoiseSource):
    """注入版噪声＝调用方给的 ``{路径: 内容}``（红测/可控实验用）。

    不依赖本机 index（生产 index 是别会话的 WIP，测不得），使"外来文件带违规"
    这类反例可确定性复现。外来文件按"新增文件"呈现（staged A 态语义）。
    """

    def __init__(self, blobs: dict[str, str]) -> None:
        self._blobs = dict(blobs)
        self._set = set(self._blobs)

    def is_noise(self, py_file: str) -> bool:
        return py_file in self._set

    def staged_names(self, diff_filter: str) -> list[str]:
        return sorted(self._set, key=lambda s: s.encode("utf-8", "replace"))

    def read(self, py_file: str) -> str | None:
        return self._blobs.get(py_file)

    def diff_text(self, py_file: str) -> str:
        content = self._blobs.get(py_file)
        if content is None:
            return ""
        lines = content.split("\n")
        if lines and lines[-1] == "":
            lines = lines[:-1]
        body = "".join(f"+{line}\n" for line in lines)
        return (
            f"diff --git a/{py_file} b/{py_file}\n"
            f"new file mode 100644\n"
            f"--- /dev/null\n"
            f"+++ b/{py_file}\n"
            f"@@ -0,0 +1,{len(lines)} @@\n" + body
        )


class SharedIndexCommitTreeView(CommitTreeView):
    """ "模拟今天共享 index"对照视图——本件 + 外来噪声文件集。

    与 :class:`CommitTreeView` 唯一的差别：index 读取的**规模**换成"今天的真相"
    （本件 ∪ 噪声），其余口径逐字相同。用途＝量化哪些台的 verdict 会随 index
    规模漂移（S1 前必须有这份运行时证据）。噪声内容默认取**真实 index**
    （:class:`RealIndexNoiseSource`，与今天门禁逐字节同口径），红测可注入
    :class:`MemoryNoiseSource` 造确定性反例。

    Args:
        noise_files: 外来 staged 路径清单（与 ``noise_source`` 二选一）。
        noise_repeat: 噪声复制倍数（index 规模敏感性实验用；>1 时按序号加
            ``#noiseN`` 后缀，路径本身不在仓库里——只放大清单规模与逐文件
            git 调用数，内容读为空由门禁自身 fail-open 处理）。
        noise_source: 噪声内容来源（None=按 ``noise_files`` 建真实 index 源）。
    """

    def __init__(  # noqa: long-param-list  构造器协议契约（基类鸭子协议+噪声注入面）
        self,
        base_rev: str,
        head_rev: str,
        *,
        noise_files: Iterable[str] = (),
        noise_repeat: int = 1,
        noise_source: IndexNoiseSource | None = None,
        gateway: object | None = None,
        project_root: str | Path | None = None,
        probe: WorktreeReadProbe | None = None,  # noqa: long-param-list  构造器协议契约：与基类 CommitTreeView 签名对称+噪声注入面
        **_extra: Any,
    ) -> None:
        super().__init__(
            base_rev,
            head_rev,
            gateway=gateway,
            project_root=project_root,
            probe=probe,
            view_label="shared_index_sim",
        )
        paths = self._expand_noise(list(noise_files), noise_repeat)
        self.noise_files = paths
        self.noise_source = noise_source or RealIndexNoiseSource(self._raw, paths)
        self._noise_set = {p for p in paths} | set(noise_source.staged_names("AM") if noise_source else [])

    @staticmethod
    def _expand_noise(paths: list[str], repeat: int) -> list[str]:
        if repeat <= 1:
            return paths
        out: list[str] = []
        for r in range(repeat):
            for p in paths:
                out.append(p if r == 0 else f"{p}#noise{r}")
        return out

    def _raw(self, argv: list[str]) -> subprocess.CompletedProcess:
        """真实 index 读取（不改写、不经映射）——噪声的"今天口径"。"""
        return self._run(argv, None)

    def is_noise(self, py_file: str) -> bool:
        """该路径是否属于注入的外来噪声集。"""
        return py_file in self._noise_set or self.noise_source.is_noise(py_file)

    def _merged(self, own: list[str], extra: list[str]) -> list[str]:
        merged = own + [e for e in extra if e not in set(own)]
        merged.sort(key=lambda s: s.encode("utf-8", "replace"))
        return merged

    def staged_files(
        self, gate_name: str = "gate", include_renamed: bool = False, suffixes: tuple[str, ...] = (".py",)
    ) -> list[str]:
        """本件 ∪ 噪声（对齐今天 ``git diff --cached --name-only`` 的返回面）。"""
        own = super().staged_files(gate_name=gate_name, include_renamed=include_renamed, suffixes=suffixes)
        filt = "AMR" if include_renamed else "AM"
        noise = [p for p in self.noise_source.staged_names(filt) if p.endswith(suffixes)]
        return self._merged(own, noise)

    def read_staged_file(self, py_file: str) -> str | None:
        """本件走 head 树；噪声走噪声源（今天的 ``git show :path``）。"""
        if self.is_noise(py_file):
            return self.noise_source.read(py_file)
        return super().read_staged_file(py_file)

    def added_lines(self, py_file: str, gate_name: str = "gate") -> list[tuple[int, str]]:
        """本件走 base..head；噪声走噪声源（今天的 ``git diff --cached``）。"""
        if self.is_noise(py_file):
            return self.noise_source.added_lines(py_file)
        return super().added_lines(py_file, gate_name=gate_name)

    def repo_state_has_file(self, py_file: str) -> bool:
        """噪声文件按"今天 index 里有"判定存在性。"""
        if self.is_noise(py_file):
            return True
        return super().repo_state_has_file(py_file)

    def run_git(self, cmd: list[str], cwd: str | None = None) -> subprocess.CompletedProcess:
        """门禁 git 入口——index 读取按"本件 ∪ 噪声"分派，其余同基类改写。

        这里必须**逐类**接管而不是只接管清单：若 ``git show :外来路径`` 仍被基类
        改写成 ``<head_rev>:外来路径``（外来文件不在本件树里 → rc=128 → 内容
        None），门禁就会对外来文件静默 fail-open，两口径 verdict 恒等——一把
        永远量不出漂移的"恒绿尺"（本 harness 首版即踩此坑，红测当场判红）。
        """
        argv = [str(c) for c in cmd]
        idx, sub = _git_subcmd(argv)
        if idx < 0:
            return super().run_git(cmd, cwd=cwd)
        opts, paths = _split_pathspec(argv, idx + 1)

        if sub == "show":
            out = self._show_via_noise(opts, argv)
            return out if out is not None else super().run_git(cmd, cwd=cwd)

        if sub == "ls-files" and "--cached" in opts:
            return self._lsfiles_merge_noise(opts, paths, argv, cmd, cwd)

        if sub == "diff" and "--cached" in opts:
            out = self._diff_cached_via_noise(opts, paths, argv)
            return out if out is not None else super().run_git(cmd, cwd=cwd)
        return super().run_git(cmd, cwd=cwd)

    # ── 三类接管分支的 helper（自 run_git 拆出，逻辑逐字节保留）──

    def _show_via_noise(self, opts: list[str], argv: list[str]) -> subprocess.CompletedProcess | None:
        """``git show :噪声路径``→噪声源读取；非噪声返回 None 走基类改写。"""
        target = next((o for o in opts if o.startswith(":") and len(o) > 1), "")
        if target and self.is_noise(target[1:]):
            content = self.noise_source.read(target[1:])
            return subprocess.CompletedProcess(
                args=argv,
                returncode=0 if content is not None else 128,
                stdout=content or "",
                stderr="" if content is not None else "fatal: bad",
            )
        return None

    def _lsfiles_merge_noise(
        self, opts: list[str], paths: list[str], argv: list[str], cmd: list[str], cwd: str | None
    ) -> subprocess.CompletedProcess:
        """``git ls-files --cached``：基类改写结果与本件噪声清单合并。"""
        extra = [p for p in paths if self.is_noise(p)]
        result = super().run_git(cmd, cwd=cwd)
        if not extra:
            return result
        listed = [f for f in (result.stdout or "").strip().splitlines() if f]
        merged = self._merged(listed, [e for e in extra if e not in set(listed)])
        return subprocess.CompletedProcess(
            args=argv, returncode=result.returncode, stdout="\n".join(merged) + "\n", stderr=result.stderr
        )

    def _diff_cached_via_noise(
        self, opts: list[str], paths: list[str], argv: list[str]
    ) -> subprocess.CompletedProcess | None:
        """``git diff --cached``：本件∪噪声名单合并 / 单噪声路径 diff 文本；其余 None 走基类。"""
        if not paths and "--name-only" in opts:
            filt = next((o.split("=", 1)[1] for o in opts if o.startswith("--diff-filter")), "AM")
            own = self._own_names(f"--diff-filter={filt}")
            noise = self.noise_source.staged_names(filt)
            merged = self._merged(own, noise)
            result = self._raw(argv)
            return subprocess.CompletedProcess(
                args=argv,
                returncode=result.returncode,
                stdout="\n".join(merged) + ("\n" if merged else ""),
                stderr=result.stderr,
            )
        if len(paths) == 1 and self.is_noise(paths[0]):
            if "--name-only" in opts or "--name-status" in opts:
                body = paths[0] + "\n"
            else:
                body = self.noise_source.diff_text(paths[0])
            return subprocess.CompletedProcess(args=argv, returncode=0, stdout=body, stderr="")
        return None

    def _own_names(self, diff_filter: str) -> list[str]:
        result = self._run(["git", "diff", self.base_rev, self.head_rev, "--name-only", diff_filter], None)
        if result.returncode != 0:
            return []
        return [f.replace("\\", "/") for f in result.stdout.strip().splitlines() if f]
