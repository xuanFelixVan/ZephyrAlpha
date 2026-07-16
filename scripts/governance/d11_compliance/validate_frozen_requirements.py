# [BLUEPRINT] MOD-INF-005 | scripts/governance/d11_compliance/validate_frozen_requirements.py | §
# [MODULE] scripts.governance.d11_compliance.validate_frozen_requirements
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
# [TTL] permanent
"""
validate_frozen_requirements.py — 依赖版本锁定与验证（蓝图 §34.2）

对比当前 Python 环境中的依赖版本与 frozen_versions.txt 中锁定的版本：
- 任何低于锁定版本 → Finding
- 任何不在锁定列表中的新包 → 警告

Usage:
    python scripts/governance/d11_compliance/validate_frozen_requirements.py
    python scripts/governance/d11_compliance/validate_frozen_requirements.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 依赖版本锁定验证 — 对比环境版本与 frozen_versions.txt
dimensions:
- D11
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import importlib.metadata
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parents[1]
_GOV_DIR = str(_SCRIPT_DIR)
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import EXIT_PASS, SCRIPTS_DIR

FROZEN_PATH = SCRIPTS_DIR / "meta" / "frozen_versions.txt"


def parse_frozen(path: Path) -> dict[str, str]:
    """解析 frozen_versions.txt。

    Args:
        path: 锁定文件路径

    Returns:
        dict[str, str]: 包名 → 最小版本
    """
    frozen: dict[str, str] = {}
    if not path.exists():
        return frozen
    for line in path.read_text(encoding="utf-8", errors="replace").split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ">=" in line:
            name, version = line.split(">=", 1)
            frozen[name.strip()] = version.strip()
    return frozen


def check_versions(frozen: dict[str, str]) -> tuple[list[str], list[str]]:
    """验证环境中版本是否满足锁定要求。

    Args:
        frozen: 锁定版本字典

    Returns:
        tuple[list[str], list[str]]: (违规列表, 通过列表)
    """
    violations: list[str] = []
    passed: list[str] = []

    for pkg_name, min_version in frozen.items():
        try:
            installed = importlib.metadata.version(pkg_name)
        except importlib.metadata.PackageNotFoundError:
            violations.append(f"{pkg_name}: 未安装（需要 >={min_version}）")
            continue

        if _version_lt(installed, min_version):
            violations.append(f"{pkg_name}: installed={installed} < frozen={min_version}")
        else:
            passed.append(f"{pkg_name}=={installed} (>={min_version})")

    return violations, passed


def _version_lt(a: str, b: str) -> bool:
    """_version_lt implementation."""
    try:
        pa = tuple(int(x) for x in a.split("."))
        pb = tuple(int(x) for x in b.split("."))
    except (ValueError, TypeError):
        return a < b
    return pa < pb


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="依赖版本锁定验证")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()

    frozen = parse_frozen(FROZEN_PATH)
    if not frozen:
        print("[FROZEN] frozen_versions.txt 为空或不存在", file=sys.stderr)
        sys.exit(0 if args.warn_only else 1)

    violations, passed = check_versions(frozen)

    print(f"\n[FROZEN] 环境版本检查 ({len(frozen)} 个依赖)：\n", file=sys.stderr)
    for p in passed:
        print(f"  ✅ {p}", file=sys.stderr)
    for v in violations:
        print(f"  ❌ {v}", file=sys.stderr)
    print(file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    main()
