#!/usr/bin/env python
# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md §1.1 + 工单 WO-B3
# [MODULE] tests.data.test_macro_vintage_mirror
# [DOMAIN] D_DATA
# [A_module] module_id=MOD-CHAINPILE-METAQ | layer=module | stability=new | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [DEPENDENCIES] zephyr.data.macro_vintage（被测）; zephyr.data.ch_writer（镜像钩子被测）; pytest monkeypatch
# [CONSUMERS] pytest only
# [STARTUP] none
# [MATURITY] stable
# [INVARIANTS] 零生产写：全部判定走纯函数 resolve_vintages（existing 由用例直供）与 ch_writer 钩子的注入替身，
#              禁触 CH/PG；每条判据都配"反例必须抛"腿（能红自证）；
#              时戳一律用例内常量（datetime(2026,9,24, tzinfo=UTC)），禁 datetime.now()
# [MODIFY-GUARD] none
"""WO-B3 宏数时点存证镜像回归测试（版次推导四判据 + 旁路钩子不伤主写入）。"""

from __future__ import annotations

import datetime
from typing import Any

import pytest

from zephyr.data import ch_writer, macro_vintage
from zephyr.data.macro_vintage import (
    _BASIS_BACKFILL,
    _BASIS_OBSERVED,
    is_macro_mirror_target,
    resolve_vintages,
)

_OBSERVED = datetime.datetime(2026, 9, 24, 3, 0, 0, tzinfo=datetime.UTC)
_ROW: tuple[Any, ...] = (
    datetime.date(2026, 3, 31),
    "gdp_yoy",
    5.2,
    "%",
    "quarterly",
    "akshare",
)
_KEY = ("gdp_yoy", "2026-03-31")


def _vintage_of(rows: list[tuple]) -> int:
    assert len(rows) == 1, f"期望单行，实得 {len(rows)}"
    return int(rows[0][6])


def test_new_key_starts_at_vintage_one() -> None:
    rows, stats = resolve_vintages([_ROW], {}, observed_at=_OBSERVED)
    assert _vintage_of(rows) == 1
    assert stats["new_key"] == 1 and stats["revised"] == 0


def test_same_value_replay_makes_no_fake_vintage() -> None:
    existing = {_KEY: {"max_vintage": 3, "values": [5.2]}}
    rows, stats = resolve_vintages([_ROW], existing, observed_at=_OBSERVED)
    assert rows == []
    assert stats["unchanged_skip"] == 1


def test_real_revision_increments_vintage_and_keeps_old() -> None:
    existing = {_KEY: {"max_vintage": 3, "values": [5.2]}}
    revised = (*_ROW[:2], 4.8, *_ROW[3:])
    rows, stats = resolve_vintages([revised], existing, observed_at=_OBSERVED)
    assert _vintage_of(rows) == 4
    assert stats["revised"] == 1
    assert float(rows[0][2]) == pytest.approx(4.8)  # 旧值在库不动=存证成立，本行只新增


def test_backfill_final_never_carries_a_publish_stamp() -> None:
    row = (*_ROW, datetime.datetime(2020, 1, 1, tzinfo=datetime.UTC), _BASIS_BACKFILL)
    rows, _ = resolve_vintages([row], {}, observed_at=_OBSERVED)
    assert rows[0][7] is None
    assert rows[0][8] == _BASIS_BACKFILL


def test_missing_stamp_falls_back_to_observed_basis() -> None:
    rows, _ = resolve_vintages([_ROW], {}, observed_at=_OBSERVED)
    assert rows[0][8] == _BASIS_OBSERVED
    assert rows[0][7] == _OBSERVED


def test_unknown_basis_is_rejected_not_silently_passed() -> None:
    row = (*_ROW, datetime.datetime(2026, 3, 1, tzinfo=datetime.UTC), "oracle_said_so")
    with pytest.raises(ValueError, match="pub_ts_basis"):
        resolve_vintages([row], {}, observed_at=_OBSERVED)


def test_short_row_is_rejected_not_guessed() -> None:
    with pytest.raises(ValueError, match="拒绝猜测"):
        resolve_vintages([("2026-03-31", "gdp_yoy")], {}, observed_at=_OBSERVED)


def test_null_value_is_skipped_with_counter() -> None:
    row = (*_ROW[:2], None, *_ROW[3:])
    rows, stats = resolve_vintages([row], {}, observed_at=_OBSERVED)
    assert rows == []
    assert stats["skipped_no_value"] == 1


def test_mirror_predicate_hits_only_the_legacy_table() -> None:
    assert is_macro_mirror_target("c1_market.macro_data") is True
    for other in ("c1_market.macro_data_vintage", "c1_market.macro_data_compat", "c1_market.kline_daily"):
        assert is_macro_mirror_target(other) is False


def test_ch_writer_hook_symbols_resolve_after_lazy_import() -> None:
    """补丁接线回归：钩子引用的两个名字必须在 macro_vintage 里真存在（NameError 防复发）。"""
    for name in ("is_macro_mirror_target", "mirror_from_legacy_rows"):
        assert callable(getattr(macro_vintage, name)), name


def test_hook_ignores_non_macro_table(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[Any] = []
    monkeypatch.setattr(macro_vintage, "mirror_from_legacy_rows", lambda rows: calls.append(rows))

    class _Result:
        table = "c1_market.kline_daily"

    ch_writer._maybe_mirror_macro_vintage(_Result(), ["report_date"], [("2026-03-31",)])
    assert calls == []


def test_hook_swallows_mirror_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """存证旁路红证：镜像内部炸掉也不得把主写入拖下水。"""

    def _boom(_rows: Any) -> dict[str, Any]:
        raise RuntimeError("mirror down")

    class _Result:
        table = "c1_market.macro_data"

    monkeypatch.setattr(macro_vintage, "mirror_from_legacy_rows", _boom)
    cols = ["report_date", "indicator_name", "indicator_value", "unit", "frequency", "data_source"]
    ch_writer._maybe_mirror_macro_vintage(_Result(), cols, [("2026-03-31", "g", 1.0, "%", "q", "akshare")])


def test_hook_reports_incomplete_columns_without_writing(monkeypatch: pytest.MonkeyPatch) -> None:
    written: list[Any] = []
    monkeypatch.setattr(macro_vintage, "mirror_from_legacy_rows", lambda rows: written.append(rows))
    cols = ["report_date", "indicator_name"]
    ch_writer._maybe_mirror_macro_vintage(_MacroResult(), cols, [("2026-03-31", "g")])
    assert written == []


class _MacroResult:
    table = "c1_market.macro_data"
