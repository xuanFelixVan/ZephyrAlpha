# [A_test] module_id: MOD-LIB-007 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LIB-007 | docs/03_modules/_domain_library/blueprint.md | §7
# [MODULE] tests.ai.library.test_ruling_precedent
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-LIB-007 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_ruling_precedent.py — 裁定先例机检 CLI 单测（MOD-LIB-007）

测试组：
- classify_ruling：显式 route_class 优先 / 关键词面主类+证据 / 未归类
- search：类命中=全命中集（召回优先）/ status / query 子串 / limit
- run_cli：零命中 rc=1 附 E2 新类提示；无参=普查 rc=0
- E2 验收：#489/#494 实册样例主类命中 D1（裁定路由政策 §2.2；册缺条目则 skip）

测试隔离：合成条目走 tmp_path YAML；实册只读零写入。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import zephyr.library.ruling_precedent as g  # noqa: E402


def _write_registry(tmp_path: Path, entries: list[dict]) -> Path:
    import yaml

    p = tmp_path / "ruling_registry.yaml"
    p.write_text(yaml.safe_dump({"entries": entries}, allow_unicode=True), encoding="utf-8")
    return p


_ENTRY_D1 = {
    "ruling_id": "裁定#9001",
    "title": "某指标退役处置",
    "summary": "证据=考试不过线，判定退役并留墓碑。",
    "status": "active",
    "date": "2026-10-01",
}
_ENTRY_EXPLICIT = {
    "ruling_id": "裁定#9002",
    "title": "阈值口径调整",
    "summary": "退役字样虽在，但本条登记为标准阈值。",
    "route_class": "D3",
    "status": "active",
    "date": "2026-10-02",
}
_ENTRY_NONE = {
    "ruling_id": "裁定#9003",
    "title": "会议纪要登记",
    "summary": "纯记录，无路由语义。",
    "status": "superseded",
    "date": "2026-10-03",
}


class TestClassify:
    def test_keyword_primary_and_evidence(self):
        primary, matched, evidence = g.classify_ruling(_ENTRY_D1)
        assert primary == "D1"
        assert "D1" in matched
        assert "退役" in evidence["D1"]

    def test_explicit_route_class_wins(self):
        primary, matched, evidence = g.classify_ruling(_ENTRY_EXPLICIT)
        assert primary == "D3"
        assert matched == ["D3"]
        assert evidence == {"显式": "D3"}

    def test_unclassified_is_empty(self):
        assert g.classify_ruling(_ENTRY_NONE) == ("", [], {})


class TestSearch:
    def test_class_filter_is_recall_first(self, tmp_path):
        reg = _write_registry(tmp_path, [_ENTRY_D1, _ENTRY_EXPLICIT, _ENTRY_NONE])
        rows = g.search("", route_class="D1", registry_path=reg)
        assert [r["entry"]["ruling_id"] for r in rows] == ["裁定#9001"]

    def test_status_and_query_filter(self, tmp_path):
        reg = _write_registry(tmp_path, [_ENTRY_D1, _ENTRY_EXPLICIT, _ENTRY_NONE])
        assert [r["entry"]["ruling_id"] for r in g.search("", status="superseded", registry_path=reg)] == ["裁定#9003"]
        assert [r["entry"]["ruling_id"] for r in g.search("9002", registry_path=reg)] == ["裁定#9002"]
        assert g.search("不存在的词", registry_path=reg) == []

    def test_limit_clamped(self, tmp_path):
        reg = _write_registry(tmp_path, [_ENTRY_D1])
        assert len(g.search("", registry_path=reg, limit=0)) == 1  # 下限钳 1


class TestCli:
    def test_zero_result_rc1_with_e2_hint(self, tmp_path, capsys, monkeypatch):
        reg = _write_registry(tmp_path, [_ENTRY_NONE])
        _orig = g.load_rulings
        monkeypatch.setattr(g, "load_rulings", lambda path=None: _orig(reg))
        assert g.run_cli(["不存在的词", "--class", "D1"]) == 1
        out = capsys.readouterr().out
        assert "零先例" in out and "新类" in out

    def test_no_args_census_rc0(self, tmp_path, capsys, monkeypatch):
        reg = _write_registry(tmp_path, [_ENTRY_D1, _ENTRY_NONE])
        _orig = g.load_rulings
        monkeypatch.setattr(g, "load_rulings", lambda path=None: _orig(reg))
        assert g.run_cli([]) == 0
        out = capsys.readouterr().out
        assert "D1 生死处置: 1 条" in out and "未归类: 1 条" in out

    def test_query_face_parses_class_prefix(self, tmp_path, monkeypatch):
        reg = _write_registry(tmp_path, [_ENTRY_D1])
        _orig = g.load_rulings
        monkeypatch.setattr(g, "load_rulings", lambda path=None: _orig(reg))
        assert g.query_face("D1 退役") == 0
        assert g.query_face("无命中词xyz") == 1


class TestE2Acceptance:
    """裁定路由政策 v2 E2 验收样例（Owner 令：#489/#494 命中正确类）。"""

    def test_489_494_primary_d1(self):
        try:
            entries = g.load_rulings()
        except SystemExit:
            pytest.skip("裁定册不在盘（真源 REG-RULING-001 投影缺失）")
        by_id = {str(e.get("ruling_id")): e for e in entries}
        for rid in ("裁定#489", "裁定#494"):
            if rid not in by_id:
                pytest.skip(f"{rid} 不在册")
            primary, matched, evidence = g.classify_ruling(by_id[rid])
            assert primary == "D1", (rid, primary, matched, evidence)
            assert "D1" in evidence
