# [BLUEPRINT] MOD-LIB-003 | docs/03_modules/_domain_library/blueprint.md | §3
# [MODULE] scripts.governance.generators.check_library_coverage
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.library.collectors.fs_collector; zephyr.governance.depgraph_schema
# [CONSUMERS] docs/library/COVERAGE.md；总攻验收门
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 双向差集=blind（盘有馆无）+ghost(馆有盘无, deceased 除外)；全程只读；报告自带索书号
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DB 不可达非零退出
# [TESTS] tests/library/test_library_smoke.py
# [A_module] module_id=MOD-LIB-003 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""check_library_coverage.py — 双向对账：盲册（blind）+ghost 报告生成器。

Usage::

    python scripts/governance/generators/check_library_coverage.py
# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/generators/check_library_coverage.yaml
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Final

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.library.collectors.fs_collector import collect as fs_collect
from zephyr.shared.utils.time_utils import now_utc

__all__ = ["run_coverage"]

_OUT: Final[Path] = Path("docs/_working/ultimate_library/COVERAGE.md")

_SQL_IDS = (
    "SELECT asset_id, home, status FROM lib_assets"  # noqa: bare-sql  模块级 _SQL_IDS 常量内部行（锁内 AST 豁免，inline 预检无 AST 需行级标记）
    " WHERE kind IN ('file','module','doc','registry')"
    " AND status NOT IN ('deceased','archived')"
)


def run_coverage(root: str = ".") -> dict[str, Any]:
    """双向对账：盘↔馆差集，写 COVERAGE.md。

    Args:
        root: 仓库根。

    Returns:
        {blind_n, ghost_n, blind_sample, ghost_sample}。
    """
    disk_assets = fs_collect(root)
    disk_ids = {a["asset_id"]: a["home"] for a in disk_assets}
    conn = get_depgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(_SQL_IDS)
            catalog = {r[0]: (r[1], r[2]) for r in cur.fetchall()}
    finally:
        conn.close()
    blind = sorted(set(disk_ids) - set(catalog))
    disk_homes = set(disk_ids.values())
    ghost = sorted(aid for aid, (home, _status) in catalog.items() if home not in disk_homes)
    stamp = now_utc().isoformat()
    lines = [
        "---",
        'asset_id: "DOC:docs/_working/ultimate_library/COVERAGE.md"',
        'ttl: "task_bound"',
        'doc_type: "audit_report"',
        "---",
        "",
        "# 馆藏双向对账报告（盲册+ghost）",
        "",
        f"- 构建时戳（UTC）：{stamp}",
        f"- 盘上在扫文件：{len(disk_ids)}｜馆内在编（file/module）：{len(catalog)}",
        f"- **blind（盘有馆无）：{len(blind)}**",
        f"- **ghost（馆有盘无）：{len(ghost)}**",
        "",
        "## blind 样本（前 50）",
        "",
    ]
    lines += [f"- {aid}" for aid in blind[:50]]
    lines += ["", "## ghost 样本（前 50）", ""]
    lines += [f"- {aid}" for aid in ghost[:50]]
    _OUT.parent.mkdir(parents=True, exist_ok=True)
    _OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return {
        "blind_n": len(blind),
        "ghost_n": len(ghost),
        "blind_sample": blind[:10],
        "ghost_sample": ghost[:10],
    }


def main() -> int:
    """CLI 入口：打印摘要。"""
    result = run_coverage()
    print(f"blind={result['blind_n']} ghost={result['ghost_n']} report={_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
