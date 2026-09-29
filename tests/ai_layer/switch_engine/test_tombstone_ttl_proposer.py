"""L6 S5「何时清」提案器测试：三判据逐一判别 + 未知保守 + 零删除断言。

零生产写：记录直接构造（不触 DB），产物落 tmp_path。
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml

from zephyr.ai_layer.switch_engine.tombstone_ttl_proposer import (
    VERDICT_ELIGIBLE,
    VERDICT_INDETERMINATE,
    VERDICT_NOT_TOMBSTONE,
    VERDICT_RETAIN,
    build_proposal,
    evaluate_record,
    policy_from_criteria,
    propose_from_store,
    write_proposal,
)
from zephyr.intelligence.switch_engine.switch_registry import SwitchRegistryRecord

AS_OF = date(2026, 9, 26)


def _policy() -> Any:
    return policy_from_criteria(
        {
            "criteria": {
                "tombstone": {
                    "ttl_windows": 2,
                    "ttl_months_equivalent_days": 30,
                    "git_tag_prefix": "tombstone/",
                    "git_tag_policy": "git_tag_never_deleted",
                }
            }
        }
    )


def _record(
    switch_id: str = "SW-20260101-demo",
    *,
    state: str = "tombstone",
    sealed_at: str = "2026-01-01T00:00:00+00:00",
    state_history: list[dict[str, Any]] | None = None,
) -> SwitchRegistryRecord:
    history = (
        state_history
        if state_history is not None
        else [
            {"state": "retired", "since": "2025-12-01T00:00:00+00:00"},
            {"state": "tombstone", "since": sealed_at, "from_state": "retired"},
        ]
    )
    return SwitchRegistryRecord(
        switch_id=switch_id,
        object_family="code_module",
        object_ref="zephyr.demo.retired_module",
        domain="D_GOVERNANCE",
        champion_ref="main",
        challenger_ref="session/st-demo",
        criteria_yaml_ref="config/switch_criteria.yaml",
        criteria_hash="0" * 64,
        state=state,
        state_history=history,
        tombstone={
            "sealed_at": sealed_at,
            "seal_ref": "seal-card-1",
            "seal_tag": "tombstone/zephyr.demo.retired_module/20260101",
            "failed_regime": "低波动 regime",
            "revival_conditions": ["regime_recurrence"],
            "ttl_deadline": "2026-03-02T00:00:00+00:00",
        },
    )


def test_policy_reads_yaml_not_hardcoded() -> None:
    policy = _policy()
    assert policy.ttl_windows == 2
    assert policy.ttl_days() == 60


def test_three_criteria_all_satisfied_is_eligible() -> None:
    result = evaluate_record(
        _record(),
        as_of=AS_OF,
        policy=_policy(),
        reverse_dep_resolver=lambda _r: 0,
    )
    assert result["verdict"] == VERDICT_ELIGIBLE
    assert result["blocking"] == []
    assert result["criteria"]["ttl_elapsed_days"] >= 60
    assert result["criteria"]["reverse_dependency_zero"] is True


def test_ttl_unsatisfied_retains() -> None:
    result = evaluate_record(
        _record(sealed_at="2026-09-01T00:00:00+00:00"),
        as_of=AS_OF,
        policy=_policy(),
        reverse_dep_resolver=lambda _r: 0,
    )
    assert result["verdict"] == VERDICT_RETAIN
    assert "criterion_ttl_unsatisfied" in result["blocking"]


def test_reverse_dependency_nonzero_retains() -> None:
    result = evaluate_record(
        _record(),
        as_of=AS_OF,
        policy=_policy(),
        reverse_dep_resolver=lambda _r: 3,
    )
    assert result["verdict"] == VERDICT_RETAIN
    assert "criterion_reverse_dependency_nonzero" in result["blocking"]


def test_unknown_reverse_dependency_is_conservative() -> None:
    result = evaluate_record(
        _record(),
        as_of=AS_OF,
        policy=_policy(),
        reverse_dep_resolver=lambda _r: None,
    )
    assert result["verdict"] == VERDICT_INDETERMINATE
    assert "criterion_reverse_dependency_unknown" in result["blocking"]


def test_revival_momentum_after_seal_retains() -> None:
    record = _record(
        state_history=[
            {"state": "tombstone", "since": "2026-01-01T00:00:00+00:00", "from_state": "retired"},
            {"state": "shadow", "since": "2026-05-01T00:00:00+00:00", "from_state": "tombstone"},
        ]
    )
    result = evaluate_record(record, as_of=AS_OF, policy=_policy(), reverse_dep_resolver=lambda _r: 0)
    assert result["verdict"] == VERDICT_RETAIN
    assert "criterion_revival_momentum_present" in result["blocking"]
    assert result["criteria"]["revival_momentum"]["revival_moves_after_seal"] == 1


def test_non_tombstone_out_of_scope() -> None:
    result = evaluate_record(
        _record(state="champion"),
        as_of=AS_OF,
        policy=_policy(),
        reverse_dep_resolver=lambda _r: 0,
    )
    assert result["verdict"] == VERDICT_NOT_TOMBSTONE


def test_proposal_counts_and_protection_fields(tmp_path: Path) -> None:
    payload = build_proposal(
        [
            _record("SW-20260101-a"),
            _record("SW-20260801-b", sealed_at="2026-08-01T00:00:00+00:00"),
            _record("SW-20251201-c", sealed_at="2025-12-01T00:00:00+00:00"),
        ],
        as_of=AS_OF,
        policy=_policy(),
        reverse_dep_resolver=lambda r: 0 if r.switch_id.endswith("c") else 1,
        extra_tags=["tombstone/zephyr.demo.retired_module/20260101"],
    )
    counts = payload["counts"]
    assert payload["execution"]["actions_executed"] == 0
    assert payload["execution"]["delete_api_present_in_module"] is False
    assert counts["records_scanned"] == 3
    assert counts["eligible_for_owner_review"] == 1
    assert counts["retain"] == 2
    assert sum(payload["by_verdict"].values()) == counts["records_scanned"]
    assert payload["sealed_tags_never_deleted"]
    assert all(
        "git_tag_never_deleted" in c["protected_assets"]
        for c in payload["candidates"]
        if c["verdict"] == VERDICT_ELIGIBLE
    )

    out = write_proposal(payload, tmp_path / "proposal.yaml")
    reloaded = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert reloaded["counts"] == counts
    assert reloaded["status"] == "dry_run_only"


def test_module_exposes_no_delete_untag_api() -> None:
    """提案器不得带任何删除/去标能力（破坏性动作留 Owner 门）。"""
    from zephyr.ai_layer.switch_engine import tombstone_ttl_proposer as module

    banned = [
        name
        for name in dir(module)
        if any(token in name.lower() for token in ("delete", "remove", "untag", "drop", "purge"))
    ]
    assert banned == []


def test_propose_from_store_degrades_without_inventing_candidates(tmp_path: Path) -> None:
    class BrokenStore:
        def ensure_schema(self) -> None:
            raise RuntimeError("供数不可用（模拟）")

    payload = propose_from_store(
        BrokenStore(),
        as_of=AS_OF,
        policy=_policy(),
        out_path=tmp_path / "degraded.yaml",
    )
    assert payload["data_source"]["status"] == "unavailable"
    assert payload["counts"]["records_scanned"] == 0
    assert payload["counts"]["eligible_for_owner_review"] == 0
    assert (tmp_path / "degraded.yaml").is_file()


def test_no_db_read_branch_never_touches_store(tmp_path: Path) -> None:
    """--no-db-read：零连接共享 governance.db（车道避让），且不得凭记忆造候选。"""

    class ExplodingStore:
        def ensure_schema(self) -> None:
            raise AssertionError("read_db=False 不得触库")

        def list_by_state(self, state: str) -> list[SwitchRegistryRecord]:
            raise AssertionError("read_db=False 不得触库")

    payload = propose_from_store(
        ExplodingStore(),
        as_of=AS_OF,
        policy=_policy(),
        out_path=tmp_path / "skipped.yaml",
        read_db=False,
    )
    assert payload["data_source"]["status"] == "skipped_by_flag"
    assert payload["counts"]["records_scanned"] == 0
    assert payload["execution"]["actions_executed"] == 0
    assert (tmp_path / "skipped.yaml").is_file()


def test_package_static_edge_exposes_proposer() -> None:
    """接线验收（chief3 令零消费→接线）：包公共面静态可见边暴露提案器（动态派发可发现）。"""
    import zephyr.ai_layer.switch_engine as pkg

    assert "tombstone_ttl_proposer" in pkg.__all__
    assert hasattr(pkg, "tombstone_ttl_proposer")
    assert callable(pkg.tombstone_ttl_proposer.propose_from_store)
    assert callable(pkg.tombstone_ttl_proposer.main)
