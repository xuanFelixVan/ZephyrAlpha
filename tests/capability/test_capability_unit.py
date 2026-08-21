# [A_test] module_id: MOD-GOV_capability_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-600 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_capability
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest

from zephyr.shared.security.capability import (
    Capability,
    CapabilityDenied,
    CapabilityRegistry,
    capability_check,
)


@pytest.fixture(autouse=True)
def reset_registry():
    CapabilityRegistry.reset()
    yield
    CapabilityRegistry.reset()


class TestCapability:
    def test_frozen_model(self):
        cap = Capability(name="test", allow=["a"], deny=["b"])
        with pytest.raises(Exception):
            cap.name = "changed"

    def test_defaults(self):
        cap = Capability(name="test")
        assert cap.allow == []
        assert cap.deny == []


class TestCapabilityRegistry:
    def test_load_from_yaml(self, tmp_path: Path):
        yaml_path = tmp_path / "capabilities.yaml"
        yaml_path.write_text(
            textwrap.dedent("""\
            rules:
              - name: write_src
                description: "AI can write src"
                allow:
                  - "src/zephyr/l02-alpha-factor/**/*.py"
                deny:
                  - "src/zephyr/l04-risk-management/**/*.py"
            """),
            encoding="utf-8",
        )
        with patch("zephyr.shared.security.capability.CAPABILITIES_YAML_PATH", yaml_path):
            registry = CapabilityRegistry()
            assert len(registry.capabilities) == 1
            assert registry.capabilities[0].name == "write_src"

    @pytest.mark.filterwarnings("ignore::UserWarning")
    def test_missing_yaml(self, tmp_path: Path):
        yaml_path = tmp_path / "nonexistent.yaml"
        with patch("zephyr.shared.security.capability.CAPABILITIES_YAML_PATH", yaml_path):
            registry = CapabilityRegistry()
            assert len(registry.capabilities) == 0

    @pytest.mark.filterwarnings("ignore::UserWarning")
    def test_singleton(self, tmp_path: Path):
        yaml_path = tmp_path / "capabilities.yaml"
        yaml_path.write_text(
            "rules:\n  - name: test\n    allow: []\n    deny: []\n",
            encoding="utf-8",
        )
        with patch("zephyr.shared.security.capability.CAPABILITIES_YAML_PATH", yaml_path):
            r1 = CapabilityRegistry()
            r2 = CapabilityRegistry()
            assert r1 is r2

    @pytest.mark.filterwarnings("ignore::UserWarning")
    def test_reset(self, tmp_path: Path):
        yaml_path = tmp_path / "capabilities.yaml"
        yaml_path.write_text(
            "rules:\n  - name: test\n    allow: []\n    deny: []\n",
            encoding="utf-8",
        )
        with patch("zephyr.shared.security.capability.CAPABILITIES_YAML_PATH", yaml_path):
            r1 = CapabilityRegistry()
            CapabilityRegistry.reset()
            r2 = CapabilityRegistry()
            assert r1 is not r2


class TestCapabilityCheck:
    def _make_registry(self, tmp_path: Path, rules_yaml: str) -> CapabilityRegistry:
        yaml_path = tmp_path / "capabilities.yaml"
        yaml_path.write_text(rules_yaml, encoding="utf-8")
        CapabilityRegistry.reset()
        with patch("zephyr.shared.security.capability.CAPABILITIES_YAML_PATH", yaml_path):
            return CapabilityRegistry()

    def test_allow_match(self, tmp_path: Path):
        registry = self._make_registry(
            tmp_path,
            textwrap.dedent("""\
            rules:
              - name: write_src
                allow:
                  - "src/zephyr/l02-alpha-factor/**/*.py"
                deny: []
        """),
        )
        allowed, info = registry.check("write", "src/zephyr/l02-alpha-factor/factor.py")
        assert allowed is True
        assert info["provenance"] is True

    def test_allow_overrides_deny_within_same_rule(self, tmp_path: Path):
        registry = self._make_registry(
            tmp_path,
            textwrap.dedent("""\
            rules:
              - name: write_src
                allow:
                  - "src/zephyr/l02-alpha-factor/**/*.py"
                deny:
                  - "src/zephyr/l02-alpha-factor/secret.py"
        """),
        )
        allowed, info = registry.check("write", "src/zephyr/l02-alpha-factor/secret.py")
        assert allowed is True
        assert info["reason"] == "allow"

    def test_default_deny(self, tmp_path: Path):
        registry = self._make_registry(
            tmp_path,
            textwrap.dedent("""\
            rules:
              - name: write_src
                allow:
                  - "src/zephyr/l02-alpha-factor/**/*.py"
                deny: []
        """),
        )
        allowed, info = registry.check("write", "src/zephyr/risk/stop_loss.py")
        assert allowed is False
        assert info["reason"] == "no_matching_rule"

    def test_deny_raises_capability_denied(self, tmp_path: Path):
        yaml_path = tmp_path / "capabilities.yaml"
        yaml_path.write_text(
            textwrap.dedent("""\
            rules:
              - name: write_src
                allow: []
                deny:
                  - "src/zephyr/l04-risk-management/**/*.py"
            """),
            encoding="utf-8",
        )
        with patch("zephyr.shared.security.capability.CAPABILITIES_YAML_PATH", yaml_path):
            with pytest.raises(CapabilityDenied) as exc_info:
                capability_check("write", "src/zephyr/l04-risk-management/risk/stop_loss.py")
            assert "write_src" in str(exc_info.value)
            assert "deny" in str(exc_info.value)

    def test_glob_star_star(self, tmp_path: Path):
        registry = self._make_registry(
            tmp_path,
            textwrap.dedent("""\
            rules:
              - name: write_src
                allow:
                  - "src/zephyr/l02-alpha-factor/**/*.py"
                deny: []
        """),
        )
        allowed, _ = registry.check("write", "src/zephyr/l02-alpha-factor/sub/deep.py")
        assert allowed is True

    def test_path_outside_repo(self, tmp_path: Path):
        registry = self._make_registry(
            tmp_path,
            textwrap.dedent("""\
            rules:
              - name: write_src
                allow:
                  - "src/**/*.py"
                deny: []
        """),
        )
        allowed, info = registry.check("write", "/etc/passwd")
        assert allowed is False
