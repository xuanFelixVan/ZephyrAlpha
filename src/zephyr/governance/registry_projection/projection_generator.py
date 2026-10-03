# [MODULE] zephyr.governance.registry_projection.projection_generator
# [DOMAIN] D_GOV_CODE_QUALITY
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §W-M1
# [TTL] permanent
# [DEPENDENCIES] zephyr.governance.registry_projection.model / renderer / state / pg_source；
#   zephyr.shared.io.file_utils (safe_write_text, content_sha256)
# [CONSUMERS] scripts/governance/registry_projection/registry_projection_generator.py（CLI）；
#   zephyr.gov_enforcement.rule_bridge.commit_belt_daemon（staleness 探针，lazy import）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 生成器是投影册唯一合法写者（PG wins）：私改=证据留档+自动再生成，永不
#   git checkout（会吃他人 staged）；CAS 冲突退避重试 3 次后死信告警；PG 不可达=
#   零写退出+降级观察行，绝不阻塞调用方（fail-open 纪律）；幂等判据=连续两次运行
#   第二次零写盘
# [MODIFY-GUARD] 新建 2026-09-23 st-wm1-buildB-20260923（W-M1 波0 车道B）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] run 永不向调用方抛 PG/写盘异常——全部折入 Report；只有编程错误（快照模型坏）才 raise
# [TESTS] tests/governance/registry_projection/test_projection_generator.py
"""generator.py — 投影生成器编排层（check/render 两模式+四象限处置）。

处置 playbook（丙号文 §3.3，全自动无人工常态参与）：
- 私改：diff 留档 .runtime/gate_audit/registry_drift_<ts>.diff → safe_write CAS 覆写
  （PG wins）→ 状态文件更新 → registry_drift 记账；
- 陈旧：静默再生成+记账（±条目数喂 registry_drift kind 身份增减量字段）；
- 冲突：证据先行留档 → 再生成 → 复检仍不等 → 死信观察行（唯一出人工的通道）；
- PG 宕机：D vs S 降级判别，私改照样处置（本地锚），PG 前进类漂移记降级观察行。


# [ALGO_FLOW]
层: 判别 → 处置
- 判别: 四象限（D/S/R 三方哈希）：干净/私改/陈旧/冲突
- 处置: 私改=证据留档+PG wins 重渲染；陈旧=静默再生成；冲突=死信；PG 不可达=零写退出"""

from __future__ import annotations

import difflib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

from zephyr.governance.registry_projection.model import ProjectionSnapshot, snapshot_from_yaml
from zephyr.governance.registry_projection.pg_source import ProjectionUnavailable
from zephyr.governance.registry_projection.renderer import SemanticMismatch, render, self_check
from zephyr.governance.registry_projection.state import (
    QUADRANT_CLEAN,
    QUADRANT_CONFLICT,
    QUADRANT_PG_UNREACHABLE,
    QUADRANT_PRIVATE_EDIT,
    QUADRANT_STALE,
    ProjectionState,
    classify,
    load_state,
    save_state,
)
from zephyr.shared.io.file_utils import content_sha256, safe_write_text

logger = logging.getLogger(__name__)

__all__: Final = ["ProjectionReport", "default_registry", "run"]

EVIDENCE_REL = ".runtime/gate_audit"

_DEFAULT_REGISTRY_ID = "REG-CAPCAN-001"

_CAS_RETRIES = 3


def default_registry() -> tuple[str, str]:
    """管理册 = REG-CAPCAN-001，物理路径经 ROOR 反查（禁 .py 硬编码 SSoT 路径）。"""
    from zephyr.governance.registry_ledger.baseline import load_roor_index  # noqa: PLC0415

    idx = load_roor_index(Path.cwd())
    matches = [p for p, v in idx.items() if v.get("registry_id") == _DEFAULT_REGISTRY_ID]
    if not matches:
        raise LookupError(f"ROOR 缺 {_DEFAULT_REGISTRY_ID}（投影管理册）")
    return _DEFAULT_REGISTRY_ID, matches[0]


