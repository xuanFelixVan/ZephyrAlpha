# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §l6_switch_engine
# [MODULE] zephyr.ai_layer.switch_engine.tombstone_ttl_proposer
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.intelligence.switch_engine.switch_registry (SwitchRegistryRecord/Store);
#                zephyr.intelligence.switch_engine.criteria (load_criteria——tombstone 判据真源)
# [CONSUMERS] 月度体检窗/夜间收口班（CLI 手跑）；Owner 净删门提案面（proposal YAML 人读+机读）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 只提案不执行（L6-#2 避让的接棒件）：本模块**零删除 API**——无 untag、无 registry
#              行删除、无文件删除、无 DB UPDATE；输出恒 actions_executed=0；
#              三判据缺一即"保留"（fail-closed：反向依赖/复活动量未知=不判可清）；
#              git tag 永不清（DESIGN §②-D）——tag 只随提案披露不作清理对象；
#              注册表净删=high human_gate（宪法 §5），本件产出仅为 Owner 门输入；
#              判据数值不在本件复制——ttl_windows/月度窗天数一律读 config/switch_criteria.yaml
#              （RULE-SSOT：阈值真源=YAML，本件只读）；生成器禁系统时钟——as_of 必填
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L6_ab_switch/DESIGN.md §②-D（清理条件 TTL）/
#                 §④-S5（墓碑管理器·TTL 清理提案）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] as_of 缺失/非法格式->ValueError；判据 YAML 缺失->SwitchCriteriaError（透传，
#                  不静默兜底）；reverse_dep_count=None->verdict=indeterminate（保守保留非报错）
# [TESTS] tests/ai_layer/switch_engine/test_tombstone_ttl_proposer.py（可清项判据三全/
#         反向依赖>0 保留/未知保留/期内复活动量保留/TTL 未满保留/tag 永不清入保护面/
#         产物零删除动作断言）
# [TTL] permanent
"""tombstone_ttl_proposer — 墓碑 TTL 清理**提案**生成器（L6 施工项 S5 的"何时清"半边）。

真源：docs/_working/ai_layer_vision/L6_ab_switch/DESIGN.md §②-D「清理条件（TTL）」+
§④-S5（墓碑管理器：封存登记/复活复检工单/**TTL 清理提案（Owner 门）**）
注：交接书把本项记为"L6 DESIGN §S6"，S6 实为审批分流器；墓碑 TTL 判据真源在 §②-D+§④-S5
（同卡 §⑤ 待 Owner 第 2 条），本件按该真源施工，锚点差异如实登记。

三判据（缺一即保留，全仓 grep 实测无第四条件）：
  ① TTL 满——封存日 + ``tombstone.ttl_windows`` × ``tombstone_monthly_window_days`` ≤ as_of；
  ② depgraph 反向依赖 = 0（由注入式 resolver 供给；未知=None→ 保守 indeterminate）；
  ③ 期间零复活**动量**——封存后不得有 ``tombstone->shadow`` 迁移，且不得留有未结清复活工单
     （revival_ticket 只产 JSON 工单不回写 state_history，故 state_history 单独判据不足——
     本件把"复活触发落痕缺口"如实登记为 partial 态，接 L1 regime 门接线批补痕）。

红线：清理动作属破坏性操作（注册表净删=high human_gate）——夜间一律只出清单，
本模块不接任何执行器，产物里 ``actions_executed`` 恒 0。生成器禁 datetime.now()/time.time()
（RULE-SCHEMA-TZ），as_of 由调用方显式传入。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 墓碑清单与判据真源
#   fields: switch_registry 墓碑记录；config/switch_criteria.yaml（ttl_windows/月度窗天数）
#   code: SwitchRegistryStore/load_criteria
# 层: 算法
# - id: A1
#   name_zh: 三判据合议出提案（缺一即保留）
#   name_en: evaluate_record/build_proposal/propose_from_store
#   intro: TTL 满+反向依赖为零+期内零复活动量方可入提案；判据未知=indeterminate 保守保留
#   inputs: I1
#   outputs: O1
# 层: 输出
# - id: O1
#   name: 提案 YAML（人读+机读，零删除动作）
#   fields: actions_executed 恒 0；tag 只披露不清理
#   code: write_proposal/CLI main
#   downstream: Owner 注册表净删 high human_gate（宪法 §5）
# 边: I1 --> A1 ; A1 --> O1
# [/ALGO_FLOW]
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.intelligence.switch_engine.criteria import load_criteria
from zephyr.intelligence.switch_engine.switch_registry import SwitchRegistryRecord

SCHEMA_VERSION: Final[str] = "1.0.0"
DEFAULT_MONTHLY_WINDOW_DAYS: Final[int] = 30
VERDICT_ELIGIBLE: Final[str] = "eligible_for_owner_review"
VERDICT_RETAIN: Final[str] = "retain"
VERDICT_INDETERMINATE: Final[str] = "retain_indeterminate"
VERDICT_NOT_TOMBSTONE: Final[str] = "out_of_scope_not_tombstone"
CLEANUP_PROHIBITED: Final[str] = "git_tag_never_deleted"
GIT_TAG_PREFIX: Final[str] = "tombstone/"

#: 复活动量口径：封存后视为"有动量"的历史态（tombstone->shadow 复检 = 复活触发）
_REVIVAL_FROM_STATES: Final[frozenset[str]] = frozenset({"tombstone"})
_REVIVAL_TO_STATES: Final[frozenset[str]] = frozenset({"shadow"})

ReverseDepResolver = Callable[[SwitchRegistryRecord], int | None]

DEFAULT_OUT: Final[Path] = (
    Path("docs/_working/ai_layer_vision/closure_wave2") / "l6_tombstone_ttl_cleanup_proposal.yaml"
)


@dataclass(frozen=True)
class TombstonePolicy:
    """判据参数（一律读 config/switch_criteria.yaml，禁本件硬编码阈值）。"""

    ttl_windows: int
    monthly_window_days: int
    git_tag_prefix: str

    def ttl_days(self) -> int:
        return self.ttl_windows * self.monthly_window_days


def policy_from_criteria(criteria: dict[str, Any] | None = None) -> TombstonePolicy:
    """从判据 YAML 取墓碑段（缺段/缺键 fail-closed 抛错，不静默回退硬编码）。"""
    payload = criteria if criteria is not None else load_criteria()
    section = (payload.get("criteria") or {}).get("tombstone")
    if not isinstance(section, dict):
        raise ValueError("switch_criteria.yaml 缺 criteria.tombstone 段（fail-closed 不出提案）")
    return TombstonePolicy(
        ttl_windows=int(section["ttl_windows"]),
        monthly_window_days=int(section.get("ttl_months_equivalent_days", DEFAULT_MONTHLY_WINDOW_DAYS)),
        git_tag_prefix=str(section.get("git_tag_prefix", GIT_TAG_PREFIX)),
    )


def _parse_instant(raw: str) -> date | None:
    """ISO 串 -> date（兼容 datetime/date/带时区后缀，取日期部分）。"""
    if not raw:
        return None
    text = str(raw).strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        pass
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _revival_momentum(record: SwitchRegistryRecord, sealed_on: date | None) -> dict[str, Any]:
    """封存后是否出现复活态迁移（tombstone->shadow）+ 落痕缺口披露。"""
    moves: list[dict[str, Any]] = []
    for hop in record.state_history:
        frm = str(hop.get("from_state") or hop.get("from") or "")
        to = str(hop.get("state") or hop.get("to_state") or "")
        if frm in _REVIVAL_FROM_STATES and to in _REVIVAL_TO_STATES:
            at = _parse_instant(str(hop.get("since") or hop.get("at") or ""))
            if sealed_on is None or (at is not None and at >= sealed_on):
                moves.append({"from": frm, "to": to, "since": str(hop.get("since", ""))})
    return {
        "revival_moves_after_seal": len(moves),
        "evidence": moves,
        "state_history_only": True,
        "revival_ticket_ledger_gap": (
            "复活工单（tombstone_manager.revival_ticket）只产 JSON 不回写 state_history，"
            "故'零复活动量'仅在 state_history 层可判——工单台账接痕属 L1 regime 门接线批"
            "（L6-#4 待接），未接前本判据记 partial"
        ),
    }


def evaluate_record(
    record: SwitchRegistryRecord,
    *,
    as_of: date,
    policy: TombstonePolicy,
    reverse_dep_resolver: ReverseDepResolver | None = None,
) -> dict[str, Any]:
    """单条 tombstone 记录 -> 三判据结论（只判不清）。"""
    tombstone = dict(record.tombstone or {})
    sealed_on = _parse_instant(str(tombstone.get("sealed_at", "")))
    ttl_days = policy.ttl_days()

    if record.state != "tombstone":
        return {
            "switch_id": record.switch_id,
            "object_ref": record.object_ref,
            "state": record.state,
            "verdict": VERDICT_NOT_TOMBSTONE,
            "criteria": {},
            "blocking": ["记录非 tombstone 态，不入清理提案面"],
        }

    criteria: dict[str, Any] = {
        "ttl_windows_required": policy.ttl_windows,
        "monthly_window_days": policy.monthly_window_days,
        "ttl_days_required": ttl_days,
        "sealed_at": str(tombstone.get("sealed_at", "")),
        "ttl_elapsed_days": (as_of - sealed_on).days if sealed_on else None,
        "ttl_satisfied": bool(sealed_on and (as_of - sealed_on).days >= ttl_days),
    }
    blocking: list[str] = []
    if not criteria["ttl_satisfied"]:
        blocking.append("criterion_ttl_unsatisfied")

    deps: int | None = reverse_dep_resolver(record) if reverse_dep_resolver else None
    criteria["reverse_dependency_count"] = deps
    criteria["reverse_dependency_zero"] = deps == 0
    if deps is None:
        blocking.append("criterion_reverse_dependency_unknown")
    elif deps != 0:
        blocking.append("criterion_reverse_dependency_nonzero")

    momentum = _revival_momentum(record, sealed_on)
    criteria["revival_momentum"] = momentum
    if momentum["revival_moves_after_seal"] > 0:
        blocking.append("criterion_revival_momentum_present")

    if blocking and "criterion_reverse_dependency_unknown" in blocking:
        verdict = VERDICT_INDETERMINATE
    elif blocking:
        verdict = VERDICT_RETAIN
    else:
        verdict = VERDICT_ELIGIBLE

    return {
        "switch_id": record.switch_id,
        "object_ref": record.object_ref,
        "object_family": record.object_family,
        "domain": record.domain,
        "state": record.state,
        "seal_tag": str(tombstone.get("seal_tag", "")),
        "failed_regime": str(tombstone.get("failed_regime", "")),
        "revival_conditions": list(tombstone.get("revival_conditions", [])),
        "criteria": criteria,
        "verdict": verdict,
        "blocking": blocking,
        "protected_assets": [CLEANUP_PROHIBITED],
        "note": "eligible 仅=可进 Owner 净删门清单，绝不自动执行",
    }


def _verdict_of(result: dict[str, Any]) -> str:
    return str(result.get("verdict", VERDICT_RETAIN))


def build_proposal(
    records: Sequence[SwitchRegistryRecord],
    *,
    as_of: date,
    policy: TombstonePolicy,
    reverse_dep_resolver: ReverseDepResolver | None = None,
    extra_tags: Sequence[str] = (),
) -> dict[str, Any]:
    """全量 tombstone 行 -> 提案 payload（计数一律字段化，禁散文写死）。"""
    results = [
        evaluate_record(
            record,
            as_of=as_of,
            policy=policy,
            reverse_dep_resolver=reverse_dep_resolver,
        )
        for record in records
    ]
    by_verdict: dict[str, int] = {}
    for result in results:
        by_verdict[_verdict_of(result)] = by_verdict.get(_verdict_of(result), 0) + 1

    seal_tags = sorted({r["seal_tag"] for r in results if r.get("seal_tag")} | {t for t in extra_tags if t})
    blocking_reasons: dict[str, int] = {}
    for result in results:
        for reason in result.get("blocking", []):
            blocking_reasons[reason] = blocking_reasons.get(reason, 0) + 1

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_by": "zephyr.ai_layer.switch_engine.tombstone_ttl_proposer",
        "as_of": as_of.isoformat(),
        "status": "dry_run_only",
        "execution": {
            "actions_executed": 0,
            "delete_api_present_in_module": False,
            "note": "清理动作=注册表净删 high human_gate（宪法 §5）——夜间一律只出清单；本件为 Owner 门输入，非执行指令",
        },
        "truth_source": {
            "design": "docs/_working/ai_layer_vision/L6_ab_switch/DESIGN.md §②-D 清理条件（TTL）+ §④-S5 TTL 清理提案",
            "criteria_config": "config/switch_criteria.yaml criteria.tombstone（ttl_windows /"
            " git_tag_policy / revival_route 只读消费）",
            "handoff_item": "Owner 2026-09-26 已批项 #9，见"
            " docs/_working/ai_layer_vision/HANDOFF_st_ailayer_final.md §一",
            "anchor_discrepancy": "交接书作'L6 DESIGN §S6'，实核 §④-S6=审批分流器；墓碑 TTL 判据"
            "真源=§②-D+§④-S5（同卡 §⑤ 待 Owner 第 2 条）——按实测锚点施工",
        },
        "criteria": [
            {
                "id": "ttl_elapsed",
                "rule": f"tombstone 满 {policy.ttl_windows} 个月度体检窗（={policy.ttl_days()} 天，按窗口日换算）",
            },
            {"id": "reverse_dependency_zero", "rule": "depgraph 反向依赖=0（未知按保守不判可清）"},
            {"id": "revival_silence", "rule": "封存期零复活触发（tombstone->shadow 迁移即动量）"},
        ],
        "protection_rules": [
            {
                "asset": CLEANUP_PROHIBITED,
                "rule": "git tag 永不清（DESIGN §②-D + switch_criteria.tombstone.git_tag_policy）",
            },
            {
                "asset": "registry_deprecated_chain",
                "rule": "deprecated 链不删（墓碑合并法）——净删行需 Owner 裁，本件仅列清单",
            },
        ],
        "counts": {
            "records_scanned": len(results),
            "eligible_for_owner_review": by_verdict.get(VERDICT_ELIGIBLE, 0),
            "retain": by_verdict.get(VERDICT_RETAIN, 0),
            "retain_indeterminate": by_verdict.get(VERDICT_INDETERMINATE, 0),
            "out_of_scope_not_tombstone": by_verdict.get(VERDICT_NOT_TOMBSTONE, 0),
            "seal_tags_listed": len(seal_tags),
            "distinct_blocking_reasons": len(blocking_reasons),
        },
        "by_verdict": dict(sorted(by_verdict.items())),
        "blocking_reason_counts": dict(sorted(blocking_reasons.items())),
        "candidates": sorted(results, key=lambda r: str(r.get("switch_id", ""))),
        "sealed_tags_never_deleted": seal_tags,
    }


def write_proposal(payload: dict[str, Any], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )
    return out_path


def propose_from_store(
    store: Any,  # noqa: any-abuse -- 注入式 duck-type 仓（SwitchRegistryStore 协议面，避免过度抽象）
    *,
    as_of: date,
    policy: TombstonePolicy | None = None,
    reverse_dep_resolver: ReverseDepResolver | None = None,
    out_path: Path | None = None,
    read_db: bool = True,
) -> dict[str, Any]:
    """读 switch_registry tombstone 行（只读）出提案。

    ``read_db=False``=完全不触库（车道/夜跑避让共享 governance.db 用），产空清单并如实标 skipped；
    供数不可用同样返回 degraded 标记——禁凭记忆造候选。
    """
    resolved_policy = policy or policy_from_criteria()
    if not read_db:
        payload = build_proposal([], as_of=as_of, policy=resolved_policy)
        payload["data_source"] = {
            "kind": "switch_registry",
            "status": "skipped_by_flag",
            "note": "--no-db-read：本进程零连接共享 governance.db（避让车道/生产写路径），"
            "候选恒空——非'无墓碑'结论，真判读须由授权宿主实跑",
        }
        if out_path is not None:
            write_proposal(payload, out_path)
        return payload

    try:
        store.ensure_schema()
        records = store.list_by_state("tombstone")
    except Exception as exc:  # noqa: BLE001 - 供数不可用属预期分支，只登记不猜测
        degraded = build_proposal([], as_of=as_of, policy=resolved_policy)
        degraded["data_source"] = {
            "kind": "switch_registry",
            "status": "unavailable",
            "error": f"{type(exc).__name__}: {exc}",
            "note": "读不到供数=空清单+如实报红，禁凭记忆造候选",
        }
        if out_path is not None:
            write_proposal(degraded, out_path)
        return degraded

    payload = build_proposal(
        records,
        as_of=as_of,
        policy=resolved_policy,
        reverse_dep_resolver=reverse_dep_resolver,
    )
    payload["data_source"] = {"kind": "switch_registry", "status": "ok", "records_read": len(records)}
    if out_path is not None:
        write_proposal(payload, out_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="墓碑 TTL 清理**提案**生成器（dry-run，零删除）")
    parser.add_argument("--as-of", required=True, help="评估基准日 YYYY-MM-DD（禁取系统时间）")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="提案 YAML 输出路径")
    parser.add_argument(
        "--no-db-read", action="store_true", help="零连接共享 governance.db（车道避让/纯模板跑），产空清单并标 skipped"
    )
    args = parser.parse_args(argv)

    as_of = date.fromisoformat(args.as_of)
    policy = policy_from_criteria()
    from zephyr.intelligence.switch_engine.switch_registry import SwitchRegistryStore

    payload = propose_from_store(
        SwitchRegistryStore(),
        as_of=as_of,
        policy=policy,
        out_path=Path(args.out),
        read_db=not args.no_db_read,
    )
    counts = payload["counts"]
    print(
        f"扫描 {counts['records_scanned']} 行 / 可进 Owner 门 {counts['eligible_for_owner_review']}"
        f" / 保留 {counts['retain']} / 未知保守保留 {counts['retain_indeterminate']}"
        f" / 已执行删除 {payload['execution']['actions_executed']}"
    )
    print(f"提案：{args.out}")
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 清理提案器=月度体检窗人工 CLI 点火，只出提案不执行，非常驻自动任务
    raise SystemExit(main())
