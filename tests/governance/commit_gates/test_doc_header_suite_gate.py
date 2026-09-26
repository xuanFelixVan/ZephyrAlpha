# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_doc_header_suite_gate
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [TESTS] self
"""test_doc_header_suite_gate.py — T8簇2 DOC-HEADER-SUITE 七台合一冒烟测试（st-commitspeed-pkg8-20260925）。

断言：
- 聚合门可构造，gate_id/priority 正确（77=BLUEPRINT-FORMAT 原槽位）。
- 7 吸收台薄工厂 gate_id/priority 逐一保真（历史测试与引用兼容）。
- 聚合检查对空输入全绿；子台失败时聚合 detail 带 [源台名] 前缀且任一失败即阻断。
- 名册 files_trigger 三台（COMPLEXITY-GUARD/FILE-COPY/FUNCTION-DUP）触发面保真。
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest
import yaml as _yaml

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec
from zephyr.shared.io.paths import REPO_ROOT

_SUITE_MOD = "blueprint_format_gate"
_CASES = [
    (_SUITE_MOD, "make_doc_header_suite_gate", "DOC-HEADER-SUITE", 77),
    # 7 吸收台薄工厂（gate_id/priority 保真——判据零退役的身份锚）
    ("blueprint_format_gate", "make_blueprint_format_gate", "BLUEPRINT-FORMAT", 130),
    ("blueprint_amodule_consistency_gate", "make_blueprint_header_gate", "BLUEPRINT-HEADER", 79),
    ("module_id_consistency_gate", "make_module_id_consistency_gate", "MODULE-ID-CONSISTENCY", 88),
    ("ttl_gate", "make_ttl_gate", "TTL-METADATA", 32),
    ("file_placement_ttl_gate", "make_file_placement_ttl_gate", "FILE-PLACEMENT-TTL", 33),
    ("exempt_zone_frontmatter_gate", "make_exempt_zone_frontmatter_gate", "EXEMPT-ZONE-FM", 87),
    ("doc_ref_broken_gate", "make_doc_ref_broken_gate", "DOC-REF-BROKEN", 91),
]


@pytest.mark.parametrize("module,factory,gate_id,priority", _CASES)
def test_gate_constructs(module, factory, gate_id, priority):
    mod = importlib.import_module(f"zephyr.gov_enforcement.commit_gates.{module}")
    spec = getattr(mod, factory)()
    assert isinstance(spec, GateSpec)
    assert spec.gate_id == gate_id
    assert spec.priority == priority
    assert callable(spec.check)


class _EmptyGitGateway:
    """最小 gateway 垫片：git 全部返回空输出（所有子判定应全绿）。"""

    project_root = REPO_ROOT

    def run_git(self, cmd, cwd=None):
        class _R:
            returncode = 0
            stdout = ""
            stderr = ""

        return _R()


def test_suite_all_green_on_empty():
    from zephyr.gov_enforcement.commit_gates.blueprint_format_gate import make_doc_header_suite_gate

    spec = make_doc_header_suite_gate()
    ok, detail = spec.check(_EmptyGitGateway(), [], session_id=None)
    assert ok is True, detail


def test_suite_aggregates_failure_with_source_prefix(monkeypatch):
    from zephyr.gov_enforcement.commit_gates import ttl_gate
    from zephyr.gov_enforcement.commit_gates.blueprint_format_gate import make_doc_header_suite_gate

    def _fail(gateway, files, **kwargs):
        return False, "TTL-METADATA 伪造违规（测试注入）"

    monkeypatch.setattr(ttl_gate, "_check", _fail)
    spec = make_doc_header_suite_gate()
    ok, detail = spec.check(_EmptyGitGateway(), [], session_id=None)
    assert ok is False
    assert "[TTL-METADATA] TTL-METADATA 伪造违规（测试注入）" in detail
    # 其余 6 台全绿：唯一失败段来自注入台
    assert detail.count("[") == 1


def test_roster_triggers_wired():
    """T8簇3：三台触发面自名册贯通（registrar 注入同口径）。"""
    roster = (
        Path(REPO_ROOT)
        / "docs"
        / "01_policies_and_standards"
        / "_registry"
        / "catalogs"
        / "in_process_gate_registry.yaml"
    )
    data = _yaml.safe_load(roster.read_text(encoding="utf-8"))
    tg = {g["gate_id"]: g.get("files_trigger") for g in data["gates"]}
    assert tg["COMPLEXITY-GUARD"] == [".py"]
    assert tg["FILE-COPY"] == [".py"]
    assert tg["FUNCTION-DUP"] == [".py"]
