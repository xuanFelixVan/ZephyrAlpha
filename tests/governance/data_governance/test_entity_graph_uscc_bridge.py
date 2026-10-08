# [TESTS] tests/governance/data_governance/test_entity_graph_uscc_bridge.py | §uscc 消歧桥单测（mock 连接层，零真实 PG，C122）
# [MODULE] tests.governance.data_governance.test_entity_graph_uscc_bridge
# [DOMAIN] D_GOV_DATA
# [DEPENDENCIES] pytest；zephyr.governance.data_governance.entity_graph_uscc_bridge
# [CONSUMERS] pytest 收编面（W3 循环检查）
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] mock DB（内存行表+假 cursor），零真实 PG 连接零生产路径写入；只测提案语义不测施写（桥零写）
# [TESTS] self
# [A_module] module_id=TEST-USCC-BRIDGE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""entity_graph_uscc_bridge 单测（mock DB）：四态提案/规范化/人物骨架立法。"""

from __future__ import annotations

from typing import Any

import pytest

from zephyr.governance.data_governance.entity_graph_uscc_bridge import (
    CompanyEnrichmentProposal,
    normalize_cn_company_name,
    propose_company_enrichment,
    propose_person_identity,
)


class _FakeCursor:
    """内存行表假 cursor：按 SQL 首词路由（node_company 两查询面）。"""

    def __init__(self, table: list[dict[str, Any]]):
        self._table = table
        self._rows: list[tuple] = []

    def execute(self, sql: str, params: tuple) -> None:  # noqa: ARG002 — 形参对齐 DB-API
        self._rows = []
        if "WHERE uscc" in sql:
            uscc = params[0]
            self._rows = [r for r in self._table if r["uscc"] == uscc][:2]
        elif "WHERE name_norm" in sql:
            norm = params[0]
            self._rows = [r for r in self._table if r["name_norm"] == norm][:5]

    def fetchall(self) -> list[tuple]:
        return [(r["entity_id"], r["uscc"], r["name"], r["name_norm"]) for r in self._rows]

    def __enter__(self) -> _FakeCursor:
        return self

    def __exit__(self, *exc: object) -> None:
        return None


class _FakeConn:
    def __init__(self, table: list[dict[str, Any]]):
        self._table = table

    def cursor(self) -> _FakeCursor:
        return _FakeCursor(self._table)


TABLE = [
    {"entity_id": "e1", "uscc": "913200001U", "name": "济川药业集团股份有限公司", "name_norm": "济川药业"},
    {"entity_id": "e2", "uscc": "91330000IJ", "name": "济川控股（集团）股份有限公司", "name_norm": "济川控股"},
]


@pytest.fixture()
def conn() -> _FakeConn:
    return _FakeConn([dict(r) for r in TABLE])


def test_normalize_strips_org_suffix_and_width() -> None:
    assert normalize_cn_company_name("江苏济川控股集团有限公司") == "江苏济川控股"
    assert normalize_cn_company_name("济川控股（集团）股份有限公司") == "济川控股"
    assert normalize_cn_company_name("  济川 药业  ") == "济川药业"


def test_uscc_hint_direct(conn: _FakeConn) -> None:
    """上游 uscc 直键 → verdict=uscc_direct，confidence=1.0。"""
    props = propose_company_enrichment(
        conn, ["济川药业集团股份有限公司"], uscc_hints={"济川药业集团股份有限公司": "913200001U"}
    )
    assert props[0].verdict == "uscc_direct"
    assert props[0].confidence == 1.0
    assert props[0].matched_entity_id == "e1"


def test_norm_unique_match(conn: _FakeConn) -> None:
    """name_norm 唯一命中 → norm_unique/0.9（跨全角括号+后缀差异仍命中）。"""
    props = propose_company_enrichment(conn, ["济川控股集团股份有限公司"])
    assert props[0].verdict == "norm_unique"
    assert props[0].confidence == 0.9
    assert props[0].matched_uscc == "91330000IJ"


def test_unresolved_when_no_row(conn: _FakeConn) -> None:
    """零命中 → unresolved（B/C/D 层富化入口），非异常。"""
    props = propose_company_enrichment(conn, ["不存在的公司无限责任社"])
    assert props[0].verdict == "unresolved"
    assert props[0].confidence == 0.0


def test_ambiguous_lists_candidates(conn: _FakeConn) -> None:
    """多义 → ambiguous 附候选列表，禁自动择一。"""
    dup = TABLE + [dict(TABLE[0], entity_id="e9", uscc="91320000DUP")]
    props = propose_company_enrichment(_FakeConn(dup), ["济川药业集团股份有限公司"])
    assert props[0].verdict == "ambiguous"
    assert len(props[0].candidates) == 2


def test_proposals_are_dataclass_only_no_write(conn: _FakeConn) -> None:
    """提案=冻结 dataclass（桥零写语义的型别保证）。"""
    props = propose_company_enrichment(conn, ["济川控股"])
    assert isinstance(props[0], CompanyEnrichmentProposal)
    with pytest.raises(Exception):  # frozen=True 施写不可变
        props[0].matched_uscc = "tampered"  # type: ignore[misc]


def test_person_skeleton_not_ready_and_evidence_count() -> None:
    """人物消歧骨架：恒 NotReady；三证据计数正确（立法=宁挂起勿错并）。"""
    weak = propose_person_identity("张三")
    strong = propose_person_identity("张三", birth_year=1970, career_track_hash="h1", company_overlap=frozenset({"e1"}))
    assert weak["status"] == "not_ready" and weak["strong_evidence_count"] == 0
    assert strong["strong_evidence_count"] == 3
