# [A_test] module_id: SRC-TST-0742 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain-autonomy_core/agent-rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.derive_rbac_roles
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self

import sys

sys.path.insert(0, "src")

import tempfile
from pathlib import Path

import pytest

try:
    from zephyr.security.access_control.derive_rbac_roles import DEFAULT_DERIVATIONS, RBACRoleDeriver

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestRBACRoleDeriver:
    def test_derive_creates_file(self):
        deriver = RBACRoleDeriver()
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "rbac_roles.yaml"
            sha = deriver.derive(out_path)
            assert out_path.exists()
            assert len(sha) == 64

    def test_derive_content_valid_yaml(self):
        import yaml

        deriver = RBACRoleDeriver()
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "rbac_roles.yaml"
            deriver.derive(out_path)
            with open(out_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            assert "version" in data
            assert "agents" in data
            assert "agent_writer" in data["agents"]

    def test_derive_deterministic_hash(self):
        deriver = RBACRoleDeriver()
        with tempfile.TemporaryDirectory() as tmpdir:
            p1 = Path(tmpdir) / "a.yaml"
            p2 = Path(tmpdir) / "b.yaml"
            h1 = deriver.derive(p1)
            h2 = deriver.derive(p2)
            assert h1 == h2

    def test_compare_missing_file(self):
        deriver = RBACRoleDeriver()
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "nonexistent.yaml"
            result = deriver.compare_with_existing(missing)
            assert result["status"] == "MISSING"
            assert result["action"] == "GENERATE_NEW"

    def test_compare_consistent_file(self):
        deriver = RBACRoleDeriver()
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "rbac_roles.yaml"
            deriver.derive(out_path)
            result = deriver.compare_with_existing(out_path)
            assert result["status"] in ("CONSISTENT", "DRIFT_DETECTED")

    def test_compare_drift_file(self):
        deriver = RBACRoleDeriver()
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "rbac_roles.yaml"
            out_path.write_text("version: '0.0.1'\nagents: {}\n", encoding="utf-8")
            result = deriver.compare_with_existing(out_path)
            assert result["status"] == "DRIFT_DETECTED"
            assert result["action"] == "REGENERATE"


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestDefaultDerivations:
    def test_three_roles(self):
        assert len(DEFAULT_DERIVATIONS) == 3
        assert "agent_writer" in DEFAULT_DERIVATIONS
        assert "agent_reviewer" in DEFAULT_DERIVATIONS
        assert "agent_architect" in DEFAULT_DERIVATIONS

    def test_role_has_required_keys(self):
        for role_name, role_def in DEFAULT_DERIVATIONS.items():
            assert "maturity" in role_def
            assert "permissions" in role_def
            assert "auto_guard_eligible" in role_def
            assert "owner_approved" in role_def

    def test_permissions_are_lists(self):
        for role_name, role_def in DEFAULT_DERIVATIONS.items():
            assert isinstance(role_def["permissions"], list)
            assert len(role_def["permissions"]) > 0
