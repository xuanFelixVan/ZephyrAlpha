# [MODULE] scripts.governance.registry_projection.registry_projection_generator
# [DOMAIN] D_GOV_CODE_QUALITY
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §W-M1
# [TESTS] tests/governance/registry_projection/test_projection_generator.py
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: W-M1 验收/运维通道按需调用 runner（人工+CI+监控事件触发），非 cron 非 daemon 非常驻
# [DEPENDENCIES] zephyr.governance.registry_projection.generator (run, default_registry)
# [CONSUMERS] 运维/施工验收 CLI；意图 API 后置钩子（wave-1 接线）；belt daemon 探针（走库内 run）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] --check 零写（影子期对账/验收通道）；--render 全自动四象限处置（PG wins）；
#   PG 不可达=降级退出零阻塞；本 CLI 永不直接改注册表内容（唯一写者=生成器编排层）
# [MODIFY-GUARD] 新建 2026-09-23 st-wm1-buildB-20260923（W-M1 波0 车道B）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 退出码：0=通过/已纠正；2=发现漂移（check 模式）；3=降级（PG 不可达等）；其余=编程错误
"""registry_projection_generator.py — 投影生成器 CLI。

Usage::

    python scripts/governance/registry_projection/registry_projection_generator.py --check
    python scripts/governance/registry_projection/registry_projection_generator.py --render
    python scripts/governance/registry_projection/registry_projection_generator.py --check \
        --snapshot-file .runtime/tmp/snap.json      # JSON 快照源（影子期/红蓝通道）
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  canonical 常量，禁本地重定义（SSOT）

if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from zephyr.governance.registry_projection.projection_generator import default_registry, run  # noqa: E402

EXIT_OK = 0
EXIT_DRIFT = 2
EXIT_DEGRADED = 3


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="注册表投影生成器（YAML := render(账本快照)）")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="零写判漂移（影子期/验收通道）")
    group.add_argument("--render", action="store_true", help="按四象限全自动处置（PG wins）")
    parser.add_argument("--snapshot-file", help="JSON 快照文件源（缺省=PG registry_snapshot 最新版）")
    parser.add_argument("--registry-id", help="缺省 REG-CAPCAN-001")
    parser.add_argument("--physical-path", help="缺省 capability_canonical_file_registry.yaml")
    parser.add_argument("--project-root", default=str(REPO_ROOT))
    parser.add_argument("--session", default="", help="调用方 session（记账归因）")
    args = parser.parse_args(argv)

    rid, phys = default_registry()
    report = run(
        args.project_root,
        mode="render" if args.render else "check",
        source=args.snapshot_file,
        registry_id=args.registry_id or rid,
        physical_path=args.physical_path or phys,
        actor_session=args.session,
    )
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    if report.ok:
        return EXIT_OK
    return EXIT_DEGRADED if report.quadrant == "pg_unreachable" else EXIT_DRIFT


if __name__ == "__main__":
    raise SystemExit(main())