def _roor_path(idx: dict, rid: str) -> str:
    matches = [p for p, v in idx.items() if v.get("registry_id") == rid]
    if not matches:
        raise LookupError(f"ROOR 缺 {rid}")
    return matches[0]


@dataclass
class ProjectionReport:
    ok: bool
    quadrant: str
    wrote: bool = False
    actions: list[str] = field(default_factory=list)
    evidence_path: str = ""
    detail: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "quadrant": self.quadrant,
            "wrote": self.wrote,
            "actions": self.actions,
            "evidence_path": self.evidence_path,
            "detail": self.detail,
        }


def _ledger_record_drift(physical_path: str, *, added: int, removed: int, detail: str) -> None:
    try:
        from zephyr.gov_enforcement.rule_bridge.commit_belt_daemon import record_registry_drift

        record_registry_drift(physical_path, added=added, removed=removed, detail=detail)
    except Exception:  # noqa: BLE001 — 记账 fail-open
        logger.debug("registry_drift 记账失败（不阻断）", exc_info=True)


def _entry_index(snapshot: ProjectionSnapshot, root_key: str) -> dict[tuple[str, str], list[tuple[str, object]]]:
    from zephyr.governance.registry_projection.model import entry_identity_key

    sec = snapshot.section(root_key)
    return {} if sec is None else {entry_identity_key(e): e for e in sec.entries}


def _identity_deltas(old: ProjectionSnapshot, new: ProjectionSnapshot, root_key: str) -> tuple[int, int]:
    old_keys = set(_entry_index(old, root_key))
    new_keys = set(_entry_index(new, root_key))
    return len(new_keys - old_keys), len(old_keys - new_keys)


def _save_evidence(project_root: Path, physical_path: str, disk_text: str, rendered: str) -> str:
    diff = "".join(
        difflib.unified_diff(
            disk_text.splitlines(keepends=True),
            rendered.splitlines(keepends=True),
            fromfile=f"disk:{physical_path}",
            tofile="render:PG_wins",
        )
    )
    from zephyr.shared.utils.time_utils import now_utc

    path = project_root / EVIDENCE_REL / f"registry_drift_{now_utc().strftime('%Y%m%dT%H%M%S%f')}.diff"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(diff, encoding="utf-8", newline="\n")
    return str(path)


def _write_rendered(project_root: Path, physical_path: str, rendered: str) -> None:
    target = project_root / physical_path
    for attempt in range(_CAS_RETRIES):
        expected_base = content_sha256(target.read_text(encoding="utf-8")) if target.exists() else None
        try:
            safe_write_text(target, rendered, expected_base_sha256=expected_base, repo_root=project_root, newline="\n")
            return
        except Exception as exc:  # noqa: BLE001 — CAS 冲突退避重试
            if attempt == _CAS_RETRIES - 1:
                _ledger_record_drift(physical_path, added=0, removed=0, detail=f"cas_dead_letter: {type(exc).__name__}")
                logger.error("投影写盘 CAS 三连冲突（两生成器并发=违规信号，人工分诊）: %s", physical_path)
                raise ProjectionUnavailable("CAS 三连冲突死信") from exc
            continue


def _commit_state(project_root: Path, snapshot: ProjectionSnapshot, rendered: str, physical_path: str) -> None:
    from zephyr.shared.utils.time_utils import now_utc

    save_state(
        project_root,
        ProjectionState(
            content_sha256=content_sha256(rendered),
            ledger_revision=snapshot.ledger_revision,
            registry_path=physical_path,
            entry_counts=snapshot.entry_counts(),
            generated_at=now_utc().isoformat(),
        ),
    )


def _source_snapshot(source: object, registry_id: str, physical_path: str) -> ProjectionSnapshot:
    """source 形态：None=PG 最新版；str/Path=JSON 文件；callable=自定义加载器。"""
    if source is None:
        from zephyr.governance.registry_projection.pg_source import load_latest_snapshot

        return load_latest_snapshot(registry_id, physical_path)
    if isinstance(source, (str, Path)):
        from zephyr.governance.registry_projection.pg_source import snapshot_from_json_file

        return snapshot_from_json_file(source)
    return source(registry_id, physical_path)


