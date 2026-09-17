# [BLUEPRINT] MOD-algo_flow_reverse_orphan | scripts/governance/d8_doc_sync/algo_flow_reverse_orphan_reconciler.py | §
# [MODULE] scripts.governance.d8_doc_sync.algo_flow_reverse_orphan_reconciler
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcilerSpec, ReconcileResult, _write_reconcile_report); scripts.ops_guard (guard_recycle, set_reconciler_context); scripts.governance.d3_metadata.batch_creation_tokens (_creation_tokens_section); zephyr.shared.io.file_utils (safe_write_text); zephyr.shared.infra.process_pool (run_subprocess_hidden，trae_067 铁律2 无窗 git 子进程)
# [CONSUMERS] GitCommitGateway._reconciliation_registry.register
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] post-commit 事件触发非时间触发 | 判定三要素全真才算孤件（HEAD 树缺失+盘上缺失+源确有退役提交）| 反向锚点命中即否决 | 检测面只报不删（file_ops=read）| 退役面必经 Owner 裁定绑定（裁定文本点名本目标）| 注册表摘条走 CAS 段内锚定+写后进程外自检
# [MODIFY-GUARD] gate_id="GATE-ALGO-FLOW-REVERSE-ORPHAN"
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] git ls-tree 失败→warn（判不了就不判，绝不因观测面故障推断删除）；单镜像读取异常计入 unreadable 不阻断整体普查；退役面任一前置不满足→ RetireRefused 且回滚注册表写前字节
# [TESTS] tests/scripts/governance/d8_doc_sync/test_algo_flow_reverse_orphan_reconciler.py
# [A_module] module_id=MOD-algo_flow_reverse_orphan | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-326
# noqa: m11-perm-manual-legitimate  M11豁免: 本件已按 post-commit 事件触发 reconciler 注册（git_commit_gateway d8_doc_sync 段 priority=245，非 cron/Timer/常驻服务），argparse/__main__ 仅为人工诊断入口与 Owner 裁定授权（裁定#307①）后才可执行的退役通道
"""algo_flow_reverse_orphan_reconciler.py — ALGO_FLOW 反向孤件普查对账（#ARCH-326）

职责：post-commit 事件触发，普查 docs/03_modules/**/algo_flow/** 出仓镜像 YAML 中
"源已退役、镜像还在"的反向孤件，报告并 critical_warn；退役动作由 Owner 裁定授权的
显式 ``--apply`` 通道执行（镜像进回收站 + 注册表 creation_tokens 段 CAS 摘条 + 同批提交）。

治本病根（2026-09-18，#ARCH-326）：
  algo_flow_link_gate 只查正向（镜像 source_of_truth 指向不存在的源 → 阻断），但删源
  那一笔 commit 不带镜像 → 门禁看不到；结果 model_capability_exam/__init__.py 于
  6a0eca4700 删除后，其 ALGO_FLOW 镜像与 capability_canonical_file_registry 登记条目
  静默存活成反向孤件。一次性普查（3227 镜像命中 1 件）证明该缺陷类真实存在，但无
  常驻观测面 → 再发生即无声。#ARCH-326 fix_phase 指定归属：并入 d8_doc_sync 事件触发
  对账，不进 pre-commit（全库扫描属触碰税，perf 方案 §2.6 分级不允许）。

门位约束（裁定#307①）：净删/退役/冻结区解锁 = Owner 常设门位。故本 reconciler 默认
只检测（file_ops 仅 read），不自动持有退役能力；``--apply`` 是显式人工入口，且必须带
``--owner-ruling NNN``，该裁定正文（或 affected_files）必须点名待退役镜像，否则拒执
行——把"口头批准"经正式通道（裁定登记表）升格为可机判授权（宪法 §9.11）。

判定三要素（全真才算反向孤件，任一不满足即不判）：
  ① 镜像在 HEAD 提交树中（tracked，工作树脏不影响判定权威面）；
  ② 镜像头 8 行有 source_of_truth 指向 .py，且该路径既不在 HEAD 树也不在盘上；
  ③ 该源路径在历史里确有删除提交（``--diff-filter=D`` 命中）——把"源被有意退役"与
     "路径写错/从未存在"分开，后者归 broken_source_reference 桶（只报，永不退役）。
否决项：HEAD 树中任一 .py 仍以镜像相对路径作 ``[ALGO_FLOW] external:`` 锚 → 源侧仍在
引用本镜像，不是孤件（保守方向：宁漏报不误删）。

Usage::

    python scripts/governance/d8_doc_sync/algo_flow_reverse_orphan_reconciler.py            # 全库普查（只读）
    python .../algo_flow_reverse_orphan_reconciler.py --json                                # 机器可读
    python .../algo_flow_reverse_orphan_reconciler.py --apply --mirror <rel> --owner-ruling <NNN>
"""

