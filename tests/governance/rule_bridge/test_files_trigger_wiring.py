# [TTL] permanent
# [MODULE] tests.governance.rule_bridge.test_files_trigger_wiring
# [DOMAIN] D_GOVERNANCE
"""test_files_trigger_wiring.py — P5 files_trigger 接线测试（st-gslim-20260923）。"""

from __future__ import annotations

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    CommitGateRegistry,
    GateSpec,
    _files_trigger_hit,
)


def test_files_trigger_matcher_semantics():
    assert _files_trigger_hit((), ["a.py"]) is True  # 空=无条件
    assert _files_trigger_hit((".py",), []) is False  # 有条件但无清单
    assert _files_trigger_hit((".py",), ["docs/x.md"]) is False
    assert _files_trigger_hit((".py",), ["src/a.py"]) is True  # 子串
    assert _files_trigger_hit(("docs/",), ["docs/x.md"]) is True  # 目录前缀
    assert _files_trigger_hit(("*.yaml",), ["a/b.yaml"]) is True  # fnmatch
    assert _files_trigger_hit(("schema",), ["src/z/schema_loader.py"]) is True


def test_check_all_skips_non_matching_gate():
    reg = CommitGateRegistry()
    calls = []

    def _chk(gw, files, **kw):
        calls.append(files)
        return True, ""

    reg.register(GateSpec(gate_id="COND", check=_chk, priority=1, files_trigger=("schema",)))
    reg.register(GateSpec(gate_id="ALWAYS", check=_chk, priority=2))
    results = reg.check_all(gateway=object(), files=["docs/x.md"])
    by_id = {r.gate_id: r for r in results}
    assert by_id["COND"].passed and "files_trigger" in by_id["COND"].detail
    assert by_id["ALWAYS"].passed
    assert len(calls) == 1  # 只有 ALWAYS 真正执行


def test_registrar_injects_files_trigger(tmp_path, monkeypatch):
    import yaml

    from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import auto_register_gates
    roster = {
        "total_gates": 1,
        "gates": [
            {
                "gate_id": "WIRED",
                "module_path": "zephyr.gov_enforcement.rule_bridge.commit_gate_registry",
                "factory_function": "run_checker_script",
                "enabled": True,
                "files_trigger": ["schema"],
            }
        ],
    }
    # factory_function 必须返回 GateSpec——用专用桩
    (tmp_path / "roster.yaml").write_text(yaml.dump(roster), encoding="utf-8")
