# [BLUEPRINT] MOD-INT-FACT-LEDGER | docs/03_modules/_domain_intelligence/universal_fact_ledger/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INT-FACT-LEDGER | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.intelligence.test_universal_fact_ledger
# [TESTS] src/zephyr/intelligence/universal_fact_ledger.py
"""MOD-INT-FACT-LEDGER 单元测试：universal_fact_ledger 通用事实账本与双重锚定。

蓝图验收（B10-01952/CAND-AISA-014，A1 §29.24-1）：
UFL 追加式事实账本（五要素+3 类型词表+confidence=1.0 硬约束，写后不可改）+
DoubleLockGrounding 校验器（实体不存在/数值非检索自 UFL 即拒绝，拒绝不可
降级须修正重提）+ 约束强度 3 档 + 查询接口。时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.intelligence.universal_fact_ledger",
    reason="universal_fact_ledger not importable",
)

from zephyr.intelligence.universal_fact_ledger import (  # noqa: E402
    ConstraintStrength,
    DoubleLockGrounding,
    FactLedgerError,
    FactRecord,
    FactType,
    NumericClaim,
    UniversalFactLedger,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)
_T1 = datetime.datetime(2026, 8, 25, 10, 30, 0)


def _ledger() -> UniversalFactLedger:
    return UniversalFactLedger(clock=lambda: _T0)


def _numeric(entity: str = "600519.SH", attr: str = "收盘价", value=1700.0, ts=_T0) -> FactRecord:
    return FactRecord(
        entity=entity, attribute=attr, value=value, timestamp=ts, source="行情快照", fact_type=FactType.NUMERIC
    )


def _enum(entity: str = "600519.SH", attr: str = "所属行业", value: str = "白酒") -> FactRecord:
    return FactRecord(
        entity=entity, attribute=attr, value=value, timestamp=_T0, source="分类表", fact_type=FactType.ENUM
    )


def _relation(entity: str = "600519.SH", attr: str = "上游", value: str = "高粱种植") -> FactRecord:
    return FactRecord(
        entity=entity, attribute=attr, value=value, timestamp=_T0, source="产业链", fact_type=FactType.RELATION
    )


# ──────────────────────────────────────────────────────────────────────────────
# UFL 追加式账本
# ──────────────────────────────────────────────────────────────────────────────


class TestAppend:
    def test_append_three_types(self) -> None:
        ledger = _ledger()
        ledger.append(_numeric())
        ledger.append(_enum())
        ledger.append(_relation())
        assert ledger.size() == 3

    def test_confidence_hard_constraint(self) -> None:
        ledger = _ledger()
        bad = FactRecord(
            entity="e", attribute="a", value=1.0, timestamp=_T0, source="s", fact_type=FactType.NUMERIC, confidence=0.9
        )
        with pytest.raises(FactLedgerError):
            ledger.append(bad)

    def test_missing_fields_raise(self) -> None:
        ledger = _ledger()
        with pytest.raises(FactLedgerError):
            ledger.append(_numeric(entity=""))
        with pytest.raises(FactLedgerError):
            ledger.append(_numeric(attr=""))
        with pytest.raises(FactLedgerError):
            ledger.append(
                FactRecord(entity="e", attribute="a", value=1.0, timestamp=_T0, source="", fact_type=FactType.NUMERIC)
            )

    def test_invalid_type_raises(self) -> None:
        ledger = _ledger()
        bad = FactRecord(entity="e", attribute="a", value="v", timestamp=_T0, source="s", fact_type="text")  # type: ignore[arg-type]
        with pytest.raises(FactLedgerError):
            ledger.append(bad)

    def test_numeric_value_domain(self) -> None:
        ledger = _ledger()
        with pytest.raises(FactLedgerError):
            ledger.append(_numeric(value="一千七"))
        with pytest.raises(FactLedgerError):
            ledger.append(_numeric(value=True))
        ledger.append(_numeric(value=1700))  # int 合法

    def test_enum_value_must_be_str(self) -> None:
        ledger = _ledger()
        bad = FactRecord(entity="e", attribute="a", value=123, timestamp=_T0, source="s", fact_type=FactType.ENUM)
        with pytest.raises(FactLedgerError):
            ledger.append(bad)


# ──────────────────────────────────────────────────────────────────────────────
# 查询接口（追加式、写后不可改语义：历史全保留，最新优先）
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_get_latest_by_timestamp(self) -> None:
        ledger = _ledger()
        ledger.append(_numeric(value=1690.0, ts=_T0))
        ledger.append(_numeric(value=1700.0, ts=_T1))
        assert ledger.get("600519.SH", "收盘价").value == 1700.0
        assert ledger.size() == 2  # 追加式：旧值保留不可改

    def test_facts_of_history_sorted(self) -> None:
        ledger = _ledger()
        ledger.append(_numeric(value=1700.0, ts=_T1))
        ledger.append(_numeric(value=1690.0, ts=_T0))
        history = ledger.facts_of("600519.SH", "收盘价")
        assert [f.value for f in history] == [1690.0, 1700.0]  # 确定性升序

    def test_get_missing_raises(self) -> None:
        with pytest.raises(FactLedgerError):
            _ledger().get("ghost", "收盘价")

    def test_entities_sorted(self) -> None:
        ledger = _ledger()
        ledger.append(_numeric(entity="b.SH"))
        ledger.append(_numeric(entity="a.SH"))
        assert ledger.entities() == ("a.SH", "b.SH")

    def test_contains(self) -> None:
        ledger = _ledger()
        ledger.append(_numeric())
        assert ledger.contains("600519.SH") is True
        assert ledger.contains("ghost") is False


# ──────────────────────────────────────────────────────────────────────────────
# DoubleLockGrounding 校验器
# ──────────────────────────────────────────────────────────────────────────────


class TestDoubleLock:
    def _grounded(self, strength=ConstraintStrength.STRICT, tolerance: float = 0.0):
        ledger = _ledger()
        ledger.append(_numeric(value=1700.0))
        ledger.append(_enum())
        return DoubleLockGrounding(ledger=ledger, strength=strength, numeric_tolerance=tolerance)

    def test_accept_when_both_locks_pass(self) -> None:
        g = self._grounded()
        result = g.validate(
            entities=["600519.SH"],
            numeric_claims=[NumericClaim(entity="600519.SH", attribute="收盘价", value=1700.0)],
        )
        assert result.accepted is True
        assert result.violations == ()

    def test_entity_miss_rejected(self) -> None:
        g = self._grounded()
        result = g.validate(entities=["ghost.SH"])
        assert result.accepted is False
        assert result.violations[0].kind == "entity_miss"

    def test_numeric_not_from_ufl_rejected(self) -> None:
        g = self._grounded()
        result = g.validate(
            entities=["600519.SH"],
            numeric_claims=[NumericClaim(entity="600519.SH", attribute="收盘价", value=9999.0)],
        )
        assert result.accepted is False
        assert result.violations[0].kind == "numeric_miss"

    def test_rejection_no_downgrade_enforce_raises(self) -> None:
        g = self._grounded()
        with pytest.raises(FactLedgerError):
            g.enforce(entities=["ghost.SH"])  # 拒绝不可降级，须修正重提

    def test_fix_and_resubmit_accepted(self) -> None:
        g = self._grounded()
        bad = g.validate(
            entities=["600519.SH"], numeric_claims=[NumericClaim(entity="600519.SH", attribute="收盘价", value=1.0)]
        )
        assert bad.accepted is False
        fixed = g.validate(
            entities=["600519.SH"], numeric_claims=[NumericClaim(entity="600519.SH", attribute="收盘价", value=1700.0)]
        )
        assert fixed.accepted is True  # 修正后重提通过

    def test_standard_strength_historical_match(self) -> None:
        g = self._grounded(strength=ConstraintStrength.STANDARD)
        g._ledger.append(_numeric(value=1710.0, ts=_T1))  # 最新值变 1710
        result = g.validate(
            entities=["600519.SH"],
            numeric_claims=[NumericClaim(entity="600519.SH", attribute="收盘价", value=1700.0)],
        )
        assert result.accepted is True  # STANDARD: 任一历史值精确相等即可

    def test_strict_strength_latest_only(self) -> None:
        g = self._grounded(strength=ConstraintStrength.STRICT)
        g._ledger.append(_numeric(value=1710.0, ts=_T1))
        result = g.validate(
            entities=["600519.SH"],
            numeric_claims=[NumericClaim(entity="600519.SH", attribute="收盘价", value=1700.0)],
        )
        assert result.accepted is False  # STRICT: 仅最新值精确相等

    def test_lenient_strength_within_tolerance(self) -> None:
        g = self._grounded(strength=ConstraintStrength.LENIENT, tolerance=5.0)
        result = g.validate(
            entities=["600519.SH"],
            numeric_claims=[NumericClaim(entity="600519.SH", attribute="收盘价", value=1703.0)],
        )
        assert result.accepted is True

    def test_lenient_strength_beyond_tolerance_rejected(self) -> None:
        g = self._grounded(strength=ConstraintStrength.LENIENT, tolerance=5.0)
        result = g.validate(
            entities=["600519.SH"],
            numeric_claims=[NumericClaim(entity="600519.SH", attribute="收盘价", value=1710.0)],
        )
        assert result.accepted is False

    def test_constructor_validation(self) -> None:
        with pytest.raises(FactLedgerError):
            DoubleLockGrounding(ledger=None)  # type: ignore[arg-type]
        with pytest.raises(FactLedgerError):
            DoubleLockGrounding(ledger=_ledger(), strength="hard")  # type: ignore[arg-type]
        with pytest.raises(FactLedgerError):
            DoubleLockGrounding(ledger=_ledger(), numeric_tolerance=-1.0)