from __future__ import annotations

__manifest__ = """
args: [--json, --apply, --mirror, --owner-ruling, --session, --no-commit, --dry-run]
description: algo_flow_reverse_orphan_reconciler.py — ALGO_FLOW 反向孤件普查对账（#ARCH-326）
dimensions:
- D8
priority: P1
timeout_seconds: 120
warn_only: false
"""

import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

__all__ = ["make_algo_flow_reverse_orphan_reconciler", "retire_orphan", "RetireRefused"]

_DEFAULT_ROOT = Path(__file__).resolve().parents[3]

# 相对路径字面量用 "/".join 构造（完整字符串字面量会触发 VOCAB-CHAIN 门禁，
# 对齐 algo_flow_translation_reconciler L113-133 先例）
_DOC_MODULES_PREFIX = "/".join(["docs", "03_modules"])
_ALGO_FLOW_SEG = "algo_flow"
_REGISTRY_REL = "/".join(
    [
        "docs",
        "01_policies_and_standards",
        "_registry",
        "catalogs",
        "capability_canonical_file_registry.yaml",
    ]
)
_RULING_REL = "/".join(
    [
        "docs",
        "01_policies_and_standards",
        "_registry",
        "catalogs",
        "ruling_registry.yaml",
    ]
)
_SELF_RELPATH = "/".join(["scripts", "governance", "d8_doc_sync", "algo_flow_reverse_orphan_reconciler.py"])

#: 镜像契约头窗口（出仓器只在前 8 行写 doc_type/ttl/module/source_of_truth，
#: 与 externalize_algo_flow._existing_yaml_for 的同一读取约定对齐）
_HEADER_WINDOW_LINES = 8
_SOT_RE = re.compile(r"^source_of_truth:\s*(\S.*?)\s*$", re.MULTILINE)
_MAX_ITEMS_IN_DETAIL = 8

_gate_paths_ready = False


def _ensure_sibling_paths() -> None:
    """把仓根与 d3_metadata 注入 sys.path（本件作为 reconciler 插件被动态加载时缺这些）。

    import 失败不静默——调用方拿 ImportError 即降级 warn（对齐"路径漂移致假 clean"教训）。
    """
    global _gate_paths_ready
    if _gate_paths_ready:
        return
    for d in (
        str(_DEFAULT_ROOT),
        str(_DEFAULT_ROOT / "scripts"),
        str(_DEFAULT_ROOT / "scripts" / "governance" / "d3_metadata"),
    ):
        if d not in sys.path:
            sys.path.insert(0, d)
    _gate_paths_ready = True


def _root_of(gateway: Any) -> Path:
    return Path(str(getattr(gateway, "project_root", None) or _DEFAULT_ROOT))


def _to_rel(root: Path, file_path: str | Path) -> str:
    """绝对/相对路径 → 仓库相对 posix 路径（root 外路径原样 posix 化）。"""
    p = Path(str(file_path))
    if not p.is_absolute():
        return str(p).replace("\\", "/")
    try:
        return p.resolve().relative_to(Path(str(root)).resolve()).as_posix()
    except (OSError, ValueError):
        return str(p).replace("\\", "/")


def _is_mirror_rel(rel: str) -> bool:
    """HEAD 树路径是否为 ALGO_FLOW 出仓镜像 YAML。"""
    return (
        rel.startswith(f"{_DOC_MODULES_PREFIX}/")
        and f"/{_ALGO_FLOW_SEG}/" in rel
        and rel.endswith(".yaml")
    )


