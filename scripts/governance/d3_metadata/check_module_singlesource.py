# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
# [MODULE] scripts.governance.check_module_singlesource
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.shared.io.paths
# [CONSUMERS] pre-commit GATE-SSOT-SINGLESOURCE hook; CI pipeline; AI session 冷启动
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 受保护文件名只能在声明 SSoT 路径下出现；扫描 src/zephyr/ 全量 .py 文件
# [MODIFY-GUARD] scripts/governance/check_module_singlesource.py;docs/03_modules/_cross_layer/model_profiler/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=PASS, exit 1=VIOLATION, exit 2=ERROR
# [TESTS] tests/test_check_module_singlesource.py
# [TTL] task_bound
"""GATE-SSOT-SINGLESOURCE: SSoT 单一真源门禁（Phase 7 治本防复发）。

防止考试系统受保护文件名在非声明 SSoT 路径下重复出现。

与现有 GATE-SSOT（check_ssot_gate.py）的区别：
    - GATE-SSOT 基于 [MODULE] header 的 module_path 冲突检测，只看 staged 新增文件
    - 本脚本基于文件名检测，扫描全量 src/zephyr/ 文件，覆盖无 header 的副本盲区

病根（v5 调研结论）：
    7 副本正是 AI「不搜索就新生成」的产物——即使没有 [MODULE] header，
    只要文件名匹配受保护列表且在非 SSoT 路径下，即为违规。

受保护文件名（考试系统核心，源自 v5 计划 P7.1）：
    exam_orchestrator, exam_test_cases, capability_passport,
    exam_judge, exam_rubric, exam_executor

声明 SSoT 路径：
    src/zephyr/intelligence/model_profiling/

用法:
    python scripts/governance/check_module_singlesource.py          # 扫描并报告
    python scripts/governance/check_module_singlesource.py --check    # CI 模式（exit 1 on violation）

Exit codes:
    0 = PASS（无违规）
    1 = VIOLATION（受保护文件名出现在非 SSoT 路径下）
    2 = ERROR（脚本异常）
"""
from __future__ import annotations

__manifest__ = """
args: []
description: 'GATE-SSOT-SINGLESOURCE: SSoT 单一真源门禁（Phase 7 治本防复发）。'
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import sys
from pathlib import Path

# 一次性 bootstrap sys.path（N 值对本文件固定且仅用一次）
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402

# ── 配置：受保护文件名 → 声明 SSoT 路径 ──────────────────────────────
# 真源：v5 计划 P7.1 + 考试系统治本调研报告
# 后续可扩展为 YAML 配置（data/governance/ssot_protected_files.yaml）

# 受保护文件名（不含 .py 后缀）
PROTECTED_FILENAMES: set[str] = {
    "exam_orchestrator",
    "exam_test_cases",
    "capability_passport",
    "exam_judge",
    "exam_rubric",
    "exam_executor",
}

# 声明 SSoT 路径（受保护文件名只能在此目录下出现）
# 真源：docs/03_modules/_cross_layer/model_profiler/blueprint.md frontmatter actual_disk_path
SSOT_PATH = "src/zephyr/intelligence/model_profiling"

# 扫描根目录
SCAN_ROOT = REPO_ROOT / "src" / "zephyr"


def scan_violations() -> list[dict]:
    """扫描 src/zephyr/ 下所有 .py 文件，检测受保护文件名是否出现在非 SSoT 路径下。

    Returns:
        violations: 违规列表，每项含 {filename, path, ssot_path}
    """
    violations: list[dict] = []
    ssot_full_path = (REPO_ROOT / SSOT_PATH).resolve()

    for py_file in SCAN_ROOT.rglob("*.py"):
        # 提取文件名（不含 .py 后缀）
        stem = py_file.stem
        if stem not in PROTECTED_FILENAMES:
            continue

        # 检查文件是否在 SSoT 路径下
        file_resolved = py_file.resolve()
        try:
            file_resolved.relative_to(ssot_full_path)
            # 在 SSoT 路径下 → 合法，跳过
            continue
        except ValueError:
            # 不在 SSoT 路径下 → 违规
            rel_path = py_file.relative_to(REPO_ROOT)
            violations.append({
                "filename": py_file.name,
                "path": str(rel_path).replace("\\", "/"),
                "ssot_path": SSOT_PATH,
            })

    return violations


def format_report(violations: list[dict]) -> str:
    """格式化违规报告。"""
    if not violations:
        return "[OK] No SSoT single-source violations detected."

    lines = [
        f"[VIOLATION] {len(violations)} SSoT single-source violation(s) detected:",
        "",
    ]
    for v in violations:
        lines.extend([
            f"  File: {v['filename']}",
            f"  Path: {v['path']}",
            f"  Expected SSoT: {v['ssot_path']}/",
            "",
        ])
    lines.extend([
        "Fix: Delete the violating file or move it to the SSoT path.",
        f"SSoT path: {SSOT_PATH}/",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="SSoT single-source gate: detect protected filenames outside declared SSoT path"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="CI mode: exit 1 on violation (default: report only)",
    )
    args = parser.parse_args()

    try:
        violations = scan_violations()
    except Exception as e:
        print(f"[ERROR] scan failed: {e}", file=sys.stderr)
        return 2

    report = format_report(violations)
    print(report)

    if violations and args.check:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
