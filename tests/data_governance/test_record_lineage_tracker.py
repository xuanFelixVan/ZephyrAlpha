# [BLUEPRINT] MOD-DATA_GOV-008 | docs/03_modules/_domain_data_governance/record_lineage_tracker/blueprint.md | §test
# [MODULE] tests.data_governance.test_record_lineage_tracker
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES] zephyr.data_governance.core.record_lineage_tracker
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_record_lineage_tracker.py
# [A_test] module_id: MOD-DATA_GOV-008 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-DATA_GOV-008 单元测试: M8-NEW-09 Metaxy 记录级血缘追踪器。

覆盖: 必填字段 Fail-Closed、登记幂等（同内容重放）、同键异内容冲突 Fail-Closed、
(factor,trade_date) 反查、sidecar flush/load 往返、坏行 Fail-Closed、无 sidecar
路径 flush Fail-Closed。
"""

from __future__ import annotations

import pytest

from zephyr.data_governance.core.record_lineage_tracker import (
    FeatureBatchProvenance,
    RecordLineageError,
    RecordLineageTracker,
)


def _prov(**overrides) -> FeatureBatchProvenance:
    base = dict(
        batch_id="batch_0123456789abcdef",
        factor_name="momentum_20d",
        source_files=("data/kline_daily.parquet",),
        transform="close/prev_close-1 rolling20",
        code_version="git:abc1234",
        computed_at="2026-08-25T15:30:00",
        trade_dates=("2026-08-25",),
        row_count=5423,
    )
    base.update(overrides)
    return FeatureBatchProvenance(**base)


class TestRegister:
    def test_register_normal(self) -> None:
        t = RecordLineageTracker()
        assert t.register(_prov()) is True
        got = t.get("batch_0123456789abcdef")
        assert got is not None
        assert got.factor_name == "momentum_20d"

    @pytest.mark.parametrize(
        "field",
        ["batch_id", "factor_name", "transform", "code_version", "computed_at"],
    )
    def test_required_field_empty_fail_closed(self, field: str) -> None:
        t = RecordLineageTracker()
        with pytest.raises(RecordLineageError):
            t.register(_prov(**{field: "  "}))

    def test_empty_source_files_fail_closed(self) -> None:
        t = RecordLineageTracker()
        with pytest.raises(RecordLineageError):
            t.register(_prov(source_files=()))

    def test_blank_source_file_entry_fail_closed(self) -> None:
        t = RecordLineageTracker()
        with pytest.raises(RecordLineageError):
            t.register(_prov(source_files=("data/a.parquet", " ")))

    def test_negative_row_count_fail_closed(self) -> None:
        t = RecordLineageTracker()
        with pytest.raises(RecordLineageError):
            t.register(_prov(row_count=-1))

    def test_non_provenance_fail_closed(self) -> None:
        t = RecordLineageTracker()
        with pytest.raises(RecordLineageError):
            t.register({"batch_id": "x"})  # type: ignore[arg-type]

    def test_idempotent_replay_same_content(self) -> None:
        t = RecordLineageTracker()
        assert t.register(_prov()) is True
        assert t.register(_prov()) is False  # 同内容重放幂等

    def test_conflict_same_key_fail_closed(self) -> None:
        t = RecordLineageTracker()
        t.register(_prov())
        with pytest.raises(RecordLineageError):
            t.register(_prov(code_version="git:deadbeef"))  # 同键异内容=溯源漂移


class TestBacktrack:
    def test_backtrack_by_factor_and_date(self) -> None:
        t = RecordLineageTracker()
        t.register(_prov())
        t.register(_prov(batch_id="batch_fedcba9876543210", trade_dates=("2026-08-24",)))
        hits = t.backtrack("momentum_20d", "2026-08-25")
        assert len(hits) == 1
        assert hits[0].batch_id == "batch_0123456789abcdef"
        assert hits[0].source_files == ("data/kline_daily.parquet",)

    def test_backtrack_unknown_empty(self) -> None:
        t = RecordLineageTracker()
        t.register(_prov())
        assert t.backtrack("nope", "2026-08-25") == []
        assert t.backtrack("momentum_20d", "2020-01-01") == []

    def test_backtrack_empty_ident_fail_closed(self) -> None:
        t = RecordLineageTracker()
        with pytest.raises(RecordLineageError):
            t.backtrack("", "2026-08-25")


class TestSidecarPersistence:
    def test_flush_load_roundtrip(self, tmp_path) -> None:
        sidecar = tmp_path / "record_lineage.jsonl"
        t = RecordLineageTracker(sidecar)
        t.register(_prov())
        t.register(_prov(batch_id="batch_fedcba9876543210", factor_name="volatility_5d"))
        assert t.flush() == 2
        assert sidecar.exists()
        t2 = RecordLineageTracker.load(sidecar)
        assert t2.get("batch_0123456789abcdef") is not None
        assert len(t2.backtrack("volatility_5d", "2026-08-25")) == 1

    def test_flush_without_sidecar_fail_closed(self) -> None:
        t = RecordLineageTracker()
        t.register(_prov())
        with pytest.raises(RecordLineageError):
            t.flush()

    def test_load_corrupt_line_fail_closed(self, tmp_path) -> None:
        sidecar = tmp_path / "bad.jsonl"
        sidecar.write_text('{"batch_id": "batch_x"}\nnot-json\n', encoding="utf-8")
        with pytest.raises(RecordLineageError):
            RecordLineageTracker.load(sidecar)

    def test_load_missing_file_fail_closed(self, tmp_path) -> None:
        with pytest.raises(RecordLineageError):
            RecordLineageTracker.load(tmp_path / "nonexistent.jsonl")

    def test_flush_atomic_and_idempotent_rewrite(self, tmp_path) -> None:
        sidecar = tmp_path / "record_lineage.jsonl"
        t = RecordLineageTracker(sidecar)
        t.register(_prov())
        t.flush()
        first = sidecar.read_bytes()
        t.flush()  # 重写同内容（原子 tmp+replace）
        assert sidecar.read_bytes() == first
