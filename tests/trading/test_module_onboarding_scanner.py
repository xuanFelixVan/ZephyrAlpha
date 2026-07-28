# [A_test] module_id: MOD-GOV_module_onboarding_scanner | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_module_onboarding_scanner
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tests never raise; all assertions within pytest
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.trading.capability_registry import CapabilityRegistry
from zephyr.trading.module_onboarding_scanner import (
    ModuleDiscovery,
    ModuleOnboardingScanner,
    UnregisteredModule,
)


def _create_python_module(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestModuleDiscovery:
    def test_default_values(self) -> None:
        md = ModuleDiscovery(module_path="/a/b.py", module_name="b", package="a")
        assert md.has_class is False
        assert md.class_names == []
        assert md.has_public_functions is False
        assert md.function_names == []
        assert md.has_blueprint is False
        assert md.blueprint_path is None
        assert md.docstring is None
        assert md.imports == []


class TestUnregisteredModule:
    def test_default_values(self) -> None:
        md = ModuleDiscovery(module_path="/a/b.py", module_name="b", package="a")
        um = UnregisteredModule(discovery=md)
        assert um.reason == "new"
        assert um.priority == "P1"
        assert um.suggested_layer == "local"


class TestModuleOnboardingScannerInit:
    def test_init(self, tmp_path: Path) -> None:
        registry = CapabilityRegistry()
        scanner = ModuleOnboardingScanner(
            src_root=tmp_path / "src",
            blueprint_root=tmp_path / "blueprints",
            registry=registry,
        )
        assert scanner.src_root == tmp_path / "src"
        assert scanner.blueprint_root == tmp_path / "blueprints"


class TestScanFilesystem:
    def test_scan_nonexistent_src(self, tmp_path: Path) -> None:
        registry = CapabilityRegistry()
        scanner = ModuleOnboardingScanner(
            src_root=tmp_path / "nonexistent",
            blueprint_root=tmp_path / "bp",
            registry=registry,
        )
        assert scanner.scan_filesystem() == []

    def test_scan_finds_modules_with_classes(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        _create_python_module(
            src / "mypackage" / "mymodule.py",
            "class MyClass:\n    def method(self):\n        return 1\n",
        )
        registry = CapabilityRegistry()
        scanner = ModuleOnboardingScanner(src_root=src, blueprint_root=tmp_path / "bp", registry=registry)
        discoveries = scanner.scan_filesystem()
        assert len(discoveries) == 1
        assert discoveries[0].has_class is True
        assert "MyClass" in discoveries[0].class_names
        assert discoveries[0].package == "mypackage"

    def test_scan_finds_modules_with_public_functions(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        _create_python_module(
            src / "pkg" / "utils.py",
            "def public_func():\n    return 42\n\ndef _private_func():\n    return 0\n",
        )
        registry = CapabilityRegistry()
        scanner = ModuleOnboardingScanner(src_root=src, blueprint_root=tmp_path / "bp", registry=registry)
        discoveries = scanner.scan_filesystem()
        assert len(discoveries) == 1
        assert discoveries[0].has_public_functions is True
        assert "public_func" in discoveries[0].function_names
        assert "_private_func" not in discoveries[0].function_names

    def test_scan_skips_init_files(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        _create_python_module(
            src / "pkg" / "__init__.py",
            "class InInit:\n    pass\n",
        )
        registry = CapabilityRegistry()
        scanner = ModuleOnboardingScanner(src_root=src, blueprint_root=tmp_path / "bp", registry=registry)
        discoveries = scanner.scan_filesystem()
        assert len(discoveries) == 0

    def test_scan_skips_runtime_modules(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        _create_python_module(
            src / "zephyr" / "runtime" / "some_module.py",
            "class SomeClass:\n    pass\n",
        )
        registry = CapabilityRegistry()
        scanner = ModuleOnboardingScanner(src_root=src, blueprint_root=tmp_path / "bp", registry=registry)
        discoveries = scanner.scan_filesystem()
        assert len(discoveries) == 0

    def test_scan_skips_modules_without_class_or_function(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        _create_python_module(
            src / "pkg" / "constants.py",
            "X = 1\nY = 2\n",
        )
        registry = CapabilityRegistry()
        scanner = ModuleOnboardingScanner(src_root=src, blueprint_root=tmp_path / "bp", registry=registry)
        discoveries = scanner.scan_filesystem()
        assert len(discoveries) == 0

    def test_scan_extracts_docstring(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        _create_python_module(
            src / "pkg" / "documented.py",
            '"""Module docstring."""\n\nclass Foo:\n    pass\n',
        )
        registry = CapabilityRegistry()
        scanner = ModuleOnboardingScanner(src_root=src, blueprint_root=tmp_path / "bp", registry=registry)
        discoveries = scanner.scan_filesystem()
        assert len(discoveries) == 1
        assert discoveries[0].docstring == "Module docstring."

    def test_scan_extracts_imports(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        _create_python_module(
            src / "pkg" / "importer.py",
            "import os\nfrom pathlib import Path\n\nclass Importer:\n    pass\n",
        )
        registry = CapabilityRegistry()
        scanner = ModuleOnboardingScanner(src_root=src, blueprint_root=tmp_path / "bp", registry=registry)
        discoveries = scanner.scan_filesystem()
        assert len(discoveries) == 1
        assert "os" in discoveries[0].imports
        assert "pathlib" in discoveries[0].imports

    def test_scan_handles_invalid_syntax(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        _create_python_module(
            src / "pkg" / "bad.py",
            "def broken(:\n",
        )
        registry = CapabilityRegistry()
        scanner = ModuleOnboardingScanner(src_root=src, blueprint_root=tmp_path / "bp", registry=registry)
        discoveries = scanner.scan_filesystem()
        assert len(discoveries) == 0


class TestScanBlueprints:
    def test_scan_nonexistent_blueprint_root(self, tmp_path: Path) -> None:
        registry = CapabilityRegistry()
        scanner = ModuleOnboardingScanner(
            src_root=tmp_path / "src",
            blueprint_root=tmp_path / "nonexistent",
            registry=registry,
        )
        assert scanner.scan_blueprints() == []

    def test_scan_finds_yaml_blueprints(self, tmp_path: Path) -> None:
        bp_root = tmp_path / "blueprints"
        bp_root.mkdir(parents=True)
        bp_file = bp_root / "my_module.yaml"
        bp_file.write_text("key: value\n", encoding="utf-8")
        registry = CapabilityRegistry()
        scanner = ModuleOnboardingScanner(src_root=tmp_path / "src", blueprint_root=bp_root, registry=registry)
        discoveries = scanner.scan_blueprints()
        assert len(discoveries) == 1
        assert discoveries[0].has_blueprint is True
        assert discoveries[0].blueprint_path is not None
        assert discoveries[0].module_name == "my_module"

    def test_scan_empty_blueprint_dir(self, tmp_path: Path) -> None:
        bp_root = tmp_path / "blueprints"
        bp_root.mkdir(parents=True)
        registry = CapabilityRegistry()
        scanner = ModuleOnboardingScanner(src_root=tmp_path / "src", blueprint_root=bp_root, registry=registry)
        assert scanner.scan_blueprints() == []


class TestDiffRegistered:
    def test_diff_finds_unregistered(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        _create_python_module(
            src / "mypackage" / "mymod.py",
            "class MyMod:\n    pass\n",
        )
        registry = CapabilityRegistry()
        scanner = ModuleOnboardingScanner(src_root=src, blueprint_root=tmp_path / "bp", registry=registry)
        unregistered = scanner.diff_registered()
        assert len(unregistered) == 1
        assert unregistered[0].reason == "missing_registration"
        assert unregistered[0].priority == "P1"

    def test_diff_skips_registered(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        _create_python_module(
            src / "mypackage" / "mymod.py",
            "class MyMod:\n    pass\n",
        )
        registry = CapabilityRegistry()
        from zephyr.trading.capability_card import CapabilityCard, CapabilityCategory

        card = CapabilityCard(
            capability_id="mypackage-mymod",
            name="MyMod",
            category=CapabilityCategory.INFRA,
            description="test",
        )
        registry.register(card)
        scanner = ModuleOnboardingScanner(src_root=src, blueprint_root=tmp_path / "bp", registry=registry)
        unregistered = scanner.diff_registered()
        assert len(unregistered) == 0

    def test_diff_with_blueprint_is_p0(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        _create_python_module(
            src / "mypackage" / "important.py",
            "class Important:\n    pass\n",
        )
        bp_root = tmp_path / "blueprints"
        bp_root.mkdir(parents=True)
        (bp_root / "important.yaml").write_text("key: val\n", encoding="utf-8")
        registry = CapabilityRegistry()
        scanner = ModuleOnboardingScanner(src_root=src, blueprint_root=bp_root, registry=registry)
        unregistered = scanner.diff_registered()
        assert len(unregistered) == 1
        assert unregistered[0].priority == "P1"

    def test_diff_empty_src(self, tmp_path: Path) -> None:
        registry = CapabilityRegistry()
        scanner = ModuleOnboardingScanner(
            src_root=tmp_path / "nonexistent",
            blueprint_root=tmp_path / "bp",
            registry=registry,
        )
        assert scanner.diff_registered() == []