def _read_disk(target: Path) -> tuple[str, str, ProjectionReport | None]:
    """读盘上文件与指纹；不可读=PG 不可达象限报告。"""
    disk_text = ""
    disk_sha = ""
    try:
        if target.exists():
            disk_text = target.read_text(encoding="utf-8")
            disk_sha = content_sha256(disk_text)
    except OSError as exc:
        return (
            "",
            "",
            ProjectionReport(ok=False, quadrant=QUADRANT_PG_UNREACHABLE, detail={"error": f"盘上文件不可读: {exc}"}),
        )
    return disk_text, disk_sha, None


def _pg_unavailable_branch(
    root: Path,
    phys: str,
    disk_text: str,
    disk_sha: str,
    state: ProjectionState | None,
    mode: str,
    exc: ProjectionUnavailable,
) -> ProjectionReport:
    """PG 宕机降级：D vs S 本地判别（私改照样现形），PG 前进类漂移不可判。"""
    anchor = state.content_sha256 if state else ""
    local_q = (QUADRANT_PRIVATE_EDIT if disk_sha != anchor else QUADRANT_CLEAN) if anchor else QUADRANT_PG_UNREACHABLE
    _ledger_record_drift(phys, added=0, removed=0, detail=f"pg_unreachable degraded quadrant={local_q}")
    if local_q == QUADRANT_PRIVATE_EDIT and mode == "render":
        return _heal_from_local_anchor(root, phys, disk_text, state, str(exc))
    return ProjectionReport(
        ok=local_q == QUADRANT_CLEAN,
        quadrant=QUADRANT_PG_UNREACHABLE,
        detail={"degraded_local_quadrant": local_q, "error": str(exc)[:200]},
    )


def _armed_initial_write(root: Path, phys: str, snapshot: ProjectionSnapshot, rendered: str) -> ProjectionReport:
    """武装首打：全量落盘+建状态文件（无本地锚，无象限可比）。"""
    try:
        _write_rendered(root, phys, rendered)
    except ProjectionUnavailable as exc:
        return ProjectionReport(ok=False, quadrant=QUADRANT_PG_UNREACHABLE, detail={"error": str(exc)[:200]})
    _commit_state(root, snapshot, rendered, snapshot.physical_path)
    return ProjectionReport(
        ok=True,
        quadrant="armed_initial",
        wrote=True,
        detail={"ledger_revision": snapshot.ledger_revision, "entry_counts": snapshot.entry_counts()},
    )


def _drift_write_phase(
    root: Path,
    disk_text: str,
    rendered: str,
    snapshot: ProjectionSnapshot,
    quadrant: str,
    evidence: str,
    actor_session: str,
) -> ProjectionReport:
    """陈旧/私改/冲突象限的再生成写盘+漂移记账（render 模式专属）。"""
    added, removed = _identity_deltas(
        snapshot_from_yaml(disk_text, registry_id=snapshot.registry_id, physical_path=snapshot.physical_path)
        if disk_text
        else snapshot,
        snapshot,
        "creation_tokens",
    )
    try:
        _write_rendered(root, snapshot.physical_path, rendered)
    except ProjectionUnavailable as exc:
        return ProjectionReport(ok=False, quadrant=quadrant, detail={"error": str(exc)[:200]})

    _commit_state(root, snapshot, rendered, snapshot.physical_path)
    _ledger_record_drift(
        snapshot.physical_path,
        added=added,
        removed=removed,
        detail=f"projection_regen quadrant={quadrant} revision={snapshot.ledger_revision} actor={actor_session or 'daemon'}",
    )
    return ProjectionReport(
        ok=True,
        quadrant=quadrant,
        wrote=True,
        evidence_path=evidence,
        detail={
            "ledger_revision": snapshot.ledger_revision,
            "added": added,
            "removed": removed,
            "entry_counts": snapshot.entry_counts(),
        },
    )


