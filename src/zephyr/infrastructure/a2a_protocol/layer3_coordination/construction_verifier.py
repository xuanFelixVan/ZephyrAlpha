# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.construction_verifier
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_construction_verifier | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""施工后验证器 — 自指悖论防御：不橡胶图章，真正验证 A2A 协议模块的施工完整性"""

import ast
from dataclasses import dataclass, field
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）


@dataclass
class StubAnalysis:
    file_name: str
    line_count: int
    class_count: int
    method_count: int
    is_empty_stub: bool
    reason: str = ""


@dataclass
class VerifierResult:
    passed: bool
    total_files: int = 0
    empty_stubs: int = 0
    verified_files: int = 0
    issues: list[str] = field(default_factory=list)
    stub_details: list[StubAnalysis] = field(default_factory=list)
    layer_breakdown: dict = field(default_factory=dict)


_MIN_LINES_FOR_IMPLEMENTATION = 15
_A2A_SRC = REPO_ROOT / "src" / "zephyr" / "infra_ops" / "cicd_pipeline" / "a2a_protocol"

_EXPECTED_LAYERS = ["layer1_discovery", "layer2_communication", "layer3_coordination"]
_KEY_IMPLEMENTED_MODULES = [
    "layer1_discovery/agent_card.py",
    "layer2_communication/a2a_state.py",
    "layer2_communication/a2a_schemas.py",
    "layer3_coordination/supervisor.py",
    "layer3_coordination/a2a_protocol_gateway.py",
]


def _analyze_py_file(file_path: Path) -> StubAnalysis:
    try:
        source = file_path.read_text(encoding="utf-8")
        lines = [l for l in source.split("\n") if l.strip() and not l.strip().startswith("#")]
        line_count = len(lines)
        tree = ast.parse(source)
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        functions = [
            n
            for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and not any(isinstance(p, ast.ClassDef) for p in [])
        ]
        class_count = len(classes)
        method_count = 0
        for cls in classes:
            cls_methods = [n.name for n in cls.body if isinstance(n, ast.FunctionDef)]
            method_count += len(cls_methods)
        all_func_count = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])

        is_empty_stub = False
        reason = ""
        if line_count < _MIN_LINES_FOR_IMPLEMENTATION and class_count == 0 and all_func_count == 0:
            is_empty_stub = True
            reason = "no_classes_or_functions"
        elif class_count > 0 and method_count == 0 and all_func_count == 0:
            is_empty_stub = True
            reason = "classes_but_no_methods"

        return StubAnalysis(
            file_name=str(file_path.relative_to(_A2A_SRC)),
            line_count=line_count,
            class_count=class_count,
            method_count=method_count if method_count > 0 else all_func_count,
            is_empty_stub=is_empty_stub,
            reason=reason,
        )
    except Exception as e:
        return StubAnalysis(
            file_name=str(file_path.relative_to(_A2A_SRC)),
            line_count=0,
            class_count=0,
            method_count=0,
            is_empty_stub=True,
            reason=f"parse_error: {e}",
        )


def _verify_layer(layer_name: str) -> dict:
    layer_path = _A2A_SRC / layer_name
    result = {"exists": False, "importable": False, "file_count": 0, "py_files": 0}

    if not layer_path.is_dir():
        return result
    result["exists"] = True

    py_files = list(layer_path.glob("*.py"))
    result["py_files"] = len(py_files)

    all_files = list(layer_path.rglob("*.py"))
    result["file_count"] = len(all_files)

    init_file = layer_path / "__init__.py"
    if init_file.exists():
        init_text = init_file.read_text(encoding="utf-8")
        if init_text.strip():
            result["importable"] = True

    return result


def _verify_registries() -> list[str]:
    issues: list[str] = []
    registry_path = REPO_ROOT / "docs" / "03_modules" / "module-registry.yaml"
    blueprint_registry_path = REPO_ROOT / "docs" / "03_modules" / "blueprint_registry.yaml"

    if not registry_path.exists():
        issues.append("module-registry.yaml not found")
    else:
        content = registry_path.read_text(encoding="utf-8")
        if "MOD-INF-025" not in content:
            issues.append("MOD-INF-025 not registered in module-registry.yaml")

    if not blueprint_registry_path.exists():
        issues.append("blueprint_registry.yaml not found")
    else:
        content = blueprint_registry_path.read_text(encoding="utf-8")
        if "MOD-INF-025" not in content:
            issues.append("MOD-INF-025 not registered in blueprint_registry.yaml")

    return issues


def _verify_init_exports() -> list[str]:
    issues: list[str] = []
    init_path = _A2A_SRC / "__init__.py"
    if not init_path.exists():
        issues.append("top-level __init__.py missing")
        return issues

    content = init_path.read_text(encoding="utf-8")
    for layer in _EXPECTED_LAYERS:
        if layer not in content:
            issues.append(f"layer package {layer} not imported in __init__.py")

    return issues


class ConstructionVerifier:
    def verify(self, task_id: str = "", output: dict | None = None, _warn_only: bool = False) -> dict:
        """验证 A2A 协议模块的施工完整性。

        返回值中的 passed 字段为 False 时表示存在需要修复的问题。
        即使 passed=False，也会返回完整的 issues 和 stub_details。
        """
        output = output or {}
        result = VerifierResult(passed=True)

        if not _A2A_SRC.is_dir():
            return {
                "task_id": task_id,
                "passed": False,
                "issues": [f"A2A source directory not found: {_A2A_SRC}"],
                "total_files": 0,
                "empty_stubs": 0,
                "verified_files": 0,
                "stub_ratio": 1.0,
                "layer_breakdown": {},
                "stub_details": [],
                "output": output,
            }

        for layer_name in _EXPECTED_LAYERS:
            layer_result = _verify_layer(layer_name)
            result.layer_breakdown[layer_name] = layer_result
            if not layer_result["exists"]:
                result.issues.append(f"layer package {layer_name} does not exist")
                result.passed = False

        registry_issues = _verify_registries()
        result.issues.extend(registry_issues)
        if registry_issues:
            result.passed = False

        init_issues = _verify_init_exports()
        result.issues.extend(init_issues)
        if init_issues:
            result.passed = False

        all_py_files = sorted(_A2A_SRC.rglob("*.py"))
        result.total_files = len(all_py_files)

        for py_file in all_py_files:
            if py_file.name == "__init__.py":
                continue
            analysis = _analyze_py_file(py_file)
            if analysis.is_empty_stub:
                result.empty_stubs += 1
                result.stub_details.append(analysis)
            else:
                result.verified_files += 1

        if result.empty_stubs > 0:
            result.issues.append(
                f"{result.empty_stubs}/{result.total_files} files are empty stubs — 模块处于 Hold 状态，功能未实现"
            )

        for key_file in _KEY_IMPLEMENTED_MODULES:
            key_path = _A2A_SRC / key_file
            if not key_path.exists():
                result.issues.append(f"key module {key_file} is missing")
                result.passed = False

        return {
            "task_id": task_id,
            "passed": result.passed,
            "issues": result.issues,
            "total_files": result.total_files,
            "empty_stubs": result.empty_stubs,
            "verified_files": result.verified_files,
            "stub_ratio": round(result.empty_stubs / max(result.total_files, 1), 3),
            "layer_breakdown": result.layer_breakdown,
            "stub_details": [
                {
                    "file": s.file_name,
                    "lines": s.line_count,
                    "classes": s.class_count,
                    "methods": s.method_count,
                    "reason": s.reason,
                }
                for s in result.stub_details
            ],
            "output": output,
        }
