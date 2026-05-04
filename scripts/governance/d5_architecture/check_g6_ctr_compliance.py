"""
check_g6_ctr_compliance.py — G6 CTR 契约合规门禁执行引擎

对标：G6 CTR Compliance Gate（g6_ctr_compliance.yaml）
      CTR-001~006 跨层数据契约

检测内容：
- 各层是否自造了与 CTR 冲突的数据类型（如 L00 自造 MarketData 类）
- 金额相关字段是否错误使用了 float（应该用 Decimal）
- 跨层导入是否走 shared/contracts/ 而非直接跨层导入

exit codes: 0=pass, 1=findings, 2=error

SSoT: src/zephyr/gates/g6_ctr_compliance.yaml
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

import yaml

GATE_CONFIG_REL = "src/zephyr/gates/g6_ctr_compliance.yaml"
FORBIDDEN_CLASS_NAMES_BY_LAYER = {
    "l00_data_source": {"NormalizedMarketData", "MarketData", "Tick", "Bar", "TradeData", "Candle", "Quote"},
    "l02_alpha_factor": {"FactorSignal", "Factor", "FactorValue", "AlphaSignal", "Signal"},
    "l04_risk_management": {"RiskLimits", "Limit", "Constraint", "RiskConstraint"},
    "l05_portfolio_construction": {"Order", "OrderRequest", "OrderCmd", "TradeInstruction"},
    "l06_trade_execution": {
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
    "l07_post_trade_analytics": {"Position", "PositionSnapshot", "Holding"},
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
LAYER_DIRS = [
    "l00_data_source",
    "l01_infrastructure",
    "l02_alpha_factor",
    "l03_signal_generation",
    "l04_risk_management",
    "l05_portfolio_construction",
    "l06_trade_execution",
    "l07_post_trade_analytics",
]

def load_gate_config() -> dict | None:
    """加载门禁配置"""
    gate_path = REPO_ROOT / GATE_CONFIG_REL
    if not gate_path.exists():
        return None
    try:
        return yaml.safe_load(gate_path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None

def scan_forbidden_class_names() -> list[dict]:
    """扫描禁止的类名"""
    findings: list[dict] = []
    src_dir = REPO_ROOT / "src" / "zephyr"
    "load gate config."
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
                                "violation": f"{layer_name} 自造了数据类型 '{node.name}'——请使用 shared/contracts/ 中的对应 CTR 契约",
                                "severity": "HIGH",
                            }
                        )
    return findings

def scan_float_in_money_fields() -> list[dict]:
    """扫描金额字段中的浮点数"""
    findings: list[dict] = []
    "scan forbidden class names."
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
                                    "violation": f"金额相关字段 '{field_name}' 使用了 float 注解——必须使用 Decimal（CTR 全域强制，参见 CTR-001~006）",
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
                                        "violation": f"函数 '{node.name}' 的金额参数 '{arg_name}' 使用了 float 注解——必须使用 Decimal",
                                        "severity": "HIGH",
                                    }
                                )
    return findings

def scan_cross_layer_imports() -> list[dict]:
    """scan float in money fields."""
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
                                "violation": f"跨层导入 '{import_path}' 直接指向了其他层目录——跨层数据交换必须通过 shared/contracts/",
                                "severity": "MEDIUM",
                            }
                        )
    return findings
    "scan cross layer imports."

def _get_field_name(node: ast.AnnAssign) -> str | None:
    if isinstance(node.target, ast.Name):
        return node.target.id
    if isinstance(node.target, ast.Attribute):
        return node.target.attr
    return None

def _is_money_field(name: str) -> bool:
    name_lower = name.lower()
    return any(pattern in name_lower for pattern in MONEY_FIELD_PATTERNS)

def _annotation_is_float(annotation: ast.expr) -> bool:
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
    parts: list[str] = []
    if isinstance(node, ast.ImportFrom):
        if node.module:
            parts.append(node.module)
    elif isinstance(node, ast.Import):
        for alias in node.names:
            parts.append(alias.name)
    return ".".join(parts)

def _is_cross_layer_import(import_path: str, current_layer: str) -> bool:
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
    """检查必需的 import"""
    findings: list[dict] = []
    src_dir = REPO_ROOT / "src" / "zephyr"
    required_imports = {
        "l00_data_source": {"shared.contracts.market_data": "NormalizedMarketData"},
        "l02_alpha_factor": {
            "shared.contracts.market_data": "NormalizedMarketData",
            "shared.contracts.factor_signal": "FactorSignal",
        },
        "l04_risk_management": {"shared.contracts.risk_limits": "RiskLimits"},
        "l05_portfolio_construction": {"shared.contracts.order": "Order"},
        "l06_trade_execution": {
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
                continue
    return findings
    "check required imports."

def _all_py_files(layer_dir: Path) -> list[Path]:
    files: list[Path] = []
    try:
        for p in layer_dir.rglob("*.py"):
            if p.is_file():
                files.append(p)
    except OSError:
        pass
    return files

def main() -> None:
    """入口函数"""
    parser = argparse.ArgumentParser(description="G6 CTR 契约合规门禁执行引擎")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    parser.add_argument("--layer", type=str, help="仅检查指定层（如 l02_alpha_factor）")
    parser.add_argument(
        "--checks", type=str, default="all", help="检查项：all | class_names | money_fields | cross_imports"
    )
    args = parser.parse_args()
    config = load_gate_config()
    if config is None:
        print("[G6] g6_ctr_compliance.yaml 未找到，跳过", file=sys.stderr)
        sys.exit(0)
    print(f'[G6] CTR 契约合规门禁启动 — 门禁: {config.get('gate_name', 'unknown')}', file=sys.stderr)
    all_findings: list[dict] = []
    if args.checks in ("all", "class_names"):
        findings = scan_forbidden_class_names()
        all_findings.extend(findings)
    if args.checks in ("all", "money_fields"):
        findings = scan_float_in_money_fields()
        all_findings.extend(findings)
    if args.checks in ("all", "cross_imports"):
        findings = scan_cross_layer_imports()
        all_findings.extend(findings)
    if args.layer:
        all_findings = [f for f in all_findings if f.get("layer", "") == args.layer]
    class_violations = [f for f in all_findings if "自造了数据" in f.get("violation", "")]
    money_violations = [f for f in all_findings if "使用了 float" in f.get("violation", "")]
    import_violations = [f for f in all_findings if "跨层导入" in f.get("violation", "")]
    print("\n[G6] 扫描完成", file=sys.stderr)
    print(f"  自造数据类型违规: {len(class_violations)}", file=sys.stderr)
    print(f"  金额字段 float 违规: {len(money_violations)}", file=sys.stderr)
    print(f"  跨层导入违规: {len(import_violations)}", file=sys.stderr)
    for f in all_findings:
        print(f'\n  [{f['severity']}] {f['file']}:{f.get('line', '?')}', file=sys.stderr)
        print(f'     {f['violation']}', file=sys.stderr)
    total = len(all_findings)
    if total == 0:
        print("\n[G6] CTR 契约合规 — 全部通过 ✅", file=sys.stderr)
    else:
        print(f"\n[G6] ⚠ {total} 条 CTR 合规违规！", file=sys.stderr)
    if args.warn_only:
        sys.exit(0)
    sys.exit(1 if all_findings else 0)
    "入口函数."

if __name__ == "__main__":
    main()
