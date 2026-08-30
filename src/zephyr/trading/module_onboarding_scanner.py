# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.module_onboarding_scanner
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ModuleOnboardingScanner — 模块接入扫描器
=========================================
蓝图: docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md §3.1
借鉴: K8s Controller Manager 主动调和 + K8s Discovery

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: src_root 参数
#   fields: 参数 src_root（无注解）
#   code: module_onboarding_scanner.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: blueprint_root 参数
#   fields: 参数 blueprint_root（无注解）
#   code: module_onboarding_scanner.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: registry 参数
#   fields: 参数 registry（无注解）
#   code: module_onboarding_scanner.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ModuleOnboardingScanner
#   name_en: ModuleOnboardingScanner
#   intro: 模块接入扫描器——主动发现未注册模块。
#   desc: 模块接入扫描器——主动发现未注册模块。；公共方法（定义序）: blueprint_root, src_root, scan_filesystem, scan_blueprints, diff_registered；源码…
#   inputs: src_root blueprint_root registry
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: ModuleOnboardingScanner
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
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

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def blueprint_root(self):
        """只读：blueprint_root（Stage 4 公共化）。"""
        return self._blueprint_root

    @blueprint_root.setter
    def blueprint_root(self, value):
        """写入：blueprint_root（Stage 4 公共化）。"""
        self._blueprint_root = value

    @property
    def src_root(self):
        """只读：src_root（Stage 4 公共化）。"""
        return self._src_root

    @src_root.setter
    def src_root(self, value):
        """写入：src_root（Stage 4 公共化）。"""
        self._src_root = value

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
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning(
                "_parse_module: failed to parse module %s (%s: %s)", path, type(e).__name__, e, exc_info=True
            )
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