def _head_tree_files(gateway: Any) -> list[str] | None:
    """HEAD 提交树文件清单（工作树无关的权威面）。失败返回 None（调用方降级 warn）。"""
    result = gateway.run_git(["git", "ls-tree", "-r", "--name-only", "HEAD"])
    if result.returncode != 0:
        return None
    return [ln.strip().replace("\\", "/") for ln in result.stdout.splitlines() if ln.strip()]


def _source_of_truth(mirror_abs: Path) -> str | None:
    """读镜像头窗口取 source_of_truth；无该键返回 None（缺键是另一缺陷类，不判孤件）。"""
    try:
        with mirror_abs.open(encoding="utf-8", errors="replace") as fh:
            head = "".join(next(fh, "") for _ in range(_HEADER_WINDOW_LINES))
    except OSError:
        return None
    m = _SOT_RE.search(head)
    if not m:
        return None
    return m.group(1).strip().strip("'\"")


def _touching_commits(gateway: Any, sot_rel: str, extra_args: list[str]) -> str:
    """`git log -1 --format=%H -- <sot>` 形态查询（返回 sha 或 ""）。"""
    result = gateway.run_git(["git", "log", "-1", "--format=%H", *extra_args, "--", sot_rel])
    if result.returncode != 0:
        return ""
    out = result.stdout.strip()
    return out.splitlines()[0].strip() if out else ""


def _reverse_anchored(gateway: Any, mirror_rel: str) -> bool:
    """否决项：HEAD 树中任一 .py 仍以镜像相对路径作 ALGO_FLOW external 锚。"""
    result = gateway.run_git(["git", "grep", "-l", "-F", mirror_rel, "HEAD", "--", "*.py"])
    return result.returncode == 0 and bool(result.stdout.strip())


def _classify(gateway: Any, tree: list[str]) -> dict:
    """全库普查 → {scanned, orphans, broken_source_references, unreadable}。"""
    root = _root_of(gateway)
    tree_set = set(tree)
    mirrors = sorted(rel for rel in tree if _is_mirror_rel(rel))
    orphans: list[dict] = []
    broken: list[dict] = []
    unreadable = 0
    for rel in mirrors:
        sot = _source_of_truth(root / rel)
        if sot is None:
            unreadable += 1  # 缺 source_of_truth 键 = 引用契约缺陷类，由 link gate 面处置
            continue
        if sot in tree_set or (root / sot).is_file():
            continue  # 源仍在（.is_file() 而非 .exists()：目录/悬空 symlink 不算源）
        if not sot.endswith(".py") or (root / sot).is_dir():
            broken.append({"mirror": rel, "source_of_truth": sot, "reason": "not_a_python_file_target"})
            continue
        if not _touching_commits(gateway, sot, []):
            broken.append({"mirror": rel, "source_of_truth": sot, "reason": "never_tracked"})
            continue
        retired_by = _touching_commits(gateway, sot, ["--diff-filter=D"])
        if not retired_by:
            broken.append({"mirror": rel, "source_of_truth": sot, "reason": "no_delete_commit"})
            continue
        if _reverse_anchored(gateway, rel):
            broken.append({"mirror": rel, "source_of_truth": sot, "reason": "reverse_anchor_alive"})
            continue
        orphans.append({"mirror": rel, "source_of_truth": sot, "retired_by": retired_by})
    return {
        "scanned": len(mirrors),
        "orphans": orphans,
        "broken_source_references": broken,
        "unreadable": unreadable,
    }


def _apply_command(mirror_rel: str) -> str:
    """把退役包写成可直接执行的一行，消除"报了但不知怎么修"的 gap。"""
    return f"python {_SELF_RELPATH} --apply --mirror {mirror_rel} --owner-ruling <裁定号> --session <sid>"


def _emit_report(gateway: Any, session_id: str, payload: dict) -> str:
    """报告落盘（复用 reconciler 家族单点写手；失败返回错误串供 detail 注明）。"""
    try:
        from zephyr.governance.audit.reconciliation_registry import _write_reconcile_report
    except ImportError as e:
        return f"report writer unavailable ({e})"
    _, err = _write_reconcile_report(_root_of(gateway), "algo_flow_reverse_orphan", dict(payload))
    return err