def run(
    project_root: str | Path,
    mode: str = "check",
    source: object = None,
    registry_id: str | None = None,
    physical_path: str | None = None,
    actor_session: str = "",
) -> ProjectionReport:
    """主入口：mode='check' 零写判漂移；mode='render' 按四象限处置（全自动）。

    本函数永不因 PG/写盘故障向调用方抛异常（折入 Report）——投影器绝不阻塞任何调用方。
    """
    root = Path(project_root)
    if not registry_id or not physical_path:
        rid, phys = default_registry()
    else:
        rid, phys = registry_id, physical_path
    target = root / phys

    disk_text, disk_sha, read_err = _read_disk(target)
    if read_err is not None:
        return read_err

    state = load_state(root, registry_path=phys)  # v2 按册取条目（PD-1）：他册在挂不影响本册武装判定
    if state is None and mode != "render":
        # 未武装（状态文件不存在=投影管理未启用）：零行为，执法层同步 fail-open
        return ProjectionReport(ok=True, quadrant="unmanaged", detail={"armed": False})

    try:
        snapshot = _source_snapshot(source, rid, phys)
    except ProjectionUnavailable as exc:
        return _pg_unavailable_branch(root, phys, disk_text, disk_sha, state, mode, exc)

    try:
        rendered = render(snapshot)
        self_check(rendered, snapshot)
    except SemanticMismatch as exc:
        return ProjectionReport(ok=False, quadrant=QUADRANT_CONFLICT, detail={"error": f"渲染自校验拒写: {exc}"})

    if state is None:
        return _armed_initial_write(root, phys, snapshot, rendered)

    render_sha = content_sha256(rendered)
    quadrant = classify(disk_sha, state.content_sha256, render_sha)

    if quadrant == QUADRANT_CLEAN:
        return ProjectionReport(ok=True, quadrant=quadrant, detail={"ledger_revision": snapshot.ledger_revision})

    evidence = ""
    if quadrant in (QUADRANT_PRIVATE_EDIT, QUADRANT_CONFLICT):
        evidence = _save_evidence(root, phys, disk_text, rendered)
        if mode != "render":
            return ProjectionReport(
                ok=False,
                quadrant=quadrant,
                evidence_path=evidence,
                detail={"teach": "此文件是 PG 账本投影：私改无效，请走意图 API 登记+生成器重打"},
            )

    if mode != "render":
        return ProjectionReport(ok=False, quadrant=quadrant, detail={"drift": True})

    return _drift_write_phase(root, disk_text, rendered, snapshot, quadrant, evidence, actor_session)


def _heal_from_local_anchor(
    root: Path, phys: str, disk_text: str, state: ProjectionState, error: str
) -> ProjectionReport:
    """PG 宕机+私改象限：状态文件 content_sha256 对应的渲染产物不可得时，证据留档+降级告警。

    本地锚只有哈希没有字节（渲染真源在 PG）——此处只能留证+记账，等 PG 复活补扫；
    绝不猜内容覆写（唯一写者纪律：无渲染即无写）。
    """
    evidence_dir = root / EVIDENCE_REL
    evidence_dir.mkdir(parents=True, exist_ok=True)
    from zephyr.shared.utils.time_utils import now_utc

    path = evidence_dir / f"registry_drift_{now_utc().strftime('%Y%m%dT%H%M%S%f')}.json"
    path.write_text(
        json.dumps(
            {
                "kind": "private_edit_pg_unreachable",
                "registry_path": phys,
                "disk_sha256": content_sha256(disk_text) if disk_text else "",
                "expected_sha256": state.content_sha256,
                "error": error[:200],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
        newline="\n",
    )
    return ProjectionReport(
        ok=False,
        quadrant=QUADRANT_PRIVATE_EDIT,
        evidence_path=str(path),
        detail={"heal": "deferred_until_pg_back", "teach": "PG 宕机窗口私改已留证，PG 复活后补扫自动纠正"},
    )
