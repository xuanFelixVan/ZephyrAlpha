# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/validate_fle_imports.py | §
# [MODULE] scripts.governance.d7_code.validate_fle_imports
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
validate_fle_imports.py — FLE import 接口合规检测



对标：PS-STD-003 COND-43~45（FLE import 实现类 / CoVe 异构）
     5 份 AI 工程接口规范（context-engine / agent-orchestrator / ...）

原则：模块间只知道彼此公开接口（protocol/ABC），不知道实现类。
检测：Python AST 扫描——跨模块 import 中是否引入了实现类而非接口。

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: FLE import 接口合规检测（COND-43 — import纪律）
dimensions:
- D7
priority: P1
timeout_seconds: 30
warn_only: false
"""


import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
import argparse
import ast

from _shared.constants import EXIT_PASS, REPO_ROOT
from _shared.walk import iter_files

INTERFACE_PATTERNS = {"zephyr\\.shared\\.contracts\\.(abstract|protocol|interface)": "import 来自 contracts（接口）✅"}
IMPLEMENTATION_PATTERNS = {
    "from\\s+zephyr\\.\\w+\\.\\w+\\s+import\\s+": "跨模块 import（需确认是否为接口）",
    "import\\s+zephyr\\.\\w+\\.\\w+\\.\\w+": "深层 import 具体实现",
}
ALLOW_LIST = {"zephyr.shared.contracts", "zephyr.__init__", "zephyr.script_system"}


def scan_file(filepath: Path) -> list[dict]:
    """扫描单个文件并返回发现列表"""
    findings = []
    "扫描单个文件并返回发现列表."
    try:
        "扫描并返回发现列表."
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return findings
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return findings
    rel = str(filepath.relative_to(REPO_ROOT))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name
                if _is_impl_import(module):
                    findings.append(
                        {
                            "file": rel,
                            "line": node.lineno,
                            "import": f"import {module}",
                            "severity": "MEDIUM",
                            "reason": f"导入实现模块 `{module}`（应优先通过 contracts 导入接口）",
                        }
                    )
        elif isinstance(node, ast.ImportFrom):
            if node.module and _is_impl_import(node.module):
                findings.append(
                    {
                        "file": rel,
                        "line": node.lineno,
                        "import": f"from {node.module} import {', '.join(n.name for n in node.names)}",
                        "severity": "MEDIUM",
                        "reason": f"从 `{node.module}` 导入（可能引入实现类）",
                    }
                )
    return findings
    "扫描单个文件并返回发现列表."


def _is_impl_import(module: str) -> bool:
    """_is_impl_import implementation."""
    if not module.startswith("zephyr"):
        return False
    for allowed in ALLOW_LIST:
        if module.startswith(allowed):
            return False
    parts = module.split(".")
    if len(parts) <= 3:
        return False
    return True


def scan_src() -> tuple[list[dict], int]:
    """扫描源码目录并返回发现列表."""
    findings = []
    "扫描并返回发现列表."
    files_scanned = 0
    src_dir = REPO_ROOT / "src"
    if not src_dir.exists():
        return (findings, 0)
    for filepath in iter_files(src_dir):
        if filepath.suffix != ".py" or filepath.name.startswith("_"):
            continue
        files_scanned += 1
        findings.extend(scan_file(filepath))
    return (findings, files_scanned)
    "扫描源码目录并返回发现列表."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="FLE import 接口合规检测")
    parser.add_argument("--warn-only", action="store_true")
    args = parser.parse_args()
    findings, files_scanned = scan_src()
    impl_imports = [f for f in findings if "实现" in f.get("reason", "")]
    non_contract_imports = [f for f in findings if "contracts" not in f.get("import", "")]
    print(f"\n[FLE-IMPORTS] 扫描 {files_scanned} 个 Python 文件", file=sys.stderr)
    print(f"  实现类 import: {len(impl_imports)}", file=sys.stderr)
    print(f"  非契约 import: {len(non_contract_imports)}", file=sys.stderr)
    for f in findings:
        print(f"[P2] {f['file']}:{f['line']}  {f['import']} – {f['reason']}", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
