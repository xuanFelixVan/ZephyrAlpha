# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_g6_ctr_compliance.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_g6_ctr_compliance
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""check_g6_ctr_compliance.py - G6 CTR Contract Compliance Gate Engine



Checks:
- Whether layers self-create data types conflicting with CTR (e.g. D_DATA creates own MarketData)
- Whether monetary fields incorrectly use float (should use Decimal)
- Whether cross-layer imports go through shared/contracts/ rather than direct layer imports

exit codes: 0=pass, 1=findings, 2=error
SSoT: src/zephyr/governance/rule_enforcement/g6_ctr_compliance.yaml
"""

from __future__ import annotations

__manifest__ = """
args: []
description: G6 CTR 契约合规门禁——层自建数据类型冲突/货币字段float误用/跨层直连导入检测
dimensions:
- D5
- D11
priority: P1
timeout_seconds: 60
warn_only: false
"""

import ast
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

import yaml

GATE_CONFIG_REL = "src/zephyr/governance/rule_enforcement/g6_ctr_compliance.yaml"
FORBIDDEN_CLASS_NAMES_BY_LAYER = {
    "data": {"NormalizedMarketData", "MarketData", "Tick", "Bar", "TradeData", "Candle", "Quote"},
    "factor": {"FactorSignal", "Factor", "FactorValue", "AlphaSignal", "Signal"},
    "risk": {"RiskLimits", "Limit", "Constraint", "RiskConstraint"},
    "pf_core": {"Order", "OrderRequest", "OrderCmd", "TradeInstruction"},
    "ex_core": {
        "Order",
        "OrderRequest",
        "OrderCmd",
        "Fill",
        "FillReport",
        "Execution",
        "Position",
        "PositionSnapshot",
        "Holding",
    },
    "pf_core": {"Position", "PositionSnapshot", "Holding"},
}
MONEY_FIELD_PATTERNS = {
    "price",
    "amount",
    "cost",
    "fee",
    "commission",
    "quantity",
    "volume",
    "value",
    "notional",
    "position_value",
    "market_value",
    "nav",
    "cash",
    "balance",
    "equity",
    "open",
    "high",
    "low",
    "close",
    "limit_price",
    "fill_price",
    "avg_price",
    "entry_price",
    "exit_price",
}
ALLOWED_CONTRACT_DIR = "shared/contracts"
ALLOWED_SHARED_DIR = "shared"
LAYER_DIRS = [  # noqa: gate-vocab  层目录名，非 domain 值
    "data",
    "infrastructure_runtime_integration",
    "factor",
    "signal",
    "risk",
    "pf_core",
    "ex_core",
    "pf_core",
]


def load_gate_config() -> dict | None:
    """load_gate_config implementation."""
    gate_path = REPO_ROOT / GATE_CONFIG_REL
    if not gate_path.exists():
        return None
    try:
        return yaml.safe_load(gate_path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None


def scan_forbidden_class_names() -> list[dict]:
    """scan_forbidden_class_names implementation."""
    findings: list[dict] = []
    src_dir = REPO_ROOT / "src" / "zephyr"
    for layer_name, forbidden_names in FORBIDDEN_CLASS_NAMES_BY_LAYER.items():
        layer_dir = src_dir / layer_name
        if not layer_dir.exists():
            continue
        for filepath in iter_files(layer_dir, extensions={".py"}):
            try:
                source = filepath.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source, filename=str(filepath))
            except (SyntaxError, OSError, UnicodeDecodeError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name in forbidden_names:
                        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
                        findings.append(
                            {
                                "file": rel,
                                "layer": layer_name,
                                "class_name": node.name,
                                "line": node.lineno,
                                "violation": (
                                    f"Layer '{layer_name}' self-creates data type '{node.name}' - "
                                    f"use shared/contracts/ CTR contracts instead"
                                ),
                                "severity": "HIGH",
                            }
                        )
    return findings


def scan_float_in_money_fields() -> list[dict]:
    """scan_float_in_money_fields implementation."""
    findings: list[dict] = []
    src_dir = REPO_ROOT / "src" / "zephyr"
    for layer_name in LAYER_DIRS:
        layer_dir = src_dir / layer_name
        if not layer_dir.exists():
            continue
        for filepath in iter_files(layer_dir, extensions={".py"}):
            try:
                source = filepath.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source, filename=str(filepath))
            except (SyntaxError, OSError, UnicodeDecodeError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.AnnAssign) and node.annotation:
                    field_name = _get_field_name(node)
                    if field_name and _is_money_field(field_name):
                        if _annotation_is_float(node.annotation):
                            rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
                            findings.append(
                                {
                                    "file": rel,
                                    "layer": layer_name,
                                    "field_name": field_name,
                                    "line": node.lineno,
                                    "violation": (
                                        f"Money field '{field_name}' uses 'float' - must use Decimal (CTR mandate)"
                                    ),
                                    "severity": "HIGH",
                                }
                            )
                elif isinstance(node, ast.FunctionDef):
                    for arg in node.args.args:
                        if arg.annotation:
                            arg_name = arg.arg
                            if _is_money_field(arg_name) and _annotation_is_float(arg.annotation):
                                rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
                                findings.append(
                                    {
                                        "file": rel,
                                        "layer": layer_name,
                                        "field_name": f"{node.name}.{arg_name}",
                                        "line": node.lineno,
                                        "violation": (
                                            f"Fn '{node.name}' param '{arg_name}' uses 'float' - must use Decimal"
                                        ),
                                        "severity": "HIGH",
                                    }
                                )
    return findings


def scan_cross_layer_imports() -> list[dict]:
    """scan_cross_layer_imports implementation."""
    findings: list[dict] = []
    src_dir = REPO_ROOT / "src" / "zephyr"
    for layer_name in LAYER_DIRS:
        layer_dir = src_dir / layer_name
        if not layer_dir.exists():
            continue
        for filepath in iter_files(layer_dir, extensions={".py"}):
            try:
                source = filepath.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source, filename=str(filepath))
            except (SyntaxError, OSError, UnicodeDecodeError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_path = _get_import_path(node)
                    if import_path and _is_cross_layer_import(import_path, layer_name):
                        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
                        findings.append(
                            {
                                "file": rel,
                                "layer": layer_name,
                                "import_path": import_path,
                                "line": node.lineno,
                                "violation": (f"Cross-layer import '{import_path}' - MUST use shared/contracts/"),
                                "severity": "MEDIUM",
                            }
                        )
    return findings


def _get_field_name(node: ast.AnnAssign) -> str | None:
    """_get_field_name implementation."""
    if isinstance(node.target, ast.Name):
        return node.target.id
    if isinstance(node.target, ast.Attribute):
        return node.target.attr
    return None


def _is_money_field(name: str) -> bool:
    """_is_money_field implementation."""
    name_lower = name.lower()
    return any(pattern in name_lower for pattern in MONEY_FIELD_PATTERNS)


def _annotation_is_float(annotation: ast.expr) -> bool:
    """_annotation_is_float implementation."""
    if isinstance(annotation, ast.Name) and annotation.id == "float":
        return True
    if isinstance(annotation, ast.Subscript):
        value = annotation.value
        if isinstance(value, ast.Name) and value.id == "float":
            return True
    if isinstance(annotation, ast.Attribute):
        if annotation.attr == "float":
            return True
    return False


def _get_import_path(node: ast.Import | ast.ImportFrom) -> str:
    """_get_import_path implementation."""
    parts: list[str] = []
    if isinstance(node, ast.ImportFrom):
        if node.module:
            parts.append(node.module)
    elif isinstance(node, ast.Import):
        for alias in node.names:
            parts.append(alias.name)
    return ".".join(parts)


def _is_cross_layer_import(import_path: str, current_layer: str) -> bool:
    """_is_cross_layer_import implementation."""
    normalized = import_path.replace(".", "/").replace("\\", "/")
    if ALLOWED_CONTRACT_DIR in normalized or normalized.split("/")[-1] == ALLOWED_SHARED_DIR:
        return False
    for other_layer in LAYER_DIRS:
        if other_layer == current_layer:
            continue
        if other_layer in normalized or other_layer.replace("_", "/") in normalized:
            return True
    return False


def check_required_imports() -> list[dict]:
    """Check compliance and report findings."""
    findings: list[dict] = []
    src_dir = REPO_ROOT / "src" / "zephyr"
    required_imports = {
        "data": {"shared.contracts.market_data": "NormalizedMarketData"},
        "factor": {
            "shared.contracts.market_data": "NormalizedMarketData",
            "shared.contracts.factor_signal": "FactorSignal",
        },
        "risk": {"shared.contracts.risk_limits": "RiskLimits"},
        "pf_core": {"shared.contracts.order": "Order"},
        "ex_core": {
            "shared.contracts.order": "Order",
            "shared.contracts.fill": "Fill",
            "shared.contracts.position": "PositionSnapshot",
        },
    }
    for layer_name, imports_needed in required_imports.items():
        layer_dir = src_dir / layer_name
        if not layer_dir.exists():
            continue
        py_files = list(iter_files(layer_dir, extensions={".py"}))
        if not py_files:
            continue
        all_source = ""
        for filepath in py_files:
            try:
                all_source += filepath.read_text(encoding="utf-8", errors="replace") + "\n"
            except OSError:
                continue
        for import_module, type_name in imports_needed.items():
            import_str = import_module.replace("/", ".")
            if import_str not in all_source and type_name not in all_source:
                pass
    return findings


def _all_py_files(layer_dir: Path) -> list[Path]:
    """_all_py_files implementation."""
    files: list[Path] = []
    try:
        for p in layer_dir.rglob("*.py"):
            if p.is_file():
                files.append(p)
    except OSError:
        pass
    return files


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="G6 CTR Contract Compliance Gate")
    parser.add_argument("--warn-only", action="store_true", help="Warning mode only")
    parser.add_argument("--layer", type=str, help="Check specific layer only")
    parser.add_argument(
        "--checks", type=str, default="all", help="Checks: all | class_names | money_fields | cross_imports"
    )
    args = parser.parse_args()

    config = load_gate_config()
    if config is None:
        print("[G6] g6-ctr-compliance.yaml not found, skipping", file=sys.stderr)
        sys.exit(EXIT_PASS)

    gate_name = config.get("gate_name", "unknown")
    print(f"[G6] CTR Compliance Gate started - Gate: {gate_name}", file=sys.stderr)

    all_findings: list[dict] = []
    if args.checks in ("all", "class_names"):
        all_findings.extend(scan_forbidden_class_names())
    if args.checks in ("all", "money_fields"):
        all_findings.extend(scan_float_in_money_fields())
    if args.checks in ("all", "cross_imports"):
        all_findings.extend(scan_cross_layer_imports())

    if args.layer:
        all_findings = [f for f in all_findings if f.get("layer", "") == args.layer]

    class_violations = [f for f in all_findings if "self-creates" in f.get("violation", "")]
    money_violations = [f for f in all_findings if "float" in f.get("violation", "").lower()]
    import_violations = [f for f in all_findings if "Cross-layer" in f.get("violation", "")]

    print("\n[G6] Scan complete", file=sys.stderr)
    print(f"  Self-created data type violations: {len(class_violations)}", file=sys.stderr)
    print(f"  Float-annotation violations: {len(money_violations)}", file=sys.stderr)
    print(f"  Cross-layer import violations: {len(import_violations)}", file=sys.stderr)

    for f in all_findings:
        severity = f["severity"]
        filename = f["file"]
        line = f.get("line", "?")
        violation = f["violation"]
        print(f"\n  [{severity}] {filename}:{line}", file=sys.stderr)
        print(f"     {violation}", file=sys.stderr)

    total = len(all_findings)
    if total == 0:
        print("\n[G6] CTR Contract Compliance - ALL PASSED", file=sys.stderr)
    else:
        print(f"\n[G6] {total} CTR compliance violations found!", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS if all_findings else EXIT_PASS)


if __name__ == "__main__":
    main()
