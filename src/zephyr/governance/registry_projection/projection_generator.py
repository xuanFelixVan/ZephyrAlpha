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
#   第二次零写盘；**测试态禁写生产投影册**（2026-10-12 维护三班 #ARCH-084 追加刀，
#   Owner 通宵令"测试面禁写投影或 fixture 隔离，你班裁"）：PYTEST_CURRENT_TEST 在场且目标
#   落在真仓根内 ⇒ 拒写＋归因告警（nodeid 直接进日志）＋独立计数，tmp 沙盘 project_root
#   照常写；判据不可得=fail-open 按现行为放行；一键回退 ZEPHYR_TEST_NO_PROD_PROJECTION=0；
#   双向一致性告警（st-maint7-20261014 P0-2② 扩面）：render/check 取到 rendered 后调
#   token_two_way_diff 比 PG 侧快照与盘上 YAML 的 creation_tokens 复合身份（键形
#   file=<路径>|token=<值>，对齐 registry_entry.entry_key），甲向=PG 有行盘上无（滞后）、
#   乙向=盘上有行 PG 无/非 active（历史直写遗留）——两向皆非零即 logger.warning 带计数与
#   样本；纯观测面：不改象限、不改写盘、异常全吞（投影器"绝不阻塞调用方"铁律不破）；
#   comparable=False（本册无该族/盘上不可解析/空册）时降级 debug 并把成因说清，
#   禁把"量不了"报成"零差异"
# [MODIFY-GUARD] 新建 2026-09-23 st-wm1-buildB-20260923（W-M1 波0 车道B）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] run 永不向调用方抛 PG/写盘异常——全部折入 Report；只有编程错误（快照模型坏）才 raise
# [TESTS] tests/governance/registry_projection/test_projection_generator.py；tests/gov/governance/test_projection_prod_write_block.py（测试面禁写守卫四臂）
"""generator.py — 投影生成器编排层（check/render 两模式+四象限处置）。

处置 playbook（丙号文 §3.3，全自动无人工常态参与）：
- 私改：diff 留档 .runtime/gate_audit/registry_drift_<ts>.diff → safe_write CAS 覆写
  （PG wins）→ 状态文件更新 → registry_drift 记账；
- 陈旧：静默再生成+记账（身份增减量喂 registry_drift kind；族集合按该册快照声明的
  节段根键逐族算后求和，禁硬编码单族名——st-maint2-20261011 T7 治"无据修剪"账面）；
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
import os
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

# 测试面禁写生产投影册（#ARCH-084 第二刀，2026-10-12 维护三班夜班）
_NO_PROD_WRITE_ENV: Final = "ZEPHYR_TEST_NO_PROD_PROJECTION"
_GUARD_OFF_VALUES: Final = frozenset({"0", "false", "off"})
# 独立计数：拒写次数与"照常写"分开可观测（在册假绿教训＝降级态与无动作同形）
TEST_PROD_PROJECTION_BLOCKED = 0


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


def _entry_index(snapshot: ProjectionSnapshot, root_key: str) -> dict[tuple[str, ...], list[tuple[str, object]]]:
    from zephyr.governance.registry_projection.model import _IDENTITY_SORT_KEY, entry_identity_key

    sec = snapshot.section(root_key)
    if sec is None:
        return {}
    # 身份声明制（st-sI-identity-20261004）：册声明字段优先，无声明退 legacy
    # (file,token) 映射（creation_tokens 排序键同构，行为零变化）
    fields = snapshot.declared_fields_for(root_key) or _IDENTITY_SORT_KEY.get(root_key)
    return {entry_identity_key(e, fields): e for e in sec.entries}


def _identity_deltas(old: ProjectionSnapshot, new: ProjectionSnapshot, root_key: str) -> tuple[int, int]:
    old_keys = set(_entry_index(old, root_key))
    new_keys = set(_entry_index(new, root_key))
    return len(new_keys - old_keys), len(old_keys - new_keys)


def _drift_family_keys(old: ProjectionSnapshot, new: ProjectionSnapshot) -> list[str]:
    """本册参与 drift 记账的族集合＝两侧快照的节段根键并集（账本派生，非新造常量表）。

    根键来源：新快照侧节段由 `publish_snapshot` 按 `registry_entry.family_key` 分组产出
    （账本真源），盘快照侧节段由 `snapshot_from_yaml` 按顶层根键产出——两者并集即该册
    声明的全部族。治本（st-maint2-20261011 T7）：此前 `_drift_write_phase` 把族名硬编码
    成 "creation_tokens"，对任何别的册（含 module_translation 册四族）恒记 0/0——条目被
    PG-wins 修剪了、账面却看不出（"无据修剪"的账面来源）。
    """
    return sorted({sec.root_key for sec in old.sections} | {sec.root_key for sec in new.sections})


def _identity_deltas_by_family(
    old: ProjectionSnapshot, new: ProjectionSnapshot
) -> tuple[int, int, dict[str, tuple[int, int]]]:
    """逐族身份增减量 → (总 added, 总 removed, {族键: (added, removed)})。

    单族算法仍是 `_identity_deltas`（creation_tokens 册的数字与硬编码时代逐字相同——
    该册只有 capabilities/creation_tokens 两族，capabilities 无增删时总和不变）。
    """
    per_family = {rk: _identity_deltas(old, new, rk) for rk in _drift_family_keys(old, new)}
    added = sum(a for a, _r in per_family.values())
    removed = sum(r for _a, r in per_family.values())
    return added, removed, per_family


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


def _repo_root_for_guard() -> Path:
    """真仓根（测试可 monkeypatch 本函数，把"生产面"指向沙盘，不动生产分支语义）。"""
    from zephyr.shared.io.paths import REPO_ROOT

    return Path(REPO_ROOT)


def _test_prod_projection_block(project_root: Path, physical_path: str) -> str | None:
    """测试态禁写生产投影册的判定：返回触发上下文（pytest nodeid）＝应拒写；None＝照常写。

    立案证据（#ARCH-084 在册三例＋维护三班 2026-10-12 夜班实测四例）：
    测试经导入链/在役落地链把 capability_canonical_file_registry.yaml 等**生产册**刷成
    PG 现态——归因 session 空串、写者无人认领，主区因此长期挂着数百行"未提交新生代"
    （实测 03:11-03:14 三分钟内 5 个不同 pid 各写一次）。测试沙盘隔离靠的是各工具的
    project_root 注入点；没带注入点的就是缺陷，禁写比放行更近事实。
    旁路旗 ZEPHYR_TEST_NO_PROD_PROJECTION=0 一键回退现行为（缺省 ON）。
    """
    if os.environ.get(_NO_PROD_WRITE_ENV, "").strip().lower() in _GUARD_OFF_VALUES:
        return None
    ctx = os.environ.get("PYTEST_CURRENT_TEST", "").strip()
    if not ctx:
        return None
    try:
        real = _repo_root_for_guard().resolve()
        root = Path(project_root).resolve()
    except Exception as exc:  # noqa: BLE001 — 判据不可得时不拒写（宁保留既有行为，不误伤生产）
        logger.warning("投影测试面守卫判据不可得，按现行为放行(%s: %s): %s", type(exc).__name__, exc, physical_path)
        return None
    # 精确同根才算"写生产册"：basetemp 在仓内 .runtime/tmp/pytest_<pid>（conftest.py:95），
    # 用"包含"判会把在册沙盘测试一屏打死——沙盘注入点语义必须原样可用。
    return ctx if root == real else None


def _write_rendered(project_root: Path, physical_path: str, rendered: str) -> None:
    ctx = _test_prod_projection_block(project_root, physical_path)
    if ctx:
        global TEST_PROD_PROJECTION_BLOCKED
        TEST_PROD_PROJECTION_BLOCKED += 1
        logger.warning(
            "TEST-PROJECTION-WRITE-BLOCKED（测试面禁写生产投影册，第 %d 次）: %s ← %s"
            "（修法＝给该测试传 tmp project_root，或带注入点走沙盘；回退旗 %s=0）",
            TEST_PROD_PROJECTION_BLOCKED,
            physical_path,
            ctx,
            _NO_PROD_WRITE_ENV,
        )
        return
    target = project_root / physical_path
    for attempt in range(_CAS_RETRIES):
        expected_base = content_sha256(target.read_text(encoding="utf-8")) if target.exists() else None
        try:
            safe_write_text(
                target,
                rendered,
                expected_base_sha256=expected_base,
                repo_root=project_root,
                newline="\n",
                # 本生成器是投影册唯一合法写者（无渲染即无写）：render 全量重打=PG wins 的
                # 设计内行为，drift 证据/identity 增减已另行记账；W4 mass-edit 守卫针对的是
                # 人工/意外整册删行（emomine 4772 行事故），生成器带逃生旗不解除守卫对其他写者
                allow_mass_edit=True,
            )
            return
        except Exception as exc:  # noqa: BLE001 — CAS 冲突退避重试
            if attempt == _CAS_RETRIES - 1:
                _ledger_record_drift(physical_path, added=0, removed=0, detail=f"cas_dead_letter: {type(exc).__name__}")
                logger.error(
                    "投影写盘三连失败（真实异常=%s，CAS 并发/守卫拒写需分诊）: %s",
                    type(exc).__name__,
                    physical_path,
                )
                raise ProjectionUnavailable(f"CAS 三连冲突死信（{type(exc).__name__}）") from exc
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
    added, removed, per_family = _identity_deltas_by_family(
        snapshot_from_yaml(disk_text, registry_id=snapshot.registry_id, physical_path=snapshot.physical_path)
        if disk_text
        else snapshot,
        snapshot,
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
        detail=(
            f"projection_regen quadrant={quadrant} revision={snapshot.ledger_revision} "
            f"actor={actor_session or 'daemon'} families={per_family}"
        ),
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
            "families": per_family,
            "entry_counts": snapshot.entry_counts(),
        },
    )


# ── 双向投影一致性对账（st-maint7-20261014 P0-2② 扩面，统筹 2026-10-14 增补第 2 条）──
# 两面病根（都有实证，非推测）：
#   甲向＝PG 有行而 YAML 无行（投影滞后）——矿考二班 10-13 夜撞 4 次拦袋；
#   乙向＝YAML 有行而 PG 无行/非 active（历史直写 YAML 入库的遗留行）——死信放量班
#     实证样本 docs/_working/tdm_goal_structure_research_2026_10_13.md 的 token 在 PG
#     是 status='retired'，而当时 HEAD 的 YAML 仍挂该行：诚实 render 相对 HEAD 恒
#     "少 1 条"，必被 registry_yaml_parse_gate 的 file|token 只增不减守门拦死
#     （同夜 6 只死信全被这同一条点名）。
# 本段职责＝把两向差集在 **render/check 就说出来**（此前只有门在拦的那一刻才说话），
# 且零阻塞——投影器铁律"绝不阻塞任何调用方"：不改象限、不改写盘、不外抛异常。
# 键形对齐 PG registry_entry.entry_key（``file=<路径>|token=<值>``）；与门侧
# _creation_token_identities 的无 ``file=`` 前缀形态刻意不同——对账两侧同键形才可比。
_TOKEN_FAMILY: Final = "creation_tokens"


def _token_identity_set(entries: object) -> set[str]:
    """creation_tokens 条目族 → 复合身份集（无 file/token 对的条目不计，与门侧同口径）。"""
    out: set[str] = set()
    if not isinstance(entries, list):
        return out
    for entry in entries:
        if isinstance(entry, list):
            pairs = dict(entry)
        elif isinstance(entry, dict):
            pairs = entry
        else:
            continue
        file_v = pairs.get("file")
        token_v = pairs.get("token")
        if isinstance(file_v, str) and isinstance(token_v, (str, int, float)):
            out.add(f"file={file_v}|token={token_v}")
    return out


def token_two_way_diff(snapshot: ProjectionSnapshot, disk_text: str) -> dict[str, object]:
    """PG 侧（本次快照）与盘上 YAML 的 creation_tokens 双向差集（纯函数，零写、零抛）。

    Returns:
        dict 含 pg_only/disk_only（排序样本截 20）、pg_only_n/disk_only_n、
        comparable、reason。**comparable=False 时绝不把"量不了"报成"零差异"**
        （静默降级与未触发同形＝已在册假绿族）。
    """
    base: dict[str, object] = {"pg_only": [], "disk_only": [], "pg_only_n": 0, "disk_only_n": 0}
    sec = snapshot.section(_TOKEN_FAMILY)
    if sec is None:
        return {**base, "comparable": False, "reason": f"快照无 {_TOKEN_FAMILY} 族（本册不管 token 条目）"}
    if not (disk_text or "").strip():
        return {**base, "comparable": False, "reason": "盘上无正文（新册/空册），无对面可比"}
    try:
        disk_snap = snapshot_from_yaml(
            disk_text, registry_id=snapshot.registry_id, physical_path=snapshot.physical_path
        )
    except Exception as exc:  # noqa: BLE001 — 盘上字节不可解析本身就是要说出来的不一致
        return {
            **base,
            "comparable": False,
            "reason": f"盘上 YAML 不可解析（{type(exc).__name__}: {str(exc)[:120]}）",
        }
    pg_ids = _token_identity_set(sec.entries)
    dsec = disk_snap.section(_TOKEN_FAMILY)
    disk_ids = _token_identity_set(dsec.entries) if dsec is not None else set()
    pg_only = sorted(pg_ids - disk_ids)
    disk_only = sorted(disk_ids - pg_ids)
    return {
        "pg_only": pg_only[:20],
        "disk_only": disk_only[:20],
        "pg_only_n": len(pg_only),
        "disk_only_n": len(disk_only),
        "comparable": True,
        "reason": f"PG 侧 {len(pg_ids)} 条／盘上 {len(disk_ids)} 条复合身份",
    }


def _warn_token_two_way_diff(snapshot: ProjectionSnapshot, disk_text: str, physical_path: str) -> None:
    """render/check 前的双向一致性告警（观测件：只说话，永不影响判定与写盘）。"""
    try:
        diff = token_two_way_diff(snapshot, disk_text)
    except Exception:  # noqa: BLE001 — 观测件任何故障都不外抛（投影器绝不阻塞调用方）
        logger.debug("token 双向对账探针异常（忽略）", exc_info=True)
        return
    if not diff.get("comparable"):
        logger.debug("token 双向对账不可比：%s (%s)", physical_path, diff.get("reason"))
        return
    pg_n = int(diff["pg_only_n"] or 0)
    disk_n = int(diff["disk_only_n"] or 0)
    if not (pg_n or disk_n):
        return
    logger.warning(
        "投影双向一致性告警 %s：PG 有行而盘上无=%d 条（滞后，本次 render 补上，样本=%s）；"
        "盘上有行而 PG 无/非 active=%d 条（直写遗留，本次 render 剔除——落盘后若被 "
        "REGISTRY-YAML-PARSE 按『相对 HEAD 少 N 条』拦袋即此形态，样本=%s）",
        physical_path,
        pg_n,
        list(diff["pg_only"])[:3],
        disk_n,
        list(diff["disk_only"])[:3],
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

    # 双向一致性告警（st-maint7-20261014 P0-2② 扩面，统筹 2026-10-14 增补第 2 条）：
    # 只告警零阻塞——投影器的铁律是"绝不阻塞任何调用方"，本段不改象限、不改写盘。
    _warn_token_two_way_diff(snapshot, disk_text, phys)

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
