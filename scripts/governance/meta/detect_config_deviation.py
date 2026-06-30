# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/detect_config_deviation.py | §
# [MODULE] scripts.governance.meta.detect_config_deviation
# [DOMAIN] D_GOVERNANCE
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
detect_config_deviation.py — 配置文件与蓝图规范偏差检测（蓝图 §28 B65 + B87）

检测 _shared/thresholds.yaml 和 manifest 中与蓝图声明不一致的地方：
- thresholds.yaml 中是否有蓝图未声明的阈值组
- manifest 中脚本声明是否与 §15.2 八组阈值对应
- 配置文件中过期/残留字段

Usage:
    python scripts/governance/meta/detect_config_deviation.py
    python scripts/governance/meta/detect_config_deviation.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 配置文件与蓝图规范偏差检测 — thresholds/manifest 一致性
dimensions:
- D3
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

_SCRIPT_DIR = Path(__file__).resolve().parents[1]
_GOV_DIR = str(_SCRIPT_DIR)
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import EXIT_PASS, SCRIPTS_DIR

THRESHOLDS_PATH = SCRIPTS_DIR / "_shared" / "thresholds.yaml"
MANIFEST_PATH = SCRIPTS_DIR / "script_manifest.yaml"

EXPECTED_THRESHOLD_GROUPS = {
    "scanning",
    "finding_quality",
    "error_budget",
    "sla_timers",
    "shadow_mode",
    "script_health",
    "ast_similarity",
    "blueprint_sync",
    "concurrency",  # ARCH-036 P3-A5: 补齐第九组（蓝图 §35 分布式执行，原遗漏）
}


def check_thresholds() -> list[str]:
    """检查 thresholds.yaml 是否与蓝图声明的八组阈值一致。"""
    violations: list[str] = []
    if yaml is None:
        return ["PyYAML 未安装 — 无法解析 thresholds.yaml"]
    if not THRESHOLDS_PATH.exists():
        return ["thresholds.yaml 不存在"]
    try:
        with open(THRESHOLDS_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return ["thresholds.yaml YAML 解析失败"]

    for group in EXPECTED_THRESHOLD_GROUPS:
        if group not in data:
            violations.append(f"thresholds.yaml 缺少阈值组: {group}")
    for group in data:
        if group not in EXPECTED_THRESHOLD_GROUPS:
            violations.append(f"thresholds.yaml 中存在未声明的阈值组: {group}")
    return violations


def check_manifest() -> list[str]:
    """检查 manifest 是否有过期/残留字段。"""
    violations: list[str] = []
    if not MANIFEST_PATH.exists():
        return ["script_manifest.yaml 不存在"]
    if yaml is None:
        return ["PyYAML 未安装 — 无法解析 script_manifest.yaml"]
    try:
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return ["script_manifest.yaml YAML 解析失败"]

    required = {"total_scripts", "categories", "scripts"}
    for r in required:
        if r not in data:
            violations.append(f"script_manifest.yaml 缺少必填字段: {r}")
    return violations


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="配置文件与蓝图规范偏差检测")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()

    all_violations: list[str] = []
    all_violations.extend(check_thresholds())
    all_violations.extend(check_manifest())

    if all_violations:
        print(f"\n[CONFIG-DEVIATION] 发现 {len(all_violations)} 处偏差：\n", file=sys.stderr)
        for v in all_violations:
            print(f"  ⚠ {v}", file=sys.stderr)
        print(file=sys.stderr)
    else:
        print("\n[CONFIG-DEVIATION] ✅ 配置文件与蓝图一致\n", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
