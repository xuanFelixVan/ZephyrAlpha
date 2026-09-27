# [A_test] module_id: MOD-TEST-detect-retirement | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOVERNANCE | scripts/governance/d5_architecture/lifecycle/detect_retirement_candidates.py | §
# [MODULE] tests.governance.lifecycle.test_detect_retirement_candidates
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-detect-retirement | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""detect_retirement_candidates.py 红蓝夹具（B10-P1）——四路机械探测。

蓝：四路全零→候选 / 评分与档位 / 报告生成 / P0 只提示不入候选。
红（保守性）：任一路未知（None）→不入候选；白名单命中→不入候选；非 active→不入候选。
tmp_path 全隔离，假 conn 注入，零触生产 PG。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[3]
_SPEC = importlib.util.spec_from_file_location(
    "detect_retirement_candidates_under_test",
    _REPO / "scripts/governance/d5_architecture/lifecycle/detect_retirement_candidates.py",
)
DET = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = DET  # dataclass 解析延迟注解需要 sys.modules 注册
_SPEC.loader.exec_module(DET)


class FakeConn:
    """假 depgraph/lib 连接：execute(sql, params) 返回预置行。"""

    def __init__(self, rows_by_sql: dict[str, list[dict]]):
        self._rows = rows_by_sql
        self.queries: list[str] = []

    def execute(self, sql: str, params=None):
        self.queries.append(sql)
        rows = self._rows.get("edges" if "FROM nodes" in sql else "lib", [])
        holder: dict = {"rows": rows}

        class _Cur:
            def fetchall(self, _h=holder):
                return _h["rows"]

        return _Cur()


def _ev(**kw) -> DET.Evidence:
    base = dict(
        r_d=0, g_d=100, p_d=None, c_d=0, sources_ok={"depgraph": True, "library": True, "git": True, "capability": True}
    )
    base.update(kw)
    return DET.Evidence(**base)


def _entry(mid: str, status: str = "active", path: str = "docs/x.md") -> dict:
    return {"module_id": mid, "status": status, "path": path}


# ---------- 蓝：候选公式 ----------


def test_all_zero_signals_active_is_candidate():
    row = DET.evaluate_module(_entry("MOD-A"), _ev())
    assert row.is_candidate and row.score == 6 and "候选-B" in row.tier


def test_very_stale_boosts_score_and_tier():
    row = DET.evaluate_module(_entry("MOD-A"), _ev(g_d=400))
    assert row.is_candidate and row.score == 7 and "候选-A" in row.tier


def test_score_components():
    row = DET.evaluate_module(_entry("MOD-A"), _ev(r_d=3, g_d=30, p_d=2, c_d=1))
    assert row.score == 0 and not row.is_candidate
    row2 = DET.evaluate_module(_entry("MOD-A"), _ev(r_d=0, g_d=95, p_d=None, c_d=0))
    assert row2.score == 6


# ---------- 红：保守性（未知不判零） ----------


def test_unknown_depgraph_blocks_candidate():
    row = DET.evaluate_module(_entry("MOD-A"), _ev(r_d=None))
    assert not row.is_candidate


def test_unknown_git_blocks_candidate():
    row = DET.evaluate_module(_entry("MOD-A"), _ev(g_d=None))
    assert not row.is_candidate


def test_unknown_capability_blocks_candidate():
    row = DET.evaluate_module(_entry("MOD-A"), _ev(c_d=None))
    assert not row.is_candidate


def test_library_null_treated_as_zero_but_positive_blocks():
    assert DET.evaluate_module(_entry("MOD-A"), _ev(p_d=None)).is_candidate
    assert not DET.evaluate_module(_entry("MOD-A"), _ev(p_d=2)).is_candidate


def test_non_active_status_never_candidate():
    assert not DET.evaluate_module(_entry("MOD-A", status="deprecated"), _ev()).is_candidate
    assert not DET.evaluate_module(_entry("MOD-A", status="draft"), _ev()).is_candidate


def test_whitelist_hit_blocks_candidate():
    row = DET.evaluate_module(_entry("MOD-A"), _ev(whitelist=["high 风险域（D_X）"]))
    assert not row.is_candidate and row.score == 6


def test_p0_never_candidate_only_hint():
    row = DET.evaluate_module(_entry("MOD-A"), _ev(p0=True, whitelist=["P0 红线"]))
    assert not row.is_candidate and row.tier.startswith("P0")


# ---------- 数据源函数（假 conn 注入） ----------


def test_fetch_depgraph_inedges_groups_by_module():
    conn = FakeConn(
        {
            "edges": [
                {"bid": "MOD-A", "bel": "", "dom": "D_X", "c": 2},
                {"bid": "", "bel": "MOD-A", "dom": "D_X", "c": 1},
                {"bid": "MOD-B", "bel": "", "dom": "D_Y", "c": 0},
            ]
        }
    )
    edges, domains, ok = DET.fetch_depgraph_inedges(conn)
    assert ok and edges["MOD-A"] == 3 and edges["MOD-B"] == 0 and domains["MOD-A"] == ["D_X"]