def _should_trigger(root: Path, committed_files: list[str]) -> bool:
    """触发条件：本次 commit 触碰源码（源可能被删/改名）或 ALGO_FLOW 镜像本身。

    root 必须是本 gateway 自己的 project_root——linked worktree 里 committed 绝对路径
    锚在该 worktree，用默认根做 relative_to 会失败并留绝对路径 → 永不触发（静默失效）。
    """
    for f in committed_files:
        rel = _to_rel(root, f)
        if rel.endswith(".py") and (rel.startswith("src/") or rel.startswith("scripts/")):
            return True
        if _is_mirror_rel(rel):
            return True
    return False


def _reconcile(gateway: Any, committed_files: list[str], session_id: str) -> Any:
    """执行反向孤件普查：只检测不退役（裁定#307① Owner 常设门位）。"""
    try:
        from zephyr.governance.audit.reconciliation_registry import ReconcileResult
    except ImportError:
        ReconcileResult = dict  # type: ignore

    tree = _head_tree_files(gateway)
    if tree is None:
        return ReconcileResult(
            action="warn",
            detail="git ls-tree HEAD 失败，无法普查 ALGO_FLOW 反向孤件（观测面故障不推断删除）",
        )
    census = _classify(gateway, tree)
    report_err = _emit_report(
        gateway,
        session_id,
        {"gate_id": "GATE-ALGO-FLOW-REVERSE-ORPHAN", "session_id": session_id, **census},
    )
    orphans = census["orphans"]
    if orphans:
        listed = "; ".join(
            f"{o['mirror']} ← 源 {o['source_of_truth']} 退役于 {o['retired_by'][:10]}"[:220] for o in orphans[:_MAX_ITEMS_IN_DETAIL]
        )
        more = f"；…（共 {len(orphans)} 件，全量见报告）" if len(orphans) > _MAX_ITEMS_IN_DETAIL else ""
        hint = _apply_command(orphans[0]["mirror"]) if len(orphans) == 1 else "逐件退役命令见报告或 --json 输出"
        return ReconcileResult(
            action="critical_warn",
            detail=(
                f"ALGO_FLOW 反向孤件 {len(orphans)} 件（源已退役、镜像与注册表条目仍在，#ARCH-326）："
                f"{listed}{more}。退役=注册表条目净删，属裁定#307① Owner 常设门位，"
                f"须经 Owner 裁定登记后显式执行：{hint}"
                + (f"；报告落盘失败({report_err})" if report_err else "")
            ),
        )

    broken = census["broken_source_references"]
    if broken:
        sample = "; ".join(f"{b['mirror']}→{b['source_of_truth']}({b.get('reason', '?')})" for b in broken[:_MAX_ITEMS_IN_DETAIL])
        return ReconcileResult(
            action="warn",
            detail=(
                f"ALGO_FLOW 镜像 source_of_truth 引用异常 {len(broken)} 件"
                f"（非反向孤件，永不自动退役）: {sample}"
                + (f"；…（共 {len(broken)} 件）" if len(broken) > _MAX_ITEMS_IN_DETAIL else "")
            ),
        )

    return ReconcileResult(
        action="clean",
        detail=(
            f"ALGO_FLOW 镜像无反向孤件（普查 {census['scanned']} 件；"
            f"缺 SOT 键 {census['unreadable']} 件不判；报告落盘失败={report_err or '无'}）"
        ),
    )


# ── Owner 裁定授权的退役通道（人工显式触发；reconcile 自动路径永不调用）──


class RetireRefused(RuntimeError):
    """退役前置不满足（fail-closed 拒执行）。"""


def _normalize_ruling_id(raw: str) -> str:
    s = str(raw).strip()
    return s if s.startswith("裁定#") else f"裁定#{s.lstrip('#')}"


