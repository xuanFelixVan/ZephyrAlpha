# [BLUEPRINT] MOD-INF-005 | scripts/governance/blind_spot_registry.py | §
"""跨子系统盲点闭合追踪——扫描blueprint中的B-R盲点ID→交叉验证代码覆盖→生成闭合率报告

用法:
    python scripts/governance/blind_spot_registry.py --json     # AI消费
    python scripts/governance/blind_spot_registry.py --report   # 人类可读报告
    python scripts/governance/blind_spot_registry.py --warn-only # 仅WARN，不FAIL
"""

from __future__ import annotations
from _shared.constants import EXIT_FINDINGS


import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)


BLUEPRINTS_TO_SCAN = [
    ("pipeline", "docs/03_modules/_cross_layer/pipeline/blueprint.md"),
    ("feedback_loop", "docs/03_modules/_cross_layer/feedback-loop/blueprint.md"),
]

_BLIND_PIPELINE = re.compile(r"\bB(\d+)\b")
_BLIND_FLE = re.compile(r"盲点[\s]*(\d+)")

CODE_DIRS = [
    "src/zephyr/feedback_loop",
    "src/zephyr/pipeline",
    "src/zephyr/resilience",
    "src/zephyr/security",
    "src/zephyr/l01_infrastructure/code_dedup_engine",
]


def extract_ids_from_blueprint(bp_path: str, subsystem: str) -> set[str]:
    """extract_ids_from_blueprint implementation."""
    bp_full = PROJECT_ROOT / bp_path
    if not bp_full.exists():
        logger.warning("blueprint not found: %s", bp_path)
        return set()
    content = bp_full.read_text(encoding="utf-8")
    if subsystem == "pipeline":
        return {f"B{m.group(1)}" for m in _BLIND_PIPELINE.finditer(content)}
    elif subsystem == "feedback_loop":
        return {f"R{m.group(1)}" for m in _BLIND_FLE.finditer(content)}
    return set()


def scan_codebase_for_references(blind_ids: set[str]) -> dict[str, list[str]]:
    """scan_codebase_for_references implementation."""
    found: dict[str, list[str]] = {}
    for code_dir in CODE_DIRS:
        full_dir = PROJECT_ROOT / code_dir
        if not full_dir.exists():
            continue
        for root, _dirs, files in os.walk(full_dir):
            for fname in files:
                if not fname.endswith(".py"):
                    continue
                fpath = Path(root) / fname
                try:
                    content = fpath.read_text(encoding="utf-8")
                except Exception:
                    continue
                for bid in blind_ids:
                    if bid in content:
                        found.setdefault(bid, []).append(str(fpath.relative_to(PROJECT_ROOT)))
    return found


def generate_report() -> dict:
    """Generate output from input data."""
    all_ids: dict[str, set[str]] = {}
    for subsystem, bp_path in BLUEPRINTS_TO_SCAN:
        ids = extract_ids_from_blueprint(bp_path, subsystem)
        all_ids[subsystem] = ids

    all_blind_ids = set()
    for ids in all_ids.values():
        all_blind_ids.update(ids)

    code_refs = scan_codebase_for_references(all_blind_ids)

    subsystems = {}
    grand_total = 0
    grand_covered = 0
    for subsystem, ids in all_ids.items():
        covered = sum(1 for bid in ids if bid in code_refs)
        subsystems[subsystem] = {
            "total": len(ids),
            "covered": covered,
            "uncovered": len(ids) - covered,
            "coverage_rate": f"{covered}/{len(ids)}" if ids else "N/A",
        }
        grand_total += len(ids)
        grand_covered += covered

    return {
        "total_blind_spots": grand_total,
        "covered_in_code": grand_covered,
        "overall_closure_rate": f"{grand_covered}/{grand_total} ({grand_covered/grand_total*100:.1f}%)" if grand_total else "N/A",
        "subsystems": subsystems,
        "code_references": code_refs,
    }


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="跨子系统盲点闭合追踪")
    parser.add_argument("--json", action="store_true", help="JSON输出（AI消费）")
    parser.add_argument("--report", action="store_true", help="人类可读报告")
    parser.add_argument("--warn-only", action="store_true", help="仅WARN，不FAIL")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    report = generate_report()

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    print(f"\n{'='*60}")
    print(f"  盲点闭合追踪报告")
    print(f"{'='*60}")
    print(f"  全项目盲点总数: {report['total_blind_spots']}")
    print(f"  代码中已引用:   {report['covered_in_code']}")
    print(f"  闭合率:         {report['overall_closure_rate']}")
    print(f"{'='*60}\n")

    for subsystem, stats in report["subsystems"].items():
        print(f"  [{subsystem}]")
        print(f"    总计: {stats['total']} | 已覆盖: {stats['covered']} | 未覆盖: {stats['uncovered']}")
        print(f"    覆盖率: {stats['coverage_rate']}")
        print()

    uncovered_count = 0
    for subsystem, ids in {k: v for k, v in {
        "pipeline": extract_ids_from_blueprint("docs/03_modules/_cross_layer/pipeline/blueprint.md", "pipeline"),
        "feedback_loop": extract_ids_from_blueprint("docs/03_modules/_cross_layer/feedback-loop/blueprint.md", "feedback_loop"),
    }.items()}.items():
        code_refs = scan_codebase_for_references(ids)
        uncovered = [bid for bid in ids if bid not in code_refs]
        if uncovered:
            print(f"  [{subsystem}] UNCOVERED ({len(uncovered)}):")
            for bid in sorted(uncovered)[:20]:
                print(f"    {bid}")
            if len(uncovered) > 20:
                print(f"    ... and {len(uncovered)-20} more")
            uncovered_count += len(uncovered)
            print()

    if uncovered_count > 0 and not args.warn_only:
        logger.warning("存在 %d 个未覆盖盲点", uncovered_count)
        sys.exit(EXIT_FINDINGS)

    logger.info("盲点追踪完成")


if __name__ == "__main__":
    main()
