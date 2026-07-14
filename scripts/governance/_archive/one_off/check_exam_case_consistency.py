# [BLUEPRINT] MOD-INF-036 | docs/03_modules/_cross_layer/model_capability_exam/blueprint.md | §17.5
# [MODULE] scripts.governance.check_exam_case_consistency
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__;zephyr.intelligence.model_profiling.exam_test_cases
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 题库定义-注册一致性;瘦能力>=3题;二元判断必须有正负例对照
# [MODIFY-GUARD] docs/03_modules/_cross_layer/model_capability_exam/blueprint.md
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
# -*- coding: utf-8 -*-
"""考试题库一致性检查——根因治本，防止"定义-注册脱钩"复发。

检查项:
  1. 孤儿题：定义了但未注册到 ALL_EXAM_CASES 的 ExamTestCase（死代码）
  2. 瘦能力：注册题数 < --min-cases（默认3）的能力维度（无法形成难度梯度）
  3. 二元判断缺对照组：self_review/rule_comprehension 等二元能力缺少正/负例
     ——防止"总是报阳性/阴性"退化策略拿满分

用法:
  python scripts/governance/check_exam_case_consistency.py
  python scripts/governance/check_exam_case_consistency.py --warn-only
  python scripts/governance/check_exam_case_consistency.py --min-cases 3

退出码: 0 = 全部合规, 1 = 有违规

背景: Claude 外部审查发现 29 道孤儿题（含 context_management 全天窗）+
self_review/rule_comprehension 缺负例对照组。本脚本作为 CI 检查，
防止下次题库扩展时同类问题复发（审查2.1/2.2 治本措施）。
"""
from __future__ import annotations

import argparse
import sys

from zephyr.intelligence.model_profiling.exam_test_cases import (  # noqa: E402
    ALL_EXAM_CASES,
    ExamTestCase,
)
import zephyr.intelligence.model_profiling.exam_test_cases as _etc  # noqa: E402

# 二元判断字段映射：字段名 -> 能力名
# 这些字段构成"二元判断"能力，必须同时有正例(True)和负例(False)对照组，
# 防止"总是报阳性"的退化策略拿满分（Claude 审查 2.2）
BINARY_FIELDS: dict[str, str] = {
    "expected_has_bug": "self_review",
    "expected_compliant": "rule_comprehension",
}

DEFAULT_MIN_CASES = 3


def _collect_defined_cases(module) -> list[tuple[str, ExamTestCase]]:
    """收集模块中所有顶层定义的 ExamTestCase 变量（名称以 EX_ 开头）。

    返回 [(var_name, case), ...]，按变量名排序。
    排除 ALL_EXAM_CASES/CASES_BY_CAPABILITY 等容器（非 ExamTestCase 实例）。
    """
    defined: list[tuple[str, ExamTestCase]] = []
    for name in sorted(vars(module)):
        if not name.startswith("EX_"):
            continue
        obj = getattr(module, name, None)
        if isinstance(obj, ExamTestCase):
            defined.append((name, obj))
    return defined


def check_orphans(
    defined: list[tuple[str, ExamTestCase]],
    registered: list[ExamTestCase],
) -> list[tuple[str, ExamTestCase]]:
    """检查孤儿题：定义了但未注册到 ALL_EXAM_CASES。"""
    registered_ids = {c.case_id for c in registered}
    return [(name, c) for name, c in defined if c.case_id not in registered_ids]


def check_thin_capabilities(
    registered: list[ExamTestCase],
    min_cases: int,
) -> dict[str, int]:
    """检查瘦能力：注册题数 < min_cases。"""
    by_cap: dict[str, int] = {}
    for c in registered:
        by_cap[c.capability] = by_cap.get(c.capability, 0) + 1
    return {cap: n for cap, n in by_cap.items() if n < min_cases}


def check_binary_negatives(registered: list[ExamTestCase]) -> list[str]:
    """检查二元判断能力是否同时有正例和负例对照组。

    对 BINARY_FIELDS 中每个 (字段, 能力) 对：
    - 收集该能力所有题目的该字段值
    - 必须同时有 True 和 False，否则报告缺失
    """
    issues: list[str] = []
    for field, cap in BINARY_FIELDS.items():
        cases = [c for c in registered if c.capability == cap]
        if not cases:
            continue
        values = [getattr(c, field) for c in cases]
        has_true = any(v is True for v in values)
        has_false = any(v is False for v in values)
        if not has_true:
            issues.append(
                f"{cap}.{field}: 缺少正例(True)——所有 {len(cases)} 题均为 False，"
                f"'总是报阴性'退化策略可拿满分"
            )
        if not has_false:
            issues.append(
                f"{cap}.{field}: 缺少负例(False)——所有 {len(cases)} 题均为 True，"
                f"'总是报阳性'退化策略可拿满分"
            )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="考试题库一致性检查")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="仅警告不阻断（exit 0）",
    )
    parser.add_argument(
        "--min-cases",
        type=int,
        default=DEFAULT_MIN_CASES,
        help=f"瘦能力阈值，注册题数 < 此值视为瘦能力（默认 {DEFAULT_MIN_CASES}）",
    )
    args = parser.parse_args()

    defined = _collect_defined_cases(_etc)
    registered = list(ALL_EXAM_CASES)

    print("== 考试题库一致性检查 ==")
    print(
        f"  定义: {len(defined)} 题 | 注册: {len(registered)} 题 | "
        f"瘦能力阈值: {args.min_cases}"
    )

    errors: list[str] = []

    # 1. 孤儿题检查（审查2.1 治本）
    orphans = check_orphans(defined, registered)
    for name, c in orphans:
        errors.append(
            f"孤儿题: {name} ({c.case_id}) cap={c.capability} "
            f"diff={c.difficulty.value} — 定义未注册到 ALL_EXAM_CASES（死代码）"
        )

    # 2. 瘦能力检查（审查2.1 治本）
    thin = check_thin_capabilities(registered, args.min_cases)
    for cap, n in sorted(thin.items()):
        errors.append(
            f"瘦能力: {cap} 仅 {n} 题（< {args.min_cases}）— 无法形成难度梯度"
        )

    # 3. 二元判断缺对照组检查（审查2.2 治本）
    for issue in check_binary_negatives(registered):
        errors.append(f"二元判断缺对照组: {issue}")

    if errors:
        print()
        for e in errors:
            print(f"  [ERROR] {e}")
        print(
            f"\n== 结果: {len(errors)} 个问题 | "
            f"{'WARN-ONLY（不阻断）' if args.warn_only else 'BLOCKED by ERROR'} =="
        )
        return 0 if args.warn_only else 1

    print("  ALL CLEAN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
