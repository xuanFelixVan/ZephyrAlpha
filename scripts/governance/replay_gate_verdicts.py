# [BLUEPRINT] MOD-GATE_ENGINE | scripts/governance/replay_gate_verdicts.py | §0.1
# [MODULE] scripts.governance.replay_gate_verdicts
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._tree_view；zephyr.gov_enforcement.rule_bridge.commit_gate_registry（GateSpec / files_trigger 匹配真源，只 import 不改）；zephyr.gov_enforcement.rule_bridge.gate_auto_registrar（名册相对路径真源）；zephyr.shared.utils.time_utils（时间戳真源）
# [CONSUMERS] 人工/CI 按需触发（提交链提速战役 S1 发布前绊线）；tests/governance/test_gate_replay_harness.py
# [STARTUP] manual
# noqa: m11-perm-manual-legitimate  M11豁免: replay 安全网=人工/CI 按需触发 CLI（CONSUMERS 在案），非周期触发无订阅语义
# [MATURITY] prototype
# [INVARIANTS] 只测量不改判——本脚本永不修改门禁判据/阈值/口径，也不写任何生产路径；每条 gate 结果双口径对跑（own_tree vs shared_index_sim），差异只统计不修复；写盘全部经 WriteSandbox 收敛到 --out-dir（生产 .runtime 零写入）；fail-open 的 gate 异常按 error 记录不抛穿；per-gate 读缓存窗口清空＝保守口径（放大而非隐藏 index 规模成本）
# [MODIFY-GUARD] CLI: --since N --gates id,id|--all --noise real|none --noise-repeat K --probe --selfcheck --max-seconds
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单 gate 异常→verdict=error 记录后继续；git 不可用→退出码 2（不产出半成品基线）；名册缺失→退出码 2
# [TESTS] tests/governance/test_gate_replay_harness.py
# [TTL] permanent
"""replay_gate_verdicts.py — 门禁 verdict 重放安全网驱动器 + 逐台比较器

一句话
------
把最近 N 笔提交"重跑一遍门禁"，同一笔同一台门跑两种读口径：

* ``own_tree``＝:class:`CommitTreeView`（只看本件，base=C^ / head=C，纯提交树）
* ``shared_index_sim``＝:class:`SharedIndexCommitTreeView`（本件 ∪ 外来噪声文件集，
  复刻今天门禁从共享暂存区看到的规模）

两者 verdict 必须逐台全等，否则这台门的判定**随 index 规模漂移**——这正是
S1（门禁改指不可变提交树视图）发布前必须清零的绊线，也是"15 台读共享 index
无 own-scope 收窄"的运行时证据。

产物
----
- ``<out-dir>/verdicts.jsonl``——每台每笔每口径一行
  ``{commit, gate_id, view, verdict, hits, ms, detail_sha, ...}``
- ``<out-dir>/verdict_divergence.yaml``——逐台差异聚合（verdict 翻转/命中数漂移/耗时比）
- ``<out-dir>/run_summary.json``——本次运行覆盖台数、error 台、probe 结论

用法::

    python scripts/governance/replay_gate_verdicts.py --since 20 --all
    python scripts/governance/replay_gate_verdicts.py --since 5 \\
        --gates DATETIME-NOW-FORBIDDEN,BARE-SUBPROCESS --noise real
    python scripts/governance/replay_gate_verdicts.py --since 30 --selfcheck

设计真源＝docs/_working/commit_speedup_campaign/50_replay_baseline/R1_design.md
"""

from __future__ import annotations

