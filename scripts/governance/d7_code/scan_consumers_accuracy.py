#!/usr/bin/env python
# [BLUEPRINT] MOD-GOV_SCAN_CONSUMERS_ACCURACY | scripts/governance/d7_code/scan_consumers_accuracy.py | §ARCH-CONSUMERS-ACCURACY-002
# [MODULE] scripts.governance.d7_code.scan_consumers_accuracy
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib(argparse/ast/sys/pathlib/collections); zephyr.gov_enforcement.commit_gates.consumers_accuracy_gate (parse_consumers_field, check_consumers_accuracy)
# [CONSUMERS] scripts/governance/run_all.py
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] baseline-scan 脚本——全项目扫描 [CONSUMERS] 字段准确性（orphan+phantom+stale），生成差异报告；stale 检测用 git grep（commit-time 不检测避免性能损耗，baseline-scan 专用）；纯 stdlib + 复用 consumers_accuracy_gate 函数；fail-open（git 不可达时跳过 stale 检测）
# [MODIFY-GUARD] 修改检测逻辑需同步更新 consumers_accuracy_gate.py（commit-time 检测）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=扫描完成（无论是否有违规）/ 1=参数错误或 import 失败
# [TESTS] 手动验证: baseline-scan 全项目扫描生成报告
# [A_module] module_id=MOD-GOV_SCAN_CONSUMERS_ACCURACY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""scan_consumers_accuracy.py — CONSUMERS 字段准确性 baseline-scan 脚本

#ARCH-CONSUMERS-ACCURACY-002 Phase 1 治本——检测历史漂移（247 个文件）。