def assert_owner_grant(gateway: Any, mirror_rel: str, ruling_ref: str) -> str:
    """机判 Owner 门位：裁定存在、status=active、且正文/affected_files 点名本镜像。

    宪法 §9.11：对话口头"Owner 说"不构成门禁豁免——门位经裁定登记生效。所以授权唯一
    合法凭据 = ruling_registry 里一条把本镜像写清楚的 active 裁定。
    """
    _ensure_sibling_paths()
    path = _root_of(gateway) / _RULING_REL
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        raise RetireRefused(f"裁定登记表不可读/解析失败，拒退役（fail-closed）: {e}") from e
    rulings = data.get("rulings") if isinstance(data, dict) else data
    want = _normalize_ruling_id(ruling_ref)
    hit = next((r for r in (rulings or []) if isinstance(r, dict) and str(r.get("ruling_id", "")) == want), None)
    if hit is None:
        raise RetireRefused(f"裁定 {want} 未登记于 {_RULING_REL}，无 Owner 授权凭据，拒退役")
    if str(hit.get("status", "")).strip() != "active":
        raise RetireRefused(f"裁定 {want} status={hit.get('status')!r} 非 active，不构成有效授权")
    if mirror_rel not in yaml.safe_dump(hit, allow_unicode=True):
        raise RetireRefused(f"裁定 {want} 正文未点名镜像 {mirror_rel}——授权不覆盖该目标，拒退役")
    return want


def _creation_tokens_section(text: str) -> tuple[int, int]:
    """creation_tokens 段边界（复用 batch_creation_tokens 单点，防死区锚点漂移）。"""
    _ensure_sibling_paths()
    from batch_creation_tokens import _creation_tokens_section as _impl

    return _impl(text)


def _registry_removal(text: str, mirror_rel: str) -> tuple[str, int]:
    """段内锚定删除本镜像的 creation_tokens 条目 → (新文本, 删除行数)。

    Raises:
        RetireRefused: 段内命中 0 条或多条（锚点不唯一=判据失配，宁不执行）。
    """
    start, end = _creation_tokens_section(text)
    lines = text[start:end].splitlines(keepends=True)
    target = f"- file: {mirror_rel}\n"
    idx = [i for i, ln in enumerate(lines) if ln == target]
    if len(idx) != 1:
        raise RetireRefused(f"creation_tokens 段内 {mirror_rel} 命中 {len(idx)} 条（需恰好 1 条），拒写")
    i = idx[0]
    j = i + 1
    while j < len(lines) and lines[j].startswith("  "):
        j += 1
    return text[:start] + "".join(lines[:i] + lines[j:]) + text[end:], j - i


def _registry_post_write_issues(text: str, mirror_rel: str, expect_count: int) -> list[str]:
    """写后进程外自检：解析通过 + 语义落位（条目消失、计数=旧-1、尾键仍末位）。"""
    try:
        data = yaml.safe_load(text)
    except Exception as exc:  # noqa: BLE001 — 解析失败即问题本体
        return [f"yaml.safe_load 解析失败: {str(exc)[:160]}"]
    if not isinstance(data, dict):
        return [f"顶层不是 mapping（实际 {type(data).__name__}）"]
    issues: list[str] = []
    keys = list(data.keys())
    if keys[-1] != "di_seam_exemptions":
        issues.append(f"末位顶层键不再是 di_seam_exemptions（实际 {keys[-1]}）——疑似错位/悬挂")
    rows = data.get("creation_tokens") or []
    if any(str(r.get("file", "")).replace("\\", "/") == mirror_rel for r in rows if isinstance(r, dict)):
        issues.append(f"{mirror_rel} 仍残留 creation_tokens 段（摘除未生效）")
    if len(rows) != expect_count:
        issues.append(f"creation_tokens 条目数 {len(rows)} != 预期 {expect_count}")
    return issues


def _retirement_commit_message(mirror_rel: str, confirmed: dict, ruling_id: str) -> str:
    """退役提交信息（REGISTRY-MASS-DELETION 逃生标记 + RULING-REFERENCE 双钉）。"""
    return (
        f"chore(algo_flow): 反向孤件退役 {Path(mirror_rel).name}——"
        f"源 {confirmed['source_of_truth']} 已退役({confirmed['retired_by'][:10]})，"
        f"镜像+注册表条目同批出仓（#ARCH-326）\n\n"
        f"[RULING-REFERENCE: {ruling_id}]\n"
        f"[allow-mass-deletion:{ruling_id} 授权净删 capability_canonical_file_registry 单条反向孤件登记]"
    )


