# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/validate_dependency_chain.py | §
# [MODULE] scripts.governance.meta.validate_dependency_chain
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.meta.__init__
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
validate_dependency_chain.py — 依赖链拓扑顺序验证

验证 run_all.py 的三条依赖链与蓝图 §5.3 定义一致：
  链 A: D1 → D3 → D5 → D8
  链 B: D2 → D4 → D11 → D9 → D12
  链 C: D6 → D7 → D10

Usage:
    python scripts/governance/meta/validate_dependency_chain.py
    python scripts/governance/meta/validate_dependency_chain.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 依赖链拓扑顺序验证（蓝图 §5.3 — 三条链 A/B/C 定义一致性检查）
dimensions:
- D1
- D5
priority: P0
timeout_seconds: 30
warn_only: false
"""

import argparse
import ast
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parents[1]
_GOV_DIR = str(_SCRIPT_DIR)
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import EXIT_PASS, REPO_ROOT

RUN_ALL_PATH = REPO_ROOT / "scripts" / "governance" / "run_all.py"

EXPECTED_CHAINS: dict[str, tuple[str, ...]] = {
    "chain_a": ("D1", "D3", "D5", "D8"),
    "chain_b": ("D2", "D4", "D11", "D9", "D12"),
    "chain_c": ("D6", "D7", "D10"),
}

ALL_DIMENSIONS: frozenset[str] = frozenset(
    {
        "D1",
        "D2",
        "D3",
        "D4",
        "D5",
        "D6",
        "D7",
        "D8",
        "D9",
        "D10",
        "D11",
        "D12",
    }
)


def extract_chains_from_run_all() -> dict[str, tuple[str, ...]] | None:
    """从 run_all.py 中提取 DEPENDENCY_CHAINS 定义。

    Returns:
        dict 或 None（提取失败时）
    """
    if not RUN_ALL_PATH.exists():
        return None
    try:
        content = RUN_ALL_PATH.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    try:
        tree = ast.parse(content, filename=str(RUN_ALL_PATH))
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "DEPENDENCY_CHAINS":
                    chains: dict[str, tuple[str, ...]] = {}
                    if isinstance(node.value, ast.Dict):
                        for key, value in zip(node.value.keys, node.value.values, strict=False):
                            chain_name = key.s if isinstance(key, ast.Constant) else ""
                            dims: list[str] = []
                            if isinstance(value, ast.Tuple):
                                for elt in value.elts:
                                    if isinstance(elt, ast.Constant):
                                        dims.append(elt.s)
                            if chain_name and dims:
                                chains[chain_name] = tuple(dims)
                    return chains
    return None


def validate_chains(warn_only: bool = False) -> int:
    """验证依赖链定义与蓝图一致。

    Args:
        warn_only: True 时 exit 0

    Returns:
        int: exit code
    """
    failures: list[str] = []
    chains = extract_chains_from_run_all()

    if chains is None:
        failures.append("无法从 run_all.py 提取 DEPENDENCY_CHAINS 定义")
    else:
        for chain_name, expected_dims in EXPECTED_CHAINS.items():
            actual = chains.get(chain_name)
            if actual is None:
                failures.append(f"缺少链 {chain_name}: 期望 {list(expected_dims)}")
            elif actual != expected_dims:
                failures.append(f"链 {chain_name} 不一致: 期望 {list(expected_dims)}, 实际 {list(actual)}")

        all_dims_in_chains: set[str] = set()
        for dims in chains.values():
            all_dims_in_chains.update(dims)
        missing = ALL_DIMENSIONS - all_dims_in_chains
        if missing:
            failures.append(f"维度未在任何链中出现: {sorted(missing)}")

        duplicated: dict[str, int] = {}
        for dims in chains.values():
            for d in dims:
                duplicated[d] = duplicated.get(d, 0) + 1
        dupes = {d: c for d, c in duplicated.items() if c > 1}
        if dupes:
            failures.append(f"维度在多个链中重复: {dupes}")

    if failures:
        print(f"\n[DEPENDENCY-CHAIN] 发现 {len(failures)} 项违规：\n", file=sys.stderr)
        for f in failures:
            print(f"  ❌ {f}", file=sys.stderr)
        print(file=sys.stderr)
    else:
        print("\n[DEPENDENCY-CHAIN] ✅ 三条依赖链定义与蓝图 §5.3 一致\n", file=sys.stderr)

    if warn_only:
        return EXIT_PASS
    return 1 if failures else 0


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="依赖链拓扑顺序验证")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()
    sys.exit(validate_chains(args.warn_only))


if __name__ == "__main__":
    main()