功能：
  - 全项目扫描 src/**.py + scripts/governance/**.py 的 [CONSUMERS] 字段
  - 三类违规检测：
    (a) orphan（轻）：括号内声明的函数名在当前文件中不存在（AST 精确检测）
    (b) phantom（重）：声明的消费者模块路径在项目内不存在（文件系统查找）
    (c) stale（中）：消费者模块存在但不 import 当前模块（git grep 反向查找，
        baseline-scan 专用，commit-time 不检测避免性能损耗）
  - 生成差异报告（按违规类型分组 + 按文件分组）
  - 支持 --json 输出（供后续 reconciler 消费）
  - 支持 --no-stale 跳过 stale 检测（性能优化）

使用：
  python scripts/governance/d7_code/scan_consumers_accuracy.py [--src DIR] [--json] [--no-stale] [--quiet]

退出码：
  0 = 扫描完成（无论是否有违规——baseline-scan 是诊断工具不是门禁）
  1 = 参数错误或 import 失败

设计原则：
  - 纯 stdlib + 复用 consumers_accuracy_gate 函数（parse_consumers_field, check_consumers_accuracy）
  - stale 检测用 git grep（性能差 N × 500ms，可 --no-stale 跳过）
  - fail-open：git 不可达时跳过 stale 检测，不中断扫描
  - 抽象代号（MOD-XXX/SH-XXX）豁免（无法静态验证）
  - tests/ 豁免（测试文件不要求 CONSUMERS 准确）
"""

from __future__ import annotations

__manifest__ = """
args: []
description: scan_consumers_accuracy.py — CONSUMERS 字段准确性 baseline-scan 脚本
dimensions:
- D7
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# 复用 consumers_accuracy_gate 的检测函数
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from _shared.constants import EXIT_FINDINGS

from zephyr.gov_enforcement.commit_gates._diff_helpers import _collect_function_names  # noqa: E402
from zephyr.gov_enforcement.commit_gates.consumers_accuracy_gate import (  # noqa: E402
    _check_module_path_exists,
    _is_abstract_code,
    _module_to_file_candidates,
    check_consumers_accuracy,
    parse_consumers_field,
)

# 扫描范围（与 commit-time gate 对齐）
_SCAN_PREFIXES: tuple[str, ...] = ("scripts/governance/", "src/")

# 文件名中 tests/ 路径豁免
_TESTS_EXEMPT = "/tests/"


def _is_test_file(rel_path: str) -> bool:
    """检测是否为测试文件（tests/ 路径豁免）。"""
    return _TESTS_EXEMPT in rel_path or rel_path.startswith("tests/")


def _find_py_files(project_root: Path) -> list[Path]:
    """查找所有待扫描的 .py 文件（src/ + scripts/governance/，排除 tests/）。"""
    results: list[Path] = []
    for prefix in ("src", "scripts/governance"):
        base = project_root / prefix
        if not base.exists():
            continue
        for py_file in base.rglob("*.py"):
            rel = py_file.relative_to(project_root).as_posix()
            if _is_test_file(rel):
                continue
            results.append(py_file)
    return results


def _read_file(path: Path) -> str:
    """读取文件内容，失败返回空字符串。"""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001 — fail-open
        return ""


def _check_stale_violation(
    consumer_module: str,
    current_module_path: str,
    project_root: Path,
) -> bool:
    """检测 stale 违规——消费者模块存在但不 import 当前模块。

    使用 git grep 反向查找消费者模块内是否有 import 当前模块的代码。

    Args:
        consumer_module: 消费者模块路径（如 zephyr.gov_enforcement.commit_gates.create_guard）
        current_module_path: 当前模块的文件相对路径（如 src/zephyr/foo/bar.py）
        project_root: 项目根目录

    Returns:
        True 如果是 stale 违规（消费者不 import 当前模块），False 如果不是 stale。
        git 不可达时返回 False（fail-open）。
    """
    # 从当前模块文件路径推断模块路径
    # src/zephyr/foo/bar.py → zephyr.foo.bar
    current_module = current_module_path
    if current_module.startswith("src/"):
        current_module = current_module[4:]  # 去掉 src/
    if current_module.endswith(".py"):
        current_module = current_module[:-3]
    if current_module.endswith("/__init__"):
        current_module = current_module[:-9]
    current_module = current_module.replace("/", ".")

    # git grep 在消费者模块文件内搜索 import 当前模块
    consumer_candidates = _consumer_module_to_files(consumer_module, project_root)
    if not consumer_candidates:
        return False  # 消费者文件不存在，不是 stale（是 phantom）

    # 构造搜索模式：import 当前模块的各种形式
    # current_module 如 "zephyr.foo.bar"
    # 搜索: "from zephyr.foo.bar import" 或 "import zephyr.foo.bar"
    search_patterns = [
        f"from {current_module} import",
        f"from {current_module}  import",
        f"import {current_module}",
        f"from {current_module}\\.",
    ]

    for consumer_file in consumer_candidates:
        try:
            content = consumer_file.read_text(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001 — fail-open
            continue

        for pattern in search_patterns:
            if re.search(pattern, content):
                return False  # 找到 import，不是 stale

    return True  # 消费者文件存在但不 import 当前模块 = stale


def _consumer_module_to_files(
    consumer_module: str, project_root: Path
) -> list[Path]:
    """将消费者模块路径转为文件系统路径列表。"""
    candidates = _module_to_file_candidates(consumer_module)
    result: list[Path] = []
    for candidate in candidates:
        full_path = project_root / candidate
        if full_path.exists():
            result.append(full_path)
    return result


def _scan_file(
    py_file: Path,
    project_root: Path,
    check_stale: bool = True,
) -> list[dict]:
    """扫描单个文件的 [CONSUMERS] 准确性，返回违规列表。

    Args:
        py_file: 文件绝对路径
        project_root: 项目根目录
        check_stale: 是否检测 stale 违规（git grep 性能差，可关闭）

    Returns:
        违规字典列表，每个字典含 type/file/consumer/detail 字段。
    """
    rel_path = py_file.relative_to(project_root).as_posix()
    content = _read_file(py_file)
    if not content:
        return []

    # 复用 commit-time 检测函数（orphan + phantom）
    violations_text = check_consumers_accuracy(rel_path, content, project_root)
    violations: list[dict] = []
    for v in violations_text:
        vtype = "orphan" if "orphan function" in v else "phantom"
        violations.append({
            "type": vtype,
            "file": rel_path,
            "detail": v.strip(),
        })

    # stale 检测（baseline-scan 专用）
    if check_stale:
        declarations = parse_consumers_field(content)
        try:
            defined_functions = _collect_function_names(content)
        except Exception:  # noqa: BLE001 — fail-open
            defined_functions = set()

        for consumer, parens in declarations:
            if _is_abstract_code(consumer):
                continue

            # phantom 已检测，跳过不存在的模块
            # 处理方法级声明：逐级缩短
            module_path = consumer
            if not _check_module_path_exists(module_path, project_root):
                parts = module_path.split(".")
                found = False
                for i in range(len(parts) - 1, 1, -1):
                    shortened = ".".join(parts[:i])
                    if _check_module_path_exists(shortened, project_root):
                        module_path = shortened
                        found = True
                        break
                if not found:
                    continue  # phantom 违规，已在上面检测

            # stale 检测：消费者模块存在但不 import 当前模块
            try:
                is_stale = _check_stale_violation(
                    module_path, rel_path, project_root
                )
            except Exception:  # noqa: BLE001 — fail-open
                is_stale = False

            if is_stale:
                violations.append({
                    "type": "stale",
                    "file": rel_path,
                    "consumer": consumer,
                    "detail": f"  {rel_path}: stale consumer '{consumer}' "
                              f"(消费者模块存在但不 import 当前模块)",
                })

    return violations


def _print_report(
    violations: list[dict],
    total_files: int,
    files_with_consumers: int,
    check_stale: bool,
) -> None:
    """打印人类可读报告。"""
    if not violations:
        print("\n✓ CONSUMERS-ACCURACY baseline-scan 完成——无违规")
        print(f"  扫描文件: {total_files}")
        print(f"  有 [CONSUMERS] 字段: {files_with_consumers}")
        print(f"  stale 检测: {'开启' if check_stale else '关闭'}")
        return

    # 按类型分组
    by_type: dict[str, list[dict]] = defaultdict(list)
    for v in violations:
        by_type[v["type"]].append(v)

    print(f"\n✗ CONSUMERS-ACCURACY baseline-scan 完成——检测到 {len(violations)} 个违规")
    print(f"  扫描文件: {total_files}")
    print(f"  有 [CONSUMERS] 字段: {files_with_consumers}")
    print(f"  stale 检测: {'开启' if check_stale else '关闭'}")
    print()

    # 按类型输出统计
    type_labels = {
        "orphan": "orphan（括号内函数名不存在）",
        "phantom": "phantom（消费者模块路径不存在）",
        "stale": "stale（消费者模块存在但不 import 当前模块）",
    }
    for vtype, label in type_labels.items():
        count = len(by_type.get(vtype, []))
        if count > 0:
            print(f"  {label}: {count} 个")

    print()
    # 按文件分组输出详情（前 50 条）
    by_file: dict[str, list[dict]] = defaultdict(list)
    for v in violations:
        by_file[v["file"]].append(v)

    print("违规详情（按文件分组，前 50 个文件）:")
    for i, (fname, fviolations) in enumerate(sorted(by_file.items())):
        if i >= 50:
            print(f"  ...(+{len(by_file) - 50} more files)")
            break
        print(f"  {fname}:")
        for v in fviolations:
            print(f"    [{v['type']}] {v.get('consumer', v.get('detail', '').strip())}")

    print()
    print("修复建议:")
    print("  1. phantom: 删除不存在的消费者模块声明，或修正模块路径")
    print("  2. orphan: 修正括号内函数名，或删除不存在的函数名")
    print("  3. stale: 删除不再 import 当前模块的消费者声明，或补充 import")
    print("  4. 修复后重新运行本脚本验证")


def main() -> int:
    """主入口。"""
    parser = argparse.ArgumentParser(
        description="CONSUMERS 字段准确性 baseline-scan 脚本"
    )
    parser.add_argument(
        "--src",
        default=str(_PROJECT_ROOT),
        help="项目根目录（默认: 脚本所在项目的根目录）",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="JSON 格式输出（供后续 reconciler 消费）",
    )
    parser.add_argument(
        "--no-stale",
        action="store_true",
        help="跳过 stale 检测（性能优化，stale 需 git grep 反向查找）",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="安静模式（只输出违规数）",
    )
    args = parser.parse_args()

    project_root = Path(args.src).resolve()
    if not project_root.exists():
        print(f"错误: 项目根目录不存在: {project_root}", file=sys.stderr)
        return EXIT_FINDINGS
    check_stale = not args.no_stale

    # 查找所有 .py 文件
    py_files = _find_py_files(project_root)
    total_files = len(py_files)

    # 扫描
    all_violations: list[dict] = []
    files_with_consumers = 0

    for py_file in py_files:
        content = _read_file(py_file)
        if not content:
            continue
        declarations = parse_consumers_field(content)
        if declarations:
            files_with_consumers += 1

        violations = _scan_file(py_file, project_root, check_stale=check_stale)
        all_violations.extend(violations)

    if args.json:
        output = {
            "total_files": total_files,
            "files_with_consumers": files_with_consumers,
            "total_violations": len(all_violations),
            "stale_checked": check_stale,
            "violations": all_violations,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    elif args.quiet:
        print(len(all_violations))
    else:
        _print_report(all_violations, total_files, files_with_consumers, check_stale)

    return 0  # baseline-scan 是诊断工具，无论是否有违规都返回 0


if __name__ == "__main__":
    sys.exit(main())