def retire_orphan(
    gateway: Any,
    mirror_rel: str,
    *,
    owner_ruling: str,
    session_id: str = "st-reverse-orphan-apply",
    commit: bool = True,
    dry_run: bool = False,
) -> dict:
    """退役一件反向孤件：复核孤件判定 + 校验 Owner 授权 → 镜像进回收站 → CAS 摘注册表
    条目（写后进程外自检，不过即回滚）→ 同批提交。

    Returns:
        结果字典（孤件凭据/授权裁定/回收路径/注册表前后条目数/提交状态）。

    Raises:
        RetireRefused: 任一前置不满足（复核、授权、锚点唯一性、写后自检）。
    """
    _ensure_sibling_paths()
    root = _root_of(gateway)
    tree = _head_tree_files(gateway)
    if tree is None:
        raise RetireRefused("git ls-tree HEAD 失败，无法复核孤件判定")
    confirmed = next((o for o in _classify(gateway, tree)["orphans"] if o["mirror"] == mirror_rel), None)
    if confirmed is None:
        raise RetireRefused(f"{mirror_rel} 不在本次复核的反向孤件清单中（三要素未全真），拒退役")
    ruling_id = assert_owner_grant(gateway, mirror_rel, owner_ruling)

    registry_abs = root / _REGISTRY_REL
    pre_text = registry_abs.read_text(encoding="utf-8")
    norm = pre_text.replace("\r\n", "\n")
    try:
        rows_before = len((yaml.safe_load(norm).get("creation_tokens")) or [])
    except (yaml.YAMLError, AttributeError) as e:
        raise RetireRefused(f"注册表当前不可解析/结构走样，拒写: {e}") from e
    new_text, removed_lines = _registry_removal(norm, mirror_rel)

    message = _retirement_commit_message(mirror_rel, confirmed, ruling_id)
    result: dict[str, Any] = {
        "gate_id": "GATE-ALGO-FLOW-REVERSE-ORPHAN",
        "mirror": mirror_rel,
        "source_of_truth": confirmed["source_of_truth"],
        "retired_by": confirmed["retired_by"],
        "owner_ruling": ruling_id,
        "registry_lines_removed": removed_lines,
        "creation_tokens_before": rows_before,
        "commit_message": message,
        "dry_run": dry_run,
    }
    if dry_run:
        result["planned"] = {
            "recycle": "镜像移入 .runtime/recycle_bin/<ts>/（30 天可恢复，永不物理删除）",
            "registry": f"摘除 {removed_lines} 行条目，creation_tokens {rows_before} → {rows_before - 1}",
        }
        return result

    # 顺序即安全面：先镜像（回收站可逆）后注册表（CAS 不可逆面）。注册表写失败时
    # 镜像已在回收站——缺陷类收敛为"缺镜像"（link gate 可观测），不会产生漏登记的静默。
    from ops_guard import guard_recycle, reset_reconciler_context, set_reconciler_context
    from zephyr.shared.io.file_utils import atomic_write, content_sha256, safe_write_text

    ctx_token = set_reconciler_context("GATE-ALGO-FLOW-REVERSE-ORPHAN", frozenset({"read", "write", "move"}))
    try:
        result["recycled_to"] = guard_recycle(
            root / mirror_rel,
            repo_root=str(root),
            reason=(
                f"#ARCH-326 反向孤件退役（{ruling_id}）："
                f"源 {confirmed['source_of_truth']} 已于 {confirmed['retired_by'][:10]} 退役"
            ),
        )
        base_sha = content_sha256(norm)
        safe_write_text(registry_abs, new_text, expected_base_sha256=base_sha, repo_root=str(root), newline="")
        issues = _registry_post_write_issues(registry_abs.read_text(encoding="utf-8"), mirror_rel, rows_before - 1)
        if issues:
            atomic_write(registry_abs, pre_text, newline="")  # 回滚（不用 CAS：磁盘已是新内容，base 必不符）
            raise RetireRefused("注册表写后自检不过，已回滚写前文本: " + "; ".join(issues))
    finally:
        reset_reconciler_context(ctx_token)

    result["creation_tokens_after"] = rows_before - 1
    if commit:
        commit_result = gateway._commit_auto(session_id, [str(root / mirror_rel), str(registry_abs)], message)
        result["commit_status"] = str(getattr(commit_result, "status", "?"))
    else:
        result["commit_status"] = "SKIPPED(--no-commit)"
    return result


