# [BLUEPRINT] GREATWALL-20260909-TIER-MIGRATION | (长城任务 2026-09-09) | §
# [TTL] permanent
# [MODULE] scripts.industry_graph.migrate_tier_to_function_role
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] 长城任务 Phase1 tier 职能化迁移(Owner 2026-09-09 v0.4 裁定); 引擎 S6/工具校验同 commit 切换后本脚本为存量唯一治理入口
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只增不删(纯 UPDATE); 幂等(仅 tier 仍为职能值时触发,复跑=0 行); 职能值(设备/材料/零部件/原材料/辅材)迁 function_role 八值词表, tier 位置归 上游(输入型环节=L1 主链模板口径); 迁移映射落盘 tier_migration_map.yaml 留痕; drill_manual 类钉死值不涉及(本脚本不触碰 child_chain_id/drill_status)
# [MODIFY-GUARD] graph_quality_standard.md(S6 词表真源,切换须同 commit)
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达->exit 2; 零迁移行->exit 0(幂等语义)
# [TESTS] 2026-09-09 首跑: 1433 行职能迁移/幂等复跑 0/引擎 S6 同 commit 切换后旧职能值清零
"""tier 职能化迁移治理脚本（Owner 2026-09-09 v0.4 裁定）。

语义收窄：位置（上游/中游/下游）是相对概念随链变，职能（设备/原料/工艺/服务）
是绝对概念不随链变——原 9 值词表把两者混在一个字段，v0.4 起拆分为
tier 三位置值 + function_role 八值（深交所课题八大关系词表）。

迁移规则（机械就近映射，全量落盘 tier_migration_map.yaml）::

    设备   -> 辅助设备(description 含 检测/测量/量测/辅助/清洗/包装/分拣/仓储) 否则 生产设备
    材料   -> 辅助材料(description 含 助剂/添加剂/辅料/辅助)               否则 生产原料
    原材料 -> 生产原料
    辅材   -> 辅助材料
    零部件 -> 加工工艺(description 含 加工/组装/装配/焊接/冲压/注塑/铸造/锻造/机加) 否则 产品业务
    位置 tier 一律归 上游（输入型环节在 L1 主链模板中的口径；位置语义错挂待 Owner 复核）

幂等锚：WHERE tier IN (职能值)——迁移后无该类行，复跑零迁移。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

MAP_PATH = Path(__file__).resolve().parent / "tier_migration_map.yaml"

AUX_EQUIP_RE = "(检测|测量|量测|辅助|清洗|包装|分拣|仓储)"
AUX_MAT_RE = "(助剂|添加剂|辅料|辅助)"
PROCESS_RE = "(加工|组装|装配|焊接|冲压|注塑|铸造|锻造|机加)"

MIGRATION_SQL = f"""
UPDATE ig_node SET
  function_role = CASE
    WHEN tier='设备'   AND description ~ '{AUX_EQUIP_RE}' THEN '辅助设备'
    WHEN tier='设备'                                        THEN '生产设备'
    WHEN tier='材料'   AND description ~ '{AUX_MAT_RE}'   THEN '辅助材料'
    WHEN tier='材料'                                        THEN '生产原料'
    WHEN tier='原材料'                                      THEN '生产原料'
    WHEN tier='辅材'                                        THEN '辅助材料'
    WHEN tier='零部件' AND description ~ '{PROCESS_RE}'    THEN '加工工艺'
    WHEN tier='零部件'                                      THEN '产品业务'
  END,
  tier = '上游',
  updated_at = now()
WHERE tier IN ('设备','材料','零部件','原材料','辅材')
"""

MAP_YAML = f"""# tier 职能化迁移映射表（Owner 2026-09-09 v0.4 裁定，治理脚本 migrate_tier_to_function_role.py 生成）
# 语义：位置(tier 三值)随链变、职能(function_role 八值)不随链变——9 值混载拆分。
# 幂等：仅 tier 仍为职能值时触发；迁移后位置一律归 上游（输入型环节=L1 主链模板口径），
#       位置语义错挂个案待 Owner 复核（开放问题登记）。
rules:
  "设备->生产设备":   "tier='设备' 且 description 不含 {AUX_EQUIP_RE}"
  "设备->辅助设备":   "tier='设备' 且 description 含 {AUX_EQUIP_RE}"
  "材料->生产原料":   "tier='材料' 且 description 不含 {AUX_MAT_RE}"
  "材料->辅助材料":   "tier='材料' 且 description 含 {AUX_MAT_RE}"
  "原材料->生产原料": "tier='原材料'（直译）"
  "辅材->辅助材料":   "tier='辅材'（直译）"
  "零部件->加工工艺": "tier='零部件' 且 description 含 {PROCESS_RE}"
  "零部件->产品业务": "tier='零部件' 其余（零部件=该环节产品本身）"
  "位置归一":         "被迁移行 tier 一律置 上游（设备/材料/零部件/原材料/辅材 均为链内输入型环节）"
engine_tool_switch: "引擎 S6 与 websearch_ingest 校验同 commit 切换（tier 三值+function_role 八值），防漂移"
"""


def main() -> int:
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    cur.execute("SELECT tier, count(*) FROM ig_node WHERE tier IN ('设备','材料','零部件','原材料','辅材') GROUP BY tier")
    before = dict(cur.fetchall())
    cur.execute(MIGRATION_SQL)
    migrated = cur.rowcount
    conn.commit()
    cur.execute("SELECT function_role, count(*) FROM ig_node WHERE function_role IS NOT NULL GROUP BY function_role")
    after = dict(cur.fetchall())
    cur.execute("SELECT tier, count(*) FROM ig_node GROUP BY tier ORDER BY 2 DESC")
    tiers_after = dict(cur.fetchall())
    conn.close()
    if migrated and not MAP_PATH.is_file():
        MAP_PATH.write_text(MAP_YAML, encoding="utf-8")
    print(json.dumps({
        "migrated": migrated,
        "before_by_tier": before,
        "after_by_function_role": after,
        "tiers_after": tiers_after,
        "map_file": str(MAP_PATH) if migrated else "skipped(零迁移,幂等)",
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] {e}")
        sys.exit(2)
