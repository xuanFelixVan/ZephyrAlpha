# [BLUEPRINT] MOD-INF-005 | scripts/governance/d11_compliance/validate_no_utf8_bom.py | §
# [MODULE] scripts.governance.d11_compliance.validate_no_utf8_bom
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d11_compliance.__init__
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
"""
validate_no_utf8_bom.py — UTF-8 BOM 检测门禁

扫描项目中所有 .yaml / .md / .py 文件，检测 UTF-8 BOM (\\ufeff) 的存在。
对标 AGENTS.md §4 编码安全规则 + §6.19 门禁-登记表原子同步铁律（BOM 免疫）。

病因背景: 2026-05-06 第二次审计发现 4 个 catalog YAML 含 BOM，
导致 generate_registry_master_index.py 注释解析器在首行 break，5 个登记表被静默丢弃。
根因: 无编码层预检门禁 → BOM 文件不被发现 → 生成器静默跳过 → 登记表漂移。

Usage:
    python scripts/governance/d11_compliance/validate_no_utf8_bom.py
    python scripts/governance/d11_compliance/validate_no_utf8_bom.py --root <dir>
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
import argparse
import json
import sys
from pathlib import Path

from _shared.constants import EXIT_PASS

__manifest__ = """
dimensions: [D1, D11]
priority: P0
timeout_seconds: 5
args:
  - --root
  - --ci
  - --warn-only
  - --jsonl
warn_only: false
description: >
  扫描 .yaml/.md/.py 文件的 UTF-8 BOM，阻断 BOM 污染。
  对标 AGENTS.md §4 编码安全 — open() 禁止省略 encoding='utf-8'。
  本门禁是 generate_registry_master_index.py BOM 免疫的编码层预防防线。
"""

TARGET_EXTENSIONS = {".yaml", ".md", ".py"}
EXCLUDE_DIRS = {
    ".git",
    ".ailocks",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".pytest_cache",
    ".mypy_cache",
    "_DO_NOT_USE_old_tree",
}


def scan_for_bom(root: Path) -> list[str]:
    """scan_for_bom implementation."""
    bom_files = []
    for f in root.rglob("*"):
        if any(part in EXCLUDE_DIRS for part in f.parts):
            continue
        if f.is_file() and f.suffix in TARGET_EXTENSIONS:
            try:
                with open(f, "rb") as fh:
                    if fh.read(3) == b"\xef\xbb\xbf":
                        rel = f.relative_to(root)
                        bom_files.append(str(rel).replace("\\", "/"))
            except OSError:
                continue
    return bom_files


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Detect UTF-8 BOM in .yaml/.md/.py under repo root.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="扫描根目录")
    parser.add_argument("--ci", action="store_true", help="CI 模式（等价于强阻断）")
    parser.add_argument("--warn-only", action="store_true", help="告警模式（有 BOM 仍 exit 0）")
    parser.add_argument("--jsonl", action="store_true", help="输出单行 JSON（含 severity）")
    args = parser.parse_args()

    root = args.root.resolve()
    bom_files = scan_for_bom(root)

    exit_code = 1 if bom_files else 0

    if args.jsonl:
        blob = {
            "severity": "HIGH" if bom_files else "INFO",
            "check_id": "UTF8-BOM",
            "bom_files": sorted(bom_files)[:50],
            "count": len(bom_files),
        }
        print(json.dumps(blob, ensure_ascii=False))

    if bom_files:
        print(f"ERROR: {len(bom_files)} 个文件含 UTF-8 BOM:")
        for f in sorted(bom_files):
            print(f"  {f}")
        print(
            "\n修复: python -c \"with open(FILE,'rb') as f: d=f.read(); "
            "open(FILE,'wb').write(d[3:] if d[:3]==b'\\\\xef\\\\xbb\\\\xbf' else d)\""
        )
        if args.warn_only:
            return EXIT_PASS
        return exit_code

    print("OK: 所有 .yaml/.md/.py 文件均为纯 UTF-8（无 BOM）")
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main())