def test_fetch_depgraph_unavailable_returns_unknown():
    edges, domains, ok = DET.fetch_depgraph_inedges(None)
    assert edges == {} and not ok


def test_fetch_library_consumers_matching():
    conn = FakeConn({"lib": [{"asset_id": "DOC-1", "c": 3}, {"asset_id": "DOC-2", "c": 0}]})
    best, assets, ok = DET.fetch_library_consumers(conn, "MOD-A", "docs/x.md")
    assert ok and best == 3 and assets == ["DOC-1", "DOC-2"]
    empty = FakeConn({"lib": []})
    best2, assets2, ok2 = DET.fetch_library_consumers(empty, "MOD-A", "docs/x.md")
    assert ok2 and best2 is None and assets2 == []
    best3, _, ok3 = DET.fetch_library_consumers(None, "MOD-A", "docs/x.md")
    assert best3 is None and not ok3


def test_load_capability_canonical_paths(tmp_path: Path):
    p = tmp_path / "cap.yaml"
    p.write_text(
        "capabilities:\n"
        "- capability_id: a\n  canonical_override: docs/a_policy.md\n"
        "- capability_id: b\n  canonical_override: src/b.py\n",
        encoding="utf-8",
    )
    paths, ok = DET.load_capability_canonical_paths(p)
    assert ok and paths == {"docs/a_policy.md", "src/b.py"}
    missing, ok2 = DET.load_capability_canonical_paths(tmp_path / "nope.yaml")
    assert missing == set() and not ok2  # 源不可用→保守


def test_load_risk_tier_high_domains(tmp_path: Path):
    p = tmp_path / "risk.yaml"
    p.write_text(
        "domain_tiers:\n- domain: D_EX_CORE\n  tier: high\n- domain: D_DOCS\n  tier: low\n",
        encoding="utf-8",
    )
    highs, ok = DET.load_risk_tier_high_domains(p)
    assert ok and highs == {"D_EX_CORE"}


def test_detect_p0_frontmatter_and_extra(tmp_path: Path):
    mod_file = tmp_path / "docs" / "m.md"
    mod_file.parent.mkdir(parents=True)
    mod_file.write_text("---\npriority: P0\nstatus: active\n---\nbody", encoding="utf-8")
    cand = tmp_path / "candidates.yaml"
    cand.write_text("candidates: []\n", encoding="utf-8")
    hit, sources = DET.detect_p0("MOD-P", "docs/m.md", tmp_path, cand, [])
    assert hit and sources == ["frontmatter-priority"]
    hit2, sources2 = DET.detect_p0("MOD-Q", "docs/q.md", tmp_path, cand, ["MOD-Q"])
    assert hit2 and "owner-extra" in sources2


def test_detect_p0_candidate_registry(tmp_path: Path):
    cand = tmp_path / "candidates.yaml"
    cand.write_text(
        "candidates:\n"
        "- candidate_id: CAND-1\n  priority: P0\n  module_id: MOD-R\n  path: docs/r.md\n"
        "- candidate_id: CAND-2\n  priority: P2\n  module_id: MOD-S\n",
        encoding="utf-8",
    )
    hit, sources = DET.detect_p0("MOD-R", "docs/r.md", tmp_path, cand, [])
    assert hit and sources == ["candidate-registry-P0"]
    hit2, _ = DET.detect_p0("MOD-S", "docs/s.md", tmp_path, cand, [])
    assert not hit2


# ---------- 报告与落点 ----------


def test_build_report_sections():
    cand = DET.evaluate_module(_entry("MOD-C"), _ev(g_d=400))
    watcher = DET.evaluate_module(_entry("MOD-W"), _ev(r_d=5, g_d=400))
    p0 = DET.evaluate_module(_entry("MOD-P0"), _ev(p0=True, whitelist=["P0 红线"]))
    report = DET.build_report([cand, watcher, p0], top=10, generated_at="2026-09-27 TEST")
    assert "## Top-" in report and "MOD-C" in report
    assert "证据链摘要" in report and "depgraph 入边=0" in report
    assert "P0 提示" in report and "MOD-P0" in report
    assert "观察名单" in report and "MOD-W" in report


def test_staging_report_path_hygiene():
    p = DET.staging_report_path(Path("D:/repo"), "sess-x")
    parts = p.parts
    assert ".runtime" in parts and "sessions" in parts and "sess-x" in parts and "staging" in parts
    assert p.suffix == ".md"


def test_load_registry_modules(tmp_path: Path):
    p = tmp_path / "reg.yaml"
    p.write_text(
        "total_registered: 2\n"
        "registered_ids:\n"
        "  - module_id: MOD-A\n    status: active\n    path: docs/a.md\n"
        "  - module_id: MOD-B\n    status: deprecated\n",
        encoding="utf-8",
    )
    entries = DET.load_registry_modules(p)
    assert len(entries) == 2 and entries[0]["module_id"] == "MOD-A"
