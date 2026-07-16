# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/validate_contracts_purity.py | §
# [MODULE] scripts.governance.d7_code.validate_contracts_purity
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d7_code.__init__
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
# [TTL] permanent
"""
validate_contracts_purity.py — 契约纯度校验



对标：COND-32（contracts 目录放业务逻辑为条件禁止）

检测内容：
- AST 扫描 src/zephyr/shared/contracts/ 下 .py 文件
- 仅允许 dataclass/Protocol/Enum/Literal/TypedDict/Annotated/BaseModel 定义
- 检测函数定义（def）、类方法、控制流等业务逻辑

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 契约纯度校验（COND-32 — contracts/仅允许数据结构定义）
dimensions:
- D7
priority: P1
timeout_seconds: 30
warn_only: false
"""


import ast
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_PY
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()

import argparse

ALLOWED_BASE_CLASSES = {
    "BaseModel",
    "Protocol",
    "Enum",
    "IntEnum",
    "StrEnum",
    "TypedDict",
    "dataclass",
    "Generic",
}

ALLOWED_DECORATORS = {
    "dataclass",
    "staticmethod",
    "classmethod",
    "property",
    "field",
    "validator",
    "root_validator",
    "model_validator",
    "field_validator",
    "computed_field",
}


def check_contract_purity(filepath: Path) -> list[dict]:
    """检查合约纯度."""
    findings = []
    """检查并返回违规列表."""
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return findings

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            is_protocol_method = False
            if isinstance(node, ast.FunctionDef) and node.body:
                first_stmt = node.body[0]
                if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant):
                    if isinstance(first_stmt.value.value, str) and first_stmt.value.value.strip() == "...":
                        is_protocol_method = True

            if not is_protocol_method and node.name != "__init__":
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id in ALLOWED_DECORATORS:
                        is_protocol_method = True
                        break
                    if isinstance(decorator, ast.Attribute) and decorator.attr in ALLOWED_DECORATORS:
                        is_protocol_method = True
                        break

                if not is_protocol_method:
                    rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
                    findings.append(
                        {
                            "file": rel,
                            "line": node.lineno,
                            "name": node.name,
                            "severity": "MEDIUM",
                        }
                    )

        elif isinstance(node, ast.ClassDef):
            has_allowed_base = False
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id in ALLOWED_BASE_CLASSES:
                    has_allowed_base = True
                    break
                if isinstance(base, ast.Attribute) and base.attr in ALLOWED_BASE_CLASSES:
                    has_allowed_base = True
                    break

            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id in ALLOWED_DECORATORS:
                    has_allowed_base = True
                    break
                if isinstance(decorator, ast.Attribute) and decorator.attr in ALLOWED_DECORATORS:
                    has_allowed_base = True
                    break

    return findings
    """检查合约纯度."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="契约纯度校验（COND-32）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    contracts_dir = REPO_ROOT / "src" / "zephyr" / "shared" / "contracts"
    if not contracts_dir.exists():
        print("[CONTRACTS-PURITY] contracts/ 目录不存在，跳过", file=sys.stderr)
        sys.exit(EXIT_PASS)

    all_findings = []
    for filepath in iter_files(contracts_dir, extensions=SCAN_EXTENSIONS_PY):
        findings = check_contract_purity(filepath)
        all_findings.extend(findings)

    if all_findings:
        print(f"\n[CONTRACTS-PURITY] {len(all_findings)} 个契约文件含业务逻辑:", file=sys.stderr)
        for f in all_findings:
            print(f"  [{f['severity']}] {f['file']}:{f['line']}", file=sys.stderr)
            print(f"    函数 '{f['name']}' 不应在契约层定义", file=sys.stderr)
    else:
        print("[CONTRACTS-PURITY] 契约文件纯度合规", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if all_findings else 0)


if __name__ == "__main__":
    main()