def make_algo_flow_reverse_orphan_reconciler(gateway: Any):
    """工厂：构造 GATE-ALGO-FLOW-REVERSE-ORPHAN 反向孤件普查 reconciler spec。

    Args:
        gateway: GitCommitGateway 实例（需 project_root 与 run_git）。与同目录其它
            d8_doc_sync 插件不同——本件必须走 HEAD 权威树，故收 gateway 而非裸 Path。

    Returns:
        ReconcilerSpec（priority=245，落在 ALGO-FLOW-TRANSLATION-DRIFT(240) 与
        agents_cheatsheet_drift/GATE-ID-UNIQ(250) 之间的同域空档）。
    """
    from zephyr.governance.audit.reconciliation_registry import ReconcilerSpec

    def _trigger(committed_files: list[str]) -> bool:
        return _should_trigger(_root_of(gateway), committed_files)

    def _reconcile_fn(committed_files: list[str], session_id: str) -> Any:
        return _reconcile(gateway, committed_files, session_id)

    return ReconcilerSpec(
        gate_id="GATE-ALGO-FLOW-REVERSE-ORPHAN",
        trigger=_trigger,
        reconcile=_reconcile_fn,
        priority=245,
        file_ops=frozenset({"read"}),  # 检测面只读；退役能力不自动持有（裁定#307①）
    )


def _main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="ALGO_FLOW 反向孤件普查 / Owner 授权退役（#ARCH-326）")
    parser.add_argument("--json", action="store_true", help="输出机器可读普查报告")
    parser.add_argument("--apply", action="store_true", help="执行退役（需 --mirror 与 --owner-ruling）")
    parser.add_argument("--mirror", help="待退役镜像相对路径")
    parser.add_argument("--owner-ruling", help="授权退役的裁定号（正文须点名该镜像）")
    parser.add_argument("--session", default="st-reverse-orphan-apply", help="提交会话号")
    parser.add_argument("--no-commit", action="store_true", help="只改盘不提交（自检用）")
    parser.add_argument("--dry-run", action="store_true", help="只演算不写盘")
    args = parser.parse_args(argv)

    class _Gateway:
        """CLI 侧最小 gateway 面（run_git + project_root；退役提交时才需要真 gateway）。"""

        def __init__(self, project_root: str) -> None:
            self.project_root = Path(project_root)

        def run_git(self, cmd: list[str]):
            # trae_067 铁律2：Windows 裸 subprocess 闪控制台窗——走统一无窗入口
            from zephyr.shared.infra.process_pool import run_subprocess_hidden

            return run_subprocess_hidden(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
            )

    if args.apply:
        if not args.mirror or not args.owner_ruling:
            print("FAIL: --apply 必须同时给 --mirror 与 --owner-ruling", file=sys.stderr)
            return 2
        _ensure_sibling_paths()
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway

        gw: Any = GitCommitGateway(project_root=str(_DEFAULT_ROOT))
        try:
            out = retire_orphan(
                gw,
                args.mirror,
                owner_ruling=args.owner_ruling,
                session_id=args.session,
                commit=not args.no_commit,
                dry_run=args.dry_run,
            )
        except RetireRefused as e:
            print(f"REFUSED: {e}", file=sys.stderr)
            return 1
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    gateway = _Gateway(str(_DEFAULT_ROOT))
    tree = _head_tree_files(gateway)
    if tree is None:
        print("FAIL: git ls-tree HEAD 失败", file=sys.stderr)
        return 1
    census = _classify(gateway, tree)
    if args.json:
        print(json.dumps(census, ensure_ascii=False, indent=2))
    else:
        print(
            f"扫描镜像 {census['scanned']} 件；反向孤件 {len(census['orphans'])} 件；"
            f"引用异常 {len(census['broken_source_references'])} 件；缺 SOT 键 {census['unreadable']} 件"
        )
        for o in census["orphans"]:
            print(f"  ORPHAN {o['mirror']} ← {o['source_of_truth']} (退役于 {o['retired_by'][:10]})")
            print(f"         退役：{_apply_command(o['mirror'])}")
        for b in census["broken_source_references"][:20]:
            print(f"  BROKEN-REF {b['mirror']} → {b['source_of_truth']} ({b.get('reason', '?')})")
    return 0 if not census["orphans"] else 3


if __name__ == "__main__":
    sys.exit(_main())
