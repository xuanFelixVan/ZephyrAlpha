# [BLUEPRINT] MOD-GOV-057 | docs/03_modules/_domain_gov_rule/standards_manager/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-GOV-057 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.gov_rule.test_standards_manager
# [TESTS] src/zephyr/gov_rule/standards_manager.py
"""MOD-GOV-057 单元测试：standards_manager 硬边界标准管理器。

蓝图验收（B1-00289/CAND-PC-002，C2 D-GOV-06）：硬边界目录四要素（编号/约束
语句/校验脚本锚点/违反响应）+ 元标准元数据 + 校验脚本注册回调挂接
gov_enforcement + 边界变更人工审批队列硬约束 + Fail-Closed 分支 + 确定性。
脚本注册/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.gov_rule.standards_manager",
    reason="standards_manager not importable",
)

from zephyr.gov_rule.standards_manager import (  # noqa: E402
    ApprovalDecision,
    BoundaryChangeRequest,
    ChangeKind,
    ChangeStatus,
    HardBoundary,
    StandardsManager,
    StandardsManagerError,
    ViolationResponse,
)

_T0 = datetime.datetime(2026, 8, 26, 17, 0, 0)


def _boundary(
    bid: str = "HB-001",
    text: str = "禁止越层 import",
    anchor: str = "scripts/gov/check_layer.py",
    response: ViolationResponse = ViolationResponse.BLOCK,
    meta: dict | None = None,
) -> HardBoundary:
    return HardBoundary(
        boundary_id=bid,
        constraint_text=text,
        script_anchor=anchor,
        violation_response=response,
        meta={"standard_id": "PS-STD-001", "owner": "owner"} if meta is None else meta,
    )


def _manager(registrar=None, seed: tuple = ()) -> StandardsManager:
    return StandardsManager(
        clock=lambda: _T0,
        script_registrar=registrar,
        initial_boundaries=seed,
    )


def _request(
    cid: str = "CHG-001",
    kind: ChangeKind = ChangeKind.ADD,
    bid: str = "HB-001",
    body: HardBoundary | None = None,
    by: str = "architect",
) -> BoundaryChangeRequest:
    return BoundaryChangeRequest(
        change_id=cid,
        kind=kind,
        boundary_id=bid,
        new_boundary=body,
        reason="治理升级",
        requested_by=by,
    )


def _approve(cid: str, by: str = "reviewer") -> ApprovalDecision:
    return ApprovalDecision(change_id=cid, approved=True, decided_by=by, note="同意")


# ──────────────────────────────────────────────────────────────────────────────
# 构造与种子目录
# ──────────────────────────────────────────────────────────────────────────────


class TestConstructor:
    def test_seed_catalog_sorted(self) -> None:
        mgr = _manager(seed=(_boundary("HB-002"), _boundary("HB-001")))
        assert [b.boundary_id for b in mgr.catalog()] == ["HB-001", "HB-002"]

    def test_seed_duplicate_rejected(self) -> None:
        with pytest.raises(StandardsManagerError):
            _manager(seed=(_boundary("HB-001"), _boundary("HB-001")))

    def test_seed_registers_scripts_in_order(self) -> None:
        calls: list[tuple[str, str]] = []
        mgr = _manager(registrar=lambda bid, anchor: calls.append((bid, anchor)), seed=(_boundary(),))
        assert calls == [("HB-001", "scripts/gov/check_layer.py")]
        assert mgr.get("HB-001").violation_response is ViolationResponse.BLOCK

    def test_seed_registrar_failure_raises(self) -> None:
        def boom(bid: str, anchor: str) -> None:
            raise RuntimeError("gate registry down")

        with pytest.raises(StandardsManagerError):
            _manager(registrar=boom, seed=(_boundary(),))

    def test_empty_catalog_by_default(self) -> None:
        mgr = _manager()
        assert mgr.catalog() == ()
        assert mgr.pending() == ()
        assert mgr.history() == ()


# ──────────────────────────────────────────────────────────────────────────────
# 四要素 + 元标准元数据校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestBoundaryValidation:
    def test_four_elements_and_meta_required(self) -> None:
        with pytest.raises(StandardsManagerError):
            _manager(seed=(_boundary(bid=""),))
        with pytest.raises(StandardsManagerError):
            _manager(seed=(_boundary(text=""),))
        with pytest.raises(StandardsManagerError):
            _manager(seed=(_boundary(anchor=""),))
        with pytest.raises(StandardsManagerError):
            _manager(seed=(_boundary(response="block"),))
        with pytest.raises(StandardsManagerError):
            _manager(seed=("not-a-boundary",))
        with pytest.raises(StandardsManagerError):
            _manager(seed=(_boundary(meta={"owner": 1}),))
        with pytest.raises(StandardsManagerError):
            _manager(seed=(_boundary(meta="ps-std"),))


# ──────────────────────────────────────────────────────────────────────────────
# 变更申请（人工审批队列硬约束）
# ──────────────────────────────────────────────────────────────────────────────


class TestProposeChange:
    def test_propose_add_goes_pending_not_catalog(self) -> None:
        mgr = _manager()
        cid = mgr.propose_change(_request(body=_boundary()))
        assert cid == "CHG-001"
        assert mgr.status_of(cid) is ChangeStatus.PENDING
        assert mgr.catalog() == ()  # 未批准不落目录
        assert len(mgr.pending()) == 1

    def test_propose_add_existing_rejected(self) -> None:
        mgr = _manager(seed=(_boundary(),))
        with pytest.raises(StandardsManagerError):
            mgr.propose_change(_request(body=_boundary()))

    def test_propose_update_or_retire_unknown_rejected(self) -> None:
        mgr = _manager()
        with pytest.raises(StandardsManagerError):
            mgr.propose_change(_request(kind=ChangeKind.UPDATE, body=_boundary()))
        with pytest.raises(StandardsManagerError):
            mgr.propose_change(_request(kind=ChangeKind.RETIRE))

    def test_propose_missing_body_rejected(self) -> None:
        mgr = _manager()
        with pytest.raises(StandardsManagerError):
            mgr.propose_change(_request(kind=ChangeKind.ADD))
        mgr_seed = _manager(seed=(_boundary(),))
        with pytest.raises(StandardsManagerError):
            mgr_seed.propose_change(_request(kind=ChangeKind.UPDATE))

    def test_propose_retire_with_body_rejected(self) -> None:
        mgr = _manager(seed=(_boundary(),))
        with pytest.raises(StandardsManagerError):
            mgr.propose_change(_request(kind=ChangeKind.RETIRE, body=_boundary()))

    def test_boundary_id_mismatch_rejected(self) -> None:
        mgr = _manager()
        with pytest.raises(StandardsManagerError):
            mgr.propose_change(_request(bid="HB-001", body=_boundary("HB-999")))

    def test_duplicate_change_id_rejected(self) -> None:
        mgr = _manager()
        mgr.propose_change(_request(cid="CHG-001", body=_boundary()))
        with pytest.raises(StandardsManagerError):
            mgr.propose_change(_request(cid="CHG-001", bid="HB-002", body=_boundary("HB-002")))

    def test_invalid_scalars_rejected(self) -> None:
        mgr = _manager()
        with pytest.raises(StandardsManagerError):
            mgr.propose_change("not-a-request")
        with pytest.raises(StandardsManagerError):
            mgr.propose_change(_request(cid="", body=_boundary()))
        with pytest.raises(StandardsManagerError):
            mgr.propose_change(_request(kind="add", body=_boundary()))
        with pytest.raises(StandardsManagerError):
            mgr.propose_change(_request(bid="", body=_boundary()))
        with pytest.raises(StandardsManagerError):
            mgr.propose_change(_request(by="", body=_boundary()))

    def test_pending_sorted_by_proposed_at_then_change_id(self) -> None:
        mgr = _manager()
        mgr.propose_change(_request(cid="CHG-B", bid="HB-002", body=_boundary("HB-002")))
        mgr.propose_change(_request(cid="CHG-A", body=_boundary()))
        assert [r.change_id for r in mgr.pending()] == ["CHG-A", "CHG-B"]


# ──────────────────────────────────────────────────────────────────────────────
# 人工裁决（一次性；批准才落目录并挂接脚本）
# ──────────────────────────────────────────────────────────────────────────────


class TestDecideChange:
    def test_approve_add_applies_and_registers(self) -> None:
        calls: list[tuple[str, str]] = []
        mgr = _manager(registrar=lambda bid, anchor: calls.append((bid, anchor)))
        mgr.propose_change(_request(body=_boundary()))
        record = mgr.decide_change(_approve("CHG-001"))
        assert record.status is ChangeStatus.APPROVED
        assert record.decided_at == _T0
        assert record.decided_by == "reviewer"
        assert mgr.get("HB-001").constraint_text == "禁止越层 import"
        assert calls == [("HB-001", "scripts/gov/check_layer.py")]
        assert mgr.pending() == ()

    def test_reject_add_not_applied(self) -> None:
        mgr = _manager()
        mgr.propose_change(_request(body=_boundary()))
        record = mgr.decide_change(
            ApprovalDecision(change_id="CHG-001", approved=False, decided_by="reviewer", note="依据不足")
        )
        assert record.status is ChangeStatus.REJECTED
        assert record.note == "依据不足"
        assert mgr.catalog() == ()
        assert mgr.status_of("CHG-001") is ChangeStatus.REJECTED

    def test_approve_update_replaces_and_reregisters(self) -> None:
        calls: list[tuple[str, str]] = []
        mgr = _manager(registrar=lambda bid, anchor: calls.append((bid, anchor)), seed=(_boundary(),))
        mgr.propose_change(
            _request(kind=ChangeKind.UPDATE, body=_boundary(text="禁止越层 import（收紧）", anchor="scripts/gov/check_layer_v2.py"))
        )
        mgr.decide_change(_approve("CHG-001"))
        assert mgr.get("HB-001").constraint_text == "禁止越层 import（收紧）"
        assert calls[-1] == ("HB-001", "scripts/gov/check_layer_v2.py")

    def test_approve_retire_removes_without_register(self) -> None:
        calls: list[tuple[str, str]] = []
        mgr = _manager(registrar=lambda bid, anchor: calls.append((bid, anchor)), seed=(_boundary(),))
        assert calls == [("HB-001", "scripts/gov/check_layer.py")]  # 种子登记
        mgr.propose_change(_request(kind=ChangeKind.RETIRE))
        mgr.decide_change(_approve("CHG-001"))
        assert mgr.catalog() == ()
        assert calls == [("HB-001", "scripts/gov/check_layer.py")]  # RETIRE 不触发脚本注册

    def test_unknown_or_double_decide_rejected(self) -> None:
        mgr = _manager()
        with pytest.raises(StandardsManagerError):
            mgr.decide_change(_approve("CHG-GHOST"))
        mgr.propose_change(_request(body=_boundary()))
        mgr.decide_change(_approve("CHG-001"))
        with pytest.raises(StandardsManagerError):
            mgr.decide_change(_approve("CHG-001"))

    def test_invalid_decision_fields_rejected(self) -> None:
        mgr = _manager()
        mgr.propose_change(_request(body=_boundary()))
        with pytest.raises(StandardsManagerError):
            mgr.decide_change("not-a-decision")
        with pytest.raises(StandardsManagerError):
            mgr.decide_change(ApprovalDecision(change_id="CHG-001", approved="yes", decided_by="reviewer"))
        with pytest.raises(StandardsManagerError):
            mgr.decide_change(ApprovalDecision(change_id="CHG-001", approved=True, decided_by=""))

    def test_registrar_failure_blocks_apply(self) -> None:
        def boom(bid: str, anchor: str) -> None:
            raise RuntimeError("gate registry down")

        mgr = _manager(registrar=boom)
        mgr.propose_change(_request(body=_boundary()))
        with pytest.raises(StandardsManagerError):
            mgr.decide_change(_approve("CHG-001"))
        assert mgr.catalog() == ()  # 挂接失败不落目录
        assert mgr.status_of("CHG-001") is ChangeStatus.PENDING  # 未记账裁决，可重审


# ──────────────────────────────────────────────────────────────────────────────
# 查询（Fail-Closed + 留痕）
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_get_and_status_fail_closed(self) -> None:
        mgr = _manager(seed=(_boundary(),))
        assert mgr.get("HB-001").meta["standard_id"] == "PS-STD-001"
        with pytest.raises(StandardsManagerError):
            mgr.get("HB-GHOST")
        with pytest.raises(StandardsManagerError):
            mgr.get("")
        with pytest.raises(StandardsManagerError):
            mgr.status_of("CHG-GHOST")
        with pytest.raises(StandardsManagerError):
            mgr.status_of("")

    def test_history_records_full_lifecycle(self) -> None:
        mgr = _manager()
        mgr.propose_change(_request(cid="CHG-001", body=_boundary()))
        mgr.propose_change(_request(cid="CHG-002", bid="HB-002", body=_boundary("HB-002")))
        mgr.decide_change(_approve("CHG-001"))
        mgr.decide_change(ApprovalDecision(change_id="CHG-002", approved=False, decided_by="reviewer"))
        history = mgr.history()
        assert [r.change_id for r in history] == ["CHG-001", "CHG-002"]
        assert [r.status for r in history] == [ChangeStatus.APPROVED, ChangeStatus.REJECTED]
        assert all(r.proposed_at == _T0 for r in history)


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_input_same_output(self) -> None:
        def run() -> tuple:
            mgr = _manager()
            mgr.propose_change(_request(cid="CHG-001", body=_boundary()))
            mgr.propose_change(_request(cid="CHG-002", bid="HB-002", body=_boundary("HB-002")))
            mgr.decide_change(_approve("CHG-002"))
            mgr.decide_change(
                ApprovalDecision(change_id="CHG-001", approved=False, decided_by="reviewer")
            )
            return (
                tuple(b.boundary_id for b in mgr.catalog()),
                tuple((r.change_id, r.status) for r in mgr.history()),
            )

        assert run() == run()