import argparse
import builtins
import contextlib
import hashlib
import importlib
import io
import json
import logging
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_REPO_ROOT), str(_REPO_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from zephyr.gov_enforcement.commit_gates._tree_view import (  # noqa: E402
    CommitTreeView,
    SharedIndexCommitTreeView,
    WorktreeReadProbe,
)
from zephyr.gov_enforcement.rule_bridge import gate_auto_registrar as _gar  # noqa: E402
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (  # noqa: E402
    _files_trigger_hit,
)

logger = logging.getLogger("replay_gate_verdicts")

__all__ = ["ReplayHost", "load_gate_specs", "main"]

# 命中数启发式：detail 里的"违规行"数（path:line / 项目符号行）——口径仅作
# 跨视图对比的稳定标量，不代表门禁自身的计数语义。
_HIT_LINE_RE = re.compile(
    r"(?m)^\s*(?:[-*•]|\d+[.)])?\s*\S*\.(?:py|yaml|yml|md|json|jsonl|sql|ps1|toml|ini|cfg|csv|tsx|ts|sh)\b"
)
_DEFAULT_OUT_REL = ".runtime/audit/replay_baseline"
_PROD_RUNTIME = "/.runtime/"


# ══════════════════════════════════════════════════════════════════════════
# 宿主（duck-typed gateway）
# ══════════════════════════════════════════════════════════════════════════
class ReplayHost:
    """门禁所需的最小 gateway 面（``run_git`` + ``project_root`` + claim 空态）。

    与生产 ``GitCommitGateway.run_git`` 的**字节口径一致**：stdout 以 bytes 取回后
    走同一条解码链（``_decode_gateway_output``），不做 newline 翻译——否则 CRLF
    文件的 ``git show`` 内容与真门禁读到的不同，重放基线即失去意义。
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root)
        self._registry = None  # 重放无活跃 session → own_scope 退化为 files-only
        self._claim_snapshots: dict[str, dict[str, str]] = {}
        self._claim_heads: dict[str, str] = {}
        self._claim_snapshots_dir = self.project_root / ".runtime" / "claim_snapshots"
        self.git_calls = 0
        self._cache: dict[tuple, subprocess.CompletedProcess] | None = None

    # 生产链内 A1 读缓存：重放刻意**每台门独立开窗**（见 INVARIANTS：保守口径）
    def open_chain(self) -> None:
        self._cache = {}

    def close_chain(self) -> None:
        self._cache = None

    def run_git(self, cmd: list[str], cwd: str | None = None) -> subprocess.CompletedProcess:
        argv = [str(c) for c in cmd]
        if self._cache is not None:
            hit = self._cache.get((tuple(argv), cwd))
            if hit is not None:
                return hit
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (  # noqa: PLC0415
            _decode_gateway_output,
        )
        from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: PLC0415

        proc = run_subprocess_hidden(
            argv, cwd=str(cwd or self.project_root), capture_output=True, text=False, timeout=60
        )
        result = subprocess.CompletedProcess(
            args=argv,
            returncode=proc.returncode,
            stdout=_decode_gateway_output(proc.stdout or b""),
            stderr=_decode_gateway_output(proc.stderr or b""),
        )
        self.git_calls += 1
        if self._cache is not None:
            self._cache[(tuple(argv), cwd)] = result
        return result

    def is_git_tracked(self, rel_path: str) -> bool:
        chk = self.run_git(["git", "ls-files", "--error-unmatch", "--", f":(icase){rel_path}"])
        return chk.returncode == 0

    def _is_git_tracked(self, rel_path: str) -> bool:
        return self.is_git_tracked(rel_path)

    def _is_staged_delete(self, rel_path: str) -> bool:
        if self.is_git_tracked(rel_path):
            return False
        chk = self.run_git(["git", "cat-file", "-e", f"HEAD:{rel_path}"])
        return chk.returncode == 0


# ══════════════════════════════════════════════════════════════════════════
# 写盘沙盒（重放期间生产 .runtime 零写入）
# ══════════════════════════════════════════════════════════════════════════
class WriteSandbox:
    """把门禁检查里的**写**动作改道到沙盒目录，并留痕。

    背景：部分门禁 fail 时向 ``.runtime/gate_audit/*.jsonl``、``.runtime/state``
    追加审计/状态（``_audit_foreign_staged``/``protected_paths_gate``/
    ``reconciler_health_gate`` 等）。重放历史提交若照写，会把"关于上周三那次提交
    的伪造外来 staged 告警"混进生产遥测——污染治理信号。故写路径命中
    ``<repo>/.runtime/`` 一律改道 ``<out-dir>/sandbox/<相对路径>``。
    """

    def __init__(self, repo_root: Path, sandbox_root: Path) -> None:
        self.repo_nc = os.path.normcase(str(repo_root.resolve())) + os.sep
        self.sandbox_root = Path(sandbox_root)
        self.events: list[dict[str, str]] = []
        self._active = False
        self._inside = False

    def _redirect(self, path: Any) -> Any:
        if not self._active or self._inside or path is None:
            return path
        if isinstance(path, int):
            return path
        try:
            s = os.fspath(path)
        except TypeError:
            return path
        if isinstance(s, bytes):
            try:
                s = s.decode("utf-8", "replace")
            except Exception:  # noqa: BLE001
                return path
        cand = s if os.path.isabs(s) else os.path.join(os.getcwd(), s)
        nc = os.path.normcase(os.path.abspath(cand))
        if not nc.startswith(self.repo_nc):
            return path
        rel = nc[len(self.repo_nc) :].replace("\\", "/")
        if _PROD_RUNTIME + "" not in "/" + rel:
            return path
        target = self.sandbox_root / rel
        self._inside = True
        try:
            self.events.append({"from": rel, "to": str(target).replace("\\", "/")})
            target.parent.mkdir(parents=True, exist_ok=True)
        finally:
            self._inside = False
        # 类型保持：pathlib.Path 未绑定方法经 _wrap(arg_index=0) 时 0 号位是 self——
        # 返回 str 会把 self 打断成 str（'str' has no attribute 'open'）。
        # 输入 Path ⇒ 返回 Path；其余返回 str（open/os.makedirs 两种签名都吃 str）。
        if isinstance(path, Path):
            return target
        return str(target)

    @contextlib.contextmanager
    def __call__(self) -> WriteSandbox:
        if self._active:
            yield self
            return
        import pathlib

        saved: list[tuple[Any, str, Any]] = []
        targets = [
            (builtins, "open"),
            (io, "open"),
            (os, "makedirs"),
            (os, "mkdir"),
            (pathlib.Path, "open"),
            (pathlib.Path, "write_text"),
            (pathlib.Path, "write_bytes"),
            (pathlib.Path, "mkdir"),
        ]

        def _wrap(fn: Any, arg_index: int) -> Any:
            def inner(*args: Any, **kwargs: Any) -> Any:
                if args and len(args) > arg_index:
                    head = list(args)
                    head[arg_index] = self._redirect(head[arg_index])
                    return fn(*head, **kwargs)
                return fn(*args, **kwargs)

            inner.__name__ = getattr(fn, "__name__", "sandboxed")
            return inner

        self._active = True
        try:
            for holder, attr in targets:
                original = getattr(holder, attr)
                saved.append((holder, attr, original))
                setattr(holder, attr, _wrap(original, 0))
            yield self
        finally:
            for holder, attr, original in saved:
                try:
                    setattr(holder, attr, original)
                except Exception:  # noqa: BLE001
                    logger.debug("WriteSandbox 还原 %s 失败", attr, exc_info=True)
            self._active = False


# ══════════════════════════════════════════════════════════════════════════
# 门禁装载（容错逐台——一台装载失败不拖垮整轮，与生产 fail-closed 口径有意不同）
# ══════════════════════════════════════════════════════════════════════════
@dataclass
class LoadedGate:
    gate_id: str
    spec: Any
    module: str
    priority: int = 100


def load_gate_specs(
    project_root: Path, wanted: set[str] | None = None
) -> tuple[list[LoadedGate], list[dict[str, str]]]:
    """按名册装载门禁（只 import + 调工厂，不经 CommitGateRegistry 的 priority 唯一性闸）。

    Args:
        project_root: 仓库根（名册相对路径真源来自 gate_auto_registrar）。
        wanted: 需装载的 gate_id 集合；None=全部 enabled。

    Returns:
        ``(装载成功的台列表, 装载失败台账)``——失败逐台记 ``{gate_id, error}``。
    """
    roster_path = project_root / _gar.REGISTRY_REL_PATH
    if not roster_path.exists():
        raise FileNotFoundError(f"gate roster missing: {roster_path}")
    import yaml

    data = yaml.safe_load(roster_path.read_text(encoding="utf-8")) or {}
    entries = [e for e in (data.get("gates") or []) if isinstance(e, dict) and e.get("enabled", True)]
    loaded: list[LoadedGate] = []
    failures: list[dict[str, str]] = []
    for entry in entries:
        gid = str(entry.get("gate_id", ""))
        if wanted is not None and gid not in wanted:
            continue
        mod_path = str(entry.get("module_path", ""))
        factory_name = str(entry.get("factory_function", ""))
        try:
            module = importlib.import_module(mod_path)
            spec = getattr(module, factory_name)()
            ft = entry.get("files_trigger")
            if ft:
                spec.files_trigger = tuple(ft) if isinstance(ft, list) else (str(ft),)
            loaded.append(
                LoadedGate(gate_id=gid, spec=spec, module=mod_path, priority=int(getattr(spec, "priority", 100)))
            )
        except Exception as e:  # noqa: BLE001 — 逐台收集（测量面容错，与生产 fail-closed 反向）
            failures.append({"gate_id": gid, "error": f"{type(e).__name__}: {e}"})
    loaded.sort(key=lambda g: g.priority)
    return loaded, failures


# ══════════════════════════════════════════════════════════════════════════
# 提交枚举与噪声集
# ══════════════════════════════════════════════════════════════════════════
def recent_commits(host: ReplayHost, since: int, ref: str = "HEAD") -> list[tuple[str, str, str]]:
    """最近 N 笔非 merge 提交 → ``[(sha, parent_sha, session_id_from_trailer)]``。"""
    result = host.run_git(["git", "log", "--no-merges", "-n", str(since), "--format=%H%x09%P%x09%B%x1e", ref])
    if result.returncode != 0:
        raise RuntimeError(f"git log 失败 rc={result.returncode}: {result.stderr[:200]}")
    out: list[tuple[str, str, str]] = []
    for chunk in result.stdout.split("\x1e"):
        chunk = chunk.strip("\r\n")
        if not chunk.strip():
            continue
        parts = chunk.split("\t", 2)
        if len(parts) < 2:
            continue
        sha, parents = parts[0].strip(), parts[1].split()
        body = parts[2] if len(parts) > 2 else ""
        sid = ""
        m = re.search(r"\[GW:([^\s\]]+)", body)
        if m:
            sid = m.group(1)
        if parents:
            out.append((sha, parents[0], sid))
    return out


def shared_index_files(host: ReplayHost) -> list[str]:
    """今天真实共享 index 的 staged AM 清单（噪声集真源=盘面实况，非编造）。"""
    result = host.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
    if result.returncode != 0:
        return []
    return [f.replace("\\", "/") for f in result.stdout.strip().splitlines() if f]


# ══════════════════════════════════════════════════════════════════════════
# 逐台执行
# ══════════════════════════════════════════════════════════════════════════
def _sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8", "replace")).hexdigest()[:16]


def _hits(passed: bool, detail: str) -> int:
    if passed or not detail:
        return 0
    n = len(_HIT_LINE_RE.findall(detail))
    return n if n else 1


def run_gate_once(
    gate: LoadedGate,
    view: CommitTreeView,
    files: list[str],
    host: ReplayHost,
    session_id: str,
    *,
    sandbox: WriteSandbox,
    use_probe: bool,
) -> dict[str, Any]:
    """跑一台门一次，返回记录（verdict/hits/ms/detail_sha/probe）。"""
    spec = gate.spec
    rec: dict[str, Any] = {
        "gate_id": gate.gate_id,
        "view": view.view_label,
        "verdict": "error",
        "hits": 0,
        "ms": 0.0,
        "detail_sha": "",
        "detail_head": "",
        "note": "",
    }
    if spec.files_trigger and not _files_trigger_hit(spec.files_trigger, files):
        rec.update(verdict="skip", note="files_trigger 未命中（与生产 check_all 同口径）")
        return rec
    probe = WorktreeReadProbe() if use_probe else view.probe
    view.probe = probe
    t0 = time.monotonic()
    host.open_chain()
    try:
        with sandbox():
            passed, detail = spec.check(view, list(files), session_id=session_id or None)
        rec["verdict"] = "pass" if passed else "fail"
        rec["detail_sha"] = _sha(str(detail))
        rec["hits"] = _hits(bool(passed), str(detail))
        rec["detail_head"] = str(detail).replace("\r\n", "\n")[:400]
    except Exception as e:  # noqa: BLE001 — 重放面逐台隔离，异常台记 error 不拖垮轮次
        rec["verdict"] = "error"
        rec["note"] = f"{type(e).__name__}: {e}"[:300]
    finally:
        host.close_chain()
        view.probe = probe
    rec["ms"] = round((time.monotonic() - t0) * 1000, 1)
    rec["git_calls"] = host.git_calls
    if use_probe:
        summary = probe.summary()
        rec["git_worktree_reads"] = summary["git_worktree_reads"]
        rec["git_worktree_read_samples"] = summary["git_worktree_read_samples"]
        rec["fs_reads"] = summary["fs_reads"]
        rec["fs_reads_by_module"] = summary["fs_reads_by_module"]
    return rec


# ══════════════════════════════════════════════════════════════════════════
# 比较器：own_tree vs shared_index_sim 逐台 verdict
# ══════════════════════════════════════════════════════════════════════════
@dataclass
class DivergenceTracker:
    """逐台聚合 A/B 两口径的差异（verdict 翻转＝硬证据；hits/detail 漂移＝次级）。"""

    per_gate: dict[str, dict[str, Any]] = field(default_factory=dict)
    examples: list[dict[str, Any]] = field(default_factory=list)

    def add(self, commit: str, a: dict[str, Any], b: dict[str, Any]) -> bool:
        gid = a["gate_id"]
        st = self.per_gate.setdefault(
            gid,
            {
                "commits": 0,
                "verdict_diverged": 0,
                "hits_diverged": 0,
                "detail_diverged": 0,
                "ms_own_total": 0.0,
                "ms_shared_total": 0.0,
                "verdict_pairs": {},
            },
        )
        st["commits"] += 1
        st["ms_own_total"] += float(a["ms"])
        st["ms_shared_total"] += float(b["ms"])
        pair = (a["verdict"], b["verdict"])
        if pair != ("skip", "skip"):
            st["verdict_pairs"][f"{pair[0]}->{pair[1]}"] = st["verdict_pairs"].get(f"{pair[0]}->{pair[1]} ", 0) + 1
        v_div = a["verdict"] != b["verdict"]
        h_div = a["hits"] != b["hits"]
        d_div = a["detail_sha"] != b["detail_sha"] and "skip" not in pair
        st["verdict_diverged"] += int(v_div)
        st["hits_diverged"] += int(h_div)
        st["detail_diverged"] += int(d_div)
        if v_div or h_div:
            self.examples.append(
                {
                    "commit": commit[:10],
                    "gate_id": gid,
                    "own_tree": {"verdict": a["verdict"], "hits": a["hits"], "ms": a["ms"]},
                    "shared_index_sim": {"verdict": b["verdict"], "hits": b["hits"], "ms": b["ms"]},
                    "own_detail_head": a.get("detail_head", "")[:200],
                    "shared_detail_head": b.get("detail_head", "")[:200],
                }
            )
        return v_div or h_div

    def to_yaml_doc(self, meta: dict[str, Any]) -> dict[str, Any]:
        gates: dict[str, Any] = {}
        for gid, st in sorted(self.per_gate.items()):
            gates[gid] = {
                "commits_compared": st["commits"],
                "verdict_diverged": st["verdict_diverged"],
                "hits_diverged": st["hits_diverged"],
                "detail_diverged": st["detail_diverged"],
                "mean_ms_own_tree": round(st["ms_own_total"] / max(1, st["commits"]), 1),
                "mean_ms_shared_index": round(st["ms_shared_total"] / max(1, st["commits"]), 1),
                "verdict_pairs": st["verdict_pairs"],
                "verdict_drifts_with_index_size": bool(st["verdict_diverged"] or st["hits_diverged"]),
            }
        return {"meta": meta, "gates": gates, "examples": self.examples[:200]}


# ══════════════════════════════════════════════════════════════════════════
# 逐字节自检（CommitTreeView 复现 == 真实提交 diff）
# ══════════════════════════════════════════════════════════════════════════
def selfcheck_commit(host: ReplayHost, sha: str, parent: str) -> dict[str, Any]:
    """校验视图四观测与 git 真值逐字节一致。

    真值口径：非 merge 提交的 ``git show <sha> -- <path>`` 恒等于
    ``git diff <parent> <sha> -- <path>``（本件当时的 diff）；``git show <rev>:path``
    是内容真值。返回不一致计数与样例。
    """
    view = CommitTreeView(parent, sha, gateway=host)
    own = view.own_files()
    bad_content = 0
    bad_added = 0
    checked = 0
    samples: list[str] = []
    for p in own:
        checked += 1
        want = host.run_git(["git", "show", f"{sha}:{p}"])
        got = view.read_staged_file(p)
        if want.returncode == 0 and (got or "") != want.stdout:
            bad_content += 1
            samples.append(f"content:{p}")
        wanth = host.run_git(["git", "show", f"{parent}:{p}"])
        goth = view.read_head_file(p)
        if wanth.returncode == 0 and (goth or "") != wanth.stdout:
            bad_content += 1
            samples.append(f"head:{p}")
        wp = host.run_git(["git", "diff", parent, sha, "--unified=0", "--ignore-cr-at-eol", "--", p])
        from zephyr.gov_enforcement.commit_gates._diff_helpers import (  # noqa: PLC0415
            _parse_diff_with_line_numbers,
        )

        if wp.returncode == 0 and view.added_lines(p) != _parse_diff_with_line_numbers(wp.stdout):
            bad_added += 1
            samples.append(f"added:{p}")
    return {
        "commit": sha[:10],
        "files_checked": checked,
        "content_mismatch": bad_content,
        "added_lines_mismatch": bad_added,
        "samples": samples[:5],
        "view_worktree_reads": view.probe.git_worktree_reads,
    }


# ══════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════
def _parse_wanted(raw: str | None, take_all: bool) -> set[str] | None:
    if take_all or not raw:
        return None
    return {g.strip() for g in raw.split(",") if g.strip()}


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="门禁 verdict 重放安全网（只读观测基建）")
    ap.add_argument("--since", type=int, default=20, help="最近 N 笔非 merge 提交（默认 20）")
    ap.add_argument("--gates", default="", help="逗号分隔 gate_id；缺省配合 --all 跑全册")
    ap.add_argument("--all", action="store_true", help="装载名册全部 enabled 门禁")
    ap.add_argument("--ref", default="HEAD", help="提交枚举起点（默认 HEAD=dev）")
    ap.add_argument("--repo", default=str(_REPO_ROOT), help="仓库根")
    ap.add_argument("--out-dir", default="", help=f"输出目录（默认 {os.environ.get('CSX_OUT', _DEFAULT_OUT_REL)}）")
    ap.add_argument("--noise", choices=("real", "none"), default="real", help="外来噪声集来源：real=今天真实 index")
    ap.add_argument("--noise-repeat", type=int, default=1, help="噪声规模放大倍数（index 规模敏感性实验）")
    ap.add_argument("--noise-cap", type=int, default=0, help="噪声文件数上限（0=不限）")
    ap.add_argument("--probe", action="store_true", help="own_tree 口径加挂工作树直读探针（慢，单独跑）")
    ap.add_argument("--selfcheck", action="store_true", help="只做逐字节复现自检，不跑门禁")
    ap.add_argument("--max-commits", type=int, default=0, help="本次最多处理多少笔（0=全部）")
    ap.add_argument("--max-seconds", type=float, default=0.0, help="全局时间预算（0=不限），超预算停止并如实报告覆盖度")
    ap.add_argument("--quiet", action="store_true")
    return ap


def _check_git_readable(host: ReplayHost) -> bool:
    """git 仓库可读性自证（不可读=退出码 2，不产半成品基线）。"""
    try:
        head_check = host.run_git(["git", "rev-parse", "--git-dir"])
        if head_check.returncode != 0:
            logger.error("git 仓库不可读：%s", head_check.stderr[:200])
            return False
    except Exception as e:  # noqa: BLE001
        logger.error("git 不可用：%s", e)
        return False
    return True


def _run_selfcheck(host: ReplayHost, commits: list, run_meta: dict[str, Any], out_dir: Path) -> int:
    """selfcheck 模式：字节级自比对（内容/added 行双尺），mismatch≠0 即退出码 1。"""
    rows = [selfcheck_commit(host, sha, parent) for sha, parent, _sid in commits]
    mism = sum(r["content_mismatch"] + r["added_lines_mismatch"] for r in rows)
    summary = {
        **run_meta,
        "mode": "selfcheck",
        "commits_checked": len(rows),
        "files_checked": sum(r["files_checked"] for r in rows),
        "byte_mismatch_total": mism,
        "worktree_reads_from_view": sum(len(r["view_worktree_reads"]) for r in rows),
        "rows": rows[:50],
    }
    (out_dir / "selfcheck.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"SELFCHECK commits={len(rows)} files={summary['files_checked']} "
        f"byte_mismatch={mism} view_worktree_reads={summary['worktree_reads_from_view']}"
    )
    return 0 if mism == 0 else 1


@dataclass
class RunCtx:
    """单轮重放的可变运行态（自 _replay_commit_on_gates 参数收敛，避免超长参数表）。"""

    sink: Any
    per_gate_records: dict[str, dict[str, Any]]
    tracker: DivergenceTracker
    sandbox: WriteSandbox
    use_probe: bool
    noise_repeat: int
    host: ReplayHost


def _own_and_noise(host: ReplayHost, parent: str, sha: str, noise_all: list[str]) -> tuple[list[str], list[str]]:
    """单 commit 的 own 文件面与噪声面（噪声剔除 own 交集）。"""
    own = CommitTreeView(parent, sha, gateway=host).own_files()
    noise = [f for f in noise_all if f not in set(own)]
    return own, noise


def _replay_commit_on_gates(
    *,
    sha: str,
    parent: str,
    sid: str,
    own: list[str],
    noise: list[str],
    gates: list,
    ctx: RunCtx,
) -> None:
    """单 commit × 全部门 × 双视图跑门+记账（自 main 主循环拆出，逻辑逐字节保留）。"""
    host = ctx.host
    sink = ctx.sink
    sandbox = ctx.sandbox
    per_gate_records = ctx.per_gate_records
    tracker = ctx.tracker
    use_probe = ctx.use_probe
    noise_repeat = ctx.noise_repeat
    own_py = [f for f in own if f.endswith(".py")]
    for gate in gates:
        va = CommitTreeView(
            parent,
            sha,
            gateway=host,
            view_label="own_tree",
            probe=WorktreeReadProbe(),
        )
        vb = SharedIndexCommitTreeView(
            parent,
            sha,
            gateway=host,
            noise_files=noise,
            noise_repeat=noise_repeat,
            probe=WorktreeReadProbe(),
        )
        rec_a = run_gate_once(gate, va, own, host, sid, sandbox=sandbox, use_probe=use_probe)
        rec_b = run_gate_once(gate, vb, own, host, sid, sandbox=sandbox, use_probe=False)
        for rec, view in ((rec_a, va), (rec_b, vb)):
            rec.update(
                {
                    "commit": sha,
                    "commit_parent": parent,
                    "session_id": sid,
                    "own_files": len(own),
                    "own_py": len(own_py),
                    "noise_files": len(noise) * max(1, noise_repeat) if rec["view"] == "shared_index_sim" else 0,
                    "view_summary": view.summary(),
                }
            )
            sink.write(json.dumps(rec, ensure_ascii=False) + "\n")
            agg = per_gate_records.setdefault(
                rec["gate_id"],
                {"own_ms": 0.0, "shared_ms": 0.0, "own_git": 0, "shared_git": 0, "n": 0, "probe": {}},
            )
            agg["n"] += 1
            key = "own_ms" if rec["view"] == "own_tree" else "shared_ms"
            gkey = "own_git" if rec["view"] == "own_tree" else "shared_git"
            agg[key] += float(rec["ms"])
            agg[gkey] += int(rec.get("git_calls", 0))
            if rec["view"] == "own_tree" and "fs_reads_by_module" in rec:
                agg["probe"] = {
                    "git_worktree_reads": rec.get("git_worktree_reads", 0),
                    "git_worktree_read_samples": rec.get("git_worktree_read_samples", []),
                    "fs_reads": rec.get("fs_reads", 0),
                    "fs_reads_by_module": rec.get("fs_reads_by_module", {}),
                }
        tracker.add(sha, rec_a, rec_b)


def _write_replay_report(
    *,
    tracker: DivergenceTracker,
    per_gate_records: dict[str, dict[str, Any]],
    run_meta: dict[str, Any],
    out_dir: Path,
    processed: int,
    gates: list,
    budget_t0: float,
) -> int:
    """重放报告落盘+漂移播报（自 main 拆出，逻辑逐字节保留）。"""
    merged_ms = {
        gid: {
            "commits": agg["n"] // 2,
            "mean_ms_own_tree": round(agg["own_ms"] / max(1, agg["n"] // 2), 1),
            "mean_ms_shared_index": round(agg["shared_ms"] / max(1, agg["n"] // 2), 1),
            "cost_ratio": round(agg["shared_ms"] / agg["own_ms"], 2) if agg["own_ms"] > 0 else None,
            "probe": agg["probe"],
        }
        for gid, agg in per_gate_records.items()
    }
    run_meta.update(
        {
            "commits_processed": processed,
            "elapsed_s": round(time.monotonic() - budget_t0, 1),
            "gates_covered": sorted(per_gate_records),
            "verdict_lines": sum(a["n"] for a in per_gate_records.values()),
        }
    )
    doc = tracker.to_yaml_doc({**run_meta, "per_gate_timing": merged_ms})
    _dump_yaml(out_dir / "verdict_divergence.yaml", doc)
    (out_dir / "run_summary.json").write_text(json.dumps(run_meta, ensure_ascii=False, indent=2), encoding="utf-8")

    drift = sorted((gid for gid, st in tracker.per_gate.items() if st["verdict_diverged"] or st["hits_diverged"]))
    print(
        f"REPLAY done commits={processed} gates={len(gates)} verdict_lines={run_meta['verdict_lines']} "
        f"verdict_drift_gates={len(drift)} -> {out_dir}"
    )
    if drift:
        print("DRIFT(台数漂移=verdict/hits 随 index 规模变化): " + ", ".join(drift[:40]))
    return 0


def main(argv: list[str] | None = None) -> int:
    from zephyr.shared.utils.time_utils import now_utc  # noqa: PLC0415

    args = build_arg_parser().parse_args(argv)
    if not args.quiet:
        logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
    root = Path(args.repo).resolve()
    out_dir = Path(args.out_dir) if args.out_dir else Path(os.environ.get("CSX_OUT", _DEFAULT_OUT_REL))
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    host = ReplayHost(root)

    if not _check_git_readable(host):
        return 2

    commits = recent_commits(host, args.since, args.ref)
    if args.max_commits:
        commits = commits[: args.max_commits]
    if not commits:
        logger.error("未取到任何提交（--since/%s --ref/%s 是否过窄？）", args.since, args.ref)
        return 2

    run_meta: dict[str, Any] = {
        "started_at": now_utc().isoformat(),
        "repo": str(root),
        "ref": args.ref,
        "commits_requested": args.since,
        "commits_taken": len(commits),
        "views": ["own_tree", "shared_index_sim"],
        "probe": bool(args.probe),
        "noise_repeat": args.noise_repeat,
    }

    if args.selfcheck:
        return _run_selfcheck(host, commits, run_meta, out_dir)

    wanted = _parse_wanted(args.gates, args.all)
    gates, failures = load_gate_specs(root, wanted)
    if not gates:
        logger.error("零台门禁装载成功（wanted=%s failures=%s）", wanted, failures[:5])
        return 2
    noise_all = shared_index_files(host) if args.noise == "real" else []
    if args.noise_cap:
        noise_all = noise_all[: args.noise_cap]
    run_meta.update(
        {
            "gates_loaded": len(gates),
            "gate_load_failures": failures,
            "noise_source": args.noise,
            "noise_files": len(noise_all),
            "shared_index_files_today": len(noise_all),
        }
    )

    verdicts_path = out_dir / "verdicts.jsonl"
    tracker = DivergenceTracker()
    per_gate_records: dict[str, dict[str, Any]] = {}
    sandbox = WriteSandbox(root, out_dir / "sandbox")
    budget_t0 = time.monotonic()
    processed = 0
    with verdicts_path.open("a", encoding="utf-8") as sink:
        for sha, parent, sid in commits:
            if args.max_seconds and (time.monotonic() - budget_t0) > args.max_seconds:
                run_meta["budget_stopped_at"] = sha
                break
            own, noise = _own_and_noise(host, parent, sha, noise_all)
            ctx = RunCtx(
                host=host,
                sink=sink,
                per_gate_records=per_gate_records,
                tracker=tracker,
                sandbox=sandbox,
                use_probe=args.probe,
                noise_repeat=args.noise_repeat,
            )
            _replay_commit_on_gates(
                # 包9 修复（st-commitspeed-tbl-20260924）：main 调用点残留 host= 关键字，
                # 与收敛后签名 (*, sha, parent, sid, own, noise, gates, ctx) 不匹配
                # （host 已入 RunCtx）——首笔即 TypeError，重放安全网整网哑火。
                sha=sha,
                parent=parent,
                sid=sid,
                own=own,
                noise=noise,
                gates=gates,
                ctx=ctx,
            )
            processed += 1
            print(
                f"[{processed}/{len(commits)}] {sha[:10]} own={len(own)} noise={len(noise)} "
                f"gates={len(gates)} elapsed={round(time.monotonic() - budget_t0, 1)}s",
                flush=True,
            )

    run_meta["sandbox_writes"] = len(sandbox.events)
    return _write_replay_report(
        tracker=tracker,
        per_gate_records=per_gate_records,
        run_meta=run_meta,
        out_dir=out_dir,
        processed=processed,
        gates=gates,
        budget_t0=budget_t0,
    )


def _dump_yaml(path: Path, doc: dict[str, Any]) -> None:
    """落 YAML（stdlib 手写序列化，避免 yaml 依赖版本差异 + 键序不稳定）。"""
    import yaml

    text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=110)
    path.write_text("# 生成器产出（scripts/governance/replay_gate_verdicts.py）——勿手工维护\n" + text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
