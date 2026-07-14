# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/detect_config_deviation.py | §
# [MODULE] scripts.governance.meta.detect_config_deviation
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
detect_config_deviation.py — 配置文件结构完整性检测（蓝图 §28 B65 + B87）

检测 _shared/thresholds.yaml 和 manifest 的结构完整性：
- thresholds.yaml 顶层阈值组（值为 dict）必须非空
- manifest 必填字段存在性

治本（ARCH-036 P3-A5）：删除原 EXPECTED_THRESHOLD_GROUPS 白名单比对——
白名单本身是硬编码第二真源，导致自指矛盾（检测器自己违反 trae_060 §2）+
双真源同步漂移（concurrency/directory_scalability 遗漏即此问题）+
元数据字段误报（module_id 被报为"未声明的阈值组"）。
改为结构校验：thresholds.yaml 是 SSoT，新增组即合法，无需白名单登记。

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

# ARCH-036 P3-A5: 删除 EXPECTED_THRESHOLD_GROUPS 白名单（自指硬编码+双真源漂移）
# 改为结构校验：顶层 dict 值字段必须非空（阈值组），元数据字段（str/int/bool）跳过。
# 这样新增阈值组无需更新检测器，消除双真源同步反模式。


def check_thresholds() -> list[str]:
    """检查 thresholds.yaml 结构完整性（治本 ARCH-036 P3-A5: 删除白名单，改为结构校验）。

    原逻辑用硬编码 EXPECTED_THRESHOLD_GROUPS 白名单比对，导致：
    - 自指硬编码（检测器自身违反 trae_060 §2）
    - 双真源同步（thresholds.yaml + 白名单必须同步，concurrency 遗漏即此问题）
    - 元数据字段误报（module_id 被报为"未声明的阈值组"）

    新逻辑：thresholds.yaml 是 SSoT，顶层 dict 值字段必须非空（阈值组），
    元数据字段（str/int/bool/None）自动跳过。新增组即合法，无需白名单登记。
    """
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

    if not isinstance(data, dict):
        return ["thresholds.yaml 顶层结构不是 dict"]

    # 结构校验：值为 dict 的顶层字段是阈值组，必须非空
    # 元数据字段（module_id 等，值为 str/int/bool/None）自动跳过
    threshold_group_count = 0
    for key, value in data.items():
        if not isinstance(value, dict):
            continue  # 元数据字段，跳过
        threshold_group_count += 1
        if not value:
            violations.append(f"thresholds.yaml 阈值组为空: {key}")

    # 防御性检查：至少应有阈值组存在（避免空文件被误判通过）
    if threshold_group_count == 0:
        violations.append("thresholds.yaml 无任何阈值组（顶层 dict 值字段）")

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
