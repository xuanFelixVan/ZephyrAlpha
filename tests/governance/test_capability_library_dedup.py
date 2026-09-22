# [A_test] module_id: MOD-GOVERNANCE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §1
# [MODULE] tests.governance.test_capability_library_dedup
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_capability_library_dedup.py — 能力反查×图书馆查重留痕单测（ulib3 T6）

权威依据：capability_lookup.py（_library_dedup_probe / write_lookup_audit_log / find）

测试组：
- 探针成功：审计行含 library_dedup.hits/asset_ids
- 探针失败（lookup_assets 抛异常）：library_dedup 缺席（fail-open 不影响反查）
- 短查询守卫不触发探针
- write_lookup_audit_log library_dedup=None 时字段缺席（向后兼容）

测试隔离：monkeypatch lookup_assets + tmp_path 审计目录，零真实 PG 依赖。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import zephyr.governance.capability_lookup as cl  # noqa: E402


@pytest.fixture()
def audit_dir(tmp_path, monkeypatch):
    d = tmp_path / "lookup_audit"
    monkeypatch.setattr(cl, "LOOKUP_AUDIT_DIR", d)
    return d


@pytest.fixture(scope="class")
def lookup() -> cl.CapabilityLookup:
    """共享单实例（CapabilityLookup 构造需全量扫盘，单测内只建一次）。
    find() 是只读查询，实例间无状态，共享安全。"""
    return cl.CapabilityLookup()


def _last_entry(d: Path, sid: str) -> dict:
    return json.loads((d / f"{sid}.jsonl").read_text(encoding="utf-8").strip().splitlines()[-1])


class TestLibraryDedup:
    def test_probe_success_recorded(self, audit_dir, monkeypatch):
        monkeypatch.setattr(
            cl, "_library_dedup_probe", lambda q, limit=5: {"hits": 2, "asset_ids": ["MOD:x", "FILE:y"]}
        )
        cl.write_lookup_audit_log(
            session_id="s1", query={"query": "k"}, result_count=1, capability_ids=["c1"],
            library_dedup={"hits": 2, "asset_ids": ["MOD:x", "FILE:y"]},
        )
        entry = _last_entry(audit_dir, "s1")
        assert entry["library_dedup"]["hits"] == 2
        assert "MOD:x" in entry["library_dedup"]["asset_ids"]

    def test_probe_none_omitted(self, audit_dir):
        cl.write_lookup_audit_log(
            session_id="s2", query={"query": "k"}, result_count=0, capability_ids=[],
        )
        entry = _last_entry(audit_dir, "s2")
        assert "library_dedup" not in entry  # 向后兼容

    def test_find_passes_dedup_probe(self, audit_dir, lookup, monkeypatch):
        captured = {}

        def _fake_probe(query, limit=5):
            captured["q"] = query
            return {"hits": 0, "asset_ids": []}

        monkeypatch.setattr(cl, "_library_dedup_probe", _fake_probe)
        lookup.find("session handoff probe-xyz", session_id="s3")
        assert captured["q"] == "session handoff probe-xyz"
        entry = _last_entry(audit_dir, "s3")
        assert entry["library_dedup"] == {"hits": 0, "asset_ids": []}

    def test_probe_failure_fail_open(self, audit_dir, lookup, monkeypatch):
        def _boom(query, limit=5):
            raise RuntimeError("pg down")

        monkeypatch.setattr(cl, "_library_dedup_probe", _boom)
        results = lookup.find("translation coverage gate", session_id="s4")
        assert isinstance(results, list)  # 反查主路径不受探针故障影响
        entry = _last_entry(audit_dir, "s4")
        assert "library_dedup" not in entry

    def test_short_query_no_probe(self, audit_dir, lookup, monkeypatch):
        called = []
        monkeypatch.setattr(cl, "_library_dedup_probe", lambda q, limit=5: called.append(q))
        assert lookup.find("a", session_id="s5") == []  # 退化查询守卫
        assert called == []  # 探针未触发
