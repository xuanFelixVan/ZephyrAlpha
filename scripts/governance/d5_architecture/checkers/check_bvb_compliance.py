# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_bvb_compliance.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_bvb_compliance
# [DOMAIN] D-GOVERNANCE
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
"""对标 architecture_principles.md §3 BvB 五维评分法：
  新引入的 OSS 依赖必须通过五维评估（License/Security/Maintenance/Community/Ecosystem）。

检查内容：
  1. technology_landscape.yaml 中 Build/Adopt/Trial 类别的技术条目
     是否有 bvb_score 字段
  2. bvb_score 是否包含全部 5 个维度（license/security/maintenance/community/ecosystem）
  3. 每个维度分数是否在 1-5 范围内
  4. 加权总分是否 >= 3.0（通过门槛）

exit: 0=pass, 1=compliance gap, 2=error
"""

from __future__ import annotations

__manifest__ = """
dimensions: [D5, D11]
priority: P1
timeout_seconds: 30
args:
  - {flag: --warn-only, type: bool, description: "仅警告模式"}
warn_only: false
description: BvB 五维评分法自动化校验——OSS 依赖准入合规
"""

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

TECH_LANDSCAPE = (
    REPO_ROOT
    / "docs"
    / "02_enterprise_architecture"
    / "target_architecture"
    / "architecture_model"
    / "technology"
    / "technology_landscape.yaml"
)

BVB_DIMENSIONS = {"license", "security", "maintenance", "community", "ecosystem"}
BVB_WEIGHTS = {"license": 0.25, "security": 0.30, "maintenance": 0.20, "community": 0.15, "ecosystem": 0.10}
BVB_PASS_THRESHOLD = 3.0
REQUIRES_BVB = {"adopt", "trial", "build", "Adopt", "Trial", "Build"}


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    import yaml

    if not TECH_LANDSCAPE.is_file():
        print(f"technology_landscape.yaml 不存在: {TECH_LANDSCAPE}")
        return EXIT_ERROR
    data = yaml.safe_load(TECH_LANDSCAPE.read_text(encoding="utf-8"))
    entries = data.get("technologies") or data.get("technology_landscape") or data.get("entries") or []

    if not entries:
        print("technology_landscape.yaml 无技术条目")
        return EXIT_PASS
    missing_score = []
    incomplete_dims = []
    below_threshold = []

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name") or entry.get("id") or "unknown"
        quadrant = entry.get("quadrant") or entry.get("status") or ""
        if quadrant not in REQUIRES_BVB:
            continue

        bvb = entry.get("bvb_score")
        if not bvb or not isinstance(bvb, dict):
            missing_score.append(name)
            continue

        dims_present = set(bvb.keys()) & BVB_DIMENSIONS
        if dims_present != BVB_DIMENSIONS:
            missing_dims = BVB_DIMENSIONS - dims_present
            incomplete_dims.append(f"{name} (缺: {', '.join(sorted(missing_dims))})")
            continue

        for dim, val in bvb.items():
            if dim in BVB_DIMENSIONS and (not isinstance(val, (int, float)) or val < 1 or val > 5):
                incomplete_dims.append(f"{name} ({dim}={val} 不在 1-5 范围)")
                break
        else:
            weighted = sum(bvb.get(d, 0) * BVB_WEIGHTS[d] for d in BVB_DIMENSIONS)
            if weighted < BVB_PASS_THRESHOLD:
                below_threshold.append(f"{name} (加权={weighted:.2f} < {BVB_PASS_THRESHOLD})")

    total_requires = len(missing_score) + len(incomplete_dims) + len(below_threshold)
    checked = sum(1 for e in entries if isinstance(e, dict) and (e.get("quadrant") or e.get("status")) in REQUIRES_BVB)

    if missing_score:
        print(f"[WARN] {len(missing_score)} 个技术条目缺少 bvb_score:")
        for n in missing_score[:10]:
            print(f"  - {n}")

    if incomplete_dims:
        print(f"[WARN] {len(incomplete_dims)} 个技术条目 BvB 维度不完整:")
        for n in incomplete_dims[:10]:
            print(f"  - {n}")

    if below_threshold:
        print(f"[WARN] {len(below_threshold)} 个技术条目 BvB 加权分低于门槛:")
        for n in below_threshold[:10]:
            print(f"  - {n}")

    if total_requires > 0:
        print(f"\nBvB 五维评分合规率: {checked - total_requires}/{checked}")
        return EXIT_FINDINGS
    print(f"OK: BvB 五维评分合规 — {checked} 个技术条目全部通过")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
