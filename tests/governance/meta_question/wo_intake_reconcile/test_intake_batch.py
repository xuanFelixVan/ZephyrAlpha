# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/chain_piling_campaign/infra_mining/10_intake_gate_design.md | §5.1 限流三参数（裁定#402 定案值）
# [MODULE] tests.governance.meta_question.wo_intake_reconcile.test_intake_batch
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts/governance/meta_question/wo_intake_reconcile/intake_batch.py（importlib 文件装载）
# [CONSUMERS] WO-003② 持续入题机制验收（限流/幂等/时间分层/带反馈四条腿）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 零 PG/零生产写入：registry 与限流读数全部注入假件，批文件走 tmp_path
# [MODIFY-GUARD] none
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=测试红
# [TESTS] 本件即测试
# [TTL] permanent
"""持续入题驱动器测试（WO-003②）：限流截断/幂等查重/时间分层铁律/健康带反馈。"""

from __future__ import annotations

import importlib.util
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402

_SPEC = importlib.util.spec_from_file_location(
    "intake_batch",
    REPO_ROOT / "scripts" / "governance" / "meta_question" / "wo_intake_reconcile" / "intake_batch.py",
)
intake = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
sys.modules[_SPEC.name] = intake
_SPEC.loader.exec_module(intake)


class FakeRegistry:
    """假登记闸：只表达 registry 契约形状（真检语义由 test_registry_real_check 侧证）。"""

    def __init__(self, grounded_line: str = "SL-A03", dup_titles: tuple[str, ...] = ()) -> None:
        self.registered: list[dict[str, Any]] = []
        self.transitions: list[Any] = []
        self.grounded_line = grounded_line
        self.dup_titles = dup_titles

    def _source_line_register(self) -> dict[str, Any]:
        return {"lines": [{"line_id": self.grounded_line}]}

    @staticmethod
    def _check_five_elements(q: dict[str, Any], register: Any = None) -> list[str]:
        plan = q.get("exam_plan") or {}
        if not str(plan.get("criterion") or "").strip() or plan.get("threshold") in (None, ""):
            raise RejectStub("exam_plan_no_threshold")
        return [] if q.get("line_ref") == register["lines"][0]["line_id"] else ["source_line_resolvability"]

    def register(self, question: dict[str, Any], *, actor: str = "") -> str:
        if str(question.get("title")) in self.dup_titles:
            raise RejectStub("dup_high_similarity", question.get("title"))
        self.registered.append(dict(question))
        return f"PQ-{len(self.registered):04d}"

    def transition(self, *args: Any, **kwargs: Any) -> None:  # 越界即测红
        self.transitions.append((args, kwargs))


class RejectStub(Exception):
    def __init__(self, subcode: str, detail: Any = None) -> None:
        super().__init__(subcode)
        self.subcode = subcode


def _batch(n: int = 3, *, generated: str = "2026-09-20", **overrides: Any) -> dict[str, Any]:
    def one(i: int) -> dict[str, Any]:
        return {
            "title": f"入题测试问 {i}？",
            "layer": "L1",
            "line_ref": "SL-A03",
            "graph_ref": None,
            "data_sources": ["DS-TQCENTER"],
            "exam_plan": {"criterion": "rank_ic", "threshold": 0.02},
            "consumers": ["L3状态变量层"],
            "frequency": "daily",
            "pit_proof": "按公告日取数",
            "provenance": {"origin": "test"},
            "net_zero_note": "净零声明 NZ-TEST",
        }

    doc = {
        "batch_id": "TEST-BATCH",
        "session": "sess-test",
        "generated_date": generated,
        "count": n,
        "questions": [one(i) for i in range(1, n + 1)],
    }
    doc.update(overrides)
    return doc


# ── 批契约与时间分层铁律 ────────────────────────────────────────────────


def test_batch_requires_all_contract_fields(tmp_path: Path) -> None:
    path = tmp_path / "b.yaml"
    path.write_text(
        yaml.safe_dump({"batch_id": "X", "questions": [{"title": "t"}]}, allow_unicode=True), encoding="utf-8"
    )
    with pytest.raises(intake.BatchError) as exc:
        intake.load_batch(path, today=date(2026, 9, 24))
    assert "batch_field_missing" in str(exc.value)


def test_same_day_batch_is_refused(tmp_path: Path) -> None:
    """[纪要§8.2] 今日输出→明日输入：同日批必拒，且无逃生旗。"""
    path = tmp_path / "b.yaml"
    path.write_text(yaml.safe_dump(_batch(generated="2026-09-24"), allow_unicode=True), encoding="utf-8")
    with pytest.raises(intake.BatchError) as exc:
        intake.load_batch(path, today=date(2026, 9, 24))
    assert "time_layer_violation" in str(exc.value)


