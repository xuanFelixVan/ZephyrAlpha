# [BLUEPRINT] MOD-ALT-006 | docs/03_modules/_domain_alt_data/concept_factor_mapper/blueprint.md | §test
# [MODULE] tests.alt_data.test_concept_factor_mapper
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.alt_data.concept_factor_mapper
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_concept_factor_mapper.py
# [A_test] module_id: MOD-ALT-006 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-ALT-006 单元测试: ConceptFactorMapper — 概念因子映射引擎。

覆盖: Excel 分号字段解析（全角；/半角;/混用/空白/None/非 str/保序去重）、
双向索引构建（字典序/去重/拒绝留痕/latest_effective_date）、质量校验
（EMPTY<min/OVERSIZED>max/STALE>stale_days/恰等不命中/无行）、asof PIT
（取≤查询日最新/无版本→None/未来版本不取）、配置 Fail-Closed、确定性、
frozen。
"""

from __future__ import annotations

import datetime
from dataclasses import FrozenInstanceError

import pytest

from zephyr.alt_data.concept_factor_mapper import (
    ConceptConstituentRow,
    ConceptFactorMapper,
    ConceptMapperConfig,
    InvalidConceptMapperConfigError,
    InvalidConceptRowError,
    MappingVersion,
)

D0 = datetime.date(2026, 8, 25)


def _row(symbol: str, concept: str, days_ago: int = 0) -> ConceptConstituentRow:
    return ConceptConstituentRow(symbol=symbol, concept=concept, effective_date=D0 - datetime.timedelta(days=days_ago))


@pytest.fixture
def mapper() -> ConceptFactorMapper:
    return ConceptFactorMapper()


class TestParseExcelField:
    def test_halfwidth_semicolon(self, mapper):
        assert mapper.parse_excel_field("半导体;新能源车") == ("半导体", "新能源车")

    def test_fullwidth_semicolon(self, mapper):
        assert mapper.parse_excel_field("半导体；新能源车") == ("半导体", "新能源车")

    def test_mixed_separators_and_blanks(self, mapper):
        assert mapper.parse_excel_field("半导体; 新能源车；;军工") == ("半导体", "新能源车", "军工")

    def test_dedupe_preserves_order(self, mapper):
        assert mapper.parse_excel_field("A;B;A；C;B") == ("A", "B", "C")

    def test_non_str_and_blank(self, mapper):
        assert mapper.parse_excel_field(None) == ()
        assert mapper.parse_excel_field(123) == ()
        assert mapper.parse_excel_field("") == ()
        assert mapper.parse_excel_field(" ; ； ") == ()


class TestBuild:
    def test_bidirectional_index_sorted(self, mapper):
        index, errors = mapper.build(
            [
                _row("600000", "半导体"),
                _row("000001", "半导体"),
                _row("600000", "军工"),
            ]
        )
        assert errors == ()
        assert index.symbol_to_concepts["600000"] == ("军工", "半导体")  # 字典序
        assert index.concept_to_symbols["半导体"] == ("000001", "600000")  # 逆向索引字典序
        assert index.row_count == 3
        assert index.latest_effective_date == D0

    def test_duplicate_rows_deduped(self, mapper):
        index, errors = mapper.build([_row("600000", "半导体"), _row("600000", "半导体")])
        assert index.row_count == 1
        assert errors == ()

    def test_invalid_rows_rejected_ledger(self, mapper):
        index, errors = mapper.build(
            [
                _row("600000", "半导体"),
                {"symbol": " ", "concept": "军工", "effective_date": D0},
                _row("000001", "半导体"),
            ]
        )
        assert index.row_count == 2
        assert len(errors) == 1
        assert errors[0][0] == 1

    def test_latest_effective_date(self, mapper):
        index, _ = mapper.build([_row("A", "X", days_ago=10), _row("B", "X", days_ago=3)])
        assert index.latest_effective_date == D0 - datetime.timedelta(days=3)

    def test_empty_build(self, mapper):
        index, errors = mapper.build([])
        assert index.row_count == 0
        assert index.latest_effective_date is None
        assert errors == ()

    def test_row_validation(self):
        with pytest.raises(InvalidConceptRowError):
            _row("", "半导体")
        with pytest.raises(InvalidConceptRowError):
            _row("600000", " ")
        with pytest.raises(InvalidConceptRowError):
            ConceptConstituentRow(symbol="600000", concept="X", effective_date="2026-08-25")  # type: ignore[arg-type]


class TestQuality:
    def test_empty_concept(self, mapper):
        index, _ = mapper.build([_row("600000", "半导体"), _row("000001", "半导体"), _row("600000", "军工")])
        rep = mapper.check_quality(index, D0)
        assert rep.empty_count == 1
        assert rep.issues[0].kind == "EMPTY_CONCEPT"
        assert rep.issues[0].concept == "军工"

    def test_oversized_concept(self):
        m = ConceptFactorMapper(ConceptMapperConfig(min_constituents=1, max_constituents=2))
        index, _ = m.build([_row(f"S{i}", "大概念") for i in range(3)])
        rep = m.check_quality(index, D0)
        assert rep.oversized_count == 1
        assert rep.issues[0].kind == "OVERSIZED_CONCEPT"

    def test_boundary_exact_not_triggered(self):
        m = ConceptFactorMapper(ConceptMapperConfig(min_constituents=2, max_constituents=2, stale_days=30))
        index, _ = m.build([_row("A", "X"), _row("B", "X")])
        rep = m.check_quality(index, D0)
        assert rep.issues == ()  # 恰等 min/max/stale 不命中

    def test_stale_mapping(self, mapper):
        index, _ = mapper.build([_row("A", "X", days_ago=31), _row("B", "X", days_ago=31)])
        rep = mapper.check_quality(index, D0)
        assert rep.stale is True
        assert any(i.kind == "STALE_MAPPING" for i in rep.issues)

    def test_stale_boundary_exact_not_triggered(self, mapper):
        index, _ = mapper.build([_row("A", "X", days_ago=30), _row("B", "X", days_ago=30)])
        rep = mapper.check_quality(index, D0)
        assert rep.stale is False

    def test_no_rows_stale(self, mapper):
        index, _ = mapper.build([])
        rep = mapper.check_quality(index, D0)
        assert rep.stale is True
        assert rep.concept_count == 0

    def test_check_quality_bad_args(self, mapper):
        index, _ = mapper.build([_row("A", "X")])
        with pytest.raises(InvalidConceptRowError):
            mapper.check_quality("x", D0)  # type: ignore[arg-type]
        with pytest.raises(InvalidConceptRowError):
            mapper.check_quality(index, "2026-08-25")  # type: ignore[arg-type]


class TestAsof:
    def test_pit_latest_eligible(self, mapper):
        v1 = MappingVersion(D0 - datetime.timedelta(days=10), mapper.build([_row("A", "旧概念", 10)])[0])
        v2 = MappingVersion(D0 - datetime.timedelta(days=2), mapper.build([_row("A", "新概念", 2)])[0])
        picked = mapper.asof([v1, v2], D0)
        assert picked is v2.index

    def test_future_version_not_picked(self, mapper):
        v1 = MappingVersion(D0 - datetime.timedelta(days=10), mapper.build([_row("A", "旧概念", 10)])[0])
        v2 = MappingVersion(D0 + datetime.timedelta(days=5), mapper.build([_row("A", "未来概念", 0)])[0])
        picked = mapper.asof([v1, v2], D0)
        assert picked is v1.index

    def test_no_eligible_returns_none(self, mapper):
        v = MappingVersion(D0 + datetime.timedelta(days=1), mapper.build([_row("A", "X")])[0])
        assert mapper.asof([v], D0) is None
        assert mapper.asof([], D0) is None

    def test_asof_bad_date(self, mapper):
        with pytest.raises(InvalidConceptRowError):
            mapper.asof([], "2026-08-25")  # type: ignore[arg-type]

    def test_version_validation(self, mapper):
        index, _ = mapper.build([_row("A", "X")])
        with pytest.raises(InvalidConceptRowError):
            MappingVersion("2026-08-25", index)  # type: ignore[arg-type]
        with pytest.raises(InvalidConceptRowError):
            MappingVersion(D0, "not-an-index")  # type: ignore[arg-type]


class TestConfigAndDeterminism:
    def test_bad_config(self):
        with pytest.raises(InvalidConceptMapperConfigError):
            ConceptMapperConfig(min_constituents=0)
        with pytest.raises(InvalidConceptMapperConfigError):
            ConceptMapperConfig(max_constituents=-1)
        with pytest.raises(InvalidConceptMapperConfigError):
            ConceptMapperConfig(stale_days=0)
        with pytest.raises(InvalidConceptMapperConfigError):
            ConceptMapperConfig(min_constituents=5, max_constituents=2)
        with pytest.raises(InvalidConceptMapperConfigError):
            ConceptFactorMapper(config="x")  # type: ignore[arg-type]

    def test_determinism(self, mapper):
        rows = [_row("B", "Y"), _row("A", "X"), _row("A", "Y"), _row("B", "X")]
        i1, _ = mapper.build(rows)
        i2, _ = mapper.build(list(reversed(rows)))
        assert i1 == i2

    def test_frozen(self, mapper):
        row = _row("A", "X")
        with pytest.raises(FrozenInstanceError):
            row.symbol = "B"  # type: ignore[misc]
        index, _ = mapper.build([row])
        with pytest.raises(FrozenInstanceError):
            index.row_count = 9  # type: ignore[misc]
