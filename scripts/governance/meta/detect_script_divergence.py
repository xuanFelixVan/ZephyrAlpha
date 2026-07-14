# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/detect_script_divergence.py | §
# [MODULE] scripts.governance.meta.detect_script_divergence
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
detect_script_divergence.py — 脚本实现与蓝图规范分歧检测（蓝图 §27.3 B81）

检测 run_all.py 实际执行逻辑与蓝图声明的调度策略是否一致：
- 依赖链顺序偏移（§5.3）
- 维度覆盖盲区（蓝图声明12维但实际只跑N维）
- timeout 策略偏差（蓝图分层→实际单层）

Usage:
    python scripts/governance/meta/detect_script_divergence.py
    python scripts/governance/meta/detect_script_divergence.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 脚本实现与蓝图规范分歧检测 — 调度策略偏移/维度盲区/timeout偏差
dimensions:
- D5
- D8
priority: P1
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

from _shared.constants import EXIT_PASS, SCRIPTS_DIR

RUN_ALL_PATH = SCRIPTS_DIR / "run_all.py"

EXPECTED_CHAINS = {
    "chain_a": ("D1", "D3", "D5", "D8"),
    "chain_b": ("D2", "D4", "D11", "D9", "D12"),
    "chain_c": ("D6", "D7", "D10"),
}

EXPECTED_TIMEOUT_CATEGORIES = {
    "D1": "file_scan",
    "D2": "file_scan",
    "D3": "content_analysis",
    "D4": "file_scan",
    "D5": "content_analysis",
    "D6": "content_analysis",
    "D7": "content_analysis",
    "D8": "content_analysis",
    "D9": "knowledge_ai",
    "D10": "content_analysis",
    "D11": "content_analysis",
    "D12": "knowledge_ai",
}


def extract_chains() -> dict:
    """从 run_all.py 提取依赖链定义。"""
    if not RUN_ALL_PATH.exists():
        return {}
    content = RUN_ALL_PATH.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(content, filename=str(RUN_ALL_PATH))
    except SyntaxError:
        return {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "DEPENDENCY_CHAINS":
                    chains = {}
                    if isinstance(node.value, ast.Dict):
                        for key, value in zip(node.value.keys, node.value.values, strict=False):
                            name = key.s if isinstance(key, ast.Constant) else ""
                            dims = (
                                tuple(elt.s for elt in value.elts if isinstance(elt, ast.Constant))
                                if isinstance(value, ast.Tuple)
                                else ()
                            )
                            if name and dims:
                                chains[name] = dims
                    return chains
    return {}


def extract_timeout_categories() -> dict:
    """从 run_all.py 提取超时类别定义。"""
    if not RUN_ALL_PATH.exists():
        return {}
    content = RUN_ALL_PATH.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(content, filename=str(RUN_ALL_PATH))
    except SyntaxError:
        return {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "DIMENSION_TIMEOUT_CATEGORIES":
                    cats = {}
                    if isinstance(node.value, ast.Dict):
                        for key, value in zip(node.value.keys, node.value.values, strict=False):
                            dim = key.s if isinstance(key, ast.Constant) else ""
                            cat = value.s if isinstance(value, ast.Constant) else ""
                            if dim:
                                cats[dim] = cat
                    return cats
    return {}


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="脚本实现与蓝图规范分歧检测")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()

    violations: list[str] = []

    actual_chains = extract_chains()
    for chain_name, expected_dims in EXPECTED_CHAINS.items():
        actual = actual_chains.get(chain_name)
        if actual is None:
            violations.append(f"缺失链 {chain_name}")
        elif actual != expected_dims:
            violations.append(f"链 {chain_name} 偏移: 蓝图层={list(expected_dims)} 实现={list(actual)}")

    actual_cats = extract_timeout_categories()
    for dim, expected_cat in EXPECTED_TIMEOUT_CATEGORIES.items():
        actual = actual_cats.get(dim)
        if actual is None:
            violations.append(f"维度 {dim} 缺少超时类别")
        elif actual != expected_cat:
            violations.append(f"维度 {dim} 超时类别偏移: 蓝图层={expected_cat} 实现={actual}")

    if violations:
        print(f"\n[DIVERGENCE] 发现 {len(violations)} 处实现漂移：\n", file=sys.stderr)
        for v in violations:
            print(f"  ⚠ {v}", file=sys.stderr)
        print(file=sys.stderr)
    else:
        print("\n[DIVERGENCE] ✅ run_all.py 实现与蓝图规范一致\n", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    main()
