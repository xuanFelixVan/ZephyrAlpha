# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_spec_sync
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: SpecSync"""

from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.spec_sync import SpecSync


def test_register_and_check():
    s = SpecSync()
    s.register("mod-1", "blueprints/mod-1.md", ["src/mod1.py", "src/mod1_helper.py"])
    result = s.check("mod-1")
    assert result["status"] == "synced"
    assert result["module_id"] == "mod-1"
    assert result["impl_count"] == 2


def test_check_not_registered():
    s = SpecSync()
    result = s.check("nonexistent")
    assert result["status"] == "not_registered"


def test_sync():
    s = SpecSync()
    s.register("mod-2", "blueprints/mod-2.md", ["src/mod2.py"])
    result = s.sync("mod-2")
    assert result == "synced"


def test_sync_not_found():
    s = SpecSync()
    result = s.sync("nonexistent")
    assert result == "not_found"


def test_list_drifted():
    s = SpecSync()
    s.register("mod-3", "bp.md", ["src/m3.py"])
    assert s.list_drifted() == []
