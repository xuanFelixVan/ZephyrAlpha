# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_heritage
# [MODULE] tests.ai_layer.heritage.test_heritage_store
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.heritage.store; zephyr.ai_layer.heritage.policy
# [CONSUMERS] pytest tests/ai_layer/heritage/test_heritage_store.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 登记闸纯判据零 DB 全枚举（DESIGN §2.5 五类拒收样本逐一断言机读拒因）;
#              DB 用例只写 ai_heritage_test_* 临时 schema（session 末 DROP），禁写生产 ai_heritage;
#              PG 不可达=skip 而非假绿；状态机全流转枚举含非法路径；零物理删除=源码扫描断言无 DELETE FROM;
#              l4_hash_lookup/domain_lookup 注入（判据一致性/词表校验不依赖生产 L2/L4 库）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L7_heredity/DESIGN.md §2.5（登记闸验收真源）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RegistrationRefused 拒因可机读断言；非法流转 RuntimeError fail-closed
# [TESTS] tests/ai_layer/heritage/test_heritage_store.py
# [TTL] permanent
"""test_heritage_store - 登记闸/状态机/hit 聚合验收（DESIGN 施工项 2）。"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import pytest

from zephyr.ai_layer.heritage.policy import load_policy
from zephyr.ai_layer.heritage.store import (
    HeritageDraft,
    HeritageStore,
    RegistrationRefused,
    build_text_norm,
    check_status_transition,
    recipe_delta_chars,
    validate_draft,
)

STAMP = datetime(2026, 9, 23, 12, 0, 0, tzinfo=UTC)


def _pg_reachable() -> bool:
    """真连一次 PG；任何异常=不可达（据此 skip，而非假绿）。"""
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        get_depgraph_pg_connection(read_only=True).cursor().execute("SELECT 1")
        return True
    except Exception:  # noqa: BLE001——可达性探测面，任何异常一律判不可达
        return False


needs_pg = pytest.mark.skipif(not _pg_reachable(), reason="PostgreSQL 不可达（skip 而非假绿）")


def _defect_draft(**overrides: object) -> HeritageDraft:
    base: dict[str, object] = {
        "entry_kind": "defect",
        "title": "pathspec bug 复发防护",
        "plain_zh": "工单收尾路径参数写错导致改动落错目录，登记签名与配方防再犯",
        "domain_id": "tooling",
        "source_kind": "work_order",
        "source_ref": "WO-20260917-001",
        "root_cause": "调用方按位置传参把 pathspec 传成了 path 语义",
        "signature": r"pathspec=.*\n.*unexpected positional arg",
        "recipe": "改关键字传参+补 smoke：对 git add 调用点逐一核对 pathspec 语义并加实单验证",
        "pattern_norm": "pathspec_semantic_mixup",
        "affected_surfaces": ("src/zephyr/gov_enforcement/bridge.py",),
        "tool_id": "git-cli",
        "scene": "python 子进程调用 git add -- <pathspec>",
    }
    base.update(overrides)
    return HeritageDraft(**base)  # type: ignore[arg-type]


def _elite_draft(**overrides: object) -> HeritageDraft:
    base: dict[str, object] = {
        "entry_kind": "elite",
        "title": "双窗判据胜者档案",
        "plain_zh": " challengera 在双窗实测以显著性优势胜出，档案供组合素材与祖先分支",
        "domain_id": "trading_algo",
        "source_kind": "l6_switch",
        "source_ref": "SW-20260920-001",
        "surface": "code_module",
        "winner_ref": "MOD-ALPHA-001",
        "loser_ref": "MOD-ALPHA-000",
        "diff_summary": "胜者把信号确认窗从固定 3 根改为波动自适应，回撤更小而胜率不降，双窗成绩稳定",
        "evidence_ref": "EX-20260918-abc",
        "mechanism_family": "prediction",
    }
    base.update(overrides)
    return HeritageDraft(**base)  # type: ignore[arg-type]


def _criteria_draft(**overrides: object) -> HeritageDraft:
    base: dict[str, object] = {
        "entry_kind": "criteria",
        "title": "双窗判据快照",
        "plain_zh": "当时为什么算它赢：OOS 衰减小于 0.5 且置换检验显著，判据冻结哈希随卡",
        "domain_id": "trading_algo",
        "source_kind": "l4_experiment",
        "source_ref": "EX-20260918-abc",
        "experiment_id": "EX-20260918-abc",
        "criteria_hash": "a" * 64,
        "venue": "dual_run",
        "verdict": "win",
        "why_win": "OOS 衰减 0.3<0.5 且 McNemar p=0.01 显著，判据口径冻结于实验卡哈希一致",
    }
    base.update(overrides)
    return HeritageDraft(**base)  # type: ignore[arg-type]


# ---------------------------------------------------------------- 纯判据（零 DB）


def test_gate_missing_source_anchor() -> None:
    policy = load_policy()
    with pytest.raises(RegistrationRefused) as ei:
        validate_draft(_defect_draft(source_ref=""), policy)
    assert ei.value.reason == "missing_source_anchor"
    with pytest.raises(RegistrationRefused) as ei:
        validate_draft(_defect_draft(source_ref="http://bad"), policy)
    assert ei.value.reason == "bad_source_ref_format"


def test_gate_placeholder_plain_zh() -> None:
    policy = load_policy()
    for bad in ("待填", "略", "太短"):
        with pytest.raises(RegistrationRefused) as ei:
            validate_draft(_defect_draft(plain_zh=bad), policy)
        assert ei.value.reason == "placeholder_plain_zh"


def test_gate_self_dedup_rejects_duplicate_sha() -> None:
    """闸4 自查重（精确层）：同文重复登记在 DB 层拒（纯判据层只验可计算性）。"""
    draft = _defect_draft()
    text_norm = build_text_norm(draft)
    sha = hashlib.sha256(text_norm.encode("utf-8")).hexdigest()
    assert len(sha) == 64


def test_gate_criteria_hash_mismatch_via_lookup() -> None:
    """闸5 判据一致性：与 L4 卡哈希不一致=拒（注入 lookup，DESIGN §2.5）。"""
    store = HeritageStore(
        "ai_heritage_test_gate",
        l4_hash_lookup=lambda exp: ("b" * 64 if exp == "EX-20260918-abc" else None),
        domain_lookup=lambda domain: True,
    )
    with pytest.raises(RegistrationRefused) as ei:
        store.verify_criteria_hash(_criteria_draft())
    assert ei.value.reason == "hash_mismatch"
    with pytest.raises(RegistrationRefused) as ei:
        store.verify_criteria_hash(_criteria_draft(experiment_id="EX-NOT-EXIST"))
    assert ei.value.reason == "experiment_card_not_found"


def test_gate_l4_unavailable_fail_closed() -> None:
    from zephyr.ai_layer.heritage.store import L4StoreUnavailable

    def down(exp: str) -> str:
        raise L4StoreUnavailable("ai_compare down")

    store = HeritageStore(
        "ai_heritage_test_gate",
        l4_hash_lookup=down,
        domain_lookup=lambda domain: True,
    )
    with pytest.raises(RegistrationRefused) as ei:
        store.verify_criteria_hash(_criteria_draft())
    assert ei.value.reason == "l4_unavailable"


def test_gate_no_real_case_for_defect() -> None:
    policy = load_policy()
    with pytest.raises(RegistrationRefused) as ei:
        validate_draft(_defect_draft(source_kind="manual"), policy)
    assert ei.value.reason == "no_real_case"


def test_gate_recipe_repeats_root_cause() -> None:
    policy = load_policy()
    with pytest.raises(RegistrationRefused) as ei:
        validate_draft(_defect_draft(recipe="调用方按位置传参把 pathspec 传成了 path 语义"), policy)
    assert ei.value.reason == "recipe_repeats_root_cause"
    assert recipe_delta_chars("abc", "abcdef") >= 0


def test_gate_tool_fields_missing_for_tooling_domain() -> None:
    policy = load_policy()
    with pytest.raises(RegistrationRefused) as ei:
        validate_draft(_defect_draft(tool_id=None), policy)
    assert ei.value.reason == "tool_fields_missing"


def test_gate_bad_pattern_slug() -> None:
    policy = load_policy()
    with pytest.raises(RegistrationRefused) as ei:
        validate_draft(_defect_draft(pattern_norm="Bad Slug!"), policy)
    assert ei.value.reason == "bad_pattern_slug"


def test_gate_elite_and_criteria_completeness() -> None:
    policy = load_policy()
    with pytest.raises(RegistrationRefused) as ei:
        validate_draft(_elite_draft(diff_summary="太短"), policy)
    assert ei.value.reason == "incomplete"
    with pytest.raises(RegistrationRefused) as ei:
        validate_draft(_criteria_draft(criteria_hash="xyz"), policy)
    assert ei.value.reason == "incomplete"
    assert validate_draft(_elite_draft(), policy)
    assert validate_draft(_criteria_draft(), policy)


def test_status_machine_full_enumeration() -> None:
    assert check_status_transition("elite", "active", "archived") == (True, "demote:active->archived")
    assert check_status_transition("elite", "archived", "compressed")[0] is True
    assert check_status_transition("defect", "retired", "active")[0] is True, "un-retire 合法"
    assert check_status_transition("defect", "retired", "compressed")[0] is True
    for kind, current, target in (
        ("elite", "active", "compressed"),
        ("elite", "active", "retired"),
        ("defect", "active", "archived"),
        ("defect", "compressed", "active"),
        ("criteria", "active", "retired"),
        ("bogus", "active", "archived"),
    ):
        ok, why = check_status_transition(kind, current, target)
        assert not ok, why


def test_store_rejects_bad_schema_name() -> None:
    with pytest.raises(ValueError, match="schema 名不合规"):
        HeritageStore("pg_catalog")
    with pytest.raises(ValueError, match="schema 名不合规"):
        HeritageStore("")


# ---------------------------------------------------------------- DB（临时 schema）


def _store(heritage_schema: str, tmp_path: Path) -> HeritageStore:
    return HeritageStore(
        heritage_schema,
        state_dir=tmp_path / "state",
        domain_lookup=lambda domain: domain in {"tooling", "trading_algo", "governance"},
        l4_hash_lookup=lambda exp: "a" * 64 if exp == "EX-20260918-abc" else None,
    )


@needs_pg
def test_register_roundtrip_and_entry_id_sequence(heritage_schema: str, tmp_path: Path) -> None:
    store = _store(heritage_schema, tmp_path)
    eid1 = store.register(_defect_draft(), as_of=STAMP)
    eid2 = store.register(_defect_draft(title="第二例", root_cause="另一种根因结构", signature="sig-2",
                                        recipe="完全不同的修复配方内容长度超过差异线二十个字以上",
                                        pattern_norm="second_pattern_x", source_ref="WO-20260917-002"),
                          as_of=STAMP)
    assert eid1.startswith("HT-20260923-"), "entry_id 形态 HT-<yyyymmdd>-<NNN>"
    seq1 = int(eid1.rsplit("-", 1)[-1])
    assert eid2 == f"HT-20260923-{seq1 + 1:03d}", "当日序号递增"
    entry = store.get(eid1)
    assert entry is not None and entry["status"] == "active" and entry["hit_count"] == 0
    assert store.dirty_since() is not None, "登记后置快照脏标记"


@needs_pg
def test_register_duplicate_sha_rejected(heritage_schema: str, tmp_path: Path) -> None:
    store = _store(heritage_schema, tmp_path)
    eid = store.register(_defect_draft(), as_of=STAMP)
    with pytest.raises(RegistrationRefused) as ei:
        store.register(_defect_draft(), as_of=STAMP)
    assert ei.value.reason == "duplicate_of" and ei.value.detail == eid


@needs_pg
def test_transition_machine_and_compressed_queryable(heritage_schema: str, tmp_path: Path) -> None:
    store = _store(heritage_schema, tmp_path)
    eid = store.register(_defect_draft(), as_of=STAMP)
    assert store.transition_status(eid, "retired", note="faces dead") == "demote:active->retired"
    assert store.transition_status(eid, "active", note="复发 un-retire") == "demote:retired->active"
    assert store.transition_status(eid, "retired") .startswith("demote")
    assert store.transition_status(eid, "compressed").startswith("demote")
    with pytest.raises(RuntimeError, match="compressed_is_terminal"):
        store.transition_status(eid, "active")
    entry = store.get(eid)
    assert entry is not None and entry["status"] == "compressed", "compressed 可反查（零物理删除）"
    with pytest.raises(RuntimeError, match="entry_not_found"):
        store.transition_status("HT-19990101-999", "active")


@needs_pg
def test_criteria_register_with_hash_match(heritage_schema: str, tmp_path: Path) -> None:
    store = _store(heritage_schema, tmp_path)
    eid = store.register(_criteria_draft(), as_of=STAMP)
    assert eid.startswith("HT-")
    assert store.status_of(eid) == "active"


@needs_pg
def test_hit_log_aggregation_monthly(heritage_schema: str, tmp_path: Path) -> None:
    store = _store(heritage_schema, tmp_path)
    eid = store.register(_defect_draft(), as_of=STAMP)
    store.record_hit(eid, "dedup_hit", as_of=STAMP)
    store.record_hit(eid, "dispatch_hit", as_of=STAMP)
    store.record_hit("HT-20260923-404", "orphan", as_of=STAMP)
    summary = store.aggregate_hits_monthly(as_of=STAMP)
    assert summary == {"aggregated": 2}
    entry = store.get(eid)
    assert entry is not None and entry["hit_count"] == 2 and entry["last_hit_at"] is not None
    archive = tmp_path / "state" / "hit_counts-2026-09.jsonl"
    assert archive.exists(), "已处理流水轮转归档"
    assert not (tmp_path / "state" / "hit_counts.jsonl").exists(), "流水文件清空防重复聚合"


@needs_pg
def test_occurrence_increment_and_log(heritage_schema: str, tmp_path: Path) -> None:
    store = _store(heritage_schema, tmp_path)
    eid = store.register(_defect_draft(), as_of=STAMP)
    count = store.record_occurrence(eid, "CASE-2026-0917-001", as_of=STAMP)
    assert count == 2
    log_lines = (tmp_path / "state" / "occurrences.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(log_lines) == 1 and "CASE-2026-0917-001" in log_lines[0]


@needs_pg
def test_snapshot_faces_defect_and_elite_top3(heritage_schema: str, tmp_path: Path) -> None:
    store = _store(heritage_schema, tmp_path)
    store.register(_defect_draft(), as_of=STAMP)
    for i in range(4):
        store.register(
            _elite_draft(
                winner_ref=f"MOD-W-{i}",
                source_ref=f"SW-2026092{i}-001",
                title=f"胜者 {i}",
                score_summary={"score": 1.0 - i * 0.1},
                gen=1,
                mechanism_family="prediction",
            ),
            as_of=STAMP,
        )
    faces = store.snapshot_faces()
    assert len(faces["defect"]) >= 1
    assert all(r["ref_key"].startswith("HT:") for r in faces["elite"] + faces["defect"])
    assert len(faces["elite"]) <= 3, "精英入快照面=每格 top3"
