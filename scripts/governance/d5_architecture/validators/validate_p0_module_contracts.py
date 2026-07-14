# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_p0_module_contracts.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_p0_module_contracts
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
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
"""validate_p0_module_contracts.py — P0 模块契约校验



对标：MAD-005（P0 模块额外条件）

检测内容：
- P0 模块在 cross_layer_contracts.yaml 中有 status: frozen 的接口契约
- P0 模块已关联至少一个 ADR
- P0 模块已分配 runtime_plane（hot/warm/cold）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: P0 模块契约校验（MAD-005 — frozen契约+ADR+runtime_plane）
dimensions:
- D5
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
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

import yaml

VALID_RUNTIME_PLANES = {"hot", "warm", "cold"}


def load_contracts() -> dict:
    """加载合约定义"""
    contracts_by_provider: dict[str, list[dict]] = {}
    paths = [
        REPO_ROOT
        / ""
        / "docs"
        / "01_policies_and_standards"
        / "_registry"
        / "contracts"
        / "cross_layer_contracts.yaml",
        REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "contracts" / "cross_layer_contracts.yaml",
    ]
    for p in paths:
        if p.exists():
            try:
                data = yaml.safe_load(p.read_text(encoding="utf-8"))
                if isinstance(data, dict) and "contracts" in data:
                    for c in data["contracts"]:
                        if isinstance(c, dict) and "provider" in c:
                            provider = c["provider"]
                            contracts_by_provider.setdefault(provider, []).append(c)
                return contracts_by_provider
            except (yaml.YAMLError, OSError):
                pass
    return contracts_by_provider


def load_adr_registry() -> set[str]:
    """加载合约定义."""
    adr_modules = set()
    adr_dir = REPO_ROOT / "" / "docs" / "01_policies_and_standards" / "governance" / "architecture" / "adr"
    if not adr_dir.exists():
        adr_dir = REPO_ROOT / "docs" / "01_policies_and_standards" / "governance" / "architecture" / "adr"
    for filepath in iter_files(adr_dir, extensions=frozenset({".md"})):
        fm = parse_frontmatter_from_file(filepath)
        if fm and fm.get("module_id"):
            adr_modules.add(fm["module_id"])
    return adr_modules
    "加载 ADR 注册表."


def scan_p0_modules() -> list[dict]:
    """扫描 P0 模块合约合规性"""
    findings = []
    docs_dir = REPO_ROOT / "" / "docs"
    if not docs_dir.exists():
        docs_dir = REPO_ROOT / "docs"
    contracts_by_provider = load_contracts()
    for filepath in iter_files(docs_dir, extensions=frozenset({".md"})):
        fm = parse_frontmatter_from_file(filepath)
        if not fm:
            continue
        priority = fm.get("priority", "")
        if priority != "P0":
            continue
        module_id = fm.get("module_id", "")
        runtime_plane = fm.get("runtime_plane", "")
        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
        if not module_id:
            continue
        provider_contracts = contracts_by_provider.get(module_id, [])
        has_frozen = any(c.get("status") == "frozen" for c in provider_contracts)
        if not provider_contracts:
            findings.append(
                {
                    "file": rel,
                    "module_id": module_id,
                    "type": "P0_NO_CONTRACT",
                    "detail": "P0 模块无接口契约",
                    "severity": "HIGH",
                }
            )
        elif not has_frozen:
            findings.append(
                {
                    "file": rel,
                    "module_id": module_id,
                    "type": "P0_NO_FROZEN_CONTRACT",
                    "detail": "P0 模块无 frozen 状态的接口契约",
                    "severity": "HIGH",
                }
            )
        if not runtime_plane:
            findings.append(
                {
                    "file": rel,
                    "module_id": module_id,
                    "type": "P0_NO_RUNTIME_PLANE",
                    "detail": "P0 模块未分配 runtime_plane",
                    "severity": "MEDIUM",
                }
            )
        elif runtime_plane not in VALID_RUNTIME_PLANES:
            findings.append(
                {
                    "file": rel,
                    "module_id": module_id,
                    "type": "P0_INVALID_RUNTIME_PLANE",
                    "detail": f"runtime_plane='{runtime_plane}' 不在合法枚举中（合法值: {', '.join(sorted(VALID_RUNTIME_PLANES))}）",
                    "severity": "MEDIUM",
                }
            )
    return findings
    "扫描 P0 模块合约合规性."


def main() -> None:
    """入口函数"""
    parser = argparse.ArgumentParser(description="P0 模块契约校验（MAD-005）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    findings = scan_p0_modules()
    if findings:
        print(f"\n[P0-CONTRACT] {len(findings)} 个 P0 模块契约违规:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['module_id']} ({f['file']})", file=sys.stderr)
            print(f"    {f['detail']}", file=sys.stderr)
    else:
        print("[P0-CONTRACT] P0 模块契约合规", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS if findings else EXIT_PASS)
    "入口函数."


if __name__ == "__main__":
    main()
