# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.module_onboarding_scanner
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_module_onboarding_scanner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ModuleOnboardingScanner — 模块接入扫描器
=========================================
蓝图: ARC-0001 §5.4
借鉴: K8s Controller Manager 主动调和 + K8s Discovery
"""

import ast
import logging
from dataclasses import dataclass, field
from pathlib import Path

from zephyr.trading.capability_registry import CapabilityRegistry

logger = logging.getLogger(__name__)


@dataclass
class ModuleDiscovery:
    module_path: str
    module_name: str
    package: str
    has_class: bool = False
    class_names: list[str] = field(default_factory=list)
    has_public_functions: bool = False
    function_names: list[str] = field(default_factory=list)
    has_blueprint: bool = False
    blueprint_path: str | None = None
    docstring: str | None = None
    imports: list[str] = field(default_factory=list)


@dataclass
class UnregisteredModule:
    discovery: ModuleDiscovery
    reason: str = "new"
    priority: str = "P1"
    suggested_layer: str = "local"


class ModuleOnboardingScanner:
    """模块接入扫描器——主动发现未注册模块。"""

    def __init__(self, src_root: Path, blueprint_root: Path, registry: CapabilityRegistry) -> None:
        self._src_root = Path(src_root)
        self._blueprint_root = Path(blueprint_root)
        self._registry = registry

    def scan_filesystem(self) -> list[ModuleDiscovery]:
        discoveries: list[ModuleDiscovery] = []
        if not self._src_root.exists():
            return discoveries
        for py_file in self._src_root.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
            if "runtime" in py_file.parts and "zephyr" in py_file.parts:
                continue
            disc = self._parse_module(py_file)
            if disc and (disc.has_class or disc.has_public_functions):
                discoveries.append(disc)
        return discoveries

    def scan_blueprints(self) -> list[ModuleDiscovery]:
        discoveries: list[ModuleDiscovery] = []
        if not self._blueprint_root.exists():
            return discoveries
        for yaml_file in self._blueprint_root.rglob("*.yaml"):
            disc = ModuleDiscovery(
                module_path=str(yaml_file),
                module_name=yaml_file.stem,
                package=yaml_file.parent.name,
                has_blueprint=True,
                blueprint_path=str(yaml_file),
            )
            discoveries.append(disc)
        return discoveries

    def diff_registered(self) -> list[UnregisteredModule]:
        registered_ids = {c.capability_id for c in self._registry.list_all()}
        unregistered: list[UnregisteredModule] = []
        for disc in self.scan_filesystem():
            cap_id = f"{disc.package}-{disc.module_name}".replace("_", "-")
            if cap_id not in registered_ids:
                priority = "P0" if disc.has_blueprint else "P1"
                unregistered.append(
                    UnregisteredModule(
                        discovery=disc,
                        reason="missing_registration",
                        priority=priority,
                        suggested_layer="local",
                    )
                )
        return unregistered

    def _parse_module(self, path: Path) -> ModuleDiscovery | None:
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception as e:
            logger.warning("_parse_module: failed to parse module %s (%s: %s)", path, type(e).__name__, e, exc_info=True)
            return None

        rel = path.relative_to(self._src_root)
        parts = list(rel.parts)
        module_name = parts[-1].replace(".py", "")
        package = parts[0] if parts else ""

        class_names: list[str] = []
        function_names: list[str] = []
        imports: list[str] = []
        docstring: str | None = ast.get_docstring(tree)

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                class_names.append(node.name)
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                function_names.append(node.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)

        return ModuleDiscovery(
            module_path=str(path),
            module_name=module_name,
            package=package,
            has_class=len(class_names) > 0,
            class_names=class_names,
            has_public_functions=len(function_names) > 0,
            function_names=function_names,
            docstring=docstring,
            imports=imports,
        )