def test_future_batch_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "b.yaml"
    path.write_text(
        yaml.safe_dump(_batch(generated=(date(2026, 9, 24) + timedelta(days=3)).isoformat()), allow_unicode=True),
        encoding="utf-8",
    )
    with pytest.raises(intake.BatchError):
        intake.load_batch(path, today=date(2026, 9, 24))


def test_count_drift_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "b.yaml"
    doc = _batch(3)
    doc["count"] = 5
    path.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    with pytest.raises(intake.BatchError) as exc:
        intake.load_batch(path, today=date(2026, 9, 24))
    assert "batch_count_drift" in str(exc.value)


# ── dry-run / apply 控制流 ─────────────────────────────────────────────


def test_dry_run_classifies_ok_and_reject() -> None:
    doc = _batch(2)
    doc["questions"][1]["exam_plan"] = {"criterion": "rank_ic"}
    report = intake.run_batch(doc, apply=False, registry=FakeRegistry())
    assert report["counts"] == {"ok": 1, "reject": 1}
    assert report["outcomes"][1]["code"] == "exam_plan_no_threshold"
    assert report["mode"] == "dry_run"


def test_dry_run_writes_nothing() -> None:
    registry = FakeRegistry()
    intake.run_batch(_batch(4), apply=False, registry=registry)
    assert registry.registered == []


def test_ungrounded_line_reported_as_degraded() -> None:
    doc = _batch(1, questions=[dict(_batch(1)["questions"][0], line_ref="SL-A06")])
    report = intake.run_batch(doc, apply=False, registry=FakeRegistry())
    assert report["outcomes"][0]["action"] == "dry_run_degraded"
    assert report["outcomes"][0]["code"] == "source_line_resolvability"


def test_apply_registers_through_gate_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(intake, "day_register_counts", lambda *_a, **_k: ({"__total__": 0}, None))
    registry = FakeRegistry()
    report = intake.run_batch(_batch(3), apply=True, registry=registry)
    assert report["counts"] == {"registered": 3}
    assert [e["code"] for e in report["outcomes"]] == ["PQ-0001", "PQ-0002", "PQ-0003"]
    assert registry.transitions == [], "入题器禁越界做状态流转（那是看板/B1 的地盘）"


# ── 限流三参数（裁定#402：单批12／会话日40／全库日120）─────────────────


def test_batch_cap_is_12(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(intake, "day_register_counts", lambda *_a, **_k: ({"__total__": 0}, None))
    registry = FakeRegistry()
    report = intake.run_batch(_batch(15), apply=True, registry=registry)
    assert report["counts"] == {"registered": 12, "rate_limited": 3}
    assert report["caps"]["batch"] == 12


def test_session_day_cap_bites(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(intake, "day_register_counts", lambda *_a, **_k: ({"__total__": 20, "sess-test|AI": 39}, None))
    report = intake.run_batch(_batch(5), apply=True, registry=FakeRegistry())
    assert report["counts"] == {"registered": 1, "rate_limited": 4}
    assert report["caps"]["session_day_remaining"] == 1


def test_global_day_cap_bites(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(intake, "day_register_counts", lambda *_a, **_k: ({"__total__": 120}, None))
    report = intake.run_batch(_batch(3), apply=True, registry=FakeRegistry())
    assert report["counts"] == {"rate_limited": 3}


def test_rate_limit_read_failure_is_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(intake, "day_register_counts", lambda *_a, **_k: ({}, "pg_connect_failed: x"))
    with pytest.raises(intake.BatchError):
        intake.run_batch(_batch(2), apply=True, registry=FakeRegistry())


# ── 幂等（查重走 registry 正门，本件不自建查重）───────────────────────


def test_duplicate_counts_as_skip_not_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(intake, "day_register_counts", lambda *_a, **_k: ({"__total__": 0}, None))
    doc = _batch(2)
    registry = FakeRegistry(dup_titles=(doc["questions"][0]["title"],))
    report = intake.run_batch(doc, apply=True, registry=registry)
    assert report["counts"] == {"registered": 1, "skip_dup": 1}
    assert all(e["action"] != "reject" for e in report["outcomes"])


# ── 健康带反馈（WO-003①↔② 接线）──────────────────────────────────────


def test_band_projection_matches_live_campaign_shape() -> None:
    """283 全 answered 的现状：入 71 问才回到单态帽 80% 内（71 由不等式机械解出，非口算）。"""
    counts = {"answered": 283}
    need = intake.band_projection(counts, 0)["min_added_for_cap80"]
    assert need == 71
    after = intake.band_projection(counts, need)
    assert after["max_status_pct"] <= 80.0
    assert not after["in_default_band"]  # answered 仍 <30% 下界 → 常态带仍不达标（诚实报）


def test_band_projection_in_band_case() -> None:
    after = intake.band_projection({"answered": 100, "registered": 60, "mining": 40}, 0)
    assert after["in_default_band"] and after["max_status_pct"] <= 80.0


def test_min_added_for_cap_zero_when_in_band() -> None:
    assert intake._min_added_for_cap({"answered": 50, "registered": 50}) == 0
