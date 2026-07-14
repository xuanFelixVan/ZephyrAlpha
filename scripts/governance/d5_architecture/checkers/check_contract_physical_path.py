# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_contract_physical_path.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_contract_physical_path
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
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
check_contract_physical_path.py — GATE-CONTRACT-PHYSICAL-PATH

检测 cross_layer_contracts.yaml 中 physical_path 字段是否指向连字符目录。

病根 (2026-06-28 SSoT 三重冗余修复):
  CT-TEL-001~004 的 physical_path 历史指向 src/zephyr/system-telemetry/ (连字符目录),
  Python 无法 import 连字符目录名, 导致 codegen 产物全是死代码.
  治本: physical_path 改为 null 停止 codegen. 但下一个 AI 可能"修复" null 为路径,
  让死代码复活. 本门禁治本: 检测 physical_path 指向连字符目录即 hard block.

检测规则:
  - physical_path 为 null/空 → OK (codegen 自动跳过, generate_contracts.py 第 540 行)
  - physical_path 路径中任何目录段含连字符 → hard block (exit 1 in --ci)
    Python 模块名必须匹配 [a-zA-Z_][a-zA-Z0-9_]*, 连字符不合法.
  - 已知死路径模式 (system-telemetry) 单独提示

模式:
  --ci (默认): 连字符目录 → exit 1
  --warn-only: 全部 exit 0 (仅报告, 不阻断)

实现:
  - yaml.safe_load 加载 cross_layer_contracts.yaml
  - 遍历 contracts 列表, 对每个 physical_path 字段做路径段分析
  - 路径分隔符统一为 / 处理跨平台
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
import re

import yaml

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

__manifest__ = """
args:
- --ci
- --warn-only
description: GATE-CONTRACT-PHYSICAL-PATH - 检测 cross_layer_contracts.yaml 中 physical_path 指向连字符目录
dimensions:
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

CONTRACTS_YAML: Path = REPO_ROOT / (
    "architecture_model/contracts/cross_layer_contracts.yaml"
)

# Python 标识符正则: [a-zA-Z_][a-zA-Z0-9_]*
# 目录段必须匹配此正则才能被 Python import
_IDENT_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

# 已知历史死路径模式 (用于精确提示)
_KNOWN_DEAD_PATTERNS = ["system-telemetry"]


def _check_physical_path(contract_id: str, physical_path: str) -> list[str]:
    """检查单个 physical_path 是否含连字符目录段, 返回违规信息列表."""
    issues: list[str] = []
    if not physical_path:
        return issues

    # 统一路径分隔符
    normalized = physical_path.replace("\\", "/")
    parts = normalized.split("/")

    # 最后一段是文件名 (.py), 不检查; 其余是目录段, 必须是合法 Python 标识符
    dir_parts = parts[:-1] if parts[-1].endswith(".py") else parts

    for idx, segment in enumerate(dir_parts):
        if not segment:
            continue  # 跳过空段 (如开头的 src/)
        if not _IDENT_RE.match(segment):
            # 检测是否为已知死路径模式
            known = segment in _KNOWN_DEAD_PATTERNS
            marker = " (已知死路径, Python 无法 import)" if known else " (含非法字符, Python 无法 import)"
            issues.append(
                f"  {contract_id}: physical_path='{physical_path}' "
                f"目录段[{idx}]='{segment}'{marker}"
            )
    return issues


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci", action="store_true", help="硬阻断模式 (发现违规 exit 1)")
    parser.add_argument("--warn-only", action="store_true", help="仅告警不阻断")
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args()

    if not CONTRACTS_YAML.exists():
        print(f"WARN: {CONTRACTS_YAML} 不存在, 跳过")
        return EXIT_PASS

    try:
        data = yaml.safe_load(CONTRACTS_YAML.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        print(f"FAIL: {CONTRACTS_YAML} YAML 解析失败: {e}")
        return EXIT_FINDINGS

    contracts = data.get("contracts", []) if isinstance(data, dict) else []
    if not contracts:
        print("WARN: contracts 列表为空, 跳过")
        return EXIT_PASS

    all_issues: list[str] = []
    null_count = 0
    valid_count = 0

    for ctr in contracts:
        if not isinstance(ctr, dict):
            continue
        contract_id = ctr.get("id", "<unknown>")
        physical = ctr.get("physical_path", "")
        if not physical:
            null_count += 1
            continue
        issues = _check_physical_path(contract_id, physical)
        if issues:
            all_issues.extend(issues)
        else:
            valid_count += 1

    print(f"[GATE-CONTRACT-PHYSICAL-PATH] 扫描 {len(contracts)} 条契约: "
          f"valid={valid_count}, null(跳过 codegen)={null_count}, 违规={len(all_issues)}")

    if not all_issues:
        print("OK: 所有 physical_path 路径合法 (无连字符目录)")
        return EXIT_PASS

    print("FAIL: 发现 physical_path 指向连字符目录 (Python 无法 import, codegen 产物为死代码):")
    for issue in all_issues:
        print(issue)

    print("\n修复方式:")
    print("  1. 如果契约有手工实现真源: 把 physical_path 改为 null (停止 codegen)")
    print("     参照 CT-TEL-001~004 模式, 在 null 后注释指明真源路径")
    print("  2. 如果确实需要 codegen: 把目录名改为下划线 (如 system-telemetry → system_telemetry)")
    print("     并同步迁移已有代码到新目录")

    if args.warn_only:
        print("WARN: 跳过 (warn-only 模式)")
        return EXIT_PASS
    return EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
