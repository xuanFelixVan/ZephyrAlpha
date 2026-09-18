# [BLUEPRINT] GREATWALL-20260909-ROLE-MIGRATION | (长城任务 2026-09-09) | §
# [TTL] permanent
# [MODULE] scripts.industry_graph.migrate_roles
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] 长城任务 Phase3 S10 role 归一(Owner 2026-09-09 五值裁定); 引擎 S10 对账
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只增不删(纯 UPDATE role 列); 幂等(仅 role 仍为违规值时触发,复跑零行); 只迁活跃落位(valid_to IS NULL,PIT 关闭行保留历史原值); 映射表 role_migration.yaml 落盘留痕; 映射规则: mentioned->提及; 含龙头/第一/前二/第二/头部/梯队/领先/最大->龙头; 含核心->核心; 其余长尾->参与(Owner 2026-09-09 指令书裁定)
# [MODIFY-GUARD] graph_quality_standard.md(S10 词表真源)
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达->exit 2
# [TESTS] 2026-09-09 首跑: 9180 行归一/幂等复跑 0/引擎 S10 清零
"""S10 role 归一治理脚本（Owner 2026-09-09 五值裁定：龙头/核心/主要/参与/提及）。

映射规则（机械语义，全表落盘 role_migration.yaml）::

    mentioned        -> 提及   (直译,采购包英语值大头)
    含'龙头'         -> 龙头   (含 全球龙头/设备龙头)
    含'第一/前二/第二/头部/梯队/领先/最大' -> 龙头  ( leadership 语义等价)
    含'核心'         -> 核心
    其余长尾         -> 参与   (Owner 裁定兜底)

幂等锚：只迁 role 不在五值词表的活跃行；PIT 关闭行（valid_to 非空）保留历史原值。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

ROLES_STD = ("龙头", "核心", "主要", "参与", "提及")
LEADER_RE = "(龙头|第一|前二|第二|头部|梯队|领先|最大)"
MAP_PATH = Path(__file__).resolve().parent / "role_migration.yaml"

MIGRATION_SQL = f"""
UPDATE ig_node_company SET
  role = CASE
    WHEN role = 'mentioned' THEN '提及'
    WHEN role ~ '{LEADER_RE}' THEN '龙头'
    WHEN role LIKE '%核心%' THEN '核心'
    ELSE '参与'
  END,
  updated_at = now()
WHERE valid_to IS NULL
  AND (role IS NULL OR (role NOT IN ('龙头','核心','主要','参与','提及')))
"""


def main() -> int:
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    cur.execute(
        """SELECT coalesce(role,'(NULL)'), count(*) FROM ig_node_company
           WHERE valid_to IS NULL AND (role IS NULL OR role NOT IN ('龙头','核心','主要','参与','提及'))
           GROUP BY 1 ORDER BY 2 DESC"""
    )
    before = dict(cur.fetchall())
    cur.execute(MIGRATION_SQL)
    migrated = cur.rowcount
    conn.commit()
    cur.execute(
        """SELECT role, count(*) FROM ig_node_company WHERE valid_to IS NULL GROUP BY 1 ORDER BY 2 DESC"""
    )
    after = dict(cur.fetchall())
    conn.close()
    if migrated and not MAP_PATH.is_file():
        lines = [
            "# role 归一迁移映射表（Owner 2026-09-09 五值裁定，migrate_roles.py 生成）",
            "# 规则：mentioned->提及｜含 龙头/第一/前二/第二/头部/梯队/领先/最大 ->龙头｜含核心->核心｜其余->参与",
            "mapping:",
        ]
        for k in sorted(before):
            tgt = ("提及" if k == "mentioned"
                   else "龙头" if __import__("re").search(LEADER_RE, k)
                   else "核心" if "核心" in k
                   else "参与" if k != "(NULL)" else "提及")
            lines.append(f'  "{k}":')
            lines.append(f'    target: "{tgt}"')
            lines.append(f'    rows: {before[k]}')
        MAP_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "migrated": migrated,
        "before_by_role": before,
        "after_by_role": after,
        "map_file": str(MAP_PATH) if migrated else "skipped(零迁移,幂等)",
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] {e}")
        sys.exit(2)
